"""GET /api/slo-health — Marhala 2 Hissa C. Seed-based."""

from fastapi.testclient import TestClient

from app.main import app
from app.repositories import (
    question_slo_repository,
    questions_repository,
    slo_repository,
)

client = TestClient(app)


def _q(qid: str, status: str = "published") -> None:
    questions_repository.insert({
        "id": qid, "subject": "Mathematics", "topic": "Counting",
        "bloom_level": "REMEMBER", "difficulty": "easy",
        "question_type": "short-answer", "marks": 1,
        "question_en": "Q", "question_ur": None,
        "options_en": "[]", "options_ur": "[]",
        "correct_answer_en": None, "correct_answer_ur": None,
        "explanation_en": None, "explanation_ur": None,
        "visual_emoji": None, "visual_count": None, "status": status,
    })


def _slo(sid: str, code: str, cls: str = "Pre Year 1", subject: str = "Mathematics") -> None:
    slo_repository.insert({
        "id": sid, "class": cls, "subject": subject,
        "slo_code": code, "slo_text": f"Outcome {code}",
        "bloom_level": None, "strand": "Number",
    })


def test_health_endpoint_shape(test_db):
    _q("q1")
    _slo("s1", "N-01")            # covered
    _slo("s2", "N-02")            # uncovered
    question_slo_repository.replace_for_question("q1", ["s1"])

    resp = client.get("/api/slo-health")
    assert resp.status_code == 200
    data = resp.json()
    for key in ("draft_note", "classes", "subjects", "health_lines",
                "slos_without_question", "untagged_questions", "import_pending"):
        assert key in data
    line = next(h for h in data["health_lines"]
                if h["norm_class"] == "pre year 1" and h["norm_subject"] == "mathematics")
    assert line["slo_count"] == 2
    assert line["covered_count"] == 1
    assert line["uncovered_count"] == 1


def test_health_filter_param(test_db):
    _slo("s1", "N-01", cls="Pre Year 1", subject="Mathematics")
    _slo("s2", "SCI-01", cls="Grade 7", subject="Science")
    resp = client.get("/api/slo-health", params={"class_name": "Grade 7"})
    assert resp.status_code == 200
    data = resp.json()
    assert {h["norm_class"] for h in data["health_lines"]} == {"grade 7"}
