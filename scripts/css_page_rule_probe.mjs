/* Does @page survive the layer import? margin_probe.mjs said "(none reported)" after the
 * swap, but its walker only recursed into `rule.cssRules` — a CSSImportRule exposes its
 * contents as `.styleSheet`, not `.cssRules`, so an imported file was simply never
 * entered. That is a defect in the measurement, not a finding about the page, and it is
 * exactly the class of error this epic keeps writing down. This probe walks imports.
 */
import { spawn } from 'node:child_process';
import { existsSync, mkdtempSync, readFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

const EDGE = 'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe';
const url = process.argv[2];
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const userDataDir = mkdtempSync(join(tmpdir(), 'pagerule-edge-'));
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

const EXPR = String.raw`(() => {
  const found = [];
  const layers = [];
  const seen = new Set();
  const walk = (sheet, origin, layerCtx, depth) => {
    if (!sheet || seen.has(sheet)) return;
    seen.add(sheet);
    let rules;
    try { rules = sheet.cssRules; } catch (e) { found.push({ error: 'cannot read ' + origin }); return; }
    for (const r of rules) {
      const kind = r.constructor.name;
      if (kind === 'CSSImportRule') {
        // THIS is the branch the first walker missed.
        const l = r.layerName !== undefined && r.layerName !== null ? r.layerName : layerCtx;
        walk(r.styleSheet, (r.href || origin), l === '' ? '(anonymous)' : (l || layerCtx), depth + 1);
        continue;
      }
      if (kind === 'CSSLayerStatementRule') layers.push({ origin, names: [...r.nameList] });
      if (kind === 'CSSLayerBlockRule') { walk({ cssRules: r.cssRules }, origin, r.name || '(anonymous)', depth + 1); continue; }
      if (kind === 'CSSPageRule') found.push({ origin, layer: layerCtx ?? '(unlayered)', text: r.cssText, depth });
      if (r.cssRules && kind !== 'CSSPageRule') walk({ cssRules: r.cssRules }, origin, layerCtx, depth + 1);
    }
  };
  for (const ss of document.styleSheets) walk(ss, ss.href || '(inline)', null, 0);
  return { pageRules: found, layerStatements: layers,
           links: [...document.querySelectorAll('link[rel=stylesheet]')].map(l => l.getAttribute('href')) };
})()`;

async function main() {
  const portFile = join(userDataDir, 'DevToolsActivePort');
  let port;
  for (let i = 0; i < 200; i++) { if (existsSync(portFile)) { const f = readFileSync(portFile, 'utf8').split('\n')[0].trim(); if (f) { port = Number(f); break; } } await sleep(100); }
  const v = await (await fetch(`http://127.0.0.1:${port}/json/version`)).json();
  ws = await connect(v.webSocketDebuggerUrl);
  const { targetId } = await send('Target.createTarget', { url: 'about:blank' });
  const { sessionId } = await send('Target.attachToTarget', { targetId, flatten: true });
  await send('Page.enable', {}, sessionId);
  await send('Runtime.enable', {}, sessionId);
  const loaded = onceEvent('Page.loadEventFired', sessionId);
  await send('Page.navigate', { url }, sessionId);
  await loaded;
  await sleep(1500);
  await send('Emulation.setEmulatedMedia', { media: 'print' }, sessionId);
  console.log(JSON.stringify(await evaluate(sessionId, EXPR), null, 1));
}
main().then(() => { cleanup(); process.exit(0); }).catch((e) => { console.error(e); cleanup(); process.exit(1); });
