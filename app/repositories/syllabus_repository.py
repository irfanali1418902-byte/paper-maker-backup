"""SQL access for the syllabus_topics table."""

import sqlite3
from typing import Optional

from app.core.database import get_connection
from app.services.exceptions import DuplicateSyllabusTopic


def find_by_id(topic_id: str) -> Optional[dict]:
    conn = get_connection()
    cur = conn.cursor()
    row = cur.execute("SELECT * FROM syllabus_topics WHERE id = ?", (topic_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def list_by_filters(
    subject: Optional[str] = None,
    grade: Optional[str] = None,
    from_page: Optional[int] = None,
    to_page: Optional[int] = None,
) -> list:
    conn = get_connection()
    cur = conn.cursor()
    query = "SELECT * FROM syllabus_topics WHERE 1=1"
    params: list = []
    if subject:
        query += " AND subject = ?"
        params.append(subject)
    if grade:
        query += " AND grade = ?"
        params.append(grade)
    if from_page is not None:
        query += " AND page_no >= ?"
        params.append(from_page)
    if to_page is not None:
        query += " AND page_no <= ?"
        params.append(to_page)
    query += " ORDER BY unit_no, page_no"
    rows = cur.execute(query, params).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def list_distinct_subject_grade() -> list:
    conn = get_connection()
    cur = conn.cursor()
    rows = cur.execute(
        "SELECT DISTINCT subject, grade FROM syllabus_topics ORDER BY subject, grade"
    ).fetchall()
    conn.close()
    return [{"subject": row["subject"], "grade": row["grade"]} for row in rows]


def insert(
    topic_id: str,
    subject: str,
    grade: str,
    unit_no: int,
    unit_title: str,
    page_range: str,
    subtopic_title: str,
    activity_type: str,
    page_no: Optional[int],
    learning_outcome: str,
    unit: Optional[str] = None,
) -> None:
    """Used by the CSV/PDF importers. Raises DuplicateSyllabusTopic on a
    UNIQUE-constraint violation so the caller never has to know we're on
    SQLite (CLAUDE.md §2); caller decides what to do with duplicates. The
    connection is closed even on that raise — a leaked connection locks the
    DB file on Windows (§5)."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """INSERT INTO syllabus_topics
               (id, subject, grade, unit_no, unit_title, page_range,
                subtopic_title, activity_type, page_no, learning_outcome, unit)
               VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
            (
                topic_id,
                subject,
                grade,
                unit_no,
                unit_title,
                page_range,
                subtopic_title,
                activity_type,
                page_no,
                learning_outcome,
                unit,
            ),
        )
        conn.commit()
    except sqlite3.IntegrityError as e:
        raise DuplicateSyllabusTopic(subtopic_title) from e
    finally:
        conn.close()


def update_unit(topic_id: str, unit_no: Optional[int], unit_title: Optional[str], unit: Optional[str]) -> bool:
    """Topic ka unit_no, unit_title, aur unit (label) update karo. True agar row mili."""
    updates: dict = {}
    if unit_no is not None:
        updates["unit_no"] = unit_no
    if unit_title is not None:
        updates["unit_title"] = unit_title
    if unit is not None:
        updates["unit"] = unit
    if not updates:
        return False
    conn = get_connection()
    cur = conn.cursor()
    set_clause = ", ".join(f"{k} = ?" for k in updates)
    cur.execute(
        f"UPDATE syllabus_topics SET {set_clause} WHERE id = ?",  # noqa: S608
        list(updates.values()) + [topic_id],
    )
    affected = cur.rowcount
    conn.commit()
    conn.close()
    return affected > 0
