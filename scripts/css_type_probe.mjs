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
 *   node scripts/css_type_probe.mjs <label> <outdir> [--viewports 1280,700]
 *
 * UI-064, 2026-08-26 — IT NO LONGER READS ONE WIDTH. Until this change every probe in the
 * repo ran at 1280x900, so of the fifteen screen `@media` queries in static/css/ exactly
 * ONE was ever observed; the other fourteen sat in bands nothing measured. See the
 * VIEWPORTS block below for the band list and `css_breakpoints.mjs` for how it is derived.
 *
 * AND THE WIDTHS WERE ONLY HALF OF IT. The property list below was blind to what those
 * rules set — flex-direction appears 22 times inside them and was not measured at all,
 * likewise flex-wrap, position and grid-template-columns. Adding viewports without adding
 * those properties would have produced a probe that visits the band and still sees
 * nothing, which is the failure this task exists to end rather than repeat.
 */

import { spawn } from 'node:child_process';
import { existsSync, mkdtempSync, mkdirSync, readFileSync, writeFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { uncoveredLines } from './css_breakpoints.mjs';

const EDGE = 'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe';
const BASE = 'http://127.0.0.1:8000/static';

/* THE VIEWPORT LIST — UI-064, and it is derived, not chosen.
 *
 * 1280x900 was the only width this probe ever ran at, so fourteen of the tree's fifteen
 * screen `@media` queries were never observed by anything. `css_breakpoints.mjs` computes
 * the BANDS — ranges of width within which the set of matching rules cannot change — and
 * one width per band is both necessary and sufficient. On 2026-08-26 the tree's bands and
 * their rule counts are:
 *
 *     1025+      1 rule    1280   <- the historical viewport, kept FIRST and unchanged
 *     761-1024   2 rules    900
 *     721-760   10 rules    740
 *     561-720   13 rules    700
 *     1-560     14 rules    520
 *
 * Add a width here only when `css_breakpoints.mjs` reports a band as UNOBSERVED — which
 * this probe prints in its own summary every run, so a new breakpoint cannot go unmeasured
 * quietly. That printing is the point: D45, D49 and this task are all the same failure,
 * a gate that could not see the thing it was gating, and the fix that lasts is a gate that
 * says out loud what it is not looking at.
 *
 * KEYS. The reference viewport's keys are UNSUFFIXED and byte-identical to what this probe
 * has always written; every other width appends `@<width>`. So `css_type_diff.mjs` reads
 * this file unchanged, old paths still paste into a state diff (css_state_probe's
 * `<path>::<state>` promise survives), and a suffix in a diff line tells you at a glance
 * that the delta is a narrow-width one. */
const VIEWPORTS = [
  { width: 1280, height: 900, ref: true },
  { width: 900, height: 900 },
  { width: 740, height: 900 },
  { width: 700, height: 900 },
  { width: 520, height: 900 },
];

const argv = process.argv.slice(2);

/* FLAG VALUES ARE CONSUMED, NOT FILTERED, and the naive version was wrong in a way that
   fails silently. `argv.filter((a) => !a.startsWith('--'))` leaves the VALUE `1280,700`
   in the positional list, so `--viewports 1280,700 before out` sets label='1280,700' and
   outdir='before' and creates a garbage directory without an error. Caught at review.
   css_state_probe.mjs had the same shape already, for --page as well, and is fixed the
   same way below. */
const FLAGS_WITH_VALUE = new Set(['--viewports', '--page']);
const positional = [];
for (let i = 0; i < argv.length; i++) {
  if (argv[i].startsWith('--')) { if (FLAGS_WITH_VALUE.has(argv[i])) i++; continue; }
  positional.push(argv[i]);
}
const label = positional[0];
const outdir = positional[1];

/* --viewports 1280,700 — for a quick single-band re-check while iterating. The first
   width given is the reference (unsuffixed), matching the default list's shape. */
const vpIdx = argv.indexOf('--viewports');
const viewports = vpIdx >= 0
  ? argv[vpIdx + 1].split(',').map(Number).map((width, i) => ({ width, height: 900, ref: i === 0 }))
  : VIEWPORTS;

if (!label || !outdir) {
  console.error('usage: node scripts/css_type_probe.mjs <label> <outdir> [--viewports 1280,700]');
  process.exit(2);
}
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
// print is live too (UI-047f, 2026-08-11) and was deliberately NOT here: css_print_probe
// owns it and measures it in print media, which is the media its regressions live in.
// This line then said "if a screen regression on print.html ever matters, this is the
// list it joins" — and on 2026-08-20 one did. print was the only page still carrying the
// white-links bug: `a { color: inherit }` in layer(elements) beat its legacy nav colour,
// so its sidebar links rendered white and hover changed nothing. It had been recorded as
// fixed along with the other eight the day before. Nothing caught it because nothing on
// this page was measured in SCREEN media by anything, which is the same silent gap
// taqseem's late entry above describes.
//
// ⚠ IT IS ADDED WITHOUT `?paper_id=`, SO THE PAPER BODY IS NOT COVERED HERE. print.html
// renders its shell either way and the shell is where this regression lived; the paper
// itself needs a row that exists in the local DB, and hardcoding a UUID would make the
// gate quietly measure an empty page the day that row goes. The body stays
// css_print_probe's, in the media it prints in.
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
  { page: 'print', url: `${BASE}/print.html`, role: 'LIVE — shell only, no paper_id' },
];

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const userDataDir = mkdtempSync(join(tmpdir(), 'type-edge-'));
const edge = spawn(EDGE, ['--headless=new', '--disable-gpu', '--no-first-run',
  '--no-default-browser-check', '--disable-extensions', '--remote-debugging-port=0',
  // Window size is the reference viewport's; every other band is reached with
  // Emulation.setDeviceMetricsOverride, which is what decides the media query anyway.
  `--user-data-dir=${userDataDir}`, `--window-size=${viewports[0].width},${viewports[0].height}`,
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
    // UI-064 — WHAT THE @media RULES ACTUALLY SET, and the list was blind to most of it.
    // Adding narrow viewports alone would NOT have made those rules measurable: the
    // properties inside them were largely absent here. Counted across the fifteen screen
    // @media blocks in static/css/ on 2026-08-26: flex-direction x22, flex-wrap x9,
    // position x9, grid-template-columns x3, z-index x2, and one each of
    // top/bottom/max-height/flex-shrink/border-top. Already covered before this change:
    // display, width, height, padding, gap, align-items, justify-content, font-size,
    // font-weight, line-height, color, background, border-radius, box-shadow, cursor,
    // min-width. So a rule flipping flex-direction to column could be deleted at any
    // width and read as zero deltas.
    // (No backticks in this comment: it lives inside a template literal, and the first
    // draft ended the literal mid-sentence. The error pointed at the word "flex".)
    //
    // WARNING, THREE OF THESE ARE SYMMETRY AND NOT EVIDENCE: right, left and max-width
    // have ZERO uses inside any media block. An earlier draft of this comment ended
    // "nothing speculative added", which review showed was simply false. They complete
    // the pairs whose partners are used (top/bottom, min-width); their cost is possible
    // noise on positioned elements. Named so the next reader need not re-derive which of
    // these were earned and which were assumed.
    //
    // flex-grow and flex-basis are NOT redundant with flex-shrink: the flex shorthand
    // appears twice inside media blocks and resolves to all three longhands.
    'flex-direction','flex-wrap','flex-grow','flex-shrink','flex-basis',
    'position','top','right','bottom','left','z-index',
    'max-height','max-width','grid-template-columns',
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
  /* The probe's own KILL_MOTION <style> is excluded, so the gate does not measure an
     element it injected: without this, the elements count reads 935 where the page has
     934 and a stray key appears in every snapshot. It is a style tag in head, so nothing
     else about the page shifts. (No backticks — template literal. Third time.) */
  const SELF = '__probe_kill_motion';
  for (const el of document.querySelectorAll('*')) {
    if (el.id === SELF) continue;
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
    elements: document.querySelectorAll('*').length - (document.getElementById(SELF) ? 1 : 0),
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

  const out = {
    label, browser: v.Browser,
    viewport: viewports.find((vp) => vp.ref),      // kept: old readers expect one
    viewports: viewports.map(({ width, height }) => ({ width, height })),
    pages: {},
  };

  for (const spec of PAGES) {
    const rec = { role: spec.role, errors: [] };
    out.pages[spec.page] = rec;
    try {
      const { targetId } = await send('Target.createTarget', { url: 'about:blank' });
      const { sessionId } = await send('Target.attachToTarget', { targetId, flatten: true });
      await send('Page.enable', {}, sessionId);
      await send('Runtime.enable', {}, sessionId);
      const ref = viewports.find((vp) => vp.ref) ?? viewports[0];
      await send('Emulation.setDeviceMetricsOverride', {
        width: ref.width, height: ref.height, deviceScaleFactor: 1, mobile: false,
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

      /* Motion off for the length of the probe — see the resize note below for why this
         probe now needs it and css_state_probe.mjs's KILL_MOTION header for the cascade
         detail (an unlayered !important sheet wins over normal declarations, NOT because
         it is unlayered). Injected before the first snapshot, never removed, and the
         target is closed straight after. */
      await evaluate(sessionId, `(() => {
        const s = document.createElement('style');
        s.id = '__probe_kill_motion';
        s.textContent = '*,*::before,*::after{transition:none !important;animation:none !important}';
        document.head.appendChild(s);
        return true;
      })()`);

      /* ONE PAGE LOAD, EVERY BAND — the page is loaded once at the reference width and
         then RESIZED, rather than reloaded per width. Reloading would be slower and, on
         these JS-rendered pages, would re-run every fetch and re-race every listener for
         no gain. Resizing changes which @media rules match, which is the whole question.

         WHAT THE 300 ms IS ACTUALLY FOR, corrected at review. The first version of this
         comment said the sleep guards against reading mid-reflow and that the
         determinism check proves it was long enough. BOTH HALVES WERE WRONG:
         getComputedStyle forces a synchronous style+layout flush in Blink, so a
         mid-reflow read is not reachable and the sleep was never guarding that. What a
         resize really starts is CSS TRANSITIONS, and the longest transition-duration in
         this tree is 0.2 s (99-legacy/library.css:131 on `bottom`, 99-legacy/bank.css:260
         on `transform`), so 300 ms clears the worst case — today.

         "Today" is not good enough for a gate, so motion is switched off outright below,
         the same way css_state_probe.mjs does it. With transitions dead the sleep is
         belt-and-braces rather than the thing correctness rests on. This matters more
         than it did: `bottom` is one of the properties UI-064 ADDED, so this probe is
         newly exposed to exactly that 0.2 s transition. */
      const drift = [];
      let refSnap = null;
      // Reference first, always — the page is already at that width from the load above,
      // and refSnap must exist before any suffixed keys are merged into it.
      const ordered = [ref, ...viewports.filter((vp) => vp !== ref)];
      for (const vp of ordered) {
        if (vp !== ref) {
          await send('Emulation.setDeviceMetricsOverride', {
            width: vp.width, height: vp.height, deviceScaleFactor: 1, mobile: false,
          }, sessionId);
          await sleep(300);
        }
        const first = await evaluate(sessionId, SNAP);
        const second = await evaluate(sessionId, SNAP);
        for (const [p, a] of Object.entries(first.all)) {
          const b = second.all[p];
          if (!b) { drift.push(`@${vp.width} ${p} missing in 2nd`); continue; }
          for (const k of Object.keys(a)) {
            if (a[k] !== b[k]) drift.push(`@${vp.width} ${p}:${k} ${a[k]} -> ${b[k]}`);
          }
        }
        if (vp === ref) {
          // The scalar fields (elements, bodyLineHeight, links, urdu) are the reference
          // viewport's. They describe the page, not the band, and the Urdu line box this
          // probe was built for is a desktop measurement.
          refSnap = first;
        } else {
          for (const [p, styles] of Object.entries(first.all)) {
            refSnap.all[`${p}@${vp.width}`] = styles;
          }
        }
      }
      rec.driftCount = drift.length;
      rec.drift = drift.slice(0, 10);
      rec.snapshot = refSnap;
      rec.keysPerViewport = Object.fromEntries(viewports.map((vp) => [
        vp.width,
        Object.keys(refSnap.all).filter((k) => (vp === ref ? !k.includes('@') : k.endsWith(`@${vp.width}`))).length,
      ]));
      /* AND IT IS COMPARED, NOT JUST PRINTED. Review's finding: this count is exactly the
         instrument that detects the bands having measured different DOMs — a late fetch
         resolving after the reference snapshot gives later bands extra keys — and the
         first version only displayed it. An unequal count is a broken run, so it goes
         into `drift`, which is the field a reader already checks. (Measured 2026-08-26:
         no page in static/ reads width in JS at all — no resize/ResizeObserver/matchMedia
         listener exists — so this should never fire. That is why it is cheap to assert.) */
      const counts = new Set(Object.values(rec.keysPerViewport));
      if (counts.size > 1) {
        drift.push(`key count differs across viewports: ${JSON.stringify(rec.keysPerViewport)}`);
        rec.driftCount = drift.length;
        rec.drift = drift.slice(0, 10);
      }
      await send('Target.closeTarget', { targetId });
    } catch (e) {
      rec.errors.push(String(e.message ?? e));
    }
  }

  writeFileSync(join(outdir, `${label}.json`), JSON.stringify(out, null, 1));

  /* THE PROBE REPORTS ITS OWN BLIND SPOTS. Printed before the payload so it is not lost
     at the bottom of a long JSON dump. If this says UNOBSERVED, a rule in that band can
     change by any amount and this run will report zero deltas. */
  console.log(`viewports: ${viewports.map((vp) => vp.width).join(', ')}  (reference ${viewports.find((vp) => vp.ref)?.width ?? viewports[0].width})`);
  const gaps = uncoveredLines(viewports.map((vp) => vp.width));
  console.log(gaps.length
    ? `${gaps.length} BAND(S) NOT MEASURED BY THIS RUN:\n${gaps.join('\n')}`
    : 'every @media width band in static/css is observed by this run');

  console.log(JSON.stringify({
    label, browser: out.browser,
    pages: Object.fromEntries(Object.entries(out.pages).map(([k, v]) => [k, {
      role: v.role, elements: v.snapshot?.elements, drift: v.driftCount,
      keysPerViewport: v.keysPerViewport,
      bodyLineHeight: v.snapshot?.bodyLineHeight, bodyFontSize: v.snapshot?.bodyFontSize,
      links: v.snapshot?.links, urduCount: v.snapshot?.urdu?.length,
      urduLineHeights: [...new Set((v.snapshot?.urdu ?? []).map((u) => u.lineHeight))],
      errors: v.errors,
    }])),
  }, null, 1));
}

main().then(() => { cleanup(); process.exit(0); }).catch((e) => { console.error(e); cleanup(); process.exit(1); });
