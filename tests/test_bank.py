"""Tests for manual question bank: POST/PATCH/DELETE /api/bank/questions."""

import json
import uuid

import pytest
from fastapi.testclient import TestClient

from app.repositories import questions_repository


@pytest.fixture
def client(test_db):
    from app.main import app
    return TestClient(app)


def _insert_gemini_question(subject="Mathematics", topic="Algebra"):
    """Helper: insert a Gemini-sourced question (default, no source field)."""
    qid = str(uuid.uuid4())
    questions_repository.insert({
        "id": qid,
        "subject": subject,
        "topic": topic,
        "bloom_level": "UNDERSTAND",
        "difficulty": "medium",
        "question_type": "multiple-choice",
        "marks": 2,
        "question_en": "What is 2+2?",
        "question_ur": None,
        "options_en": json.dumps(["3", "4", "5", "6"]),
        "options_ur": "[]",
        "correct_answer_en": "4",
        "correct_answer_ur": None,
        "explanation_en": None,
        "explanation_ur": None,
        "visual_emoji": None,
        "visual_count": None,
    })
    return qid


# ---- POST /api/bank/questions -----------------------------------------------

class TestCreateManualQuestion:
    def test_save_english_mcq(self, client):
        res = client.post("/api/bank/questions", json={
            "question_text": "Which planet is closest to the Sun?",
            "is_urdu": False,
            "question_type": "multiple-choice",
            "options": ["Mercury", "Venus", "Earth", "Mars"],
            "correct_answer": "Mercury",
            "marks": 1,
            "subject": "Science",
            "topic": "Solar System",
        })
        assert res.status_code == 201
        data = res.json()
        assert data["question_en"] == "Which planet is closest to the Sun?"
        assert data["question_ur"] is None
        assert data["source"] == "manual"
        assert data["question_type"] == "multiple-choice"

    def test_save_urdu_question(self, client):
        res = client.post("/api/bank/questions", json={
            "question_text": "اسلام کے پانچ ارکان کیا ہیں؟",
            "is_urdu": True,
            "question_type": "short-answer",
            "marks": 3,
            "subject": "Islamiat",
            "topic": "Arkan-e-Islam",
        })
        assert res.status_code == 201
        data = res.json()
        assert data["question_ur"] == "اسلام کے پانچ ارکان کیا ہیں؟"
        assert data["question_en"] is None
        assert data["source"] == "manual"

    def test_save_fill_blank(self, client):
        res = client.post("/api/bank/questions", json={
            "question_text": "The capital of Pakistan is ___.",
            "is_urdu": False,
            "question_type": "fill-blank",
            "correct_answer": "Islamabad",
            "marks": 1,
            "subject": "General Knowledge",
            "topic": "Capitals",
        })
        assert res.status_code == 201
        assert res.json()["question_type"] == "fill-blank"
        assert res.json()["source"] == "manual"

    def test_save_true_false(self, client):
        res = client.post("/api/bank/questions", json={
            "question_text": "The Earth revolves around the Moon.",
            "is_urdu": False,
            "question_type": "true-false",
            "correct_answer": "False",
            "marks": 1,
            "subject": "Science",
            "topic": "Solar System",
        })
        assert res.status_code == 201
        assert res.json()["question_type"] == "true-false"

    def test_mcq_requires_at_least_2_options(self, client):
        res = client.post("/api/bank/questions", json={
            "question_text": "Choose one:",
            "question_type": "multiple-choice",
            "options": ["Only option"],
            "subject": "Science",
            "topic": "Physics",
        })
        assert res.status_code == 422

    def test_mcq_options_max_4(self, client):
        res = client.post("/api/bank/questions", json={
            "question_text": "Choose:",
            "question_type": "multiple-choice",
            "options": ["A", "B", "C", "D", "E"],
            "subject": "Science",
            "topic": "Physics",
        })
        assert res.status_code == 422

    def test_mcq_correct_answer_must_be_in_options(self, client):
        res = client.post("/api/bank/questions", json={
            "question_text": "Pick:",
            "question_type": "multiple-choice",
            "options": ["A", "B", "C"],
            "correct_answer": "D",
            "subject": "Science",
            "topic": "Physics",
        })
        assert res.status_code == 422

    def test_subject_and_topic_required_without_syllabus_id(self, client):
        res = client.post("/api/bank/questions", json={
            "question_text": "Some question",
            "question_type": "short-answer",
            # no subject, no topic, no syllabus_topic_id
        })
        assert res.status_code == 422

    def test_manual_questions_appear_in_list(self, client):
        client.post("/api/bank/questions", json={
            "question_text": "Unique bank question XYZ",
            "question_type": "short-answer",
            "subject": "History",
            "topic": "Mughal Era",
        })
        res = client.get("/api/questions?subject=History&topic=Mughal Era")
        assert res.status_code == 200
        questions = res.json()
        assert any("Unique bank question XYZ" in (q.get("question_en") or "") for q in questions)


# ---- PATCH /api/bank/questions/{id} -----------------------------------------

class TestUpdateManualQuestion:
    def test_update_question_text(self, client, test_db):
        create = client.post("/api/bank/questions", json={
            "question_text": "Old question text",
            "question_type": "short-answer",
            "subject": "Math",
            "topic": "Algebra",
        })
        qid = create.json()["id"]
        res = client.patch(f"/api/bank/questions/{qid}", json={"question_text": "Updated text"})
        assert res.status_code == 200
        assert res.json()["question_en"] == "Updated text"

    def test_update_marks(self, client):
        create = client.post("/api/bank/questions", json={
            "question_text": "Some question",
            "question_type": "short-answer",
            "marks": 2,
            "subject": "Math",
            "topic": "Algebra",
        })
        qid = create.json()["id"]
        res = client.patch(f"/api/bank/questions/{qid}", json={"marks": 5})
        assert res.status_code == 200
        assert res.json()["marks"] == 5

    def test_cannot_edit_gemini_question(self, client, test_db):
        qid = _insert_gemini_question()
        res = client.patch(f"/api/bank/questions/{qid}", json={"question_text": "Hacked"})
        assert res.status_code == 404

    def test_update_nonexistent_returns_404(self, client):
        res = client.patch("/api/bank/questions/no-such-id", json={"marks": 3})
        assert res.status_code == 404

    def test_empty_body_returns_422(self, client):
        create = client.post("/api/bank/questions", json={
            "question_text": "Q",
            "question_type": "short-answer",
            "subject": "Math",
            "topic": "Algebra",
        })
        qid = create.json()["id"]
        res = client.patch(f"/api/bank/questions/{qid}", json={})
        assert res.status_code == 422


# ---- DELETE /api/bank/questions/{id} ----------------------------------------

class TestDeleteManualQuestion:
    def test_delete_manual_question(self, client, test_db):
        create = client.post("/api/bank/questions", json={
            "question_text": "Delete me",
            "question_type": "short-answer",
            "subject": "Math",
            "topic": "Algebra",
        })
        qid = create.json()["id"]
        res = client.delete(f"/api/bank/questions/{qid}")
        assert res.status_code == 200
        assert res.json()["status"] == "ok"
        assert questions_repository.find_by_id(qid) is None

    def test_cannot_delete_gemini_question(self, client, test_db):
        qid = _insert_gemini_question()
        res = client.delete(f"/api/bank/questions/{qid}")
        assert res.status_code == 404
        assert questions_repository.find_by_id(qid) is not None

    def test_delete_nonexistent_returns_404(self, client):
        res = client.delete("/api/bank/questions/no-such-id")
        assert res.status_code == 404
