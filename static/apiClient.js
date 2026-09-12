// Shared API client for all frontend pages (index / dashboard / print).
//
// Ek shared key per deployment. localStorage mein rehti hai aur har /api call ke
// x-api-key header mein jaati hai. Server par key set na ho (dev) to yeh header
// harmless hai — ignore ho jata hai, is liye dev experience par koi asar nahi.
// apiFetch() hi har /api call ka single choke-point hai; 401 par key-gate khulta.
//
// Classic (non-module) script hai, is liye `apiFetch` global scope mein aata hai
// aur baaki page-scripts isse naam se call kar sakti hain.
//
// ─── IDLE AUTO-LOCK (2026-09-08) ────────────────────────────────────────────
// KYUN. `localStorage` HAMESHA ke liye rehta hai. School PC par kai teachers
// ek hi machine share karte hain (Irfan ne 2026-09-08 ko tasdeeq ki), to bina
// lock ke silsila ye banta hai: teacher subah key daalta hai -> chala jata hai
// -> koi BACHA usi PC par app kholta hai aur bina kuch kiye ANDAR hai, agla
// parcha khula hua. Ek exam system ke liye ye sab se mehnga rasta hai aur is
// mein koi hunar nahi chahiye.
//
// Key ab bhi localStorage mein hai (session-scope karne se teacher har baar
// key daalta, jo rozana rukawat hai), magar us ke saath aakhri INSAANI harkat
// ka waqt likha jata hai. 30 minute tak koi click/keypress na ho to key mit
// jati hai aur gate wapas aa jata hai.
//
// ⚠ WAQT SIRF INSAANI HARKAT PAR BARHTA HAI, `apiFetch` par NAHI. Agar har API
// call touch karti to koi bhi timer-driven page kabhi lock na hota. Naapa gaya
// 2026-09-08: `grep -rn "setInterval" static/*.html static/*.js` khali hai --
// aaj koi page poll nahi karta, is liye "30 min koi harkat nahi" ka matlab
// waqai "banda uth kar chala gaya" hai. Agar kabhi polling aaye to ye faisla
// dobara dekhna hoga, warna lock waqt se pehle lag sakta hai.
//
// ⚠ YE AUTHENTICATION NAHI HAI. Key ab bhi ek shared secret hai -- system ko
// aaj bhi nahi pata ke banda KAUN hai, aur koi role ya audit trail nahi
// (`identity tables: KOI NAHI`, naapa gaya 2026-09-08). Ye sirf shared-PC wala
// surakh band karta hai. Asli users/roles/activity-log alag kaam hai.
//
// ─── WO "ALAG KAAM" HO GAYA (SEC-02, 2026-09-12) ────────────────────────────
// Upar wala paragraph apni jagah SACH hai aur is liye mita nahi -- wo key wale
// mode ko bayan karta hai, jo un schoolon par aaj bhi chal raha hai jinhon ne
// users nahi banaye. Magar ab ek doosra mode bhi hai: `users`. Wahan har
// teacher ka apna account hai, session server par rehti hai (HttpOnly cookie,
// JS us tak pahunch hi nahi sakta), role hai, aur har login `auth_events`
// mein darj hota hai.
//
// IS FILE KE LIYE FARQ SIRF ITNA HAI: 401 par kahan bhejna hai. Server har
// 401 ke saath `x-pm-auth-mode` header deta hai --
//     users -> login page (key-gate NAHI; wahan key ka koi wajood nahi)
//     key   -> wahi purana key-gate, haraf ba haraf
// Header par chalne ka faida ye hai ke page load par mode poochhne ke liye ek
// extra request nahi karni parti.
//
// ⚠ IDLE LOCK KA MATLAB DONO MODES MEIN ALAG HAI, aur ye farq jaan lena
// zaroori hai. Key mode mein lock SIRF BROWSER mein hai: key localStorage se
// mit jati hai, magar server ke nazdeek wo key us ke baad bhi utni hi durust
// rehti hai -- yani DevTools se qeemat copy kar lene wale ke liye lock ka koi
// wajood nahi. Users mode mein waqt ka faisla SERVER karta hai
// (`sessions.last_seen_at`, 30 min) aur neeche wala lock sirf us ka aaina hai.
// Yehi wo surakh tha jo ye file khud apne upar likh kar maan chuki thi.

const _rawFetch = window.fetch.bind(window);
const PM_KEY_STORAGE = "pm_api_key";
const PM_SEEN_STORAGE = "pm_api_key_seen"; // aakhri insaani harkat, ms
const PM_IDLE_MS = 30 * 60 * 1000;

// localStorage private-mode/disabled par throw kar sakta hai. Key gate us
// soorat mein har baar khulega -- kaam chalta rahega, bas yaad nahi rahega.
function pmStore(k, v) {
  try {
    localStorage.setItem(k, v);
  } catch {
    /* storage band hai */
  }
}
function pmRead(k) {
  try {
    return localStorage.getItem(k) || "";
  } catch {
    return "";
  }
}
function pmDrop(k) {
  try {
    localStorage.removeItem(k);
  } catch {
    /* storage band hai */
  }
}

// Har naya tab bhi "harkat" hai -- warna ek purana `seen` naye tab ko foran
// lock kar deta.
const pmTouch = () => pmStore(PM_SEEN_STORAGE, String(Date.now()));

function pmIdleExpired() {
  const seen = Number(pmRead(PM_SEEN_STORAGE));
  // Koi timestamp na ho (purana browser jahan key pehle se pari hai) to use
  // expired NAHI maanenge -- pehli harkat par likh jayega. Warna upgrade ke
  // din har teacher bila wajah bahar ho jata.
  if (!seen) return false;
  return Date.now() - seen > PM_IDLE_MS;
}

const PM_IDLE_MSG = "30 minute tak koi harkat nahi hui, is liye lock ho gaya.";

// ⚠ EXPIRY MILE TO GATE WAHIN KHULTA HAI — key chup-chaap girana kaafi NAHI.
// Pehla draft yahan sirf `pmDrop` karta tha, aur `auth_lock_probe.mjs` ka case 2
// us par fail hua. Sabab ye tha: page ki apni scripts `apiFetch` ko
// DOMContentLoaded se PEHLE chala deti hain, to key `pmInit` ke chalne se pehle
// hi khamoshi se mit chuki hoti thi; `pmInit` ko phir kuch milta hi nahi tha aur
// gate kabhi nahi aata. Us soorat mein page khula rehta -- teacher ke data ke
// saath, bas API calls tooti hui. `pmLock` ko yahin bulane se expiry ka pata jis
// bhi raste se chale, natija ek hi hai.
function pmGetKey() {
  if (pmRead(PM_KEY_STORAGE) && pmIdleExpired()) {
    pmLock(PM_IDLE_MSG);
    return "";
  }
  return pmRead(PM_KEY_STORAGE);
}

function pmShowKeyGate(msg) {
  let gate = document.getElementById("pm-key-gate");
  if (!gate) {
    gate = document.createElement("div");
    gate.id = "pm-key-gate";
    gate.style.cssText =
      "position:fixed;inset:0;background:rgba(0,0,0,.6);display:flex;align-items:center;justify-content:center;z-index:9999;font-family:sans-serif";
    gate.innerHTML =
      '<div style="background:#fff;padding:24px;border-radius:12px;max-width:360px;width:90%;box-shadow:0 10px 40px rgba(0,0,0,.3)">' +
      '<h3 style="margin:0 0 8px">Access key chahiye</h3>' +
      '<p id="pm-key-msg" style="margin:0 0 12px;color:#555;font-size:14px">Is tool ko use karne ke liye apni key daalein.</p>' +
      '<input id="pm-key-input" type="password" placeholder="x-api-key" style="width:100%;padding:10px;border:1px solid #ccc;border-radius:8px;box-sizing:border-box" />' +
      '<button id="pm-key-save" style="margin-top:12px;width:100%;padding:10px;border:0;border-radius:8px;background:#1a4d2e;color:#fff;font-size:15px;cursor:pointer">Save & continue</button>' +
      "</div>";
    document.body.appendChild(gate);
    const save = () => {
      const v = gate.querySelector("#pm-key-input").value.trim();
      if (v) {
        pmStore(PM_KEY_STORAGE, v);
        // Key ke saath hi ghadi shuru -- warna nayi key foran expired lagti
        // agar purana `seen` 30 min se bhi purana para ho.
        pmTouch();
        location.reload();
      }
    };
    gate.querySelector("#pm-key-save").addEventListener("click", save);
    gate
      .querySelector("#pm-key-input")
      .addEventListener("keydown", (e) => {
        if (e.key === "Enter") save();
      });
  }
  if (msg) gate.querySelector("#pm-key-msg").textContent = msg;
  gate.style.display = "flex";
  gate.querySelector("#pm-key-input").focus();
}

// Login page ka raasta, `?next=` ke saath taake teacher jahan ja raha tha
// wahin wapas pahunche. `replace` se login page history mein nahi rehta.
function pmGoLogin() {
  const next = encodeURIComponent(location.pathname + location.search);
  location.replace("/login.html?next=" + next);
}

async function apiFetch(url, opts = {}) {
  const key = pmGetKey();
  const headers = Object.assign({}, opts.headers || {});
  if (key) headers["x-api-key"] = key;
  // Har API call cache-proof: browser ka HTTP cache bypass. Server bhi /api par
  // no-store bhejta hai, magar us se PEHLE cache hui purani entry ko fetch() default
  // mode reuse kar leta tha (stale GET → merge purani value wapas POST → clobber).
  // `cache:'no-store'` us stored entry ko bhi ignore karta hai. opts se override mumkin.
  const res = await _rawFetch(
    url,
    Object.assign({ cache: "no-store" }, opts, { headers }),
  );
  if (res.status === 401) {
    // Users mode: yahan key ka koi wajood hi nahi -- gate kholna teacher se
    // ek aisi cheez maangna hoga jo us ke paas kabhi thi hi nahi. Login page.
    if (res.headers.get("x-pm-auth-mode") === "users") {
      pmGoLogin();
      return res;
    }
    // ⚠ PAIGHAAM DO ALAG HAALTON KA FARQ KARTA HAI, AUR PEHLE NAHI KARTA THA.
    // Pehle har 401 par ek hi jumla aata tha: "Key ghalat ya missing hai".
    // Yani jis banday ne ABHI TAK KOI KEY DAALI HI NAHI, use bhi ye bataya
    // jata tha ke us ki key GHALAT hai. Irfan 2026-09-08 ko theek isi par
    // atka -- key sahi thi, paighaam jhoota tha, aur wo key ko qusoorwar
    // samjhe. `key` yahan wo qeemat hai jo is call ke waqt MOJOOD thi, is
    // liye ye farq bharosay ke qabil hai.
    const thi = !!key;
    pmDrop(PM_KEY_STORAGE);
    pmDrop(PM_SEEN_STORAGE);
    pmShowKeyGate(
      thi
        ? "Key ghalat hai — dobara daalein."
        : "Is tool ko use karne ke liye apni key daalein.",
    );
  }
  return res;
}

// ── Lock: haath se, ya khud bekari se ────────────────────────────────────────

function pmLock(msg) {
  const tha = !!pmRead(PM_KEY_STORAGE);
  pmDrop(PM_KEY_STORAGE);
  pmDrop(PM_SEEN_STORAGE);
  if (tha) pmShowKeyGate(msg || "Lock ho gaya — key dobara daalein.");
  return tha;
}

// Harkat par ghadi aage. Throttle 30s: `pointerdown`/`keydown` teez chalte
// hain aur har ek par localStorage likhna faltu hai.
let pmLastTouch = 0;
function pmOnActivity() {
  const now = Date.now();
  if (now - pmLastTouch < 30000) return;
  pmLastTouch = now;
  if (pmRead(PM_KEY_STORAGE)) pmTouch();
}
addEventListener("pointerdown", pmOnActivity, { passive: true });
addEventListener("keydown", pmOnActivity, { passive: true });

// Har minute dekho. Sirf tab lock karo jab key WAQAI pari ho -- dev mode
// (koi key nahi) mein ye kuch nahi karta.
setInterval(() => {
  if (pmRead(PM_KEY_STORAGE) && pmIdleExpired()) {
    pmLock(PM_IDLE_MSG);
  }
}, 60000);

// Lock button `.pz-top` mein JS SE lagta hai, HTML mein nahi -- aur ye
// jaan-boojh kar hai. Ye file nau pages par chalti hai; button HTML mein
// daalne ka matlab nau files chhoona aur `css_baseline.py` ki frozen inventory
// (id / onclick / name / data-*) hilana hota. Wahi tareeqa jo upar key-gate
// pehle se use karta hai.
//
// Button sirf tab dikhta hai jab key stored ho: agar server par auth off hai
// (local dev) to key hoti hi nahi, aur teacher ko ek aisa button nahi dikhta
// jo kuch na kare.
function pmMountLockButton() {
  if (!pmRead(PM_KEY_STORAGE)) return;
  const top = document.querySelector(".pz-top");
  if (!top || top.querySelector(".pz-lock")) return;
  const btn = document.createElement("button");
  btn.type = "button";
  btn.className = "pz-lock";
  btn.textContent = "Lock";
  btn.title = "Key bhool jao — PC chhorne se pehle dabayein";
  btn.addEventListener("click", () => pmLock("Lock kar diya — key dobara daalein."));
  // `.lang-toggle` se pehle, taake language switch kona sab pages par apni
  // jagah rahe. Wo na mile to aakhir mein.
  const lang = top.querySelector(".lang-toggle");
  if (lang) top.insertBefore(btn, lang);
  else top.appendChild(btn);
}

// ⚠ EXPIRY KA CHECK LOAD PAR BHI HOTA HAI, sirf upar wale interval par NAHI.
// Bila iske silsila ye banta: teacher subah lock chhore baghair chala jata,
// sham ko koi page kholta, aur key 60 second tak (interval ke pehle tick tak)
// zinda rehti. Wo poora waqt app khuli hoti. Load par dekhne se gate usi lamhe
// aata hai jis lamhe page khulta hai.
// ── Users mode ka top-bar: naam, Logout, aur admin ke liye Users ───────────
//
// Button yahan se lagte hain, HTML se nahi -- wahi tareeqa jo upar Lock button
// ke liye likha hai, aur wahi wajah: ye file nau pages par chalti hai, to HTML
// mein daalne ka matlab nau files chhoona aur `css_baseline.py` ki frozen
// inventory hilana hota.
function pmMountUserBar(me) {
  const top = document.querySelector(".pz-top");
  if (!top || top.querySelector(".pz-user")) return;

  const who = document.createElement("span");
  who.className = "pz-user";
  // textContent -- naam wo qeemat hai jo kisi insaan ne type ki thi.
  who.textContent = me.user.display_name || me.user.username;

  const out = document.createElement("button");
  out.type = "button";
  out.className = "pz-lock";
  out.textContent = "Logout";
  out.title = "PC chhorne se pehle dabayein";
  out.addEventListener("click", async () => {
    // ⚠ SERVER PAR LOGOUT, SIRF BROWSER MEIN NAHI. Purane key wale lock ka
    // asal aib yehi tha: wo localStorage saaf karta tha aur server ke nazdeek
    // kuch nahi badalta tha. Yahan session DB se mit jati hai, to us cookie
    // se dobara andar aana mumkin hi nahi rehta.
    await apiFetch("/api/auth/logout", { method: "POST" });
    pmGoLogin();
  });

  const nodes = [who];
  if (me.user.role === "admin") {
    const link = document.createElement("a");
    link.className = "pz-user-link";
    link.href = "/users.html";
    link.textContent = "Users";
    nodes.push(link);
  }
  nodes.push(out);

  const lang = top.querySelector(".lang-toggle");
  nodes.forEach((n) => (lang ? top.insertBefore(n, lang) : top.appendChild(n)));
}

function pmInit() {
  if (pmRead(PM_KEY_STORAGE) && pmIdleExpired()) {
    pmLock(PM_IDLE_MSG);
    return; // key ja chuki — lock button lagane ko kuch nahi bacha
  }
  pmMountLockButton();

  // Users mode hai ya nahi -- ye ek hi sawal hai aur jawab sasta hai (`me`
  // auth ke peeche nahi). Key/khule mode par `user` khali aata hai aur yahan
  // kuch nahi hota, yani purane setups par ye code chalta hi nahi.
  _rawFetch("/api/auth/me")
    .then((r) => (r.ok ? r.json() : null))
    .then((me) => {
      if (me && me.user) pmMountUserBar(me);
    })
    .catch(() => {
      /* server band hai -- baqi page ka masla, yahan khamoshi */
    });
}

if (document.readyState === "loading") {
  addEventListener("DOMContentLoaded", pmInit);
} else {
  pmInit();
}
