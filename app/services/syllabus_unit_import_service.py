"""Excel se syllabus topics ka unit field bulk update karo.

Har row ek topic ko target karti hai — subtopic_title se DB mein dhundha jata hai.
subject/grade hint priority: subject+grade > subject-only > global first.
Ek row fail hone se baaki nahi rukti.
"""

from __future__ import annotations

import io
from typing import Optional

import pandas as pd

from app.core.database import get_connection
from app.repositories import syllabus_repository  # noqa: E402

# ── topic lookup ──────────────────────────────────────────────────────────────

def _resolve_topic_id(
    subtopic_title: str,
    subject: Optional[str],
    grade: Optional[str],
) -> Optional[str]:
    """subtopic_title se topic_id dhundho — subject+grade hint priority."""
    if not subtopic_title or not subtopic_title.strip():
        return None

    needle = subtopic_title.strip().lower()
    conn = get_connection()
    rows = conn.execute(
        "SELECT id, subject, grade, subtopic_title FROM syllabus_topics"
    ).fetchall()
    conn.close()

    normalised: dict[str, list[tuple]] = {}
    for row in rows:
        key = row["subtopic_title"].strip().lower()
        normalised.setdefault(key, []).append((row["id"], row["subject"], row["grade"]))

    candidates = normalised.get(needle)
    if not candidates:
        return None

    subj = (subject or "").strip()
    grd = (grade or "").strip()

    for tid, s, g in candidates:
        if subj and grd and s == subj and g == grd:
            return tid
    for tid, s, _g in candidates:
        if subj and s == subj:
            return tid
    return candidates[0][0]


# ── cell helper ───────────────────────────────────────────────────────────────

def _cell(row: pd.Series, col: str) -> Optional[str]:
    if col not in row.index:
        return None
    val = row[col]
    if pd.isna(val):
        return None
    s = str(val).strip()
    return s if s else None


# ── main entry point ──────────────────────────────────────────────────────────

def import_units_from_excel(file_bytes: bytes) -> dict:
    """Excel bytes parse karo aur syllabus_topics mein unit field update karo.

    Required column: subtopic_title
    Optional columns: subject, grade, unit_no, unit_title, unit

    Returns:
        {updated: int, skipped: int, results: [{row, subtopic_title, status, reason?}]}
    Raises:
        ValueError: agar subtopic_title column missing ho ya file parse na ho.
    """
    try:
        df = pd.read_excel(io.BytesIO(file_bytes), dtype=str)
    except Exception as exc:
        raise ValueError(f"Excel parse nahi hua: {exc}") from exc

    df.columns = [str(c).strip().lower() for c in df.columns]

    if "subtopic_title" not in df.columns:
        raise ValueError(
            "Excel mein 'subtopic_title' column zaroori hai lekin mila nahi."
        )

    updated = 0
    skipped = 0
    results = []

    for idx, row in df.iterrows():
        row_num = int(idx) + 2

        subtopic = _cell(row, "subtopic_title")
        if not subtopic:
            skipped += 1
            results.append({
                "row": row_num,
                "subtopic_title": "(khali)",
                "status": "skip",
                "reason": "subtopic_title khali hai",
            })
            continue

        subject = _cell(row, "subject")
        grade = _cell(row, "grade")

        topic_id = _resolve_topic_id(subtopic, subject, grade)
        if topic_id is None:
            skipped += 1
            results.append({
                "row": row_num,
                "subtopic_title": subtopic,
                "status": "skip",
                "reason": "topic DB mein nahi mila",
            })
            continue

        # unit_no integer parse
        unit_no_val: Optional[int] = None
        raw_unit_no = _cell(row, "unit_no")
        if raw_unit_no is not None:
            try:
                unit_no_val = int(float(raw_unit_no))
            except ValueError:
                pass  # invalid → skip field

        unit_title_val = _cell(row, "unit_title")
        unit_val = _cell(row, "unit")

        if unit_no_val is None and unit_title_val is None and unit_val is None:
            skipped += 1
            results.append({
                "row": row_num,
                "subtopic_title": subtopic,
                "status": "skip",
                "reason": "koi bhi unit field nahi di gayi",
            })
            continue

        syllabus_repository.update_unit(topic_id, unit_no_val, unit_title_val, unit_val)
        updated += 1
        results.append({"row": row_num, "subtopic_title": subtopic, "status": "ok"})

    return {"updated": updated, "skipped": skipped, "results": results}
