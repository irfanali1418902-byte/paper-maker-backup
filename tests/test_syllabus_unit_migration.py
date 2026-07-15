"""HISSA 0 tests — syllabus_topics.unit column migration + repository."""

import uuid

from app.core import database
from app.core.database import get_connection
from app.repositories import syllabus_repository


def _insert_topic(subject="Math", grade="Grade 4", subtopic="Fractions", unit=None):
    tid = str(uuid.uuid4())
    syllabus_repository.insert(
        topic_id=tid,
        subject=subject,
        grade=grade,
        unit_no=1,
        unit_title="Numbers",
        page_range="1-10",
        subtopic_title=subtopic,
        activity_type="classwork",
        page_no=1,
        learning_outcome="",
        unit=unit,
    )
    return tid


# ── 1. Column exists after init_db ───────────────────────────────────────────

def test_unit_column_exists(test_db):
    conn = get_connection()
    cols = {row[1] for row in conn.execute("PRAGMA table_info(syllabus_topics)").fetchall()}
    conn.close()
    assert "unit" in cols


# ── 2. NULL default for new rows ─────────────────────────────────────────────

def test_unit_defaults_to_null(test_db):
    tid = _insert_topic()
    row = syllabus_repository.find_by_id(tid)
    assert row["unit"] is None


# ── 3. unit value round-trips correctly ──────────────────────────────────────

def test_unit_value_saved_and_read(test_db):
    tid = _insert_topic(unit="Unit 1: Numbers")
    row = syllabus_repository.find_by_id(tid)
    assert row["unit"] == "Unit 1: Numbers"


# ── 4. update_unit sets the field ────────────────────────────────────────────

def test_update_unit_sets_field(test_db):
    tid = _insert_topic()
    result = syllabus_repository.update_unit(tid, unit_no=2, unit_title="Fractions", unit="Unit 2")
    assert result is True
    row = syllabus_repository.find_by_id(tid)
    assert row["unit"] == "Unit 2"
    assert row["unit_no"] == 2
    assert row["unit_title"] == "Fractions"


# ── 5. update_unit with no fields returns False ───────────────────────────────

def test_update_unit_no_fields_returns_false(test_db):
    tid = _insert_topic()
    result = syllabus_repository.update_unit(tid, unit_no=None, unit_title=None, unit=None)
    assert result is False


# ── 6. Purane topics (unit=None) list_by_filters mein kaam karein ────────────

def test_old_topics_still_work_in_list(test_db):
    _insert_topic(subject="Science", grade="Grade 5", subtopic="Plants")
    _insert_topic(subject="Science", grade="Grade 5", subtopic="Animals")
    rows = syllabus_repository.list_by_filters(subject="Science", grade="Grade 5")
    assert len(rows) == 2
    for r in rows:
        assert r["unit"] is None  # purana data NULL rahega


# ── 7. Migration idempotent — second init_db call breaks nothing ──────────────

def test_migration_idempotent(test_db):
    database.init_db()  # doosri baar chalao
    conn = get_connection()
    cols = {row[1] for row in conn.execute("PRAGMA table_info(syllabus_topics)").fetchall()}
    conn.close()
    assert "unit" in cols
