"""SQL access for the image_library table. No business logic, no HTTP."""

from typing import Optional

from app.core.database import get_connection


def insert(row: dict) -> None:
    conn = get_connection()
    cur = conn.cursor()
    name_normalized = row["name"].strip().lower()
    cur.execute(
        """INSERT INTO image_library
           (id, file_path, name, name_normalized, subject, grade, syllabus_topic_id, uploaded_by)
           VALUES (?,?,?,?,?,?,?,?)""",
        (
            row["id"],
            row["file_path"],
            row["name"],
            name_normalized,
            row.get("subject"),
            row.get("grade"),
            row.get("syllabus_topic_id"),
            row.get("uploaded_by"),
        ),
    )
    conn.commit()
    conn.close()


def name_exists(name: str) -> bool:
    """True agar is normalized naam ki koi image pehle se library mein ho."""
    conn = get_connection()
    row = conn.execute(
        "SELECT id FROM image_library WHERE name_normalized = ?",
        (name.strip().lower(),),
    ).fetchone()
    conn.close()
    return row is not None


def name_exists_excluding(name: str, exclude_id: str) -> bool:
    """True agar is naam ki koi DOOSRI image (exclude_id ke ilawa) library mein ho."""
    conn = get_connection()
    row = conn.execute(
        "SELECT id FROM image_library WHERE name_normalized = ? AND id != ?",
        (name.strip().lower(), exclude_id),
    ).fetchone()
    conn.close()
    return row is not None


def update_image(image_id: str, updates: dict) -> bool:
    """image_library row mein sirf diye gaye fields update karo."""
    if not updates:
        return False
    conn = get_connection()
    cur = conn.cursor()
    set_clause = ", ".join(f"{k} = ?" for k in updates)
    values = list(updates.values()) + [image_id]
    cur.execute(f"UPDATE image_library SET {set_clause} WHERE id = ?", values)  # noqa: S608
    affected = cur.rowcount
    conn.commit()
    conn.close()
    return affected > 0


def bulk_update_topic(
    image_ids: list,
    syllabus_topic_id: "Optional[str]",
    subject: "Optional[str]",
    grade: "Optional[str]",
) -> int:
    """Kai images ka topic (aur subject/grade) ek saath update karo. Updated count wapas."""
    if not image_ids:
        return 0
    conn = get_connection()
    cur = conn.cursor()
    placeholders = ",".join("?" for _ in image_ids)
    values = [syllabus_topic_id, subject, grade] + image_ids
    cur.execute(
        f"UPDATE image_library SET syllabus_topic_id = ?, subject = ?, grade = ?"  # noqa: S608
        f" WHERE id IN ({placeholders})",
        values,
    )
    affected = cur.rowcount
    conn.commit()
    conn.close()
    return affected


def find_by_name(name: str) -> "Optional[dict]":
    """Case-insensitive naam se pehli matching image wapas karo."""
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM image_library WHERE name_normalized = ? LIMIT 1",
        (name.strip().lower(),),
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def find_by_name_and_topic(name: str, syllabus_topic_id: str) -> "Optional[dict]":
    """Topic-scoped naam match — bulk import ke liye (topic-first priority)."""
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM image_library"
        " WHERE name_normalized = ? AND syllabus_topic_id = ? LIMIT 1",
        (name.strip().lower(), syllabus_topic_id),
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def find_by_id(image_id: str) -> Optional[dict]:
    conn = get_connection()
    cur = conn.cursor()
    row = cur.execute("SELECT * FROM image_library WHERE id = ?", (image_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def list_by_filters(
    subject: Optional[str] = None,
    grade: Optional[str] = None,
    syllabus_topic_id: Optional[str] = None,
    q: Optional[str] = None,
) -> list:
    conn = get_connection()
    cur = conn.cursor()
    query = "SELECT * FROM image_library WHERE 1=1"
    params: list = []
    if subject:
        query += " AND subject = ?"
        params.append(subject)
    if grade:
        query += " AND grade = ?"
        params.append(grade)
    if syllabus_topic_id:
        query += " AND syllabus_topic_id = ?"
        params.append(syllabus_topic_id)
    if q:
        query += " AND name LIKE ?"
        params.append(f"%{q}%")
    query += " ORDER BY created_at DESC"
    rows = cur.execute(query, params).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def delete(image_id: str) -> bool:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM image_library WHERE id = ?", (image_id,))
    affected = cur.rowcount
    conn.commit()
    conn.close()
    return affected > 0


def topic_ids_with_images(ids: list) -> set:
    """Given a list of syllabus_topic_ids, return the subset that has >= 1 library image."""
    if not ids:
        return set()
    conn = get_connection()
    cur = conn.cursor()
    placeholders = ",".join("?" for _ in ids)
    rows = cur.execute(
        f"SELECT DISTINCT syllabus_topic_id FROM image_library WHERE syllabus_topic_id IN ({placeholders})",  # noqa: S608
        ids,
    ).fetchall()
    conn.close()
    return {row[0] for row in rows}


def topic_image_counts(ids: list) -> dict:
    """Given a list of syllabus_topic_ids, return {topic_id: count} for those with >= 1 image."""
    if not ids:
        return {}
    conn = get_connection()
    cur = conn.cursor()
    placeholders = ",".join("?" for _ in ids)
    rows = cur.execute(
        f"SELECT syllabus_topic_id, COUNT(*) FROM image_library"  # noqa: S608
        f" WHERE syllabus_topic_id IN ({placeholders})"
        f" GROUP BY syllabus_topic_id",
        ids,
    ).fetchall()
    conn.close()
    return {row[0]: row[1] for row in rows}
