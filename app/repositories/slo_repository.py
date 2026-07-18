"""SQL access for the slo (Student Learning Outcomes) table. No business logic, no HTTP."""

from typing import Optional

from app.core.database import get_connection


def insert(row: dict) -> None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """INSERT INTO slo
           (id, class, subject, slo_code, slo_text, bloom_level, strand)
           VALUES (?,?,?,?,?,?,?)""",
        (
            row["id"],
            row["class"],
            row["subject"],
            row["slo_code"],
            row["slo_text"],
            row.get("bloom_level"),
            row.get("strand"),
        ),
    )
    conn.commit()
    conn.close()


def find_by_code(slo_code: str) -> Optional[dict]:
    """slo_code (UNIQUE) se ek SLO wapas karo, warna None."""
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM slo WHERE slo_code = ? LIMIT 1", (slo_code,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def update_by_code(slo_code: str, updates: dict) -> bool:
    """Is slo_code par sirf diye gaye fields update karo (created_at untouched)."""
    if not updates:
        return False
    conn = get_connection()
    cur = conn.cursor()
    set_clause = ", ".join(f"{k} = ?" for k in updates)
    values = list(updates.values()) + [slo_code]
    cur.execute(f"UPDATE slo SET {set_clause} WHERE slo_code = ?", values)  # noqa: S608
    affected = cur.rowcount
    conn.commit()
    conn.close()
    return affected > 0


def list_by_class_subject_normalized(class_name: str, subject: str) -> list:
    """Coverage universe — class + subject dono par CASE/whitespace-insensitive
    match (LOWER(TRIM(...))). papers.class_name free-text/gandi hai (e.g.
    'NUrsery' vs 'Nursery'), is liye compare-time normalize — data ko haath nahi
    lagate. slo_code se sorted. Koi row na mile to [] (universe unavailable)."""
    conn = get_connection()
    rows = conn.execute(
        """SELECT * FROM slo
           WHERE LOWER(TRIM(class)) = LOWER(TRIM(?))
             AND LOWER(TRIM(subject)) = LOWER(TRIM(?))
           ORDER BY slo_code""",
        (class_name, subject),
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def list_by_filters(
    class_name: Optional[str] = None,
    subject: Optional[str] = None,
    strand: Optional[str] = None,
) -> list:
    """class/subject/strand par filter kar ke SLO list karo (slo_code se sorted)."""
    conn = get_connection()
    where = "WHERE 1=1"
    params: list = []
    if class_name:
        where += " AND class = ?"
        params.append(class_name)
    if subject:
        where += " AND subject = ?"
        params.append(subject)
    if strand:
        where += " AND strand = ?"
        params.append(strand)
    rows = conn.execute(
        f"SELECT * FROM slo {where} ORDER BY slo_code",  # noqa: S608
        params,
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]
