"""Blueprint Bloom guidance — Marhala 2B (Blueprint-page, soft).

Bloom source = question ka APNA bloom_level. Zyada tar tests pure hain (subject=None
=> koi DB nahi); sirf bank-pointer wala test seeded bank use karta hai.
"""

import pytest
from fastapi.testclient import TestClient

from app.services import blueprint_bloom_guidance_service as guide


def _q(bloom):
    """Minimal question dict — service sirf bloom_level dekhti hai."""
    return {"id": "x", "bloom_level": bloom}


def _rows(g):
    return {r["bloom"]: r for r in g["rows"]}


def _sf(g):
    return {s["bloom"]: s for s in g["shortfalls"]}


# ── mix + empty-bloom ginti ─────────────────────────────────────────────────────

def test_empty_bloom_counted_separately():
    # 3 REMEMBER + 1 None + 1 "" -> with_bloom 3, no_bloom 2; % sirf 3 par.
    qs = [_q("REMEMBER"), _q("REMEMBER"), _q("REMEMBER"), _q(None), _q("")]
    g = guide.compute_bloom_guidance(qs, "Pre Year 1", subject=None)
    assert g["available"] is True
    assert g["total_questions"] == 5
    assert g["with_bloom"] == 3
    assert g["no_bloom"] == 2
    assert _rows(g)["remember"]["actual_percent"] == 100.0  # 3/3, na ke 3/5


def test_bloom_case_insensitive():
    qs = [_q("remember"), _q("REMEMBER"), _q("Remember")]
    g = guide.compute_bloom_guidance(qs, "Pre Year 1", subject=None)
    assert g["with_bloom"] == 3
    assert _rows(g)["remember"]["actual_count"] == 3


def test_unknown_bloom_value_treated_as_no_bloom():
    # taxonomy se bahar ki value -> no_bloom (crash nahi, ginti alag)
    qs = [_q("REMEMBER"), _q("FOOBAR")]
    g = guide.compute_bloom_guidance(qs, "Pre Year 1", subject=None)
    assert g["with_bloom"] == 1
    assert g["no_bloom"] == 1


# ── shortfall detection per class-tier ──────────────────────────────────────────

def test_meets_standard_no_shortfall_pre_primary():
    # 7 remember + 3 understand == Pre-Primary 70/30 -> koi farq nahi
    qs = [_q("REMEMBER")] * 7 + [_q("UNDERSTAND")] * 3
    g = guide.compute_bloom_guidance(qs, "Pre Year 1", subject=None)
    assert g["has_shortfall"] is False
    assert g["shortfalls"] == []
    assert _rows(g)["remember"]["diff"] == 0.0


def test_shortfall_detected_middle():
    # Middle 20/30/30/20; sab remember -> remember +80 (over), baqi under.
    qs = [_q("REMEMBER")] * 10
    g = guide.compute_bloom_guidance(qs, "Class 7", subject=None)
    assert g["group"] == "Middle"
    assert g["has_shortfall"] is True
    sf = _sf(g)
    assert sf["remember"]["direction"] == "over" and sf["remember"]["gap"] == 80.0
    assert sf["understand"]["direction"] == "under" and sf["understand"]["gap"] == 30.0
    assert sf["apply"]["direction"] == "under"
    assert sf["analyze"]["direction"] == "under"


def test_shortfall_detected_matric():
    # Matric R15 U25 A30 An20 E10; 5 apply + 5 analyze:
    #   apply 50% (over 20), analyze 50% (over 30), remember -15, understand -25 (under).
    #   evaluate 0 vs 10 -> diff -10 THEEK 10% -> NOT flagged.
    qs = [_q("APPLY")] * 5 + [_q("ANALYZE")] * 5
    g = guide.compute_bloom_guidance(qs, "Class 9", subject=None)
    assert g["group"] == "Matric"
    sf = _sf(g)
    assert sf["apply"]["direction"] == "over" and sf["apply"]["gap"] == 20.0
    assert sf["understand"]["direction"] == "under" and sf["understand"]["gap"] == 25.0
    assert "evaluate" not in sf  # theek 10% -> warning nahi


# ── boundary: theek 10% farq par warning NAHI ───────────────────────────────────

def test_boundary_exactly_10_no_warning():
    # 6 remember + 4 understand; Pre-Primary 70/30.
    # remember 60% (target 70 -> diff -10), understand 40% (target 30 -> diff +10).
    # Dono THEEK 10% -> koi shortfall nahi (strictly > 10 chahiye).
    qs = [_q("REMEMBER")] * 6 + [_q("UNDERSTAND")] * 4
    g = guide.compute_bloom_guidance(qs, "Pre Year 1", subject=None)
    assert g["has_shortfall"] is False
    r = _rows(g)
    assert r["remember"]["diff"] == -10.0
    assert r["understand"]["diff"] == 10.0


def test_just_over_10_warns():
    # 59 remember + 41 understand (100 q): remember 59 (diff -11), understand 41
    # (diff +11) -> dono flagged.
    qs = [_q("REMEMBER")] * 59 + [_q("UNDERSTAND")] * 41
    g = guide.compute_bloom_guidance(qs, "Pre Year 1", subject=None)
    assert g["has_shortfall"] is True
    assert set(_sf(g)) == {"remember", "understand"}


# ── graceful exits (crash nahi) ─────────────────────────────────────────────────

def test_all_empty_bloom_graceful():
    qs = [_q(None), _q(""), _q(None)]
    g = guide.compute_bloom_guidance(qs, "Pre Year 1", subject=None)
    assert g["available"] is False
    assert g["with_bloom"] == 0
    assert g["no_bloom"] == 3
    assert "Bloom set nahi" in g["message"]
    assert g["has_shortfall"] is False


def test_no_class_graceful():
    g = guide.compute_bloom_guidance([_q("REMEMBER")], None, subject=None)
    assert g["available"] is False
    assert "Class set nahi" in g["message"]


def test_unknown_class_graceful():
    g = guide.compute_bloom_guidance([_q("REMEMBER")], "Class 99", subject=None)
    assert g["available"] is False
    assert "standard define nahi" in g["message"]


def test_empty_question_list_graceful():
    g = guide.compute_bloom_guidance([], "Pre Year 1", subject=None)
    assert g["available"] is False
    assert g["total_questions"] == 0
    assert g["with_bloom"] == 0


# ── bank pointer (under-represented) — seeded DB ────────────────────────────────

def _seed_q(qid, subject, bloom, status="published"):
    from app.repositories import questions_repository
    questions_repository.insert({
        "id": qid, "subject": subject, "topic": "T",
        "bloom_level": bloom, "difficulty": "easy",
        "question_type": "short-answer", "marks": 1,
        "question_en": "Q", "question_ur": None,
        "options_en": "[]", "options_ur": "[]",
        "correct_answer_en": None, "correct_answer_ur": None,
        "explanation_en": None, "explanation_ur": None,
        "visual_emoji": None, "visual_count": None,
        "source": "manual", "status": status,
    })


def test_bank_available_counts_only_published_matching(test_db):
    # Middle standard; paper sab remember -> apply/understand/analyze under.
    # Bank mein 2 published APPLY + 1 draft APPLY (subject Math) -> bank_available 2.
    _seed_q("a1", "Math", "APPLY")
    _seed_q("a2", "Math", "APPLY")
    _seed_q("a3", "Math", "APPLY", status="draft")
    _seed_q("other", "Science", "APPLY")   # doosra subject -> count nahi
    paper_qs = [_q("REMEMBER")] * 5
    g = guide.compute_bloom_guidance(paper_qs, "Class 7", subject="Math")
    assert g["has_shortfall"] is True
    assert _sf(g)["apply"]["bank_available"] == 2


def test_no_bank_pointer_when_subject_none():
    qs = [_q("REMEMBER")] * 5
    g = guide.compute_bloom_guidance(qs, "Class 7", subject=None)
    # under shortfalls to hain, par bank_available key set nahi (subject nahi)
    assert g["has_shortfall"] is True
    assert all("bank_available" not in s for s in g["shortfalls"])


# ── /api/blueprint-paper integration ────────────────────────────────────────────

@pytest.fixture
def client(test_db):
    from app.main import app
    return TestClient(app)


def test_blueprint_paper_returns_bloom_guidance(client):
    # 6 published Math REMEMBER; grade "Class 7" (Middle) -> shortfall guidance.
    for i in range(6):
        _seed_q(f"r{i}", "Math", "REMEMBER")
    res = client.post("/api/blueprint-paper", json={
        "sections_input": [{
            "heading": "A", "question_types": ["short-answer"],
            "topic_ids": [], "count": 6, "marks_each": 1, "source_filter": "manual",
        }],
        "subject": "Math",
        "grade": "Class 7",
    })
    assert res.status_code == 200
    g = res.json()["bloom_guidance"]
    assert g["available"] is True and g["group"] == "Middle"
    assert g["has_shortfall"] is True
    sf = {s["bloom"]: s for s in g["shortfalls"]}
    assert sf["remember"]["direction"] == "over"
    # apply under-represented; bank mein Math APPLY zero -> pointer 0
    assert sf["apply"]["direction"] == "under" and sf["apply"]["bank_available"] == 0


def test_blueprint_paper_guidance_unavailable_without_class(client):
    for i in range(3):
        _seed_q(f"r{i}", "Math", "REMEMBER")
    res = client.post("/api/blueprint-paper", json={
        "sections_input": [{
            "heading": "A", "question_types": ["short-answer"],
            "topic_ids": [], "count": 3, "marks_each": 1, "source_filter": "manual",
        }],
        "subject": "Math",
    })
    assert res.status_code == 200
    g = res.json()["bloom_guidance"]
    assert g["available"] is False and g["has_shortfall"] is False
