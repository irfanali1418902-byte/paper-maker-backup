"""Exam coverage service — Hissa 3.

Bunyadi usool ke tests: coverage SIRF usi exam ke papers se ginti hai. Sabse ahem —
doosre exam ke paper mein aaya SLO is exam ke liye covered NAHI.
"""

from app.repositories import (
    papers_repository,
    question_slo_repository,
    questions_repository,
    settings_repository,
    slo_exam_plan_repository,
    slo_repository,
)
from app.services import coverage_service

CLASS = "C1"
SUBJECT = "Math"


def _set_n(n: int) -> None:
    settings_repository.upsert(
        school_name="T", school_name_ur="", address="", address_ur="",
        logo_base64=None, accent_color="#000", exam_count=n,
    )


def _slo(slo_id: str, code: str, exam_no: int, seq=None) -> None:
    slo_repository.insert({
        "id": slo_id, "class": CLASS, "subject": SUBJECT, "slo_code": code,
        "slo_text": f"outcome {code}", "bloom_level": None, "strand": "N", "sequence": seq,
    })
    slo_exam_plan_repository.overwrite_assignments(
        [{"slo_id": slo_id, "exam_no": exam_no, "position": None}]
    )


def _question(qid: str) -> None:
    questions_repository.insert({
        "id": qid, "subject": SUBJECT, "topic": "t", "bloom_level": "REMEMBER",
        "difficulty": "easy", "question_type": "multiple-choice", "marks": 1,
        "question_en": "q", "question_ur": None, "options_en": "[]", "options_ur": "[]",
        "correct_answer_en": None, "correct_answer_ur": None,
        "explanation_en": None, "explanation_ur": None,
        "visual_emoji": None, "visual_count": None,
    })


def _paper(pid: str, qids: list, exam_no, class_name=CLASS) -> None:
    papers_repository.insert(
        paper_id=pid, subject=SUBJECT, class_name=class_name, total_marks=len(qids),
        question_ids=qids, paper_title=pid, exam_no=exam_no,
    )


def _link(qid: str, slo_id: str) -> None:
    question_slo_repository.replace_for_question(qid, [slo_id])


def test_planned_slo_not_in_any_paper_is_missing(test_db):
    _set_n(4)
    _slo("s1", "M-01", exam_no=3)
    res = coverage_service.exam_coverage(CLASS, SUBJECT, 3)
    assert res["planned_count"] == 1
    assert res["covered_count"] == 0
    assert [m["slo_code"] for m in res["missing"]] == ["M-01"]
    assert res["planned"][0]["covered"] is False


def test_slo_in_other_exam_paper_still_missing(test_db):
    """SABSE AHEM: SLO exam 3 mein planned, lekin sirf exam-5 ke paper mein aaya —
    exam 3 ke liye covered NAHI."""
    _set_n(5)
    _slo("s1", "M-01", exam_no=3)
    _question("q1")
    _link("q1", "s1")
    _paper("pB", ["q1"], exam_no=5)  # ghalat exam

    res = coverage_service.exam_coverage(CLASS, SUBJECT, 3)
    assert res["covered_count"] == 0
    assert res["planned"][0]["covered"] is False
    assert [m["slo_code"] for m in res["missing"]] == ["M-01"]


def test_paper_exam_no_null_excluded(test_db):
    """exam_no NULL wala paper coverage se bilkul bahar (NULL = ? kabhi true nahi)."""
    _set_n(4)
    _slo("s1", "M-01", exam_no=3)
    _question("q1")
    _link("q1", "s1")
    _paper("pNull", ["q1"], exam_no=None)  # kisi exam se attach nahi

    res = coverage_service.exam_coverage(CLASS, SUBJECT, 3)
    assert res["covered_count"] == 0
    assert res["planned"][0]["covered"] is False


def test_one_slo_two_papers_both_paper_ids_no_double_count(test_db):
    """Ek SLO do papers (dono exam 3) mein — paper_ids mein dono, covered_count phir
    bhi 1 (double count nahi)."""
    _set_n(4)
    _slo("s1", "M-01", exam_no=3)
    _question("q1")
    _question("q2")
    _link("q1", "s1")
    _link("q2", "s1")
    _paper("pA", ["q1"], exam_no=3)
    _paper("pB", ["q2"], exam_no=3)

    res = coverage_service.exam_coverage(CLASS, SUBJECT, 3)
    assert res["planned_count"] == 1
    assert res["covered_count"] == 1  # double count nahi
    assert res["planned"][0]["covered"] is True
    assert res["planned"][0]["paper_ids"] == ["pA", "pB"]  # sorted, dono


def test_covered_happy_path_and_percent(test_db):
    _set_n(4)
    _slo("s1", "M-01", exam_no=3)
    _slo("s2", "M-02", exam_no=3)
    _question("q1")
    _link("q1", "s1")
    _paper("pA", ["q1"], exam_no=3)

    res = coverage_service.exam_coverage(CLASS, SUBJECT, 3)
    assert res["planned_count"] == 2
    assert res["covered_count"] == 1
    assert res["coverage_percent"] == 50
    assert res["papers"] == [{"id": "pA", "paper_title": "pA"}]


def test_summary_counts_all_exams_plus_unassigned(test_db):
    _set_n(4)
    _slo("s1", "M-01", exam_no=3)
    _slo("s2", "M-02", exam_no=3)
    _slo("s3", "M-03", exam_no=1)
    _slo("u1", "M-09", exam_no=0)  # Unassigned
    _question("q1")
    _link("q1", "s1")
    _paper("pA", ["q1"], exam_no=3)

    summ = coverage_service.coverage_summary(CLASS, SUBJECT)
    by_exam = {e["exam_no"]: (e["planned_count"], e["covered_count"]) for e in summ["exams"]}
    assert by_exam[3] == (2, 1)
    assert by_exam[1] == (1, 0)
    assert by_exam[2] == (0, 0)
    assert by_exam[0] == (1, 0)  # Unassigned: planned 1, covered hamesha 0
    assert summ["exam_count"] == 4


def test_class_normalized_match_for_papers(test_db):
    """papers.class_name free-text — 'c1' bhi 'C1' ke plan se match kare."""
    _set_n(4)
    _slo("s1", "M-01", exam_no=3)
    _question("q1")
    _link("q1", "s1")
    _paper("pA", ["q1"], exam_no=3, class_name="  c1 ")  # case/space farq

    res = coverage_service.exam_coverage(CLASS, SUBJECT, 3)
    assert res["covered_count"] == 1
