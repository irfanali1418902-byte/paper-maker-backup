/* css_state_probe.mjs — what does a HOVERED, FOCUSED or DISABLED element paint?
 *
 *   node scripts/css_state_probe.mjs <label> <outdir>
 *   node scripts/css_state_probe.mjs before docs/ui/probe --page bank
 *
 * Writes <outdir>/<label>.json in EXACTLY the shape css_type_probe.mjs writes,
 * so css_type_diff.mjs compares two runs with no changes to it:
 *
 *   node scripts/css_type_diff.mjs before.json after.json --names
 *
 * WHY THIS EXISTS — DEFERRED.md D45, and it is not hypothetical. Every probe in
 * this repo before this one measures the page AT REST. A declaration that only
 * applies on :hover, :focus-visible or :disabled therefore contributes ZERO
 * deltas whether it is right or wrong, and two tasks in two days were bitten:
 *
 *   UI-061  deleted four `input:focus` rules from four pages. Their being dead
 *           could only be argued from layer order plus 0 deltas at rest. If the
 *           argument had been wrong the focus ring would have vanished and NO
 *           GATE WOULD HAVE FIRED. It was confirmed by Irfan's eye, by hand.
 *   UI-062  re-pointed `.btn-cancel:hover` from each page's own --bg onto
 *           --color-surface-sunken, a third grey neither page used. All 34
 *           measured deltas, pytest, ruff and the ratchet passed without
 *           noticing. Review caught it by reading, not by measuring.
 *
 * HOW THE STATE IS ENTERED. CDP `CSS.forcePseudoState` sets the flag the style
 * engine itself reads, so the cascade resolves exactly as it would under a real
 * pointer or a real tab-stop. It is NOT a synthetic mouse move: no scrolling, no
 * pointer capture, no JS handlers fire. That matters because these pages render
 * from JS and a real mousemove would race their listeners.
 *
 * :disabled IS DIFFERENT AND IS HANDLED DIFFERENTLY. It is not a forceable flag
 * in every build — it reflects the `disabled` ATTRIBUTE. So it is applied by
 * setting the attribute, snapshotting, then restoring the element's previous
 * value. That is a real DOM mutation for the length of one snapshot; every
 * element is restored before the page is closed, and `restored` in the output
 * records that it happened.
 *
 * WHAT IS MEASURED, and it is NOT css_type_probe's property list. That list is
 * a type-and-box probe. A state changes ink and chrome: colour, border, shadow,
 * OUTLINE — which css_type_probe does not carry at all, and an outline is what
 * a focus ring IS — opacity, cursor. Box properties are kept too, because a
 * hover that adds a border moves the used box.
 *
 * SCOPE IS INTERACTIVE ELEMENTS ONLY, deliberately. Forcing :hover on all 5,379
 * elements of bank would produce an unreadable diff dominated by inherited
 * colour. The selector list below is the set that can actually take these
 * states. Widen it when a real rule falls outside it, not on principle.
 *
 * HIDDEN ELEMENTS ARE STILL MEASURED, and that is the point on this repo:
 * bank's and print's modals are display:none at rest, getComputedStyle still
 * resolves them, and .btn-save / .btn-cancel live nowhere else.
 */
import { spawn } from 'node:child_process';
import { existsSync, mkdtempSync, mkdirSync, readFileSync, writeFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

const EDGE = 'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe';
const VIEWPORT = { width: 1280, height: 900 };
const BASE = 'http://127.0.0.1:8000/static';

const argv = process.argv.slice(2);
const positional = argv.filter((a) => !a.startsWith('--'));
const label = positional[0];
const outdir = positional[1];
const pageIdx = argv.indexOf('--page');
const onlyPage = pageIdx >= 0 ? argv[pageIdx + 1] : null;

if (!label || !outdir) {
  console.error('usage: node scripts/css_state_probe.mjs <label> <outdir> [--page <p>]');
  process.exit(2);
}

/* Same nine pages as css_type_probe.mjs, same roles, so the two probes are read
   side by side rather than reconciled. */
const PAGES = [
  { page: 'slo', url: `${BASE}/slo.html`, role: 'LIVE — regression gate' },
  { page: 'slo-health', url: `${BASE}/slo-health.html`, role: 'LIVE — regression gate' },
  { page: 'library', url: `${BASE}/library.html`, role: 'LIVE — regression gate' },
  { page: 'taqseem', url: `${BASE}/taqseem.html`, role: 'LIVE — regression gate' },
  { page: 'blueprint', url: `${BASE}/blueprint.html`, role: 'LIVE — regression gate' },
  { page: 'bank', url: `${BASE}/bank.html`, role: 'subject — modal pair lives here' },
  { page: 'landing', url: `${BASE}/landing.html`, role: 'subject' },
  { page: 'index', url: `${BASE}/index.html`, role: 'subject' },
  { page: 'print', url: `${BASE}/print.html`, role: 'LIVE — shell only, no paper_id' },
].filter((p) => !onlyPage || p.page === onlyPage);

/* The states, and the forced pseudo-classes each one means.
 *
 * ⚠ FOCUS IS TWO STATES, NOT ONE, AND THE FIRST VERSION OF THIS FILE GOT IT
 * WRONG IN THE ONE WAY THAT MATTERED. It forced `focus-visible` alone, which
 * does NOT match a `:focus` rule — so every `input:focus` rule in the repo
 * measured identical to rest, in the probe built to close exactly that hole.
 * `03-elements/forms.css`:79 IS an `input:focus` rule and UI-061 deleted four
 * more like it. Caught at review, 2026-08-25.
 *
 *   hover          UI-062's blind spot, and every .btn-*:hover in the tree
 *   focus          POINTER focus — `:focus` matches, `:focus-visible` does not.
 *                  This is the pass that sees forms.css:79.
 *   focus-visible  KEYBOARD focus — a real tab-stop matches BOTH, so both are
 *                  forced. Anything else models a state no user can reach.
 *   active         cheap once the machinery exists; several legacy buttons
 *                  declare one and nothing has ever checked them
 *   disabled       D46 territory — four opacities across nine files
 */
const STATES = {
  hover: ['hover'],
  focus: ['focus'],
  'focus-visible': ['focus', 'focus-visible'],
  active: ['active'],
  disabled: null, // attribute, not a forced flag — see the header
};

/* Interactive elements only — forcing :hover on all 5,379 of bank's elements
   gives a diff dominated by inherited colour.
 *
 * THE LAST THREE ARE NOT INTERACTIVE ELEMENTS AND ARE HERE ANYWAY. Review
 * enumerated all 66 state selectors under static/css/ and found three live
 * `:hover` rules on rendered elements that the tag list could never reach:
 * `tbody tr:hover` (slo, a LIVE regression-gate page), `.q-row:hover` (bank),
 * `.bp-row:hover` (blueprint). A scope that misses a live rule on a gate page
 * is not a scope, it is a hole. Widen this list when a real rule falls outside
 * it — that is what happened here — not on principle. */
const INTERACTIVE = [
  'button', 'a', 'input', 'select', 'textarea', 'summary', 'label',
  '[tabindex]', '[role="button"]', '[onclick]',
  'tbody tr', '.q-row', '.bp-row',
].join(',');

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const userDataDir = mkdtempSync(join(tmpdir(), 'state-edge-'));
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
process.on('SIGINT', () => { cleanup(); process.exit(130); });

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

/* PROPERTY SET FIXED HERE, before anything is measured — css_type_probe.mjs's
   own rule, and for the same reason: a set chosen after seeing a diff is a set
   chosen to make the diff look good.

   OUTLINE IS THE ADDITION THAT MATTERS. css_type_probe carries no outline
   property at all, and 03-elements/forms.css:106 draws the app's focus ring as
   `outline: 2px solid var(--color-accent)`. A probe without outline-* cannot see
   a focus ring appear, change colour, or vanish — which is precisely the UI-061
   hole this file exists to close. */
const STATE_PROPS = [
  'color', 'background-color', 'opacity', 'cursor',
  'outline-color', 'outline-style', 'outline-width', 'outline-offset',
  'box-shadow', 'text-decoration-line', 'filter', 'transform',
  'border-top-color', 'border-right-color', 'border-bottom-color', 'border-left-color',
  'border-top-width', 'border-right-width', 'border-bottom-width', 'border-left-width',
  'border-top-style', 'border-right-style', 'border-bottom-style', 'border-left-style',
  'border-top-left-radius', 'border-top-right-radius',
  'border-bottom-right-radius', 'border-bottom-left-radius',
];

/* path() and desc() are byte-identical to css_type_probe.mjs's, so a path in a
   state diff can be pasted into a rest diff and land on the same element. */
const HELPERS = String.raw`
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
  };`;

const snapExpr = (state) => String.raw`(() => {
  ${HELPERS}
  const PROPS = ${JSON.stringify(STATE_PROPS)};
  const out = {};
  for (const el of document.querySelectorAll(${JSON.stringify(INTERACTIVE)})) {
    const cs = getComputedStyle(el);
    const rec = { '@': desc(el) };
    for (const p of PROPS) rec[p] = cs.getPropertyValue(p);
    out[path(el) + '::' + ${JSON.stringify(state)}] = rec;
  }
  return out;
})()`;

/* Every interactive element's path, from the page itself.
 *
 * CORRECTNESS DOES NOT DEPEND ON THIS ORDER MATCHING DOM.querySelectorAll's,
 * and an earlier version of this comment claimed the two were "guaranteed to
 * agree" — a claim the code neither needs nor checks. Every nodeId is forced
 * into the SAME state and the snapshot re-queries with the IDENTICAL selector,
 * so only SET EQUALITY matters, never order. The count comparison below is a
 * tripwire for the one real hazard: page JS mutating the DOM between the two
 * calls. */
const PATHS_EXPR = String.raw`(() => {
  ${HELPERS}
  return [...document.querySelectorAll(${JSON.stringify(INTERACTIVE)})].map(path);
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

  const out = { label, browser: v.Browser, viewport: VIEWPORT, states: STATES, pages: {} };

  for (const spec of PAGES) {
    const rec = { role: spec.role, errors: [] };
    out.pages[spec.page] = rec;
    let targetId;
    try {
      ({ targetId } = await send('Target.createTarget', { url: 'about:blank' }));
      const { sessionId } = await send('Target.attachToTarget', { targetId, flatten: true });
      await send('Page.enable', {}, sessionId);
      await send('Runtime.enable', {}, sessionId);
      await send('DOM.enable', {}, sessionId);
      await send('CSS.enable', {}, sessionId);
      await send('Emulation.setDeviceMetricsOverride', {
        width: VIEWPORT.width, height: VIEWPORT.height, deviceScaleFactor: 1, mobile: false,
      }, sessionId);
      const loaded = onceEvent('Page.loadEventFired', sessionId);
      await send('Page.navigate', { url: spec.url }, sessionId);
      await loaded;
      await evaluate(sessionId, 'document.fonts.ready');
      /* Same settle rule as css_type_probe: these pages fetch their data, so wait
         for the element count to stop moving rather than guess. */
      let prev = -1, stable = 0;
      for (let i = 0; i < 60 && stable < 3; i++) {
        const n = await evaluate(sessionId, 'document.querySelectorAll("*").length');
        if (n === prev) stable++; else { stable = 0; prev = n; }
        await sleep(100);
      }

      const { root } = await send('DOM.getDocument', { depth: -1, pierce: false }, sessionId);
      const { nodeIds } = await send('DOM.querySelectorAll',
        { nodeId: root.nodeId, selector: INTERACTIVE }, sessionId);
      const paths = await evaluate(sessionId, PATHS_EXPR);
      if (nodeIds.length !== paths.length) {
        rec.errors.push(`nodeId/path count mismatch: ${nodeIds.length} vs ${paths.length}`);
      }

      const all = {};
      let restored = 0;
      for (const [state, forced] of Object.entries(STATES)) {
        if (forced === null) {
          /* Attribute, not a forced flag — see the header. Only elements that
             HAVE a disabled attribute in HTML can take it; a disabled <a> is not
             a thing and forcing one would invent a state the app cannot reach. */
          const touched = await evaluate(sessionId, String.raw`(() => {
            ${HELPERS}
            const prev = [];
            for (const el of document.querySelectorAll('button,input,select,textarea,fieldset,optgroup,option')) {
              prev.push([path(el), el.hasAttribute('disabled') ? el.getAttribute('disabled') : null]);
              el.setAttribute('disabled', '');
            }
            window.__statePrev = prev;
            return prev.length;
          })()`);
          Object.assign(all, await evaluate(sessionId, snapExpr(state)));
          restored = await evaluate(sessionId, String.raw`(() => {
            ${HELPERS}
            const byPath = new Map(window.__statePrev);
            let n = 0;
            for (const el of document.querySelectorAll('button,input,select,textarea,fieldset,optgroup,option')) {
              const was = byPath.get(path(el));
              if (was === null || was === undefined) el.removeAttribute('disabled');
              else el.setAttribute('disabled', was);
              n++;
            }
            delete window.__statePrev;
            return n;
          })()`);
          if (restored !== touched) rec.errors.push(`disabled restore mismatch: set ${touched}, restored ${restored}`);
          continue;
        }

        /* PIPELINED, NOT SERIALISED, and the difference is minutes. Awaiting
           each forcePseudoState in turn costs one full round-trip per element
           per state: on bank that is 1,533 x 5 x 2 calls, and review measured
           the serialised version at ~445 s for that page alone against
           css_type_probe's ~30 s for all nine. The calls are independent, so
           they go out together and are awaited once. */
        await Promise.all(nodeIds.map((nodeId) =>
          send('CSS.forcePseudoState', { nodeId, forcedPseudoClasses: forced }, sessionId)));
        Object.assign(all, await evaluate(sessionId, snapExpr(state)));
        await Promise.all(nodeIds.map((nodeId) =>
          send('CSS.forcePseudoState', { nodeId, forcedPseudoClasses: [] }, sessionId)));
      }

      rec.snapshot = {
        all,
        interactive: paths.length,
        elements: prev,
        links: await evaluate(sessionId, '[...document.querySelectorAll("link[rel=stylesheet]")].map((l) => l.getAttribute("href"))'),
        title: await evaluate(sessionId, 'document.title'),
      };
      rec.disabledRestored = restored;
      rec.driftCount = 0;
      await send('Target.closeTarget', { targetId }, undefined);
    } catch (e) {
      rec.errors.push(String(e && e.message ? e.message : e));
      rec.snapshot = { all: {} };
      if (targetId) { try { await send('Target.closeTarget', { targetId }); } catch { /* gone */ } }
    }
  }

  mkdirSync(outdir, { recursive: true });
  const file = join(outdir, `${label}.json`);
  writeFileSync(file, JSON.stringify(out, null, 1), 'utf8');

  console.log(`state probe: ${label}   ${v.Browser}`);
  console.log(`states: ${Object.keys(STATES).join(', ')}`);
  console.log('');
  console.log('page              interactive   records   errors');
  console.log('--------------- ------------- --------- --------');
  for (const [page, r] of Object.entries(out.pages)) {
    const n = Object.keys(r.snapshot?.all || {}).length;
    console.log(`${page.padEnd(15)} ${String(r.snapshot?.interactive ?? 0).padStart(13)} ${String(n).padStart(9)} ${String(r.errors.length).padStart(8)}`);
    for (const e of r.errors) console.log(`    ! ${e}`);
  }
  console.log('');
  console.log(`written: ${file}`);
  console.log('compare: node scripts/css_type_diff.mjs <before>.json <after>.json --names');
}

main().then(() => { cleanup(); process.exit(0); }).catch((e) => { console.error(e); cleanup(); process.exit(1); });
