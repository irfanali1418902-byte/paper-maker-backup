"""Tests for Blueprint HISSA 2: paper assembly, shortfall, topic filter, image_path."""

from __future__ import annotations

import json
import uuid

import pytest
from fastapi.testclient import TestClient

from app.repositories import papers_repository, questions_repository


@pytest.fixture
def client(test_db):
    from app.main import app
    return TestClient(app)


# ── helpers ───────────────────────────────────────────────────────────────────

def _insert_q(subject="Science", qtype="multiple-choice", topic_id=None, source="manual"):
    qid = str(uuid.uuid4())
    questions_repository.insert({
        "id": qid,
        "subject": subject,
        "topic": "Test Topic",
        "bloom_level": "UNDERSTAND",
        "difficulty": "medium",
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
    })
    return qid


def _insert_q_with_image(subject="Science", qtype="multiple-choice", image_path="uploads/test.png"):
    qid = str(uuid.uuid4())
    questions_repository.insert({
        "id": qid,
        "subject": subject,
        "topic": "Test Topic",
        "bloom_level": "UNDERSTAND",
        "difficulty": "medium",
        "question_type": qtype,
        "marks": 1,
        "question_en": f"Q with image {qid[:6]}?",
        "question_ur": None,
        "options_en": "[]",
        "options_ur": "[]",
        "correct_answer_en": "A",
        "correct_answer_ur": None,
        "explanation_en": None,
        "explanation_ur": None,
        "visual_emoji": None,
        "visual_count": None,
        "image_path": image_path,
        "image_size": "medium",
        "source": "manual",
    })
    return qid


def _section(heading="Sec A", types=None, topic_ids=None, count=5, marks=1, source="manual"):
    return {
        "heading": heading,
        "question_types": types or ["multiple-choice"],
        "topic_ids": topic_ids or [],
        "count": count,
        "marks_each": marks,
        "source_filter": source,
    }


def _post_blueprint_paper(client, sections, subject="Science", class_name=None, title=None):
    body: dict = {"sections_input": sections}
    if subject:
        body["subject"] = subject
    if class_name:
        body["class_name"] = class_name
    if title:
        body["paper_title"] = title
    return client.post("/api/blueprint-paper", json=body)


# ── happy path ────────────────────────────────────────────────────────────────

class TestHappyPath:
    def test_single_section_paper(self, client):
        for _ in range(3):
            _insert_q()
        res = _post_blueprint_paper(client, [_section(count=2)])
        assert res.status_code == 200
        assert len(res.json()["questions"]) == 2

    def test_multi_section_paper(self, client):
        for _ in range(5):
            _insert_q(qtype="multiple-choice")
        for _ in range(3):
            _insert_q(qtype="short-answer")
        sections = [
            _section("A", ["multiple-choice"], count=3),
            _section("B", ["short-answer"], count=2),
        ]
        res = _post_blueprint_paper(client, sections)
        assert res.status_code == 200
        data = res.json()
        assert len(data["questions"]) == 5

    def test_response_has_paper_id(self, client):
        _insert_q()
        res = _post_blueprint_paper(client, [_section(count=1)])
        assert "paper_id" in res.json()

    def test_response_has_sections_meta(self, client):
        for _ in range(3):
            _insert_q()
        res = _post_blueprint_paper(client, [_section(count=2)])
        assert "sections_meta" in res.json()
        assert len(res.json()["sections_meta"]) == 1

    def test_sections_meta_has_correct_fields(self, client):
        for _ in range(3):
            _insert_q()
        res = _post_blueprint_paper(client, [_section("Sec A", count=2)])
        sec = res.json()["sections_meta"][0]
        assert sec["heading"] == "Sec A"
        assert "question_ids" in sec
        assert "marks" in sec
        assert "shortfall" in sec

    def test_sections_meta_stored_in_db(self, client):
        for _ in range(3):
            _insert_q()
        res = _post_blueprint_paper(client, [_section(count=2)])
        pid = res.json()["paper_id"]
        row = papers_repository.find_by_id(pid)
        assert row["sections_meta"] is not None
        stored = json.loads(row["sections_meta"])
        assert len(stored) == 1
        assert stored[0]["heading"] == "Sec A"

    def test_shortfall_notes_empty_when_all_filled(self, client):
        for _ in range(5):
            _insert_q()
        res = _post_blueprint_paper(client, [_section(count=3)])
        assert res.json()["shortfall_notes"] == []

    def test_total_marks_computed(self, client):
        for _ in range(4):
            _insert_q()
        res = _post_blueprint_paper(client, [_section(count=4, marks=2)])
        # marks_each=2, 4 questions picked → total = 4 * actual question marks (1 each)
        assert res.json()["total_marks"] == 4

    def test_paper_persisted_in_db(self, client):
        for _ in range(3):
            _insert_q()
        before = papers_repository.count_all()
        _post_blueprint_paper(client, [_section(count=2)])
        assert papers_repository.count_all() == before + 1

    def test_usage_count_incremented(self, client):
        qid = _insert_q()
        _post_blueprint_paper(client, [_section(count=1)])
        q = questions_repository.find_by_id(qid)
        assert q["usage_count"] == 1


# ── shortfall ─────────────────────────────────────────────────────────────────

class TestShortfall:
    def test_partial_section_still_builds_paper(self, client):
        """DB has 3, section wants 5 — paper still built with 3."""
        for _ in range(3):
            _insert_q()
        res = _post_blueprint_paper(client, [_section(count=5)])
        assert res.status_code == 200
        assert len(res.json()["questions"]) == 3

    def test_shortfall_note_present(self, client):
        for _ in range(3):
            _insert_q()
        res = _post_blueprint_paper(client, [_section("Sec A", count=5)])
        notes = res.json()["shortfall_notes"]
        assert len(notes) == 1
        assert "Sec A" in notes[0]
        assert "5 maange" in notes[0]
        assert "3 mile" in notes[0]

    def test_shortfall_in_sections_meta(self, client):
        for _ in range(2):
            _insert_q()
        res = _post_blueprint_paper(client, [_section(count=5)])
        assert res.json()["sections_meta"][0]["shortfall"] == 3

    def test_one_section_full_one_partial(self, client):
        """Section A full (5/5), Section B partial (2/5) — both in paper."""
        for _ in range(5):
            _insert_q(qtype="multiple-choice")
        for _ in range(2):
            _insert_q(qtype="short-answer")
        sections = [
            _section("A", ["multiple-choice"], count=5),
            _section("B", ["short-answer"], count=5),
        ]
        res = _post_blueprint_paper(client, sections)
        assert res.status_code == 200
        data = res.json()
        assert len(data["questions"]) == 7
        assert len(data["shortfall_notes"]) == 1
        assert "B" in data["shortfall_notes"][0]

    def test_section_zero_available_skipped_gracefully(self, client):
        """Section B has no questions — paper built from Section A only."""
        for _ in range(3):
            _insert_q(qtype="multiple-choice")
        sections = [
            _section("A", ["multiple-choice"], count=3),
            _section("B", ["short-answer"], count=3),
        ]
        res = _post_blueprint_paper(client, sections)
        assert res.status_code == 200
        assert len(res.json()["questions"]) == 3
        assert len(res.json()["shortfall_notes"]) == 1

    def test_zero_shortfall_stored_when_exact(self, client):
        for _ in range(5):
            _insert_q()
        res = _post_blueprint_paper(client, [_section(count=5)])
        assert res.json()["sections_meta"][0]["shortfall"] == 0


# ── all-empty error ───────────────────────────────────────────────────────────

class TestAllEmpty:
    def test_404_when_no_questions_at_all(self, client):
        res = _post_blueprint_paper(client, [_section(count=5)])
        assert res.status_code == 404

    def test_404_when_wrong_subject(self, client):
        for _ in range(3):
            _insert_q(subject="Science")
        res = _post_blueprint_paper(client, [_section(count=3)], subject="Mathematics")
        assert res.status_code == 404

    def test_404_when_all_sections_empty(self, client):
        """All types requested but none in DB."""
        res = _post_blueprint_paper(client, [
            _section("A", ["multiple-choice"], count=5),
            _section("B", ["short-answer"], count=5),
        ])
        assert res.status_code == 404


# ── topic filter ──────────────────────────────────────────────────────────────

class TestTopicFilter:
    def test_topic_id_filters_correctly(self, client):
        topic_a = str(uuid.uuid4())
        topic_b = str(uuid.uuid4())
        for _ in range(3):
            _insert_q(topic_id=topic_a)
        for _ in range(3):
            _insert_q(topic_id=topic_b)
        sections = [_section(topic_ids=[topic_a], count=10)]
        res = _post_blueprint_paper(client, sections)
        assert res.status_code == 200
        assert len(res.json()["questions"]) == 3

    def test_multiple_topic_ids(self, client):
        topic_a = str(uuid.uuid4())
        topic_b = str(uuid.uuid4())
        topic_c = str(uuid.uuid4())
        for _ in range(2):
            _insert_q(topic_id=topic_a)
        for _ in range(2):
            _insert_q(topic_id=topic_b)
        for _ in range(2):
            _insert_q(topic_id=topic_c)
        # Request topic_a + topic_b only
        sections = [_section(topic_ids=[topic_a, topic_b], count=10)]
        res = _post_blueprint_paper(client, sections)
        assert res.status_code == 200
        assert len(res.json()["questions"]) == 4

    def test_empty_topic_ids_fetches_all(self, client):
        topic_a = str(uuid.uuid4())
        for _ in range(3):
            _insert_q(topic_id=topic_a)
        for _ in range(2):
            _insert_q(topic_id=None)
        sections = [_section(topic_ids=[], count=10)]
        res = _post_blueprint_paper(client, sections)
        assert res.status_code == 200
        assert len(res.json()["questions"]) == 5


# ── image_path passthrough ────────────────────────────────────────────────────

class TestImagePath:
    def test_question_with_image_carries_through(self, client):
        _insert_q_with_image(image_path="uploads/test_q.png")
        res = _post_blueprint_paper(client, [_section(count=1)])
        assert res.status_code == 200
        q = res.json()["questions"][0]
        assert q["image_path"] == "uploads/test_q.png"
        assert q["image_size"] == "medium"

    def test_question_without_image_has_null_image_path(self, client):
        _insert_q()
        res = _post_blueprint_paper(client, [_section(count=1)])
        q = res.json()["questions"][0]
        assert q["image_path"] is None


# ── saved blueprint_id ────────────────────────────────────────────────────────

class TestSavedBlueprint:
    def test_paper_from_saved_blueprint(self, client):
        for _ in range(5):
            _insert_q()
        # Save a blueprint first
        bp_res = client.post("/api/blueprints", json={
            "name": "Test Blueprint",
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

    def test_invalid_blueprint_id_returns_404(self, client):
        res = client.post("/api/blueprint-paper", json={"blueprint_id": "nonexistent-id"})
        assert res.status_code == 404

    def test_request_without_blueprint_or_sections_rejected(self, client):
        res = client.post("/api/blueprint-paper", json={"subject": "Science"})
        assert res.status_code == 422


# ── multi-type section ────────────────────────────────────────────────────────

class TestMultiTypeSection:
    def test_section_with_two_types(self, client):
        for _ in range(3):
            _insert_q(qtype="fill-in-the-blank")
        for _ in range(3):
            _insert_q(qtype="short-answer")
        sections = [_section("Mixed", ["fill-in-the-blank", "short-answer"], count=4)]
        res = _post_blueprint_paper(client, sections)
        assert res.status_code == 200
        assert len(res.json()["questions"]) == 4
