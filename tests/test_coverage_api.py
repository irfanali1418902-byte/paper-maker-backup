"""Coverage HTTP routes — Hissa 3. Status codes + basic shape."""

from fastapi.testclient import TestClient

from app.main import app
from app.repositories import (
    papers_repository,
    question_slo_repository,
    questions_repository,
    settings_repository,
    slo_exam_plan_repository,
    slo_repository,
)

CLASS = "C1"
SUBJECT = "Math"


def _set_n(n: int) -> None:
    settings_repository.upsert(
        school_name="T", school_name_ur="", address="", address_ur="",
        logo_base64=None, accent_color="#000", exam_count=n,
    )


def _seed_one_covered(exam_no: int = 3) -> None:
    slo_repository.insert({
        "id": "s1", "class": CLASS, "subject": SUBJECT, "slo_code": "M-01",
        "slo_text": "o1", "bloom_level": None, "strand": "N", "sequence": 1,
    })
    slo_exam_plan_repository.overwrite_assignments(
        [{"slo_id": "s1", "exam_no": exam_no, "position": None}]
    )
    questions_repository.insert({
        "id": "q1", "subject": SUBJECT, "topic": "t", "bloom_level": "REMEMBER",
        "difficulty": "easy", "question_type": "multiple-choice", "marks": 1,
        "question_en": "q", "question_ur": None, "options_en": "[]", "options_ur": "[]",
        "correct_answer_en": None, "correct_answer_ur": None,
        "explanation_en": None, "explanation_ur": None,
        "visual_emoji": None, "visual_count": None,
    })
    question_slo_repository.replace_for_question("q1", ["s1"])
    papers_repository.insert(
        paper_id="pA", subject=SUBJECT, class_name=CLASS, total_marks=1,
        question_ids=["q1"], paper_title="pA", exam_no=exam_no,
    )


def test_coverage_ok(test_db):
    _set_n(4)
    _seed_one_covered(3)
    client = TestClient(app)
    resp = client.get("/api/coverage", params={"class_name": CLASS, "subject": SUBJECT, "exam_no": 3})
    assert resp.status_code == 200
    data = resp.json()
    assert data["planned_count"] == 1
    assert data["covered_count"] == 1
    assert data["exam_no"] == 3


def test_coverage_blank_class_400(test_db):
    _set_n(4)
    client = TestClient(app)
    resp = client.get("/api/coverage", params={"class_name": " ", "subject": SUBJECT, "exam_no": 3})
    assert resp.status_code == 400


def test_coverage_exam_no_above_n_400(test_db):
    _set_n(4)
    client = TestClient(app)
    resp = client.get("/api/coverage", params={"class_name": CLASS, "subject": SUBJECT, "exam_no": 9})
    assert resp.status_code == 400


def test_coverage_exam_no_zero_400(test_db):
    """Detail sirf 1..N ke liye — 0 (Unassigned) yahan 400 (summary mein aata hai)."""
    _set_n(4)
    client = TestClient(app)
    resp = client.get("/api/coverage", params={"class_name": CLASS, "subject": SUBJECT, "exam_no": 0})
    assert resp.status_code == 400


def test_coverage_summary_ok(test_db):
    _set_n(4)
    _seed_one_covered(3)
    client = TestClient(app)
    resp = client.get("/api/coverage-summary", params={"class_name": CLASS, "subject": SUBJECT})
    assert resp.status_code == 200
    data = resp.json()
    by_exam = {e["exam_no"]: (e["planned_count"], e["covered_count"]) for e in data["exams"]}
    assert by_exam[3] == (1, 1)
    assert 0 in by_exam  # Unassigned column shamil


def test_coverage_summary_blank_subject_400(test_db):
    _set_n(4)
    client = TestClient(app)
    resp = client.get("/api/coverage-summary", params={"class_name": CLASS, "subject": " "})
    assert resp.status_code == 400
