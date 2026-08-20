/* UI-032 — THE MARGIN / SPACE-TOKEN TEST for print.html.
 *
 * The one test MEASURED.md calls deciding and records as never run. It answers a
 * question the earlier before/after diff could not: 12 element-instances changed each of
 * padding-top/right/bottom/left (48 deltas) and WHICH elements those are was never
 * identified. If any of them is `.sheet` or sits on the margin chain, the printed page
 * margin moved.
 *
 * 99-legacy/print.css:1-2 states the margin is single-sourced: `@page { margin: 0 }` and
 * the whole page margin is `.sheet { padding: var(--page-margin) }` (14mm). That comment
 * also records the page was once broken the other way (@page 14mm + .sheet 14mm = 28mm),
 * so this is a regression that has happened before.
 *
 * Everything here runs in PRINT MEDIA (Emulation.setEmulatedMedia). Screen media does not
 * apply print.css:215 or :375, so a screen measurement describes a page nobody prints.
 *
 * Fonts are awaited before any box is believed — the session that measured .school-ur read
 * 22px because it measured in the same tick the text was injected, before the
 * font-display:swap webfont arrived. The real number was 47px.
 *
 * Edge gets its OWN --user-data-dir and is killed by the pid we spawned; UI-031a's review
 * agent ran `Get-Process msedge | Stop-Process -Force` and would have taken Irfan's own
 * browser with it.
 *
 *   node margin_probe.mjs <label> <outdir> <paperId...>
 */

import { spawn } from 'node:child_process';
import { existsSync, mkdtempSync, mkdirSync, readFileSync, writeFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

const EDGE = 'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe';
const VIEWPORT = { width: 1280, height: 900 };
const BASE = 'http://127.0.0.1:8000/static/print.html';

const label = process.argv[2];
const outdir = process.argv[3];
const papers = process.argv.slice(4);
mkdirSync(outdir, { recursive: true });

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

// ---------------------------------------------------------------- launch Edge

const userDataDir = mkdtempSync(join(tmpdir(), 'margin-edge-'));
const edge = spawn(EDGE, [
  '--headless=new',
  '--disable-gpu',
  '--no-first-run',
  '--no-default-browser-check',
  '--disable-extensions',
  '--remote-debugging-port=0',
  `--user-data-dir=${userDataDir}`,
  `--window-size=${VIEWPORT.width},${VIEWPORT.height}`,
  'about:blank',
], { stdio: ['ignore', 'ignore', 'pipe'] });

const stderrChunks = [];
edge.stderr.on('data', (b) => stderrChunks.push(b.toString()));

function cleanup() {
  try { edge.kill('SIGKILL'); } catch { /* already gone */ }
  try { rmSync(userDataDir, { recursive: true, force: true }); } catch { /* locked */ }
}
process.on('exit', cleanup);

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

function onceEvent(method, sessionId, timeoutMs = 60000) {
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

// ---------------------------------------------------------------- the snapshot
//
// The property set is FIXED HERE, before anything is measured — the rule pages/slo.css
// wrote after two counts of the same migration disagreed. Box properties only: this test
// is about geometry, not paint. The ink-colour finding (F1) is already recorded and is
// deliberately not re-measured here.
//
// Paths are tag + child-index chains so the same element aligns across two snapshots
// without depending on class names, which the migration is allowed to leave untouched but
// the JS is not required to keep stable.

const SNAP = String.raw`(() => {
  const PROPS = [
    'padding-top','padding-right','padding-bottom','padding-left',
    'margin-top','margin-right','margin-bottom','margin-left',
    'border-top-width','border-right-width','border-bottom-width','border-left-width',
    'box-sizing','display','position','overflow','width','height',
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

  // The margin chain, called out by name rather than left to be found in the diff.
  // .sheet's padding IS the printed page margin (print.css:1-2). Its ancestors matter
  // because anything they add sits outside it and the @page box is 0.
  const chainSel = ['html', 'body', '.print-main', '.sheet', '.letterhead', '.paper-body'];
  const chain = {};
  for (const sel of chainSel) {
    const el = document.querySelector(sel);
    if (!el) { chain[sel] = null; continue; }
    const cs = getComputedStyle(el);
    const r = el.getBoundingClientRect();
    chain[sel] = {
      desc: desc(el), path: path(el),
      padding: [cs.paddingTop, cs.paddingRight, cs.paddingBottom, cs.paddingLeft],
      margin: [cs.marginTop, cs.marginRight, cs.marginBottom, cs.marginLeft],
      border: [cs.borderTopWidth, cs.borderRightWidth, cs.borderBottomWidth, cs.borderLeftWidth],
      rect: { x: r.x, y: r.y, w: r.width, h: r.height },
      offset: { w: el.offsetWidth, h: el.offsetHeight },
      boxSizing: cs.boxSizing, maxWidth: cs.maxWidth, overflow: cs.overflow,
    };
  }

  // The knobs. setVar() writes these onto documentElement.style, an inline declaration
  // that outranks every layer — asserted at UI-018, measured here.
  const rootCS = getComputedStyle(document.documentElement);
  const sheetEl = document.querySelector('.sheet');
  const knobs = {
    rootInline: document.documentElement.getAttribute('style') || '',
    pageMarginRoot: rootCS.getPropertyValue('--page-margin').trim(),
    qFontRoot: rootCS.getPropertyValue('--q-font').trim(),
    qGapRoot: rootCS.getPropertyValue('--q-gap').trim(),
    pageMarginAtSheet: sheetEl ? getComputedStyle(sheetEl).getPropertyValue('--page-margin').trim() : null,
  };

  // @page cannot be read from computed style; read it out of the stylesheets instead,
  // and record which sheet it came from and whether it arrived inside a layer.
  const pageRules = [];
  for (const ss of document.styleSheets) {
    const walk = (rules, origin, inLayer) => {
      for (const r of rules) {
        if (r.constructor.name === 'CSSPageRule' || r.type === 6) {
          pageRules.push({ origin, inLayer, text: r.cssText });
        }
        if (r.cssRules) {
          const layerName = (r.constructor.name === 'CSSLayerBlockRule') ? (r.name || '(anon)') : inLayer;
          walk(r.cssRules, origin, layerName);
        }
      }
    };
    try { walk(ss.cssRules, ss.href || '(inline)', null); } catch (e) { /* cross-origin */ }
  }

  return {
    all, chain, knobs, pageRules,
    elements: document.querySelectorAll('*').length,
    questions: document.querySelectorAll('.question').length,
    media: matchMedia('print').matches ? 'print' : 'screen',
    title: document.title, url: location.href,
    fonts: document.fonts.status,
  };
})()`;

// ------------------------------------------------------------------------ run

function pdfPages(b64) {
  const buf = Buffer.from(b64, 'base64');
  const s = buf.toString('latin1');
  // /Count in the page-tree root is the authoritative number; fall back to counting
  // /Type /Page objects if the catalog is written differently.
  const counts = [...s.matchAll(/\/Count\s+(\d+)/g)].map((m) => Number(m[1]));
  const objs = [...s.matchAll(/\/Type\s*\/Page(?![s])/g)].length;
  return { count: counts.length ? Math.max(...counts) : null, typePageObjects: objs, bytes: buf.length };
}

async function main() {
  const port = await waitForPort();
  const version = await (await fetch(`http://127.0.0.1:${port}/json/version`)).json();
  ws = await connect(version.webSocketDebuggerUrl);

  const out = { label, browser: version.Browser, viewport: VIEWPORT, papers: {} };

  for (const paperId of papers) {
    const rec = { errors: [] };
    out.papers[paperId] = rec;
    const url = `${BASE}?paper_id=${paperId}`;
    try {
      const { targetId } = await send('Target.createTarget', { url: 'about:blank' });
      const { sessionId } = await send('Target.attachToTarget', { targetId, flatten: true });

      await send('Page.enable', {}, sessionId);
      await send('Runtime.enable', {}, sessionId);
      await send('Emulation.setDeviceMetricsOverride', {
        width: VIEWPORT.width, height: VIEWPORT.height, deviceScaleFactor: 1, mobile: false,
      }, sessionId);

      const loaded = onceEvent('Page.loadEventFired', sessionId);
      await send('Page.navigate', { url }, sessionId);
      await loaded;

      // Wait for the paper to actually render — this page fetches it. A blank page
      // measures nothing and produces a 1-page PDF, which is how ?id= vs ?paper_id=
      // cost time twice (MEASURED.md).
      let questions = 0;
      for (let i = 0; i < 100; i++) {
        questions = await evaluate(sessionId, `document.querySelectorAll('.question').length`);
        if (questions > 0) break;
        await sleep(200);
      }
      if (!questions) rec.errors.push('no .question rendered — paper did not load');

      // PRINT MEDIA. Everything below describes the printed artefact, not the screen.
      await send('Emulation.setEmulatedMedia', { media: 'print' }, sessionId);

      // Await the webfonts before any box is believed.
      await evaluate(sessionId, `document.fonts.ready.then(() => true)`);
      await sleep(600);

      // Determinism first: two snapshots with no action between them. Without this a
      // data-driven page's jitter reads as a CSS delta (UI-031b).
      const first = await evaluate(sessionId, SNAP);
      const second = await evaluate(sessionId, SNAP);
      const drift = [];
      for (const [p, a] of Object.entries(first.all)) {
        const b = second.all[p];
        if (!b) { drift.push(`${p} (missing in 2nd)`); continue; }
        for (const k of Object.keys(a)) if (a[k] !== b[k]) drift.push(`${p}:${k} ${a[k]} -> ${b[k]}`);
      }
      rec.driftCount = drift.length;
      rec.drift = drift.slice(0, 20);
      rec.snapshot = first;

      // Pagination the literal way: produce the PDF and count its pages. marginless and
      // preferCSSPageSize so @page owns the box — the right setting for measuring CSS,
      // and NOT proof of what a physical printer does.
      const pdf = await send('Page.printToPDF', {
        printBackground: true,
        marginTop: 0, marginBottom: 0, marginLeft: 0, marginRight: 0,
        preferCSSPageSize: true,
      }, sessionId);
      const pdfPath = join(outdir, `${label}-${paperId.slice(0, 8)}.pdf`);
      writeFileSync(pdfPath, Buffer.from(pdf.data, 'base64'));
      rec.pdf = { path: pdfPath, ...pdfPages(pdf.data) };

      await send('Target.closeTarget', { targetId });
    } catch (e) {
      rec.errors.push(String(e.message ?? e));
    }
  }

  writeFileSync(join(outdir, `${label}.json`), JSON.stringify(out, null, 1));
  console.log(JSON.stringify({
    label,
    browser: out.browser,
    papers: Object.fromEntries(Object.entries(out.papers).map(([k, v]) => [k.slice(0, 8), {
      elements: v.snapshot?.elements, questions: v.snapshot?.questions,
      media: v.snapshot?.media, fonts: v.snapshot?.fonts,
      drift: v.driftCount, pdf: v.pdf && { pages: v.pdf.count, objs: v.pdf.typePageObjects },
      sheetPadding: v.snapshot?.chain?.['.sheet']?.padding,
      errors: v.errors,
    }])),
  }, null, 1));
}

main().then(() => { cleanup(); process.exit(0); })
  .catch((e) => { console.error(e); cleanup(); process.exit(1); });
