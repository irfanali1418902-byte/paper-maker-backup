"""GET /api/coverage + /api/coverage-summary — Marhala 5.

TestClient in-process; conftest `test_db` fixture DB inject karta hai. Tests mein
PAPER_MAKER_API_KEY unset => endpoints unprotected, is liye koi auth header nahi
(sibling test_slo_coverage_api jaisa).
"""

from fastapi.testclient import TestClient

from app.main import app
from app.repositories import slo_exam_plan_repository, slo_repository

client = TestClient(app)


def _slo(slo_id: str, code: str) -> None:
    slo_repository.insert({
        "id": slo_id, "class": "Pre Year 1", "subject": "Mathematics",
        "slo_code": code, "slo_text": f"Outcome {code}",
        "bloom_level": None, "strand": "Number",
    })


def _plan(slo_id: str, exam_no: int) -> None:
    slo_exam_plan_repository.overwrite_assignments(
        [{"slo_id": slo_id, "exam_no": exam_no, "position": None}]
    )


def test_coverage_summary_200(test_db):
    _slo("s1", "MATH-01")
    _plan("s1", 1)
    resp = client.get(
        "/api/coverage-summary",
        params={"class_name": "Pre Year 1", "subject": "Mathematics"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["class"] == "Pre Year 1"
    assert data["subject"] == "Mathematics"
    assert "exam_count" in data
    assert isinstance(data["exams"], list)
    row1 = next(e for e in data["exams"] if e["exam_no"] == 1)
    assert set(row1.keys()) == {
        "exam_no", "unassigned", "planned", "covered", "coverage_percent"
    }
    assert row1["planned"] == 1


def test_blank_class_400(test_db):
    resp = client.get(
        "/api/coverage-summary",
        params={"class_name": " ", "subject": "Mathematics"},
    )
    assert resp.status_code == 400


def test_exam_no_out_of_range_400(test_db):
    resp = client.get(
        "/api/coverage",
        params={"class_name": "Pre Year 1", "subject": "Mathematics", "exam_no": 99},
    )
    assert resp.status_code == 400
