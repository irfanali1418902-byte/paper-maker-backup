/* UI-044 — type/leading probe, screen media.
 *
 * Two jobs, and they are different:
 *
 *   1. REGRESSION GATE on the three LIVE pages (slo, slo-health, library). These are the
 *      only pages a teacher uses today that load main.css, so any rule added to the new
 *      tree reaches them. The bar Irfan set is "byte-identical"; bytes cannot be the test
 *      because the CSS files themselves change, so the measurable equivalent is used:
 *      ZERO element x property deltas over a property set fixed before measuring.
 *
 *   2. THE URDU LINE BOX on bank, which is the thing UI-044 exists to fix. Measured with
 *      the webfont awaited — the print session read 22px instead of 47px by measuring in
 *      the same tick the text was injected, before font-display:swap had delivered.
 *
 * Edge gets its own --user-data-dir and is killed by the pid we spawned (UI-031a hazard).
 *
 *   node type_probe.mjs <label> <outdir>
 */

import { spawn } from 'node:child_process';
import { existsSync, mkdtempSync, mkdirSync, readFileSync, writeFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

const EDGE = 'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe';
const VIEWPORT = { width: 1280, height: 900 };
const BASE = 'http://127.0.0.1:8000/static';

const label = process.argv[2];
const outdir = process.argv[3];
mkdirSync(outdir, { recursive: true });

// The live pages are the gate. Only index is held now. landing added 2026-08-10 for
// UI-047d, per PROBES.md's rule that a migrating page joins this list or the gate
// silently stops covering it.
//
// taqseem added 2026-08-12, AND IT IS LATE. UI-047a migrated it and did not add it
// here, so for the length of that task the gate did not cover a live page — which is
// exactly what the rule above exists to prevent. It surfaced when UI-043's scope
// question needed a measurement of `.chip`, a class that exists on taqseem and on no
// other live page: the probe could not answer, because it was not looking. The older
// reason this line gave for excluding taqseem — "no Urdu rule at all" — was about the
// Urdu half of this probe and was never a reason to skip the computed-style half.
//
// print is live too (UI-047f, 2026-08-11) and is deliberately NOT here: css_print_probe
// owns it and measures it in print media, which is the media its regressions live in.
// If a screen regression on print.html ever matters, this is the list it joins.
//
// blueprint added 2026-08-13 with UI-047b — on time, unlike taqseem — and index the same day
// as the SUBJECT of UI-047c, before that migration rather than after it. index is the largest
// page in the app (783 elements, a 7-screen SPA, 224 inline style attributes) and the one
// whose before/after cannot be read off a browser glance. Adding a page here BEFORE migrating
// it is the pattern UI-047d used on landing, where 279 deltas were measured and each one
// accounted for; taqseem was migrated without it and the gap produced a false all-clear the
// next day.
const PAGES = [
  { page: 'slo', url: `${BASE}/slo.html`, role: 'LIVE — regression gate' },
  { page: 'slo-health', url: `${BASE}/slo-health.html`, role: 'LIVE — regression gate' },
  { page: 'library', url: `${BASE}/library.html`, role: 'LIVE — regression gate' },
  { page: 'taqseem', url: `${BASE}/taqseem.html`, role: 'LIVE — regression gate' },
  { page: 'blueprint', url: `${BASE}/blueprint.html`, role: 'LIVE — regression gate' },
  { page: 'bank', url: `${BASE}/bank.html`, role: 'subject — the Urdu fix' },
  { page: 'landing', url: `${BASE}/landing.html`, role: 'subject — UI-047d migration' },
  { page: 'index', url: `${BASE}/index.html`, role: 'subject — UI-047c migration' },
];

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const userDataDir = mkdtempSync(join(tmpdir(), 'type-edge-'));
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

// PROPERTY SET FIXED HERE, before anything is measured — the rule pages/slo.css wrote after
// two counts of the same migration disagreed. Type and box, since a leading change moves
// both: the line box itself and everything laid out below it.
//
// UI-041 ADDED THE SECOND GROUP. The original 18 are a TYPE probe: font, colour,
// background-colour and the box. A button component also moves RADIUS, SHADOW and CURSOR,
// and the original set cannot see any of those.
//
// THE JUSTIFICATION HERE WAS WRONG IN ITS FIRST DRAFT AND THE CORRECTION IS THE USEFUL
// PART. It claimed a rule flattening library's buttons to borderless would have reported
// ZERO deltas under the old 18. It would not: box-sizing is border-box globally
// (02-generic/reset.css:73), so removing a 1px border changes the used width and height —
// both of which ARE in the original set — on the button and on its flex siblings.
// Mutation-tested in-browser on library.html at review: `button { border: none }` produces 172
// element x property deltas within the original 18, and the narrower
// `.btn-primary,.btn-ghost { border: none }` produces 18. BOTH NUMBERS ARE DELTAS, NOT
// PROPERTIES — an earlier draft said "moves 172 of the original 18", which cannot be read
// literally and collides with the 18 twice over. Border removal was the one example that
// WOULD have been caught.
//
// What genuinely produces zero deltas under the old set, same mutation test, same page:
// `border-radius: 0` -> 0, `box-shadow: none` -> 0, `cursor: default` -> 0. Those three are
// why this list grew, and they are enough on their own: library.css:86 gives .btn-ghost a
// 9px radius, library.css:76 gives .btn-primary a box-shadow and a radius of
// var(--radius-btn) (10px, library.css:16 — an earlier draft of this comment said 12px,
// which is index.css:126's .ghost-btn, not library's). A component that changed any of the
// three would have passed the gate silently. Do not shrink this list back.
const SNAP = String.raw`(() => {
  const PROPS = [
    'font-size','line-height','font-family','font-weight','letter-spacing',
    'margin-top','margin-right','margin-bottom','margin-left',
    'padding-top','padding-right','padding-bottom','padding-left',
    'color','background-color','width','height','display',
    // UI-041 — what a button component actually changes.
    'border-top-width','border-right-width','border-bottom-width','border-left-width',
    'border-top-style','border-right-style','border-bottom-style','border-left-style',
    'border-top-color','border-right-color','border-bottom-color','border-left-color',
    'border-top-left-radius','border-top-right-radius',
    'border-bottom-right-radius','border-bottom-left-radius',
    'box-shadow','cursor','opacity','min-height','min-width','white-space',
    'column-gap','row-gap','align-items','justify-content',
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

  // The Urdu elements, called out by name rather than left to be found in a diff.
  // .q-text .qt.rtl is bank's held rule (99-legacy/bank.css:229) — Nastaliq with NO
  // line-height of its own, so it inherits whatever body gives it.
  const urdu = [];
  for (const el of document.querySelectorAll('.q-text .qt.rtl, .qt.rtl, .urdu-mode, .urdu, .ur')) {
    const cs = getComputedStyle(el);
    const r = el.getBoundingClientRect();
    urdu.push({
      desc: desc(el), path: path(el),
      fontFamily: cs.fontFamily, fontSize: cs.fontSize, lineHeight: cs.lineHeight,
      rect: { w: +r.width.toFixed(2), h: +r.height.toFixed(2) },
      // The ink extent: how tall the glyphs actually paint, vs the box they sit in.
      // Nastaliq paints well outside its em box, which is the whole reason this rule
      // is exposed and the Latin ones are not.
      clientRects: [...el.getClientRects()].map((q) => +q.height.toFixed(2)),
      text: (el.textContent || '').trim().slice(0, 40),
    });
  }

  return {
    all, urdu,
    elements: document.querySelectorAll('*').length,
    bodyLineHeight: getComputedStyle(document.body).lineHeight,
    bodyFontSize: getComputedStyle(document.body).fontSize,
    links: [...document.querySelectorAll('link[rel=stylesheet]')].map((l) => l.getAttribute('href')),
    fonts: document.fonts.status,
    title: document.title, url: location.href,
  };
})()`;

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

  const out = { label, browser: v.Browser, viewport: VIEWPORT, pages: {} };

  for (const spec of PAGES) {
    const rec = { role: spec.role, errors: [] };
    out.pages[spec.page] = rec;
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
      // These pages fetch their data; wait for the DOM to stop growing rather than
      // guessing a settle time.
      let prev = -1;
      for (let i = 0; i < 60; i++) {
        const n = await evaluate(sessionId, `document.querySelectorAll('*').length`);
        if (n === prev) break;
        prev = n; await sleep(250);
      }
      // Never believe a webfont line box without awaiting the font.
      await evaluate(sessionId, `document.fonts.ready.then(() => true)`);
      await sleep(500);

      // Determinism before any delta is believed.
      const first = await evaluate(sessionId, SNAP);
      const second = await evaluate(sessionId, SNAP);
      const drift = [];
      for (const [p, a] of Object.entries(first.all)) {
        const b = second.all[p];
        if (!b) { drift.push(`${p} missing in 2nd`); continue; }
        for (const k of Object.keys(a)) if (a[k] !== b[k]) drift.push(`${p}:${k} ${a[k]} -> ${b[k]}`);
      }
      rec.driftCount = drift.length;
      rec.drift = drift.slice(0, 10);
      rec.snapshot = first;
      await send('Target.closeTarget', { targetId });
    } catch (e) {
      rec.errors.push(String(e.message ?? e));
    }
  }

  writeFileSync(join(outdir, `${label}.json`), JSON.stringify(out, null, 1));
  console.log(JSON.stringify({
    label, browser: out.browser,
    pages: Object.fromEntries(Object.entries(out.pages).map(([k, v]) => [k, {
      role: v.role, elements: v.snapshot?.elements, drift: v.driftCount,
      bodyLineHeight: v.snapshot?.bodyLineHeight, bodyFontSize: v.snapshot?.bodyFontSize,
      links: v.snapshot?.links, urduCount: v.snapshot?.urdu?.length,
      urduLineHeights: [...new Set((v.snapshot?.urdu ?? []).map((u) => u.lineHeight))],
      errors: v.errors,
    }])),
  }, null, 1));
}

main().then(() => { cleanup(); process.exit(0); }).catch((e) => { console.error(e); cleanup(); process.exit(1); });
