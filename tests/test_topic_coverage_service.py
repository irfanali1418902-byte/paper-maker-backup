"""topic_coverage_service — hafta-war planned vs covered. R7 Marhala 3.

Do baatein jo in tests ka markaz hain, kyunke yehi is module ko SLO coverage se
alag karti hain:

  1. `covered` GLOBAL hai. `papers` mein `week_no` column hai hi nahi, to paper ka
     kisi hafte se koi taalluq nahi. Topic kisi bhi paper mein aaya = covered.
  2. subject/grade ka gate TOPIC par hai, paper par nahi. Paper ka `class_name`
     kuch bhi ho — ganda, khali, ya kisi aur class ka — hisaab par asar nahi
     padta, kyunke ek topic id pehle se theek ek (subject, grade) ki hai.
"""

import pytest

from app.repositories import (
    papers_repository,
    questions_repository,
    syllabus_repository,
    topic_week_plan_repository,
)
from app.services import topic_coverage_service, topic_week_service

SUBJ = "Mathematics"
GRADE = "Pre Year 2"


def _topic(topic_id: str, title: str = "T", subject: str = SUBJ, grade: str = GRADE) -> None:
    syllabus_repository.insert(
        topic_id=topic_id, subject=subject, grade=grade, unit_no=1,
        unit_title="Unit", page_range="", subtopic_title=title,
        activity_type="Introduction", page_no=None, learning_outcome="",
    )


def _q(qid: str, topic_id=None, subject: str = SUBJ) -> None:
    questions_repository.insert({
        "id": qid, "subject": subject, "topic": "Counting",
        "bloom_level": "REMEMBER", "difficulty": "easy",
        "question_type": "short-answer", "marks": 1,
        "question_en": "Q", "question_ur": None,
        "options_en": "[]", "options_ur": "[]",
        "correct_answer_en": None, "correct_answer_ur": None,
        "explanation_en": None, "explanation_ur": None,
        "visual_emoji": None, "visual_count": None,
        "syllabus_topic_id": topic_id,
    })


def _paper(paper_id: str, question_ids: list, subject: str = SUBJ,
           class_name="Pre Year 2", exam_no=None) -> None:
    papers_repository.insert(
        paper_id=paper_id, subject=subject, class_name=class_name,
        total_marks=len(question_ids), question_ids=question_ids, exam_no=exam_no,
    )


def _assign(topic_id: str, week_no: int) -> None:
    topic_week_plan_repository.overwrite_assignments(
        [{"syllabus_topic_id": topic_id, "week_no": week_no, "position": None}]
    )


def _week(result: dict, week_no: int) -> dict:
    return next(w for w in result["weeks"] if w["week_no"] == week_no)


@pytest.fixture
def n4(monkeypatch):
    """N=4 — chhota board, taake har hafta test mein likha ja sake."""
    monkeypatch.setattr(topic_week_service, "week_count", lambda: 4)


# ---- shape ----


def test_returns_one_row_per_week_plus_unassigned(test_db, n4):
    result = topic_coverage_service.coverage(SUBJ, GRADE)
    assert [w["week_no"] for w in result["weeks"]] == [1, 2, 3, 4, 0]
    assert result["weeks"][-1]["unassigned"] is True
    assert all(w["unassigned"] is False for w in result["weeks"][:-1])
    assert result["week_count"] == 4


def test_empty_subject_grade_gives_zeros_not_a_crash(test_db, n4):
    result = topic_coverage_service.coverage("Nahi", "Mojood")
    assert result["total_topics"] == 0
    assert result["covered_topics"] == 0
    # 0/0 ko 0% dikhana jhoot hai — None, bilkul _assemble_coverage jaisa.
    assert result["coverage_percent"] is None
    assert all(w["planned"] == 0 and w["coverage_percent"] is None for w in result["weeks"])


# ---- covered ki tareef ----


def test_topic_in_a_paper_counts_as_covered(test_db, n4):
    _topic("t1")
    _assign("t1", 2)
    _q("q1", "t1")
    _paper("p1", ["q1"])

    result = topic_coverage_service.coverage(SUBJ, GRADE)
    assert _week(result, 2) == {
        "week_no": 2, "unassigned": False, "planned": 1, "covered": 1,
        "coverage_percent": 100,
    }


def test_planned_but_never_examined_is_not_covered(test_db, n4):
    _topic("t1")
    _topic("t2")
    _assign("t1", 1)
    _assign("t2", 1)
    _q("q1", "t1")
    _paper("p1", ["q1"])          # sirf t1 paper mein aaya

    result = topic_coverage_service.coverage(SUBJ, GRADE)
    assert _week(result, 1)["planned"] == 2
    assert _week(result, 1)["covered"] == 1
    assert _week(result, 1)["coverage_percent"] == 50


def test_covered_ignores_which_exam_the_paper_belongs_to(test_db, n4):
    """YEHI SLO COVERAGE SE BUNYADI FARQ HAI. Wahan exam 3 ka paper exam 2 ka SLO
    cover nahi karta. Yahan paper ka koi hafta hai hi nahi (`papers` mein `week_no`
    column nahi), to exam_no ka is hisaab se koi taalluq nahi."""
    _topic("t1")
    _assign("t1", 1)
    _q("q1", "t1")
    _paper("p1", ["q1"], exam_no=7)      # exam 7 ka paper, hafta 1 ka topic

    assert _week(topic_coverage_service.coverage(SUBJ, GRADE), 1)["covered"] == 1


def test_untagged_paper_still_covers(test_db, n4):
    """exam_no None — SLO coverage aise paper ko `covered_pairs_all_exams` mein
    ginti hi nahi (exam_no IS NOT NULL). Yahan ginta hai: 30 mein se 10 papers
    par exam_no nahi hai (naapa 2026-08-23) aur wo bhi asli papers hain."""
    _topic("t1")
    _assign("t1", 3)
    _q("q1", "t1")
    _paper("p1", ["q1"], exam_no=None)

    assert _week(topic_coverage_service.coverage(SUBJ, GRADE), 3)["covered"] == 1


def test_paper_class_name_does_not_gate_the_count(test_db, n4):
    """Gate topic par hai, paper par nahi — is liye paper ka ganda/khali/ghair-mutabiq
    class_name hisaab nahi badalta. SLO ke raaste par yehi field LOWER(TRIM) se match
    hoti hai aur wahan usay saaf rakhna zaroori hai."""
    _topic("t1")
    _assign("t1", 1)
    _q("q1", "t1")
    _paper("p1", ["q1"], class_name="  KOI aur CLASS  ")

    assert _week(topic_coverage_service.coverage(SUBJ, GRADE), 1)["covered"] == 1


def test_question_without_a_topic_never_covers(test_db, n4):
    """594 mein se 130 sawalon par syllabus_topic_id NULL hai (sab English). Wo
    coverage mein kabhi nahi aa sakte — module ki kami nahi, data ki soorat."""
    _topic("t1")
    _assign("t1", 1)
    _q("q1", None)
    _paper("p1", ["q1"])

    assert _week(topic_coverage_service.coverage(SUBJ, GRADE), 1)["covered"] == 0


def test_other_subject_grade_topics_do_not_leak(test_db, n4):
    _topic("t1")
    _topic("x1", subject="Geography", grade="Grade 8")
    _assign("t1", 1)
    _assign("x1", 1)
    _q("q1", "t1")
    _q("qx", "x1", subject="Geography")
    _paper("p1", ["q1", "qx"])

    result = topic_coverage_service.coverage(SUBJ, GRADE)
    assert result["total_topics"] == 1
    assert _week(result, 1)["planned"] == 1


def test_same_topic_in_two_papers_counts_once(test_db, n4):
    _topic("t1")
    _assign("t1", 1)
    _q("q1", "t1")
    _q("q2", "t1")
    _paper("p1", ["q1"])
    _paper("p2", ["q2"])

    result = topic_coverage_service.coverage(SUBJ, GRADE)
    assert _week(result, 1)["covered"] == 1
    assert sorted(result["paper_map"]["t1"]) == ["p1", "p2"]


# ---- bucketing — get_plan ke bilkul barabar ----


@pytest.mark.parametrize("week_no", [0, 9])
def test_out_of_range_and_zero_land_in_unassigned(test_db, n4, week_no):
    """N=4 par week 9 (N ghatne se nikla) aur week 0 — dono Unassigned. Yehi
    get_plan() ka rule hai; dono ek jaise bucket karein warna page ka board aur
    report alag ginti dikhayenge."""
    _topic("t1")
    _assign("t1", week_no)

    result = topic_coverage_service.coverage(SUBJ, GRADE)
    assert _week(result, 0)["planned"] == 1
    assert sum(_week(result, i)["planned"] for i in range(1, 5)) == 0


def test_topic_with_no_plan_row_lands_in_unassigned(test_db, n4):
    _topic("t1")   # koi _assign nahi — week_no NULL
    assert _week(topic_coverage_service.coverage(SUBJ, GRADE), 0)["planned"] == 1


def test_unassigned_covered_is_the_real_count_not_forced_zero(test_db, n4):
    """`coverage_summary` Unassigned ka covered 0 force karta hai, kyunke wahan
    "kisi exam mein nahi" ka matlab hai us exam ke liye cover ho hi nahi sakta.
    Yahan covered ka koi hafta hai hi nahi, to "hafta tay nahi magar paper mein aa
    chuka" asal aur kaam ki soorat hai — usay 0 dikhana maloomat chupana hoga."""
    _topic("t1")
    _assign("t1", 0)
    _q("q1", "t1")
    _paper("p1", ["q1"])

    row = _week(topic_coverage_service.coverage(SUBJ, GRADE), 0)
    assert row["unassigned"] is True
    assert row["covered"] == 1
    assert row["coverage_percent"] == 100


# ---- totals ----


def test_totals_are_over_the_whole_subject_grade(test_db, n4):
    _topic("t1")
    _topic("t2")
    _topic("t3")
    _assign("t1", 1)
    _assign("t2", 3)
    # t3 ka koi plan nahi
    _q("q1", "t1")
    _q("q3", "t3")
    _paper("p1", ["q1", "q3"])

    result = topic_coverage_service.coverage(SUBJ, GRADE)
    assert result["total_topics"] == 3
    assert result["covered_topics"] == 2
    assert result["coverage_percent"] == 67           # round(2/3*100)
    assert sum(w["planned"] for w in result["weeks"]) == 3


def test_week_count_setting_drives_the_row_count(test_db, monkeypatch):
    monkeypatch.setattr(topic_week_service, "week_count", lambda: 2)
    result = topic_coverage_service.coverage(SUBJ, GRADE)
    assert [w["week_no"] for w in result["weeks"]] == [1, 2, 0]
