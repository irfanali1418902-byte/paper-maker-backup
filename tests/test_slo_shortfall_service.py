"""Paper Bloom shortfall service — Marhala 2 Hissa B.

Seed-based — koi hardcoded bank-count nahi; har test apna paper/SLO banata aur
usi seed ki reasoning se assert karta hai.
"""

from app.repositories import (
    papers_repository,
    question_slo_repository,
    questions_repository,
    slo_repository,
)
from app.services import slo_shortfall_service
from app.services.slo_shortfall_service import _largest_remainder


def _q(qid: str) -> None:
    questions_repository.insert({
        "id": qid, "subject": "Mathematics", "topic": "Counting",
        "bloom_level": "APPLY", "difficulty": "easy",  # question ka apna bloom — IGNORE hona chahiye
        "question_type": "short-answer", "marks": 1,
        "question_en": "Q", "question_ur": None,
        "options_en": "[]", "options_ur": "[]",
        "correct_answer_en": None, "correct_answer_ur": None,
        "explanation_en": None, "explanation_ur": None,
        "visual_emoji": None, "visual_count": None,
    })


def _slo(slo_id: str, code: str, bloom, cls="Pre Year 1") -> None:
    slo_repository.insert({
        "id": slo_id, "class": cls, "subject": "Mathematics",
        "slo_code": code, "slo_text": f"Outcome {code}",
        "bloom_level": bloom, "strand": "Number",
    })


def _paper(pid: str, qids: list, class_name="Pre Year 1") -> None:
    papers_repository.insert(pid, "Mathematics", class_name, len(qids), qids)


def _tagged(qid: str, bloom, cls="Pre Year 1") -> None:
    """Ek classifiable question: question + ek SLO (diya bloom) + link."""
    _q(qid)
    _slo(f"s_{qid}", f"C-{qid}", bloom, cls=cls)
    question_slo_repository.replace_for_question(qid, [f"s_{qid}"])


def _rows_by_bloom(sf: dict) -> dict:
    return {r["bloom"]: r for r in sf["bloom_rows"]}


# ── largest-remainder helper (sum property) ─────────────────────────────────────

def test_largest_remainder_sums_to_total():
    d = {"remember": 70, "understand": 30, "apply": 0}
    for n in (0, 1, 3, 5, 7, 10, 13, 24):
        got = _largest_remainder(d, n)
        assert sum(got.values()) == n
    assert _largest_remainder(d, 10) == {"remember": 7, "understand": 3, "apply": 0}


# ── graceful exits ──────────────────────────────────────────────────────────────

def test_paper_not_found_returns_none(test_db):
    assert slo_shortfall_service.compute_shortfall("ghost") is None


def test_no_class_graceful(test_db):
    _tagged("q1", "remember")
    papers_repository.insert("p1", "Mathematics", None, 1, ["q1"])
    sf = slo_shortfall_service.compute_shortfall("p1")
    assert sf["distribution_available"] is False
    assert "class" in sf["message"].lower()


def test_unknown_class_graceful(test_db):
    _tagged("q1", "remember", cls="Class 99")
    _paper("p1", ["q1"], class_name="Class 99")
    sf = slo_shortfall_service.compute_shortfall("p1")
    assert sf["distribution_available"] is False


def test_all_untagged_graceful_not_zero_panel(test_db):
    _q("q1")
    _q("q2")
    _paper("p1", ["q1", "q2"])  # koi SLO tag nahi
    sf = slo_shortfall_service.compute_shortfall("p1")
    assert sf["distribution_available"] is False
    assert sf["classifiable_questions"] == 0
    assert sf["untagged_questions"] == 2
    assert "tagged nahi" in sf["message"]


# ── happy path ──────────────────────────────────────────────────────────────────

def test_meets_standard_no_shortfall(test_db):
    # 10 classifiable: 7 remember + 3 understand == Pre-Primary 70/30 -> koi kami nahi
    for i in range(7):
        _tagged(f"r{i}", "remember")
    for i in range(3):
        _tagged(f"u{i}", "understand")
    _paper("p1", [f"r{i}" for i in range(7)] + [f"u{i}" for i in range(3)])
    sf = slo_shortfall_service.compute_shortfall("p1")
    assert sf["distribution_available"] is True
    assert sf["group"] == "Pre-Primary"
    assert sf["classifiable_questions"] == 10
    assert sf["total_short"] == 0
    rows = _rows_by_bloom(sf)
    assert rows["remember"]["needed"] == 7 and rows["remember"]["actual"] == 7
    assert rows["understand"]["needed"] == 3 and rows["understand"]["actual"] == 3


def test_shortfall_detected(test_db):
    # 10 classifiable: 5 remember + 5 understand. Target 7/3 -> remember short 2.
    for i in range(5):
        _tagged(f"r{i}", "remember")
    for i in range(5):
        _tagged(f"u{i}", "understand")
    _paper("p1", [f"r{i}" for i in range(5)] + [f"u{i}" for i in range(5)])
    sf = slo_shortfall_service.compute_shortfall("p1")
    rows = _rows_by_bloom(sf)
    assert rows["remember"] == {"bloom": "remember", "needed": 7, "actual": 5, "short": 2}
    assert rows["understand"]["short"] == 0  # need 3, have 5
    assert sf["total_short"] == 2


# ── decisions: case, multi-SLO, untagged vs unknown, off-target ─────────────────

def test_bloom_case_insensitive(test_db):
    # SLO bloom UPPER-case 'REMEMBER' phir bhi remember gina jaye (warna ginti 0)
    _tagged("q1", "REMEMBER")
    _paper("p1", ["q1"])
    sf = slo_shortfall_service.compute_shortfall("p1")
    assert sf["classifiable_questions"] == 1
    assert _rows_by_bloom(sf)["remember"]["actual"] == 1


def test_multi_slo_uses_highest(test_db):
    # q1 -> remember + understand SLO. Highest = understand. multi_slo flag set.
    _q("q1")
    _slo("s_r", "N-1", "remember")
    _slo("s_u", "N-2", "understand")
    question_slo_repository.replace_for_question("q1", ["s_r", "s_u"])
    _paper("p1", ["q1"])
    sf = slo_shortfall_service.compute_shortfall("p1")
    rows = _rows_by_bloom(sf)
    assert rows["understand"]["actual"] == 1
    assert rows.get("remember", {"actual": 0})["actual"] == 0  # remember count nahi hua
    assert sf["multi_slo_questions"] == 1
    assert sf["classifiable_questions"] == 1  # ek hi question


def test_untagged_and_bloom_unknown_counted_separately(test_db):
    _tagged("q_ok", "remember")
    _q("q_untagged")                       # koi SLO link nahi
    _q("q_unknown")                        # SLO tagged par bloom NULL
    _slo("s0", "N-0", None)
    question_slo_repository.replace_for_question("q_unknown", ["s0"])
    _paper("p1", ["q_ok", "q_untagged", "q_unknown"])
    sf = slo_shortfall_service.compute_shortfall("p1")
    assert sf["classifiable_questions"] == 1
    assert sf["untagged_questions"] == 1
    assert sf["bloom_unknown_questions"] == 1


def test_off_target_bloom_shown_with_zero_need(test_db):
    # apply-SLO question — Pre-Primary target apply=0; row dikhe (needed 0, actual 1, short 0)
    _tagged("q1", "apply")
    _paper("p1", ["q1"])
    sf = slo_shortfall_service.compute_shortfall("p1")
    rows = _rows_by_bloom(sf)
    assert "apply" in rows
    assert rows["apply"]["needed"] == 0 and rows["apply"]["actual"] == 1
    assert rows["apply"]["short"] == 0
