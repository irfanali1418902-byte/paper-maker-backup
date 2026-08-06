/* UI-044b — PRINT-MEDIA probe. D36.
 *
 * Two jobs:
 *
 *   1. print.html's pagination, measured the literal Ctrl+P way: produce the PDF and count
 *      its pages. HEAD is 2 / 6 / 7 on the three test papers; migrated it is 3 / 6 / 7.
 *      That one extra page is D36 and it is what this task has to put back.
 *
 *   2. THE THREE LIVE PAGES IN PRINT MEDIA — a gate that has never been run. UI-044a proved
 *      they do not move on SCREEN. A `@media print` rule in the shared tree would reach them
 *      too, and their print output is a different measurement that nobody has taken. It is
 *      measured here rather than waved away, because "nobody prints slo-health" is an
 *      assumption and this epic's most repeated failure is exactly that shape.
 *
 * Everything runs under Emulation.setEmulatedMedia({media:'print'}); screen media does not
 * even apply print.css:215 or :375. Webfonts awaited before any box is believed.
 *
 *   node print_probe.mjs <label> <outdir>
 */

import { spawn } from 'node:child_process';
import { existsSync, mkdtempSync, mkdirSync, readFileSync, writeFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

const EDGE = 'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe';
const VIEWPORT = { width: 1280, height: 900 };
const BASE = 'http://127.0.0.1:8000/static';

const PAPERS = [
  '0d04c750-ddaa-406a-a9bb-a154cf487c9d', // 20Q, 0 images — HEAD 2 pages, migrated 3. THE one.
  'a5015cda-8269-4e96-8e87-82da9ccf091f', // 20Q, 19 images — 6 both ways
  '9ade2655-21e6-449d-943a-ae875542012e', // 25Q, 25 images — 7 both ways
];

const PAGES = [
  { key: 'slo', url: `${BASE}/slo.html`, role: 'LIVE — print-media gate', pdf: true },
  { key: 'slo-health', url: `${BASE}/slo-health.html`, role: 'LIVE — print-media gate', pdf: true },
  { key: 'library', url: `${BASE}/library.html`, role: 'LIVE — print-media gate', pdf: true },
  ...PAPERS.map((id) => ({
    key: `print:${id.slice(0, 8)}`, url: `${BASE}/print.html?paper_id=${id}`,
    role: 'subject — D36 pagination', pdf: true, waitFor: '.question',
  })),
];

const label = process.argv[2];
const outdir = process.argv[3];
mkdirSync(outdir, { recursive: true });

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const userDataDir = mkdtempSync(join(tmpdir(), 'printprobe-edge-'));
const edge = spawn(EDGE, ['--headless=new', '--disable-gpu', '--no-first-run',
  '--no-default-browser-check', '--disable-extensions', '--remote-debugging-port=0',
  `--user-data-dir=${userDataDir}`, `--window-size=${VIEWPORT.width},${VIEWPORT.height}`,
  'about:blank'], { stdio: ['ignore', 'ignore', 'pipe'] });
const stderrChunks = [];
edge.stderr.on('data', (b) => stderrChunks.push(b.toString()));
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

// Property set fixed here, before measuring. Type + box, because a leading change moves the
// line box and then everything laid out below it.
const SNAP = String.raw`(() => {
  const PROPS = [
    'font-size','line-height','font-family','font-weight',
    'margin-top','margin-bottom','padding-top','padding-bottom',
    'height','width','display','color',
  ];
  const path = (el) => {
    const parts = [];
    for (let n = el; n && n.nodeType === 1; n = n.parentElement) {
      const p = n.parentElement;
      const i = p ? Array.prototype.indexOf.call(p.children, n) : 0;
      parts.unshift(n.tagName + '[' + i + ']');
    }
    return parts.join('>');
  };
  const desc = (el) => {
    const cls = (typeof el.className === 'string' && el.className) ? '.' + el.className.trim().split(/\s+/).join('.') : '';
    return el.tagName.toLowerCase() + (el.id ? '#' + el.id : '') + cls;
  };
  const all = {};
  for (const el of document.querySelectorAll('*')) {
    const cs = getComputedStyle(el);
    const rec = { '@': desc(el) };
    for (const p of PROPS) rec[p] = cs.getPropertyValue(p);
    all[path(el)] = rec;
  }
  const bodyCS = getComputedStyle(document.body);
  const sheet = document.querySelector('.sheet');
  return {
    all,
    elements: document.querySelectorAll('*').length,
    bodyLineHeight: bodyCS.lineHeight, bodyFontSize: bodyCS.fontSize,
    docHeight: document.documentElement.getBoundingClientRect().height,
    sheetHeight: sheet ? +sheet.getBoundingClientRect().height.toFixed(2) : null,
    sheetPadding: sheet ? getComputedStyle(sheet).padding : null,
    media: matchMedia('print').matches ? 'print' : 'screen',
    links: [...document.querySelectorAll('link[rel=stylesheet]')].map((l) => l.getAttribute('href')),
    fonts: document.fonts.status,
  };
})()`;

function pdfPages(b64) {
  const s = Buffer.from(b64, 'base64').toString('latin1');
  const counts = [...s.matchAll(/\/Count\s+(\d+)/g)].map((m) => Number(m[1]));
  const boxes = [...new Set([...s.matchAll(/\/MediaBox\s*\[\s*[\d.\-]+\s+[\d.\-]+\s+([\d.\-]+)\s+([\d.\-]+)\s*\]/g)].map((m) => `${m[1]}x${m[2]}`))];
  return { pages: counts.length ? Math.max(...counts) : null, mediaBox: boxes };
}

async function main() {
  const portFile = join(userDataDir, 'DevToolsActivePort');
  let port;
  for (let i = 0; i < 200; i++) {
    if (existsSync(portFile)) { const f = readFileSync(portFile, 'utf8').split('\n')[0].trim(); if (f) { port = Number(f); break; } }
    await sleep(100);
  }
  if (!port) throw new Error('Edge never wrote DevToolsActivePort. ' + stderrChunks.join(''));
  const v = await (await fetch(`http://127.0.0.1:${port}/json/version`)).json();
  ws = await connect(v.webSocketDebuggerUrl);
  const out = { label, browser: v.Browser, pages: {} };

  for (const spec of PAGES) {
    const rec = { role: spec.role, errors: [] };
    out.pages[spec.key] = rec;
    try {
      const { targetId } = await send('Target.createTarget', { url: 'about:blank' });
      const { sessionId } = await send('Target.attachToTarget', { targetId, flatten: true });
      await send('Page.enable', {}, sessionId);
      await send('Runtime.enable', {}, sessionId);
      await send('Emulation.setDeviceMetricsOverride', {
        width: VIEWPORT.width, height: VIEWPORT.height, deviceScaleFactor: 1, mobile: false,
      }, sessionId);
      const loaded = onceEvent('Page.loadEventFired', sessionId);
      await send('Page.navigate', { url: spec.url }, sessionId);
      await loaded;

      if (spec.waitFor) {
        let n = 0;
        for (let i = 0; i < 100; i++) {
          n = await evaluate(sessionId, `document.querySelectorAll(${JSON.stringify(spec.waitFor)}).length`);
          if (n > 0) break;
          await sleep(200);
        }
        if (!n) rec.errors.push(`nothing matched ${spec.waitFor}`);
      } else {
        let prev = -1;
        for (let i = 0; i < 40; i++) {
          const n = await evaluate(sessionId, `document.querySelectorAll('*').length`);
          if (n === prev) break;
          prev = n; await sleep(250);
        }
      }

      await send('Emulation.setEmulatedMedia', { media: 'print' }, sessionId);
      await evaluate(sessionId, `document.fonts.ready.then(() => true)`);
      await sleep(600);

      const first = await evaluate(sessionId, SNAP);
      const second = await evaluate(sessionId, SNAP);
      let drift = 0;
      for (const [p, a] of Object.entries(first.all)) {
        const b = second.all[p];
        if (!b) { drift++; continue; }
        for (const k of Object.keys(a)) if (a[k] !== b[k]) drift++;
      }
      rec.driftCount = drift;
      rec.snapshot = first;

      if (spec.pdf) {
        const pdf = await send('Page.printToPDF', {
          printBackground: true, marginTop: 0, marginBottom: 0, marginLeft: 0, marginRight: 0,
          preferCSSPageSize: true,
        }, sessionId);
        rec.pdf = pdfPages(pdf.data);
        writeFileSync(join(outdir, `${label}-${spec.key.replace(/[:]/g, '_')}.pdf`), Buffer.from(pdf.data, 'base64'));
      }
      await send('Target.closeTarget', { targetId });
    } catch (e) {
      rec.errors.push(String(e.message ?? e));
    }
  }

  writeFileSync(join(outdir, `${label}.json`), JSON.stringify(out, null, 1));
  console.log(JSON.stringify(Object.fromEntries(Object.entries(out.pages).map(([k, v]) => [k, {
    role: v.role, media: v.snapshot?.media, drift: v.driftCount,
    bodyLH: v.snapshot?.bodyLineHeight, bodyFS: v.snapshot?.bodyFontSize,
    sheetH: v.snapshot?.sheetHeight, docH: v.snapshot?.docHeight?.toFixed(1),
    pdfPages: v.pdf?.pages, mediaBox: v.pdf?.mediaBox, errors: v.errors,
  }])), null, 1));
}

main().then(() => { cleanup(); process.exit(0); }).catch((e) => { console.error(e); cleanup(); process.exit(1); });
