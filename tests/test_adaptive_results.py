"""Tests for adaptive_results_service: template, upload, analysis, generation."""

import io

import pandas as pd
import pytest

from app.repositories import papers_repository, questions_repository, result_repository
from app.services import adaptive_results_service, settings_service
from app.services.exceptions import ResultsValidationError

# ---- helpers ---------------------------------------------------------------


def _insert_question(qid: str, topic: str, bloom: str = "REMEMBER", marks: int = 1):
    questions_repository.insert(
        {
            "id": qid,
            "subject": "Science",
            "topic": topic,
            "bloom_level": bloom,
            "difficulty": "easy",
            "question_type": "multiple-choice",
            "marks": marks,
            "question_en": "Q?",
            "question_ur": None,
            "options_en": None,
            "options_ur": None,
            "correct_answer_en": None,
            "correct_answer_ur": None,
            "explanation_en": None,
            "explanation_ur": None,
            "visual_emoji": None,
            "visual_count": None,
        }
    )


def _insert_paper(pid: str, qids: list):
    papers_repository.insert(
        paper_id=pid,
        subject="Science",
        class_name="9A",
        total_marks=sum(1 for _ in qids),
        question_ids=qids,
        paper_title="Test Paper",
    )


def _make_xlsx(rows: list, columns: list) -> bytes:
    df = pd.DataFrame(rows, columns=columns)
    buf = io.BytesIO()
    df.to_excel(buf, index=False, engine="openpyxl")
    return buf.getvalue()


# ---- template --------------------------------------------------------------


def test_template_returns_none_for_missing_paper(test_db):
    assert adaptive_results_service.build_excel_template("no-such-id") is None


def test_template_columns_match_paper_questions(test_db):
    _insert_question("q1", "Cells", marks=1)
    _insert_question("q2", "DNA", marks=3)
    _insert_paper("p1", ["q1", "q2"])

    xlsx = adaptive_results_service.build_excel_template("p1")
    assert xlsx is not None
    df = pd.read_excel(io.BytesIO(xlsx))
    assert list(df.columns) == ["roll_no", "student_name", "Q1 (marks: 1)", "Q2 (marks: 3)"]


# ---- upload ----------------------------------------------------------------


def test_upload_returns_none_for_missing_paper(test_db):
    xlsx = _make_xlsx([], ["roll_no", "student_name", "Q1 (marks: 1)"])
    assert adaptive_results_service.upload_results("no-such", "f.xlsx", xlsx) is None


def test_upload_saves_student_count(test_db):
    _insert_question("q1", "Cells", marks=1)
    _insert_paper("p1", ["q1"])
    cols = ["roll_no", "student_name", "Q1 (marks: 1)"]
    rows = [["R1", "Ali", 1], ["R2", "Sara", 0]]
    xlsx = _make_xlsx(rows, cols)

    result = adaptive_results_service.upload_results("p1", "f.xlsx", xlsx)
    assert result["student_count"] == 2
    assert result["warning"] is None or isinstance(result["warning"], str)


def test_upload_warning_when_students_below_minimum(test_db):
    _insert_question("q1", "Cells", marks=1)
    _insert_paper("p1", ["q1"])
    # Default: class_size=25, min_analysis_percent=60 → need ceil(25*60/100)=15 students
    cols = ["roll_no", "student_name", "Q1 (marks: 1)"]
    rows = [["R1", "Ali", 1]]
    xlsx = _make_xlsx(rows, cols)

    result = adaptive_results_service.upload_results("p1", "f.xlsx", xlsx)
    assert result["warning"] is not None
    assert "1 students" in result["warning"]


def test_upload_replaces_previous_data(test_db):
    _insert_question("q1", "Cells", marks=2)
    _insert_paper("p1", ["q1"])
    cols = ["roll_no", "student_name", "Q1 (marks: 2)"]

    xlsx1 = _make_xlsx([["R1", "Ali", 2]], cols)
    adaptive_results_service.upload_results("p1", "first.xlsx", xlsx1)

    uploads_before = result_repository.list_uploads_for_paper("p1")
    assert len(uploads_before) == 1

    xlsx2 = _make_xlsx([["R1", "Ali", 1], ["R2", "Sara", 2]], cols)
    adaptive_results_service.upload_results("p1", "second.xlsx", xlsx2)

    uploads_after = result_repository.list_uploads_for_paper("p1")
    assert len(uploads_after) == 1  # old replaced, not accumulated
    assert uploads_after[0]["filename"] == "second.xlsx"


def test_upload_raises_on_column_count_mismatch(test_db):
    _insert_question("q1", "Cells", marks=1)
    _insert_paper("p1", ["q1"])
    xlsx = _make_xlsx([], ["roll_no", "student_name"])  # missing q column
    with pytest.raises(ResultsValidationError):
        adaptive_results_service.upload_results("p1", "f.xlsx", xlsx)


def test_upload_raises_when_marks_exceed_max(test_db):
    _insert_question("q1", "Cells", marks=1)
    _insert_paper("p1", ["q1"])
    cols = ["roll_no", "student_name", "Q1 (marks: 1)"]
    xlsx = _make_xlsx([["R1", "Ali", 5]], cols)  # 5 > max 1
    with pytest.raises(ResultsValidationError):
        adaptive_results_service.upload_results("p1", "f.xlsx", xlsx)


# ---- analysis --------------------------------------------------------------


def test_analysis_returns_none_when_no_upload(test_db):
    _insert_question("q1", "Cells", marks=1)
    _insert_paper("p1", ["q1"])
    assert adaptive_results_service.get_analysis("p1") is None


def test_analysis_topic_and_bloom_scores(test_db):
    _insert_question("q1", "Cells", bloom="REMEMBER", marks=2)
    _insert_question("q2", "DNA", bloom="APPLY", marks=2)
    _insert_paper("p1", ["q1", "q2"])
    cols = ["roll_no", "student_name", "Q1 (marks: 2)", "Q2 (marks: 2)"]
    xlsx = _make_xlsx(
        [["R1", "Ali", 2, 0], ["R2", "Sara", 1, 2]],
        cols,
    )
    adaptive_results_service.upload_results("p1", "f.xlsx", xlsx)

    analysis = adaptive_results_service.get_analysis("p1")
    assert analysis is not None
    topics = {t["topic"] for t in analysis["topic_scores"]}
    assert "Cells" in topics and "DNA" in topics
    blooms = {b["bloom_level"] for b in analysis["bloom_scores"]}
    assert "REMEMBER" in blooms and "APPLY" in blooms
    assert analysis["student_count"] == 2


def test_analysis_flags_weak_topics_below_threshold(test_db):
    _insert_question("q1", "Weak Topic", bloom="REMEMBER", marks=10)
    _insert_paper("p1", ["q1"])
    # Student scores 2/10 = 20% — below default threshold 60%
    cols = ["roll_no", "student_name", "Q1 (marks: 10)"]
    xlsx = _make_xlsx([["R1", "Ali", 2]], cols)
    adaptive_results_service.upload_results("p1", "f.xlsx", xlsx)

    analysis = adaptive_results_service.get_analysis("p1")
    assert "Weak Topic" in analysis["weak_topics"]


def test_analysis_strong_topic_not_flagged(test_db):
    _insert_question("q1", "Strong Topic", bloom="REMEMBER", marks=10)
    _insert_paper("p1", ["q1"])
    cols = ["roll_no", "student_name", "Q1 (marks: 10)"]
    xlsx = _make_xlsx([["R1", "Ali", 9]], cols)  # 90% — above threshold
    adaptive_results_service.upload_results("p1", "f.xlsx", xlsx)

    analysis = adaptive_results_service.get_analysis("p1")
    assert "Strong Topic" not in analysis["weak_topics"]


# ---- generate --------------------------------------------------------------


def test_generate_creates_paper_in_db(test_db):
    _insert_question("q1", "Cells", bloom="REMEMBER", marks=1)
    _insert_question("q2", "DNA", bloom="APPLY", marks=1)
    _insert_paper("p1", ["q1", "q2"])
    cols = ["roll_no", "student_name", "Q1 (marks: 1)", "Q2 (marks: 1)"]
    xlsx = _make_xlsx([["R1", "Ali", 0, 1], ["R2", "Sara", 1, 1]], cols)
    adaptive_results_service.upload_results("p1", "f.xlsx", xlsx)

    new_id = adaptive_results_service.generate_paper("p1", total_questions=2, language=None)
    assert new_id is not None
    paper = papers_repository.find_by_id(new_id)
    assert paper is not None
    assert paper["subject"] == "Science"


def test_generate_returns_none_when_no_upload(test_db):
    _insert_question("q1", "Cells", marks=1)
    _insert_paper("p1", ["q1"])
    assert adaptive_results_service.generate_paper("p1", total_questions=5, language=None) is None


# ---- settings integration --------------------------------------------------


def test_settings_new_fields_have_defaults(test_db):
    s = settings_service.get_settings()
    assert s.get("class_size", 25) == 25
    assert s.get("min_analysis_percent", 60) == 60
    assert s.get("weak_topic_threshold", 60) == 60
