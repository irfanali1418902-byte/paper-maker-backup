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
