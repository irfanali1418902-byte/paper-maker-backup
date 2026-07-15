# PaperMaker — Fix / Feature Log

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
