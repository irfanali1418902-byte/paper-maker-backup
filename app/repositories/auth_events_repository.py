"""SQL access for the auth_events table (SEC-02) — kaun aaya, kab, aur kahan se.

Do alag maqsad, ek hi table:
  * Insaan ke liye: admin dekh sake ke kis ne kab login kiya, aur kis naam par
    nakaam koshishein ho rahi hain.
  * Machine ke liye: `count_recent_failures()` lockout ka faisla karti hai.

Dusra maqsad pehle se zyada sakht hai: agar ye ginti ghalat ho to ya to log
band ho jaye (jhoota lockout) ya hamla khula reh jaye. Isi liye ye DB mein hai,
kisi process ki memory mein nahi -- restart se hamlawar ka counter sifar nahi
hona chahiye.
"""

from typing import List

from app.core.database import get_connection

# Jo events likhe jate hain. Naye event ka naam yahan daalo taake ek jagah se
# pata chale ke log mein kya kya mil sakta hai.
LOGIN_OK = "login_ok"
LOGIN_FAIL = "login_fail"
LOGOUT = "logout"
LOCKED_OUT = "locked_out"
USER_CREATED = "user_created"
USER_UPDATED = "user_updated"
PASSWORD_CHANGED = "password_changed"


def insert(
    at: str,
    event: str,
    username: str = "",
    user_id: str = "",
    ip: str = "",
    detail: str = "",
) -> None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """INSERT INTO auth_events (at, event, username, user_id, ip, detail)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (at, event, (username or "").strip().lower(), user_id or None, ip, detail),
    )
    conn.commit()
    conn.close()


def count_recent_failures(username: str, since: str) -> int:
    """`since` ke baad is naam par kitne nakaam login. Lockout ka poora hisaab.

    Naam par ginti hai, IP par NAHI -- aur ye faisla hai, kotahi nahi. School
    mein bees teachers ek hi router ke peeche baithe hain, yani un sab ka IP
    server ko ek jaisa (ya NAT ke peeche ek hi) dikh sakta hai. IP par lock
    lagane ka matlab hota: ek banda apna password teen dafa ghalat likhe aur
    poora staff room bahar. Naam par lock us nuqsaan ko usi account tak
    mehdood rakhta hai jis par hamla ho raha hai.
    """
    conn = get_connection()
    cur = conn.cursor()
    n = cur.execute(
        """SELECT COUNT(*) FROM auth_events
            WHERE username = ? AND event = ? AND at > ?""",
        ((username or "").strip().lower(), LOGIN_FAIL, since),
    ).fetchone()[0]
    conn.close()
    return int(n)


def clear_failures(username: str) -> None:
    """Kamiyab login par us naam ke nakaam nishaan mita do -- warna teacher
    subah do dafa ghalti kare, dopahar tak theek chale, aur shaam ko teesri
    ghalti par lock ho jaye. Lockout ki window ka matlab "lagatar" hai."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "DELETE FROM auth_events WHERE username = ? AND event = ?",
        ((username or "").strip().lower(), LOGIN_FAIL),
    )
    conn.commit()
    conn.close()


def list_recent(limit: int = 100) -> List[dict]:
    """Admin ke liye aakhri events, naye pehle."""
    conn = get_connection()
    cur = conn.cursor()
    rows = cur.execute(
        "SELECT * FROM auth_events ORDER BY id DESC LIMIT ?", (int(limit),)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]
