# PaperMaker — Fix / Feature Log

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
