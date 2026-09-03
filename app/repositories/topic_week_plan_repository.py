"""SQL access for the topic_week_plan table (syllabus topic -> hafta). No business logic.

Ek row per topic: kaunsa hafta (week_no 1..N; 0 = Unassigned). subject/grade
syllabus_topics se JOIN par milte hain (topic id ek hi subject+grade ka), is liye
yahan store nahi hote.

`slo_exam_plan_repository` ka aaina -- shape, ordering aur upsert wahan se liye gaye
hain taake dono plan ek jaise chalein. Tafseel: docs/TOPIC_WEEK_PLAN.md
"""

from app.core.database import get_connection


def list_resolved(subject: str, grade: str) -> list:
    """Us (subject, grade) ke SAARE topics -- apne week_no/position ke saath (LEFT
    JOIN, to plan-less topic bhi aate hain, week_no NULL). Ordering: week_no, phir
    teacher ka position, phir syllabus ki apni tarteeb (unit_no -> page_no), phir
    title. Exact subject/grade match (/api/syllabus-grades se aaye values guaranteed
    match)."""
    conn = get_connection()
    rows = conn.execute(
        """SELECT t.id AS syllabus_topic_id, t.subtopic_title, t.unit_no, t.unit_title,
                  t.page_no, t.activity_type, p.week_no, p.position
           FROM syllabus_topics t
           LEFT JOIN topic_week_plan p ON p.syllabus_topic_id = t.id
           WHERE t.subject = ? AND t.grade = ?
           ORDER BY COALESCE(p.week_no, 9999),
                    COALESCE(p.position, 999999),
                    COALESCE(t.unit_no, 999999),
                    COALESCE(t.page_no, 999999),
                    t.subtopic_title""",
        (subject, grade),
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def list_planned(subject: str, grade: str, week_no: int) -> list:
    """Ek (subject, grade, week_no) ke liye PLANNED topics -- poore topic fields +
    position. INNER JOIN (sirf woh topics jinka plan is hafte mein hai). Ye
    week-coverage ka 'universe' hai: is hafte kya-kya parhaya jana chahiye.
    Ordering list_resolved jaisi."""
    conn = get_connection()
    rows = conn.execute(
        """SELECT t.id AS syllabus_topic_id, t.subtopic_title, t.unit_no, t.unit_title,
                  t.page_no, t.activity_type, p.position
           FROM topic_week_plan p
           JOIN syllabus_topics t ON t.id = p.syllabus_topic_id
           WHERE t.subject = ? AND t.grade = ? AND p.week_no = ?
           ORDER BY COALESCE(p.position, 999999),
                    COALESCE(t.unit_no, 999999),
                    COALESCE(t.page_no, 999999),
                    t.subtopic_title""",
        (subject, grade, week_no),
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def overwrite_assignments(assignments: list) -> int:
    """Bulk upsert: har topic ka week_no/position set (ya update). syllabus_topic_id
    PK par ON CONFLICT -- pehle se maujood row overwrite ho jaati hai. Sab ek hi
    transaction mein (executemany + ek commit), taake plan half-written na reh jaye.

    assignments: [{"syllabus_topic_id": str, "week_no": int, "position": int|None}, ...].
    Business logic (validate, sort) service mein hai -- yahan sirf likhna.
    Rows affected wapas."""
    if not assignments:
        return 0
    conn = get_connection()
    cur = conn.cursor()
    cur.executemany(
        """INSERT INTO topic_week_plan (syllabus_topic_id, week_no, position, updated_at)
           VALUES (?, ?, ?, CURRENT_TIMESTAMP)
           ON CONFLICT(syllabus_topic_id) DO UPDATE SET
             week_no=excluded.week_no,
             position=excluded.position,
             updated_at=CURRENT_TIMESTAMP""",
        [(a["syllabus_topic_id"], a["week_no"], a["position"]) for a in assignments],
    )
    affected = cur.rowcount
    conn.commit()
    conn.close()
    return affected


def clear_assignments(topic_ids: list) -> int:
    """In topics ka plan hata do (row delete). Excel ka khali cell = clear
    (replace-set semantics) -- Marhala 2 isay use karega, magar `week_no` NOT NULL
    hai to "clear" ka matlab row ka na hona hi hai, 0 likhna nahi. Rows deleted."""
    if not topic_ids:
        return 0
    conn = get_connection()
    cur = conn.cursor()
    placeholders = ",".join("?" * len(topic_ids))
    cur.execute(
        f"DELETE FROM topic_week_plan WHERE syllabus_topic_id IN ({placeholders})",
        topic_ids,
    )
    deleted = cur.rowcount
    conn.commit()
    conn.close()
    return deleted


def existing_topic_ids(topic_ids: list) -> set:
    """In mein se kaunse topic ids waqai syllabus_topics mein hain. Import ka
    "ghalat id par saaf error" isi par khara hoga (Marhala 2), aur service ka
    move bhi 404 isi se nikalta hai."""
    if not topic_ids:
        return set()
    conn = get_connection()
    placeholders = ",".join("?" * len(topic_ids))
    rows = conn.execute(
        f"SELECT id FROM syllabus_topics WHERE id IN ({placeholders})",
        topic_ids,
    ).fetchall()
    conn.close()
    return {row["id"] for row in rows}
