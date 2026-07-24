"""SQL access for the slo_exam_plan table (SLO -> exam assignment). No business logic.

Ek row per SLO: kaunsi exam (exam_no 1..N; 0 = Unassigned). class/subject slo se JOIN
par milte hain (slo_id ek hi class+subject ka), is liye yahan store nahi hote."""

from app.core.database import get_connection


def list_resolved(class_name: str, subject: str) -> list:
    """Us (class, subject) ke SAARE SLO — apne exam_no/position ke saath (LEFT JOIN,
    to plan-less SLO bhi aate hain, exam_no NULL). Ordering: exam_no, phir teacher ka
    position, phir asal teaching sequence, phir slo_code. Exact class/subject match
    (/api/slo jaisa — facets se aaye values guaranteed match)."""
    conn = get_connection()
    rows = conn.execute(
        """SELECT s.id AS slo_id, s.slo_code, s.slo_text, s.bloom_level, s.strand,
                  s.sequence, p.exam_no, p.position
           FROM slo s
           LEFT JOIN slo_exam_plan p ON p.slo_id = s.id
           WHERE s.class = ? AND s.subject = ?
           ORDER BY COALESCE(p.exam_no, 9999),
                    COALESCE(p.position, 999999),
                    COALESCE(s.sequence, 999999),
                    s.slo_code""",
        (class_name, subject),
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def list_planned(class_name: str, subject: str, exam_no: int) -> list:
    """Ek (class, subject, exam_no) ke liye PLANNED SLO — poore slo fields (slo_code,
    slo_text, strand, bloom_level) + position. INNER JOIN (sirf woh SLO jinka plan is
    exam mein hai). Ye exam-coverage ka 'universe' hai: is exam mein kya-kya cover
    hona chahiye. Ordering list_resolved jaisa (position -> sequence -> slo_code).
    Exact class/subject match (facets se aaye values guaranteed match)."""
    conn = get_connection()
    rows = conn.execute(
        """SELECT s.id AS slo_id, s.slo_code, s.slo_text, s.strand, s.bloom_level,
                  s.sequence, p.position
           FROM slo_exam_plan p
           JOIN slo s ON s.id = p.slo_id
           WHERE s.class = ? AND s.subject = ? AND p.exam_no = ?
           ORDER BY COALESCE(p.position, 999999),
                    COALESCE(s.sequence, 999999),
                    s.slo_code""",
        (class_name, subject, exam_no),
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def overwrite_assignments(assignments: list) -> int:
    """Bulk upsert: har SLO ka exam_no/position set (ya update). slo_id PK par
    ON CONFLICT — pehle se maujood row overwrite ho jaati hai. Sab ek hi transaction
    mein (executemany + ek commit), taake plan half-written na reh jaye.

    assignments: [{"slo_id": str, "exam_no": int, "position": int|None}, ...].
    Business logic (split, sequence sort) service mein hai — yahan sirf likhna.
    Rows affected wapas."""
    if not assignments:
        return 0
    conn = get_connection()
    cur = conn.cursor()
    cur.executemany(
        """INSERT INTO slo_exam_plan (slo_id, exam_no, position, updated_at)
           VALUES (?, ?, ?, CURRENT_TIMESTAMP)
           ON CONFLICT(slo_id) DO UPDATE SET
             exam_no=excluded.exam_no,
             position=excluded.position,
             updated_at=CURRENT_TIMESTAMP""",
        [(a["slo_id"], a["exam_no"], a["position"]) for a in assignments],
    )
    affected = cur.rowcount
    conn.commit()
    conn.close()
    return affected
