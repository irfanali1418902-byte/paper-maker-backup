"""SQL access for the users table (SEC-02).

Ye layer sirf rows leti aur deti hai -- password kabhi yahan hash nahi hota,
koi role ka faisla yahan nahi hota. Wo `app/services/user_service.py` ka kaam
hai, wahi is repo ka waahid caller hona chahiye.
"""

from typing import List, Optional

from app.core.database import get_connection


def count_active() -> int:
    """Kitne active users hain. Poori app ka auth mode isi ek ginti par hai
    (`app/api/auth.py: auth_mode()`), is liye ye function har /api request par
    chalta hai -- sasta rehna zaroori hai. `users` table par ye ginti chand
    rows ki hai aur sqlite ise index ke baghair bhi microseconds mein deta
    hai; koi cache JAAN-BOOJH KAR nahi rakha, wajah auth.py mein likhi hai."""
    conn = get_connection()
    cur = conn.cursor()
    n = cur.execute("SELECT COUNT(*) FROM users WHERE is_active = 1").fetchone()[0]
    conn.close()
    return int(n)


def get_by_username(username: str) -> Optional[dict]:
    """Login ka raasta. `username` lower-case mein store hota hai, is liye
    yahan bhi lower kar ke dhoondte hain -- warna "Irfan" login na kar pata
    jab account "irfan" ke naam se bana ho."""
    conn = get_connection()
    cur = conn.cursor()
    row = cur.execute(
        "SELECT * FROM users WHERE username = ?", (username.strip().lower(),)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def get_by_id(user_id: str) -> Optional[dict]:
    conn = get_connection()
    cur = conn.cursor()
    row = cur.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def list_all() -> List[dict]:
    """Admin ki user list. Active pehle, phir naam ke hisaab se -- deactivate
    kiye hue accounts dikhte HAIN (gayab nahi hote), warna admin ko pata hi na
    chale ke kis ka login band kiya gaya tha."""
    conn = get_connection()
    cur = conn.cursor()
    rows = cur.execute(
        "SELECT * FROM users ORDER BY is_active DESC, username ASC"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def insert(
    user_id: str,
    username: str,
    display_name: str,
    password_hash: str,
    role: str,
) -> None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """INSERT INTO users (id, username, display_name, password_hash, role)
           VALUES (?, ?, ?, ?, ?)""",
        (user_id, username.strip().lower(), display_name, password_hash, role),
    )
    conn.commit()
    conn.close()


def update_password(user_id: str, password_hash: str) -> None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE users SET password_hash = ? WHERE id = ?", (password_hash, user_id))
    conn.commit()
    conn.close()


def update_profile(user_id: str, display_name: str, role: str, is_active: int) -> None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE users SET display_name = ?, role = ?, is_active = ? WHERE id = ?",
        (display_name, role, int(is_active), user_id),
    )
    conn.commit()
    conn.close()


def touch_login(user_id: str, at: str) -> None:
    """Kamiyab login par waqt darj. Sirf display ke liye (admin list mein
    "aakhri login"), kisi faisle ke liye nahi."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE users SET last_login_at = ? WHERE id = ?", (at, user_id))
    conn.commit()
    conn.close()


def count_active_admins(exclude_user_id: str = "") -> int:
    """Kitne active admin hain (ek ko chhor kar, agar kaha jaye).

    Ye ginti ek hi sawal ke liye hai: "agar main ye tabdeeli kar doon to kya
    is school ke paas koi admin bachega?" Aakhri admin ka apna role teacher kar
    dena ya khud ko deactivate kar dena = user management ka darwaza hamesha ke
    liye band, aur phir sirf server par baith kar `scripts/create_admin.py`
    chalana hi raasta bachta hai. Us ghalti ko hone se pehle rok dete hain.
    """
    conn = get_connection()
    cur = conn.cursor()
    n = cur.execute(
        "SELECT COUNT(*) FROM users WHERE is_active = 1 AND role = 'admin' AND id != ?",
        (exclude_user_id,),
    ).fetchone()[0]
    conn.close()
    return int(n)
