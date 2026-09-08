/* =========================================================================
   auth_lock_probe.mjs — IDLE AUTO-LOCK KA GATE.

   KYUN YE FILE MOJOOD HAI. `tests/test_auth.py` ka apna usool yahan bhi lagta
   hai, harf ba harf: *"ek boundary jise koi gate nahi dekhta, wo agle refactor
   mein khamoshi se khul sakti hai — aur khulne par kuch bhi fail nahi hoga."*
   Auto-lock (2026-09-08) poori tarah client-side hai, aur is repo mein JS ka
   koi test harness nahi (`package.json` tak nahi). To pytest ise nahi dekh
   sakta. Bina is probe ke `static/apiClient.js` ka koi bhi refactor lock ko
   chup-chaap mar sakta hai aur har adad phir bhi green rehta.

   ⚠ YE APNA SERVER KHUD CHALATA HAI, AUTH OFF KAR KE. Do wajah:
     1. Auth ON ho to har page load 401 par gate khol deta hai — aur phir probe
        ye farq nahi kar sakta ke gate LOCK ki wajah se aaya ya 401 ki wajah se.
        Auth off rakhne se gate ki EK hi mumkin wajah bachti hai: idle lock.
     2. 2026-09-08 ka sabaq: jis din `.env` mein key aayi, poore 1,106 tests
        `assert 401 == 200` par gir gaye kyunke suite developer ki `.env` par
        munhasir thi. `tests/conftest.py` ko hermetic banaya gaya tha; ye file
        wahi qaida shuru se maanti hai.

   USAGE
     node scripts/auth_lock_probe.mjs

   Kuch chalta hua nahi chahiye — port 8011 khud le leta hai. Exit 0 = sab pass.
   ========================================================================= */

import { spawn } from 'node:child_process';
import { existsSync, mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

const EDGE = 'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe';
const PORT = 8011;
const PAGE = `http://127.0.0.1:${PORT}/static/index.html`;
const PY = '.venv\\Scripts\\python.exe';
const IDLE_MS = 30 * 60 * 1000;
const SHOT = process.argv.includes('--shot')
  ? process.argv[process.argv.indexOf('--shot') + 1]
  : null;

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

// ── server, auth OFF ────────────────────────────────────────────────────────
// PAPER_MAKER_API_KEY ko khali string par set karte hain, unset NAHI: khali bhi
// os.environ mein MOJOOD ginti hai, aur `load_dotenv()` (override=False) sirf
// wahi naam bharta hai jo environ mein na ho. Is tarah `.env` ki asli key —
// jo Irfan ne 2026-09-08 ko daali — is probe par nahi aati.
const server = spawn(PY, ['-m', 'uvicorn', 'app.main:app', '--host', '127.0.0.1', '--port', String(PORT)],
  { env: { ...process.env, PAPER_MAKER_API_KEY: '' }, stdio: ['ignore', 'ignore', 'pipe'] });
let serverErr = '';
server.stderr.on('data', (d) => { serverErr += d.toString(); });

const userDataDir = mkdtempSync(join(tmpdir(), 'lock-edge-'));
const edge = spawn(EDGE, ['--headless=new', '--disable-gpu', '--no-first-run',
  '--no-default-browser-check', '--disable-extensions', '--remote-debugging-port=0',
  `--user-data-dir=${userDataDir}`, '--window-size=1280,900', 'about:blank'],
  { stdio: ['ignore', 'ignore', 'pipe'] });

function cleanup() {
  try { edge.kill('SIGKILL'); } catch { /* gone */ }
  try { server.kill('SIGKILL'); } catch { /* gone */ }
  try { rmSync(userDataDir, { recursive: true, force: true }); } catch { /* locked */ }
}
process.on('exit', cleanup);

// ── CDP plumbing (css_shot.mjs jaisa hi) ────────────────────────────────────
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

// Page load par apiClient ka `pmInit` chalta hai; DOMContentLoaded ke baad ek
// chhota sa saans, taake gate/button DOM mein aa chuke hon.
async function loadPage(sessionId) {
  const loaded = onceEvent('Page.loadEventFired', sessionId);
  await send('Page.navigate', { url: PAGE }, sessionId);
  await loaded;
  await sleep(400);
}

// Wahi teen sawal jo har case poochhta hai.
const STATE = `({
  key:   !!localStorage.getItem('pm_api_key'),
  gate:  (() => { const g = document.getElementById('pm-key-gate');
                  return !!g && g.style.display !== 'none'; })(),
  lock:  !!document.querySelector('.pz-lock'),
})`;

const results = [];
function check(name, got, want) {
  const ok = got.key === want.key && got.gate === want.gate && got.lock === want.lock;
  results.push({ name, ok, got, want });
  const fmt = (s) => `key=${s.key ? 'hai' : 'nahi'} gate=${s.gate ? 'khula' : 'band'} lock-btn=${s.lock ? 'hai' : 'nahi'}`;
  console.log(`  ${ok ? 'PASS' : 'FAIL'}  ${name}`);
  if (!ok) console.log(`        mila:   ${fmt(got)}\n        chahiye: ${fmt(want)}`);
}

async function main() {
  // server uthne ka intezar
  let up = false;
  for (let i = 0; i < 150; i++) {
    try { const r = await fetch(PAGE); if (r.ok) { up = true; break; } } catch { /* abhi nahi */ }
    if (server.exitCode !== null) break;
    await sleep(200);
  }
  if (!up) throw new Error('uvicorn nahi utha (port ' + PORT + ')\n' + serverErr.slice(-1500));

  const portFile = join(userDataDir, 'DevToolsActivePort');
  let port;
  for (let i = 0; i < 200; i++) {
    if (existsSync(portFile)) { const f = readFileSync(portFile, 'utf8').split('\n')[0].trim(); if (f) { port = Number(f); break; } }
    await sleep(100);
  }
  if (!port) throw new Error('Edge did not report a DevTools port');
  const v = await (await fetch(`http://127.0.0.1:${port}/json/version`)).json();
  ws = await connect(v.webSocketDebuggerUrl);

  const { targetId } = await send('Target.createTarget', { url: 'about:blank' });
  const { sessionId } = await send('Target.attachToTarget', { targetId, flatten: true });
  await send('Page.enable', {}, sessionId);
  await send('Runtime.enable', {}, sessionId);

  // origin par pahunche baghair localStorage likha nahi ja sakta
  await loadPage(sessionId);

  // 1 — TAAZA KEY: kuch lock na ho, aur Lock button mojood ho.
  await evaluate(sessionId, `localStorage.setItem('pm_api_key','probe-key');
    localStorage.setItem('pm_api_key_seen', String(Date.now())); true`);
  await loadPage(sessionId);
  check('taaza key — khuli rehti hai, Lock button aata hai',
    await evaluate(sessionId, STATE), { key: true, gate: false, lock: true });

  // `--shot <dir>`: `.pz-lock` ka wajood `querySelector` se sabit ho jata hai,
  // magar wo ye nahi batata ke button DIKHTA kaisa hai -- theek jagah baitha hai
  // ya topbar tod raha hai. 2026-09-08 ka sabaq (`scripts/css_shot.mjs` ka
  // header) yahan bhi lagta hai: adad green ho sakte hain aur page phir bhi
  // toota ho. Ye naap nahi hai, dekhne ke liye hai.
  if (SHOT) {
    mkdirSync(SHOT, { recursive: true });
    const shot = await send('Page.captureScreenshot', { format: 'png' }, sessionId);
    const f = join(SHOT, 'lock-button.png');
    writeFileSync(f, Buffer.from(shot.data, 'base64'));
    console.log(`        tasveer: ${f}`);
  }

  // 2 — PURANI KEY: ye is poore kaam ki asal wajah hai. 31 minute purana
  // timestamp = teacher uth kar chala gaya. Key mit jani chahiye AUR gate usi
  // load par khulna chahiye (60s wale interval ka intezar nahi).
  await evaluate(sessionId, `localStorage.setItem('pm_api_key','probe-key');
    localStorage.setItem('pm_api_key_seen', String(Date.now() - ${IDLE_MS + 60000})); true`);
  await loadPage(sessionId);
  check('31 min purani key — mit jati hai, gate foran khulta hai',
    await evaluate(sessionId, STATE), { key: false, gate: true, lock: false });

  // 3 — DEV MODE: key hi nahi. Teacher ko aisa button nahi dikhna chahiye jo
  // kuch na kare, aur gate bhi nahi (server par auth off hai).
  await evaluate(sessionId, `localStorage.clear(); true`);
  await loadPage(sessionId);
  check('koi key nahi (dev) — na gate, na Lock button',
    await evaluate(sessionId, STATE), { key: false, gate: false, lock: false });

  // 4 — HAATH SE LOCK: PC chhorne se pehle wala rasta.
  await evaluate(sessionId, `localStorage.setItem('pm_api_key','probe-key');
    localStorage.setItem('pm_api_key_seen', String(Date.now())); true`);
  await loadPage(sessionId);
  await evaluate(sessionId, `document.querySelector('.pz-lock').click(); true`);
  await sleep(200);
  check('Lock button dabaya — key foran jati hai, gate khulta hai',
    await evaluate(sessionId, STATE), { key: false, gate: true, lock: true });

  await send('Target.closeTarget', { targetId });

  const failed = results.filter((r) => !r.ok).length;
  console.log(`\n  ${results.length - failed}/${results.length} pass`);
  if (failed) throw new Error(`${failed} case fail hue`);
}

main().then(() => { cleanup(); process.exit(0); })
  .catch((e) => { console.error('\n' + e.message); cleanup(); process.exit(1); });
