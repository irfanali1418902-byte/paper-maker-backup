# PaperMaker — Fix / Feature Log

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
