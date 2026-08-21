"""Grade filter — paper ke questions syllabus grade se filter hone chahiyen.

2026-08-21 se pehle grade kahin filter karta hi nahi tha. `class_name` sirf
`_resolve_title()` aur `_persist_paper()` tak jata tha; `_pick_questions()` use
dekhta bhi nahi tha. Naapa gaya: "Grade 4" ka 10-sawal balanced paper 8 sawal
laata tha jin mein se sirf 2 Grade 4 ke thay -- baqi Pre Year 1 (pre-school) ke,
jaise "Count the candies and match with the correct number".

Ye tests wahi soorat pakadti hain: ek hi subject, do grades, aur ye tasdeeq ke
doosre grade ka sawal paper mein aa hi nahi sakta.
"""

from __future__ import annotations

import pytest

from app.repositories import questions_repository, syllabus_repository
from app.schemas.requests import GeneratePaperRequest
from app.services import paper_service


def _question(qid: str, topic_id: str | None, bloom: str = "UNDERSTAND") -> dict:
    return {
        "id": qid,
        "subject": "Mathematics",
        "topic": "T",
        "bloom_level": bloom,
        "difficulty": "medium",
        "question_type": "short-answer",
        "marks": 2,
        "question_en": f"Q {qid}",
        "question_ur": None,
        "options_en": "[]",
        "options_ur": "[]",
        "correct_answer_en": None,
        "correct_answer_ur": None,
        "explanation_en": None,
        "explanation_ur": None,
        "visual_emoji": None,
        "visual_count": None,
        "syllabus_topic_id": topic_id,
        "image_path": None,
        "image_size": None,
        "source": "manual",
        "learning_outcome": None,
        "estimated_time": None,
        "keywords": None,
        "source_book": None,
        "page_number": None,
        "status": "published",
        "answer_lines": None,
    }


@pytest.fixture
def two_grades(test_db):
    """Ek subject, do grades, aur ek bin-syllabus sawal.

    Bin-syllabus sawal is liye ke wo asal soorat hai: 2026-08-21 ko English ke
    saare 130 sawal aise hi thay (`syllabus_topic_id` NULL).
    """
    g4, py1 = "topic-g4", "topic-py1"
    syllabus_repository.insert(
        topic_id=g4,
        subject="Mathematics",
        grade="Grade 4",
        unit_no=1,
        unit_title="U",
        page_range="1-2",
        subtopic_title="Place value",
        activity_type="Introduction",
        page_no=1,
        learning_outcome="LO",
    )
    syllabus_repository.insert(
        topic_id=py1,
        subject="Mathematics",
        grade="Pre Year 1",
        unit_no=1,
        unit_title="U",
        page_range="1-2",
        subtopic_title="Counting",
        activity_type="Introduction",
        page_no=1,
        learning_outcome="LO",
    )
    questions_repository.insert(_question("g4-a", g4))
    questions_repository.insert(_question("g4-b", g4, bloom="REMEMBER"))
    questions_repository.insert(_question("py1-a", py1))
    questions_repository.insert(_question("py1-b", py1, bloom="REMEMBER"))
    questions_repository.insert(_question("orphan", None))
    return {"g4": g4, "py1": py1}


# ── repository ────────────────────────────────────────────────────────────────


def test_grade_none_returns_everything(two_grades):
    """Default = purana behaviour. Ye sab se aham test hai: filter opt-in hai,
    to bina grade ke chalne wale saare mojooda raaste na toote."""
    rows = questions_repository.find_least_used(
        subject="Mathematics", bloom_level="UNDERSTAND", difficulty=None, limit=99
    )
    assert {r["id"] for r in rows} == {"g4-a", "py1-a", "orphan"}


def test_grade_excludes_other_grades(two_grades):
    rows = questions_repository.find_least_used(
        subject="Mathematics",
        bloom_level="UNDERSTAND",
        difficulty=None,
        limit=99,
        grade="Grade 4",
    )
    assert {r["id"] for r in rows} == {"g4-a"}


def test_grade_excludes_questions_with_no_syllabus_link(two_grades):
    """INNER JOIN ka seedha nateeja, aur ye jaan-boojh kar hai -- wahi rawaiya jo
    `list_for_slo_export()` ka hai. Bin-link sawal ka grade maloom hi nahi, to
    usay "Grade 4 ka" nahi kaha ja sakta."""
    rows = questions_repository.find_least_used(
        subject="Mathematics",
        bloom_level="UNDERSTAND",
        difficulty=None,
        limit=99,
        grade="Grade 4",
    )
    assert "orphan" not in {r["id"] for r in rows}


@pytest.mark.parametrize("grade", ["grade 4", "GRADE 4", "  Grade 4  "])
def test_grade_match_ignores_case_and_whitespace(two_grades, grade):
    """UI ki value aur DB ki value mein farq aa sakta hai; match saabit rahe."""
    rows = questions_repository.find_least_used(
        subject="Mathematics",
        bloom_level="UNDERSTAND",
        difficulty=None,
        limit=99,
        grade=grade,
    )
    assert {r["id"] for r in rows} == {"g4-a"}


def test_grade_combines_with_the_other_filters(two_grades):
    """Grade doosre filters ko HATATA nahi -- JOIN ke baad bhi subject/bloom lagte
    hain. Ye is liye ke JOIN ne query ki shakl badli hai."""
    rows = questions_repository.find_least_used(
        subject="Mathematics",
        bloom_level="REMEMBER",
        difficulty="medium",
        limit=99,
        question_types=["short-answer"],
        grade="Grade 4",
    )
    assert {r["id"] for r in rows} == {"g4-b"}

    assert (
        questions_repository.find_least_used(
            subject="Mathematics",
            bloom_level="REMEMBER",
            difficulty="hard",
            limit=99,
            grade="Grade 4",
        )
        == []
    )


# ── service + schema ──────────────────────────────────────────────────────────


def test_generate_paper_request_accepts_grade():
    req = GeneratePaperRequest(subject="Mathematics", grade="Grade 4")
    assert req.grade == "Grade 4"


def test_grade_defaults_to_none_so_nothing_changes_by_accident():
    assert GeneratePaperRequest(subject="Mathematics").grade is None


def test_paper_only_contains_the_requested_grade(two_grades):
    """Poora raasta: request se le kar paper tak. Yehi wo cheez hai jo pehle
    toot-ti thi."""
    paper = paper_service.assemble_balanced_paper(
        GeneratePaperRequest(
            subject="Mathematics",
            grade="Grade 4",
            total_questions=4,
            class_name="Grade 4",
        )
    )
    assert paper is not None
    picked = {q["id"] for q in paper["questions"]}
    assert picked and picked <= {"g4-a", "g4-b"}


def test_the_filter_is_not_hardcoded_to_one_grade(two_grades):
    """Ulta rukh: Pre Year 1 maangne par sirf Pre Year 1 aaye. Ye Grade 4 wale
    test ka aaina hai -- us akele se ye zahir nahi hota ke filter waqai grade par
    chal raha hai, na ke ittefaq se."""
    paper = paper_service.assemble_balanced_paper(
        GeneratePaperRequest(subject="Mathematics", grade="Pre Year 1", total_questions=4)
    )
    assert paper is not None
    picked = {q["id"] for q in paper["questions"]}
    assert picked and picked <= {"py1-a", "py1-b"}


def test_unknown_grade_gives_no_paper_rather_than_a_wrong_one(two_grades):
    """Anjaan grade par khali lautna chahiye (caller use 404 banata hai) -- chup
    chaap kisi doosre grade ke sawal dena sab se bura nateeja hota."""
    assert (
        paper_service.assemble_balanced_paper(
            GeneratePaperRequest(subject="Mathematics", grade="Grade 9", total_questions=4)
        )
        is None
    )


# ── frontend wiring ───────────────────────────────────────────────────────────


def test_build_paper_sends_grade_not_just_class_name():
    """Backend ka filter bekaar hai agar UI `grade` bhejna band kar de -- aur ye
    line chup-chaap gayab ho sakti hai. Wahi guard jo test_generator_class_name.py
    `class_name` par lagata hai."""
    from pathlib import Path

    html = (Path(__file__).parent.parent / "static" / "index.html").read_text(encoding="utf-8")
    start = html.index("function buildPaper")
    region = html[start : html.index("\nasync function ", start + 10)]
    assert "grade:" in region, "buildPaper() ne grade bhejna band kar diya -- filter mar gaya"
    assert "gradeSelect" in region
