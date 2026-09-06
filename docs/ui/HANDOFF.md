# Handoff — 2026-09-06

> **Ye file 2026-09-06 ko poori tarah nayi likhi gayi.** Is se pehle yahan 20 Agast ka
> handoff tha jis par 31 Agast ko "YE FILE BASI HAI" ka banner laga diya gaya aur wo
> banner bhi khud chhe din purana ho chuka tha. **Is dafa naya likha gaya, patch nahi
> kiya** — aur agli dafa bhi yehi karna.

---

## Naya chat yahan se shuru karo

**Teen files, isi tarteeb mein:**

1. **`docs/ROADMAP.md` §0** — poore project ka audit. Kitna hua, kitna baqi, har kaam
   ka apna paimana. **2026-09-06 ko naya naapa gaya.**
2. **`docs/ui/STATUS.md`** — CSS epic ka zinda board, sab se ooper aaj ka khulasa.
3. **`docs/ui/DEFERRED.md`** — 44 rows, 14 band, **30 khuli**. Har khuli row batati hai
   ke wo kaam maang rahi hai ya faisla.

**Aur ye teen usool, jo is project ne mehngey mol seekhe:**

- **Row par bharosa mat karo, repo mein naapo.** 2026-09-06 ke audit mein `R5` aur `R9`
  "khula" likhe thay aur dono kab ke ho chuke thay. Usi din `DEFERRED.md` ki teen rows
  (D9, D19, D20) sirf is liye khuli thin ke kaam ho chuka tha aur row kaati nahi gayi.
- **Gate wo cheez nahi pakadta jo wo dekh hi nahi sakta.** `css_type_probe` fresh load
  par walk karta hai: JS-rendered markup, `:hover`, aur JS class-hooks us ke bahar hain.
  09-05 ko `index.html` par ek `class` attribute do dafa likha gaya (`.qtype` mar jata,
  paper generate karte waqt question types khali chale jate) aur **gate ne 0 deltas
  diye** — wo aankh se pakra gaya.
- **Ek jaisa symptom, ek jaisa fix nahi.** D26 aur D66 dono `opacity` ki wajah se AA se
  neeche thay; D26 mein opacity delete karna durust tha, D66 mein wohi karna adad pass
  kar deta aur design tor deta. Hamesha us surface par naapo jahan cheez asal mein hai.

---

## Aaj kahan khare hain — naapa 2026-09-06

```
git            HEAD 30ee89a · working tree saaf · backup/master ke BARABAR (0 aage)
tests          1,083 pass · ruff saaf
DB             integrity ok · 1,214 sawal · 310 topics
CSS            legacy_css_lines 1601 (target 1450) · unsanctioned_hex 298
gate           das pages x paanch viewports · drift 0
DEFERRED       44 rows · 14 band · 30 khuli
```

**PRD:** 22 mein se 19 ho chuke, 2 mansookh/band, **1 aadha (R8)**.

---

## Jo abhi chal sakta hai — tarteeb ke saath

### 1. PY1 ke baqi 6 topics — waahid seeding kaam jo aaj mumkin hai
Backup **sqlite backup API se** (WAL-safe), `python -u`, tail parho. Quota rozana
~20–25 topics deti rahi hai, to ye **ek run** ka kaam hai.
⚠ **Seeding ke foran baad:** `seed_bank.py` ko PY1 ka 1-mark paimana maloom nahi —
`select count(*) from questions q join syllabus_topics t on t.id=q.syllabus_topic_id
where t.grade='Pre Year 1' and q.marks <> 1` → **0 aana chahiye** (aaj 0 hai).

### 2. Do hygiene rows — tez, magar destructive, "go" chahiye
- **D2** — 22 stale `feature/*`, `hissa-*`, `fix/*` branches (kul 35 local)
- **D10** — repo root mein **26** `.db`/`.zip` files
Dono CSS epic se alag `chore` session hain.
⚠ **Backup DB files delete karne se pehle Irfan se poochho** — kuch retention par hain.

### 3. R8 ka bacha hua aadha — per-student paper generation
Per-student **results** ka poora raasta mojood aur tested hai
(`adaptive_results_service.py`); paper ab bhi poori class ke bloom-weakness se banta
hai (`/api/generate-adaptive-paper`). Jo baqi hai wo sirf per-student paper generation
hai. **Ye product ka waahid khula kaam hai.**

### 4. 44 jaali syllabus topics — data ka kaam, code ka nahi
`Math G5`, `Math G6`, `Science G7`, `Geography G8` — chaaron mein **bilkul wohi 11
Grade-4 maths topics** hain (naapa gaya). **Seeding mana hai** jab tak asal syllabus
import na ho; Geography par yehi ho chuka tha aur 44 sawal delete karne pare. Import ka
raasta (R9, PDF + OCR fallback) mojood aur tested hai — **asal PDF/Excel chahiye.**

### 5. CSS epic ka baqi hissa — zyadatar faisla, kaam nahi
30 khuli rows. Bara hissa `disagree` ke ~50 rules par khara hai aur har ek ek faisla
maangta hai. `agree` ka bila-faisla hissa **khatam** ho chuka.

---

## AAGE KA PLAN — session ke hisaab se (Irfan, 2026-09-06)

**Tarteeb ka usool: pehle wo jo TEACHER tak pahunchta hai, phir product, phir andar ki
safai.** Aaj product PRD ke hisaab se ~95% mukammal hai — is ka matlab ye hai ke **ab
sab se bara faida naya code likhne se nahi, is ko school ke computer par chalane se
aata hai.**

### Session 1 — PY1 ke baqi 6 topics *(chhota, magar quota ka mohtaj)*
Bank ka waahid hissa jo aaj seed ho sakta hai. Quota rozana ~20–25 topics deti rahi
hai, to **ek run kaafi hai.** Backup sqlite backup API se (WAL-safe), `python -u`,
tail parho. **Seeding ke foran baad `marks <> 1` wala check chalao** (HANDOFF ke
"jo abhi chal sakta hai" §1 mein poori query hai). Is ke baad bank ke asal topics
**266/266** ho jayenge.

### Session 2 — SCHOOL PC PAR CHALAO *(sab se zyada qeemat, aur ye code ka kaam nahi)*
`Dockerfile` mojood hai aur `docs/SETUP-LOCAL.md` poora deployment guide hai — 20
teachers, ek school PC, LAN par, offline. **Magar likha hua guide aur chalta hua system
do alag cheezein hain.** Is session ka maqsad: guide ke qadam asal machine par chala kar
dekhna kahan tootta hai — Python, `.env`, DB ka path, Nastaliq font, LAN address,
firewall, aur teacher ka Ctrl+P.
⚠ `SETUP-LOCAL.md`:80 ki chetawni: agar DB path ghalat ho to app **khali database bana
leti hai** aur school ko khali dikhti hai. **Ye session Irfan ke saath, us machine par
hona chahiye** — is mein AI ka hissa kam, mojoodgi ka zyada hai.

### Session 3 — Repo hygiene: D2 + D10 *(tez, destructive, "go" chahiye)*
22 stale branches, aur repo root mein **26** `.db`/`.zip` files. Ek `chore` session,
CSS epic se bilkul alag. ⚠ **Backup DB delete karne se pehle Irfan se poochho** — kuch
retention par hain.

### Session 4 — R8 ka bacha hua aadha: per-student paper
Product ka **waahid** khula kaam. Per-student results ka poora raasta mojood aur tested
hai; paper ab bhi poori class ke bloom-weakness se banta hai. **Pehla sawal code ka
nahi hai:** ek teacher 25 alag parche kaise chhapega aur kya wo asal mein chahta hai?
Jawab pata chalne se pehle likhna ulta hoga.

### Musalsal — CSS ke 30 khule rows *(batch mein, faisle ke saath)*
Bara hissa `disagree` ke ~50 rules par khara hai aur **har ek Irfan ka faisla maangta
hai, waqt nahi.** Behtar tareeqa: ek session mein **ek family** uthao (rang, ya spacing,
ya buttons), sab naap kar do-teen sawal ek saath poochho, phir laago karo. Isi tareeqe
se 09-05/06 ko chaudah rows band huin.

### RUKA HUA — 44 jaali syllabus topics *(Irfan ke baghair nahi chal sakta)*
`Math G5`, `Math G6`, `Science G7`, `Geography G8` — chaaron mein wohi 11 Grade-4 maths
topics hain. **Import ka raasta mojood aur tested hai (R9, PDF + OCR fallback); jo nahi
hai wo asal syllabus ki PDF/Excel hai.** Jab tak wo na aaye, ye rows sirf intezar hain —
aur in ko seed karna **mana** hai (Geography par ye ho chuka aur 44 sawal delete karne
pare).

---

## Auzaar — kaun sa sawal kis se poochha jata hai

`docs/ui/PROBES.md` mein poori list aur usage hai. Sab ko app chalti chahiye
(`.venv/Scripts/python.exe -m uvicorn app.main:app`).

| sawal | auzaar |
|---|---|
| "kuch hila to nahi?" — **har CSS commit ka gate** | `css_type_probe.mjs` + `css_type_diff.mjs`, das pages × paanch viewports |
| "ye rule delete karun to kya hilta hai?" | `css_drain_probe.mjs <page>` |
| "ye selector har page par kya compute karta hai?" | `css_selector_probe.mjs "<sel>" "<props>" <pages>` |
| "kaun sa text WCAG AA se neeche hai?" | `css_contrast_probe.mjs` *(naya, UI-092)* |
| "JS se bane elements?" | `css_inject_probe.mjs` — fixtures rot hoti hain, header parho |

---

## Aakhri do din kya hua (UI-083 → UI-094)

Chaudah `DEFERRED` rows band huin, sab naap ke saath aur har ek ka apna gate:

- **D51** (chaar pages, `.ctl-stack`, 155 tag-sites) · **D63** (`.row` component) ·
  **D64** (`.app-nav` component, 40 **maqsood** deltas) · **D43**, **D65** (`label` +
  `height:100%`) · **D9/D15/D19/D20/D24** (paanch chhoti) ·
  **D26/D31/D41/D66** (chaaron contrast rows).
- **Naya auzaar:** `scripts/css_contrast_probe.mjs`.
- Poori tafseel `PROGRESS.md` mein 2026-09-05 aur 2026-09-06 ke andraaj mein.

⚠ **Ek adad jo ulta gaya aur wo jaan-boojh kar hai:** `legacy_css_lines` 1593 se **1601**
par charha, gira nahi. Base rules aur murda declarations nikleen, magar un ki jagah
"ye upar chala gaya / ye murda hai, upar mat le jao" wale warning-comments likhe gaye
aur wo lines gin'ti mein aati hain. **Asal kami tab hogi jab ye pointer-comments khud
jayenge.**
