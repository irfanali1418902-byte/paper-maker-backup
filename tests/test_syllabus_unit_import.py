"""HISSA 3 tests — syllabus_unit_import_service.import_units_from_excel."""

from __future__ import annotations

import io
import uuid

import openpyxl
import pytest

from app.repositories import syllabus_repository
from app.services import syllabus_unit_import_service as svc

HEADER = ["subtopic_title", "subject", "grade", "unit_no", "unit_title", "unit"]


def _make_xlsx(rows: list[list], header: list[str] = HEADER) -> bytes:
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(header)
    for row in rows:
        ws.append(row)
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


def _insert_topic(subtopic: str, subject: str = "Math", grade: str = "Grade 4") -> str:
    from app.core.database import get_connection
    tid = str(uuid.uuid4())
    conn = get_connection()
    conn.execute(
        """INSERT INTO syllabus_topics
           (id, subject, grade, unit_no, unit_title, page_range,
            subtopic_title, activity_type, page_no, learning_outcome)
           VALUES (?,?,?,?,?,?,?,?,?,?)""",
        (tid, subject, grade, 1, "Old Title", "1-5", subtopic, "classwork", 1, ""),
    )
    conn.commit()
    conn.close()
    return tid


# ── 1. Happy path — sab fields update hon ────────────────────────────────────

def test_happy_path_all_fields(test_db):
    tid = _insert_topic("Fractions")
    xlsx = _make_xlsx([["Fractions", "Math", "Grade 4", 2, "New Title", "Unit 2: Fractions"]])
    result = svc.import_units_from_excel(xlsx)

    assert result["updated"] == 1
    assert result["skipped"] == 0

    row = syllabus_repository.find_by_id(tid)
    assert row["unit_no"] == 2
    assert row["unit_title"] == "New Title"
    assert row["unit"] == "Unit 2: Fractions"


# ── 2. Missing subtopic_title column → ValueError ─────────────────────────────

def test_missing_subtopic_title_column_raises(test_db):
    xlsx = _make_xlsx([["Fractions", 1]], header=["topic", "unit_no"])
    with pytest.raises(ValueError, match="subtopic_title"):
        svc.import_units_from_excel(xlsx)


# ── 3. Topic not found → skip ─────────────────────────────────────────────────

def test_topic_not_found_skipped(test_db):
    xlsx = _make_xlsx([["NonExistentTopic", "Math", "Grade 4", 1, "X", "Unit 1"]])
    result = svc.import_units_from_excel(xlsx)
    assert result["skipped"] == 1
    assert result["results"][0]["reason"] == "topic DB mein nahi mila"


# ── 4. subject+grade hint priority ───────────────────────────────────────────

def test_subject_grade_hint_priority(test_db):
    science_id = _insert_topic("Plants", subject="Science", grade="Grade 5")
    math_id    = _insert_topic("Plants", subject="Math",    grade="Grade 5")

    xlsx = _make_xlsx([["Plants", "Math", "Grade 5", 3, "Algebra", "Unit 3"]])
    svc.import_units_from_excel(xlsx)

    math_row    = syllabus_repository.find_by_id(math_id)
    science_row = syllabus_repository.find_by_id(science_id)
    assert math_row["unit"] == "Unit 3"
    assert science_row["unit"] is None  # chhua nahi


# ── 5. Khali unit fields → skip ──────────────────────────────────────────────

def test_empty_unit_fields_skipped(test_db):
    _insert_topic("Decimals")
    xlsx = _make_xlsx([["Decimals", None, None, None, None, None]])
    result = svc.import_units_from_excel(xlsx)
    assert result["skipped"] == 1
    assert "koi bhi unit field" in result["results"][0]["reason"]


# ── 6. Sirf unit field (unit_no/unit_title khali) ───────────────────────────

def test_only_unit_label_updates(test_db):
    tid = _insert_topic("Addition")
    xlsx = _make_xlsx([["Addition", None, None, None, None, "Unit 1: Numbers"]])
    result = svc.import_units_from_excel(xlsx)

    assert result["updated"] == 1
    row = syllabus_repository.find_by_id(tid)
    assert row["unit"] == "Unit 1: Numbers"
    assert row["unit_no"] == 1       # purana value unchanged
    assert row["unit_title"] == "Old Title"  # purana value unchanged


# ── 7. Mixed rows — correct counts ───────────────────────────────────────────

def test_mixed_rows_counts(test_db):
    _insert_topic("Subtraction")
    _insert_topic("Multiplication")

    xlsx = _make_xlsx([
        ["Subtraction",    "Math", "Grade 4", 1, "Numbers", "Unit 1"],
        ["Multiplication", "Math", "Grade 4", 2, "Ops",     "Unit 2"],
        ["Ghost Topic",    "Math", "Grade 4", 1, "X",       "Unit 1"],
    ])
    result = svc.import_units_from_excel(xlsx)
    assert result["updated"] == 2
    assert result["skipped"] == 1


# ── 8. Khali subtopic_title row → skip ───────────────────────────────────────

def test_empty_subtopic_row_skipped(test_db):
    xlsx = _make_xlsx([["", "Math", "Grade 4", 1, "Title", "Unit 1"]])
    result = svc.import_units_from_excel(xlsx)
    assert result["skipped"] == 1
    assert "khali" in result["results"][0]["reason"]


# ── 9. Invalid file bytes → ValueError ───────────────────────────────────────

def test_invalid_file_raises(test_db):
    with pytest.raises(ValueError, match="Excel parse nahi hua"):
        svc.import_units_from_excel(b"not excel")
