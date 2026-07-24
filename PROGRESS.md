# PaperMaker — Fix / Feature Log

## 2026-07-24 — Ops: sequence import "Updated:50" magar seq NULL — stale server

Alaamat: teacher ne sequence-wali Excel import ki, "Updated: 50, Errors: 0" mila,
magar `/api/slo` aur DB dono mein saari 50 `sequence` NULL. DB file ka mtime import
ke baad bhi purana (Jul 23 21:21) — yani us DB par aaj koi write hi nahi hua.

Diagnosis:
- Do uvicorn processes chal rahe the (PID 21160, 38148), dono ka `cwd` repo, `DB_PATH`
  unset → **dono ek hi** `paper_maker.db` par. Sirf 38148 :8000 par bind tha.
- Dono **Jul 23 18:34** ke — yani `sequence` ka code (jo isi 23 ko baad mein aaya) is
  running process mein load hi nahi tha. uvicorn `--reload` ke baghair chala tha, is liye
  purana `slo_import_service` module memory mein reh gaya (slo_text/bloom/strand update
  karta tha, sequence nahi → "Updated:50" sach tha magar seq NULL).
- Disk code sahi sabit hua: DB ki temp copy par poora import path chalaya → `updated:1,
  errors:0`, DB ne `sequence=99` wapas diya.

Hal: dono purane process band → fresh `uvicorn --reload` (PID naya). Teacher ne dobara
import kiya → (1) `POST /api/slo/import 200` access-log mein, (2) DB mtime badla
(Jul 24 06:38), (3) seq non-null **50/50**. Phir taqseem N=8 sahi chala (4 mixed,
4 single-strand; ab strand-boundary par mix, alphabetical artifact nahi).

Sabaq: `sequence`/naye feature ke baad server hamesha restart (ya `--reload` ke saath
chalao); warna "Updated" report sach hote hue bhi naye columns skip ho sakte hain.

## 2026-07-23 — SLO: `sequence` column (asal kitab ki tarteeb)

Maqsad: taqseem (exam distribution) `slo_code` se sort karta tha, magar slo_code
**strand-grouped** hai (C→D→N→S→W), teaching tarteeb nahi. Nateeja: Number strand
akela 25/50 SLO hone se **4 exam sirf Number** ke ban rahe the. Asli tarteeb sirf
teacher jaanta hai — is liye teacher ke bharne ke liye alag `sequence` column.

Changes:
- `app/core/database.py` — `init_db()` mein idempotent migration: `slo` table mein
  `ALTER TABLE ADD COLUMN sequence INTEGER` (nullable). Purani 50 rows NULL rehti hain.
- `app/repositories/slo_repository.py` — `insert()` mein `sequence` column+value.
  `update_by_code()` generic tha (koi change nahi) — re-import par sequence refresh.
- `app/services/slo_import_service.py` — `sequence` optional column parho: khali→NULL,
  poora number→int (Excel "3.0" bhi qubool), **number na ho ("abc"/"2.5")→row error**
  (chupke null nahi). Add + update dono paths mein sequence.
- `static/slo_import_template.xlsx` — purana (ignored) `book_pages` column hataya,
  `sequence` add. Sample rows teaching-order (W,N,C,S = seq 1,2,3,4) dikhate hain.
- `static/slo.html` — list mein pehla **"Seq"** column (NULL → "—" muted, taake teacher
  dekh sake kaunse khali). Import hint text update (book_pages hata, sequence likha).
- `scripts?/taqseem.py` (scratchpad standalone) — sort ab `sequence` se, NULL par
  slo_code fallback (aakhir mein); report top par kitne NULL saaf batata hai. N configurable.

Verify: migration real DB par chala (sequence column + 50 NULL confirmed). Import
end-to-end test (valid/float/empty/invalid/re-import) sahi. Naye 5 sequence tests +
poora SLO suite: **104 passed**. Koi DB data change nahi (sirf nullable column add).

Agla step (manual): teacher/user Excel mein sequence bhar kar re-import karega →
50 rows update; phir taqseem asal teaching order se banega.

## 2026-07-23 — UI: pdfSubject free-text → datalist (KAAM 3)

Scan ke baad KAAM 3 mein asal mein sirf **ek** field bacha tha (alag phase nahi, chhota
add-on): `pdfSubject` (index.html Syllabus Upload). `exSubject`/`fSubject` KAAM 2 mein ho
gaye; generator ka `subject` (index.html:429) cascade se auto-bharta hai — chhoda.

Fix (`static/index.html`):
- `pdfSubject` → `<datalist>` (pdfGrade jaisa hi). CREATION field hai (naya subject ka
  syllabus yahin add hota hai), is liye strict dropdown nahi — maujooda subjects suggest,
  naya likhna bhi allowed.
- `loadSyllabusGrades()` mein `fillDatalist()` helper — ab pdfGrade + pdfSubject dono
  `_allGrades` se bharte hain.

Verify: index.html tag-balanced (headless parse); wiring (list=+datalist+fillDatalist)
match. Backend change nahi (frontend-only). Browser click verify baqi — extension off.

## 2026-07-23 — UI: class fields free-text → dropdown (KAAM 2)

Maqsad: free-text class/subject se data bikhar jata tha — 'Pre year 1' vs stored
'PRE YEAR 1'. Aaj isi wajah se SLO list KHALI dikhi thi. Root cause: SLO list filter
(`slo_repository.list_by_filters`) **EXACT** match karta hai (`class = ?`), zara sa
farq = 0 rows.

Ahem: SLO ka class/subject syllabus ke `grade` se **alag vocabulary** hai (SLO Excel ke
apne `class,subject` columns). Is liye dropdown syllabus-grades se NAHI — SLO table ke
asal distinct values se banaya.

Backend:
- `slo_repository.list_distinct_facets()` — DISTINCT class + subject (non-empty, sorted).
- `GET /api/slo/facets` → `{classes, subjects}` (sibling `list_slos` jaisa unwrapped read).

Frontend (`static/slo.html`):
- `fClass`, `fSubject`, `exSubject` free-text input → `<select>`. `exGrade` (pehle se
  select) ab syllabus-grades ke bajaye facets.classes se bharta hai — export bhi SLO data
  se match kare.
- `loadExportGrades()` (syllabus-grades) → `loadFacets()` + `fillFacetSelect()` (facets).
  Chaaron dropdown ek hi `/api/slo/facets` call se.

Frontend (`static/index.html` — Syllabus upload):
- `pdfGrade` ye CREATION field hai (naya class ka syllabus yahin add hota hai) — strict
  dropdown naye class ko block kar deta. Is liye `<datalist>` (input + maujooda grades
  suggest, naya likhna bhi allowed). `_allGrades` se populate (already loaded).
- `pdfSubject` + baaqi subject fields = KAAM 3 (alag phase).
- Cosmetic label fields (`bpClass` bank.html, `bpClassName` blueprint.html) — chhode,
  ye paper par chhapne wale roster naam hain, data se link nahi.

Verify: `/api/slo/facets` → `{"classes":["Pre Year 1"],"subjects":["Mathematics"]}`;
`/api/slo?class_name=Pre Year 1&subject=Mathematics` → rows aate hain (exact match ab
dropdown se guaranteed). Teenon pages HTML tag-balanced (headless parse). 828/828 tests pass.
Browser click verify NAHI ho saka — Chrome extension connected nahi tha.

## 2026-07-23 — UI: bank.html "Naya question add karo" form collapsible (KAAM 1)

Maqsad: teacher zyadatar Excel se questions add karta hai — manual add form roz nazar
aane ki zaroorat nahi, sirf jagah gherta tha. Ab `print.html` ke Print Settings jaisa
`<details>` pattern, default **BAND**.

Fix (`static/bank.html`):
- "Naya question add karo" card (`<div class="card">`) → `<details class="card add-q-collapse"
  id="addQCard">` + `<summary class="add-q-summary">` (arrow + title + hint). Andar ka
  poora content ek `<div class="add-q-body">` mein wrap. Koi ID/JS/handler nahi badla —
  form waisa hi kaam karta hai, sirf collapse hua.
- CSS: summary marker hidden, `[open]` par arrow rotate + border-bottom, body padding.

## 2026-07-23 — Data cleanup: dummy/trial data DB se hataya

Maqsad: trial data saaf, sirf asal seed rakhna. ("class" = syllabus_topics.grade via
syllabus_topic_id; questions table mein direct class column nahi.)

RAKHA: Pre Year 1 Mathematics 329 questions, saare 50 SLOs, 329 question_slo links
(sab Pre Year 1 ke), Image Library (99) — poori, syllabus_topics, blueprints (2),
usage_log (99).

DELETE (single transaction, guards ke sath): ALL papers (72), class null/empty
Mathematics questions (60) + Pre Year 2 (40) + Pre Year 3 (20) = 120 questions +
unke question_slo links (0 the). Orphan trial results bhi (user ne "sab delete"
chuna): result_uploads (14) + student_question_results (840).

Nateeja: questions 449→329, papers 72→0, results 0, SLO 50 (unchanged), question_slo
329 (unchanged), image_library 99 (unchanged). Verify: live API 329; 0 non-Pre-Year-1
baaqi; 0 dangling question_slo (dono taraf). Backup (user ke apne backup ke ilawa,
sqlite .backup se consistent): `paper_maker_backup_before_dummy_cleanup_20260723_172026.db`.

## 2026-07-23 — Fix: bank.html Edit button dead (onclick markup toota)

Symptom: Question Bank mein **Edit** dabane se kuch nahi hota (Delete theek — confirm
+ orphan warning). Script parse ho rahi thi (Delete chalta tha), masla generated
markup mein tha.

Wajah: `renderQRow` mein Edit button ka onclick
`openEditModal(${escAttr(JSON.stringify(q))})` tha. `JSON.stringify` **double quotes**
deta hai (`{"id":...}`) aur `escAttr` sirf single quote escape karta hai — double-quoted
`onclick="..."` attribute pehle hi `"` par **toot jata** tha → handler `openEditModal({`
ban jata (invalid JS) → click par kuch nahi. (Delete safe tha kyunki UUID mein quote
nahi.) `node --check` isse nahi pakadta — bug JS syntax mein nahi, HTML markup mein tha.

Fix (`static/bank.html`):
- Edit onclick ab Delete jaisa: `openEditModal('${escAttr(q.id)}')` (id string).
- `openEditModal(q)` ab string aane par `_allQuestions` se lookup karta hai (JSON.parse
  path hata — UUID JSON nahi).

Verify: node --check clean; VM mein real HTML id-set + missing-id→null getElementById ke
sath `openEditModal('<id>')` sab 5 types (mcq/tf/fill/short-answer + Urdu `"quotes"&<b>`
wala) par bina throw OK; koi missing element id nahi. Static file live — sirf hard-refresh.

## 2026-07-23 — Marhala 2B: Blueprint Bloom shortfall (soft guidance)

Maqsad: Blueprint se paper banate waqt paper ka ASAL Bloom mix class-standard se
compare → kisi Bloom level par **10% se ZYADA** farq ho to teacher ko soft guidance
+ 2 option (Ignore / Questions badlo). App khud kuch adjust NAHI karta.

**Ahem faisle:**
- Bloom source = **question ka apna `bloom_level`** (Question Bank wala), SLO ka NAHI
  (SLO-based per-paper wala purana `slo_shortfall_service` alag hai — chheda nahi).
- `bloom_level` khali/na-maloom questions **alag gine** (`no_bloom`); percentages
  sirf `with_bloom` par (warna numbers jhoot bolenge).
- Threshold strictly > 10 (epsilon se float-noise ignore) — **theek 10% par warning NAHI**.
- Class→tier: `bloom_standards.get_bloom_suggestion` (reliable source = syllabus
  `grade`, na ho to free-text `class_name`).
- Option 2 = **pointer-only** (user faisla): under-represented Bloom ke liye bank-count
  + `/bank.html?subject&bloom` filtered link; koi inline replace nahi.

**Backend:**
- `app/services/blueprint_bloom_guidance_service.py` (naya) — `compute_bloom_guidance(
  questions, class_tier, subject)`. subject=None → bank-count skip (pure/testable).
  Graceful: class na ho / tier na mile / `with_bloom==0` → `available False` + message.
- `app/services/blueprint_paper_service.py` — `assemble_blueprint_paper` mein
  `class_tier` param + return mein `bloom_guidance`.
- `app/schemas/requests.py` — `BlueprintPaperRequest.grade` (tier ke liye).
- `app/api/papers.py` — `class_tier = resolved_grade or class_name` resolve + pass.
- `tests/test_blueprint_bloom_guidance.py` (naya, 16 tests) — mix/empty-alag,
  case-insensitive, per-tier shortfall, boundary theek-10%, all-empty graceful,
  bank-pointer (seeded), 2× `/api/blueprint-paper` integration.

**Frontend:**
- `static/blueprint.html` — makePaper `grade` bhejta hai; `#bloomGuidance` panel
  (`renderBloomGuidance`) sirf `available && has_shortfall` par; no_bloom note,
  per-Bloom rows, "Ignore karo" (hide) + "Questions badlo" (bank pointers reveal).
- `static/bank.html` — `applyUrlListFilters()`: `?subject&bloom` se list pre-filter.

**Verify:** `pytest tests/test_blueprint_bloom_guidance.py` 16 green; blueprint+api
regression suites 157 green. **Browser test baaqi — server RESTART ke baad** (naya
`grade` field + guidance panel).

## 2026-07-23 — Marhala 4B: live print controls (sidebar stepper + POST save)

Maqsad: teacher print.html sidebar mein 3 knobs hilaye → preview foran badle
(setVar, koi fetch) → "Is class ke liye mehfooz karein" par DB likhe (auto-save
nahi) → Reset global default par (visual-only, DB untouched).

**Backend (POST):**
- `app/schemas/requests.py` — naya `ClassPrintSettingsSave` (class_name + font_size
  11–20 / q_gap 6–30 / page_margin 10–25, `Field(ge/le)` → out-of-range 422).
- `app/services/class_print_settings_service.py` — naya `save_print_settings()`:
  normalize_class, blank class → ValueError (route 400), warna repo.upsert (4A wala).
- `app/api/school_settings.py` — naya `POST /api/print-settings` (StatusResponse;
  ValueError→400, baaqi→500). GET/repo 4A se.
- `tests/test_class_print_settings.py` — POST: roundtrip, normalization, upsert
  overwrite, blank→400, out-of-bounds→422 (6 params, value persist bhi nahi hoti),
  boundary font accept. Total file ab 28 tests.

**Frontend (print.html):**
- `.options` font-size → `calc(var(--q-font) - 1px)` — **user faisla:** options bhi
  scale hon (font bara = bachcha jawab bhi padh sake). `.marks`/`.sec-title` waise.
  Default 14 par 13px = pehle jaisa.
- Sidebar mein `<details class="print-settings no-print">` — 3 stepper controls
  (+/− buttons, min/max par disabled), Save + Reset, status + hint line. Collapsible
  ([[project-papermaker-kaam-b-collapse-manual-add]] pattern). `.app-sidebar` par
  `overflow-y:auto` (khulne par clip na ho).
- JS: `PRINT_BOUNDS` (UI limits = schema mirror), `_printState`/`_printGlobalDefaults`/
  `_currentClassName`. `stepPrint` → clamp + setVar foran. `applyPrintSettings` (4A)
  extend: resolved values se controls init + Save UI configure (class na ho to Save
  disabled). `resetPrintSettings` → global default (visual). `savePrintSettings` →
  POST, inline feedback (koi alert nahi). `_printGlobalDefaults` loadPaper mein
  school-settings ke print_* se.

**Control type:** stepper +/− (non-tech teachers ke liye — sirf valid steps, bade
tap-target). **Feedback:** inline status line (✓ mehfooz / err), koi browser-dialog nahi.

**Verify:** POST tests + `pytest` (poora suite) 812 green; `ruff` clean; inline
JS `node --check` OK. **Browser test — server RESTART ke baad** (naya POST route).

**Browser test follow-up (2026-07-23):**
- Layout bug: sidebar flex-column mein `.print-settings` (details) shrink ho raha tha
  → summary+ps-body side-by-side, buttons wrap. Fix: `.print-settings { width:100%;
  box-sizing:border-box }` + `summary { display:block }`. (CSS-only.)
- POST 405: code theek — current app ke openapi mein `['get','post']` dono, TestClient
  POST=200. 405 = live server abhi **purana 4A code** (sirf GET) chala raha tha (GET+405
  combo = stale process ki nishaani). Hal: sahi process kill karke restart. Code bug nahi.

## 2026-07-23 — Marhala 4A · Commit 3: print.html CSS vars + JS apply (+ tests)

Maqsad: backend ke resolved print settings ko print.html par CSS vars se apply.

- `static/print.html` — (1) `:root` mein `--q-font: 14px`, `--q-gap: 14px`
  (`--page-margin` Commit 1 se). (2) `.question` gap → `var(--q-gap)`; `.qhead`
  + `.qtext-en` → `var(--q-font)`; `.qnum` → `calc(var(--q-font) + 1px)`;
  `.qtext-ur` → `calc(var(--q-font) + 2px)` (Urdu +2, qnum +1 nisbat barqarar).
  (3) naya `applyPrintSettings(className)` — `GET /api/print-settings?class_name=`
  fetch, `setVar` se font(px)/gap(px)/margin(mm) apply; fetch/JSON error par
  silent (defaults CSS mein pehle se). `loadPaper` mein `paper.class_name` ke
  saath await.
- `tests/test_class_print_settings.py` (naya, 16 tests) — migration columns
  DEFAULT 14, resolution (fresh default, global fallback, blank/None class,
  class-row override, normalization "Class 5"/"class 5"/" CLASS 5 ", other class
  → global, upsert replace), aur endpoint (global/override/no-param).

**Defaults par diff-zero:** `--q-font 14 / --q-gap 14 / --page-margin 14mm` =
purani hardcoded values → koi class-override na ho to output bilkul waisa.

**Verify:** `pytest` = **800 passed** (poora suite). Browser test baaqi (server
restart ke baad — neeche).

## 2026-07-23 — Marhala 4A · Commit 2: per-class print settings backend + chain

Maqsad: 3 print knobs (font_size, q_gap, page_margin) per-class store + resolve.
Row-level fallback: class ki row ho to woh, warna school_settings ke global
defaults. UI 4B mein; yeh sirf backend + endpoint.

- `app/core/database.py` — (1) school_settings migration mein 3 naye global-default
  columns `print_font_size/print_q_gap/print_page_margin` (DEFAULT 14 = maujooda
  print.html values, purana output na badle). (2) naya `class_print_settings` table
  (`class_key` PK = normalize_class(class_name); font_size/q_gap/page_margin NOT NULL).
- `app/schemas/requests.py` — `SchoolSettings` mein 3 fields (default 14).
- `app/repositories/settings_repository.py` — `upsert` mein 3 columns (accent jaisa).
- `app/services/settings_service.py` — `save_settings` 3 fields pass karta hai.
- **naya** `app/repositories/class_print_settings_repository.py` — get(class_key)/upsert.
- **naya** `app/services/class_print_settings_service.py` — `get_print_settings(class_name)`:
  normalize_class → class row → warna global. Row-level fallback.
- `app/schemas/responses.py` — naya `PrintSettingsResolved` (font_size/q_gap/page_margin).
- `app/api/school_settings.py` — naya `GET /api/print-settings?class_name=` (auth same router).

**Verify:** temp-DB smoke (real DB safe) — fresh default 14/14/14, global override,
class-row wins + normalization ("class 5"=="Class 5"==" CLASS 5 "), aur other/empty/None
class → global fallback. `pytest tests/test_settings_repository.py tests/test_api_routes.py`
= 62 passed. Client-side (print.html JS apply) = Commit 3.

**Baaqi:** naye service/endpoint ke liye dedicated test abhi nahi likha (existing pass;
smoke se cover) — chaho to Commit 3 se pehle add kar dun.

## 2026-07-23 — Marhala 4A · Commit 1: print margin bug (28mm → 14mm)

Maqsad (per-class print settings feature ka Commit 1 — sirf bug fix, aage nahi barha).
Bug: `print.html` mein `@page { margin: 14mm }` **+** `.sheet { padding: 14mm }`, aur
`@media print` mein `.sheet` padding reset nahi hota tha → chhapte waqt asal margin
14+14 = **28mm** ban raha tha.

**Faisla (plan §0 — single source):** `@page` margin `0`, saara page-margin `.sheet`
padding se, `var(--page-margin)` (default `14mm`). Isse bug bhi theek aur aage
`page_margin` setting ke liye mechanism bhi tayyar (throwaway `padding:0` nahi likha).

- `static/print.html` — 3 edits: (1) `@page` margin `14mm→0` (2) `:root` mein
  `--page-margin: 14mm` (3) `.sheet` padding `14mm → var(--page-margin)`.
- `@media print` block chhua nahi — padding ab var se aata hai (14mm), single source.

**Asar:** har paper ka print margin 28→14mm (yeh deliberate correction, user ne manzoor
kiya). Font/spacing waghera bilkul waise hi — koi aur farq nahi. Sirf CSS, koi
backend/JS nahi. User browser test karega.

**Note (4B ke liye):** `export_service.py` (DOCX/python-docx + PDF/LibreOffice) apna
**alag** layout render karta hai — Word default ~1inch margin, yeh CSS use hi nahi karta.
4A/print.html ke settings export par apply NAHI honge. Teacher kis raaste se print karta
hai (browser vs export) — 4B se pehle confirm karna.


## 2026-07-21 — feature/print-shortfall (print.html panel + sections_meta persistence)

Maqsad: print.html blueprint jaisa shortfall payghaam dikhaye (reason + read-only
options), do jagah alag wording ka khatra khatam. Masla (pichle session ka STOP):
`shortfall_details` (reason/options) DB mein **mehfooz nahi hoti** — assembly ke waqt
banti hai phir discard. Sirf `sections_meta` bachti hai (heading/question_ids/marks/
shortfall-int). Isliye backend change laazmi tha.

**Faisla (Option 1):** reason/options ko **`sections_meta` ke andar** hi rakho (alag
column/migration nahi). Short section par hi keys aati hain; poore section par bilkul nahi.

- `app/services/blueprint_paper_service.py` — short section ki meta mein `shortfall_reason`
  + `shortfall_options` embed (`diag` se). Full section = keys hi nahi.
- `static/print.html` — naya `sectionShortfallHtml(sec, gotCount)`: `shortfall_reason` ho
  to panel (heading + wajah + read-only options), warna **purana numeric note**
  (`{wanted} maange, {n} mile`). Options **clickable nahi**. Naya `.shortfall-panel`
  CSS (`display:block` — `.no-print` ke inline-flex ko override).
- `tests/test_blueprint_shortfall_reason.py` — `TestSectionsMetaPersistence` (short →
  reason+options meta mein; full → keys absent).

**SHART (poori hui):** purane papers ke `sections_meta` mein reason/options nahi →
**numeric-note fallback** chalta hai (bilkul pehle jaisa). `.no-print` usool bar-qarar —
dono branch screen-only, kaghaz par kuch nahi.

**Real-DB check:** 79 papers, 0 JSON parse-fail, 0 shape-issue → koi page nahi tootta.
27 legacy short-sections (shortfall>0, no reason) → numeric note. 0 sections mein abhi
reason (kuch regenerate nahi hua).

**Verify:** **784 tests pass, ruff clean.** (Uncommitted working-tree changes — commit
Irfan ke kehne par.) Browser render (panel + Ctrl+P par note gayab) baqi — Irfan ka test.

## 2026-07-21 — feature/design-base (Brand config + local fonts + icon sprite)

Sirf **tanzeem** ka kaam — **koi visual badlaav NAHI**, pages bilkul pehle jaise. Teen
QADAM, teen alag commits. Maqsad: branding ek jagah se, app fully offline (fonts local),
aur nav icons ek sprite se.

**QADAM 1 — Brand config:**
- `config/brand.json` (Parcha / "Parcha Paper Maker" / "Exam paper generator" / colours).
- `app/services/brand_service.py` — **startup par ek dafa** parhta hai (module-load), file
  missing/kharab ho to **crash NAHI** — safe defaults + `uvicorn.error` warning. `get_brand()`.
- `GET /api/brand` (`app/api/brand.py`, `BrandResponse` schema). **Jaan-boojh kar auth ke
  bahar (public)** — cosmetic shell hai (koi secret/DB/AI-cost nahi) aur har page load par
  chahiye; auth ke peeche hota to key set hone se pehle har page par key-gate khul jata.
- `static/js/brand.js` — `/api/brand` se `document.title` (`<page> — full_name`) + sidebar
  `.brand .name` set. Defaults baked (config jaise) → fetch fail par bhi sahi text, **koi FOUC nahi**.
- Sab 7 pages: `<body data-page="...">`, hardcoded **"AII Smart Paper Maker" → "Parcha Paper
  Maker"**, brand.js include. (`.brand .name` par **full_name** dikhta hai — pehle jaisa full
  naam.)
- `index.html`: `.sidebar` → **`.app-sidebar`**, `.nav-link` → **`.app-nav a`** (baqi 6 pages
  jaise). Safe kyunke active-state JS `[data-nav]`/`data-active` par chalta hai, class par nahi.

**QADAM 2 — Fonts local (offline):**
- 9 woff2 `static/fonts/` mein: **IBM Plex Sans** 400/500/600/700, **Noto Nastaliq Urdu**
  400/600, **Source Serif 4** 400/600/700 (fontsource CDN = official fonts, per-weight).
- `static/app.css` `@font-face` (sab `font-display: swap`).
- Sab pages se Google Fonts ke **3 links** (2 preconnect + css) hataye → `<link rel="stylesheet"
  href="/static/app.css">`.
- Cache middleware: `/static/fonts/*.woff2` par **1-saal immutable**; `app.css`/`icons.svg`
  par jaan-boojh kar **koi long cache nahi** (StaticFiles ka default ETag/304).
- `.urdu/.ur` stack (sirf index mein defined) pehle se **Jameel-first** — koi tabdeeli nahi.

**QADAM 3 — Icon sprite:**
- `static/icons.svg` — **10 unique `<symbol>`** (i-generator/library/bank/blueprint/outcomes/
  slo-health/adaptive/analytics/mypapers/settings), sab `viewBox 0 0 24 24`, stroke 1.8, round.
- `.icon { 17px }` app.css mein; **index apne `.app-nav a svg` se 19px** rakhta hai (index ke
  icons pehle 19px the — chhote na hon, no-visual-change).
- 6 sidebar pages ke inline nav SVG → `<svg class="icon"><use href="/static/icons.svg#i-..."></use></svg>`.
- `static/brand/logo.svg` (mojooda navy+blue document mark, standalone — abhi koi consumer nahi).
- `print.html` **chhua nahi** (text-only nav, koi icon nahi — scope ke mutabiq).

**FAISLE / spec se hatt kar (jaan-boojh kar):**
- **Source Serif 4 bundle kiya** — font-list mein nahi tha, magar index ke paper-preview mein
  use hota hai (`Georgia` fallback). No-visual-change + offline honor karne ke liye zaroori,
  warna offline preview Georgia par gir jata.
- **`/static` mount naya add** kiya (`app/main.py`) — spec ke saare asset paths `/static/...`
  maangte the, app pehle sirf `/` par mount tha. Legacy `/apiClient.js` waise hi chalta hai.
- Fontsource ka **"latin" subset** — extended-Latin/doosre scripts system font par fall back
  (UI text ke liye kaafi).
- **`/api/brand` public** rakha (upar wajah).

**BAQI (follow-up, is scope se bahar):** `index.html` ke tip-text mein 3 jagah **"AII"** copy
bacha hai ("AII suggests", "AII PDF/images parse karke…") — sidebar brand naam nahi, body copy
hai; 1d ne sirf "AII Smart/… Paper Maker" naam kaha tha.

**Files:** naye — `config/brand.json`, `app/api/brand.py`, `app/services/brand_service.py`,
`static/js/brand.js`, `static/app.css`, `static/icons.svg`, `static/brand/logo.svg`,
`static/fonts/*.woff2` (9). Chhue — `app/main.py`, `app/schemas/responses.py`, sab 7 static HTML.

**Verify:** **772 tests pass, ruff clean.** Server smoke (curl): saare 7 pages + app.css +
icons.svg + logo.svg + brand.js + `/api/brand` + 9 fonts → **200**; fonts par 1yr immutable,
css/svg par sirf ETag. **Browser render (icons `<use>`, font visual, Urdu RTL, print preview,
OFFLINE) baqi — Irfan ka incognito test** (Claude-in-Chrome extension is env mein connect nahi tha).

## 2026-07-19 — feat/slo-health (SLO Health page — Marhala 2 Hissa C)

Ek page jo DONO taraf ka gap dikhata hai: (a) SLO jinke paas koi (published) question
nahi, (b) (published) questions jinke paas koi SLO tag nahi. Plus per class/subject
health line aur "SLO import baqi". `GET /api/slo-health` (coverage/shortfall ke parallel,
magar paper-scoped nahi — poore data par). Live compute (JOIN), snapshot NAHI.

**Sab se ahem:** page GENERAL hai — SAARI classes/subjects/strands ke liye. Koi class/
subject/strand HARDCODE nahi (abhi sirf Pre Year 1 Math ka SLO data hai, magar Grade
4/5/6 Math, Grade 7 Science, Grade 8 Geography syllabus mein maujood — aate hi khud aayenge).

**Faisle amal mein:**
- **Covered = SLO ke paas >=1 linked PUBLISHED question.** draft/archived shumar NAHI —
  page par saaf note (`draft_note`).
- **Questions par class column NAHI** (koi migration nahi kiya). grade `syllabus_topic`
  se LEFT JOIN; jis question ka topic-link nahi uska grade na-maloom -> **"(class na-maloom)"**
  bucket (Part 3 aur health line mein).
- **`normalize_class`** naya (`app/core/text_norm.py`) — `normalize_subject` jaisa alias-dict
  (abhi khali, structure mojood). Case/alias normalize har jagah: class, subject, bloom.
- **Bloom NULL SLO -> "(bloom na-maloom)"** bucket (silently REMEMBER nahi maante).
- **import_pending** = `syllabus_repository.list_distinct_subject_grade()` ke woh combos
  jinka SLO group nahi.
- **Filter** (class+subject) DB se distinct — dropdown response ke `classes`/`subjects`
  se populate (hardcode nahi); filter server-side, magar dropdown lists hamesha POORE.

**Naye REPO functions (coverage/shortfall ke shared functions NAHI chhede):**
- `slo_repository.list_all()`
- `question_slo_repository.slo_ids_with_published_questions()` (JOIN questions status='published')
- `questions_repository.list_published_with_grade_and_tag()` (LEFT JOIN syllabus_topics for grade,
  EXISTS+JOIN slo for is_tagged — orphan link ko tagged nahi ginta, covered jaisa).

**MULTI-TENANT (abhi implement NAHI — sirf jagah):** teeno naye repo functions mein optional
`school_id` param add kiya jo abhi use nahi hota — aage 100+ schools par `WHERE school_id = ?`
yahin lagega bina signature tode. Service/route abhi ise pass nahi karte.

**Files:** `app/services/slo_health_service.py` (naya) · `app/api/slo.py` (route) ·
`static/slo-health.html` (naya page) · nav link **6 pages** (index, slo, bank, blueprint,
library, print — user ne "5" kaha tha; print.html ka nav bhi maujood tha to consistency ke
liye woh bhi). NOTE: bank/blueprint/library/print ke nav mein "Learning Outcomes" (slo.html)
link pehle se nahi tha — sirf SLO Health add kiya (scope).

**Tests:** `test_slo_health_service.py` (11) + `test_slo_health_api.py` (2) = 13 naye —
seed-based, koi hardcoded DB count nahi (apne seeded id/norm-keys par assert). draft-covered,
class-na-maloom, bloom-null, import-pending, filter, multi-class general — sab covered.

**Baqi:** browser test + merge teacher karega. Pre-generate/blueprint integration alag scope.

**FUTURE (idea — implement nahi):** Blueprint shortfall warning behtar karna. Abhi sirf
"Section A: 20 maange, 8 mile" dikhata hai. Behtar yeh ho ke **wajah** bhi bataye (kaunsi
shart tang hai) aur **teen option** de — bilkul Hissa B ke Bloom shortfall ki tarah:
(a) jo mil raha usi se banao, (b) filan shart hata do -> itne milenge, (c) naye questions
likho. App khud chup-chaap adjust NA kare.

---

## 2026-07-19 — feature/slo-phase-2b-shortfall (Bloom shortfall — Marhala 2 Hissa B)

Paper ka asal Bloom distribution vs class standard (Pre-Primary 70/30) — per-Bloom
**kami (shortfall)**. `GET /api/paper/{id}/bloom-shortfall` (coverage endpoint ke parallel).
**App khud kuch adjust NAHI karta** — sirf report; teacher UI par 3 option chunta hai.

**Faisla (darj):** Bloom source = **SLO ka `bloom_level`**, question ka nahi. Wajah: SLO book
se soch kar bana (PY1 Math 31 remember/19 understand = 70/30 fit); question ka bloom auto-derive
+ mashkook ("Trace the number 3" par APPLY; 197 mein 80 APPLY = 41%, standard se door).

- **`slo_shortfall_service.py`** (naya): SLO bloom se actual, `bloom_standards.get_bloom_suggestion`
  se target %, **largest-remainder (Hamilton)** se target counts (sum = N). Per-Bloom
  `{needed, actual, short}` + total_short. Live compute (JOIN), snapshot nahi.
- **`question_slo_repository.list_slo_blooms_for_questions`** (naya) — question→SLO.bloom rows.
  Coverage ka shared `list_links_for_questions` **NAHI chheda** (uski query na toote).
- **`app/api/papers.py`** — naya route; **`static/index.html`** — Bloom Shortfall panel (SLO Coverage
  ke neeche): per-Bloom bar + kami + **3 option** (jo mil raha usi se / doosre Bloom se / naye sawal).

**Ahem faisle amal mein:**
- **Multi-SLO** question → uske SLOs mein sabse **UNCHA (highest)** Bloom; UI par `ℹ️ N multi-SLO` nishaan.
- **Denominator N** = classifiable questions (SLO-tagged AND bloom maloom).
- **CASE-normalize** (`_norm` = LOWER+TRIM) har bloom par — `REMEMBER`(q) / `remember`(slo) /
  `remember`(standard) sab ek jagah; warna ginti zero. (Source SLO hai, magar defensive.)
- **untagged** (koi SLO link nahi) aur **bloom-unknown** (SLO tagged par bloom NULL) — **DO alag ginti**,
  distribution se bahar (subject badalne par masla tagging ka hai ya SLO-data ka — farq zaroori).
- Koi classifiable question na ho → panel ZERO nahi, **graceful message** (coverage `_no_universe` jaisa).

**Tests:** `test_slo_shortfall_service.py` (11) + `test_slo_shortfall_api.py` (2) = 13 naye —
seed-based, koi hardcoded bank-count nahi. ruff clean; full suite **759 pass** (746 → 759).
Browser test + merge teacher karega.

**Baqi:** Hissa C (SLO Health page) pending. Pre-generate shortfall (bank-availability) alag scope —
abhi nahi (post-hoc pehle). Data gaps qaim: Pre-writing/C-05/C-06/Colour-Circle-11-24 (pichhli entry dekho).

---

## 2026-07-19 — Pre Year 1 Math SLO tagging (DATA kaam, app code nahi)

197 Pre Year 1 Mathematics questions ko SLO se tag kiya — coverage report ko zinda
karne ke liye (pehle sirf 8 tagged the). Yeh mostly DATA kaam hai; app code touch
nahi hua, do standalone one-shot scripts `scripts/` mein (branch `chore/slo-prefill-script`).

**1. `scripts/prefill_slo_pre_year1_math.py`** (one-shot, read-only — DB mein kuch NAHI likhta):
Question text ke template se slo_code khud derive karta hai (manual picker nahi):
- Number: `Trace the number N` → N-03/N-11/N-16 · `Count..write`/`How many`/`There are`/Urdu
  count+write → N-04/N-12/N-17 · `Colour` → N-06 · `Circle all` → N-07 — **range** 1-10/11-20/21-24
  se sahi code. Colour/Circle sirf 1-10 (11-24 ka SLO nahi → khali).
- Shape: `Trace the <shape>` text se · `Name this shape` MCQ ka **correct_answer_en** (answer-key)
  se — S-01..S-04 (flat) / D-01..D-06 (solid).
- Comparison: topic `Concept of "a" and "b"` se C-01..C-04.
- Koi rule match na ho → khali (andaaza nahi).
Output DO sheets ek Excel mein: **UPLOAD 161** (auto-filled) · **MANUAL 36** (28 khali +
8 review). import `pd.read_excel(sheet_name=0)` = pehli sheet (UPLOAD) parhta hai (script verify karta).
`.xlsx` gitignored (`scripts/*.xlsx`).

**2. Teacher ne UPLOAD sheet import ki** (`/api/slo/assign-import`): **Updated 161, Errors 0**.
Tagging 8 → **169 questions**.

**3. 8 stray test-tags theek kiye** (bina delete ke): 8 `How many..are there?` MCQ par pichhle
browser-test ka kachra tha (number question par D-01/C-01/S-01/W-01/N-01). Kyunki assign-import
**replace-set** hai, `fix_8_stray_tags.xlsx` (8 rows, sab sahi **N-04**, range 1-10) upload se
purana ghalat link khud replace ho gaya — alag delete ki zaroorat nahi. **Updated 8**.

**4. `scripts/clean_stray_slo_links.py`** — dry-run cleanup helper (default sirf dikhata, delete
`--delete` par). Is dafa **istemal NAHI hua** (replace-set behtar tha), aainda ke liye rakha.
Iske dry-run ne ek bara khatra pakRa: table 8 nahi 169 links par tha (teacher upload ho chuki thi),
to "saare PY1 links" wala pehla broad target 161 sahi tags mita deta — target ko precise
(`How many` + non-count code) kiya, tab 8 dikhe.

**TASDEEQ:** coverage report ab **zinda** — bare paper par **13/50 (26%)**, aur **Pre-writing 0/3**
(pehle jhoota `1/3` dikh raha tha, kyunki number-8 question par ghalti se W-01 laga tha).

**DATA GAP (report ne khud pakRa — aainda tagging/question-banane ke liye darj):**
- **Pre-writing** ke teeno SLO (W-01/02/03) — bank mein ek bhi question nahi.
- **Comparison C-05** (which has more/less) aur **C-06** (equal groups) — koi question nahi.
- **Colour/Circle numbers 11-24** — in skills ka koi SLO define nahi (28 questions MANUAL sheet
  mein khali chhoRe — inhe kabhi tag nahi kar sakte jab tak SLO na banein ya questions na haten).

**Baqi:** Hissa B (shortfall 70/30) + Hissa C (SLO Health page) abhi bhi pending. `feature/slo-export-class-filter`
(export grade/subject filter, 746 tests) bhi merge ke intezaar mein — alag branch.

---

## 2026-07-19 — feature/slo-export-class-filter (SLO export grade/subject filter)

SLO bulk-assign export (`GET /api/questions/slo-export`) ab optional `?grade=&subject=`
leta hai — kyunki export saare 317 Mathematics questions deta tha (Pre Year 1 ke ~197
nahi), teacher ko tagging ke liye chhaant-na parta. **Backward compatible:** koi param na
ho to purana sab-questions behaviour + `slo_assign_export.xlsx`.

- **Naya `app/core/text_norm.py`** — `normalize_subject()`: alias **dict** (`math/maths →
  mathematics`), hardcoded if-else NAHI (nayi alias add karna aasaan). Compare-time only, data untouched.
- **`questions_repository.list_for_slo_export(grade, subject)`** (naya) — grade par
  `syllabus_topics` JOIN (case/whitespace-insensitive); **`syllabus_topic_id` NULL wale grade
  filter par khud EXCLUDE** (expected, INNER JOIN). subject dono-taraf `normalize_subject` se
  Python-side filter — DB mein `Math`/`Mathematics` dono ho to bhi sahi.
- **`question_slo_import_service`** — `build_export_xlsx(grade, subject)` (return **bytes hi**,
  purane 2 export tests untouched) + naya `export_filename()` → dynamic naam
  `slo_assign_export_Pre_Year_1_Mathematics.xlsx`. Columns waise hi 5 — koi naya nahi.
- **`app/api/slo.py`** — route par optional query params + dynamic `Content-Disposition`.
- **`static/slo.html`** — export par grade **`<select>`** (`/api/syllabus-grades` distinct se
  populate — **hardcode NAHI**, nayi class add hote hi aa jaye) + subject input + button URL builder.

**NOTE (code change NAHI kiya, sirf darj):** coverage universe (`slo_coverage_service`) abhi
`normalize_subject` use nahi karta — `papers.subject` vs `slo.subject` par `LOWER(TRIM)` (alias
nahi). Aaj teeno 'Mathematics' hain to theek; Math/Mathematics mismatch aaya to universe khali
(covered SLO phir bhi dikhte, remaining/% None — crash nahi). [[project-papermaker-roadmap]] Hissa B se pehle chhota fit ho sakta.

**Tests:** `tests/test_slo_export_filter.py` (8) — **seed-based, koi hardcoded 317/197 nahi**
(apne `q1..q5`/`t_py1,t_py2` ke id-sets se assert). ruff clean; full suite **746 pass** (738 → 746).
Browser test + merge/push teacher karega (GitHub Desktop).

---

## 2026-07-18 — fix/paper-class-and-delete-warning (2 zinda bugs)

SLO Marhala 2 Hissa A ke dauran nikle do data-masle ki tashkhees se: `class_name`
None (47/63 papers) aur orphaned papers (40/63). Do fixes (merge `4fb1409`):

**Fix 1 — Generator class_name capture** (`static/index.html buildPaper`): ab
`class_name: val('gradeSelect') || null` body mein jaata hai. Backend
(`GeneratePaperRequest.class_name` + `_persist_paper`) pehle se ready tha — masla
sirf frontend line ka tha (isi liye har Generator paper class None banta,
coverage universe kabhi nahi banta). Zero backend change. **Regression-guard**:
`test_generator_class_name.py` `index.html` ke buildPaper mein `class_name`+`gradeSelect`
ki maujoodgi check karta — line dobara gayab hui to test fail.
(Blueprint/bank-paper pehle se class bhejte the — free-text `bpClassName`/`bpClass`.)

**Fix 2 — question delete se pehle paper warning**: `papers.question_ids` JSON blob
hai (koi FK/cascade nahi), is liye sawal delete karna papers ko chup-chaap orphan
kar deta tha. Ab delete se pehle warning kaun se papers tootenge:
`papers_repository.find_papers_containing` (quoted-id `LIKE '%"uuid"%'`, substring-safe),
`paper_service.papers_using_question` (count+titles, untitled→'(Untitled)'),
`GET /api/bank/questions/{id}/paper-usage`, `bank.html deleteQuestion` (3-4 naam +
"aur N mazeed"). **Sirf warning** — koi block/cascade/snapshot nahi (jaan-boojh kar simple).

**Haath NAHI lagaya (data, code nahi):** 40 orphaned papers (deleted sawal wapas nahi
aate — murda), 47 None-class papers (coverage graceful handle karta, andaaze se backfill
galat hota). **Deferred tajweez:** Blueprint/bank-paper ka free-text class box →
dropdown+custom fallback (isi se Jasmine/NUrsery/play aaye) — alag chhota kaam, baad me.

**Tests:** `test_generator_class_name.py` (2) + `test_paper_delete_warning.py` (6) =
8 naye. ruff clean; full suite **738 pass** (730 → 738). Browser test (teacher) green:
Generator par Pre Year 1 chuna → paper class set + poora coverage; delete par paper-naam warning.

---

## 2026-07-18 — SLO Marhala 2 Hissa A (paper coverage + Excel tagging)

Do stacked branches, tarteeb se master mein merge (`--no-ff`):
`feature/slo-phase-2a-coverage` (9d8a9d1) → `feature/slo-phase-2a-excel-tagging` (f7876c3).

**Coverage** (`slo_coverage_service.py`, `GET /api/paper/{id}/slo-coverage`):
Paper ke sawalon se covered vs class/subject ke reh gaye SLO + strand breakdown +
untagged-question ginti. **Live compute (JOIN), stored snapshot NAHI** — link/SLO
baad me badle to report khud sahi rahe. class match **normalized** (`LOWER(TRIM)`)
kyunki `papers.class_name` free-text/gandi hai; universe na mile (class None ya us
class/subject ki koi SLO nahi) to **graceful covered-only + saaf message**, koi crash nahi.
`coverage_percent` = covered∩universe / total. Repo: `list_links_for_questions` (batch
JOIN), `list_by_class_subject_normalized`. UI: `index.html` paper preview ke neeche
SLO Coverage section (progress bar + strand table + reh-gaye list + untagged note).

**Excel tagging** (KAAM A — user manual picker use nahi karta, sab Excel/Blueprint se):
- **Naye questions**: bulk upload Excel mein optional `slo_code` column (comma-separated
  = kai SLO). Ghalat code → skip + warning, question phir bhi import (topic-behavior jaisa).
  Insert ke baad link (image-attach pattern par). `bulk_upload_template.xlsx` + bank.html hint update.
- **Purane 200+ questions**: `GET /api/questions/slo-export` (Excel: `question_id` +
  current `slo_code`) → teacher `slo_code` bhare/edit kare → `POST /api/slo/assign-import`.
  **question_id se match** (text se nahi), **replace-set** (idempotent, khali=clear).
  `question_id` protection: import par saaf error (khali/unknown id) + Excel cell-comment
  warning — real sheet-lock NAHI (over-engineer). Shared `resolve_slo_codes` (case/space-insensitive).
  `question_slo_import_service.py` naya; `slo.html` par bulk-assign card.

**Duplicate trap (confirmed + tested):** bulk question import upsert NAHI karta — har row
naya uuid. Same sheet dobara upload = QUESTION duplicate. Isi liye purane questions ke liye
slo-export/assign-import (id se) — question sheet re-upload NAHI. SLO links khud replace-set
(multiply nahi hote). `test_bulk_import_slo.py::test_reupload_duplicates_the_question` documents.

**Data findings (live test):** saare Pre Year 1 Math papers ORPHANED (question_ids ab
questions table me nahi — sawal delete ho chuke, coverage 0 dikhega); real-question papers ka
`class_name = None` (poora universe view sirf class-set paper par). Ye data-hygiene, code bug nahi.

**Tests:** `test_slo_coverage_{service,api}.py` (13) + `test_bulk_import_slo.py` (6) +
`test_question_slo_import.py` (11) = 30 naye. ruff clean; full suite **730 pass** (700 → 730).
Browser test (teacher) green: bulk-assign 8 tags, purana paper covered-only + graceful,
naya Pre Year 1 paper POORA view (0/50, 5 strands sahi, reh-gaye 50), 'play' class graceful.
`sample_slo_assign.xlsx` (gitignored) test ke liye.

**Baqi:** Hissa B (shortfall) + Hissa C (SLO Health page) abhi NAHI. Aur [[project-papermaker-kaam-b-collapse-manual-add]] (bank.html manual form collapse) pending.

---

## 2026-07-18 — feature/slo-phase-1 (SLO Marhala 1 — question↔SLO link)

**Scope:** Har question ko ek ya kai SLO se jorna (Marhala 2 paper-coverage report ki buniyaad).
Bulk-assign Excel is marhale me NAHI (pehle manual UI se validate) — baad me
`question_slo_import_service` + `POST /api/slo/bulk-assign` me fit hoga.

**DB** (`app/core/database.py`): naya **`question_slo` link table** (column NAHI) —
`question_id`, `slo_id`, `created_at`, composite PK `(question_id, slo_id)`. Wajah: (1) ek sawal =
kai SLO, (2) `questions` table bilkul untouched → 200+ purane questions bina migration ke chalte
rahein, (3) gemini (protected) question bhi tag ho bina uske row ko chhue. `slo_id` (PK) se link
(slo_code se nahi) — re-import par id stable; report ke liye slo_code/slo_text JOIN se. FK enforce
nahi (baaqi schema jaisa) — coverage report defensive INNER JOIN. Index: `idx_question_slo_slo`
(reverse lookup "is SLO ke saare questions" — Marhala 2). Migration = sirf CREATE TABLE/INDEX
(idempotent, server restart chahiye).

**Repo** (`app/repositories/question_slo_repository.py`, naya): `replace_for_question` (replace-set,
duplicate INSERT OR IGNORE), `list_slo_ids_for_question`, `list_slos_for_question` (JOIN, orphan
link INNER JOIN se khud drop), `list_question_ids_for_slo` (reverse), `existing_slo_ids` (link se
pehle validate — orphan se bachao).

**Service** (`app/services/question_service.py`): `set_slos_for_question` (sirf maujood slo_ids
likhta — orphan filter), `get_slos_for_question`; manual create/update me `slo_ids` diya ho to link
write (replace-set).

**API** (`app/api/questions.py`): `GET /api/questions/{id}/slo` + `PUT .../slo` (replace-set, khali
list = clear; **har source** par — link table protected row ko nahi chhoota); `slo_ids` optional on
manual create (`POST /api/bank/questions`) + update (`PATCH /api/bank/questions/{id}`).
Schemas: `ManualQuestionRequest`/`Update` me `slo_ids`, naya `SetQuestionSloRequest`; update ke
"kam az kam ek field" validator me `slo_ids` shaamil.

**UI** (`static/bank.html`): Add + Edit modal me **SLO picker** (checkbox list + search).
Filter subject+class par — **gate:** subject/class/topic teeno maloom hon tabhi bharta, warna
"pehle topic chuno" hint (teacher ko 50 SLO me se dhoondna na pare). Add: subject/grade/topic
badalne par reset. Edit: subject se filter, linked SLO pre-checked, un-check kar ke clear.
(Edit modal sirf manual questions ke liye khulta; gemini tagging PUT endpoint se — UI me abhi surface nahi.)

**Tests:** `tests/test_question_slo_repository.py` (7) + `tests/test_question_slo_api.py` (11) =
18 naye. ruff clean; full suite **700 pass** (682 → 700). Live server smoke: PUT link → GET →
empty-PUT clear sab OK (dev DB cleanup). Browser test (teacher): gate/add/edit/clear/purane-questions —
sab green, tabhi merge (`--no-ff`, commit `26fb90c` → merge `fca1fbf`).

---

## 2026-07-18 — feature/slo-phase-0 (SLO Marhala 0 — table + Excel import)

**Scope:** SIRF `slo` table + Excel bulk import. Question↔SLO link (Marhala 1) aur
paper coverage (Marhala 2) is marhale me NAHI. Data target: Pre Year 1 Math (~50 SLO).

**DB** (`app/core/database.py`): `init_db()` me naya `slo` table (CREATE TABLE IF NOT EXISTS,
existing data safe) — `id` TEXT uuid PK, `class`, `subject`, `slo_code` (UNIQUE), `slo_text`,
`bloom_level` (nullable), `strand`, `created_at`. `strand` ALAG column (slo_code parse nahi karte —
Marhala 2 strand-wise coverage seedha column par bane). Index: `idx_slo_class_subject`.

**Bloom auto-suggest** (`app/core/bloom_standards.py`): naya `suggest_bloom_from_text()` —
slo_text ke pehle content-verb se level (`_VERB_BLOOM` map: count/identify/recognize→remember,
describe→understand, solve→apply, compare→analyze...). Fillers (students/will/be/able/to) skip.
Verb match na ho → **None** (default "remember" NAHI, taake galat label na lage). Sirf tajweez —
import me teacher ki di hui value overwrite nahi hoti; khali ho tabhi auto-fill.

**Import service** (`app/services/slo_import_service.py`, `library_meta_import_service` pattern par):
pandas `read_excel(dtype=str)`, columns lowercase-normalize. Required: class/subject/slo_code/slo_text;
optional: bloom_level/strand; `book_pages` + koi bhi extra column IGNORE (error nahi).
Duplicate `slo_code` par **UPDATE** (draft dobara import: slo_text/bloom_level/strand refresh,
`created_at` untouched), naya par ADD. Ek row fail se baaki nahi rukti. Summary:
`{added, updated, errors, results:[{row, slo_code, status, reason?}]}`.

**Repo/API/UI:** `app/repositories/slo_repository.py` (insert/find_by_code/update_by_code/list_by_filters);
`app/api/slo.py` — `GET /api/slo` (class/subject/strand filter), `GET /api/slo/template`,
`POST /api/slo/import`; `app/main.py` me router register (auth ke peeche). `static/slo.html` (import +
summary + filterable list), `static/slo_import_template.xlsx` (header + 4 sample rows), index.html nav link.

**Strand codes (is book se, 50 SLO):** W=Pre-writing(3), N=Number(25), C=Comparison(6),
D=Solid Shape(8), S=Flat Shape(8). Pattern/Measurement/Data is book me NAHI.

**Tests:** `tests/test_slo_import.py` (10) + `tests/test_slo_api.py` (6) = 16 naye. ruff clean;
full suite **682 pass** (666 → 682). Smoke test (real boot): template/import/re-import/list/slo.html
sab OK; bloom verify (compare→analyze, count/recognize→remember, trace→None); demo rows real DB se saaf.

---

## 2026-07-18 — feature/db-index-caching (HISSA 4 DB index + HISSA 5 caching)

**HISSA 4 — image_library filter indexes** (`app/core/database.py`, commit `59517e0`):
- `init_db()` me 3 `CREATE INDEX IF NOT EXISTS`: `syllabus_topic_id` (list filter +
  topic_ids_with_images/topic_image_counts + find_by_name_and_topic — 4 code paths), `subject`, `grade`.
- Migration = sirf CREATE INDEX (existing data safe, idempotent, sirf server restart chahiye — koi schema change nahi).
- Query plan pehle `SCAN image_library` → ab `SEARCH ... USING INDEX`. init_db 2x chala, error nahi.
- **Scope se bahar (index nahi lagta):** search `q` (`name/keywords LIKE '%..%'` leading wildcard) aur
  `category` (`LOWER(category)=?`) — FTS/expression index chahiye, HISSA me nahi.
- **Reality:** abhi sirf 106 rows — koi query slow nahi thi; ye future-proofing hai (library barhne par).

**HISSA 5 — caching headers** (`app/main.py`):
- Nayi `@app.middleware("http")` — sirf `/library/*.webp` (full + thumbs) par
  `Cache-Control: public, max-age=31536000, immutable` (1 saal). HTML/JS ko haath nahi (StaticFiles default ETag/304).
- **Cache-busting zaroorat NAHI** — code-verified: `image_id=uuid.uuid4()` har upload, koi route
  existing `{uuid}.webp` overwrite nahi karta (replace = delete + naya upload = naya UUID = nayi URL).
  Filename hi content-address hai. Future guardrail: agar kabhi in-place replace feature bane to
  naya UUID/`?v=` rakhna warna immutable stale dega.
- Verified (TestClient): webp → immutable header; library.html/index.html → koi long-cache nahi.

**Tests:** ruff clean; full suite **666 pass**. Do alag commits (H4 db, H5 main).

---

## 2026-07-18 — feature/bulk-convert (HISSA 3 — 99 purani PNG → smart WebP)

**Kya kiya:** `image_library` ki 99 purani rows (`file_path .png`, `compression=None`, static/library/)
ko smart WebP me convert kiya — `process_and_save()` (same uuid) se full webp + 300px thumb, phir DB update.
Data migration hai (koi naya code nahi; detection HISSA-2/saturation-gate wahi).

**Irreversible-safety (convert se PEHLE):**
- DB backup: `paper_maker_backup_bulkconvert_20260718_*.db`
- 99 original PNG backup: `backups/library_png_20260718/` (static ke bahar) — `.gitignore` me `backups/` add
- Convert ke baad browser me crisp confirm (horse_bw, candy_bw, trace, sharpener_bw, walnut_bw lossless;
  basket_c colour saaf) — TAB original .png delete.

**Per row:** `file_path` → `library/{uuid}.webp`, `thumb_path` → `library/thumbs/{uuid}.webp`,
`compression` → lossless/lossy. Per-row try/except + commit (resumable; ek run timeout hua, doosre ne baaki 21 pura kiya).

**Natija:** 99/99 convert, 0 fail. **lossless 76, lossy 23** (saare lossy = `_c` colour photos).
Size: PNG 52.93 MB → WebP full **21.05 MB (−60.2%)** (+thumbs 25.97 MB, −50.9%).
Lossy 23: 25.19→2.19 MB (−91.3%); lossless 76: 27.74→18.86 MB (−32%, phir bhi crisp).
Integrity: 99 webp + 99 thumb + DB sab OK.

**Note:** images aur `paper_maker.db` gitignored hain (version control me nahi) — commit sirf PROGRESS + .gitignore.
Backups (DB + 99 PNG folder) local safe rakhe. Cloud deploy-remote par push NAHI (sirf backup remote).

---

## 2026-07-18 — smart-compression: unit tests + backup push

**Unit tests — `tests/test_smart_compression.py` (16 naye, pure functions, koi DB/client nahi):**
numpy se controlled images bana kar exact boundaries test kiye —
- `_buckets_to_cover`: 1 flat colour → 1 bucket; 60/40 → 2; photo-noise → >40;
  **boundary 47 colours → 40 buckets** (lossless side) vs **48 → 41** (lossy side); khaali → 1.
- `_is_low_saturation`: pure grayscale → True; saturated red → False;
  **boundary 13% sat (<0.14) → True** vs **15% (>0.14) → False**; khaali → True.
- `_choose_compression` **3-stage order**: force_lossless jeetta hai; high-detail B/W
  (64 near-gray, buckets 55>40 par low-sat) → saturation gate lossless deta hai (bucket rule se pehle);
  saturated colour noise → lossy; flat colour graphic (chand buckets) → lossless.

**Run:** ruff clean (import-order auto-fix); **poora suite 666 pass** (pehle 650 → +16).

**Git:** commits `bef8ead` (feat: buckets + saturation gate) → merge `6e39909` → `1483f37` (tests).
**Push:** `backup` remote (paper-maker-backup.git) par push kiya — yeh **backup repo hai, deploy-remote NAHI**
(Railway/Northflank yahan configured hi nahi). Isliye "master push se deploy todta hai" wala rule nahi toota.
`master -> master` synced (ahead 0).

---

## 2026-07-18 — feature/smart-lossy-webp: saturation gate (detailed B/W line-art false-lossy fix)

**Asli _bw test se pakda:** library me 65 named images hain (`_bw` = line-art, `_c` = colour) —
UUID naam se store, DB `image_library.name` → `file_path` mapping se mile (original `.png`, compression=None).
Naye buckets-metric par 40 me se 38 `_bw` lossless, par **2 false-lossy**: `sharpener_bw` (51 buckets,
21 shaded sharpeners) aur `walnut_bw` (55 buckets, dense stippling) — ground truth Read se dekha, dono
sach me B/W line-art hain jo lossy me smear ho jate.

**Root cause:** detailed B/W line-art (grey shading/stippling) bucket-count me simple colour photos se
**OVERLAP** karta hai (sharpener 51, walnut 55 vs cat_c 56, banana_c 46, panda_c 41). Buckets *akele*
in dono ko alag nahi kar sakte — koi N kaam nahi karega (wahi 8/16 wali limitation, dusre end par).

**Discriminator = saturation.** B/W drawing chahe kitni detailed ho, saturation ~0; colour photo ki high.
Real library par mapa: `_bw` sat-frac (S>40 wale pixels ka hissa) ≤0.122, `_c` ≥0.104.

**Fix — `app/services/image_processing_service.py`, `_choose_compression` me saturation gate:**
1. `force_lossless` (mode 1/P/transparency) → lossless  [waise hi]
2. **NAYA** `_is_low_saturation()` — sat-frac < `_SAT_LOSSLESS_MAX=0.14` → lossless (har B/W drawing, detailed bhi)
3. warna colour: `_buckets_to_cover <= _MAX_BUCKETS_LOSSLESS(40)` → lossless, warna → lossy
- Constants: `_SAT_PIXEL_MIN=40` (HSV S se upar = meaningful rang), `_SAT_LOSSLESS_MAX=0.14`.

**Validated (real library, ground truth):** 40/40 `_bw` → lossless ✓; 22/24 `_c` → lossy ✓;
sirf `cat_c`+`football_c` (muted colour) over-lossless — storage cost only, quality nahi (safety bias).
ruff clean; 85 library/image tests pass. Merged to master (LOCAL only, cloud push NAHI).

---

## 2026-07-18 — feature/smart-lossy-webp: detection metric fix (top-8 coverage → buckets-to-85)

**Masla (code review se):** purana `_is_line_art` **fixed top-8 buckets ka coverage ≥0.85** dekhta tha.
Ye multi-colour flat art par galat tha — 10-15 flat rang wali (bacchon wali crisp) illustration ka
top-8 coverage <0.85 aa jaata → galti se **lossy** (quality loss us cheez par jise crisp chahiye).
`_TOP_BUCKETS` ko 8→16 karna wahi bug ka bada version tha (16-colour art phir lossy). Magic number kaam nahi karta.

**Naya metric — "85% coverage tak kitne buckets chahiye?"** (`_buckets_to_cover`):
- Buckets ghatte order me jodo jab tak cumulative coverage ≥0.85 na ho; kitne lage = signal.
- Flat art (chand flat rang) → **kam buckets**; photo (gradients phaile) → **bohot buckets**.
- `_is_line_art = _buckets_to_cover(img) <= _MAX_BUCKETS_LOSSLESS (40)`.
- `_QUANT_SHIFT=3`, `_COVERAGE_TARGET=0.85` waise hi. `force_lossless`/`_choose_compression` unchanged.

**N=40 kaise choose kiya — real uploads par mapa (synthetic NAHI):**
- `static/uploads/` ke 1206 asli teacher images ka sample: do alag populations —
  line-art/flat **≤29 buckets** par rukta, photo **≥41** se shuru; **30–40 bilkul khaali (gap)**.
- 6 library photos ka floor bhi 46 tha — match. N=40 valley me baitha, isliye magic number nahi (±5 safe).
- Ground truth khud dekha (Read se): `099cdf59`(1b, safed worksheet+trace+text) → lossless ✓;
  `1b2feffd`(41b, 6 shaded tables+bold "SIX") → lossy ✓ (bold text q85 me bachta, tables photographic);
  `861d9631`(379b, 23 baskets photo) → lossy ✓. Delicate line-art hamesha safed pages par (kam buckets) → lossless.

**Verified:** updated service function real images par expected split; ruff clean; 85 library/image tests pass. Cloud push NAHI.

---

## 2026-07-17 — feature/smart-lossy-webp (Smart Lossy/Lossless WebP)

**Kya bana (sirf naye uploads):** har image ka type detect karke best compression —
line drawing/trace/outline → LOSSLESS (bacchon ke liye crisp), photo → LOSSY q85 (zyada saving).
Ambiguous → hamesha lossless (safety bias).

**Detection tareeqa — "dominant colour coverage" (raw unique-count se robust):**
- Raw unique-colour count ka masla: anti-aliasing se ek simple trace bhi hazaaron edge-shades de deta
  hai → galti se photo detect. Isliye coverage use kiya.
- `app/services/image_processing_service.py`:
  - `_is_line_art(full)`: RGB → numpy, colours quantize (`>>3` = 32 levels/channel, AA noise merge),
    `np.bincount` se top-8 buckets ka pixel coverage; **coverage ≥ 0.85 → lossless**, warna lossy.
  - `_has_graphic_signals(img)`: hard signals jo seedha lossless karte hain (coverage skip):
    mode "1" (bilevel), mode "P" (palette ≤256), ya real transparency. Grayscale "L" ko force NAHI
    (B/W photo ho sakta hai) — coverage decide karta hai. Signal P→RGBA convert se PEHLE capture.
  - `_choose_compression()` → `"lossless"`/`"lossy"`; full + thumb **dono same mode** use karte hain.
  - Tunables: `_LOSSY_QUALITY=85`, `_QUANT_SHIFT=3`, `_TOP_BUCKETS=8`, `_COVERAGE_LOSSLESS_THRESHOLD=0.85`.
  - Return dict mein ab `compression` bhi.
- `app/core/database.py` — `image_library.compression TEXT` (CREATE + safe ALTER; purani rows NULL)
- `app/schemas/responses.py` — `LibraryImage.compression`
- `app/repositories/library_repository.py` — `insert()` mein `compression` column
- `app/api/library.py` — single + bulk row mein `compression` add
- `requirements.txt` — `numpy` explicitly add (ab seedha import; pehle sirf pandas ke through transitive)

**Verified (manual smoke):**
- Line art (grid + circle) → `lossless`, full 6.7 KB (crisp) ✓
- Photo (random noise, worst-case) → `lossy`, full 467 KB ✓

**Baaki:** pytest + ruff (baad mein), naye detection tests likhna. Cloud push NAHI.

---

## 2026-07-17 — feature/webp-thumbnails (HISSA 2 — WebP + Thumbnails)

**Kya bana (sirf naye uploads — purani JPG/PNG untouched, woh HISSA 3 Bulk Convert mein):**
- `app/services/image_processing_service.py` (naya) — `process_and_save(contents, image_id)`:
  Pillow se open, EXIF orientation fix, palette→RGBA; **2 LOSSLESS WebP** banata hai —
  Full (max 1200px, upscale nahi) → `static/library/{uuid}.webp`,
  Thumb (max 300px) → `static/library/thumbs/{uuid}.webp` (dono `lossless=True, method=6` — trace/outline crisp)
  Corrupt/na-khulne wali image → `ValueError`
- `app/api/library.py` — single upload (`POST /api/library`) + bulk upload (`POST /api/library/bulk`)
  ab `dest.write_bytes()` ki jagah service call karte hain; row mein `thumb_path` add;
  process fail → single 400, bulk us file ko skip (baaki chalti rahein)
- `app/api/library.py` — DELETE route ab thumb file bhi hataata hai (orphan fix)
- `app/repositories/library_repository.py` — `insert()` mein `thumb_path` column
- `app/core/database.py` — `image_library.thumb_path TEXT` (CREATE TABLE + safe ALTER migration; purani rows NULL)
- `app/schemas/responses.py` — `LibraryImage.thumb_path: Optional[str] = None`
- `static/library.html` — grid `renderCard()` ab `thumb_path || file_path` (purani images full par fall back)

**Verified (server restart + manual smoke test):**
- 1600×1000 PNG → full 1200×750, thumb 300×188, dono `WEBP` ✓
- 500px image upscale nahi hui (500×500 raha) ✓
- delete → full + thumb dono disk se hatt gaye (koi orphan nahi) ✓
- DB migration clean, `thumb_path` column present, `thumbs/` dir auto-create ✓

**Test fixture fix (same branch):** upload route ab image ko genuinely decode karta hai (Pillow),
isliye purane test files ka minimal 1×1 PNG/JPG (jo truncated/broken tha — `load()` par "broken data stream")
fail karne laga. `test_library_api.py` mein `_img_bytes()` helper (Pillow se valid bytes) + baaki 5 library
test files mein PNG ki IDAT line valid bytes se replace. Upload tests ab `.webp` ext, `thumb_path`, aur
thumbnail file existence check karte hain; bulk test `*.webp` count karta hai; delete test thumb removal verify.
- Service refactor: `process_and_save(contents, id, library_dir)` — dir ab param hai (tests `_LIBRARY_DIR`
  monkeypatch karte hain, isliye service ko route se dir milna chahiye, apna hardcoded nahi).

**Tests:** 650 pass, ruff clean. Cloud push NAHI.

**Fix (same branch) — upload size limit 2 MB → 10 MB + pixel guard:**
- **Masla:** 2 MB byte-check upload ke baad par conversion se PEHLE tha. WebP+1200px cap se stored
  size waise hi chhoti hoti hai, lekin bade high-res PNG (4–8 MB) convert hone se pehle hi reject ho jaate the.
- **Faisla (Option A):** 2 MB ko *storage guard* ki jagah *input/decode guard* maana. `_MAX_BYTES` 2 → 10 MB
  (single + bulk dono routes), byte-check ab bhi conversion se pehle (sasta rejection).
- `app/api/library.py` — `_MAX_BYTES = 10 MB`; error messages ("2 MB" → "10 MB") single + bulk.
- `app/services/image_processing_service.py` — **pixel guard** `_MAX_PIXELS = 50 MP`: chhoti file bade
  dimensions (decompression bomb) ko bhaari decode se PEHLE (header ki `img.size` se) reject karta hai.
- `static/library.html` — 2 labels ("max 2 MB" → "max 10 MB") + client-side pre-check `2*1024*1024` → `10*...`.
- `tests/test_library_api.py` — oversized tests (single + bulk) ab `10 MB + 1` use karte hain
  (warna 2 MB payload naye limit ke neeche aa ke corrupt-path test karta, size-path nahi).
- **Verified (manual):** 7.34 MB real PNG → 200 + 1200×1200 WebP ✓; 64 MP pixel-bomb (0.19 MB file) → 400 guard ✓
- pytest + ruff: baad mein (user browser test kar raha hai).

---

## 2026-07-16 — feature/fix-warning-null (in progress)

**Bug:** `adaptive_results_service.py` mein `upload_results()` warning calculation fail hoti thi jab `school_settings` table mein `class_size`/`min_analysis_percent` columns `NULL` hote hain (SQLite `ALTER TABLE ADD COLUMN` existing rows ko NULL rakhta hai). `settings.get("class_size", 25)` ka default sirf missing key par kaam karta hai — NULL value par `None` return hota tha, phir `math.ceil(None × pct / 100)` crash.

**Fix (`adaptive_results_service.py` lines 64–78):**
- `settings.get("class_size") or 25` — `or` None aur 0 dono handle karta hai
- `settings.get("min_analysis_percent") or 60` — same
- Poora warning block `try/except Exception: pass` mein — warning crash hone par upload fail nahi hoga

## 2026-07-16 — feature/remove-dashboard → master (dashboard.html delete)

**Kya kiya:**
- `static/dashboard.html` delete kiya — legacy page tha, Results screen hatayi thi to orphan ho gaya tha;
  Analytics screen (index.html) same kaam karta hai aur zyada features bhi hain
- `static/index.html` — saare references clean kiye:
  - `#dashboardBtn` button Results screen se hata diya
  - `mpDashboard()` aur `openDashboard()` functions delete
  - 3 jagah `dashboardBtn.style.display` lines delete (loadPaper, generateQuestions, buildAdaptivePaper)
  - CSV upload ke baad auto-open dashboard line delete
  - My Papers table mein "Dashboard" button delete
  - `btn.dashboard` i18n keys (EN + UR) delete
- Analytics screen aur Adaptive Analysis untouched

---

## 2026-07-16 — feature/category-dropdown → master (Image Library category dropdown)

**Kya kiya:**
- `static/library.html` — Category field 2 jagah text box se dropdown bana:
  - **Bulk Tag modal**: `bmCategory` input → select (12 options) + hidden `bmCategoryNew` text box
  - **Edit modal**: `editCategory` input → select + hidden `editCategoryNew` text box
- `_buildCategorySelect()` helper: dono selects consistently populate karta hai;
  existing value auto-pre-select; unknown DB value → "Naya likhein" select + text box mein value
- `onBmCategoryChange()` / `onEditCategoryChange()`: "Naya likhein" chunne par text box dikhao
- `saveBulkMeta()` + `saveEdit()`: `__new__` sentinel resolve karke actual category string bhejte hain
- 12 categories (DB se): animal, concept, flower, food, fruit, furniture, number, object, shape, sports, vegetable, vehicle

---

## 2026-07-16 — feature/bloom-suggestions → master (Bloom Taxonomy class-wise suggestions)

**Kya kiya:**
- `app/core/bloom_standards.py` (naya) — 4 class groups (Pre-Primary/Primary/Middle/Matric) with
  Bloom % distributions; `get_bloom_suggestion()` with flexible matching: case-insensitive,
  spaces/dashes normalize, `Grade X` aur `Class X` dono variants support
- `app/api/bloom_suggestions.py` (naya) — `GET /api/bloom-suggestion/{class_name}`;
  match nahi → 404
- `app/main.py` — bloom_suggestions router registered
- `static/blueprint.html` — Grade dropdown ke neeche neela info box (`#bloomSuggestionBox`);
  `onGradeChange()` mein suggestion fetch + display; sirf mashwara, koi auto-fill/enforcement nahi

**Bug fix (same branch):** DB mein grades `Grade 4`/`Grade 6` etc hain, `Class X` nahi —
`bloom_standards.py` mein `Grade X` variants add kiye taake matching kaam kare.

**Distributions:**
- Pre-Primary: Remember 70%, Understand 30%
- Primary: Remember 30%, Understand 35%, Apply 25%, Analyze 10%
- Middle: Remember 20%, Understand 30%, Apply 30%, Analyze 20%
- Matric: Remember 15%, Understand 25%, Apply 30%, Analyze 20%, Evaluate 10%

---

## 2026-07-16 — feature/adaptive-skip-upload → master (Adaptive: skip upload if results exist)

**Kya kiya:**
- `app/api/adaptive_results.py` — naya route `GET /api/adaptive/has-results/{paper_id}`:
  paper nahi → 404; uploads nahi → `{has_results: false, student_count: 0}`;
  upload mila → unique roll_no count → `{has_results: true, student_count: N}`
- `static/index.html` — Step 1 mein `div#adHasResultsBox` add kiya (green info box, default hidden)
- `static/index.html` — `onAdaptivePaperSelect()` async ho gayi: paper select hote hi
  has-results check karta hai; results hain → box dikhao + "Upload Results" button chhupao;
  2 buttons: "Analysis dekho →" (Step 3) aur "Naya Result Upload karo" (Step 2)
- Existing upload/analysis/generate logic unchanged

**Verified:** `GET /api/adaptive/has-results/628ccbea-...` → `{has_results: true, student_count: 25}` ✓

---

## 2026-07-16 — feature/analytics-improve → master (Analytics screen improvements)

**Kya kiya:**
- `static/index.html` — Paper ID text box hata ke dropdown lagaya (GET /api/papers se load hota hai); paper select hote hi auto analytics load; "Analytics dekhen" button backup ke liye rakha
- `static/index.html` — "Kaisa tha?" column add kiya per-question table mein — Roman Urdu difficulty explanation: >80% "Asaan tha — X% ne sahi kiya", 40–80% "Theek tha", <40% "Mushkil tha — sirf X% ne sahi kiya"
- `static/index.html` — Row background color ab Difficulty Index (P-value) se: Green (40–80%), Yellow (80–90% ya 30–40%), Red (>90% ya <30%); D-index column aur Quality badge unchanged
- `static/index.html` — `initAnalyticsScreen()` naya function: showScreen('analytics') hook se call hota hai, `currentPaperId` auto pre-select karta hai
- Legend text update: difficulty range explain karti hai (P-value based)

**Tests:** sirf frontend — koi backend change nahi, pytest pending

---

## 2026-07-15 — feature/language-filter HISSA 2+3 (commit de7b95b)

**Kya kiya:**
- `app/services/blueprint_paper_service.py` — `language_filter` har section se read karke `_fetch_simple` + `_fetch_with_distribution` ko pass. Shortfall notes mein `(English only)`/`(Urdu only)` label.
- `app/services/paper_service.py` — `_pick_questions()` ko `language_filter` param mila; `assemble_balanced_paper` aur `_assemble_by_ratio` `req.language_filter` pass karte hain (adaptive paper mein nahi — `AdaptivePaperRequest` mein field nahi).
- `static/blueprint.html` — FILTERS row mein Language dropdown (Sab / English only / Urdu only); `onLangFilter()` handler; `addSection`/`loadPreset`/`loadBlueprintToUI` mein `language_filter: null` default.
- `static/index.html` — Generate paper form mein Language filter dropdown; `buildPaper()` POST body mein `language_filter: langVal || null`.

**Tests:** 635 pass (pehle wali 3 adaptive failures fix ho gayi — `AdaptivePaperRequest` mein field nahi thi).

---

## 2026-07-15 — feature/language-filter HISSA 1 (commit 6fcc19f)

**Kya kiya:**
- `app/repositories/questions_repository.py` — `_apply_language_filter()` helper; `find_for_blueprint_section`, `find_least_used`, `find_for_bank_paper` mein `language_filter` param.
- `app/schemas/requests.py` — `GeneratePaperRequest` mein `language_filter: Optional[Literal["en","ur"]] = None`.
- `tests/test_language_filter.py` — 11 nayi tests (repository + schema validation).

---

## 2026-07-15 — fix/bad-file-crash → master (Bulk upload crash guard)

**Kya fix kiya:**
- `app/services/bulk_import_service.py` — 0-bytes upfront check; corrupt file pe user-friendly message (raw Python exception expose nahi hota); header-only xlsx pe explicit error; DB insert per-row try/except
- `app/api/questions.py` — `file.file.read()` try/except mein wrap kiya (pehle unguarded 500 tha)
- `tests/test_bulk_import.py` — 5 nayi `TestBadFileCrash` tests: jpg ext, 0 bytes, corrupt message quality, header-only, server survives 3 bad uploads
- `start.bat` — naya launcher: `.env` load, venv check, browser auto-open 2s baad

**Tests:** 624 pass, ruff clean

---

## 2026-07-15 — fix/edit-modal-save → master (print.html answer_lines save bug)

**Root cause:** `saveQuestion()` mein `question_ur`, `correct_answer_en`, `correct_answer_ur` hamesha payload mein jaate the (empty string `""`). `_not_blank` Pydantic validator 422 raise karta tha → answer_lines kabhi DB tak nahi pahunchti thi.

**Kya fix kiya:**
- `static/print.html` — `saveQuestion()`: optional text fields sirf tab payload mein jayen agar non-empty (empty string → omit)
- `static/print.html` — `ef_answer_lines` dropdown options fix: `0, 2, 3, 4, 6, 8` (bank.html se match; pehle `5, 10` the jo invalid hain)
- `tests/test_print_edit_modal.py` — 8 naye tests: valid values, zero, bilingual, empty-string-422, DB persistence

**Tests:** 619 pass, ruff clean

---

## 2026-07-15 — feature/bulk-answer-lines → master (Bulk Excel mein answer_lines column)

**Kya bana:**
- `app/services/bulk_import_service.py` — `answer_lines` column parse karo (valid: `0,2,3,4,6,8`; invalid/blank = NULL + warning)
- `app/repositories/questions_repository.py` — `insert()` mein `answer_lines` column add
- `static/bulk_upload_template.xlsx` — `answer_lines` column (22nd, green/optional) add kiya
- `tests/test_bulk_import.py` — 11 naye tests (valid values, zero, blank, invalid, non-numeric, backward compat, parametrize)

**Tests:** 590 pass, ruff clean

---

## 2026-07-15 — Pre Year 1 questions delete (197 sawal)

- Backup: `paper_maker_backup_pyr1_20260715_104351.db`
- DELETE: 197 Pre Year 1 sawal (syllabus_topics JOIN, grade='Pre Year 1')
- Baad mein Pre Year 1 count = 0 ✓, baaki classes (70 sawal) safe

---

## 2026-07-14 — Image Library — Excel se Meta Import (feature/image-meta-import → master)

**Kya bana:**

- **`app/services/library_meta_import_service.py`** (naya) — Core service:
  - `import_meta_from_excel(file_bytes)`: pandas se Excel parse, har row par `image_name` se DB match
  - Topic resolution: `subject + class` hint ke saath priority — subject+grade > subject-only > global first
  - Partial update: khali cell = us field ko chhua nahi (purana data rahe)
  - Return: `{updated, skipped, results: [{row, image_name, status, reason?, warnings?}]}`

- **`app/api/library.py`** — 2 naye routes:
  - `POST /api/library/excel-meta-import` — Excel upload, service call, JSON summary
  - `GET /api/library/excel-meta-import/template` — template .xlsx download

- **`static/library_meta_import_template.xlsx`** (naya) — 7-column template (image_name zaroori, baaki optional), colored headers, 2 example rows

- **`static/library.html`** — Bulk Upload card ke baad naya card:
  - Template download button, xlsx file input, Import button
  - `importMetaExcel()` JS: POST → results render (row number + status + warnings) → grid reload
  - Same `.bulk-results` CSS — Bulk Upload se consistent UI

**Tests:** 17 naye tests (11 service + 6 API) — 579 total pass, ruff clean

**Excel columns:**
`image_name` (zaroori) | `topic` | `subject` | `class` | `keywords` | `category` | `question_types`

---

## 2026-07-11 — Image System HISSA C — In-form image selection UI (feature/image-system)

**Kya bana (frontend only — koi backend change nahi):**

- **`static/print.html`** — Edit modal mein topic thumbnail strip:
  - Modal khulte hi `loadTopicStrip(topicId, qid)` call hoti hai
  - `/api/library?syllabus_topic_id=...` se images fetch, strip mein dikhayi
  - Thumbnail click → `applyLibraryImageInModal()` → image-from-library API → modal ka preview update
  - Topic na ho ya images na hon → strip hidden (no clutter)
  - "Choose Image" file upload button barabar maujood hai (dono options)

- **`static/bank.html`** — Add form + Edit modal mein thumbnail grid:
  - Add form: topic select `onchange="onAddTopicChange()"` → library images strip
  - Thumbnail click → highlight (selected), dobara click → deselect
  - Question save hone ke baad agar image select thi → image-from-library API call
  - Edit modal: `openEditModal()` mein `_loadEditStrip(topicId, qid)` call
  - Edit thumbnail click → seedha attach + list refresh + modal close

**Test run:** 482 passed (no backend change) — ruff clean

**Browser test checklist (khud check karo):**
1. print.html: paper mein ✏️ button → modal khule → agar topic hai to library strip dikhe
2. Strip mein thumbnail click → modal preview update ho, file upload button abhi bhi kaam kare
3. Topic nahi ya library mein images nahi → strip bilkul nahi dikhi
4. bank.html: nayi question form → subject → class → topic chunein → library strip dikhe
5. Thumbnail click → highlighted ho (blue border), dobara click → deselect
6. "Save" karo → question save + image attach ho (list mein image_path set ho)
7. Edit button → modal khule → strip dikhe → click karo → modal band, list refresh ho
8. Purani "Choose Image" file upload dono jagah abhi bhi kaam kare (backward compat)

---

## 2026-07-11 — Image System HISSA B — Excel image column (feature/image-system)

**Kya bana:**

- **`app/services/bulk_import_service.py`** — `image` column support:
  - `_find_library_image(name, topic_id)` helper: topic-scoped match pehle (`find_by_name_and_topic`), phir global (`find_by_name`), narm (case-insensitive, trim)
  - `_validate_row()` — `_image_name` internal field pass-through
  - `import_from_bytes()` — post-insert: library se file `static/uploads/` mein copy, `image_path` set; naam na mile → warning (skip nahi)
  - `image` column absent (purani files) → `""` → koi action nahi (backward compat)
- **`static/bulk_upload_template.xlsx`** — `image` column (13th) add kiya
- **`tests/test_bulk_import_image.py`** — 7 nayi tests

**Test run:** 482 passed, 0 failed — ruff clean

**Browser test (khud check karo):**
1. Purana template (.xlsx bina image column) import karo → bilkul theek chale
2. Naye template mein image naam likho (library mein pehle upload karo) → question mein image dikhe
3. Galat naam likhain → question import ho, warning mein naam aaye
4. Case mismatch test: "OrangeS5" library mein, "oranges5" Excel mein → match ho

---

## 2026-07-11 — Image System HISSA A — Bulk Image Upload (feature/image-system)

**Kya bana:**

- **`app/core/database.py`** — `image_library` table mein `name_normalized TEXT` column add kiya (CREATE TABLE + safe ALTER TABLE migration existing DBs ke liye + back-fill UPDATE)
- **`app/repositories/library_repository.py`** — `insert()` updated: `name_normalized = name.strip().lower()` field include hoti hai. Teen nayi helpers: `name_exists(name)` (duplicate check), `find_by_name(name)`, `find_by_name_and_topic(name, topic_id)` (HISSA B ke liye)
- **`app/api/library.py`** — `POST /api/library/bulk` nayi route: `List[UploadFile]`, per-file MIME + size + duplicate check, skip karo invalid/duplicate, result list wapas karo
- **`static/library.html`** — "Ek saath kai images upload" card: multi-file input, subject/grade/topic cascade (alag single-upload se), per-file result list (ok/skip/err styled), library grid auto-refresh on success
- **`tests/test_library_api.py`** — 8 nayi bulk tests: all_added, duplicate_skip, wrong_mime_skip, oversized_skip, name_normalized_stored, topic_tagged, per_file_result_list, case_insensitive_duplicate

**Test run:** 475 passed, 0 failed — ruff clean

**Browser test (khud check karo):**
1. Library page → "Ek saath kai images" card dikhe
2. Subject → Grade → Topic cascade kaam kare
3. Multiple PNG/JPG files select → Upload → result list (ok/skip) dikhe
4. Duplicate naam dobara upload karo → skip + reason dikhe
5. GIF file try karo → skip (JPG/PNG only)
6. Grid refresh ho nayi images ke saath

---

## 2026-07-11 — Blueprint HISSA 4 — blueprint.html frontend (feature/blueprint)

**Kya bana:**

- **`static/blueprint.html`** — nayi file, poora Blueprint Builder UI:
  - Paper metadata: blueprint name, subject+grade cascade, paper title, class name
  - Preset loader: `/api/blueprint-presets` se presets — "Load sections" button
  - Dynamic section cards: heading, topic multi-select (syllabus se checkboxes), question types (MCQ/Fill/T-F/Short), count, marks_each, source filter
  - Live total marks bar (count × marks_each, real-time update)
  - "Save Blueprint" → `POST /api/blueprints` — DB mein save
  - "Paper Banao" → `POST /api/blueprint-paper` → `print.html?paper_id=...` mein redirect
  - Shortfall warnings: agar section mein maange zyada mile kam — yellow list dikhti hai
  - Saved Blueprints list: Load / Paper Banao / Delete per blueprint
- **Sidebars updated** — Blueprint link add kiya: `bank.html`, `library.html`, `print.html`, `index.html`
- **Branch:** feature/blueprint (commit a16a9fc)

**Test checklist (browser mein khud check karo):**
1. `/blueprint.html` open ho — sidebar aur page dono sahi dikhein
2. Subject → Grade change kare → topics load hon section cards mein
3. Preset load kare → sections replace hon
4. Section add/remove karo — marks bar update ho
5. Save Blueprint → success message aur list mein nayi entry dikhe
6. Paper Banao → print.html khole, paper render ho
7. Shortfall warning: aisa subject/topics chunein jahan kam questions hain
8. Saved list mein "Load" → form mein load ho; "Paper Banao" → direct paper
9. "Delete" → blueprint list se hata de

---

## 2026-07-11 — Blueprint HISSA 3 — print.html blueprint rendering (feature/blueprint)

**Kya bana:**

- **`app/schemas/responses.py`** — `Paper` model mein `sections_meta: Optional[str] = None` add kiya
  - Pehle FastAPI response_model strip kar deta tha — ab `GET /api/paper/{id}` mein sections_meta aata hai
- **`static/print.html` (HTML)** — `sectionA` + `sectionB` divs hata ke `sectionsContainer` bana
- **`static/print.html` (CSS)** — `.shortfall-note` style add kiya (yellow warning box, screen only)
- **`static/print.html` (JS)** — `loadPaper()` mein sections_meta branch:
  - `sections_meta` non-null → blueprint rendering: qMap build, har section ka `section-block` dynamically inject
  - `sections_meta` null → `_renderLegacySections()` call (A/B objective/subjective — bilkul unchanged)
  - Shortfall notes `.no-print .shortfall-note` — screen par dikhein, print mein nahi
  - `_renderLegacySections()` new helper: container mein sectionA/sectionB divs create karke purana `renderSection()` call karta hai
- **Tests:** 58 blueprint tests pass, ruff clean
- **Branch:** feature/blueprint (commit 3a76257) — merge pending

---

## 2026-07-11 — feature/bulk-import merged to master (HISSA 4 — Bulk Upload)

**Kya bana:**

- **Backend — `app/services/bulk_import_service.py`**
  - pandas se `.xlsx`/`.csv` parse (openpyxl engine)
  - Per-row validation: type check (mcq/fill/tf/short), blank question, MCQ options, correct letter/tf value
  - Topic matching: case-insensitive + strip → subject+grade → subject-only → global; match na mile to `topic_id=NULL` + fuzzy suggestion (difflib)
  - `source='manual'` insert — HISSA 1 ki `questions_repository.insert()` reuse
  - Return: `{added, skipped, errors: ["row N: wajah"], warnings: ["row N: note"]}`
  - Marks: blank/zero/invalid → silent default 1
  - `is_urdu=yes` → `question_ur` mein, warna `question_en`

- **API — `app/api/questions.py`**
  - `POST /api/questions/bulk-import` route (.xlsx/.xls/.csv accept, ext check at route level)

- **Frontend — `static/bank.html`**
  - "Bulk Upload — Excel se questions import karo" card (bank-paper card ke baad)
  - Drag-and-drop zone + file chooser (.xlsx/.csv, max 5 MB client-side check)
  - Upload button (disabled jab tak file na chune), Clear button
  - Result box: green (sab add), orange (kuch skip), red (sab skip) — har skip row ka number + wajah, warnings alag list
  - Question list auto-refresh after successful import
  - "Template download karo" button → `/bulk_upload_template.xlsx`

- **Template — `static/bulk_upload_template.xlsx`**
  - 4 sample rows (mcq/tf/fill/short), green styling
  - `Instructions` sheet mein puri guide

- **Tests — `tests/test_bulk_import.py`** — 39 tests
  - Happy path (xlsx + csv, sab 4 types), DB mein actually insert check
  - MCQ correct letter → option text resolve
  - is_urdu, marks defaults (blank/zero/string)
  - Per-row validation errors (blank question, invalid type, MCQ options, wrong correct)
  - Mixed valid+invalid — ek buri row se baaki nahi rukein
  - Topic matching (unknown → warning + import, blank → no warning)
  - File format errors (PDF reject, corrupt xlsx, missing column, empty file)

- **Merge:** `feature/bulk-import → master`, clean (koi conflict nahi)
- **Total: 409 tests pass, ruff clean**

## 2026-07-11 — feature/question-bank merged to master (HISSA 1–3 + bank.html)

**Kya bana:**

- **HISSA 1 — Manual Question CRUD** (`source=manual`)
  - `app/core/database.py` — `source TEXT DEFAULT 'gemini'` column migration; existing rows safe
  - `app/repositories/questions_repository.py` — `insert()` mein `source` field; `list_by_filters()` mein `source` filter support
  - `app/schemas/requests.py` — `CreateManualQuestionRequest` + `UpdateQuestionRequest` mein `source` field
  - `app/api/questions.py` — `POST /api/questions/manual` route (manual question create, no Gemini)
  - `tests/test_bank.py` — 231 tests (CRUD, source filter, edge cases)

- **HISSA 2 — bank.html (Manage Page)**
  - `static/bank.html` — nayi page: question list (filter: subject/class/topic/source), add/edit/delete modal, inline form validation
  - `static/index.html` — "Question Bank" nav link added (sidebar)
  - `static/library.html` — "Question Bank" nav link added (sidebar)

- **HISSA 3 — bank-paper route (bina Gemini API)**
  - `app/services/question_service.py` — `get_questions_for_bank_paper()` — DB se manual questions fetch, subject/source filter
  - `app/services/paper_service.py` — `create_bank_paper()` — paper object banao from bank questions (no API call)
  - `app/api/papers.py` — `POST /api/bank-paper` route registered
  - `tests/test_hissa3.py` — 284 tests (bank-paper route, source filter, question types)

- **bank.html UI — "Bank se Paper Banao" section**
  - `static/bank.html` — subject/class/topic select + "Paper Banao" button → `/api/bank-paper` call → `print.html` redirect

- **Ruff fix:** `tests/test_hissa3.py` — 2 unused variables (`g_id`, `qid`) removed (F841)

- **Total: 370 tests pass, ruff clean**

## 2026-07-10 — feature/image-library Hissa 4 (Auto-Suggest)

- `app/repositories/library_repository.py` — `topic_image_counts(ids)` added (returns {topic_id: count})
- `app/api/library.py` — `topics-with-images` response changed: `{"topics": {"id": count}}` (breaking change, test updated)
- `app/schemas/requests.py` — `CopyFromLibraryRequest` added (image_id + image_size validator)
- `app/api/questions.py` — `_LIBRARY_DIR` constant + `POST /api/questions/{id}/image-from-library` route (copy file from library to uploads, update DB)
- `static/print.html` — auto-suggest badges (📚 N image(s) — Dekho/Nahi), library picker modal (grid thumbnails, size selector), localStorage dismiss per paper, batch API call on paper load
- `tests/test_library_api.py` — topics-with-images tests updated for new shape + `test_topics_with_images_returns_counts` added
- `tests/test_copy_from_library.py` — 7 nayi tests (PNG/JPG copy, default size, replace old upload, 404s)
- **Total: 335 tests pass, ruff clean**

## 2026-07-10 — feature/image-library Hissa 2 (Library Manager page)

- `static/library.html` — nayi page: upload form (cascade Subject→Class→Topic dropdown), client-side file pre-check (type + size), image grid (filter: subject/grade/naam), delete with confirm
- `static/index.html` — "Image Library" nav link added (sidebar)
- `static/print.html` — "Image Library" nav link added (sidebar)
- **Total: 327 tests pass, ruff clean**

## 2026-07-10 — feature/image-library Hissa 1 (DB + API + backup)

- `app/core/database.py` — `image_library` table added in `init_db()`
- `static/library/` — folder created, gitignored
- `app/repositories/library_repository.py` — insert, find_by_id, list_by_filters, delete, topic_ids_with_images
- `app/schemas/responses.py` — `LibraryImage` model added
- `app/api/library.py` — POST /api/library, GET /api/library (filters), DELETE /api/library/{id}, GET /api/library/topics-with-images
- `app/main.py` — library router imported and included
- `backup.bat` — [3/3]→[4/4], library-backups step added
- `tests/test_library_api.py` — 12 nayi tests (upload PNG/JPG, wrong MIME 400, oversized 400, blank name 400, list+filter, delete, topics-with-images)
- **Total: 327 tests pass, ruff clean**

## 2026-07-10 — feature/image-size (Hissa 3)

- `app/core/database.py` — `image_size TEXT` nullable migration
- `app/schemas/responses.py` — `image_size: Optional[str]` in `Question`
- `app/schemas/requests.py` — `image_size` in `UpdateQuestionRequest` + validator (small/medium/large only)
- `app/repositories/questions_repository.py` — `image_size` in `insert()`
- `static/print.html` — CSS size classes (img-sm/md/lg), modal dropdown (sirf image wale questions par), renderQuestion() size class
- `tests/test_image_size.py` — 9 nayi tests (valid sizes, invalid reject 422, null field)
- **Total: 315 tests pass, ruff clean**

## 2026-07-10 — feature/question-image Hissa 1 (Backend)

**Kya kiya:**
- `app/core/database.py` — `questions` table mein `image_path TEXT` column migration added (nullable, existing rows safe)
- `app/repositories/questions_repository.py` — `insert()` mein `image_path` column add; `update()` already generic fields le leta hai
- `app/schemas/responses.py` — `Question` model mein `image_path: Optional[str] = None` add
- `app/api/questions.py` — 2 nayi routes:
  - `POST /api/questions/{id}/image` — JPG/PNG upload, max 2MB, content-type se ext decide, purani image (kisi bhi ext) pehle delete
  - `DELETE /api/questions/{id}/image` — DB NULL + file delete
- `static/uploads/` folder create (images yahan store hongi)
- `.gitignore` — `static/uploads/` add (GitHub par na jaaye)

**Tests (Hissa 1b):** `tests/test_question_image_api.py` — 9 nayi tests:
- PNG/JPG successful upload (200, file on disk, DB path set)
- Oversized (>2MB) → 400, koi file nahi likhi
- Wrong MIME (text/plain, image/gif, application/pdf) → 400
- Unknown question_id → 404
- Delete: file disk se hata, DB NULL
- Replace PNG→JPG: purana .png orphan nahi raha
- **Bug fix:** DELETE route mein `_UPLOADS_DIR / Path(...).name` use kiya (pehle `.parent` galat path de raha tha)
- **Total:** 306 tests pass, ruff clean.

**Hissa 2 (Frontend) — 2026-07-10:**
- `static/print.html` — edit modal mein image section add (file input, thumbnail preview, remove button, warning)
- `renderQuestion()` mein `imageHtml` — `max-height: 180px` screen, `160px` print
- `onImageFileChange()` — client-side pre-check (type + size), instant local preview, auto-upload
- `uploadQuestionImage()` — FormData POST, server response se `_paperQuestions` + re-render
- `deleteQuestionImage()` — DELETE, in-memory update + re-render, UI reset
- `printWithImagesLoaded()` — `Promise.all(imgs.map(img => img.decode()))` phir `window.print()`
- Print button ab `printWithImagesLoaded()` call karta hai
