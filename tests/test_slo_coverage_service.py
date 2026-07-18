"""Paper SLO coverage service — Marhala 2 Hissa A."""

from app.repositories import (
    papers_repository,
    question_slo_repository,
    questions_repository,
    slo_repository,
)
from app.services import slo_coverage_service


def _q(qid: str, subject: str = "Mathematics") -> None:
    questions_repository.insert({
        "id": qid, "subject": subject, "topic": "Counting",
        "bloom_level": "REMEMBER", "difficulty": "easy",
        "question_type": "short-answer", "marks": 1,
        "question_en": "Q", "question_ur": None,
        "options_en": "[]", "options_ur": "[]",
        "correct_answer_en": None, "correct_answer_ur": None,
        "explanation_en": None, "explanation_ur": None,
        "visual_emoji": None, "visual_count": None,
    })


def _slo(slo_id: str, code: str, strand: str = "Number",
         cls: str = "Pre Year 1", subject: str = "Mathematics") -> None:
    slo_repository.insert({
        "id": slo_id, "class": cls, "subject": subject,
        "slo_code": code, "slo_text": f"Outcome {code}",
        "bloom_level": None, "strand": strand,
    })


def _paper(pid: str, qids: list, class_name="Pre Year 1", subject="Mathematics") -> None:
    papers_repository.insert(pid, subject, class_name, len(qids), qids)


def test_paper_not_found_returns_none(test_db):
    assert slo_coverage_service.compute_coverage("ghost") is None


def test_full_coverage_with_universe(test_db):
    _q("q1")
    _q("q2")
    _slo("s1", "MATH-01", "Number")
    _slo("s2", "MATH-02", "Number")
    _slo("s3", "MATH-03", "Shape")
    question_slo_repository.replace_for_question("q1", ["s1"])
    question_slo_repository.replace_for_question("q2", ["s2"])
    _paper("p1", ["q1", "q2"])

    cov = slo_coverage_service.compute_coverage("p1")
    assert cov["universe_available"] is True
    assert cov["total_slos"] == 3
    assert cov["covered_in_universe"] == 2
    assert cov["coverage_percent"] == round(2 / 3 * 100)  # 67
    assert [s["slo_code"] for s in cov["covered"]] == ["MATH-01", "MATH-02"]
    assert [r["slo_code"] for r in cov["remaining"]] == ["MATH-03"]
    assert cov["untagged_questions"] == 0


def test_covered_lists_covering_question_ids(test_db):
    _q("q1")
    _q("q2")
    _slo("s1", "MATH-01")
    question_slo_repository.replace_for_question("q1", ["s1"])
    question_slo_repository.replace_for_question("q2", ["s1"])  # dono ne s1 cover kiya
    _paper("p1", ["q1", "q2"])
    cov = slo_coverage_service.compute_coverage("p1")
    entry = next(s for s in cov["covered"] if s["slo_code"] == "MATH-01")
    assert set(entry["question_ids"]) == {"q1", "q2"}


def test_strand_breakdown(test_db):
    _q("q1")
    _slo("s1", "MATH-N1", "Number")
    _slo("s2", "MATH-N2", "Number")
    _slo("s3", "MATH-S1", "Shape")
    question_slo_repository.replace_for_question("q1", ["s1"])
    _paper("p1", ["q1"])
    cov = slo_coverage_service.compute_coverage("p1")
    by = {s["strand"]: s for s in cov["strands"]}
    assert by["Number"]["total"] == 2 and by["Number"]["covered"] == 1
    assert by["Shape"]["total"] == 1 and by["Shape"]["covered"] == 0
    assert [r["slo_code"] for r in by["Number"]["remaining_list"]] == ["MATH-N2"]


def test_untagged_questions_counted(test_db):
    _q("q1")
    _q("q2")
    _q("q3")
    _slo("s1", "MATH-01")
    question_slo_repository.replace_for_question("q1", ["s1"])
    _paper("p1", ["q1", "q2", "q3"])  # q2, q3 untagged
    cov = slo_coverage_service.compute_coverage("p1")
    assert cov["untagged_questions"] == 2


def test_all_untagged_zero_coverage(test_db):
    _q("q1")
    _q("q2")
    _slo("s1", "MATH-01")  # SLO maujood par kisi sawal se linked nahi
    _paper("p1", ["q1", "q2"])
    cov = slo_coverage_service.compute_coverage("p1")
    assert cov["coverage_percent"] == 0
    assert cov["covered_slos"] == 0
    assert cov["untagged_questions"] == 2
    assert len(cov["remaining"]) == 1


def test_class_name_normalized_match(test_db):
    """paper.class_name 'nursery ' (case+space) SLO.class 'Nursery' se match kare."""
    _q("q1")
    _slo("s1", "NUR-01", cls="Nursery")
    question_slo_repository.replace_for_question("q1", ["s1"])
    _paper("p1", ["q1"], class_name="nursery ")  # gandi value
    cov = slo_coverage_service.compute_coverage("p1")
    assert cov["universe_available"] is True
    assert cov["total_slos"] == 1
    assert cov["coverage_percent"] == 100


def test_no_universe_when_class_none(test_db):
    _q("q1")
    _slo("s1", "MATH-01")
    question_slo_repository.replace_for_question("q1", ["s1"])
    _paper("p1", ["q1"], class_name=None)
    cov = slo_coverage_service.compute_coverage("p1")
    assert cov["universe_available"] is False
    assert cov["coverage_percent"] is None
    assert cov["remaining"] == []
    # covered phir bhi dikhta hai (links se, class par depend nahi)
    assert cov["covered_slos"] == 1
    assert "class set nahi" in cov["universe_message"]


def test_no_universe_when_class_has_no_slo(test_db):
    _q("q1")
    _slo("s1", "MATH-01", cls="Pre Year 1")
    question_slo_repository.replace_for_question("q1", ["s1"])
    _paper("p1", ["q1"], class_name="Pre Year 2")  # is class ki koi SLO nahi
    cov = slo_coverage_service.compute_coverage("p1")
    assert cov["universe_available"] is False
    assert cov["covered_slos"] == 1  # covered phir bhi (cross-class link)
    assert "koi SLO define nahi" in cov["universe_message"]


def test_science_paper_no_slo_graceful(test_db):
    _q("q1", subject="Science")
    _paper("p1", ["q1"], subject="Science")
    cov = slo_coverage_service.compute_coverage("p1")
    assert cov["universe_available"] is False
    assert cov["covered_slos"] == 0
    assert cov["untagged_questions"] == 1
