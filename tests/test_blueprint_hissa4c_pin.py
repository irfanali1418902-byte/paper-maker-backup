"""Blueprint HISSA 4-C: must-include pinned questions (include_question_ids).

Teacher "questions dikhao" list se question pin karta — backend usay section mein
GUARANTEE karta: pinned pehle, dedup, count ke andar; pinned > count to count barh
jaata. Filter se bahar ka (e.g. draft) bhi pin par aata (must-include override).
TestClient in-process; conftest `test_db` fixture (test_blueprint_hissa3 jaisa)."""

from __future__ import annotations

import json
import uuid

import pytest
from fastapi.testclient import TestClient

from app.repositories import questions_repository


@pytest.fixture
def client(test_db):
    from app.main import app
    return TestClient(app)


def _insert_q(status="published", subject="Science") -> str:
    qid = str(uuid.uuid4())
    questions_repository.insert({
        "id": qid, "subject": subject, "topic": "T", "bloom_level": "UNDERSTAND",
        "difficulty": "medium", "question_type": "multiple-choice", "marks": 1,
        "question_en": f"Q {qid[:6]}?", "question_ur": None,
        "options_en": json.dumps(["A", "B", "C", "D"]), "options_ur": "[]",
        "correct_answer_en": "A", "correct_answer_ur": None,
        "explanation_en": None, "explanation_ur": None,
        "visual_emoji": None, "visual_count": None,
        "syllabus_topic_id": None, "source": "manual", "status": status,
    })
    return qid


def _section(count=3, pins=None, status_filter="published") -> dict:
    s = {
        "heading": "Sec A", "question_types": ["multiple-choice"], "topic_ids": [],
        "count": count, "marks_each": 1, "source_filter": "manual",
        "status_filter": status_filter,
    }
    if pins is not None:
        s["include_question_ids"] = pins
    return s


def _post(client, section, subject="Science"):
    return client.post("/api/blueprint-paper", json={
        "sections_input": [section], "subject": subject,
    })


def test_pinned_guaranteed_first_within_count(client):
    """Draft pinned question published-only section mein bhi aaye (must-include),
    PEHLI jagah, aur total == count (pinned + filler)."""
    f1 = _insert_q(status="published")
    f2 = _insert_q(status="published")
    f3 = _insert_q(status="published")
    target = _insert_q(status="draft")  # filter kabhi na le (published-only section)

    res = _post(client, _section(count=3, pins=[target]))
    assert res.status_code == 200
    ids = [q["id"] for q in res.json()["questions"]]
    assert len(ids) == 3
    assert ids[0] == target                        # pinned pehle
    assert set(ids[1:]).issubset({f1, f2, f3})     # baqi published filler se


def test_pinned_dedup_no_duplicate(client):
    """Pin list mein duplicate + filter-pool ka wahi question → sirf ek baar."""
    q1 = _insert_q(status="published")
    _insert_q(status="published")
    _insert_q(status="published")

    res = _post(client, _section(count=3, pins=[q1, q1]))  # duplicate; q1 pool mein bhi
    assert res.status_code == 200
    ids = [q["id"] for q in res.json()["questions"]]
    assert ids.count(q1) == 1
    assert len(ids) == len(set(ids)) == 3
    assert ids[0] == q1


def test_pinned_over_count_expands(client):
    """Pinned (3) > count (2) → count inhi tak barh jaaye, saare pinned present."""
    p1 = _insert_q(status="draft")
    p2 = _insert_q(status="draft")
    p3 = _insert_q(status="draft")

    res = _post(client, _section(count=2, pins=[p1, p2, p3]))
    assert res.status_code == 200
    ids = [q["id"] for q in res.json()["questions"]]
    assert len(ids) == 3
    assert set(ids) == {p1, p2, p3}


def test_nonexistent_pin_skipped(client):
    """Ghair-maujood id chup-chaap skip; valid pin phir bhi aaye, koi crash nahi."""
    target = _insert_q(status="draft")
    _insert_q(status="published")

    res = _post(client, _section(count=2, pins=["does-not-exist", target]))
    assert res.status_code == 200
    ids = [q["id"] for q in res.json()["questions"]]
    assert ids[0] == target
    assert "does-not-exist" not in ids


def test_no_pins_unchanged(client):
    """Koi pin na ho → purana rawaiyya bilkul waisa (backward-compat)."""
    _insert_q(status="published")
    _insert_q(status="published")
    res = _post(client, _section(count=5))  # no include_question_ids key
    assert res.status_code == 200
    assert len(res.json()["questions"]) == 2


# ── Hissa 4-D: multi-section per-section pin contract (backend already per-section) ──

def test_two_sections_distinct_pins(client):
    """Do sections, har ek ka apna include_question_ids → har pin apni-apni section
    mein aaye, cross-contamination nahi (frontend isi contract par bharosa karta)."""
    _insert_q(status="published")  # filler taake sections khaali na hon
    _insert_q(status="published")
    pin_a = _insert_q(status="draft")  # sirf pin par aayenge (published-only filter se bahar)
    pin_b = _insert_q(status="draft")

    sec_a = _section(count=2, pins=[pin_a])
    sec_b = _section(count=2, pins=[pin_b])
    sec_b["heading"] = "Sec B"

    res = client.post("/api/blueprint-paper", json={
        "sections_input": [sec_a, sec_b], "subject": "Science",
    })
    assert res.status_code == 200
    meta = res.json()["sections_meta"]
    assert len(meta) == 2
    assert pin_a in meta[0]["question_ids"]
    assert pin_b in meta[1]["question_ids"]


def test_pin_only_in_its_section(client):
    """Section A ka pin section B mein na aaye (aur ulta)."""
    pin_a = _insert_q(status="draft")
    pin_b = _insert_q(status="draft")

    sec_a = _section(count=1, pins=[pin_a])
    sec_b = _section(count=1, pins=[pin_b])
    sec_b["heading"] = "Sec B"

    res = client.post("/api/blueprint-paper", json={
        "sections_input": [sec_a, sec_b], "subject": "Science",
    })
    assert res.status_code == 200
    meta = res.json()["sections_meta"]
    assert pin_a not in meta[1]["question_ids"]
    assert pin_b not in meta[0]["question_ids"]
