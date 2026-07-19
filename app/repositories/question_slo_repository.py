"""SQL access for the question_slo link table (question <-> SLO, many-to-many).
No business logic, no HTTP. Marhala 1."""

from app.core.database import get_connection


def list_slo_ids_for_question(question_id: str) -> list:
    """Is question ke saare linked slo_id (created_at se sorted, purane pehle)."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT slo_id FROM question_slo WHERE question_id = ? ORDER BY created_at",
        (question_id,),
    ).fetchall()
    conn.close()
    return [row["slo_id"] for row in rows]


def list_slos_for_question(question_id: str) -> list:
    """Is question ke linked SLO — poore slo row (slo_code, slo_text, strand samet)
    JOIN se. Orphan link (SLO delete ho gayi) INNER JOIN se khud hat jaata hai."""
    conn = get_connection()
    rows = conn.execute(
        """SELECT s.* FROM question_slo qs
           JOIN slo s ON s.id = qs.slo_id
           WHERE qs.question_id = ?
           ORDER BY s.slo_code""",
        (question_id,),
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def list_question_ids_for_slo(slo_id: str) -> list:
    """Reverse lookup — is SLO se jude saare question_id (Marhala 2 coverage)."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT question_id FROM question_slo WHERE slo_id = ?",
        (slo_id,),
    ).fetchall()
    conn.close()
    return [row["question_id"] for row in rows]


def list_links_for_questions(question_ids: list) -> list:
    """Diye gaye question_ids ke saare (question_id -> SLO) link — SLO fields
    JOIN se (slo_code, slo_text, strand, class, subject). Coverage report ki base
    query: ek `IN (...)` mein poore paper ke covered SLO. Orphan link INNER JOIN se
    khud drop. Empty list de to empty result."""
    if not question_ids:
        return []
    unique_ids = list(dict.fromkeys(question_ids))
    placeholders = ",".join("?" for _ in unique_ids)
    conn = get_connection()
    rows = conn.execute(
        f"""SELECT qs.question_id, s.id AS slo_id, s.slo_code, s.slo_text,
                   s.strand, s.class AS slo_class, s.subject AS slo_subject
            FROM question_slo qs
            JOIN slo s ON s.id = qs.slo_id
            WHERE qs.question_id IN ({placeholders})""",  # noqa: S608
        unique_ids,
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def list_slo_blooms_for_questions(question_ids: list) -> list:
    """Diye gaye question_ids ke liye (question_id -> SLO.bloom_level) rows —
    Bloom shortfall report ki base (Marhala 2 Hissa B). Ek question kai SLO se
    juda ho to kai rows (caller "highest" level lega). Orphan link INNER JOIN se
    khud drop. bloom_level NULL bhi aa sakta (SLO tagged par bloom khali) —
    caller usay 'bloom-unknown' alag ginta hai. Empty list de to empty result.

    (Coverage ke `list_links_for_questions` se ALAG rakha — woh shared function
    chherne se coverage ki query badalti; yeh focused hai.)"""
    if not question_ids:
        return []
    unique_ids = list(dict.fromkeys(question_ids))
    placeholders = ",".join("?" for _ in unique_ids)
    conn = get_connection()
    rows = conn.execute(
        f"""SELECT qs.question_id, s.bloom_level
            FROM question_slo qs
            JOIN slo s ON s.id = qs.slo_id
            WHERE qs.question_id IN ({placeholders})""",  # noqa: S608
        unique_ids,
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def all_codes_by_question() -> dict:
    """Har question_id ke current slo_code (sorted) — ek JOIN se, export ke liye.
    Returns { question_id: [slo_code, ...] }. Orphan link INNER JOIN se drop."""
    conn = get_connection()
    rows = conn.execute(
        """SELECT qs.question_id, s.slo_code
           FROM question_slo qs
           JOIN slo s ON s.id = qs.slo_id
           ORDER BY s.slo_code"""
    ).fetchall()
    conn.close()
    out: dict = {}
    for r in rows:
        out.setdefault(r["question_id"], []).append(r["slo_code"])
    return out


def replace_for_question(question_id: str, slo_ids: list) -> None:
    """Is question ke saare purane link hata kar sirf diye gaye slo_ids set karo
    (replace-set). Khali list = saare link clear. Ek transaction mein — duplicate
    slo_ids INSERT OR IGNORE se safe."""
    unique_ids = list(dict.fromkeys(slo_ids))  # order rakho, duplicate hatao
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM question_slo WHERE question_id = ?", (question_id,))
    for slo_id in unique_ids:
        cur.execute(
            "INSERT OR IGNORE INTO question_slo (question_id, slo_id) VALUES (?, ?)",
            (question_id, slo_id),
        )
    conn.commit()
    conn.close()


def existing_slo_ids(slo_ids: list) -> set:
    """Diye gaye slo_ids mein se jo waqai slo table mein maujood hain — unka set.
    (Link banane se pehle validate karne ke liye — orphan link se bachao.)"""
    if not slo_ids:
        return set()
    unique_ids = list(dict.fromkeys(slo_ids))
    placeholders = ",".join("?" for _ in unique_ids)
    conn = get_connection()
    rows = conn.execute(
        f"SELECT id FROM slo WHERE id IN ({placeholders})",  # noqa: S608
        unique_ids,
    ).fetchall()
    conn.close()
    return {row["id"] for row in rows}
