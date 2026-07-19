"""SLO export ke optional grade/subject filter (feature/slo-export-class-filter).

Koi hardcoded DB-count (317/197) nahi — har test apna seed data banata aur usi
seed set (ya query se nikale expected set) ke against assert karta hai, taake
asal DB badalne par test jhoota fail na ho.
"""

from __future__ import annotations

import io

import openpyxl

from app.core.text_norm import normalize_subject
from app.repositories import questions_repository, syllabus_repository
from app.services import question_slo_import_service

EXPECTED_HEADER = ("question_id", "subject", "topic", "question", "slo_code")


# ── seed helpers ────────────────────────────────────────────────────────────────

def _topic(tid: str, grade: str, subject: str = "Mathematics") -> None:
    syllabus_repository.insert(
        topic_id=tid, subject=subject, grade=grade, unit_no=1,
        unit_title="U", page_range="1-2", subtopic_title="S",
        activity_type="A", page_no=1, learning_outcome="LO", unit=None,
    )


def _q(qid: str, subject: str = "Mathematics", topic_id: str | None = None) -> None:
    questions_repository.insert({
        "id": qid, "subject": subject, "topic": "T",
        "bloom_level": "REMEMBER", "difficulty": "easy",
        "question_type": "short-answer", "marks": 1,
        "question_en": f"Q {qid}", "question_ur": None,
        "options_en": "[]", "options_ur": "[]",
        "correct_answer_en": None, "correct_answer_ur": None,
        "explanation_en": None, "explanation_ur": None,
        "visual_emoji": None, "visual_count": None,
        "syllabus_topic_id": topic_id,
    })


def _rows(xlsx: bytes):
    """(header_tuple, [question_id, ...]) — data rows ke question_id column (A)."""
    ws = openpyxl.load_workbook(io.BytesIO(xlsx)).active
    rows = list(ws.iter_rows(values_only=True))
    return rows[0], [r[0] for r in rows[1:] if r[0]]


def _seed_mixed() -> dict:
    """PY1/PY2 topics + mixed subject/topic questions. Returns seeded id-sets."""
    _topic("t_py1", "Pre Year 1")
    _topic("t_py2", "Pre Year 2")
    _q("q1", subject="Mathematics", topic_id="t_py1")
    _q("q2", subject="Math", topic_id="t_py1")        # subject alias
    _q("q3", subject="Mathematics", topic_id="t_py2")
    _q("q4", subject="English", topic_id=None)         # no topic + non-math
    _q("q5", subject="Mathematics", topic_id=None)     # no topic
    return {
        "all": {"q1", "q2", "q3", "q4", "q5"},
        "py1": {"q1", "q2"},
        "math": {"q1", "q2", "q3", "q5"},  # Mathematics + Math alias, English chhoR
    }


# ── (a) no filter = purana behaviour (sab questions) ────────────────────────────

def test_no_filter_returns_all(test_db):
    ids = _seed_mixed()
    header, got = _rows(question_slo_import_service.build_export_xlsx())
    assert header == EXPECTED_HEADER
    assert set(got) == ids["all"]


# ── (b) grade filter ────────────────────────────────────────────────────────────

def test_grade_filter(test_db):
    ids = _seed_mixed()
    header, got = _rows(question_slo_import_service.build_export_xlsx(grade="Pre Year 1"))
    assert header == EXPECTED_HEADER
    assert set(got) == ids["py1"]  # syllabus_topic_id NULL wale (q5) khud excluded


def test_grade_filter_case_insensitive(test_db):
    ids = _seed_mixed()
    _, got = _rows(question_slo_import_service.build_export_xlsx(grade="  pre year 1 "))
    assert set(got) == ids["py1"]


# ── (c) ghalat grade => 0 data rows, header phir bhi maujood ────────────────────

def test_unknown_grade_zero_rows_header_present(test_db):
    _seed_mixed()
    header, got = _rows(question_slo_import_service.build_export_xlsx(grade="Class 99"))
    assert header == EXPECTED_HEADER   # header hamesha
    assert got == []                   # koi data row nahi


# ── (d) subject normalize: Math == Mathematics, non-math excluded ───────────────

def test_subject_math_alias_matches_mathematics(test_db):
    ids = _seed_mixed()
    _, got_math = _rows(question_slo_import_service.build_export_xlsx(subject="Math"))
    _, got_full = _rows(question_slo_import_service.build_export_xlsx(subject="Mathematics"))
    assert set(got_math) == set(got_full) == ids["math"]
    assert "q4" not in got_math  # English chhoR diya


# ── (e) grade + subject dono ────────────────────────────────────────────────────

def test_grade_and_subject_combined(test_db):
    ids = _seed_mixed()
    _, got = _rows(
        question_slo_import_service.build_export_xlsx(grade="Pre Year 1", subject="math")
    )
    assert set(got) == ids["py1"] & ids["math"]  # {q1, q2}


# ── filename ────────────────────────────────────────────────────────────────────

def test_export_filename_default_and_dynamic(test_db):
    assert question_slo_import_service.export_filename() == "slo_assign_export.xlsx"
    assert (
        question_slo_import_service.export_filename(grade="Pre Year 1", subject="Mathematics")
        == "slo_assign_export_Pre_Year_1_Mathematics.xlsx"
    )
    # sirf grade
    assert (
        question_slo_import_service.export_filename(grade="Pre Year 2")
        == "slo_assign_export_Pre_Year_2.xlsx"
    )


# ── normalize helper ────────────────────────────────────────────────────────────

def test_normalize_subject_aliases():
    assert normalize_subject("Math") == normalize_subject("Mathematics") == "mathematics"
    assert normalize_subject("  MATHS ") == "mathematics"
    assert normalize_subject("English") == "english"   # anjaan -> lower/trim
    assert normalize_subject(None) == ""
