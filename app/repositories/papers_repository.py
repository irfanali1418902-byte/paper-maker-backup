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
    """exam_no: paper kis exam se tag hua (1..N). None/0 = Unassigned — coverage
    isse exam-wise nikalti hai. Purane callers exam_no na bhejein to None rahega."""
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


def list_by_exam(exam_no: int, subject: str, class_name: str) -> list[dict]:
    """Ek exam_no ke DIYE GAYE subject+class ke papers (newest first), list-view
    fields (+ exam_no). Coverage card 'is exam ke papers' dikhane ke liye. subject+
    class normalized match (LOWER(TRIM)) — warna doosre subject/class ke same-exam_no
    papers bhi aa jaate; class_name NULL wale khud bahar. question_ids excluded (heavy)."""
    conn = get_connection()
    cur = conn.cursor()
    rows = cur.execute(
        "SELECT id, paper_title, subject, class_name, total_marks, exam_no, created_at "
        "FROM papers WHERE exam_no = ? "
        "  AND LOWER(TRIM(subject)) = LOWER(TRIM(?)) "
        "  AND LOWER(TRIM(class_name)) = LOWER(TRIM(?)) "
        "ORDER BY created_at DESC",
        (exam_no, subject, class_name),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def covered_slo_pairs(exam_no: int, subject: str, class_name: str) -> set:
    """Ek exam ke papers ke sawalon se cover hue distinct slo_id ka SET — sirf DIYE
    GAYE subject+class ke papers (warna doosre subject/class ke papers jinka exam_no
    same ho leak ho jaate). papers.class_name free-text/gandi hai is liye compare-time
    LOWER(TRIM(...)) normalize (slo_coverage_service jaisa) — data ko haath nahi.
    class_name NULL wale papers khud bahar (NULL match nahi karta).
    question_ids (JSON) json_each se expand -> question_slo JOIN -> slo_id. Orphan
    link INNER JOIN se drop. Membership-test ke liye set."""
    conn = get_connection()
    rows = conn.execute(
        """SELECT DISTINCT qs.slo_id
           FROM papers p, json_each(p.question_ids) je
           JOIN question_slo qs ON qs.question_id = je.value
           WHERE p.exam_no = ?
             AND LOWER(TRIM(p.subject)) = LOWER(TRIM(?))
             AND LOWER(TRIM(p.class_name)) = LOWER(TRIM(?))""",
        (exam_no, subject, class_name),
    ).fetchall()
    conn.close()
    return {row["slo_id"] for row in rows}


def covered_pairs_all_exams(subject: str, class_name: str) -> list[dict]:
    """Har (exam_no, slo_id) coverage-jodi — DIYE GAYE subject+class ke TAMAM tagged
    papers par (exam_no IS NOT NULL). Cross-exam analysis ka data: ek SLO exam 2 ke
    liye planned tha magar exam 3 ke paper ne cover kar diya — service isse pakadti
    hai. subject+class normalized match (LOWER(TRIM)) taake doosre subject/class ke
    papers na ginein; class_name NULL wale khud bahar. json_each se question_ids
    expand -> question_slo JOIN. Distinct jodi."""
    conn = get_connection()
    rows = conn.execute(
        """SELECT DISTINCT p.exam_no, qs.slo_id
           FROM papers p, json_each(p.question_ids) je
           JOIN question_slo qs ON qs.question_id = je.value
           WHERE p.exam_no IS NOT NULL
             AND LOWER(TRIM(p.subject)) = LOWER(TRIM(?))
             AND LOWER(TRIM(p.class_name)) = LOWER(TRIM(?))""",
        (subject, class_name),
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]
