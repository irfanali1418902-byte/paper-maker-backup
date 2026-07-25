"""GET /api/coverage + /api/coverage-summary — Marhala 5.

TestClient in-process; conftest `test_db` fixture DB inject karta hai. Tests mein
PAPER_MAKER_API_KEY unset => endpoints unprotected, is liye koi auth header nahi
(sibling test_slo_coverage_api jaisa).
"""

import json
import uuid

from fastapi.testclient import TestClient

from app.main import app
from app.repositories import (
    papers_repository,
    questions_repository,
    slo_exam_plan_repository,
    slo_repository,
)

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


# --- Marhala 6a gap-guard: blueprint path exam_no threading ---

def _insert_q(subject="Science", qtype="multiple-choice") -> str:
    qid = str(uuid.uuid4())
    questions_repository.insert({
        "id": qid, "subject": subject, "topic": "Test Topic",
        "bloom_level": "UNDERSTAND", "difficulty": "medium",
        "question_type": qtype, "marks": 1,
        "question_en": f"Q {qid[:6]}?", "question_ur": None,
        "options_en": json.dumps(["A", "B", "C", "D"]), "options_ur": "[]",
        "correct_answer_en": "A", "correct_answer_ur": None,
        "explanation_en": None, "explanation_ur": None,
        "visual_emoji": None, "visual_count": None,
        "syllabus_topic_id": None, "source": "manual", "status": "published",
    })
    return qid


def test_blueprint_paper_persists_exam_no(test_db):
    """Marhala 6a gap-guard: blueprint se bana paper exam_no ke saath PERSIST ho —
    poori chain schema(BlueprintPaperRequest) -> route(papers.py) -> service
    (assemble_blueprint_paper) -> papers_repository.insert. Pehle exam_no silently
    gir jaata tha (paper hamesha NULL). Ye test us gap ko band rakhta hai."""
    _insert_q(subject="Science", qtype="multiple-choice")
    section = {
        "heading": "Sec A",
        "question_types": ["multiple-choice"],
        "topic_ids": [],
        "count": 1,
        "marks_each": 1,
        "source_filter": "manual",
        "status_filter": "published",
    }
    resp = client.post("/api/blueprint-paper", json={
        "sections_input": [section],
        "subject": "Science",
        "exam_no": 3,
    })
    assert resp.status_code == 200
    pid = resp.json()["paper_id"]
    paper = papers_repository.find_by_id(pid)
    assert paper is not None
    assert paper["exam_no"] == 3      # NULL nahi — gap band
