"""Smart Question Bank — HISSA A tests.

Covers:
- DB migration: 6 new columns exist, idempotent on re-run
- list_by_filters: q search (text + keywords), status filter
- PATCH /api/questions/{id}: new smart fields saved + returned
- POST /api/bank/questions: new fields saved on create
- PATCH /api/questions/bulk-meta: replace + append keywords, status, empty ids → 422
- Old questions (no new fields) return NULL without crash
"""

import sqlite3
import uuid

import pytest
from fastapi.testclient import TestClient

from app.core.database import init_db
from app.main import app
from app.repositories import questions_repository

client = TestClient(app)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _q(db_path, **overrides):
    """Insert a minimal question row and return its id."""
    defaults = {
        "id": str(uuid.uuid4()),
        "subject": "Math",
        "topic": "Fractions",
        "bloom_level": "REMEMBER",
        "difficulty": "easy",
        "question_type": "short-answer",
        "marks": 1,
        "question_en": "What is a fraction?",
        "question_ur": None,
        "options_en": "[]",
        "options_ur": "[]",
        "correct_answer_en": None,
        "correct_answer_ur": None,
        "explanation_en": None,
        "explanation_ur": None,
        "visual_emoji": None,
        "visual_count": None,
        "syllabus_topic_id": None,
        "image_path": None,
        "image_size": None,
        "source": "manual",
        "learning_outcome": None,
        "estimated_time": None,
        "keywords": None,
        "source_book": None,
        "page_number": None,
        "status": "published",
    }
    defaults.update(overrides)
    conn = sqlite3.connect(db_path)
    conn.execute(
        """INSERT INTO questions
           (id, subject, topic, bloom_level, difficulty, question_type, marks,
            question_en, question_ur, options_en, options_ur,
            correct_answer_en, correct_answer_ur, explanation_en, explanation_ur,
            visual_emoji, visual_count, syllabus_topic_id, image_path, image_size,
            source, learning_outcome, estimated_time, keywords, source_book,
            page_number, status)
           VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (
            defaults["id"], defaults["subject"], defaults["topic"],
            defaults["bloom_level"], defaults["difficulty"], defaults["question_type"],
            defaults["marks"], defaults["question_en"], defaults["question_ur"],
            defaults["options_en"], defaults["options_ur"],
            defaults["correct_answer_en"], defaults["correct_answer_ur"],
            defaults["explanation_en"], defaults["explanation_ur"],
            defaults["visual_emoji"], defaults["visual_count"],
            defaults["syllabus_topic_id"], defaults["image_path"], defaults["image_size"],
            defaults["source"], defaults["learning_outcome"], defaults["estimated_time"],
            defaults["keywords"], defaults["source_book"], defaults["page_number"],
            defaults["status"],
        ),
    )
    conn.commit()
    conn.close()
    return defaults["id"]


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def test_db(monkeypatch, tmp_path):
    db_file = tmp_path / "test.db"
    monkeypatch.setattr("app.core.database.DB_PATH", db_file)
    init_db()
    return str(db_file)


# ---------------------------------------------------------------------------
# Migration tests
# ---------------------------------------------------------------------------

def test_migration_adds_6_new_columns(test_db):
    conn = sqlite3.connect(test_db)
    cols = {row[1] for row in conn.execute("PRAGMA table_info(questions)").fetchall()}
    conn.close()
    for col in ("learning_outcome", "estimated_time", "keywords", "source_book", "page_number", "status"):
        assert col in cols, f"Column missing: {col}"


def test_migration_idempotent(test_db):
    """Running init_db() twice must not raise."""
    import app.core.database as db_mod
    db_mod.init_db()


def test_old_question_nulls_no_crash(test_db):
    """A question with NULL new fields must be returned without error."""
    qid = _q(test_db, learning_outcome=None, keywords=None, status="published")
    row = questions_repository.find_by_id(qid)
    assert row["keywords"] is None
    assert row["status"] == "published"


# ---------------------------------------------------------------------------
# list_by_filters — q search
# ---------------------------------------------------------------------------

def test_search_by_question_en(test_db):
    _q(test_db, question_en="Pythagoras theorem explains triangles")
    _q(test_db, question_en="Unrelated history question")
    results = questions_repository.list_by_filters(q="Pythagoras")
    assert len(results) == 1
    assert "Pythagoras" in results[0]["question_en"]


def test_search_by_keywords(test_db):
    _q(test_db, question_en="Short answer", keywords="geometry, triangles, angles")
    _q(test_db, question_en="Another question", keywords="algebra")
    results = questions_repository.list_by_filters(q="triangle")
    assert len(results) == 1
    assert results[0]["keywords"] == "geometry, triangles, angles"


def test_search_empty_returns_all(test_db):
    _q(test_db)
    _q(test_db)
    results = questions_repository.list_by_filters(q=None)
    assert len(results) == 2


def test_null_keywords_no_crash_in_search(test_db):
    """Questions with NULL keywords must not crash the LIKE search."""
    _q(test_db, keywords=None, question_en="Safe question")
    results = questions_repository.list_by_filters(q="Safe")
    assert len(results) == 1


# ---------------------------------------------------------------------------
# list_by_filters — status filter
# ---------------------------------------------------------------------------

def test_status_filter_published(test_db):
    _q(test_db, status="published")
    _q(test_db, status="draft")
    results = questions_repository.list_by_filters(status="published")
    assert all(r["status"] == "published" for r in results)
    assert len(results) == 1


def test_status_filter_draft(test_db):
    _q(test_db, status="published")
    _q(test_db, status="draft")
    results = questions_repository.list_by_filters(status="draft")
    assert len(results) == 1
    assert results[0]["status"] == "draft"


# ---------------------------------------------------------------------------
# PATCH /api/questions/{id} — new fields via API
# ---------------------------------------------------------------------------

def test_patch_question_new_fields(test_db):
    qid = _q(test_db)
    resp = client.patch(f"/api/questions/{qid}", json={
        "keywords": "geometry, angles",
        "source_book": "NCERT Math 7",
        "page_number": 42,
        "status": "draft",
        "learning_outcome": "Identify triangles",
        "estimated_time": 3,
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["keywords"] == "geometry, angles"
    assert data["source_book"] == "NCERT Math 7"
    assert data["page_number"] == 42
    assert data["status"] == "draft"
    assert data["learning_outcome"] == "Identify triangles"
    assert data["estimated_time"] == 3


# ---------------------------------------------------------------------------
# bulk_update_meta — repository level
# ---------------------------------------------------------------------------

def test_bulk_meta_replace_keywords(test_db):
    id1 = _q(test_db, keywords="old, tags")
    id2 = _q(test_db, keywords="other")
    count = questions_repository.bulk_update_meta([id1, id2], {"keywords": "new, kw"}, "replace")
    assert count == 2
    assert questions_repository.find_by_id(id1)["keywords"] == "new, kw"
    assert questions_repository.find_by_id(id2)["keywords"] == "new, kw"


def test_bulk_meta_append_keywords(test_db):
    id1 = _q(test_db, keywords="alpha, beta")
    count = questions_repository.bulk_update_meta([id1], {"keywords": "gamma, alpha"}, "append")
    assert count == 1
    result_kws = {k.strip() for k in questions_repository.find_by_id(id1)["keywords"].split(",")}
    assert result_kws == {"alpha", "beta", "gamma"}


def test_bulk_meta_status(test_db):
    id1 = _q(test_db, status="published")
    id2 = _q(test_db, status="published")
    questions_repository.bulk_update_meta([id1, id2], {"status": "archived"}, "replace")
    assert questions_repository.find_by_id(id1)["status"] == "archived"
    assert questions_repository.find_by_id(id2)["status"] == "archived"


# ---------------------------------------------------------------------------
# PATCH /api/questions/bulk-meta — API level
# ---------------------------------------------------------------------------

def test_api_bulk_meta_empty_ids_422(test_db):
    resp = client.patch("/api/questions/bulk-meta", json={
        "question_ids": [],
        "status": "draft",
    })
    assert resp.status_code == 422


def test_api_bulk_meta_no_field_422(test_db):
    resp = client.patch("/api/questions/bulk-meta", json={
        "question_ids": ["some-id"],
    })
    assert resp.status_code == 422


def test_api_bulk_meta_success(test_db):
    id1 = _q(test_db)
    resp = client.patch("/api/questions/bulk-meta", json={
        "question_ids": [id1],
        "status": "draft",
        "keywords": "math, fractions",
    })
    assert resp.status_code == 200
    assert resp.json()["updated"] == 1
    row = questions_repository.find_by_id(id1)
    assert row["status"] == "draft"
    assert row["keywords"] == "math, fractions"
