# Paper Maker — HANDOVER (19 July 2026)
### Naye chat mein isse shuru karo — pehle context, phir SUBAH: SLO tagging (DATA), phir Hissa B

---

## PROJECT BUNIYAD (hamesha yaad)

- **Folder:** `C:\PaperMaker\paper-maker-mvp` (sirf yahi — **E: drive / backup / koi aur project MAT dekho**, wahan purani copies hain)
- **Stack:** FastAPI + SQLite + static HTML/JS
- **Server:** uvicorn par `localhost:8000` — **node/:3000 NAHI** (Claude Code ne ek dafa galat jagah dekha tha)
- **Workflow:** feature branch → plan → implement → **browser test** → merge → pytest/ruff → PROGRESS.md → GitHub Desktop push → backup.bat
- **Har hissa ALAG branch** (2A do stacked branches thin, `--no-ff` merge)
- **Test count: 738 passing** (666 → 738 aaj — SLO Marhala 1/2A + 2 bug fixes)
- **Roman Urdu / Hinglish** mein baat, **screenshots** har step par
- Har naye route/DB change ke baad **server restart** zaroori
- Push = GitHub Desktop (Ctrl+P) — sirf **backup remote**, cloud deploy NAHI. App offline hai.
- **PROGRESS.md har fix ke baad turant** update karo (batch mat karo).

---

## ⚠️ AHEM SABAQ (aaj seekhe — dobara na dohrana)

### 1. Main manual add form use NAHI karta — sab Excel bulk + Blueprint se
Question banane/tag karne ka mera tareeqa: **bulk Excel upload** + **Blueprint**. Manual
add/edit form (bank.html) main haath se nahi bharta. **Is liye har naye feature ka
"data path" pehle Excel/Blueprint ke zariye socho**, manual picker sirf fallback hai.
(Isi wajah se KAAM A — SLO tagging — bhi Excel se banaya, manual picker se nahi.)

### 2. GitHub Desktop: Summary box khaali ho to commit CHUP-CHAAP fail
Text galti se **Description** (bara box) mein chala jaye aur **Summary** (chhota box, upar,
"required") khaali reh jaye to commit **hota hi nahi** — aur koi error bhi nahi aata.
**Qaida:** commit ke baad hamesha "0 changed files" / "No local changes" dekh lo.

### 3. Browser cache — hard refresh se bhi kabhi nahi jaati
static HTML/JS badalne ke baad hard refresh (Ctrl+F5) par bhi purani file chalti reh
sakti hai. Feature test hamesha **incognito** window mein karo (saaf cache).

### 4. Feature banane se pehle dekho ke DATA maujood hai ya nahi
Coverage/shortfall jaise features test karte waqt pehle tasdeeq karo ke asli data hai:
kai Pre Year 1 papers **orphaned** nikle (sawal delete ho chuke) aur `class_name = None` tha,
to coverage khali dikha raha tha — **code bug nahi, data-hygiene masla**. Feature se
pehle "kya is par test karne layak data maujood hai?" pooch lo, warna asli bug samajh baithte hain.

---

## AAJ (18 July) KYA HUA — sab MUKAMMAL (test 666 → 738)

### SLO Marhala 1 — Question ↔ SLO link ✅
Branch `feature/slo-phase-1` → master merge (`--no-ff`, commit `26fb90c` → `fca1fbf`).
- **DB:** naya **`question_slo` link table** (column NAHI) — `question_id`, `slo_id`, `created_at`,
  composite PK `(question_id, slo_id)`. Wajah: (1) ek sawal = kai SLO, (2) `questions` table
  bilkul untouched → 200+ purane sawal bina migration ke chalte rahein, (3) gemini (protected)
  question bhi tag ho bina row chhue. Link `slo_id` (PK) se — re-import par stable. Index
  `idx_question_slo_slo` (reverse lookup, Marhala 2). Migration = sirf CREATE TABLE/INDEX (idempotent).
- **Repo/Service/API:** `question_slo_repository.py` (naya, replace-set semantics, orphan INNER JOIN se drop),
  `question_service.set/get_slos_for_question`, `GET/PUT /api/questions/{id}/slo` (khali list = clear,
  **har source** par kaam), `slo_ids` optional on manual create/update.
- **UI:** `bank.html` Add + Edit modal mein **SLO picker** (checkbox + search), subject/class/topic
  teeno maloom hon tabhi bharta (gate), warna "pehle topic chuno" hint.
- **Tests:** `test_question_slo_repository.py` (7) + `test_question_slo_api.py` (11) = 18 naye. **700 pass** (682 → 700).

### SLO Marhala 2 Hissa A — paper coverage + Excel tagging ✅
Do stacked branches, `--no-ff` merge: `feature/slo-phase-2a-coverage` (`9d8a9d1`)
→ `feature/slo-phase-2a-excel-tagging` (`f7876c3`).
- **Coverage** (`slo_coverage_service.py`, `GET /api/paper/{id}/slo-coverage`): paper ke sawalon se
  covered vs reh-gaye SLO + strand breakdown + untagged ginti. **Live compute (JOIN), stored snapshot
  NAHI** — link/SLO baad me badle to report khud sahi. class match **normalized** (`LOWER(TRIM)`)
  kyunki `papers.class_name` free-text/gandi hai; universe na mile to **graceful covered-only + saaf
  message**, koi crash nahi. UI: `index.html` preview ke neeche SLO Coverage section (progress bar +
  strand table + reh-gaye list + untagged note).
- **Excel tagging** (KAAM A — main manual picker use nahi karta):
  - **Naye questions:** bulk upload Excel me optional `slo_code` column (comma-separated = kai SLO).
    Ghalat code → skip + warning, question phir bhi import.
  - **Purane 200+ questions:** `GET /api/questions/slo-export` (Excel: `question_id` + current `slo_code`)
    → teacher bhare → `POST /api/slo/assign-import`. **question_id se match** (text se nahi),
    **replace-set** (idempotent, khali = clear). `question_slo_import_service.py` naya; `slo.html` par bulk-assign card.
  - **Duplicate trap (tested):** question bulk import upsert NAHI karta — same sheet dobara = QUESTION
    duplicate. Isi liye purane sawalon ke liye slo-export/assign-import (id se), question sheet re-upload NAHI.
- **Tests:** coverage (13) + `test_bulk_import_slo.py` (6) + `test_question_slo_import.py` (11) = 30 naye. **730 pass** (700 → 730).

### 2 zinda bug fixes ✅
Branch `fix/paper-class-and-delete-warning` (merge `4fb1409`).
- **Fix 1 — Generator class_name capture:** `index.html buildPaper` ab `class_name: val('gradeSelect') || null`
  bhejta hai. Backend pehle se ready tha — masla sirf frontend line ka (isi liye har Generator paper class
  None banta, coverage universe kabhi nahi banta). Zero backend change. Regression-guard `test_generator_class_name.py`.
- **Fix 2 — question delete se pehle paper warning:** `papers.question_ids` JSON blob hai (koi FK/cascade nahi),
  sawal delete papers ko chup-chaap orphan kar deta tha. Ab delete se pehle kaun se papers tootenge dikhta:
  `find_papers_containing` (quoted-id LIKE, substring-safe), `GET /api/bank/questions/{id}/paper-usage`,
  `bank.html deleteQuestion` warning. **Sirf warning** — koi block/cascade nahi (jaan-boojh kar simple).
- **Tests:** `test_generator_class_name.py` (2) + `test_paper_delete_warning.py` (6) = 8 naye. **738 pass** (730 → 738).

---

## 🌅 KAL SUBAH SABSE PEHLE — DATA (code nahi): SLO tagging

**Yeh Hissa B se PEHLE hona hai.** 200+ Pre Year 1 Math questions abhi **untagged** hain —
jab tak inpar SLO nahi lagenge, coverage/shortfall (Hissa B) khaali dikhayega. Yeh coding
nahi, sirf Excel bharne ka kaam hai. Manual picker MAT chalao — sab Excel se.

### Qadam-ba-qadam (jo bhi naya session yeh karayega)

**STEP 0 — server + data confirm**
- Server chal raha hai? (uvicorn `:8000`, `node/:3000` NAHI)
- `GET /api/slo` → 50 Pre Year 1 Math SLO maujood hain?

**STEP 1 — export (current tags Excel me nikaalo)**
- Browser: `slo.html` khol → **bulk-assign card** → "Export questions for tagging" (ya seedha
  `GET /api/questions/slo-export`).
- Excel milega do column ke saath: **`question_id`** (mat chhuo) + **`slo_code`** (current tags, ab khaali).
- Filter/limit: agar sirf Pre Year 1 Math chahiye to us subject/class ke questions export honge.

**STEP 2 — Excel bharo**
- Har row ke `slo_code` cell me sahi SLO code likho. **Kai SLO = comma-separated** (misal: `N-3, C-1`).
- Codes wahi jo `GET /api/slo` deta hai (Pre Year 1 Math: `W-*`, `N-*`, `C-*`, `D-*`, `S-*`).
- **`question_id` column bilkul mat badlo** — matching isi se hoti hai (text se nahi).
- Khaali chhoRa = us question ke saare SLO **clear** ho jayenge (replace-set semantics).

**STEP 3 — wapas upload**
- `slo.html` bulk-assign card → bhari hui Excel upload → `POST /api/slo/assign-import`.
- **replace-set / idempotent:** dobara upload safe hai (multiply nahi hote), har question ke tags us row
  ke hisaab se **replace** honge. Ghalat/unknown `question_id` par saaf error milega — question sheet
  re-upload NAHI karni (woh QUESTION duplicate banati hai).

**STEP 4 — tasdeeq**
- Kisi Pre Year 1 Math paper ka `GET /api/paper/{id}/slo-coverage` — ab covered SLO barhne chahiye,
  untagged ginti girni chahiye. (Yaad: orphaned/None-class papers par phir bhi 0 — woh data masla hai, tag nahi.)

**Iske baad hi Hissa B (shortfall) ka asli test ho payega — warna sab 0 dikhega.**

---

## HISSA B — Shortfall (70/30 Bloom distribution) ka poora PLAN

**Maqsad:** paper banate waqt teacher ko Bloom distribution ki **kami (shortfall)** dikhana —
lekin **app chup-chaap adjust NA kare**, teacher ko 3 saaf option de.

### Asal usool (Marhala 0 ka faisla)
- **SLO list = poora course** (har SLO ka Bloom sach). **Standard = paper banate waqt** lagta hai.
- **SLO ki ginti ≠ sawaalon ki ginti.** Ek SLO se kai sawaal. Qillat SLO ki nahi, **question bank** ki.
- Pre-Primary standard = **Remember 70% / Understand 30%** (Play Group, Nursery, KG, Pre Year 1/2/3).

### App ka behaviour (yeh core faisla — implement isi par)
| Surat | App kya kare |
|---|---|
| Sawaal kaafi hain | Chup-chaap 70/30 par paper bana de |
| Sawaal kam hain | **Shortfall dikhaye** — misal "7 remember chahiye the, 4 mil rahe". Teacher ko **3 option**: (a) jo mil raha usi se banao, (b) kami doosre Bloom se poori karo, (c) naye sawaal likhne hain |
| Us Bloom ka koi sawaal nahi | Saaf bata de — "Understand ka ek bhi sawaal nahi" |

**Faisla hamesha teacher ka.** App marzi-based rahe (Bloom feature ki tarah) — koi khudkaar substitution NAHI.

### Tareeqa / faisle (naye session yeh tay kare, phir plan de — implement mere confirm par)
1. **Nayi branch** master se: `feature/slo-phase-2b-shortfall`.
2. **Bloom standard kahan rakhein?** — `bloom_standards.py` mein already Pre-Primary/Primary/Middle/Matric
   distribution table hai. Shortfall service isi se target % le. (Naya config file banana hai ya isi ko extend — tay karo.)
3. **Shortfall compute kahan?** — nayi service (misal `slo_shortfall_service.py`) ya coverage service ko extend?
   Input: class+subject (Bloom group tay karta), maujood tagged questions ka Bloom breakdown, requested paper size.
   Output: per-Bloom `{needed, available, short}` + overall message.
   **Live compute (coverage jaisa), stored snapshot NAHI.**
4. **Bloom source:** question ka Bloom kahan se? — SLO ke `bloom_level` se (question→SLO link→SLO.bloom_level),
   ya question ka apna Bloom field? Ek question kai SLO se juda ho (mixed Bloom) to kaise ginein — **yeh tay karna hai**
   (tajweez: SLO.bloom_level primary; multi-SLO par kaise resolve ho, plan me likho).
5. **API:** naya endpoint, misal `GET /api/paper/shortfall?class=&subject=&size=` (paper generate se PEHLE,
   preview ke liye) — ya generate response ke saath shortfall block. Dono ke faide plan me.
6. **UI (index.html Generator):** generate se pehle/baad shortfall panel — per-Bloom bar + kami highlight +
   **3 option** button/radio (adjust NA kare, teacher chune). Excel/Blueprint flow bhi cover ho (main manual nahi karta).
7. **Class → Bloom group mapping:** `class_name` free-text/gandi hai (Marhala 2A ka sabaq) — **normalized match**
   (`LOWER(TRIM)`) + group na mile to graceful ("is class ka Bloom standard set nahi") + saaf message, crash nahi.
8. **Tests:** service (per-Bloom math, edge: 0 available, class None, universe khali) + API + regression.
   Full suite green rahe (738 se barhega).

**NOTE:** yeh sirf plan-tayari hai. Naya session pehle **SIRF PLAN** de (files, faisle, tests ginti),
mere confirm ke baad implement — 2A/Marhala 1 jaisa tareeqa.

---

## BAQI PENDING (Hissa B ke baad)

- **Hissa C — SLO Health page:** har class-subject ke liye chhota naqsha — har Bloom level ke kitne SLO,
  kitne sawaal, kaun se SLO par ek bhi sawaal nahi. Kami paper banane se PEHLE dikh jaye (`strand` column isi liye alag rakha).
- **KAAM B — manual add form collapse:** `bank.html` ka manual add form ko collapsible `<details>` mein daalna
  (main manual use nahi karta, isliye default band). SLO Excel-tagging ke baad. `[[project-papermaker-kaam-b-collapse-manual-add]]`
- **#3 — class dropdown:** Blueprint/bank-paper ka **free-text class box** → dropdown + custom fallback
  (isi free-text se `Jasmine`/`NUrsery`/`play` jaise gande class aaye jo coverage torte hain). Chhota alag kaam.
- **Baqi classes ke SLO:** wahi tarteeb `SUBJECT-CLASS-STRAND-SERIAL`, 7 columns, "Students will be able to…" style.
  Pehle book/curriculum se strand, phir SLO. (Pre Year 2 Math book upload ho chuki — 81 pages.)

---

## ⚠️ ZAROORI YAAD-DASHTEN

- **`backups/library_png_20260718/` + DB backup — abhi MAT hatao.** ~25 July tak rakhna hai,
  jab tak converted images se asal paper bana kar print na kar loon.
- **40 orphaned + 47 None-class papers ko HAATH MAT LAGAO** — orphaned = deleted sawal wapas nahi aate (murda);
  None-class = coverage graceful handle karta, andaaze se backfill galat hota. Yeh data-hygiene, code bug NAHI.
- **SLO import UPDATE mode ki tanbeeh:** abhi duplicate `slo_code` par **UPDATE** hai (draft phase me theek —
  wording badal kar dobara import ho). **Lekin jab SLO settle ho jayein aur teacher app me edit karne lagein,
  tab SKIP par le aana** — warna purani Excel dobara import teacher ki mehnat mita degi.
- **Push = GitHub Desktop backup remote hi** — cloud deploy NAHI (master push Railway/Northflank trigger karta,
  healthcheck fail — kabhi cloud push mat karo). App offline hai.
- DB me **50 asli SLO + tagged questions** = production data. `backup.bat` ahem.

---

## KAL KA PEHLA PROMPT (naye session me)

```
Naya session — Paper Maker. HANDOVER_19July parh liya hai.

STEP 0 — Context confirm (implement kuch nahi):
cd C:\PaperMaker\paper-maker-mvp  (sirf yahi folder — E: drive MAT dekho)
1. git status — clean? kis branch par?
2. git log --oneline -6 — 4fb1409 (bug fixes), f7876c3 (2A excel), fca1fbf (Marhala 1) master me hain?
3. git branch --merged master — koi branch reh gayi?
4. Server chal raha? (uvicorn :8000, node/:3000 NAHI)
5. GET /api/slo — 50 SLO maujood?
6. backups/library_png_20260718/ maujood? (abhi hatana NAHI)

RUKO. Mere confirm par KAAM 1.

KAAM 1 — SUBAH ka DATA kaam (code nahi): Pre Year 1 Math questions ko SLO tag karna.
Handover ke "KAL SUBAH SABSE PEHLE" section ke STEP 1–4 karao (export → Excel bharo → upload → verify).
Manual picker MAT — sab Excel se.

KAAM 2 (data ke baad) — Hissa B ka SIRF PLAN (implement NAHI):
Handover ke "HISSA B" section ke 8 nuqte address karo. App chup-chaap adjust NA kare —
teacher ko 3 option. Files/faisle/tests ginti do. Implement mere confirm par.
```
