"""Tests for Blueprint HISSA 3: difficulty/bloom/status filters + distribution."""

from __future__ import annotations

import json
import uuid

import pytest
from fastapi.testclient import TestClient

from app.repositories import questions_repository


@pytest.fixture
def client(test_db):
    from app.main import app
    return TestClient(app)


# ── helpers ───────────────────────────────────────────────────────────────────

def _insert_q(
    subject="Science",
    qtype="multiple-choice",
    topic_id=None,
    source="manual",
    difficulty="medium",
    bloom_level="UNDERSTAND",
    status="published",
):
    qid = str(uuid.uuid4())
    questions_repository.insert({
        "id": qid,
        "subject": subject,
        "topic": "Test Topic",
        "bloom_level": bloom_level,
        "difficulty": difficulty,
        "question_type": qtype,
        "marks": 1,
        "question_en": f"Q {qid[:6]}?",
        "question_ur": None,
        "options_en": json.dumps(["A", "B", "C", "D"]) if qtype == "multiple-choice" else "[]",
        "options_ur": "[]",
        "correct_answer_en": "A",
        "correct_answer_ur": None,
        "explanation_en": None,
        "explanation_ur": None,
        "visual_emoji": None,
        "visual_count": None,
        "syllabus_topic_id": topic_id,
        "source": source,
        "status": status,
    })
    return qid


def _section(
    heading="Sec A",
    types=None,
    topic_ids=None,
    count=5,
    marks=1,
    source="manual",
    status_filter="published",
    difficulty_filter=None,
    bloom_filter=None,
    difficulty_distribution=None,
):
    sec = {
        "heading": heading,
        "question_types": types or ["multiple-choice"],
        "topic_ids": topic_ids or [],
        "count": count,
        "marks_each": marks,
        "source_filter": source,
        "status_filter": status_filter,
    }
    if difficulty_filter is not None:
        sec["difficulty_filter"] = difficulty_filter
    if bloom_filter is not None:
        sec["bloom_filter"] = bloom_filter
    if difficulty_distribution is not None:
        sec["difficulty_distribution"] = difficulty_distribution
    return sec


def _post(client, sections, subject="Science"):
    return client.post("/api/blueprint-paper", json={
        "sections_input": sections,
        "subject": subject,
    })


# ── status filter ─────────────────────────────────────────────────────────────

class TestStatusFilter:
    def test_draft_excluded_by_default(self, client):
        """Default status_filter='published' → draft questions nahi aane chahiye."""
        _insert_q(status="published")
        _insert_q(status="published")
        _insert_q(status="draft")
        res = _post(client, [_section(count=10)])
        assert res.status_code == 200
        assert len(res.json()["questions"]) == 2

    def test_archived_excluded_by_default(self, client):
        _insert_q(status="published")
        _insert_q(status="archived")
        res = _post(client, [_section(count=10)])
        assert res.status_code == 200
        assert len(res.json()["questions"]) == 1

    def test_status_all_includes_draft(self, client):
        """status_filter='all' → draft bhi aaye."""
        _insert_q(status="published")
        _insert_q(status="draft")
        _insert_q(status="archived")
        res = _post(client, [_section(count=10, status_filter="all")])
        assert res.status_code == 200
        assert len(res.json()["questions"]) == 3

    def test_status_draft_only(self, client):
        _insert_q(status="published")
        _insert_q(status="draft")
        _insert_q(status="draft")
        res = _post(client, [_section(count=10, status_filter="draft")])
        assert res.status_code == 200
        assert len(res.json()["questions"]) == 2

    def test_old_section_no_status_field_uses_published_default(self, client):
        """Purana blueprint section jisme status_filter field hi nahi — sirf published aaye."""
        _insert_q(status="published")
        _insert_q(status="draft")
        # Old-style section dict — no status_filter key at all
        old_sec = {
            "heading": "Old Section",
            "question_types": ["multiple-choice"],
            "topic_ids": [],
            "count": 10,
            "marks_each": 1,
            "source_filter": "manual",
        }
        res = client.post("/api/blueprint-paper", json={
            "sections_input": [old_sec],
            "subject": "Science",
        })
        assert res.status_code == 200
        assert len(res.json()["questions"]) == 1


# ── difficulty filter ─────────────────────────────────────────────────────────

class TestDifficultyFilter:
    def test_easy_filter_returns_only_easy(self, client):
        _insert_q(difficulty="easy")
        _insert_q(difficulty="easy")
        _insert_q(difficulty="medium")
        _insert_q(difficulty="hard")
        res = _post(client, [_section(count=10, difficulty_filter="easy")])
        assert res.status_code == 200
        qs = res.json()["questions"]
        assert len(qs) == 2
        assert all(q["difficulty"] == "easy" for q in qs)

    def test_hard_filter_returns_only_hard(self, client):
        for _ in range(3):
            _insert_q(difficulty="medium")
        _insert_q(difficulty="hard")
        res = _post(client, [_section(count=10, difficulty_filter="hard")])
        assert res.status_code == 200
        qs = res.json()["questions"]
        assert len(qs) == 1
        assert qs[0]["difficulty"] == "hard"

    def test_no_difficulty_filter_returns_all(self, client):
        _insert_q(difficulty="easy")
        _insert_q(difficulty="medium")
        _insert_q(difficulty="hard")
        res = _post(client, [_section(count=10)])
        assert res.status_code == 200
        assert len(res.json()["questions"]) == 3


# ── bloom filter ──────────────────────────────────────────────────────────────

class TestBloomFilter:
    def test_bloom_filter_returns_correct_level(self, client):
        _insert_q(bloom_level="REMEMBER")
        _insert_q(bloom_level="REMEMBER")
        _insert_q(bloom_level="APPLY")
        _insert_q(bloom_level="EVALUATE")
        res = _post(client, [_section(count=10, bloom_filter="REMEMBER")])
        assert res.status_code == 200
        qs = res.json()["questions"]
        assert len(qs) == 2
        assert all(q["bloom_level"] == "REMEMBER" for q in qs)

    def test_invalid_bloom_filter_rejected(self, client):
        res = _post(client, [_section(count=5, bloom_filter="INVALID_LEVEL")])
        assert res.status_code == 422


# ── difficulty_distribution ───────────────────────────────────────────────────

class TestDifficultyDistribution:
    def test_distribution_picks_correct_counts(self, client):
        for _ in range(5):
            _insert_q(difficulty="easy")
        for _ in range(5):
            _insert_q(difficulty="medium")
        for _ in range(5):
            _insert_q(difficulty="hard")
        dist = {"easy": 2, "medium": 3, "hard": 2}
        res = _post(client, [_section(count=7, difficulty_distribution=dist)])
        assert res.status_code == 200
        qs = res.json()["questions"]
        assert len(qs) == 7
        counts = {"easy": 0, "medium": 0, "hard": 0}
        for q in qs:
            counts[q["difficulty"]] += 1
        assert counts["easy"] == 2
        assert counts["medium"] == 3
        assert counts["hard"] == 2

    def test_distribution_partial_shortfall_note(self, client):
        """easy mein sirf 1 sawal, 3 maange — shortfall note aaye."""
        _insert_q(difficulty="easy")
        for _ in range(5):
            _insert_q(difficulty="medium")
        dist = {"easy": 3, "medium": 2}
        res = _post(client, [_section(count=5, difficulty_distribution=dist)])
        assert res.status_code == 200
        notes = res.json()["shortfall_notes"]
        assert any("easy" in n for n in notes)
        assert any("3" in n and "1" in n for n in notes)

    def test_distribution_remaining_slots_filled(self, client):
        """Distribution sum < count — remaining slots any-difficulty se bharein."""
        for _ in range(5):
            _insert_q(difficulty="easy")
        for _ in range(5):
            _insert_q(difficulty="medium")
        # count=10, distribution only specifies 3+3=6 → 4 remaining
        dist = {"easy": 3, "medium": 3}
        res = _post(client, [_section(count=10, difficulty_distribution=dist)])
        assert res.status_code == 200
        assert len(res.json()["questions"]) == 10

    def test_distribution_and_difficulty_filter_rejected(self, client):
        """Dono ek saath → 422."""
        sec = _section(
            count=5,
            difficulty_filter="easy",
            difficulty_distribution={"easy": 3, "medium": 2},
        )
        res = _post(client, [sec])
        assert res.status_code == 422

    def test_distribution_sum_exceeds_count_rejected(self, client):
        """sum(distribution) > count → 422."""
        sec = _section(count=5, difficulty_distribution={"easy": 3, "medium": 5})
        res = _post(client, [sec])
        assert res.status_code == 422

    def test_distribution_invalid_key_rejected(self, client):
        sec = _section(count=5, difficulty_distribution={"veryhard": 2, "medium": 3})
        res = _post(client, [sec])
        assert res.status_code == 422


# ── backward compat ───────────────────────────────────────────────────────────

class TestBackwardCompat:
    def test_old_blueprint_sections_still_work(self, client):
        """Purana saved blueprint (naye fields nahi) — paper banta rahe."""
        for _ in range(5):
            _insert_q(status="published")
        # Save old-style blueprint (no new fields)
        bp_res = client.post("/api/blueprints", json={
            "name": "Old Blueprint",
            "subject": "Science",
            "sections": [{
                "heading": "Section A",
                "question_types": ["multiple-choice"],
                "topic_ids": [],
                "count": 3,
                "marks_each": 1,
                "source_filter": "manual",
            }],
        })
        assert bp_res.status_code == 201
        bp_id = bp_res.json()["id"]
        res = client.post("/api/blueprint-paper", json={"blueprint_id": bp_id})
        assert res.status_code == 200
        assert len(res.json()["questions"]) == 3

    def test_old_blueprint_draft_not_included(self, client):
        """Purana blueprint → status default published → draft excluded."""
        _insert_q(status="published")
        _insert_q(status="published")
        _insert_q(status="draft")
        bp_res = client.post("/api/blueprints", json={
            "name": "Old BP Draft Test",
            "subject": "Science",
            "sections": [{
                "heading": "A",
                "question_types": ["multiple-choice"],
                "topic_ids": [],
                "count": 10,
                "marks_each": 1,
                "source_filter": "manual",
            }],
        })
        bp_id = bp_res.json()["id"]
        res = client.post("/api/blueprint-paper", json={"blueprint_id": bp_id})
        assert res.status_code == 200
        assert len(res.json()["questions"]) == 2
