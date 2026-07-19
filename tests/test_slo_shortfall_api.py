"""GET /api/paper/{id}/bloom-shortfall — Marhala 2 Hissa B."""

from fastapi.testclient import TestClient

from app.main import app
from app.repositories import (
    papers_repository,
    question_slo_repository,
    questions_repository,
    slo_repository,
)

client = TestClient(app)


def _q(qid: str) -> None:
    questions_repository.insert({
        "id": qid, "subject": "Mathematics", "topic": "Counting",
        "bloom_level": "APPLY", "difficulty": "easy",
        "question_type": "short-answer", "marks": 1,
        "question_en": "Q", "question_ur": None,
        "options_en": "[]", "options_ur": "[]",
        "correct_answer_en": None, "correct_answer_ur": None,
        "explanation_en": None, "explanation_ur": None,
        "visual_emoji": None, "visual_count": None,
    })


def _slo(slo_id: str, code: str, bloom: str) -> None:
    slo_repository.insert({
        "id": slo_id, "class": "Pre Year 1", "subject": "Mathematics",
        "slo_code": code, "slo_text": f"Outcome {code}",
        "bloom_level": bloom, "strand": "Number",
    })


def test_bloom_shortfall_endpoint_shape(test_db):
    _q("q1")
    _q("q2")
    _slo("s1", "N-1", "remember")
    _slo("s2", "N-2", "remember")
    question_slo_repository.replace_for_question("q1", ["s1"])
    question_slo_repository.replace_for_question("q2", ["s2"])
    papers_repository.insert("p1", "Mathematics", "Pre Year 1", 2, ["q1", "q2"])

    resp = client.get("/api/paper/p1/bloom-shortfall")
    assert resp.status_code == 200
    data = resp.json()
    assert data["distribution_available"] is True
    assert data["group"] == "Pre-Primary"
    assert data["classifiable_questions"] == 2
    # 2 remember, target 70/30 of 2 -> remember 1, understand 1 -> understand short 1
    rows = {r["bloom"]: r for r in data["bloom_rows"]}
    assert rows["understand"]["short"] == 1
    assert data["total_short"] == 1


def test_bloom_shortfall_404(test_db):
    assert client.get("/api/paper/ghost/bloom-shortfall").status_code == 404
