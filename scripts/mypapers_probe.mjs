/* =========================================================================
   mypapers_probe.mjs — PEHLI SCREEN KHALI TO NAHI AA RAHI? (D69 ka gate)

   KYUN YE FILE MOJOOD HAI. D69 wo qism ka bug tha jise is repo ka koi bhi
   mojooda gate nahi dekh sakta tha, aur wo baat khud row mein likhi hai:

     · pytest use nahi dekh sakta — masla server par nahi hai. `/api/papers`
       us waqt bhi 33 papers theek de raha tha; koi bhi API test pass hota.
     · CSS ratchet use nahi dekh sakta — ek bhi rule, hex ya inline style nahi
       badli. Metric hilta hi nahi.
     · `css_*_probe` use nahi dekh sakte — wo shakl naapte hain, MAZMOON nahi.
       Khali fehrist aur bhari fehrist ka layout ek jaisa hai.

   Yani ek aisa bug jo app ki PEHLI SCREEN par baitha tha, "My Papers" banne ke
   din se, aur poore do mahine har gate ke saamne se guzarta raha. Wo aakhir-kar
   2026-09-08 ko kisi auzaar se nahi, BROWSER MEIN AANKH SE pakra gaya.

   Is liye ye probe wohi sawal poochta hai jo us din aankh ne poochha tha:

       app abhi abhi khuli hai — kya "My Papers" mein papers DIKH rahe hain?

   ⚠ YE PROBE US SOORAT MEIN BHI PASS HO JATA AGAR DB KHALI HOTA, is liye wo
   pehle DB SE GINTI LETA HAI (`/api/papers`) aur phir DOM se. Dono ka milna
   zaroori hai. Sirf "koi row hai" poochhna is bug ko pakadta hi nahi: bug ka
   poora matlab ye tha ke API sach bolti thi aur screen khali rehti thi.

   Auth JAAN-BOOJH KAR OFF hai (key khali) — `auth_lock_probe.mjs` ke phase 1
   wali wajah: auth ON ho to page load par gate/login aa jata hai aur phir
   probe ye farq nahi kar sakta ke screen auth ki wajah se khali hai ya bug ki
   wajah se.

       node scripts/mypapers_probe.mjs
   ========================================================================= */

import { spawn } from 'node:child_process';
import { existsSync, mkdtempSync, readFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

const EDGE = 'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe';
const PORT = 8015;
const PY = '.venv\\Scripts\\python.exe';

const pageUrl = () => `http://127.0.0.1:${PORT}/static/index.html`;
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

// ── server (auth OFF) ───────────────────────────────────────────────────────
const servers = [];
function startServer(port, key) {
  const p = spawn(PY, ['-m', 'uvicorn', 'app.main:app', '--host', '127.0.0.1', '--port', String(port)],
    { env: { ...process.env, PAPER_MAKER_API_KEY: key }, stdio: ['ignore', 'ignore', 'pipe'] });
  p.err = '';
  p.stderr.on('data', (d) => { p.err += d.toString(); });
  servers.push(p);
  return p;
}
async function waitFor(port, proc) {
  for (let i = 0; i < 150; i++) {
    try { const r = await fetch(pageUrl()); if (r.ok) return; } catch { /* abhi nahi */ }
    if (proc.exitCode !== null) break;
    await sleep(200);
  }
  throw new Error(`uvicorn nahi utha (port ${port})\n` + proc.err.slice(-1500));
}

const srv = startServer(PORT, '');
const userDataDir = mkdtempSync(join(tmpdir(), 'mypapers-edge-'));
const edge = spawn(EDGE, ['--headless=new', '--disable-gpu', '--no-first-run',
  '--no-default-browser-check', '--disable-extensions', '--remote-debugging-port=0',
  `--user-data-dir=${userDataDir}`, '--window-size=1280,900', 'about:blank'],
  { stdio: ['ignore', 'ignore', 'pipe'] });

function cleanup() {
  try { edge.kill('SIGKILL'); } catch { /* gone */ }
  for (const s of servers) { try { s.kill('SIGKILL'); } catch { /* gone */ } }
  try { rmSync(userDataDir, { recursive: true, force: true }); } catch { /* locked */ }
}
process.on('exit', cleanup);

// ── CDP plumbing (auth_lock_probe.mjs jaisa hi) ─────────────────────────────
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
async function evaluate(sessionId, expression) {
  const r = await send('Runtime.evaluate',
    { expression, returnByValue: true, awaitPromise: true }, sessionId);
  if (r.exceptionDetails) throw new Error(r.exceptionDetails.text + ' :: ' + expression);
  return r.result.value;
}

// Load ke baad ek saans: `mpLoad()` ek API call karti hai, to DOM us ke lauthne
// par bharta hai, load event par nahi.
async function loadPage(sessionId) {
  const loaded = onceEvent('Page.loadEventFired', sessionId);
  await send('Page.navigate', { url: pageUrl() }, sessionId);
  await loaded;
  await sleep(900);
}

// Wohi sawal jo 2026-09-08 ko aankh ne poochha tha, DOM se.
//   · screen  — kaun si screen khuli hai (markup kehta hai "mypapers")
//   · status  — `#mpStatus` ka matn ("33 papers mile"). KHALI = mpLoad chali hi nahi.
//   · rows    — `#mpList` ke TABLE ki rows.
//
// ⚠ `#mpList.children.length` GINNA GHALAT HAI, aur pehla draft wohi ginta tha:
// us ne `DOM mein 1, DB mein 33` diya aur ek lamhe ke liye aisa laga jaise fix
// kaam nahi kar raha. Asal mein `mpList` ke andar EK wrapper `<div>` hai, us
// mein `<table>`, aur rows `<tbody>` mein. Yani wo "1" theek tha — sawal
// ghalat tha. Isi liye ab `tbody tr` ginte hain.
const STATE = `({
  screen: (() => { let n = ''; document.querySelectorAll('.screen').forEach(s => {
                     if (s.dataset.active === '1') n = s.dataset.screen; }); return n; })(),
  status: (document.getElementById('mpStatus') || {}).textContent || '',
  rows:   document.querySelectorAll('#mpList tbody tr').length,
})`;

const results = [];
function check(name, ok, detail) {
  results.push({ name, ok });
  console.log(`  ${ok ? 'PASS' : 'FAIL'}  ${name}`);
  if (!ok && detail) console.log(`        ${detail}`);
}

async function main() {
  await waitFor(PORT, srv);

  // DB ka sach PEHLE, DOM se poochhne se pehle. Is ke baghair khali DB par ye
  // probe khamoshi se pass ho jata -- theek wohi khamoshi jis ne D69 ko do
  // mahine chhupaye rakha.
  const api = await (await fetch(`http://127.0.0.1:${PORT}/api/papers`)).json();
  console.log(`\n  DB mein papers: ${api.total}`);
  if (!api.total) {
    throw new Error('Is DB mein koi paper nahi -- ye probe khali DB par kuch sabit nahi karta.');
  }

  const portFile = join(userDataDir, 'DevToolsActivePort');
  let port;
  for (let i = 0; i < 200; i++) {
    if (existsSync(portFile)) { const f = readFileSync(portFile, 'utf8').split('\n')[0].trim(); if (f) { port = Number(f); break; } }
    await sleep(100);
  }
  if (!port) throw new Error('Edge did not report a DevTools port');

  const list = await (await fetch(`http://127.0.0.1:${port}/json/list`)).json();
  ws = await connect(list[0].webSocketDebuggerUrl);
  const { targetId } = await send('Target.createTarget', { url: 'about:blank' });
  const { sessionId } = await send('Target.attachToTarget', { targetId, flatten: true });
  await send('Page.enable', {}, sessionId);
  await send('Runtime.enable', {}, sessionId);

  console.log('');
  await loadPage(sessionId);
  const s = await evaluate(sessionId, STATE);

  check('app khulte hi "mypapers" hi khuli screen hai',
    s.screen === 'mypapers', `mila: ${JSON.stringify(s.screen)}`);

  // ⚠ YEHI WO CASE HAI JO D69 PAR FAIL HOTA THA. Pehle `#mpStatus` bilkul
  // khali hota tha -- `mpLoad()` chalti to us mein "Loading..." aur phir
  // "33 papers mile" likhti hai. Khali matn = wo kabhi chali hi nahi.
  check('bina kuch dabaye fehrist bhar chuki hai (#mpStatus)',
    s.status.trim() !== '', `#mpStatus khali hai -- yani mpLoad() chali hi nahi`);

  check(`fehrist mein DB jitni rows hain (${api.total})`,
    s.rows === api.total, `DOM mein ${s.rows}, DB mein ${api.total}`);

  await send('Target.closeTarget', { targetId });

  const failed = results.filter((r) => !r.ok).length;
  console.log(`\n  ${results.length - failed}/${results.length} pass`);
  if (failed) throw new Error(`${failed} case fail hue`);
}

main().then(() => { cleanup(); process.exit(0); })
  .catch((e) => { console.error('\n' + e.message); cleanup(); process.exit(1); });
