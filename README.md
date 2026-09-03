# AII Smart Paper Maker

An AI-powered exam paper generator built for a school in Swat, Pakistan. It
generates **bilingual (English + Urdu), Bloom-tagged** questions with AI, stores
them in a local SQLite question bank, assembles balanced exam papers, analyzes
student results with psychometric item analysis (P-value / D-index), and can
build **adaptive papers** that target a class's weakest Bloom levels.

Everything runs from a single Python process and one SQLite file — no external
database server, no cloud dependency beyond the AI provider.

---

## Features

- **AI question generation** — produces questions in both English and proper
  Urdu script, each tagged with a Bloom's Taxonomy level
  (`REMEMBER … CREATE`) and calibrated to a requested difficulty (easy /
  medium / hard). Supports multiple-choice (with 4 bilingual options) and other
  question types, plus optional emoji "visuals" for young-learner counting
  questions.
- **Question bank** — every generated question is saved to SQLite and can be
  browsed and filtered by subject, topic, and Bloom level.
- **Balanced paper assembly** — builds a paper from the bank according to a
  Bloom + difficulty distribution, prioritizing least-used questions to reduce
  repetition, and reports an expected-difficulty balance summary.
- **Manual question replacement** — swap any question in an assembled paper for
  another from the bank; total marks and balance are recomputed.
- **Result analyzer dashboard** — teachers download a CSV template, fill in
  marks offline, upload it back, and get per-student rankings (competition
  style, ties share a rank), pass/fail against the 33% KPK board threshold, and
  per-question / per-Bloom breakdowns.
- **Item analysis (psychometrics)** — Difficulty Index (P-value) and
  Discrimination Index (D) per question, with automatic bad-question flags
  (too easy, too hard, negative discrimination / likely mis-keyed). D is marked
  unreliable for classes under 10 students.
- **Adaptive paper generation** — reads a source paper's latest results,
  derives the class's weak Bloom levels, and weights a new paper toward them.
- **Syllabus import** — upload a text-based PDF, or a ZIP of PDFs and page
  images (JPG/PNG), and the AI extracts structured units/topics (using vision
  for images) so teachers can select topics from a dropdown instead of typing.
- **Printing** — papers are printed **from the browser** (`static/print.html`,
  Ctrl+P), with print-specific CSS, per-class print settings, and an optional
  school letterhead (name, address, logo, accent color). Urdu renders in
  Nastaliq using the font installed on the machine.
  *(There is no Word/PDF export. It existed once and was deleted in `e2bdcc4`,
  2026-08-13 — 621 lines nothing called, plus a LibreOffice subprocess
  dependency.)*

---

## Tech stack

| Layer        | Choice                                                        |
|--------------|---------------------------------------------------------------|
| Language     | Python 3.12 (3.10+ supported)                                 |
| Web framework| FastAPI + Uvicorn (ASGI)                                       |
| Data models  | Pydantic v2                                                   |
| Database     | SQLite (single `paper_maker.db` file)                         |
| AI providers | Google Gemini (`gemini-2.5-flash`) or Anthropic Claude (`claude-sonnet-4-6`) |
| HTTP client  | `requests` (to the AI providers)                              |
| PDF parsing  | PyMuPDF (text + page-image extraction for syllabus import)    |
| Spreadsheets | pandas + openpyxl (results template / upload)                 |
| Printing     | Browser print (`static/print.html` + print CSS) — **no Word/PDF export**, deleted in `e2bdcc4` |
| Frontend     | Static HTML/JS (`static/`) served by FastAPI                  |
| Urdu font    | Jameel Noori Nastaleeq (installed on the machine that prints)  |
| Tooling      | ruff (lint), black (format), pytest (tests), pre-commit       |
| Deployment   | **None — runs locally.** Cloud plan closed 2026-08-31 (O1); see below |

The codebase follows a strict layered architecture (routes → services →
repositories → database). See [`ARCHITECTURE.md`](ARCHITECTURE.md) for the full
contract and [`CLAUDE.md`](CLAUDE.md) for coding conventions.

---

## Local setup

### 1. Prerequisites

- Python 3.10 or newer (3.12 is the pinned version in `.python-version`).
- Git.

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

Using a virtual environment is recommended:

```bash
python -m venv .venv
# Windows (PowerShell):
.venv\Scripts\Activate.ps1
# macOS / Linux:
source .venv/bin/activate

pip install -r requirements.txt
```

### 3. Configure environment variables

Copy `.env.example` to `.env` and add at least one AI provider key:

```bash
cp .env.example .env
```

Then edit `.env`. The minimum needed to run is one key:

```
GEMINI_API_KEY=your-gemini-api-key-here
```

`python-dotenv` loads `.env` automatically at startup — you don't need to
export anything manually. See [Environment variables](#environment-variables)
for the full list.

### 4. Run the server

```bash
uvicorn app.main:app --reload --port 8000
```

The SQLite database (`paper_maker.db`) is created automatically on first start,
and the schema is migrated in-place on every start. Delete the file to start
fresh.

### 5. Open the app

- Paper maker + adaptive UI: <http://localhost:8000>
- Result analyzer dashboard: <http://localhost:8000/dashboard.html>
- Interactive API docs (Swagger): <http://localhost:8000/docs>

---

## Environment variables

All are optional individually, but **at least one AI key is required** for
generation to work. Full descriptions and placeholders are in `.env.example`.

| Variable            | Required?                         | Purpose                                                                 |
|---------------------|-----------------------------------|-------------------------------------------------------------------------|
| `GEMINI_API_KEY`    | One of Gemini/Anthropic           | Google Gemini key (free tier). Used when Anthropic key is absent.       |
| `ANTHROPIC_API_KEY` | One of Gemini/Anthropic           | Anthropic Claude key (paid). **Takes priority** over Gemini if set.     |
| `DB_PATH`           | No (defaults to `paper_maker.db`) | Absolute/relative path to the SQLite file (point at a volume in prod).  |
| `PORT`              | No                                | Unused — nothing in `app/` reads it. It existed for the deploy start command; that was closed 2026-08-31 (O1). |

Never commit `.env`. `.gitignore` already ignores `.env` and `.env.*`.

---

## How to use

1. Enter a **Subject** and **Topic** (e.g. Mathematics / Fractions), or pick a
   topic from the syllabus dropdown if you imported one.
2. Click **Generate questions (AI)** — the AI returns bilingual, Bloom-tagged
   questions and saves them to the bank.
3. Click **Build paper from bank** — a balanced paper is assembled (each
   question shows its expected difficulty, plus a paper-level balance summary).
   You can manually replace individual questions from the bank.
4. **Print** the paper from the browser (`print.html` → Ctrl+P).
5. Download the **results CSV template**, fill in each student's marks per
   question, and upload it on the dashboard (`/dashboard.html`) to see
   rankings, P-value, D-index, and bad-question flags.
6. Click **Generate adaptive paper** to build a new paper focused on the Bloom
   levels the class scored weakest on in an uploaded result set.

**Syllabus upload (optional):** in the "Syllabus upload" panel, upload a
text-based PDF or a ZIP (multiple PDFs + JPG/PNG images). The AI extracts
units/topics (reading images via vision) and saves them; they then appear in
the topic dropdown.

### Reproducible test data

To exercise the D-index flags you need at least 10 students. Seed an engineered
result set for an existing paper:

```bash
python -m scripts.seed_large_class <paper_id>
```

### Printing

There is **no Word or PDF export, and LibreOffice is not needed.** That feature
was deleted on 2026-08-13 (`e2bdcc4`) — 621 lines that nothing called, plus a
LibreOffice subprocess dependency. This section used to be a four-step install
guide for it; it was **18 days out of date** before anyone measured it.

The teacher prints from the browser: open a paper in `print.html` and press
Ctrl+P (or the page's Print button, which waits for images to decode first).
`static/css/99-legacy/print.css` and `pages/print.css` carry the print rules —
`@page` margins, the `.no-print` chrome, and per-class print settings the
teacher can adjust on the page.

For Urdu to print in Nastaliq, **Jameel Noori Nastaleeq** must be installed on
the machine doing the printing; otherwise the browser substitutes a fallback
font.

---

## Running tests

```bash
python -m pytest tests/ -v
```

or, matching CI:

```bash
pytest -q
```

Tests run against an isolated temporary SQLite database and mock the AI
provider, so **no API keys or network access are required**. The suite covers
services, repositories, and the HTTP routes.

Lint and format checks (also enforced in CI and via pre-commit):

```bash
ruff check .
black --check .
```

To install the git pre-commit hooks locally:

```bash
pre-commit install
```

---

## Deployment

> **⛔ There is no deployment. Closed 2026-08-31 (ROADMAP §B, O1).**
>
> The app **runs locally** on the teacher's machine. The repo has exactly one git
> remote — `backup` — and it is a backup, not a host: no auto-deploy, no hosting
> remote, no prod environment. The Railway → Northflank migration plan
> (`docs/MIGRATION.md`) is closed and marked as history. The next direction is a
> **school PC / Docker package**, not cloud.
>
> `railway.toml` was **deleted on 2026-08-31** along with this decision — it was
> config for a platform nothing points at.
>
> The Word/PDF-export claims this file used to carry are gone too — measured and
> corrected 2026-08-31, in eight places. See **Printing** below.

### How it actually runs

Locally, on the teacher's Windows machine:

```
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

`start.bat` / `start-local.bat` / `start-school.bat` wrap this.

**If it ever needs to run somewhere else**, only three things are
environment-specific — nothing here assumes a particular host:

- **AI key** — `GEMINI_API_KEY` (or `ANTHROPIC_API_KEY`).
- **`DB_PATH`** — must point at storage that survives a restart. There is exactly
  one database and it holds the teacher's real data.
- **`PAPER_MAKER_API_KEY`** — unset means the `/api` routes are **unprotected**,
  which is fine on localhost and is not fine anywhere else. The app warns about
  this on startup.

A `Dockerfile` is in the repo for the school-PC / Docker packaging work, which is
the direction that replaced cloud.

### CI

`.github/workflows/ci.yml` runs on every push to `master` and every pull
request: `ruff check` → `black --check` → `pytest -q`. No secrets are needed
because the AI provider is mocked and tests use a temporary SQLite DB.

---

## Project status

| Phase | Scope | Status |
|-------|-------|--------|
| Phase 1   | Core engine — AI generation, Bloom tagging, question bank, balanced paper assembly, frontend | ✅ Complete |
| Phase 2   | Result analyzer dashboard, rankings, ~~Word + PDF export~~ (export shipped, then deleted 2026-08-13 — `e2bdcc4`) | ✅ Complete |
| Phase 2.5 | Item analysis — P-value, D-index, bad-question flags | ✅ Complete |
| Phase 3   | Adaptive paper generation from class weaknesses | ✅ Complete |

Planned / not yet built: per-student adaptive papers (currently whole-class),
topic-level weakness targeting (currently Bloom-level), auto-generating
questions when the bank is empty for a weak level, and OCR for scanned
image-only PDFs (image-based syllabus pages are handled via the ZIP + vision
path).

See `PROJECT.md` for the detailed phase log and `ARCHITECTURE.md` for the system
design.
