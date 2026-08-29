/* UI-071 — the injection probe. For CSS that no snapshot can reach.
 *
 * WHY THIS EXISTS, AND IT IS NOT A NEW IDEA — IT IS AN OLD ONE FINALLY WRITTEN DOWN.
 * `05-components/status.css`'s header already says "the state classes are set by JS and
 * match nothing at rest … verify colour by injecting the class", and D12 has recorded the
 * general hole since 2026-07-28: CSS built in JS is invisible to every metric. Until now
 * each session did that injection by hand, differently, and threw it away. Three families
 * measured on 2026-08-29 return ZERO elements at rest on every page:
 *
 *     .shortfall-panel  blueprint, print     built in shortfallHtml() / renderSection()
 *     .pill             index, slo           built in the candidate + import renderers
 *     .chips            slo-health, taqseem  built in the group + section renderers
 *
 * `css_type_probe` and `css_state_probe` walk `document.querySelectorAll('*')`, so for all
 * three they report 0 elements and therefore 0 deltas — whether the CSS is right or wrong.
 * That is D45's shape exactly: a gate that cannot see the thing passes regardless. Item 7's
 * second half is mostly these three, so it could not be verified without this.
 *
 *   node scripts/css_inject_probe.mjs <label> <outdir>
 *   node scripts/css_type_diff.mjs <outdir>/<before>.json <outdir>/<after>.json --names
 *
 * The output shape is deliberately `css_type_probe`'s, so the existing reviewed diff tool
 * reads it with no changes. One viewport (1280): none of these families has a rule inside
 * any `@media` block — checked, the same way css_state_probe justifies staying at one width.
 *
 * THE FIXTURES ARE COPIED FROM THE PAGE'S OWN BUILDER, LINE-CITED BELOW, AND THAT IS THE
 * PART THAT ROTS. If a builder's markup changes and this file does not, the probe measures a
 * shape the app no longer renders and reports a confident zero. Re-read the cited lines
 * before trusting a run. The container is the real one the builder writes into, so inherited
 * and contextual styles are real — blueprint's panel genuinely lives inside `.status-bar.warn`,
 * which is why its `background: var(--surface)` is a white panel on a tinted bar.
 *
 * Edge gets its own --user-data-dir and is killed by the pid we spawned (UI-031a hazard).
 */
import { spawn } from 'node:child_process';
import { existsSync, mkdtempSync, mkdirSync, readFileSync, writeFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

const EDGE = 'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe';
const BASE = 'http://127.0.0.1:8000/static';
const VIEWPORT = { width: 1280, height: 900 };

/* The property set is FIXED HERE, before measuring — PROBES.md rule 3. It is the union of
 * what these three families actually declare, plus the box properties a wrong layer would
 * disturb. Do not tune it after seeing a result. */
const PROPS = [
  'display', 'flex-direction', 'flex-wrap', 'gap', 'align-items', 'justify-content',
  'color', 'background-color',
  'border-top-width', 'border-left-width', 'border-top-color', 'border-left-color',
  'border-top-left-radius',
  'padding-top', 'padding-right', 'padding-bottom', 'padding-left',
  'margin-top', 'margin-right', 'margin-bottom', 'margin-left',
  'font-size', 'font-weight', 'line-height',
  'list-style-type', 'list-style-position',
];

/* ── THE FIXTURES ────────────────────────────────────────────────────────────────────────
 * `into`  — a selector for the REAL container the builder writes into.
 * `cls`   — a class the builder also sets on that container (blueprint's status bar).
 * `html`  — the builder's own output shape, text replaced with placeholders.
 * Each entry cites the source line so the next reader can check it has not rotted. */
const FIXTURES = {
  /* blueprint.html:1280 shortfallHtml(), delivered via :1189 setStatusHtml('warn', …),
   * which sets `class="status-bar warn"` on #actionStatus. */
  blueprint: [{
    into: '#actionStatus',
    cls: 'status-bar warn',
    html: '<strong>hdr</strong><div class="shortfall-panels">'
      + '<div class="shortfall-panel">'
      + '<div class="sf-head">head</div>'
      + '<div class="sf-reason">reason</div>'
      + '<div class="sf-q">Kya karein?</div>'
      + '<ul class="sf-options"><li>opt</li>'
      + '<li>opt <span class="sf-gain">gain</span></li></ul>'
      + '</div></div>',
  }],

  /* print.html:993 — same six inner rules, different box, and `no-print` on the panel.
   * It lands in a `.section-block`, which is ITSELF built in JS (print.html:1085), so the
   * fixture supplies that wrapper too and hangs it on `#sheet` (print.html:84) — the
   * outermost container that exists at rest. `#sheet` carries an inline
   * `style="display:none"` until a paper loads; that is stripped here, because a
   * display:none ancestor makes every used value below it meaningless (D53's second half). */
  print: [{
    into: '#sheet',
    show: true,
    wrap: 'section-block',
    html: '<div class="shortfall-panel no-print">'
      + '<div class="sf-head">head</div>'
      + '<div class="sf-reason">reason</div>'
      + '<div class="sf-q">Kya karein?</div>'
      + '<ul class="sf-options"><li>opt</li>'
      + '<li>opt <span class="sf-gain">gain</span></li></ul>'
      + '</div>',
  }],

  /* index.html:2190-2192 — three `.pill`s, and each carries its colour as an INLINE style.
   * They are kept verbatim: the inline pair is what a `.pill` rule has to coexist with.
   *
   * ⚠ THE CONTAINER IS `#replaceCandidates`, NOT `#results`, AND THE FIRST DRAFT GOT THAT
   * WRONG — review caught it on 2026-08-29, the day this file shipped. `renderCandidates()`
   * (index.html:2184) writes into `#replaceCandidates` (index.html:592), which lives inside
   * `.modal-body` in the `#replaceModal` overlay. `#results` also exists and also resolves,
   * so the probe reported a clean, confident measurement from a DOM context in which the
   * app never renders a `.pill`. That is rule 10's own warning arriving immediately: a
   * fixture that resolves is not a fixture that is faithful.
   *
   * The modal is closed at rest (`data-open="0"`), so `set` opens it first — measuring
   * inside a display:none ancestor is measuring nothing. */
  index: [{
    into: '#replaceCandidates',
    set: [{ sel: '#replaceModal', attr: 'data-open', value: '1' }],
    html: '<div class="cand"><div class="c-tags">'
      + '<span class="pill" style="color:#2E5AAC;background:#EAF1FB;">bloom</span>'
      + '<span class="pill" style="color:#5B6678;background:#EEF1F6;">diff</span>'
      + '<span class="pill" style="color:#2E7D5B;background:#E6F4EC;">marks</span>'
      + '</div></div>',
  }],

  /* slo.html:180 — the import-result counters. UI-071 renamed these `.pill` -> `.sum-pill`
   * because index's `.pill` is a question's metadata chip and this is a counter: one class
   * name, two components. The rename is why a before/after diff of THIS entry is not
   * meaningful — the element identity changed on purpose. Compare absolute values instead. */
  slo: [{
    into: '#pills',
    html: '<span class="sum-pill">Total: 0</span><span class="sum-pill add">Added: 0</span>',
  }],

  /* slo-health.html:170-181 — `.chips` wrapping the bloom `.tag`s, inside a `.group-block`.
   * The container is `#uncoveredBox` (slo-health.html:109), what `renderUncovered()` writes
   * into — NOT `.slo-main`, which is merely an ancestor. Corrected with the index fixture
   * on 2026-08-29 for the same reason. */
  'slo-health': [{
    into: '#uncoveredBox',
    html: '<div class="group-block"><div class="chips">'
      + '<span class="tag">bloom · 1</span><span class="tag muted">bloom · 2</span>'
      + '</div></div>',
  }],

  /* taqseem.html:150 — this one stacks, and UI-071 renamed it `.chips` -> `.col-chips`
   * for the same reason as `.pill` above: it shares only `display: flex` with
   * slo-health's `.chips`, and joined its page's own `.col-*` family. Same caveat —
   * this entry's before/after is a rename, so read the absolute values.
   *
   * ⚠ ITS CHILDREN ARE `.chip` CARDS, NOT `.tag` SPANS, AND THE FIRST DRAFT USED `.tag`.
   * `taqseem.html:143` fills `.col-chips` with `chipHtml()` output (taqseem.html:127) —
   * `.chip > .chip-main > .code/.strand/.seq` plus a `select.move-sel`. `.tag` is
   * slo-health's class and 99-legacy/taqseem.css has no rule for it at all, so the first
   * draft measured two inert spans and would have passed any `.chip` regression. Review
   * caught it 2026-08-29. */
  taqseem: [{
    into: '.tq-main',
    html: '<div class="col"><div class="col-chips">'
      + '<div class="chip"><div class="chip-main">'
      + '<span class="code">C-1</span><span class="strand">strand</span>'
      + '<span class="seq">seq 1</span></div>'
      + '<select class="move-sel"><option>Exam 1</option></select></div>'
      + '<div class="chip"><div class="chip-main">'
      + '<span class="code">C-2</span><span class="seq none">seq —</span></div>'
      + '<select class="move-sel"><option>Unassigned</option></select></div>'
      + '</div></div>',
  }],
};

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const label = process.argv[2];
const outdir = process.argv[3];
if (!label || !outdir) {
  console.error('usage: node scripts/css_inject_probe.mjs <label> <outdir>');
  process.exit(2);
}

const userDataDir = mkdtempSync(join(tmpdir(), 'inj-edge-'));
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
async function evaluate(sid, expr) {
  const r = await send('Runtime.evaluate', { expression: expr, returnByValue: true, awaitPromise: true }, sid);
  if (r.exceptionDetails) throw new Error(r.exceptionDetails.exception?.description ?? r.exceptionDetails.text);
  return r.result.value;
}

/* Inject, then snapshot ONLY the injected subtrees. Marked with a data attribute so the
 * walk cannot wander into the page's own elements and report noise as a delta. */
const injectExpr = (fixtures) => String.raw`(() => {
  const F = ${JSON.stringify(fixtures)};
  const made = [];
  for (const f of F) {
    /* NO BACKTICKS IN THIS BLOCK — it lives inside a String.raw template and a stray one
       ends the literal. (Cost one syntax error on 2026-08-29.)
       The set list runs first: it is how a fixture opens the panel or modal its family
       only ever renders inside. Measuring under a display:none ancestor measures nothing. */
    for (const s of (f.set || [])) {
      const t = document.querySelector(s.sel);
      if (t) t.setAttribute(s.attr, s.value);
    }
    const host = document.querySelector(f.into);
    if (!host) { made.push({ into: f.into, ok: false }); continue; }
    if (f.cls) host.className = f.cls;
    if (f.show) host.style.display = '';
    const holder = document.createElement('div');
    holder.setAttribute('data-inject-probe', '1');
    if (f.wrap) holder.className = f.wrap;
    holder.innerHTML = f.html;
    host.appendChild(holder);
    made.push({ into: f.into, ok: true });
  }
  return made;
})()`;

const snapExpr = String.raw`(() => {
  const PROPS = ${JSON.stringify(PROPS)};
  const out = {};
  const path = (el) => {
    const parts = [];
    for (let n = el; n && n.nodeType === 1; n = n.parentElement) {
      const p = n.parentElement;
      parts.unshift(p ? n.tagName + '[' + [...p.children].indexOf(n) + ']' : n.tagName);
      if (n.hasAttribute && n.hasAttribute('data-inject-probe')) break;
    }
    return parts.join('>');
  };
  for (const holder of document.querySelectorAll('[data-inject-probe]')) {
    for (const el of holder.querySelectorAll('*')) {
      const cs = getComputedStyle(el);
      const rec = { '@': el.tagName.toLowerCase() + (el.className ? '.' + String(el.className).trim().split(/\s+/).join('.') : '') };
      for (const p of PROPS) rec[p] = cs.getPropertyValue(p);
      out[path(el)] = rec;
    }
  }
  return out;
})()`;

async function main() {
  const portFile = join(userDataDir, 'DevToolsActivePort');
  let port;
  for (let i = 0; i < 200; i++) { if (existsSync(portFile)) { const f = readFileSync(portFile, 'utf8').split('\n')[0].trim(); if (f) { port = Number(f); break; } } await sleep(100); }
  const v = await (await fetch(`http://127.0.0.1:${port}/json/version`)).json();
  ws = await connect(v.webSocketDebuggerUrl);

  const out = { label, browser: v.Browser, viewport: VIEWPORT, viewports: [VIEWPORT], pages: {} };
  console.log('page          injected  elems  drift');
  console.log('------------ --------- ------ ------');

  for (const [page, fixtures] of Object.entries(FIXTURES)) {
    const { targetId } = await send('Target.createTarget', { url: 'about:blank' });
    const { sessionId } = await send('Target.attachToTarget', { targetId, flatten: true });
    await send('Page.enable', {}, sessionId);
    await send('Runtime.enable', {}, sessionId);
    const loaded = onceEvent('Page.loadEventFired', sessionId);
    await send('Page.navigate', { url: `${BASE}/${page}.html` }, sessionId);
    await loaded;
    await evaluate(sessionId, 'document.fonts.ready');
    await sleep(500);

    const made = await evaluate(sessionId, injectExpr(fixtures));
    const errors = made.filter((m) => !m.ok).map((m) => `container not found: ${m.into}`);
    await sleep(200);

    /* Two snapshots, no action between — PROBES.md rule 1. */
    const one = await evaluate(sessionId, snapExpr);
    await sleep(200);
    const two = await evaluate(sessionId, snapExpr);
    let driftCount = 0;
    for (const k of Object.keys(two)) {
      for (const p of PROPS) if (one[k] && one[k][p] !== two[k][p]) driftCount++;
    }

    /* `elements` is what css_type_diff prints in its `elems` column (:137). Without it
       that column reads `undefined` — which is how this was found, and an undefined in a
       gate's summary line is worth fixing rather than explaining. */
    out.pages[page] = {
      role: 'inject',
      errors,
      driftCount,
      drift: [],
      snapshot: { elements: Object.keys(two).length, all: two },
      keysPerViewport: { [String(VIEWPORT.width)]: Object.keys(two).length },
    };
    console.log(`${page.padEnd(12)} ${String(made.filter((m) => m.ok).length).padStart(9)} ${String(Object.keys(two).length).padStart(6)} ${String(driftCount).padStart(6)}`);
    if (errors.length) for (const e of errors) console.log(`  ⚠ ${e}`);
    await send('Target.closeTarget', { targetId });
  }

  mkdirSync(outdir, { recursive: true });
  const file = join(outdir, `${label}.json`);
  writeFileSync(file, JSON.stringify(out, null, 1), 'utf8');
  console.log(`\nwritten: ${file}`);
  console.log('compare: node scripts/css_type_diff.mjs <before>.json <after>.json --names');
}

main().then(() => { cleanup(); process.exit(0); }).catch((e) => { console.error(e); cleanup(); process.exit(1); });
