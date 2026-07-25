"""Exam-wise SLO coverage service — Marhala 5.

Strict per-exam coverage: har exam apne TAGGED papers se judge hota hai. Ek SLO
exam 2 mein planned magar exam 3 ke paper ne cover kiya => kisi exam ko credit nahi
(cross-exam leak nahi). Yeh test us usool ko lock karte hain.

DB: conftest `test_db` fixture (tmp SQLite + init_db). Data seedha repos se seed.
"""

from app.repositories import (
    papers_repository,
    question_slo_repository,
    questions_repository,
    slo_exam_plan_repository,
    slo_repository,
)
from app.services import coverage_service


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


def _link(qid: str, slo_ids: list) -> None:
    question_slo_repository.replace_for_question(qid, slo_ids)


def _paper(pid: str, qids: list, exam_no, class_name="Pre Year 1",
           subject="Mathematics") -> None:
    papers_repository.insert(pid, subject, class_name, len(qids), qids, exam_no=exam_no)


def _plan(slo_id: str, exam_no: int, position=None) -> None:
    slo_exam_plan_repository.overwrite_assignments(
        [{"slo_id": slo_id, "exam_no": exam_no, "position": position}]
    )


def _summary_rows(class_name="Pre Year 1", subject="Mathematics") -> dict:
    summ = coverage_service.coverage_summary(class_name, subject)
    return {e["exam_no"]: e for e in summ["exams"]}


# ⭐ sab se ahem — strict cross-exam
def test_covered_in_wrong_exam_stays_missing(test_db):
    """s1 exam 2 mein planned; exam 3 ke paper ne s1 cover kiya. covered-in-wrong-exam
    kisi ko credit nahi: exam 2 mein remaining, exam 2 & exam 3 dono summary covered=0."""
    _q("q1")
    _slo("s1", "MATH-01")
    _link("q1", ["s1"])
    _plan("s1", 2)                     # planned for exam 2
    _paper("p1", ["q1"], exam_no=3)    # covered by an exam-3 paper

    detail = coverage_service.exam_coverage("Pre Year 1", "Mathematics", 2)
    assert detail["covered_slos"] == 0
    assert [r["slo_code"] for r in detail["remaining"]] == ["MATH-01"]

    rows = _summary_rows()
    assert rows[2]["covered"] == 0     # planned exam ko credit nahi
    assert rows[3]["covered"] == 0     # s1 exam 3 mein planned hi nahi


def test_planned_but_missing(test_db):
    """exam 2 ke liye planned SLO, koi paper nahi => remaining mein."""
    _slo("s1", "MATH-01")
    _plan("s1", 2)
    detail = coverage_service.exam_coverage("Pre Year 1", "Mathematics", 2)
    assert detail["total_slos"] == 1
    assert detail["covered_slos"] == 0
    assert [r["slo_code"] for r in detail["remaining"]] == ["MATH-01"]


def test_null_exam_paper_excluded(test_db):
    """exam_no=NULL (untagged) paper ka SLO kisi exam coverage mein na aaye."""
    _q("q1")
    _slo("s1", "MATH-01")
    _link("q1", ["s1"])
    _plan("s1", 1)
    _paper("p1", ["q1"], exam_no=None)   # untagged

    detail = coverage_service.exam_coverage("Pre Year 1", "Mathematics", 1)
    assert detail["covered_slos"] == 0
    assert [r["slo_code"] for r in detail["remaining"]] == ["MATH-01"]

    rows = _summary_rows()
    assert rows[1]["covered"] == 0


def test_slo_two_papers_same_exam(test_db):
    """Ek SLO, do papers same exam => paper_map[slo] mein dono paper_ids, magar
    covered_slos count mein double-count nahi (SET membership)."""
    _q("q1")
    _q("q2")
    _slo("s1", "MATH-01")
    _link("q1", ["s1"])
    _link("q2", ["s1"])
    _plan("s1", 1)
    _paper("p1", ["q1"], exam_no=1)
    _paper("p2", ["q2"], exam_no=1)

    detail = coverage_service.exam_coverage("Pre Year 1", "Mathematics", 1)
    assert detail["covered_slos"] == 1     # double-count nahi
    entry = next(s for s in detail["covered"] if s["slo_code"] == "MATH-01")
    assert set(entry["paper_ids"]) == {"p1", "p2"}


def test_summary_includes_unassigned(test_db):
    """coverage_summary mein exam_no=0 (Unassigned) bucket shamil ho — bina-plan SLO
    yahan ginte hain."""
    _slo("s1", "MATH-01")   # koi plan nahi => Unassigned
    rows = _summary_rows()
    assert 0 in rows
    assert rows[0]["unassigned"] is True
    assert rows[0]["planned"] == 1
    assert rows[0]["covered"] == 0


def test_class_normalized_match(test_db):
    """paper.class_name 'pre year 1' (gandi) SLO.class 'Pre Year 1' se match kare —
    covered_slo_pairs LOWER(TRIM) normalize karta hai."""
    _q("q1")
    _slo("s1", "MATH-01")                 # class 'Pre Year 1'
    _link("q1", ["s1"])
    _plan("s1", 1)
    _paper("p1", ["q1"], exam_no=1, class_name="pre year 1")  # dirty value

    detail = coverage_service.exam_coverage("Pre Year 1", "Mathematics", 1)
    assert detail["covered_slos"] == 1
    entry = next(s for s in detail["covered"] if s["slo_code"] == "MATH-01")
    assert entry["paper_ids"] == ["p1"]
