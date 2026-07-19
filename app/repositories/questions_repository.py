"""SQL access for the questions table. No business logic, no HTTP."""

from typing import Optional

from app.core.database import get_connection
from app.core.text_norm import normalize_subject


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
            page_number, status, answer_lines)
           VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
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
            question_row.get("answer_lines"),
        ),
    )
    conn.commit()
    conn.close()


def _apply_language_filter(query: str, params: list, language_filter: Optional[str]) -> tuple[str, list]:
    """language_filter='en' → sirf English questions; 'ur' → sirf Urdu; None → sab."""
    if language_filter == "en":
        query += " AND question_en IS NOT NULL AND question_en != ''"
    elif language_filter == "ur":
        query += " AND question_ur IS NOT NULL AND question_ur != ''"
    return query, params


def find_least_used(
    subject: str,
    bloom_level: str,
    difficulty: Optional[str],
    limit: int,
    question_types: Optional[list] = None,
    language_filter: Optional[str] = None,
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
    query, params = _apply_language_filter(query, params, language_filter)
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
    language_filter: Optional[str] = None,
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
    query, params = _apply_language_filter(query, params, language_filter)
    query += " ORDER BY usage_count ASC"
    rows = cur.execute(query, params).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def find_for_blueprint_section(
    subject: Optional[str],
    topic_ids: list,
    question_types: list,
    source: Optional[str],
    status: str = "published",
    difficulty: Optional[str] = None,
    bloom_level: Optional[str] = None,
    language_filter: Optional[str] = None,
) -> list:
    """Blueprint section ke liye filtered query — difficulty/bloom/status/language support.

    status='all' → status filter nahi lagta (draft/archived bhi aate hain).
    topic_ids=[] → koi topic filter nahi.
    difficulty=None → koi difficulty filter nahi.
    bloom_level=None → koi bloom filter nahi.
    language_filter='en' → sirf English; 'ur' → sirf Urdu; None → sab.
    """
    conn = get_connection()
    query = "SELECT * FROM questions WHERE 1=1"
    params: list = []

    if subject:
        query += " AND subject = ?"
        params.append(subject)

    if topic_ids:
        placeholders = ",".join("?" for _ in topic_ids)
        query += f" AND syllabus_topic_id IN ({placeholders})"
        params.extend(topic_ids)

    if question_types:
        type_placeholders = ",".join("?" for _ in question_types)
        query += f" AND question_type IN ({type_placeholders})"
        params.extend(question_types)

    if source:
        query += " AND source = ?"
        params.append(source)

    if status != "all":
        query += " AND status = ?"
        params.append(status)

    if difficulty:
        query += " AND difficulty = ?"
        params.append(difficulty)

    if bloom_level:
        query += " AND bloom_level = ?"
        params.append(bloom_level)

    query, params = _apply_language_filter(query, params, language_filter)

    query += " ORDER BY usage_count ASC"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


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


def list_for_slo_export(
    grade: Optional[str] = None,
    subject: Optional[str] = None,
) -> list:
    """SLO-export ke liye questions — optional grade + subject filter. Koi filter
    na ho to SAARE questions (purana backward-compatible behaviour).

    * grade: `syllabus_topics.grade` par JOIN (case/whitespace-insensitive). Grade
      dene par jin questions ka `syllabus_topic_id` NULL hai wo INNER JOIN se khud
      EXCLUDE hote hain — yeh expected hai.
    * subject: `normalize_subject()` se dono taraf normalize kar ke match
      ('Math' == 'Mathematics'). Python-side filter taake DB variant bhi handle ho.
    """
    conn = get_connection()
    query = "SELECT q.* FROM questions q"
    params: list = []
    if grade:
        query += (
            " JOIN syllabus_topics st ON q.syllabus_topic_id = st.id"
            " WHERE LOWER(TRIM(st.grade)) = LOWER(TRIM(?))"
        )
        params.append(grade)
    rows = conn.execute(query, params).fetchall()
    conn.close()
    result = [dict(row) for row in rows]
    if subject:
        target = normalize_subject(subject)
        result = [r for r in result if normalize_subject(r.get("subject")) == target]
    return result


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
