"""GET /api/paper/{id}/slo-coverage — Marhala 2 Hissa A."""

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
        "bloom_level": "REMEMBER", "difficulty": "easy",
        "question_type": "short-answer", "marks": 1,
        "question_en": "Q", "question_ur": None,
        "options_en": "[]", "options_ur": "[]",
        "correct_answer_en": None, "correct_answer_ur": None,
        "explanation_en": None, "explanation_ur": None,
        "visual_emoji": None, "visual_count": None,
    })


def _slo(slo_id: str, code: str, strand: str = "Number") -> None:
    slo_repository.insert({
        "id": slo_id, "class": "Pre Year 1", "subject": "Mathematics",
        "slo_code": code, "slo_text": f"Outcome {code}",
        "bloom_level": None, "strand": strand,
    })


def test_coverage_endpoint_shape(test_db):
    _q("q1")
    _q("q2")
    _slo("s1", "MATH-01")
    _slo("s2", "MATH-02")
    question_slo_repository.replace_for_question("q1", ["s1"])
    papers_repository.insert("p1", "Mathematics", "Pre Year 1", 2, ["q1", "q2"])

    resp = client.get("/api/paper/p1/slo-coverage")
    assert resp.status_code == 200
    data = resp.json()
    assert data["paper_id"] == "p1"
    assert data["universe_available"] is True
    assert data["total_slos"] == 2
    assert data["coverage_percent"] == 50
    assert data["untagged_questions"] == 1
    assert [r["slo_code"] for r in data["remaining"]] == ["MATH-02"]


def test_coverage_unknown_paper_404(test_db):
    resp = client.get("/api/paper/ghost/slo-coverage")
    assert resp.status_code == 404


def test_coverage_old_paper_no_links(test_db):
    """Purana paper (koi SLO link nahi) na toote — 200, 0 coverage."""
    _q("q1")
    _slo("s1", "MATH-01")
    papers_repository.insert("p1", "Mathematics", "Pre Year 1", 1, ["q1"])
    resp = client.get("/api/paper/p1/slo-coverage")
    assert resp.status_code == 200
    data = resp.json()
    assert data["coverage_percent"] == 0
    assert data["untagged_questions"] == 1
    assert data["covered_slos"] == 0
