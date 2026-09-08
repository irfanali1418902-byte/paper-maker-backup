/* =========================================================================
   auth_lock_probe.mjs — IDLE AUTO-LOCK AUR KEY-GATE KA GATE.

   KYUN YE FILE MOJOOD HAI. `tests/test_auth.py` ka apna usool yahan bhi lagta
   hai, harf ba harf: *"ek boundary jise koi gate nahi dekhta, wo agle refactor
   mein khamoshi se khul sakti hai — aur khulne par kuch bhi fail nahi hoga."*
   Auto-lock (UI-108) poori tarah client-side hai, aur is repo mein JS ka koi
   test harness nahi (`package.json` tak nahi). To pytest ise nahi dekh sakta.

   DO PHASE, AUR YE JAAN-BOOJH KAR HAI:

   · PHASE 1 — AUTH OFF. Lock ke chaar case. Auth ON ho to har page load 401
     par gate khol deta hai, aur phir probe ye farq nahi kar sakta ke gate LOCK
     ki wajah se aaya ya 401 ki wajah se. Auth off rakhne se gate ki EK hi
     mumkin wajah bachti hai: idle lock.

   · PHASE 2 — AUTH ON, ek maloom test key ke saath. Gate ke PAIGHAAM ke do
     case, jo phase 1 mein mumkin hi nahi kyunke wahan 401 aata hi nahi.

   PHASE 2 KI ASAL KAHANI, taake koi ise "sirf matn ka test" samajh kar na
   hataye: 2026-09-08 ko Irfan ne kaha *"key mange raha hai, jo maine daala wo
   ghalat hai."* Key ghalat nahi thi — naap kar dekha, wohi key `curl` par 200
   deti thi aur gate ke poore flow se andar bhi le jati thi. Jhoot PAIGHAAM
   bol raha tha: har 401 par ek hi jumla aata tha, "Key ghalat ya missing hai",
   is liye jis banday ne abhi tak koi key daali hi NAHI thi use bhi bataya jata
   tha ke us ki key GHALAT hai. Wo ek jumla ek sahi key ko do dafa qusoorwar
   thehra chuka hai.

   ⚠ DONO SERVER YE FILE KHUD CHALATI HAI. UI-107 ka sabaq: jis din `.env`
   mein key aayi, poore 1,106 tests `assert 401 == 200` par gir gaye kyunke
   suite developer ki `.env` par munhasir thi. Yahan `PAPER_MAKER_API_KEY`
   hamesha saaf tay ki jati hai -- phase 1 mein khali, phase 2 mein test key --
   aur khali qeemat unset se alag hai: khali bhi `os.environ` mein MOJOOD
   ginti hai, aur `load_dotenv(override=False)` sirf wahi naam bharta hai jo
   environ mein na ho. Is tarah `.env` ki asli key kisi phase par nahi aati.

   USAGE
     node scripts/auth_lock_probe.mjs [--shot <dir>]

   Kuch chalta hua nahi chahiye — ports 8011 aur 8013 khud le leta hai.
   Exit 0 = sab pass.
   ========================================================================= */

import { spawn } from 'node:child_process';
import { existsSync, mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

const EDGE = 'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe';
const PORT_OFF = 8011; // auth OFF  — lock ke cases
const PORT_ON = 8013; // auth ON   — paighaam ke cases
const TEST_KEY = 'probe-server-key-sirf-yahan';
const PY = '.venv\\Scripts\\python.exe';
const IDLE_MS = 30 * 60 * 1000;
const SHOT = process.argv.includes('--shot')
  ? process.argv[process.argv.indexOf('--shot') + 1]
  : null;

const pageUrl = (port) => `http://127.0.0.1:${port}/static/index.html`;
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

// ── servers ─────────────────────────────────────────────────────────────────
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
    try { const r = await fetch(pageUrl(port)); if (r.ok) return; } catch { /* abhi nahi */ }
    if (proc.exitCode !== null) break;
    await sleep(200);
  }
  throw new Error(`uvicorn nahi utha (port ${port})\n` + proc.err.slice(-1500));
}

const srvOff = startServer(PORT_OFF, '');
const srvOn = startServer(PORT_ON, TEST_KEY);

const userDataDir = mkdtempSync(join(tmpdir(), 'lock-edge-'));
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

// Page load par apiClient ka `pmInit` chalta hai; load ke baad ek chhota sa
// saans, taake gate/button DOM mein aa chuke hon aur pehli `apiFetch` lauth aaye.
async function loadPage(sessionId, port) {
  const loaded = onceEvent('Page.loadEventFired', sessionId);
  await send('Page.navigate', { url: pageUrl(port) }, sessionId);
  await loaded;
  await sleep(700);
}

// Wahi sawal jo har case poochhta hai.
const STATE = `({
  key:   !!localStorage.getItem('pm_api_key'),
  gate:  (() => { const g = document.getElementById('pm-key-gate');
                  return !!g && g.style.display !== 'none'; })(),
  lock:  !!document.querySelector('.pz-lock'),
  msg:   (document.getElementById('pm-key-msg') || {}).textContent || '',
})`;

const results = [];
const fmt = (s) => `key=${s.key ? 'hai' : 'nahi'} gate=${s.gate ? 'khula' : 'band'} lock-btn=${s.lock ? 'hai' : 'nahi'}`;

function check(name, got, want) {
  const ok = got.key === want.key && got.gate === want.gate && got.lock === want.lock;
  results.push({ name, ok });
  console.log(`  ${ok ? 'PASS' : 'FAIL'}  ${name}`);
  if (!ok) console.log(`        mila:    ${fmt(got)}\n        chahiye: ${fmt(want)}`);
}

function checkMsg(name, got, wantSub) {
  const ok = got.gate && got.msg.includes(wantSub);
  results.push({ name, ok });
  console.log(`  ${ok ? 'PASS' : 'FAIL'}  ${name}`);
  if (!ok) console.log(`        gate=${got.gate ? 'khula' : 'BAND'}  paighaam: ${JSON.stringify(got.msg)}\n        chahiye jis mein ho: ${JSON.stringify(wantSub)}`);
}

async function main() {
  await waitFor(PORT_OFF, srvOff);
  await waitFor(PORT_ON, srvOn);

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

  // ── PHASE 1: auth OFF — lock ────────────────────────────────────────────
  console.log('\n  Phase 1 — auth OFF (lock ka amal)\n');

  // origin par pahunche baghair localStorage likha nahi ja sakta
  await loadPage(sessionId, PORT_OFF);

  // 1 — TAAZA KEY: kuch lock na ho, aur Lock button mojood ho.
  await evaluate(sessionId, `localStorage.setItem('pm_api_key','probe-key');
    localStorage.setItem('pm_api_key_seen', String(Date.now())); true`);
  await loadPage(sessionId, PORT_OFF);
  check('taaza key — khuli rehti hai, Lock button aata hai',
    await evaluate(sessionId, STATE), { key: true, gate: false, lock: true });

  // `--shot <dir>`: `.pz-lock` ka wajood `querySelector` se sabit ho jata hai,
  // magar wo ye nahi batata ke button DIKHTA kaisa hai -- theek jagah baitha hai
  // ya topbar tod raha hai. UI-101 ka sabaq (`scripts/css_shot.mjs` ka header)
  // yahan bhi lagta hai. Ye naap nahi hai, dekhne ke liye hai.
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
  await loadPage(sessionId, PORT_OFF);
  check('31 min purani key — mit jati hai, gate foran khulta hai',
    await evaluate(sessionId, STATE), { key: false, gate: true, lock: false });

  // 3 — DEV MODE: key hi nahi. Teacher ko aisa button nahi dikhna chahiye jo
  // kuch na kare, aur gate bhi nahi (server par auth off hai).
  await evaluate(sessionId, `localStorage.clear(); true`);
  await loadPage(sessionId, PORT_OFF);
  check('koi key nahi (dev) — na gate, na Lock button',
    await evaluate(sessionId, STATE), { key: false, gate: false, lock: false });

  // 4 — HAATH SE LOCK: PC chhorne se pehle wala rasta.
  await evaluate(sessionId, `localStorage.setItem('pm_api_key','probe-key');
    localStorage.setItem('pm_api_key_seen', String(Date.now())); true`);
  await loadPage(sessionId, PORT_OFF);
  await evaluate(sessionId, `document.querySelector('.pz-lock').click(); true`);
  await sleep(200);
  check('Lock button dabaya — key foran jati hai, gate khulta hai',
    await evaluate(sessionId, STATE), { key: false, gate: true, lock: true });

  // ── PHASE 2: auth ON — gate ka paighaam ─────────────────────────────────
  console.log('\n  Phase 2 — auth ON (gate kya KEHTA hai)\n');

  // 5 — PEHLI BAAR AANE WALA. Is ne koi key daali hi nahi, is liye ise ghalti
  // ka ilzaam nahi milna chahiye. Yehi wo case hai jis par Irfan atka tha.
  await loadPage(sessionId, PORT_ON);
  await evaluate(sessionId, `localStorage.clear(); true`);
  await loadPage(sessionId, PORT_ON);
  checkMsg('koi key daali hi nahi — paighaam ILZAAM na de',
    await evaluate(sessionId, STATE), 'apni key daalein');

  // 6 — WAQAI GHALAT KEY: ab ilzaam theek hai, aur wo saaf hona chahiye.
  await evaluate(sessionId, `localStorage.setItem('pm_api_key','ye-key-ghalat-hai');
    localStorage.setItem('pm_api_key_seen', String(Date.now())); true`);
  await loadPage(sessionId, PORT_ON);
  checkMsg('waqai ghalat key — paighaam saaf kahe ke key ghalat hai',
    await evaluate(sessionId, STATE), 'Key ghalat hai');

  // 7 — SAHI KEY: gate band, andar. Ye sabit karta hai ke phase 2 ke upar wale
  // do case sirf paighaam ka farq hain, kisi tooti hui auth ka nateeja nahi.
  await evaluate(sessionId, `localStorage.setItem('pm_api_key',${JSON.stringify(TEST_KEY)});
    localStorage.setItem('pm_api_key_seen', String(Date.now())); true`);
  await loadPage(sessionId, PORT_ON);
  check('sahi key (auth ON) — gate band, andar',
    await evaluate(sessionId, STATE), { key: true, gate: false, lock: true });

  await send('Target.closeTarget', { targetId });

  const failed = results.filter((r) => !r.ok).length;
  console.log(`\n  ${results.length - failed}/${results.length} pass`);
  if (failed) throw new Error(`${failed} case fail hue`);
}

main().then(() => { cleanup(); process.exit(0); })
  .catch((e) => { console.error('\n' + e.message); cleanup(); process.exit(1); });
