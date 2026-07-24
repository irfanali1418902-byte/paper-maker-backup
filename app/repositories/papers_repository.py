"""SQL access for the papers table."""

import json
from typing import Optional

from app.core.database import get_connection


def insert(
    paper_id: str,
    subject: str,
    class_name: Optional[str],
    total_marks: int,
    question_ids: list,
    paper_title: Optional[str] = None,
    sections_meta: Optional[list] = None,
    exam_no: Optional[int] = None,
) -> None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO papers (id, subject, class_name, total_marks, question_ids, paper_title, sections_meta, exam_no) "
        "VALUES (?,?,?,?,?,?,?,?)",
        (
            paper_id, subject, class_name, total_marks,
            json.dumps(question_ids), paper_title,
            json.dumps(sections_meta) if sections_meta is not None else None,
            exam_no,
        ),
    )
    conn.commit()
    conn.close()


def find_papers_containing(question_id: str) -> list[dict]:
    """Woh papers jinke question_ids mein yeh question_id maujood hai —
    [{id, paper_title}] (newest first). Delete-warning ke liye: teacher ko
    dikhao kaun se papers orphan honge. question_ids JSON array ["uuid",...] hai;
    quoted-id se LIKE match (uuid substring false-match se bacha)."""
    conn = get_connection()
    cur = conn.cursor()
    rows = cur.execute(
        "SELECT id, paper_title FROM papers WHERE question_ids LIKE ? ORDER BY created_at DESC",
        (f'%"{question_id}"%',),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def find_by_id(paper_id: str) -> Optional[dict]:
    conn = get_connection()
    cur = conn.cursor()
    row = cur.execute("SELECT * FROM papers WHERE id = ?", (paper_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def count_all() -> int:
    conn = get_connection()
    cur = conn.cursor()
    n = cur.execute("SELECT COUNT(*) FROM papers").fetchone()[0]
    conn.close()
    return n


def top_subject() -> Optional[str]:
    """Subject jiske sab se zyada papers bane hain (ties par alphabetical).
    Koi paper na ho to None."""
    conn = get_connection()
    cur = conn.cursor()
    row = cur.execute(
        "SELECT subject FROM papers GROUP BY subject ORDER BY COUNT(*) DESC, subject ASC LIMIT 1"
    ).fetchone()
    conn.close()
    return row[0] if row else None


def update_question_ids(paper_id: str, question_ids: list, total_marks: int) -> None:
    """Replace a paper's question set + recomputed total in place — used when a
    teacher manually swaps a question in the preview."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE papers SET question_ids = ?, total_marks = ? WHERE id = ?",
        (json.dumps(question_ids), total_marks, paper_id),
    )
    conn.commit()
    conn.close()


def list_all() -> list[dict]:
    """All papers, newest first. question_ids excluded (heavy, not needed for list view)."""
    conn = get_connection()
    cur = conn.cursor()
    rows = cur.execute(
        "SELECT id, paper_title, subject, class_name, total_marks, created_at "
        "FROM papers ORDER BY created_at DESC"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def covered_slo_pairs(exam_no: int, subject: str, class_name: Optional[str]) -> list[dict]:
    """Coverage (Hissa 3) ki core join — SIRF usi exam ke papers se. `question_ids`
    JSON array hai; `json_each` se har id ko row bana kar `question_slo` tak jaate
    hain. Returns distinct [{slo_id, paper_id}].

    AHEM: `p.exam_no = ?` hi "usi exam" ka usool nafiz karta hai — doosre exam (ya
    NULL) ke paper yahan aate hi nahi (SQL mein NULL = ? kabhi true nahi). subject +
    class normalized match (papers.class_name free-text/gandi — data ko haath nahi
    lagate; slo_coverage_service jaisa)."""
    conn = get_connection()
    rows = conn.execute(
        """SELECT DISTINCT qs.slo_id AS slo_id, p.id AS paper_id
           FROM papers p
           JOIN json_each(p.question_ids) je
           JOIN question_slo qs ON qs.question_id = je.value
           WHERE p.exam_no = ?
             AND LOWER(TRIM(p.subject)) = LOWER(TRIM(?))
             AND LOWER(TRIM(COALESCE(p.class_name, ''))) = LOWER(TRIM(?))""",
        (exam_no, subject, class_name or ""),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def covered_pairs_all_exams(subject: str, class_name: Optional[str]) -> list[dict]:
    """Summary (bulk coverage) ke liye — ek hi query mein SAB exams ke (exam_no,
    slo_id) distinct pairs. exam_no NULL wale papers bahar (IS NOT NULL). Caller
    exam_no par group kar ke har exam ka covered-slo set bana leta hai. Isi se N
    alag queries se bachte hain."""
    conn = get_connection()
    rows = conn.execute(
        """SELECT DISTINCT p.exam_no AS exam_no, qs.slo_id AS slo_id
           FROM papers p
           JOIN json_each(p.question_ids) je
           JOIN question_slo qs ON qs.question_id = je.value
           WHERE p.exam_no IS NOT NULL
             AND LOWER(TRIM(p.subject)) = LOWER(TRIM(?))
             AND LOWER(TRIM(COALESCE(p.class_name, ''))) = LOWER(TRIM(?))""",
        (subject, class_name or ""),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def list_by_exam(exam_no: int, subject: str, class_name: Optional[str]) -> list[dict]:
    """Us exam ke papers — [{id, paper_title}] (newest first). Coverage detail mein
    'kis paper mein aaya' dikhane ke liye. subject + class normalized match."""
    conn = get_connection()
    rows = conn.execute(
        """SELECT id, paper_title FROM papers
           WHERE exam_no = ?
             AND LOWER(TRIM(subject)) = LOWER(TRIM(?))
             AND LOWER(TRIM(COALESCE(class_name, ''))) = LOWER(TRIM(?))
           ORDER BY created_at DESC""",
        (exam_no, subject, class_name or ""),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def search(query: str) -> list[dict]:
    """Filter papers by paper_title or subject (case-insensitive LIKE), newest first."""
    pattern = f"%{query}%"
    conn = get_connection()
    cur = conn.cursor()
    rows = cur.execute(
        "SELECT id, paper_title, subject, class_name, total_marks, created_at "
        "FROM papers WHERE paper_title LIKE ? OR subject LIKE ? ORDER BY created_at DESC",
        (pattern, pattern),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]
