/* =========================================================================
   css_shot.mjs — PAGE KI TASVEER LO.

   UI-101. Is repo ke paas naapne ke saat auzaar hain aur DEKHNE ka ek bhi
   nahi tha. Wo khala baar baar mehsoos hui:

     D41  "nobody has looked at either page in a browser for this"
     D62  "us se pehle browser mein dono nav saath dekh lena chahiye"
     D26  ek poora draft is liye ghalat gaya ke backdrop dekha nahi, farz kiya

   Aur 2026-09-08 ko wo khala mehngi pari: aath pages Panze shell par le jaye
   gaye, har adad theek naapa gaya -- computed styles, contrast, print, tests --
   aur phir Irfan ne kaha "mujhe kuch nazar nahi aa raha". Adad sahi ho sakte
   hain aur page phir bhi toota ho sakta hai; `css_type_probe` ye nahi bata
   sakta ke cheez DIKHTI kaisi hai.

   Ye file wo sawal bhar deti hai. Ye naap NAHI hai -- koi pass/fail nahi, koi
   ratchet nahi. Sirf PNG.

   USAGE
     node scripts/css_shot.mjs <outdir> [page ...] [--width 1280] [--full]

   Default: das zinda pages, 1280x900, sirf viewport (jo teacher pehli nazar
   mein dekhta hai). `--full` poora page leta hai -- bank par wo 43000px lamba
   hota hai, is liye default nahi.

   App chalti chahiye: .venv/Scripts/python.exe -m uvicorn app.main:app
   ========================================================================= */

import { spawn } from 'node:child_process';
import { existsSync, mkdtempSync, mkdirSync, readFileSync, writeFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

const EDGE = 'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe';
const BASE = 'http://127.0.0.1:8000/static';
const DEFAULT_PAGES = ['slo', 'slo-health', 'library', 'taqseem', 'blueprint',
  'bank', 'landing', 'index', 'print', 'plan'];

const argv = process.argv.slice(2);
const wIdx = argv.indexOf('--width');
const WIDTH = wIdx >= 0 ? Number(argv[wIdx + 1]) : 1280;
const FULL = argv.includes('--full');
const positional = [];
for (let i = 0; i < argv.length; i++) {
  if (argv[i].startsWith('--')) { if (argv[i] === '--width') i++; continue; }
  positional.push(argv[i]);
}
const outdir = positional[0];
if (!outdir) {
  console.error('usage: node scripts/css_shot.mjs <outdir> [page ...] [--width 1280] [--full]');
  process.exit(2);
}
const PAGES = positional.length > 1 ? positional.slice(1) : DEFAULT_PAGES;
mkdirSync(outdir, { recursive: true });

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const userDataDir = mkdtempSync(join(tmpdir(), 'shot-edge-'));
const edge = spawn(EDGE, ['--headless=new', '--disable-gpu', '--no-first-run',
  '--no-default-browser-check', '--disable-extensions', '--remote-debugging-port=0',
  `--user-data-dir=${userDataDir}`, `--window-size=${WIDTH},900`, 'about:blank'],
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

  for (const page of PAGES) {
    const { targetId } = await send('Target.createTarget', { url: 'about:blank' });
    const { sessionId } = await send('Target.attachToTarget', { targetId, flatten: true });
    await send('Page.enable', {}, sessionId);
    await send('Runtime.enable', {}, sessionId);
    await send('Emulation.setDeviceMetricsOverride',
      { width: WIDTH, height: 900, deviceScaleFactor: 1, mobile: false }, sessionId);
    const loaded = onceEvent('Page.loadEventFired', sessionId);
    await send('Page.navigate', { url: `${BASE}/${page}.html` }, sessionId);
    await loaded;
    await send('Runtime.evaluate', { expression: 'document.fonts.ready', awaitPromise: true }, sessionId);
    await sleep(700);

    const shot = await send('Page.captureScreenshot',
      { format: 'png', captureBeyondViewport: FULL }, sessionId);
    const file = join(outdir, `${page}-${WIDTH}.png`);
    writeFileSync(file, Buffer.from(shot.data, 'base64'));
    console.log(`  ${page.padEnd(11)} ${file}`);
    await send('Target.closeTarget', { targetId });
  }
  console.log('\n  Ye naap nahi hai -- koi pass/fail nahi. Dekhne ke liye hai.');
}

main().then(() => { cleanup(); process.exit(0); }).catch((e) => { console.error(e); cleanup(); process.exit(1); });
