"""SQL access for the sessions table (SEC-02).

⚠ YAHAN JO `token_hash` AATA HAI WO HASH HI HONA CHAHIYE, khaam token nahi.
Hashing `app/services/session_service.py` mein hoti hai. Agar kabhi kisi ne
seedha token yahan bhej diya to sab kuch chalta rahega -- aur DB mein zinda
tokens pare hon ge. Isi liye har function ka parameter ka naam `token_hash`
hai, `token` nahi: naam hi guard hai.
"""

from typing import List, Optional

from app.core.database import get_connection


def insert(token_hash: str, user_id: str, created_at: str, expires_at: str) -> None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """INSERT INTO sessions (token_hash, user_id, created_at, last_seen_at, expires_at)
           VALUES (?, ?, ?, ?, ?)""",
        (token_hash, user_id, created_at, created_at, expires_at),
    )
    conn.commit()
    conn.close()


def get_with_user(token_hash: str) -> Optional[dict]:
    """Session + us ka user, ek query mein.

    JOIN is liye ke har request par do round-trip karne ka koi faida nahi, aur
    `is_active` yahin dekh lena zaroori hai: admin ne abhi jis teacher ka login
    band kiya hai, us ki pehle se khuli hui session agle hi request par
    bekaar honi chahiye -- warna "band kar diya" ek jhoot hai jo us ke browser
    band karne tak chalta rahe.
    """
    conn = get_connection()
    cur = conn.cursor()
    row = cur.execute(
        """SELECT s.token_hash, s.user_id, s.created_at, s.last_seen_at, s.expires_at,
                  u.username, u.display_name, u.role, u.is_active
             FROM sessions s
             JOIN users u ON u.id = s.user_id
            WHERE s.token_hash = ?""",
        (token_hash,),
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def touch(token_hash: str, at: str) -> None:
    """Idle ghadi aage barhao. Har kamiyab request par chalti hai."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE sessions SET last_seen_at = ? WHERE token_hash = ?", (at, token_hash))
    conn.commit()
    conn.close()


def delete(token_hash: str) -> None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM sessions WHERE token_hash = ?", (token_hash,))
    conn.commit()
    conn.close()


def delete_for_user(user_id: str) -> int:
    """Us user ki saari sessions khatam. Teen jagah chalta hai: password badla,
    role badla, ya account band hua. Teenon mein purani session ka zinda rehna
    ghalat hoga -- password badalne ka poora matlab hi "jo pehle andar tha wo
    ab bahar hai" hai."""
    conn = get_connection()
    cur = conn.cursor()
    n = cur.execute("DELETE FROM sessions WHERE user_id = ?", (user_id,)).rowcount
    conn.commit()
    conn.close()
    return int(n)


def delete_expired(now: str) -> int:
    """Woh sessions jo apni sakht hadd paar kar chuki hain. Login par chalta
    hai (alag se koi scheduler nahi -- ek school server par ek aur chalta hua
    purza rakhne se behtar hai ise us lamhe chalana jab koi waise bhi aa raha
    ho)."""
    conn = get_connection()
    cur = conn.cursor()
    n = cur.execute("DELETE FROM sessions WHERE expires_at <= ?", (now,)).rowcount
    conn.commit()
    conn.close()
    return int(n)


def list_for_user(user_id: str) -> List[dict]:
    conn = get_connection()
    cur = conn.cursor()
    rows = cur.execute(
        "SELECT * FROM sessions WHERE user_id = ? ORDER BY last_seen_at DESC", (user_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]
