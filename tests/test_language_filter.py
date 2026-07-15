"""HISSA 1 tests: language_filter in repository queries and request schema."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.repositories import questions_repository


# ── fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def client(test_db):
    from app.main import app
    return TestClient(app)


def _base_q(overrides: dict) -> dict:
    """Minimal valid question dict for direct repo insert."""
    q = {
        "id": "test-id",
        "subject": "Science",
        "topic": "Light",
        "bloom_level": "UNDERSTAND",
        "difficulty": "medium",
        "question_type": "short-answer",
        "marks": 2,
        "question_en": None,
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
        "answer_lines": None,
    }
    q.update(overrides)
    return q


@pytest.fixture
def seeded_db(test_db):
    """Insert one English-only, one Urdu-only, one bilingual question."""
    questions_repository.insert(_base_q({
        "id": "en-only",
        "question_en": "What is photosynthesis?",
        "question_ur": None,
    }))
    questions_repository.insert(_base_q({
        "id": "ur-only",
        "question_en": None,
        "question_ur": "روشنی کیا ہے؟",
    }))
    questions_repository.insert(_base_q({
        "id": "bilingual",
        "question_en": "What is light?",
        "question_ur": "روشنی کیا ہے؟",
    }))
    return test_db


# ── find_for_blueprint_section ────────────────────────────────────────────────

class TestFindForBlueprintSection:
    def test_no_filter_returns_all(self, seeded_db):
        rows = questions_repository.find_for_blueprint_section(
            subject="Science", topic_ids=[], question_types=[],
            source=None, status="all", language_filter=None,
        )
        ids = {r["id"] for r in rows}
        assert ids == {"en-only", "ur-only", "bilingual"}

    def test_en_filter_excludes_urdu_only(self, seeded_db):
        rows = questions_repository.find_for_blueprint_section(
            subject="Science", topic_ids=[], question_types=[],
            source=None, status="all", language_filter="en",
        )
        ids = {r["id"] for r in rows}
        assert "ur-only" not in ids
        assert "en-only" in ids
        assert "bilingual" in ids

    def test_ur_filter_excludes_english_only(self, seeded_db):
        rows = questions_repository.find_for_blueprint_section(
            subject="Science", topic_ids=[], question_types=[],
            source=None, status="all", language_filter="ur",
        )
        ids = {r["id"] for r in rows}
        assert "en-only" not in ids
        assert "ur-only" in ids
        assert "bilingual" in ids

    def test_bilingual_appears_in_both_filters(self, seeded_db):
        en_rows = questions_repository.find_for_blueprint_section(
            subject="Science", topic_ids=[], question_types=[],
            source=None, status="all", language_filter="en",
        )
        ur_rows = questions_repository.find_for_blueprint_section(
            subject="Science", topic_ids=[], question_types=[],
            source=None, status="all", language_filter="ur",
        )
        en_ids = {r["id"] for r in en_rows}
        ur_ids = {r["id"] for r in ur_rows}
        assert "bilingual" in en_ids
        assert "bilingual" in ur_ids


# ── find_least_used ───────────────────────────────────────────────────────────

class TestFindLeastUsed:
    def test_no_filter_returns_all(self, seeded_db):
        rows = questions_repository.find_least_used(
            subject="Science", bloom_level="UNDERSTAND",
            difficulty=None, limit=10, language_filter=None,
        )
        ids = {r["id"] for r in rows}
        assert ids == {"en-only", "ur-only", "bilingual"}

    def test_en_filter(self, seeded_db):
        rows = questions_repository.find_least_used(
            subject="Science", bloom_level="UNDERSTAND",
            difficulty=None, limit=10, language_filter="en",
        )
        ids = {r["id"] for r in rows}
        assert "ur-only" not in ids
        assert "en-only" in ids

    def test_ur_filter(self, seeded_db):
        rows = questions_repository.find_least_used(
            subject="Science", bloom_level="UNDERSTAND",
            difficulty=None, limit=10, language_filter="ur",
        )
        ids = {r["id"] for r in rows}
        assert "en-only" not in ids
        assert "ur-only" in ids


# ── Schema validation ─────────────────────────────────────────────────────────

class TestLanguageFilterSchema:
    def test_invalid_language_filter_returns_422(self, client):
        res = client.post("/api/generate-paper", json={
            "subject": "Science",
            "language_filter": "french",
        })
        assert res.status_code == 422

    def test_valid_en_filter_accepted(self, client):
        # No questions in DB → 404, but schema parses correctly (not 422)
        res = client.post("/api/generate-paper", json={
            "subject": "Science",
            "language_filter": "en",
        })
        assert res.status_code != 422

    def test_null_filter_accepted(self, client):
        res = client.post("/api/generate-paper", json={
            "subject": "Science",
            "language_filter": None,
        })
        assert res.status_code != 422

    def test_omitted_filter_accepted(self, client):
        res = client.post("/api/generate-paper", json={
            "subject": "Science",
        })
        assert res.status_code != 422
