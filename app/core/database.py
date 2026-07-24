"""
SQLite database layer. Zero setup, zero cost — koi server install nahi karna,
ek file (paper_maker.db) hi poori database hai. Jab scale badhe to isi schema
ko Supabase/PostgreSQL par seedha migrate kiya ja sakta hai.
"""

import os
import sqlite3
from pathlib import Path

# app/core/database.py se project root tak teen levels upar.
_DEFAULT_DB_PATH = Path(__file__).parent.parent.parent / "paper_maker.db"
# DB_PATH env override — production (Railway) par persistent volume path
# (e.g. /data/paper_maker.db) point karne ke liye. Set na ho to project root
# wali file (local dev). Ephemeral container FS par volume zaroori hai, warna
# har redeploy par saara data ud jata hai.
DB_PATH = Path(os.environ.get("DB_PATH") or _DEFAULT_DB_PATH)


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    # Custom DB_PATH (e.g. mounted volume) ka parent dir ensure karo taake
    # pehli boot par sqlite connect fail na ho.
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS questions (
            id TEXT PRIMARY KEY,
            subject TEXT NOT NULL,
            topic TEXT NOT NULL,
            bloom_level TEXT NOT NULL,
            difficulty TEXT NOT NULL,
            question_type TEXT NOT NULL,
            marks INTEGER NOT NULL,
            question_en TEXT,
            question_ur TEXT,
            options_en TEXT,
            options_ur TEXT,
            correct_answer_en TEXT,
            correct_answer_ur TEXT,
            explanation_en TEXT,
            explanation_ur TEXT,
            visual_emoji TEXT,
            visual_count INTEGER,
            usage_count INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            syllabus_topic_id TEXT REFERENCES syllabus_topics(id)
        )
        """)

    # Older DB files (created before the visual_* columns were added) need
    # to be migrated in-place — CREATE TABLE IF NOT EXISTS won't add columns
    # to an existing table.
    existing_cols = {row[1] for row in cur.execute("PRAGMA table_info(questions)").fetchall()}
    if "visual_emoji" not in existing_cols:
        cur.execute("ALTER TABLE questions ADD COLUMN visual_emoji TEXT")
    if "visual_count" not in existing_cols:
        cur.execute("ALTER TABLE questions ADD COLUMN visual_count INTEGER")
    if "syllabus_topic_id" not in existing_cols:
        cur.execute("ALTER TABLE questions ADD COLUMN syllabus_topic_id TEXT REFERENCES syllabus_topics(id)")
    if "answer_lines" not in existing_cols:
        cur.execute("ALTER TABLE questions ADD COLUMN answer_lines INTEGER")
    if "image_path" not in existing_cols:
        cur.execute("ALTER TABLE questions ADD COLUMN image_path TEXT")
    if "image_size" not in existing_cols:
        cur.execute("ALTER TABLE questions ADD COLUMN image_size TEXT")
    if "source" not in existing_cols:
        cur.execute("ALTER TABLE questions ADD COLUMN source TEXT DEFAULT 'gemini'")
    # Smart Question Bank columns (HISSA A).
    if "learning_outcome" not in existing_cols:
        cur.execute("ALTER TABLE questions ADD COLUMN learning_outcome TEXT")
    if "estimated_time" not in existing_cols:
        cur.execute("ALTER TABLE questions ADD COLUMN estimated_time INTEGER")
    if "keywords" not in existing_cols:
        cur.execute("ALTER TABLE questions ADD COLUMN keywords TEXT")
    if "source_book" not in existing_cols:
        cur.execute("ALTER TABLE questions ADD COLUMN source_book TEXT")
    if "page_number" not in existing_cols:
        cur.execute("ALTER TABLE questions ADD COLUMN page_number INTEGER")
    if "status" not in existing_cols:
        cur.execute("ALTER TABLE questions ADD COLUMN status TEXT DEFAULT 'published'")
        cur.execute("UPDATE questions SET status = 'published' WHERE status IS NULL")

    cur.execute("""
        CREATE TABLE IF NOT EXISTS papers (
            id TEXT PRIMARY KEY,
            subject TEXT NOT NULL,
            class_name TEXT,
            total_marks INTEGER NOT NULL,
            question_ids TEXT NOT NULL,
            paper_title TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """)

    # Existing DBs (created before paper_title was added) need in-place migration.
    papers_cols = {row[1] for row in cur.execute("PRAGMA table_info(papers)").fetchall()}
    if "paper_title" not in papers_cols:
        cur.execute("ALTER TABLE papers ADD COLUMN paper_title TEXT")
    if "sections_meta" not in papers_cols:
        cur.execute("ALTER TABLE papers ADD COLUMN sections_meta TEXT")
    # exam_no: paper ko kis exam se tag kiya (0 = Unassigned). Coverage feature
    # isse cross-exam SLO coverage nikalti hai. Live DB mein column pehle se
    # maujood ho sakta hai — papers_cols check idempotent hai, dobara add nahi hoga.
    if "exam_no" not in papers_cols:
        cur.execute("ALTER TABLE papers ADD COLUMN exam_no INTEGER")

    cur.execute("""
        CREATE TABLE IF NOT EXISTS blueprints (
            id          TEXT PRIMARY KEY,
            name        TEXT NOT NULL,
            subject     TEXT,
            grade       TEXT,
            sections    TEXT NOT NULL,
            created_at  TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS syllabus_topics (
            id TEXT PRIMARY KEY,
            subject TEXT NOT NULL,
            grade TEXT,
            unit_no INTEGER NOT NULL,
            unit_title TEXT NOT NULL,
            page_range TEXT,
            subtopic_title TEXT NOT NULL,
            activity_type TEXT NOT NULL,
            page_no INTEGER,
            learning_outcome TEXT,
            unit TEXT,
            UNIQUE(subject, grade, unit_no, subtopic_title, page_no)
        )
        """)

    # Existing DBs: add unit column (nullable, no default — NULL means unassigned).
    syllabus_cols = {row[1] for row in cur.execute("PRAGMA table_info(syllabus_topics)").fetchall()}
    if "unit" not in syllabus_cols:
        cur.execute("ALTER TABLE syllabus_topics ADD COLUMN unit TEXT")

    cur.execute("""
        CREATE TABLE IF NOT EXISTS school_settings (
            id INTEGER PRIMARY KEY,
            school_name TEXT,
            school_name_ur TEXT,
            address TEXT,
            address_ur TEXT,
            logo_base64 TEXT,
            accent_color TEXT
        )
        """)

    # Per-call AI provider usage log. Har successful Gemini/Claude API call
    # ek row likhti hai — yehi future per-school billing ka base banega.
    # IF NOT EXISTS itself is idempotent: fresh installs banayenge, existing
    # DBs untouched chhod denge.
    cur.execute("""
        CREATE TABLE IF NOT EXISTS usage_log (
            id TEXT PRIMARY KEY,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
            provider TEXT NOT NULL,
            model TEXT NOT NULL,
            status TEXT NOT NULL,
            input_tokens INTEGER,
            output_tokens INTEGER,
            total_tokens INTEGER
        )
        """)

    # Phase 2 — student performance analyzer. Teacher ek paper ka results
    # sheet (CSV ya similar) upload karte hain; har upload ek row, aur uske
    # andar har student-question pair ki marks_obtained ek alag row.
    # FK declarations documentation ke liye hain — SQLite enforcement default
    # off hai (no PRAGMA foreign_keys = ON), to existing inserts ki behavior
    # nahi badalti.
    cur.execute("""
        CREATE TABLE IF NOT EXISTS result_uploads (
            id TEXT PRIMARY KEY,
            paper_id TEXT NOT NULL REFERENCES papers(id),
            filename TEXT NOT NULL,
            uploaded_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS student_question_results (
            id TEXT PRIMARY KEY,
            result_upload_id TEXT NOT NULL REFERENCES result_uploads(id),
            roll_no TEXT NOT NULL,
            student_name TEXT,
            question_id TEXT NOT NULL REFERENCES questions(id),
            marks_obtained INTEGER NOT NULL
        )
        """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS image_library (
            id                TEXT PRIMARY KEY,
            file_path         TEXT NOT NULL,
            thumb_path        TEXT,
            compression       TEXT,
            name              TEXT NOT NULL,
            name_normalized   TEXT,
            subject           TEXT,
            grade             TEXT,
            syllabus_topic_id TEXT REFERENCES syllabus_topics(id),
            uploaded_by       TEXT,
            created_at        TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """)

    # school_settings: adaptive class config columns.
    settings_cols = {row[1] for row in cur.execute("PRAGMA table_info(school_settings)").fetchall()}
    if "class_size" not in settings_cols:
        cur.execute("ALTER TABLE school_settings ADD COLUMN class_size INTEGER DEFAULT 25")
    if "min_analysis_percent" not in settings_cols:
        cur.execute("ALTER TABLE school_settings ADD COLUMN min_analysis_percent INTEGER DEFAULT 60")
    if "weak_topic_threshold" not in settings_cols:
        cur.execute("ALTER TABLE school_settings ADD COLUMN weak_topic_threshold INTEGER DEFAULT 60")
    # Marhala 4A — global print defaults (per-class na ho to yehi). Default 14 =
    # print.html ke maujooda hardcoded values, isliye purana output bilkul na badle.
    if "print_font_size" not in settings_cols:
        cur.execute("ALTER TABLE school_settings ADD COLUMN print_font_size INTEGER DEFAULT 14")
    if "print_q_gap" not in settings_cols:
        cur.execute("ALTER TABLE school_settings ADD COLUMN print_q_gap INTEGER DEFAULT 14")
    if "print_page_margin" not in settings_cols:
        cur.execute("ALTER TABLE school_settings ADD COLUMN print_page_margin INTEGER DEFAULT 14")
    # School Settings page — identity (phone/email/principal) + academic session.
    # phone/email letterhead .contact line par; principal_name sirf record ke liye.
    # session_start_month default 3 (March); exam_count default 8 (taqseem N ka
    # future source — abhi sirf store, wiring Hissa 2 mein).
    if "phone" not in settings_cols:
        cur.execute("ALTER TABLE school_settings ADD COLUMN phone TEXT DEFAULT ''")
    if "email" not in settings_cols:
        cur.execute("ALTER TABLE school_settings ADD COLUMN email TEXT DEFAULT ''")
    if "principal_name" not in settings_cols:
        cur.execute("ALTER TABLE school_settings ADD COLUMN principal_name TEXT DEFAULT ''")
    if "session_start_month" not in settings_cols:
        cur.execute("ALTER TABLE school_settings ADD COLUMN session_start_month INTEGER DEFAULT 3")
    if "exam_count" not in settings_cols:
        cur.execute("ALTER TABLE school_settings ADD COLUMN exam_count INTEGER DEFAULT 8")

    # Existing DBs: add name_normalized column and back-fill from name.
    lib_cols = {row[1] for row in cur.execute("PRAGMA table_info(image_library)").fetchall()}
    if "name_normalized" not in lib_cols:
        cur.execute("ALTER TABLE image_library ADD COLUMN name_normalized TEXT")
        cur.execute(
            "UPDATE image_library SET name_normalized = LOWER(TRIM(name))"
            " WHERE name_normalized IS NULL"
        )
    # Smart Image Library columns (HISSA A).
    if "keywords" not in lib_cols:
        cur.execute("ALTER TABLE image_library ADD COLUMN keywords TEXT")
    if "question_types" not in lib_cols:
        cur.execute("ALTER TABLE image_library ADD COLUMN question_types TEXT")
    if "category" not in lib_cols:
        cur.execute("ALTER TABLE image_library ADD COLUMN category TEXT")
    if "source_book" not in lib_cols:
        cur.execute("ALTER TABLE image_library ADD COLUMN source_book TEXT")
    if "page_number" not in lib_cols:
        cur.execute("ALTER TABLE image_library ADD COLUMN page_number INTEGER")
    # HISSA 2: WebP thumbnail path (purani rows NULL — grid full par fall back karta hai).
    if "thumb_path" not in lib_cols:
        cur.execute("ALTER TABLE image_library ADD COLUMN thumb_path TEXT")
    # Smart Lossy: kaunsa compression use hua ('lossless'|'lossy'; purani rows NULL).
    if "compression" not in lib_cols:
        cur.execute("ALTER TABLE image_library ADD COLUMN compression TEXT")

    # HISSA 4 — image_library filter indexes. list_by_filters()/topic-counts in
    # columns par filter karte hain; abhi query plan full SCAN karta hai. Ye
    # CREATE INDEX IF NOT EXISTS existing data par safe + idempotent hain (koi
    # schema/restart change nahi). Search (LIKE '%..%') aur category (LOWER())
    # ko ye index nahi lagte — woh alag masla hai (FTS/expression index), yahan nahi.
    cur.execute("CREATE INDEX IF NOT EXISTS idx_image_library_topic ON image_library(syllabus_topic_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_image_library_subject ON image_library(subject)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_image_library_grade ON image_library(grade)")

    # SLO (Student Learning Outcomes) — Marhala 0: sirf table + Excel import.
    # Question<->SLO link Marhala 1 mein, paper coverage Marhala 2 mein aayega.
    # strand alag column hai (slo_code parse nahi karte) taake Marhala 2 mein
    # strand-wise coverage report seedha column par ban sake. bloom_level nullable
    # hai — import verb se suggest karta hai, teacher override kar sakta hai.
    cur.execute("""
        CREATE TABLE IF NOT EXISTS slo (
            id          TEXT PRIMARY KEY,
            class       TEXT NOT NULL,
            subject     TEXT NOT NULL,
            slo_code    TEXT NOT NULL,
            slo_text    TEXT NOT NULL,
            bloom_level TEXT,
            strand      TEXT,
            created_at  TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(slo_code)
        )
        """)
    # class+subject par listing/filter (e.g. "Pre Year 1 Math ke saare SLO") —
    # SCAN se bachao. (slo_code ka UNIQUE khud implicit index bhi de deta hai.)
    cur.execute("CREATE INDEX IF NOT EXISTS idx_slo_class_subject ON slo(class, subject)")

    # Existing DBs: add sequence column (INTEGER, nullable). slo_code strand ke
    # hisaab se group hai (teaching order NAHI), is liye taqseem/list ke asal kitab
    # ki tarteeb ke liye teacher yahan number bharta hai. Purani rows NULL rehti
    # hain (taqseem un par slo_code fallback karta hai).
    slo_cols = {row[1] for row in cur.execute("PRAGMA table_info(slo)").fetchall()}
    if "sequence" not in slo_cols:
        cur.execute("ALTER TABLE slo ADD COLUMN sequence INTEGER")

    # Question <-> SLO link — Marhala 1. Alag link table (questions column NAHI)
    # taake: (1) ek sawal = kai SLO, (2) 200+ purane questions bilkul untouched
    # (koi ALTER/migration nahi), (3) gemini (protected) question bhi tag ho sake
    # bina uske row ko chhuye. Composite PK duplicate link ko rokta hai (idempotent).
    # slo_id (PK) se link karte hain, slo_code se nahi — re-import par id stable
    # rehta hai; report ke liye slo_code/slo_text JOIN se aa jaata hai. FK enforce
    # nahi hoti (baaqi schema jaisa) — coverage report defensive JOIN karega.
    cur.execute("""
        CREATE TABLE IF NOT EXISTS question_slo (
            question_id TEXT NOT NULL REFERENCES questions(id),
            slo_id      TEXT NOT NULL REFERENCES slo(id),
            created_at  TEXT DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (question_id, slo_id)
        )
        """)
    # Reverse lookup "is SLO ke saare questions" (Marhala 2 coverage) — SCAN se bachao.
    # (question_id par filter composite PK ka implicit index khud de deta hai.)
    cur.execute("CREATE INDEX IF NOT EXISTS idx_question_slo_slo ON question_slo(slo_id)")

    # Marhala 4A — per-class print settings. class_key = normalize_class(class_name);
    # papers.class_name free-text hai isliye normalized key se "Class 5"/"class 5" ek
    # hi row. Row na mile to school_settings ke global print_* defaults (row-level
    # fallback). Purane papers: koi row nahi + defaults 14/14/14 = output bilkul waisa.
    cur.execute("""
        CREATE TABLE IF NOT EXISTS class_print_settings (
            class_key   TEXT PRIMARY KEY,
            font_size   INTEGER NOT NULL,
            q_gap       INTEGER NOT NULL,
            page_margin INTEGER NOT NULL
        )
        """)

    # Hissa 2 — SLO → exam plan (taqseem). Har SLO ka ek assignment: kaunsi exam
    # (1..N) mein. exam_no = 0 => Unassigned (NULL-sequence ya N-shrink se nikle SLO).
    # class/subject slo se JOIN par milte hain (slo_id globally ek hi class+subject ka),
    # is liye yahan denormalize nahi. N global hai (school_settings.exam_count).
    # position = exam ke andar teacher ka order (optional). Plan per class+subject =
    # us (class,subject) ke slo_id set ke assignments.
    cur.execute("""
        CREATE TABLE IF NOT EXISTS slo_exam_plan (
            slo_id     TEXT PRIMARY KEY REFERENCES slo(id),
            exam_no    INTEGER NOT NULL,
            position   INTEGER,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """)
    cur.execute("CREATE INDEX IF NOT EXISTS idx_slo_exam_plan_exam ON slo_exam_plan(exam_no)")

    conn.commit()
    conn.close()
