"""SQL access for the questions table. No business logic, no HTTP."""

from typing import Optional

from app.core.database import get_connection


def insert(question_row: dict) -> None:
    """Inserts one fully-formed question. Caller is responsible for
    pre-computing every column value (uuid, marks, JSON-encoded options, etc.)."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """INSERT INTO questions
           (id, subject, topic, bloom_level, difficulty, question_type, marks,
            question_en, question_ur, options_en, options_ur,
            correct_answer_en, correct_answer_ur, explanation_en, explanation_ur,
            visual_emoji, visual_count, syllabus_topic_id, image_path, image_size,
            source, learning_outcome, estimated_time, keywords, source_book,
            page_number, status)
           VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (
            question_row["id"],
            question_row["subject"],
            question_row["topic"],
            question_row["bloom_level"],
            question_row["difficulty"],
            question_row["question_type"],
            question_row["marks"],
            question_row["question_en"],
            question_row["question_ur"],
            question_row["options_en"],
            question_row["options_ur"],
            question_row["correct_answer_en"],
            question_row["correct_answer_ur"],
            question_row["explanation_en"],
            question_row["explanation_ur"],
            question_row["visual_emoji"],
            question_row["visual_count"],
            question_row.get("syllabus_topic_id"),
            question_row.get("image_path"),
            question_row.get("image_size"),
            question_row.get("source", "gemini"),
            question_row.get("learning_outcome"),
            question_row.get("estimated_time"),
            question_row.get("keywords"),
            question_row.get("source_book"),
            question_row.get("page_number"),
            question_row.get("status", "published"),
        ),
    )
    conn.commit()
    conn.close()


def find_least_used(
    subject: str,
    bloom_level: str,
    difficulty: Optional[str],
    limit: int,
    question_types: Optional[list] = None,
) -> list:
    """Returns N matching questions ordered by usage_count ASC (least-used first).
    question_types diya jaye to sirf un types ke questions (IN filter)."""
    conn = get_connection()
    cur = conn.cursor()
    query = "SELECT * FROM questions WHERE subject = ? AND bloom_level = ?"
    params: list = [subject, bloom_level]
    if difficulty:
        query += " AND difficulty = ?"
        params.append(difficulty)
    if question_types:
        placeholders = ",".join("?" for _ in question_types)
        query += f" AND question_type IN ({placeholders})"
        params.extend(question_types)
    query += " ORDER BY usage_count ASC LIMIT ?"
    params.append(limit)
    rows = cur.execute(query, params).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def increment_usage_count(question_id: str) -> None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE questions SET usage_count = usage_count + 1 WHERE id = ?", (question_id,))
    conn.commit()
    conn.close()


def update(question_id: str, fields: dict) -> bool:
    """Updates only the provided fields on a question. Returns True if the row
    existed, False if question_id was not found."""
    if not fields:
        return find_by_id(question_id) is not None
    cols = ", ".join(f"{k} = ?" for k in fields)
    params = list(fields.values()) + [question_id]
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(f"UPDATE questions SET {cols} WHERE id = ?", params)  # noqa: S608
    affected = cur.rowcount
    conn.commit()
    conn.close()
    return affected > 0


def find_by_id(question_id: str) -> Optional[dict]:
    conn = get_connection()
    cur = conn.cursor()
    row = cur.execute("SELECT * FROM questions WHERE id = ?", (question_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def delete(question_id: str) -> bool:
    """Sirf source='manual' wale delete honge. Returns True if deleted."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM questions WHERE id = ? AND source = 'manual'", (question_id,))
    affected = cur.rowcount
    conn.commit()
    conn.close()
    return affected > 0


def count_all() -> int:
    conn = get_connection()
    cur = conn.cursor()
    n = cur.execute("SELECT COUNT(*) FROM questions").fetchone()[0]
    conn.close()
    return n


def find_for_bank_paper(
    subject: Optional[str] = None,
    syllabus_topic_id: Optional[str] = None,
    question_types: Optional[list] = None,
    source: Optional[str] = None,
) -> list:
    """Bloom distribution ke bina direct query — bank-paper assembly ke liye.
    source=None means sab, source='manual' means sirf teacher-written."""
    conn = get_connection()
    cur = conn.cursor()
    query = "SELECT * FROM questions WHERE 1=1"
    params: list = []
    if subject:
        query += " AND subject = ?"
        params.append(subject)
    if syllabus_topic_id:
        query += " AND syllabus_topic_id = ?"
        params.append(syllabus_topic_id)
    if question_types:
        placeholders = ",".join("?" for _ in question_types)
        query += f" AND question_type IN ({placeholders})"
        params.extend(question_types)
    if source:
        query += " AND source = ?"
        params.append(source)
    query += " ORDER BY usage_count ASC"
    rows = cur.execute(query, params).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def list_by_filters(
    subject: Optional[str] = None,
    topic: Optional[str] = None,
    bloom_level: Optional[str] = None,
    syllabus_topic_id: Optional[str] = None,
    q: Optional[str] = None,
    status: Optional[str] = None,
) -> list:
    conn = get_connection()
    cur = conn.cursor()
    query = "SELECT * FROM questions WHERE 1=1"
    params: list = []
    if subject:
        query += " AND subject = ?"
        params.append(subject)
    if topic:
        query += " AND topic = ?"
        params.append(topic)
    if bloom_level:
        query += " AND bloom_level = ?"
        params.append(bloom_level)
    if syllabus_topic_id:
        query += " AND syllabus_topic_id = ?"
        params.append(syllabus_topic_id)
    if q:
        like = f"%{q}%"
        query += " AND (question_en LIKE ? OR question_ur LIKE ? OR keywords LIKE ?)"
        params.extend([like, like, like])
    if status:
        query += " AND status = ?"
        params.append(status)
    rows = cur.execute(query, params).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def bulk_update_meta(
    question_ids: list,
    fields: dict,
    keywords_mode: str = "replace",
) -> int:
    """Kai questions ke smart fields ek saath update karo. Returns count of updated rows."""
    if not question_ids or not fields:
        return 0

    conn = get_connection()
    cur = conn.cursor()
    updated = 0

    if "keywords" in fields and keywords_mode == "append":
        kw_new_set = {kw.strip() for kw in (fields.get("keywords") or "").split(",") if kw.strip()}
        other_fields = {k: v for k, v in fields.items() if k != "keywords"}
        for qid in question_ids:
            row = cur.execute("SELECT keywords FROM questions WHERE id = ?", (qid,)).fetchone()
            if row is None:
                continue
            existing_set = {kw.strip() for kw in (row[0] or "").split(",") if kw.strip()}
            merged = existing_set | kw_new_set
            merged_str = ", ".join(sorted(merged)) if merged else None
            upd = {"keywords": merged_str, **other_fields}
            cols = ", ".join(f"{k} = ?" for k in upd)
            cur.execute(f"UPDATE questions SET {cols} WHERE id = ?", [*upd.values(), qid])  # noqa: S608
            updated += cur.rowcount
    else:
        placeholders = ",".join("?" for _ in question_ids)
        cols = ", ".join(f"{k} = ?" for k in fields)
        cur.execute(
            f"UPDATE questions SET {cols} WHERE id IN ({placeholders})",  # noqa: S608
            [*fields.values(), *question_ids],
        )
        updated = cur.rowcount

    conn.commit()
    conn.close()
    return updated
