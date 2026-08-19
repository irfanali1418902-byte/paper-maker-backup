/* css_selector_probe.mjs — what does this selector ACTUALLY compute to, per page?
 *
 *   node scripts/css_selector_probe.mjs "<selector>" "<prop,prop,...>" page page ...
 *   node scripts/css_selector_probe.mjs ".status-bar" "background-color,color" \
 *        --add=".status-bar:ok" bank library
 *
 * `--add=<selector>:<class>` adds a class before measuring and removes it after.
 * It is what makes hidden state reachable: .status-bar is display:none until JS
 * writes .ok/.err/.warn, and .modal-backdrop is display:none until .open. Neither
 * appears in any snapshot, so css_type_probe returns 0 for them whether the CSS is
 * right or wrong.
 *
 * WHY THIS EXISTS. "The rule text is identical in both files" is NOT the claim
 * "it paints the same thing" — the legacy :root blocks resolve differently per
 * page, because the migrated entry files remap some legacy token names onto the
 * new tree's roles and others were never remapped. On 2026-08-15/16 that gap was
 * found SIX times in one sitting: two live status palettes, two checkbox colours,
 * two primary blues, --radius-btn at 10px vs 8px, --bg at two greys, and a
 * checkbox at 16px vs 15px. Every one of them looked byte-identical in the files.
 *
 * SECOND USE, and it caught as much: a declaration that is DEAD in layer(legacy)
 * comes back to life when it is copied into layer(components), because layer order
 * is decided before specificity. Measure what a declaration computes to before
 * moving it up a layer. .filter-bar's font-size and .modal-header h3's 16px were
 * both dead; the first was resurrected and moved 75 deltas before it was caught.
 *
 * Elements built inside a JS template string need injection instead — see
 * PROGRESS.md 2026-08-16 for blueprint's .type-checks. */
import { spawn } from 'node:child_process';
import { existsSync, mkdtempSync, readFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

const EDGE = 'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe';
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const userDataDir = mkdtempSync(join(tmpdir(), 'sel-edge-'));
const edge = spawn(EDGE, ['--headless=new', '--disable-gpu', '--no-first-run',
  '--no-default-browser-check', '--disable-extensions', '--remote-debugging-port=0',
  `--user-data-dir=${userDataDir}`, '--window-size=1280,900', 'about:blank'],
  { stdio: ['ignore', 'ignore', 'pipe'] });
function cleanup() {
  try { edge.kill('SIGKILL'); } catch { /* gone */ }
  try { rmSync(userDataDir, { recursive: true, force: true }); } catch { /* locked */ }
}
process.on('exit', cleanup);

let nextId = 1; const pending = new Map(); const waiters = []; let ws;
function send(method, params = {}, sessionId) {
  const id = nextId++; const msg = { id, method, params };
  if (sessionId) msg.sessionId = sessionId;
  ws.send(JSON.stringify(msg));
  return new Promise((res, rej) => pending.set(id, { resolve: res, reject: rej }));
}
function onceEvent(method, sessionId, ms = 60000) {
  return new Promise((res, rej) => {
    const w = { method, sessionId, resolve: res }; waiters.push(w);
    setTimeout(() => { const i = waiters.indexOf(w); if (i >= 0) { waiters.splice(i, 1); rej(new Error('timeout ' + method)); } }, ms);
  });
}
function connect(u) {
  return new Promise((res, rej) => {
    const s = new WebSocket(u);
    s.onopen = () => res(s); s.onerror = (e) => rej(new Error(String(e.message ?? e)));
    s.onmessage = (ev) => {
      const m = JSON.parse(ev.data);
      if (m.id && pending.has(m.id)) { const p = pending.get(m.id); pending.delete(m.id); m.error ? p.reject(new Error(m.error.message)) : p.resolve(m.result); return; }
      for (let i = waiters.length - 1; i >= 0; i--) { const w = waiters[i]; if (w.method === m.method && (!w.sessionId || w.sessionId === m.sessionId)) { waiters.splice(i, 1); w.resolve(m.params); } }
    };
  });
}
async function evaluate(sid, expr) {
  const r = await send('Runtime.evaluate', { expression: expr, returnByValue: true, awaitPromise: true }, sid);
  if (r.exceptionDetails) throw new Error(r.exceptionDetails.exception?.description ?? r.exceptionDetails.text);
  return r.result.value;
}

const SEL = process.argv[2];
const PROPS = process.argv[3].split(',');
const rest = process.argv.slice(4);
const addArg = rest.find((a) => a.startsWith('--add='));
/* --attr=<selector>:<name>=<value> — the same idea as --add, for state that is an
   ATTRIBUTE rather than a class. index's Urdu toggle sets dir="rtl", and a whole
   block of RTL rules hangs off it that no snapshot probe has ever entered. */
const attrArg = rest.find((a) => a.startsWith('--attr='));
let ATTR = null;
if (attrArg) {
  const spec = attrArg.slice('--attr='.length);
  const i = spec.indexOf(':');
  const [name, ...v] = spec.slice(i + 1).split('=');
  ATTR = { sel: spec.slice(0, i), name, value: v.join('=') };
}
const PAGES = rest.filter((a) => !a.startsWith('--'));
/* "--add=<selector>:<class>" — last colon splits, so selectors may contain none. */
let ADD = null;
if (addArg) {
  const spec = addArg.slice('--add='.length);
  const i = spec.lastIndexOf(':');
  ADD = { sel: spec.slice(0, i), cls: spec.slice(i + 1) };
}

const EXPR = String.raw`(() => {
  const ADD = ${JSON.stringify(ADD)};
  const ATTR = ${JSON.stringify(ATTR)};
  let at = null, hadAttr = null;
  if (ATTR) {
    at = document.querySelector(ATTR.sel);
    if (at) { hadAttr = at.getAttribute(ATTR.name); at.setAttribute(ATTR.name, ATTR.value); }
  }
  let target = null, added = false;
  if (ADD) {
    target = document.querySelector(ADD.sel);
    if (target && !target.classList.contains(ADD.cls)) { target.classList.add(ADD.cls); added = true; }
  }
  const els = document.querySelectorAll(${JSON.stringify(SEL)});
  let o;
  if (!els.length) o = { n: 0 };
  else {
    const cs = getComputedStyle(els[0]);
    o = { n: els.length };
    for (const p of ${JSON.stringify(PROPS)}) o[p] = cs.getPropertyValue(p);
  }
  if (added) target.classList.remove(ADD.cls);
  if (at) { if (hadAttr === null) at.removeAttribute(ATTR.name); else at.setAttribute(ATTR.name, hadAttr); }
  return o;
})()`;

async function main() {
  const portFile = join(userDataDir, 'DevToolsActivePort');
  let port;
  for (let i = 0; i < 200; i++) { if (existsSync(portFile)) { const f = readFileSync(portFile, 'utf8').split('\n')[0].trim(); if (f) { port = Number(f); break; } } await sleep(100); }
  const v = await (await fetch(`http://127.0.0.1:${port}/json/version`)).json();
  ws = await connect(v.webSocketDebuggerUrl);
  console.log(`selector: ${SEL}${ADD ? `   (+ .${ADD.cls} on ${ADD.sel})` : ''}${ATTR ? `   (+ [${ATTR.name}="${ATTR.value}"] on ${ATTR.sel})` : ''}`);
  for (const page of PAGES) {
    const { targetId } = await send('Target.createTarget', { url: 'about:blank' });
    const { sessionId } = await send('Target.attachToTarget', { targetId, flatten: true });
    await send('Page.enable', {}, sessionId);
    await send('Runtime.enable', {}, sessionId);
    const loaded = onceEvent('Page.loadEventFired', sessionId);
    await send('Page.navigate', { url: `http://127.0.0.1:8000/static/${page}.html` }, sessionId);
    await loaded;
    await evaluate(sessionId, 'document.fonts.ready');
    await sleep(400);
    const r = await evaluate(sessionId, EXPR);
    console.log(`  ${page.padEnd(11)} ` + (r.n === 0 ? 'no match' : `n=${String(r.n).padEnd(3)} ` + PROPS.map(p => `${p}=${r[p]}`).join('  ')));
    await send('Target.closeTarget', { targetId });
  }
}
main().then(() => { cleanup(); process.exit(0); }).catch((e) => { console.error(e); cleanup(); process.exit(1); });
