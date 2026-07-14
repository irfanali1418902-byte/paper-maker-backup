"""Excel se image library ka meta (topic/keywords/category/question_types) bulk update.

Har row ek image ko target karti hai — image_name se DB mein dhundha jata hai.
Ek row fail hone se baaki nahi rukti.
"""

from __future__ import annotations

import io
from typing import Optional

import pandas as pd

from app.core.database import get_connection
from app.repositories import library_repository

# image_name ke ilawa sab optional
REQUIRED_COLUMNS = {"image_name"}

OPTIONAL_META_COLUMNS = {"topic", "subject", "class", "keywords", "category", "question_types"}

ALL_COLUMNS = REQUIRED_COLUMNS | OPTIONAL_META_COLUMNS


# ── topic resolution ──────────────────────────────────────────────────────────

def _resolve_topic(
    topic_name: str,
    subject: Optional[str],
    grade: Optional[str],
) -> tuple[Optional[str], Optional[str], Optional[str]]:
    """topic naam se syllabus_topic_id, subject, grade wapas karo.

    Priority:
    1. subject + grade match
    2. subject-only match
    3. global first match
    Nahi mila to (None, None, None).
    """
    if not topic_name or not topic_name.strip():
        return None, None, None

    needle = topic_name.strip().lower()
    conn = get_connection()
    rows = conn.execute(
        "SELECT id, subject, grade, subtopic_title FROM syllabus_topics"
    ).fetchall()
    conn.close()

    normalised: dict[str, list[tuple[str, str, str]]] = {}
    for row in rows:
        key = row["subtopic_title"].strip().lower()
        normalised.setdefault(key, []).append((row["id"], row["subject"], row["grade"]))

    candidates = normalised.get(needle)
    if not candidates:
        return None, None, None

    subj = (subject or "").strip()
    grd = (grade or "").strip()

    for tid, s, g in candidates:
        if subj and grd and s == subj and g == grd:
            return tid, s, g
    for tid, s, g in candidates:
        if subj and s == subj:
            return tid, s, g
    tid, s, g = candidates[0]
    return tid, s, g


# ── cell helpers ──────────────────────────────────────────────────────────────

def _cell(row: pd.Series, col: str) -> Optional[str]:
    """Row se col ka string value — khali/NaN to None."""
    if col not in row.index:
        return None
    val = row[col]
    if pd.isna(val):
        return None
    s = str(val).strip()
    return s if s else None


# ── main entry point ──────────────────────────────────────────────────────────

def import_meta_from_excel(file_bytes: bytes) -> dict:
    """Excel/CSV bytes parse karo aur image_library mein meta update karo.

    Returns:
        {updated: int, skipped: int, results: [{row, image_name, status, reason}]}
    Raises:
        ValueError: agar image_name column missing ho ya file parse na ho sake.
    """
    try:
        df = pd.read_excel(io.BytesIO(file_bytes), dtype=str)
    except Exception as exc:
        raise ValueError(f"Excel parse nahi hua: {exc}") from exc

    # Column names normalize karo (lowercase + strip)
    df.columns = [str(c).strip().lower() for c in df.columns]

    if "image_name" not in df.columns:
        raise ValueError(
            "Excel mein 'image_name' column zaroori hai lekin mila nahi."
        )

    updated = 0
    skipped = 0
    results = []

    for idx, row in df.iterrows():
        row_num = int(idx) + 2  # 1-based, +1 for header

        image_name = _cell(row, "image_name")
        if not image_name:
            skipped += 1
            results.append({
                "row": row_num,
                "image_name": "(khali)",
                "status": "skip",
                "reason": "image_name khali hai",
            })
            continue

        img = library_repository.find_by_name(image_name)
        if img is None:
            skipped += 1
            results.append({
                "row": row_num,
                "image_name": image_name,
                "status": "skip",
                "reason": "image library mein nahi mili",
            })
            continue

        updates: dict = {}
        warnings: list[str] = []

        # Topic resolution
        topic_val = _cell(row, "topic")
        if topic_val is not None:
            subj_hint = _cell(row, "subject")
            grade_hint = _cell(row, "class")
            topic_id, resolved_subject, resolved_grade = _resolve_topic(
                topic_val, subj_hint, grade_hint
            )
            if topic_id:
                updates["syllabus_topic_id"] = topic_id
                updates["subject"] = resolved_subject
                updates["grade"] = resolved_grade
            else:
                warnings.append(f"topic '{topic_val}' nahi mila — skip")

        # Simple string fields
        for field in ("keywords", "category", "question_types"):
            val = _cell(row, field)
            if val is not None:
                updates[field] = val

        if not updates and not warnings:
            skipped += 1
            results.append({
                "row": row_num,
                "image_name": image_name,
                "status": "skip",
                "reason": "koi bhi field nahi di gayi",
            })
            continue

        if updates:
            library_repository.update_image(img["id"], updates)

        updated += 1
        entry: dict = {"row": row_num, "image_name": image_name, "status": "ok"}
        if warnings:
            entry["warnings"] = warnings
        results.append(entry)

    return {"updated": updated, "skipped": skipped, "results": results}
