"""Tests for image_size field on PATCH /api/questions/{id}.

Covers: valid size saves to DB, invalid size is rejected (422),
and null/missing size behaves as medium default.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.repositories import questions_repository

client = TestClient(app)


def _insert_question(qid: str = "sz-q-001") -> None:
    questions_repository.insert({
        "id": qid,
        "subject": "Science",
        "topic": "Plants",
        "bloom_level": "remember",
        "difficulty": "easy",
        "question_type": "short-answer",
        "marks": 2,
        "question_en": "What is a leaf?",
        "question_ur": None,
        "options_en": None,
        "options_ur": None,
        "correct_answer_en": None,
        "correct_answer_ur": None,
        "explanation_en": None,
        "explanation_ur": None,
        "visual_emoji": None,
        "visual_count": None,
        "image_path": None,
        "image_size": None,
    })


# ---------------------------------------------------------------------------
# Valid sizes save correctly
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("size", ["small", "medium", "large"])
def test_patch_valid_image_size_saves_to_db(test_db, size):
    qid = f"sz-{size}"
    _insert_question(qid)

    resp = client.patch(
        f"/api/questions/{qid}",
        json={"image_size": size, "question_en": "What is a leaf?"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["image_size"] == size

    # Verify DB
    q = questions_repository.find_by_id(qid)
    assert q["image_size"] == size


# ---------------------------------------------------------------------------
# Invalid size rejected (422 from Pydantic)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("bad_size", ["huge", "tiny", "LARGE", "xl", ""])
def test_patch_invalid_image_size_returns_422(test_db, bad_size):
    _insert_question("sz-bad")
    resp = client.patch(
        "/api/questions/sz-bad",
        json={"image_size": bad_size, "question_en": "What is a leaf?"},
    )
    assert resp.status_code == 422

    # DB must be unchanged
    q = questions_repository.find_by_id("sz-bad")
    assert q["image_size"] is None


# ---------------------------------------------------------------------------
# image_size response field present (null) on questions without it
# ---------------------------------------------------------------------------

def test_question_response_includes_image_size_field(test_db):
    _insert_question("sz-null")
    resp = client.patch(
        "/api/questions/sz-null",
        json={"question_en": "What is a leaf?"},
    )
    assert resp.status_code == 200
    assert "image_size" in resp.json()
    assert resp.json()["image_size"] is None
