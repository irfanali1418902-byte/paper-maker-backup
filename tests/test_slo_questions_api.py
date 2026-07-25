"""GET /api/slo/{slo_id}/questions — Hissa 4-B (blueprint "questions dikhao").

Read-only route: ek SLO se tagged saare questions (published + draft dono, koi status
filter nahi). Minimal fields. TestClient in-process; conftest `test_db` fixture DB deta
(test_coverage_api jaisa — koi auth header nahi kyunki API key unset)."""

import json
import uuid

from fastapi.testclient import TestClient

from app.main import app
from app.repositories import (
    question_slo_repository,
    questions_repository,
    slo_repository,
)

client = TestClient(app)


def _slo(slo_id: str, code: str) -> None:
    slo_repository.insert({
        "id": slo_id, "class": "Pre Year 1", "subject": "Mathematics",
        "slo_code": code, "slo_text": f"Outcome {code}",
        "bloom_level": None, "strand": "Number",
    })


def _insert_q(status="published") -> str:
    qid = str(uuid.uuid4())
    questions_repository.insert({
        "id": qid, "subject": "Mathematics", "topic": "Test Topic",
        "bloom_level": "UNDERSTAND", "difficulty": "medium",
        "question_type": "multiple-choice", "marks": 1,
        "question_en": f"Q {qid[:6]}?", "question_ur": None,
        "options_en": json.dumps(["A", "B", "C", "D"]), "options_ur": "[]",
        "correct_answer_en": "A", "correct_answer_ur": None,
        "explanation_en": None, "explanation_ur": None,
        "visual_emoji": None, "visual_count": None,
        "syllabus_topic_id": None, "source": "manual", "status": status,
    })
    return qid


def test_returns_published_and_draft_tagged(test_db):
    """Tagged questions dono halaat (published + draft) mein aayein — koi status
    filter nahi. Minimal fields aur untagged question shamil na ho."""
    _slo("slo-a", "MATH-01")
    qpub = _insert_q(status="published")
    qdraft = _insert_q(status="draft")
    _untagged = _insert_q(status="published")  # is SLO se link NAHI — nahi aana chahiye

    question_slo_repository.replace_for_question(qpub, ["slo-a"])
    question_slo_repository.replace_for_question(qdraft, ["slo-a"])

    resp = client.get("/api/slo/slo-a/questions")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 2
    ids = {q["id"] for q in data["questions"]}
    assert ids == {qpub, qdraft}          # untagged bahar
    statuses = {q["status"] for q in data["questions"]}
    assert statuses == {"published", "draft"}   # dono halaat
    # Minimal shape — poora row nahi
    assert set(data["questions"][0].keys()) == {"id", "question_en", "status", "bloom_level"}


def test_unknown_slo_empty_list(test_db):
    """SLO ka wajood check nahi — koi question na ho to 200 + khali list (error nahi)."""
    resp = client.get("/api/slo/does-not-exist/questions")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 0
    assert data["questions"] == []
