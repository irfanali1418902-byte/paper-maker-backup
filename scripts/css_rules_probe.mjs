/* CDP driver for `css_orphans.py --rules` — the DOM half of UI-032's measurement.
 *
 * The token check is a grep. The RULE check cannot be: whether `static/theme.css`'s
 * `.btn` rule reaches this page is a question about the page's *elements*, and the
 * elements only exist once the page's JS has run. So every selector is run through
 * `querySelectorAll` against the live document, exactly as `taqseem` (UI-031c) was
 * measured — that page passed the token check and still could not ship.
 *
 * Driven headless because the answer is a count, not a look. Edge is launched with its
 * OWN --user-data-dir and killed by the pid we spawned: UI-031a's review agent ran
 * `Get-Process msedge | Stop-Process -Force` and would have taken Irfan's browser with
 * it.
 *
 * Contract — stdin/argv JSON in, stdout JSON out (the Python side owns all parsing and
 * every number; this file only asks the DOM and reports what it said):
 *
 *   in : { edge, viewport:{width,height}, settleMs, pages:[{page,url,screens?}],
 *          probes:[{id,sel}] }
 *   out: { pages: { <page>: { counts:{id:n}, elements:n, drift:[ids], title, url,
 *                             screens:{<name>:{ok,elements}}, errors:[] } }, port }
 *
 * `drift` is not decoration. Every page is probed TWICE with no action in between and
 * the two results compared; a data-driven page that jitters run-to-run would otherwise
 * read as a CSS fact. `slo-health` was proven deterministic this way before its diff was
 * believed (STATUS.md, UI-031b).
 */

import { spawn } from 'node:child_process';
import { existsSync, mkdtempSync, readFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

const input = JSON.parse(readFileSync(process.argv[2], 'utf8'));
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

// ---------------------------------------------------------------- launch Edge

const userDataDir = mkdtempSync(join(tmpdir(), 'cssrules-edge-'));
const edge = spawn(input.edge, [
  '--headless=new',
  '--disable-gpu',
  '--no-first-run',
  '--no-default-browser-check',
  '--disable-extensions',
  '--remote-debugging-port=0',
  `--user-data-dir=${userDataDir}`,
  `--window-size=${input.viewport.width},${input.viewport.height}`,
  'about:blank',
], { stdio: ['ignore', 'ignore', 'pipe'] });

const stderrChunks = [];
edge.stderr.on('data', (b) => stderrChunks.push(b.toString()));

function cleanup() {
  try { edge.kill('SIGKILL'); } catch { /* already gone */ }
  try { rmSync(userDataDir, { recursive: true, force: true }); } catch { /* locked */ }
}
process.on('exit', cleanup);

// --remote-debugging-port=0 means the port is chosen by the browser and written here.
// Reading the file beats guessing a free port and beats a fixed one (a stale Edge on
// 9222 would have us probing the wrong browser).
async function waitForPort() {
  const portFile = join(userDataDir, 'DevToolsActivePort');
  for (let i = 0; i < 200; i++) {
    if (existsSync(portFile)) {
      const first = readFileSync(portFile, 'utf8').split('\n')[0].trim();
      if (first) return Number(first);
    }
    await sleep(100);
  }
  throw new Error(`Edge never wrote DevToolsActivePort. stderr:\n${stderrChunks.join('')}`);
}

// ------------------------------------------------------------------ CDP plumbing

let nextId = 1;
const pending = new Map();
const waiters = [];
let ws;

function send(method, params = {}, sessionId) {
  const id = nextId++;
  const msg = { id, method, params };
  if (sessionId) msg.sessionId = sessionId;
  ws.send(JSON.stringify(msg));
  return new Promise((resolve, reject) => pending.set(id, { resolve, reject }));
}

function onceEvent(method, sessionId, timeoutMs = 30000) {
  return new Promise((resolve, reject) => {
    const w = { method, sessionId, resolve };
    waiters.push(w);
    setTimeout(() => {
      const i = waiters.indexOf(w);
      if (i >= 0) { waiters.splice(i, 1); reject(new Error(`timeout waiting for ${method}`)); }
    }, timeoutMs);
  });
}

function connect(url) {
  return new Promise((resolve, reject) => {
    const sock = new WebSocket(url);
    sock.onopen = () => resolve(sock);
    sock.onerror = (e) => reject(new Error(`ws error: ${e.message ?? e}`));
    sock.onmessage = (ev) => {
      const m = JSON.parse(ev.data);
      if (m.id && pending.has(m.id)) {
        const { resolve: res, reject: rej } = pending.get(m.id);
        pending.delete(m.id);
        m.error ? rej(new Error(`${m.error.message} (${JSON.stringify(m.error.data ?? '')})`)) : res(m.result);
        return;
      }
      for (let i = waiters.length - 1; i >= 0; i--) {
        const w = waiters[i];
        if (w.method === m.method && (!w.sessionId || w.sessionId === m.sessionId)) {
          waiters.splice(i, 1);
          w.resolve(m.params);
        }
      }
    };
  });
}

async function evaluate(sessionId, expression) {
  const r = await send('Runtime.evaluate', {
    expression, returnByValue: true, awaitPromise: true,
  }, sessionId);
  if (r.exceptionDetails) {
    throw new Error(r.exceptionDetails.exception?.description ?? r.exceptionDetails.text);
  }
  return r.result.value;
}

// The probe itself. One round trip for every selector would be ~120 per page; this runs
// the whole list inside the document and returns a single object. A selector the engine
// rejects records -1 rather than aborting the page — the Python side reports those
// separately instead of silently counting them as "does not match".
function probeExpression(probes) {
  return `(() => {
    const P = ${JSON.stringify(probes)};
    const out = {};
    for (const p of P) {
      try { out[p.id] = document.querySelectorAll(p.sel).length; }
      catch (e) { out[p.id] = -1; }
    }
    return { counts: out, elements: document.querySelectorAll('*').length, title: document.title, url: location.href };
  })()`;
}

// ------------------------------------------------------------------------ run

async function main() {
  const port = await waitForPort();
  const version = await (await fetch(`http://127.0.0.1:${port}/json/version`)).json();
  ws = await connect(version.webSocketDebuggerUrl);

  const out = { port, browser: version.Browser, pages: {} };

  for (const page of input.pages) {
    const rec = { errors: [], screens: {} };
    out.pages[page.page] = rec;
    let sessionId;
    try {
      const { targetId } = await send('Target.createTarget', { url: 'about:blank' });
      ({ sessionId } = await send('Target.attachToTarget', { targetId, flatten: true }));

      await send('Page.enable', {}, sessionId);
      await send('Runtime.enable', {}, sessionId);
      await send('Emulation.setDeviceMetricsOverride', {
        width: input.viewport.width, height: input.viewport.height,
        deviceScaleFactor: 1, mobile: false,
      }, sessionId);

      const loaded = onceEvent('Page.loadEventFired', sessionId);
      await send('Page.navigate', { url: page.url }, sessionId);
      await loaded;
      await sleep(input.settleMs);

      const first = await evaluate(sessionId, probeExpression(input.probes));
      const second = await evaluate(sessionId, probeExpression(input.probes));
      rec.counts = { ...first.counts };
      rec.elements = first.elements;
      rec.title = first.title;
      rec.url = first.url;
      rec.drift = Object.keys(first.counts).filter((k) => first.counts[k] !== second.counts[k]);
      rec.elementsDrift = first.elements !== second.elements;

      // An SPA holds six of its seven screens outside the default view; querySelectorAll
      // sees only what is in the DOM, so each screen is switched to and re-probed and the
      // counts are unioned. index.html is 7 screens behind showScreen() (STATUS.md).
      for (const screen of page.screens ?? []) {
        try {
          await evaluate(sessionId, `showScreen(${JSON.stringify(screen)}); true`);
          await sleep(input.screenSettleMs ?? input.settleMs);
          const s = await evaluate(sessionId, probeExpression(input.probes));
          rec.screens[screen] = { ok: true, elements: s.elements };
          for (const [k, v] of Object.entries(s.counts)) {
            if (v > (rec.counts[k] ?? 0)) rec.counts[k] = v;
          }
        } catch (e) {
          rec.screens[screen] = { ok: false, error: String(e.message ?? e) };
          rec.errors.push(`screen ${screen}: ${e.message ?? e}`);
        }
      }
    } catch (e) {
      rec.errors.push(String(e.message ?? e));
    } finally {
      if (sessionId) { try { await send('Target.closeTarget', { targetId: (await send('Target.getTargetInfo', {}, sessionId)).targetInfo.targetId }); } catch { /* closing is best-effort */ } }
    }
  }

  process.stdout.write(JSON.stringify(out));
}

main().then(() => { cleanup(); process.exit(0); })
  .catch((e) => { process.stderr.write(String(e.stack ?? e)); cleanup(); process.exit(1); });
