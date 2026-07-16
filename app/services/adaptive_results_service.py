"""Adaptive results pipeline: Excel template, upload, topic analysis, paper generation."""

import io
import json
import math
import uuid
from datetime import date
from typing import Optional

import pandas as pd

from app.repositories import papers_repository, questions_repository, result_repository
from app.services import settings_service
from app.services.exceptions import ResultsValidationError

_FLOOR = 20.0  # minimum weight per topic so all topics stay represented


# ---- public API ------------------------------------------------------------


def build_excel_template(paper_id: str) -> Optional[bytes]:
    """Returns a .xlsx template (header row only) for the teacher to fill in.
    Columns: roll_no, student_name, Q1 (marks: X), ...
    Returns None if the paper doesn't exist."""
    paper = papers_repository.find_by_id(paper_id)
    if paper is None:
        return None
    question_ids = json.loads(paper["question_ids"])
    questions = [questions_repository.find_by_id(qid) for qid in question_ids]
    questions = [q for q in questions if q]

    columns = ["roll_no", "student_name"] + [
        f"Q{i + 1} (marks: {q['marks']})" for i, q in enumerate(questions)
    ]
    df = pd.DataFrame(columns=columns)
    buf = io.BytesIO()
    df.to_excel(buf, index=False, engine="openpyxl")
    return buf.getvalue()


def upload_results(paper_id: str, filename: str, file_bytes: bytes) -> Optional[dict]:
    """Parse, validate, and save results. Re-upload replaces previous data.

    Returns:
        {"upload_id": str, "student_count": int, "warning": str | None}
    Returns None if the paper doesn't exist.
    Raises ResultsValidationError on structural/content errors."""
    paper = papers_repository.find_by_id(paper_id)
    if paper is None:
        return None

    question_ids = json.loads(paper["question_ids"])
    questions = [questions_repository.find_by_id(qid) for qid in question_ids]
    questions = [q for q in questions if q]

    df = _parse_file(filename, file_bytes)
    _validate(df, questions)

    student_count = len(df)
    settings = settings_service.get_settings()
    class_size = settings.get("class_size", 25)
    min_pct = settings.get("min_analysis_percent", 60)
    required = math.ceil(class_size * min_pct / 100)
    warning: Optional[str] = None
    if student_count < required:
        warning = (
            f"Sirf {student_count} students ka data hai; "
            f"reliable analysis ke liye {required} chahiye "
            f"({class_size} class size × {min_pct}% minimum)."
        )

    result_repository.delete_uploads_for_paper(paper_id)

    upload_id = str(uuid.uuid4())
    result_repository.insert_upload(upload_id=upload_id, paper_id=paper_id, filename=filename)
    for _, row in df.iterrows():
        for idx, q in enumerate(questions):
            marks = int(float(row.iloc[2 + idx]))
            result_repository.insert_student_result(
                result_id=str(uuid.uuid4()),
                result_upload_id=upload_id,
                roll_no=str(row.iloc[0]).strip(),
                student_name=str(row.iloc[1]).strip(),
                question_id=q["id"],
                marks_obtained=marks,
            )

    return {"upload_id": upload_id, "student_count": student_count, "warning": warning}


def get_analysis(paper_id: str) -> Optional[dict]:
    """Topic-wise, Bloom-wise, student-wise breakdown from the latest upload.
    Returns None if the paper has no uploads yet."""
    uploads = result_repository.list_uploads_for_paper(paper_id)
    if not uploads:
        return None
    paper = papers_repository.find_by_id(paper_id)
    if paper is None:
        return None

    question_ids = json.loads(paper["question_ids"])
    q_map = {qid: questions_repository.find_by_id(qid) for qid in question_ids}
    q_map = {k: v for k, v in q_map.items() if v}

    rows = result_repository.list_results_for_upload(uploads[0]["id"])

    settings = settings_service.get_settings()
    threshold = settings.get("weak_topic_threshold", 60)

    students_by_roll: dict = {}
    topic_data: dict = {}
    bloom_data: dict = {}

    for row in rows:
        q = q_map.get(row["question_id"])
        if not q:
            continue
        roll = str(row["roll_no"])
        obtained = row["marks_obtained"]
        max_m = q["marks"]

        s = students_by_roll.setdefault(
            roll,
            {"roll_no": roll, "student_name": row.get("student_name") or roll, "obtained": 0, "max": 0},
        )
        s["obtained"] += obtained
        s["max"] += max_m

        t = topic_data.setdefault(q["topic"], {"obtained": 0.0, "max": 0})
        t["obtained"] += obtained
        t["max"] += max_m

        b = bloom_data.setdefault(q["bloom_level"], {"obtained": 0.0, "max": 0})
        b["obtained"] += obtained
        b["max"] += max_m

    student_list = [
        {
            "roll_no": v["roll_no"],
            "student_name": v["student_name"],
            "marks_obtained": v["obtained"],
            "total_marks": v["max"],
            "percent": _pct(v["obtained"], v["max"]),
        }
        for v in students_by_roll.values()
    ]
    student_list.sort(key=lambda s: s["percent"], reverse=True)
    class_avg = (
        round(sum(s["percent"] for s in student_list) / len(student_list), 1)
        if student_list else 0.0
    )

    topic_scores = sorted(
        [
            {
                "topic": topic,
                "avg_percent": _pct(v["obtained"], v["max"]),
                "is_weak": _pct(v["obtained"], v["max"]) < threshold,
            }
            for topic, v in topic_data.items()
        ],
        key=lambda t: t["avg_percent"],
    )

    bloom_scores = sorted(
        [
            {
                "bloom_level": bloom,
                "avg_percent": _pct(v["obtained"], v["max"]),
                "is_weak": _pct(v["obtained"], v["max"]) < threshold,
            }
            for bloom, v in bloom_data.items()
        ],
        key=lambda b: b["avg_percent"],
    )

    return {
        "paper_id": paper_id,
        "upload_id": uploads[0]["id"],
        "class_avg_percent": class_avg,
        "student_count": len(student_list),
        "topic_scores": topic_scores,
        "bloom_scores": bloom_scores,
        "students": student_list,
        "weak_topics": [t["topic"] for t in topic_scores if t["is_weak"]],
    }


def generate_paper(
    paper_id: str,
    total_questions: int,
    language: Optional[str],
) -> Optional[str]:
    """Generate a topic-weighted adaptive paper and persist it to My Papers.
    Weak topics get proportionally more questions than strong ones.
    Returns new paper_id, or None if the source paper / analysis doesn't exist."""
    analysis = get_analysis(paper_id)
    if not analysis:
        return None
    source_paper = papers_repository.find_by_id(paper_id)
    if not source_paper:
        return None

    subject = source_paper["subject"]
    settings = settings_service.get_settings()
    threshold = settings.get("weak_topic_threshold", 60)

    topic_scores = analysis["topic_scores"]
    weights = {
        t["topic"]: _FLOOR + max(0.0, threshold - t["avg_percent"])
        for t in topic_scores
    }
    distribution = _largest_remainder(weights, total_questions)

    selected_ids: list[str] = []
    selected_questions: list[dict] = []
    for topic, count in distribution.items():
        if count <= 0:
            continue
        qs = _fetch_by_topic(subject, topic, count, language)
        for q in qs:
            selected_ids.append(q["id"])
            selected_questions.append(q)
            questions_repository.increment_usage_count(q["id"])

    if not selected_questions:
        return None

    from_title = source_paper.get("paper_title") or subject
    title = f"Adaptive — {from_title} — {date.today().strftime('%d %b %Y')}"
    total_marks = sum(q["marks"] for q in selected_questions)
    new_id = str(uuid.uuid4())
    papers_repository.insert(
        paper_id=new_id,
        subject=subject,
        class_name=None,
        total_marks=total_marks,
        question_ids=selected_ids,
        paper_title=title,
    )
    return new_id


# ---- private helpers -------------------------------------------------------


def _pct(part: float, whole: float) -> float:
    if whole == 0:
        return 0.0
    return round(part / whole * 100, 1)


def _parse_file(filename: str, file_bytes: bytes) -> pd.DataFrame:
    lower = filename.lower()
    try:
        if lower.endswith(".csv"):
            return pd.read_csv(io.BytesIO(file_bytes))
        if lower.endswith(".xlsx") or lower.endswith(".xls"):
            return pd.read_excel(io.BytesIO(file_bytes))
    except Exception as e:
        raise ValueError(f"File parse fail hui: {e}") from e
    raise ValueError(f"Format support nahi: '{filename}'. .csv ya .xlsx use karen.")


def _validate(df: pd.DataFrame, questions: list) -> None:
    expected = 2 + len(questions)
    if len(df.columns) != expected:
        raise ResultsValidationError(
            [{"row": 1, "issue": f"Columns chahiye {expected}, mile {len(df.columns)}."}]
        )
    errors: list[dict] = []
    for pandas_idx, row in df.iterrows():
        row_no = int(pandas_idx) + 2
        if pd.isna(row.iloc[0]) or str(row.iloc[0]).strip() == "":
            errors.append({"row": row_no, "issue": "roll_no missing."})
        if pd.isna(row.iloc[1]) or str(row.iloc[1]).strip() == "":
            errors.append({"row": row_no, "issue": "student_name missing."})
        for q_idx, q in enumerate(questions):
            val = row.iloc[2 + q_idx]
            if pd.isna(val):
                errors.append({"row": row_no, "issue": f"Q{q_idx + 1} marks missing."})
                continue
            try:
                fval = float(val)
            except (ValueError, TypeError):
                errors.append({"row": row_no, "issue": f"Q{q_idx + 1} number hona chahiye, mila '{val}'."})
                continue
            if not fval.is_integer():
                errors.append({"row": row_no, "issue": f"Q{q_idx + 1} pura number hona chahiye, mila {val}."})
                continue
            marks = int(fval)
            if marks < 0:
                errors.append({"row": row_no, "issue": f"Q{q_idx + 1} marks negative nahi ho sakte."})
            elif marks > q["marks"]:
                errors.append({"row": row_no, "issue": f"Q{q_idx + 1} marks ({marks}) max ({q['marks']}) se zyada hain."})
    if errors:
        raise ResultsValidationError(errors)


def _fetch_by_topic(subject: str, topic: str, limit: int, language: Optional[str]) -> list:
    from app.core.database import get_connection
    conn = get_connection()
    cur = conn.cursor()
    query = "SELECT * FROM questions WHERE subject = ? AND topic = ? AND status = 'published'"
    params: list = [subject, topic]
    if language == "en":
        query += " AND question_en IS NOT NULL AND question_en != ''"
    elif language == "ur":
        query += " AND question_ur IS NOT NULL AND question_ur != ''"
    query += " ORDER BY usage_count ASC LIMIT ?"
    params.append(limit)
    rows = cur.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def _largest_remainder(weights: dict, total: int) -> dict:
    total_weight = sum(weights.values())
    if total_weight <= 0:
        return {k: 0 for k in weights}
    exact = {k: total * w / total_weight for k, w in weights.items()}
    counts = {k: int(v) for k, v in exact.items()}
    remaining = total - sum(counts.values())
    by_remainder = sorted(weights, key=lambda k: exact[k] - counts[k], reverse=True)
    for k in by_remainder[:remaining]:
        counts[k] += 1
    return counts
