"""Question <-> SLO link API — Marhala 1.

GET/PUT /api/questions/{id}/slo, aur manual create/update mein slo_ids.
"""

import json

from fastapi.testclient import TestClient

from app.main import app
from app.repositories import questions_repository, slo_repository

client = TestClient(app)


def _make_slo(slo_id: str, code: str, strand: str = "Number") -> None:
    slo_repository.insert({
        "id": slo_id,
        "class": "Pre Year 1",
        "subject": "Mathematics",
        "slo_code": code,
        "slo_text": f"Outcome {code}",
        "bloom_level": None,
        "strand": strand,
    })


def _make_gemini_question(qid: str = "g1") -> None:
    """Seedha DB mein gemini (protected) question — source default 'gemini'."""
    questions_repository.insert({
        "id": qid,
        "subject": "Mathematics",
        "topic": "Counting",
        "bloom_level": "REMEMBER",
        "difficulty": "easy",
        "question_type": "multiple-choice",
        "marks": 1,
        "question_en": "2+2?",
        "question_ur": None,
        "options_en": json.dumps(["3", "4"]),
        "options_ur": "[]",
        "correct_answer_en": "4",
        "correct_answer_ur": None,
        "explanation_en": None,
        "explanation_ur": None,
        "visual_emoji": None,
        "visual_count": None,
    })


def _create_manual(slo_ids=None) -> str:
    body = {
        "question_text": "Count to 10",
        "question_type": "short-answer",
        "subject": "Mathematics",
        "topic": "Counting",
    }
    if slo_ids is not None:
        body["slo_ids"] = slo_ids
    resp = client.post("/api/bank/questions", json=body)
    assert resp.status_code == 201, resp.text
    return resp.json()["id"]


# ── PUT + GET on any question ────────────────────────────────────────────────

def test_put_then_get(test_db):
    _make_slo("s1", "MATH-01")
    _make_slo("s2", "MATH-02")
    qid = _create_manual()

    resp = client.put(f"/api/questions/{qid}/slo", json={"slo_ids": ["s1", "s2"]})
    assert resp.status_code == 200
    assert resp.json()["total"] == 2

    resp = client.get(f"/api/questions/{qid}/slo")
    assert resp.status_code == 200
    codes = [s["slo_code"] for s in resp.json()["slos"]]
    assert codes == ["MATH-01", "MATH-02"]


def test_put_replace_set(test_db):
    _make_slo("s1", "MATH-01")
    _make_slo("s2", "MATH-02")
    qid = _create_manual()
    client.put(f"/api/questions/{qid}/slo", json={"slo_ids": ["s1", "s2"]})
    client.put(f"/api/questions/{qid}/slo", json={"slo_ids": ["s2"]})  # replace
    resp = client.get(f"/api/questions/{qid}/slo")
    assert [s["id"] for s in resp.json()["slos"]] == ["s2"]


def test_put_empty_clears(test_db):
    _make_slo("s1", "MATH-01")
    qid = _create_manual(slo_ids=["s1"])
    client.put(f"/api/questions/{qid}/slo", json={"slo_ids": []})
    assert client.get(f"/api/questions/{qid}/slo").json()["total"] == 0


def test_gemini_question_can_be_tagged(test_db):
    """Gemini (protected) question bhi tag ho — link table uske row ko nahi chhoota."""
    _make_slo("s1", "MATH-01")
    _make_gemini_question("g1")
    resp = client.put("/api/questions/g1/slo", json={"slo_ids": ["s1"]})
    assert resp.status_code == 200
    assert resp.json()["total"] == 1


def test_unknown_slo_id_filtered(test_db):
    _make_slo("s1", "MATH-01")
    qid = _create_manual()
    resp = client.put(f"/api/questions/{qid}/slo", json={"slo_ids": ["s1", "ghost"]})
    assert resp.json()["total"] == 1  # ghost link nahi bana


def test_put_unknown_question_404(test_db):
    resp = client.put("/api/questions/nope/slo", json={"slo_ids": []})
    assert resp.status_code == 404


def test_get_unknown_question_404(test_db):
    resp = client.get("/api/questions/nope/slo")
    assert resp.status_code == 404


# ── manual create/update carry slo_ids ───────────────────────────────────────

def test_manual_create_with_slo_ids(test_db):
    _make_slo("s1", "MATH-01")
    qid = _create_manual(slo_ids=["s1"])
    assert client.get(f"/api/questions/{qid}/slo").json()["total"] == 1


def test_manual_create_without_slo_ids_has_none(test_db):
    """Purane raste se banaya question (bina slo_ids) — bilkul un-linked."""
    qid = _create_manual()
    assert client.get(f"/api/questions/{qid}/slo").json()["total"] == 0


def test_manual_update_replaces_slo_ids(test_db):
    _make_slo("s1", "MATH-01")
    _make_slo("s2", "MATH-02")
    qid = _create_manual(slo_ids=["s1"])
    resp = client.patch(f"/api/bank/questions/{qid}", json={"slo_ids": ["s2"]})
    assert resp.status_code == 200
    got = client.get(f"/api/questions/{qid}/slo").json()
    assert [s["id"] for s in got["slos"]] == ["s2"]


def test_manual_update_slo_ids_only_is_valid(test_db):
    """Sirf slo_ids bhejna 'kam az kam ek field' rule pass kare (400 na aaye)."""
    _make_slo("s1", "MATH-01")
    qid = _create_manual()
    resp = client.patch(f"/api/bank/questions/{qid}", json={"slo_ids": ["s1"]})
    assert resp.status_code == 200
