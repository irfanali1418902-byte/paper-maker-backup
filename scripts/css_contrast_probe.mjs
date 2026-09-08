/* =========================================================================
   css_contrast_probe.mjs — WHICH TEXT FAILS WCAG AA, ON THE BACKGROUND THAT
   IS ACTUALLY PAINTED?

   UI-092. D26, D31 and D41 are three rows about the same token
   (`--color-text-muted`) failing AA by margins of 0.02, 0.06 and 1.46, and
   all three say the same thing about how to check it:

     D41  "Verify by re-running the contrast computation against the MEASURED
           background of each page — not against white, and not against the
           token's nominal value."
     D31  "whoever takes the palette decision should re-measure every
           muted-text surface at once and set the token from the worst case,
           rather than nudging it twice."

   Until now every one of those numbers was produced by hand, in a session,
   and thrown away. This file is that computation written down.

   WHY THE BACKDROP IS THE WHOLE PROBLEM. D26's first draft FAILED review for
   measuring both colours in the browser and then computing the ratio against
   an ASSUMED `#16294A` backdrop, when `theme.css` was painting a white box
   there — the colours were right, the backdrop was guessed, and the
   conclusion came out inverted (it reported a regression that was actually a
   near-doubling). D41 records the same trap from the other side: computing
   `.pagehead p` against white gives 4.76:1 and PASSES, while the measured
   canvas `rgb(247,248,251)` gives 4.48:1 and FAILS. So this probe never reads
   a token file. It walks the ancestor chain in the live page.

   WHAT IT DOES, per element with its own visible text:
     1. computed `color`, `font-size`, `font-weight`, `opacity`
     2. walk ancestors until a `background-color` with alpha > 0
     3. composite the text colour over that backdrop using BOTH the colour's
        own alpha and the accumulated element opacity
     4. contrast ratio, WCAG 2.1 relative luminance
     5. threshold: 3.0 for large text (>=24px, or >=18.66px at weight >=700),
        4.5 otherwise

   ⚠ THIS IMPROVES ON D31'S METHOD AND THE DIFFERENCE IS RECORDED THERE. That
   row's walk "stops at the first background with alpha > 0 and does not
   composite translucent layers", and it warns the number would be wrong on a
   translucent surface such as bank's `rgba(255,255,255,.07)` sidebar hovers.
   This one keeps walking, collects every translucent background up to the
   first opaque one, and composites them back-to-front — so those surfaces
   are in scope and so are stacked ones.

   ⚠ AND THE FIRST DRAFT OF THIS FILE GOT THAT WRONG IN A WAY WORTH KEEPING.
   It composited a translucent background straight onto WHITE instead of onto
   the element's real parent, and reported `index`'s navy sidebar links as
   `rgb(255,255,255)` on `rgb(255,255,255)` — **1.00:1**, white on white, for
   text that is perfectly legible. A ratio of exactly 1.00 in this probe's
   output is the signature of a backdrop bug, not of a real failure: nothing
   in a real design paints text on its own colour. Treat it as "the probe is
   wrong here" and check the walk.

   FOUR MORE LIMITS, all real:
     · ONE VIEWPORT, 1280x900. A reflow can change which backdrop is painted.
     · AT REST. JS-rendered text is not here for the same reason
       css_type_probe cannot see it, and neither are :hover/:focus colours.
       D31's sidebar hover example is exactly that: reachable only by
       injecting the state.
     · TEXT NODES ONLY. An element whose text is entirely inside child
       elements is skipped — the child is measured instead, which is correct,
       but it means a count of "elements" is not a count of visible strings.
     · IMAGES AND GRADIENTS ARE NOT BACKGROUNDS HERE. The walk reads
       `background-color` only. Text over a gradient or a photo reports the
       colour underneath it, which may be nothing like what the eye sees.
       `landing`'s hero is the standing case: its white heading reports 1.06:1
       against the body colour because the hero's dark backdrop is not a
       `background-color`. That number is the probe's, not the design's.
     · ⚠ THE `TOTAL` LINE IS NOT COMPARABLE BETWEEN RUNS, AND THE FIRST TWO
       RUNS OF THIS FILE PROVED IT. `bank` renders one text element per
       question row, so its count moved 3168 -> 85 between two runs minutes
       apart — the list had not finished loading in the second. The TOTAL fell
       396 -> 29 and only ELEVEN of that was the change under test. Diff
       per element (path + text), never by count.

   AND THE LIMIT THAT IS NOT THIS PROBE'S: 4.48 vs 4.5 is a computed ratio,
   not a legibility complaint. D41 says it plainly — "nobody has looked at
   either page in a browser for this". A number here is a reason to look, not
   a verdict about whether the app reads well.

   USAGE
     node scripts/css_contrast_probe.mjs [page ...] [--json <path>] [--all]

   Default is the ten live pages. `--all` lists passing text too, not just
   failures. Needs the app running:
     .venv/Scripts/python.exe -m uvicorn app.main:app
   ========================================================================= */

import { spawn } from 'node:child_process';
import { existsSync, mkdtempSync, readFileSync, writeFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

const EDGE = 'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe';
const BASE = 'http://127.0.0.1:8000/static';
const VIEWPORT = { width: 1280, height: 900 };

/* The same ten css_type_probe gates. A page that is live but not here is a page
   this check silently stops covering — PROBES.md's rule, and the reason taqseem
   was added to the type probe late. */
const DEFAULT_PAGES = ['slo', 'slo-health', 'library', 'taqseem', 'blueprint',
  'bank', 'landing', 'index', 'print', 'plan'];

const argv = process.argv.slice(2);
const jsonIdx = argv.indexOf('--json');
const jsonOut = jsonIdx >= 0 ? argv[jsonIdx + 1] : null;
const showAll = argv.includes('--all');
const positional = [];
for (let i = 0; i < argv.length; i++) {
  if (argv[i].startsWith('--')) { if (argv[i] === '--json') i++; continue; }
  positional.push(argv[i]);
}
const PAGES = positional.length ? positional : DEFAULT_PAGES;

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const userDataDir = mkdtempSync(join(tmpdir(), 'contrast-edge-'));
const edge = spawn(EDGE, ['--headless=new', '--disable-gpu', '--no-first-run',
  '--no-default-browser-check', '--disable-extensions', '--remote-debugging-port=0',
  `--user-data-dir=${userDataDir}`, `--window-size=${VIEWPORT.width},${VIEWPORT.height}`,
  'about:blank'], { stdio: ['ignore', 'ignore', 'pipe'] });
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
async function evaluate(sid, expr, ms = 120000) {
  const r = await send('Runtime.evaluate', { expression: expr, returnByValue: true, awaitPromise: true, timeout: ms }, sid);
  if (r.exceptionDetails) throw new Error(r.exceptionDetails.exception?.description ?? r.exceptionDetails.text);
  return r.result.value;
}

/* The in-page half. No backticks anywhere inside — this is itself a backtick
   template and one in a comment ends it mid-string (css_drain_probe's note). */
const EXPR = String.raw`(() => {
  function parse(c) {
    const m = String(c).match(/rgba?\(([^)]+)\)/);
    if (!m) return null;
    const p = m[1].split(',').map((x) => parseFloat(x));
    return { r: p[0], g: p[1], b: p[2], a: p.length > 3 ? p[3] : 1 };
  }
  function over(fg, bg) {
    const a = fg.a;
    return { r: fg.r * a + bg.r * (1 - a), g: fg.g * a + bg.g * (1 - a), b: fg.b * a + bg.b * (1 - a), a: 1 };
  }
  function lum(c) {
    const f = (v) => { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); };
    return 0.2126 * f(c.r) + 0.7152 * f(c.g) + 0.0722 * f(c.b);
  }
  function ratio(a, b) {
    const l1 = lum(a), l2 = lum(b);
    return (Math.max(l1, l2) + 0.05) / (Math.min(l1, l2) + 0.05);
  }
  function path(el) {
    const bits = [];
    for (let n = el; n && n.nodeType === 1 && bits.length < 4; n = n.parentElement) {
      let s = n.tagName.toLowerCase();
      if (n.id) { s += '#' + n.id; bits.unshift(s); break; }
      if (n.classList.length) s += '.' + [...n.classList].slice(0, 2).join('.');
      bits.unshift(s);
    }
    return bits.join('>');
  }

  const out = [];
  for (const el of document.querySelectorAll('*')) {
    // TEXT NODES ONLY -- an element whose text lives in children is skipped and
    // the child is measured instead.
    let text = '';
    for (const n of el.childNodes) if (n.nodeType === 3) text += n.nodeValue;
    text = text.replace(/\s+/g, ' ').trim();
    if (!text) continue;
    if (!el.getClientRects().length) continue;

    const cs = getComputedStyle(el);
    if (cs.visibility === 'hidden') continue;
    // Visually-hidden labels: screen reader ke liye DOM mein, aankh ke liye
    // nahi. Icon-rail nav apne naam isi tareeqe se rakhti hai (index). Inka
    // getClientRects() 1px deta hai, is liye upar wala check kaafi nahi -- aur
    // bina is ke probe nau jhoote failures deta hai.
    if (cs.clipPath && cs.clipPath !== 'none' && cs.position === 'absolute'
        && el.getBoundingClientRect().width <= 1) continue;
    // font-size 0: icon-rail ka doosra tareeqa. Panze ke rail par labels DOM
    // mein rehte hain (accessible naam) magar size sifar hota hai -- kyunke
    // saat pages un ko <span> mein nahi, seedhe text node mein rakhte hain aur
    // text node par koi selector nahi chalta.
    if (parseFloat(cs.fontSize) === 0) continue;
    // WCAG 1.4.3 "inactive user interface components" ko chhoot deta hai, aur
    // is app ke disabled buttons opacity .5 par hain -- unhein ginna ek jhoota
    // failure hai jo asli failures ko dhaanp leta hai.
    if (el.disabled || el.getAttribute('aria-disabled') === 'true') continue;
    for (let n = el; n && n.nodeType === 1; n = n.parentElement) {
      if (n.disabled) { el.__skip = 1; break; }
    }
    if (el.__skip) continue;

    // Accumulated opacity: an ancestor at .7 dims this text too. D26's 'before'
    // case was exactly this and assuming 1 is how that row got inverted.
    let op = 1;
    for (let n = el; n && n.nodeType === 1; n = n.parentElement) {
      const o = parseFloat(getComputedStyle(n).opacity);
      if (!isNaN(o)) op *= o;
    }
    if (op < 0.05) continue;

    // Walk up collecting EVERY background with alpha > 0 until an opaque one,
    // then composite them back-to-front. A translucent panel must land on its
    // real parent, not on white -- an earlier version of this file composited
    // straight onto white and reported a navy sidebar's links as 1.00:1
    // (white on white). D31 warns about exactly this surface,
    // bank's rgba(255,255,255,.07) sidebar hovers.
    const stack = [];
    let bgFrom = 'default-white';
    for (let n = el; n && n.nodeType === 1; n = n.parentElement) {
      const c = parse(getComputedStyle(n).backgroundColor);
      if (c && c.a > 0) {
        stack.push(c);
        if (bgFrom === 'default-white') bgFrom = path(n);
        if (c.a >= 1) break;
      }
    }
    let bg = { r: 255, g: 255, b: 255, a: 1 };
    for (let i = stack.length - 1; i >= 0; i--) bg = over(stack[i], bg);

    const fg0 = parse(cs.color);
    if (!fg0) continue;
    const fg = over({ r: fg0.r, g: fg0.g, b: fg0.b, a: fg0.a * op }, bg);

    const size = parseFloat(cs.fontSize);
    const weight = parseInt(cs.fontWeight, 10) || 400;
    const large = size >= 24 || (size >= 18.66 && weight >= 700);
    const need = large ? 3.0 : 4.5;
    const r = ratio(fg, bg);

    out.push({
      path: path(el),
      text: text.slice(0, 40),
      color: cs.color, bg: 'rgb(' + Math.round(bg.r) + ', ' + Math.round(bg.g) + ', ' + Math.round(bg.b) + ')',
      bgFrom, size, weight, opacity: Math.round(op * 100) / 100,
      ratio: Math.round(r * 100) / 100, need, pass: r >= need,
    });
  }
  return out;
})()`;

const fmt = (n) => String(n).padStart(5);

async function main() {
  const portFile = join(userDataDir, 'DevToolsActivePort');
  let port;
  for (let i = 0; i < 200; i++) {
    if (existsSync(portFile)) { const f = readFileSync(portFile, 'utf8').split('\n')[0].trim(); if (f) { port = Number(f); break; } }
    await sleep(100);
  }
  if (!port) throw new Error('Edge did not report a DevTools port');
  const v = await (await fetch(`http://127.0.0.1:${port}/json/version`)).json();
  ws = await connect(v.webSocketDebuggerUrl);

  console.log(`contrast: WCAG AA, ${VIEWPORT.width}x${VIEWPORT.height}, at rest`);
  console.log('');
  const all = {};
  let totalFail = 0, totalText = 0;

  for (const page of PAGES) {
    const { targetId } = await send('Target.createTarget', { url: 'about:blank' });
    const { sessionId } = await send('Target.attachToTarget', { targetId, flatten: true });
    await send('Page.enable', {}, sessionId);
    await send('Runtime.enable', {}, sessionId);
    const loaded = onceEvent('Page.loadEventFired', sessionId);
    await send('Page.navigate', { url: `${BASE}/${page}.html` }, sessionId);
    await loaded;
    await evaluate(sessionId, 'document.fonts.ready');
    await sleep(500);
    const rows = await evaluate(sessionId, EXPR);
    await send('Target.closeTarget', { targetId });

    all[page] = rows;
    const fails = rows.filter((r) => !r.pass).sort((a, b) => a.ratio - b.ratio);
    totalFail += fails.length; totalText += rows.length;
    console.log(`${page.padEnd(11)} ${String(rows.length).padStart(4)} text  ${String(fails.length).padStart(3)} fail`);
    for (const r of (showAll ? rows.slice().sort((a, b) => a.ratio - b.ratio) : fails)) {
      console.log(`   ${fmt(r.ratio)}${r.pass ? ' ok ' : ' <  '}${r.need}  ${String(r.size) + 'px/' + r.weight}  ${r.color} on ${r.bg}  ${r.path}`);
      console.log(`          bg from ${r.bgFrom}${r.opacity !== 1 ? `   opacity ${r.opacity}` : ''}   "${r.text}"`);
    }
  }

  console.log('');
  console.log(`TOTAL: ${totalFail} failing of ${totalText} text elements, ${PAGES.length} pages`);
  console.log('');
  console.log('  A ratio here is a reason to LOOK, not a verdict. 4.48 vs 4.50 is');
  console.log('  arithmetic; legibility is a browser and an eye. See this file\'s header');
  console.log('  for the four limits, and D41 for why that sentence is in this repo.');

  if (jsonOut) { writeFileSync(jsonOut, JSON.stringify({ viewport: VIEWPORT, pages: all }, null, 1)); console.log(`\n  json: ${jsonOut}`); }
}

main().then(() => { cleanup(); process.exit(0); }).catch((e) => { console.error(e); cleanup(); process.exit(1); });
