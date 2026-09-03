/* =========================================================================
   css_drain_probe.mjs — WHICH LEGACY RULES ARE ALREADY DEAD?

   Sprint 6's question, and it is NOT the question the migrations asked.

   The migrations asked "what does this page LOSE when static/theme.css is
   unlinked?" — css_orphans.py answered that, by diffing the page against
   theme.css. That file was deleted on 2026-08-13 and that tool's job is
   over. The drain asks the opposite: "this legacy rule is still here — if I
   delete it, does anything move?" Nothing measured that until this file.

   It matters because the alternative is reading 2,115 lines and forming an
   opinion, and this epic has now watched that fail four times in two days —
   most sharply on `.row`, which was read as safe, written down as safe, and
   was not.

   HOW IT WORKS, and the design is the reason it is usable at all.
   Everything happens INSIDE ONE PAGE LOAD, in one Runtime.evaluate:

     1. snapshot every element's computed styles              (the baseline)
     2. for each rule in 99-legacy/<page>.css:
          sheet.deleteRule(i)  ->  re-snapshot  ->  count deltas
          sheet.insertRule(cssText, i)                        (restore)
     3. report each rule's delta count

   NO FILE IS EVER EDITED. The CSSOM is mutated and put back, so an
   interrupted run cannot leave a half-drained stylesheet on disk — which a
   delete-probe-restore loop over the real file absolutely could.

   AND NO PER-RULE ROUND TRIP. A page like slo is 930 elements x 44
   properties; shipping that over CDP forty times would be ~1.6M values on
   the wire. The whole loop runs in-page and returns counts.

   READING THE OUTPUT — and the second column is the one to be careful with.

     deltas = 0   The rule changes nothing. Something else already supplies
                  every property it sets, at equal or higher precedence.
                  SAFE TO DELETE. This is the drain's whole target.

     deltas > 0   The rule is load-bearing HERE, TODAY, AT THIS VIEWPORT.
                  It needs a home — a component, the page's entry file, or
                  a deliberate decision to let the value change.

   WHAT A ZERO DOES NOT MEAN. Four limits, all of them real:

     · VIEWPORT. One size, 1280x900. ⚠ "same as css_type_probe" USED TO FOLLOW HERE AND
       IS NO LONGER TRUE: UI-064 gave css_type_probe five width bands (1280/900/740/700/
       520) and left this probe at one, so this limit is now THIS probe's alone. If a
       drain candidate lives inside an @media block, confirm it with css_type_probe at
       the relevant band before deleting — the zero here means less than it used to.
       Every
       @media rule outside that range reports 0 because it is not applying,
       not because it is dead. slo.css:86's `@media (max-width: 720px)` is
       the example. Treat media blocks as UNMEASURED, not dead.
     · JS-RENDERED CONTENT. Elements that only exist after data loads are
       not in the snapshot. taqseem's chips are the standing case: its
       `.chip` rules would read 0 on an empty board and are not dead.
     · PROPERTY LIST. The same 44 as css_type_probe, deliberately, so the
       two agree. Anything outside it — `overflow` is the one that has
       already bitten — is invisible. A rule setting only `overflow` reports
       0 and is not dead.
     · STATE. `:hover`, `:focus`, `:active` match nothing at rest. Their
       rules report 0 for the same reason `.nav a:hover` did on 2026-08-12.

   So a 0 is a CANDIDATE, not a verdict. Check the selector against these
   four before deleting anything. A delta count above 0, on the other hand,
   is proof: the rule is doing work.

   USAGE
     node scripts/css_drain_probe.mjs <page> [--json <path>]

   Needs the app running: .venv/Scripts/python.exe -m uvicorn app.main:app
   ========================================================================= */

import { spawn } from 'node:child_process';
import { mkdtempSync, writeFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

const EDGE = 'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe';
const VIEWPORT = { width: 1280, height: 900 };
const BASE = 'http://127.0.0.1:8000/static';

const page = process.argv[2];
if (!page) {
  console.error('usage: node scripts/css_drain_probe.mjs <page> [--json <path>]');
  console.error('                                        [--query=?a=b] [--warm="<js>"] [--wait=ms]');
  process.exit(2);
}
const jsonIdx = process.argv.indexOf('--json');
const jsonOut = jsonIdx > 0 ? process.argv[jsonIdx + 1] : null;

/* --query / --warm / --wait: WITHOUT THESE, A ZERO ON A DATA-DRIVEN PAGE IS
   MEANINGLESS. Most of these pages render their real content from JS after an
   API call, so a probe that loads the bare page measures a DOM that no user ever
   sees: the 2026-08-16 sweep returned 339 zero-delta candidates and 204 of them
   were simply markup that had not been built yet. --query adds a query string
   (print.html needs ?paper_id=<uuid>), --warm runs a snippet after load to
   trigger a render, and --wait extends the settle time before the drain loop. */
const qArg = process.argv.find((a) => a.startsWith('--query='));
const warmArg = process.argv.find((a) => a.startsWith('--warm='));
const waitArg = process.argv.find((a) => a.startsWith('--wait='));
const WARM = warmArg ? warmArg.slice('--warm='.length) : null;
const WAIT = waitArg ? Number(waitArg.slice('--wait='.length)) : 1200;
const url = `${BASE}/${page}.html${qArg ? qArg.slice('--query='.length) : ''}`;

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const userDataDir = mkdtempSync(join(tmpdir(), 'drain-edge-'));
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
async function evaluate(sid, expr, ms = 300000) {
  const r = await send('Runtime.evaluate', { expression: expr, returnByValue: true, awaitPromise: true, timeout: ms }, sid);
  if (r.exceptionDetails) throw new Error(r.exceptionDetails.exception?.description ?? r.exceptionDetails.text);
  return r.result.value;
}

/* The in-page half. PROPERTY LIST IS css_type_probe's, unchanged and on
   purpose — if the two probes disagreed about what a "delta" is, a rule
   could read dead here and move the gate there. */
const DRAIN = (pageName) => String.raw`(() => {
  const PROPS = [
    'font-size','line-height','font-family','font-weight','letter-spacing',
    'margin-top','margin-right','margin-bottom','margin-left',
    'padding-top','padding-right','padding-bottom','padding-left',
    'color','background-color','width','height','display',
    'border-top-width','border-right-width','border-bottom-width','border-left-width',
    'border-top-style','border-right-style','border-bottom-style','border-left-style',
    'border-top-color','border-right-color','border-bottom-color','border-left-color',
    'border-top-left-radius','border-top-right-radius',
    'border-bottom-right-radius','border-bottom-left-radius',
    'box-shadow','cursor','opacity','min-height','min-width','white-space',
  ];

  // Find 99-legacy/<page>.css. It is reached through the entry file's
  // @import ... layer(legacy), so it is a CSSImportRule's .styleSheet and
  // NOT a top-level document.styleSheets entry. Walking imports is the same
  // correction css_page_rule_probe.mjs's header records.
  function findLegacy(sheets, want, depth) {
    for (const sh of sheets) {
      try {
        if ((sh.href || '').includes(want)) return sh;
        for (const r of sh.cssRules) {
          if (r.styleSheet) { const hit = findLegacy([r.styleSheet], want, depth + 1); if (hit) return hit; }
        }
      } catch (e) { /* cross-origin or not yet parsed */ }
    }
    return null;
  }
  const legacy = findLegacy([...document.styleSheets], '99-legacy/' + ${JSON.stringify(pageName)} + '.css', 0);
  if (!legacy) return { error: '99-legacy/' + ${JSON.stringify(pageName)} + '.css not found in the CSSOM' };

  // KILL TRANSITIONS BEFORE MEASURING ANYTHING, and this is not cosmetic —
  // without it the probe cannot measure two of the nine files at all.
  // Deleting a rule changes the properties it set; if those properties are
  // transitioned, they ANIMATE to the new value. Re-inserting the rule starts
  // the animation back the other way, and the restore check snapshots while it
  // is still running — so the sheet reads as drifted when nothing is wrong.
  // It fired on landing's .qa-card (transform/box-shadow/border-color, .12s,
  // 35 deltas) and bank's .bulk-drop-zone (background/border-color, .15s, 5).
  // NOTE: no backticks anywhere in this in-page block -- it is itself a
  // backtick template, and one inside a comment ends it mid-string. That is
  // exactly how this edit failed the first time, with 'card is not defined'.
  // Safe to do: transition-* and animation-* are not among the 44 properties
  // measured, so suppressing them cannot move a number this probe reports.
  const freeze = document.createElement('style');
  freeze.textContent = '*, *::before, *::after { transition: none !important; animation: none !important; }';
  document.head.appendChild(freeze);

  const els = [...document.querySelectorAll('*')];
  function snap() {
    const out = new Array(els.length);
    for (let i = 0; i < els.length; i++) {
      const cs = getComputedStyle(els[i]);
      const rec = new Array(PROPS.length);
      for (let p = 0; p < PROPS.length; p++) rec[p] = cs.getPropertyValue(PROPS[p]);
      out[i] = rec;
    }
    return out;
  }
  function countDeltas(a, b) {
    let n = 0, firstEl = -1, firstProp = null, was = null, now = null;
    for (let i = 0; i < a.length; i++) {
      for (let p = 0; p < PROPS.length; p++) {
        if (a[i][p] !== b[i][p]) {
          n++;
          if (firstEl < 0) { firstEl = i; firstProp = PROPS[p]; was = a[i][p]; now = b[i][p]; }
        }
      }
    }
    return { n, firstProp, was, now, sample: firstEl < 0 ? null : (els[firstEl].tagName.toLowerCase() + (els[firstEl].className && typeof els[firstEl].className === 'string' ? '.' + els[firstEl].className.trim().split(/\s+/).join('.') : '')).slice(0, 44) };
  }

  const base = snap();
  const rules = [];
  // Reverse order: deleteRule shifts every index above it, and walking down
  // means the indices of rules not yet visited never move.
  for (let i = legacy.cssRules.length - 1; i >= 0; i--) {
    const rule = legacy.cssRules[i];
    const text = rule.cssText;
    const sel = (rule.selectorText || (text.split('{')[0] || '').trim()).slice(0, 90);
    let rec;
    try {
      legacy.deleteRule(i);
      rec = countDeltas(base, snap());
      legacy.insertRule(text, i);
    } catch (e) {
      rules.push({ i, sel, deltas: -1, note: 'could not delete/restore: ' + e.message });
      continue;
    }
    // Restoring must land exactly back on the baseline. If it does not, the
    // sheet has drifted and every later measurement is against a moved
    // baseline — so stop rather than report numbers that look fine.
    const after = countDeltas(base, snap());
    if (after.n !== 0) return { error: 'restore drifted at rule ' + i + ' (' + sel + '): ' + after.n + ' deltas remain' };
    rules.push({ i, sel, deltas: rec.n, prop: rec.firstProp, was: rec.was, now: rec.now, sample: rec.sample });
  }
  rules.reverse();
  return { page: ${JSON.stringify(pageName)}, elements: els.length, ruleCount: legacy.cssRules.length, href: legacy.href, rules };
})()`;

(async () => {
  let wsUrl = null;
  for (let i = 0; i < 100 && !wsUrl; i++) {
    await sleep(100);
    const m = stderrChunks.join('').match(/ws:\/\/[^\s]+/);
    if (m) wsUrl = m[0];
  }
  if (!wsUrl) { console.error('Edge did not report a devtools endpoint.'); process.exit(1); }
  ws = await connect(wsUrl);

  const { targetId } = await send('Target.createTarget', { url: 'about:blank' });
  const { sessionId } = await send('Target.attachToTarget', { targetId, flatten: true });
  await send('Page.enable', {}, sessionId);
  await send('Runtime.enable', {}, sessionId);

  const loaded = onceEvent('Page.loadEventFired', sessionId);
  await send('Page.navigate', { url }, sessionId);
  await loaded;
  await sleep(WAIT);

  if (WARM) {
    /* Report what the warm-up produced. A warm-up that silently did nothing
       gives the same zeros as no warm-up at all, and they read identically. */
    const before = await evaluate(sessionId, 'document.querySelectorAll("*").length');
    try {
      await evaluate(sessionId, `(async () => { ${WARM} })()`);
    } catch (e) {
      console.error('WARM-UP THREW: ' + e.message);
      process.exit(1);
    }
    await sleep(WAIT);
    const after = await evaluate(sessionId, 'document.querySelectorAll("*").length');
    console.log(`  warm-up: ${before} -> ${after} elements`);
    if (after === before) console.log('  ⚠ warm-up added no elements — every zero below is still suspect');
  }

  const res = await evaluate(sessionId, DRAIN(page));
  if (res && res.error) { console.error('ERROR: ' + res.error); process.exit(1); }

  const dead = res.rules.filter((r) => r.deltas === 0);
  const live = res.rules.filter((r) => r.deltas > 0);
  const failed = res.rules.filter((r) => r.deltas < 0);

  console.log(`\n${res.href}`);
  console.log(`${res.ruleCount} rules · ${res.elements} elements · viewport ${VIEWPORT.width}x${VIEWPORT.height}\n`);
  console.log(`  ${'deltas'.padStart(7)}  selector`);
  console.log(`  ${'-'.repeat(7)}  ${'-'.repeat(60)}`);
  for (const r of res.rules) {
    const d = r.deltas < 0 ? 'ERR' : String(r.deltas);
    const tail = r.deltas > 0 ? `   [${r.prop}: ${r.was} -> ${r.now} on ${r.sample}]` : '';
    console.log(`  ${d.padStart(7)}  ${r.sel}${tail}`);
  }
  console.log(`\n  DEAD (0 deltas, candidates): ${dead.length}`);
  console.log(`  LIVE (load-bearing):         ${live.length}`);
  if (failed.length) console.log(`  FAILED to delete/restore:    ${failed.length}`);
  console.log(`\n  A zero is a CANDIDATE, not a verdict — check @media, JS-rendered`);
  console.log(`  content, :hover/:focus and properties outside the 44 first.`);
  console.log(`  See this file's header.\n`);

  if (jsonOut) { writeFileSync(jsonOut, JSON.stringify(res, null, 1)); console.log(`  json: ${jsonOut}\n`); }
  process.exit(0);
})().catch((e) => { console.error(e); process.exit(1); });
