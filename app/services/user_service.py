"""Users: password hashing aur account ke rules (SEC-02).

Ye file do cheezon ki zimmedar hai jo kahin aur nahi honi chahiyen:
  1. Password ka hash banana aur jaanchna.
  2. Kya qubool hai -- naam, password ki lambai, role, aur "aakhri admin".

Sessions is file mein NAHI hain (`session_service.py`), aur SQL yahan nahi
(`repositories/users_repository.py`).

─── PASSWORD HASHING: SCRYPT, AUR KOI NAYI DEPENDENCY NAHI ──────────────────
`hashlib.scrypt` Python ki apni library mein hai. bcrypt/argon2 ke liye pip
package chahiye hota, aur is project ka deploy raasta school ka PC hai jahan
`pip install` karne wala koi mojood nahi hota -- ek missing wheel wahan poori
app band kar deta hai. scrypt un se kamtar nahi: memory-hard hai, yani GPU par
hamla mehnga rehta hai.

⚠ PLAIN PASSWORD KABHI DB MEIN NAHI JATA, aur na kabhi log mein. Is file se
bahar sirf `password_hash` ki string jati hai, jis mein algorithm, parameters,
salt aur hash -- sab ek saath hain. Is shakal ka faida: kal parameters badalne
par purane hash parhe ja sakte hain (unhi ke apne n/r/p se), yani sab ko ek
saath logout kiye baghair upgrade mumkin hai.
"""

import base64
import hashlib
import hmac
import secrets
import uuid
from typing import List, Optional

from app.repositories import users_repository
from app.services.exceptions import UserValidationError

# scrypt ke parameters. n=2^14 par ek hash ~16 MB memory aur chand
# millisecond leta hai -- teacher ko login par mehsoos nahi hota, aur hamlawar
# ke liye har koshish isi qeemat par parti hai.
_SCRYPT_N = 2**14
_SCRYPT_R = 8
_SCRYPT_P = 1
_SALT_BYTES = 16
_DK_LEN = 32

#: Kam az kam itna lamba password. 8 se barhana kal ka faisla ho sakta hai;
#: abhi ye wo hadd hai jahan school ke teachers se bila jhagre manwaya ja sake.
MIN_PASSWORD_LEN = 8

#: Sirf do roles. Zyada roles ka matlab har endpoint par "kaun kar sakta hai"
#: ka sawal, aur us ki abhi koi zaroorat nahi: admin account banata hai, teacher
#: parche banata hai.
ROLES = ("admin", "teacher")


def hash_password(password: str) -> str:
    """`scrypt$n$r$p$salt$hash` -- sab kuch ek string mein, base64 mein."""
    salt = secrets.token_bytes(_SALT_BYTES)
    dk = hashlib.scrypt(
        password.encode("utf-8"), salt=salt, n=_SCRYPT_N, r=_SCRYPT_R, p=_SCRYPT_P, dklen=_DK_LEN
    )
    return "scrypt${}${}${}${}${}".format(
        _SCRYPT_N,
        _SCRYPT_R,
        _SCRYPT_P,
        base64.b64encode(salt).decode(),
        base64.b64encode(dk).decode(),
    )


def verify_password(password: str, stored: str) -> bool:
    """Kya ye password us hash se milta hai.

    Parameters hash ki apni string se aate hain, upar wale constants se NAHI --
    isi liye parameters badalne par purane accounts chalte rehte hain.

    Har ghalti par `False`, exception nahi: DB ki koi kharab qeemat (kati hui
    string, purana format) login ko 500 nahi karni chahiye -- wo 401 hai.
    """
    try:
        algo, n, r, p, salt_b64, hash_b64 = stored.split("$")
        if algo != "scrypt":
            return False
        dk = hashlib.scrypt(
            password.encode("utf-8"),
            salt=base64.b64decode(salt_b64),
            n=int(n),
            r=int(r),
            p=int(p),
            dklen=len(base64.b64decode(hash_b64)),
        )
    except (ValueError, TypeError, MemoryError):
        return False
    # compare_digest: waisi hi wajah jo app/api/auth.py par likhi hai.
    return hmac.compare_digest(dk, base64.b64decode(hash_b64))


def to_public(row: dict) -> dict:
    """Wo shakal jo API se bahar ja sakti hai. `password_hash` yahan se girta
    hai -- ek hi jagah, taake koi route ghalti se poora row na laut de."""
    return {
        "id": row["id"],
        "username": row["username"],
        "display_name": row["display_name"] or row["username"],
        "role": row["role"],
        "is_active": bool(row["is_active"]),
        "created_at": row.get("created_at") or "",
        "last_login_at": row.get("last_login_at") or "",
    }


def _validate_username(username: str) -> str:
    name = (username or "").strip().lower()
    if len(name) < 3:
        raise UserValidationError("Username kam az kam 3 harf ka ho.")
    if not all(ch.isalnum() or ch in "._-" for ch in name):
        raise UserValidationError("Username mein sirf harf, adad, aur . _ - chal sakte hain.")
    return name


def _validate_password(password: str) -> str:
    if len(password or "") < MIN_PASSWORD_LEN:
        raise UserValidationError(f"Password kam az kam {MIN_PASSWORD_LEN} harf ka ho.")
    return password


def _validate_role(role: str) -> str:
    if role not in ROLES:
        raise UserValidationError(f"Role sirf in mein se ho sakta hai: {', '.join(ROLES)}.")
    return role


def create_user(username: str, password: str, display_name: str = "", role: str = "teacher") -> dict:
    """Naya account. Wapas public shakal aati hai (hash ke baghair)."""
    name = _validate_username(username)
    _validate_password(password)
    _validate_role(role)
    if users_repository.get_by_username(name):
        raise UserValidationError(f"'{name}' naam ka user pehle se mojood hai.")
    user_id = str(uuid.uuid4())
    users_repository.insert(
        user_id=user_id,
        username=name,
        display_name=(display_name or "").strip() or name,
        password_hash=hash_password(password),
        role=role,
    )
    return to_public(users_repository.get_by_id(user_id))


def set_password(user_id: str, password: str) -> None:
    """Password badlo. Sessions yahan se khatam NAHI hoti -- wo faisla
    `session_service.change_password()` karta hai, kyunke wo sessions ka malik
    hai aur do jagah se ek hi cheez mitana wahi purana do-raaste wala bug hai."""
    _validate_password(password)
    if not users_repository.get_by_id(user_id):
        raise UserValidationError("User nahi mila.")
    users_repository.update_password(user_id, hash_password(password))


def update_user(user_id: str, display_name: str, role: str, is_active: bool) -> dict:
    """Naam/role/haalat badlo.

    ⚠ AAKHRI ADMIN KI HIFAZAT YAHIN HAI. Agar ye tabdeeli school ko bina kisi
    active admin ke chhor de to rad ho jati hai. Warna ek hi click user
    management ka darwaza hamesha ke liye band kar sakta hai, aur us ke baad
    sirf server par baith kar `scripts/create_admin.py` chalana hi raasta
    bachta hai -- ek aisi soorat jo school ke waqt par nahi aati.
    """
    row = users_repository.get_by_id(user_id)
    if not row:
        raise UserValidationError("User nahi mila.")
    _validate_role(role)
    losing_admin = row["role"] == "admin" and row["is_active"] and (role != "admin" or not is_active)
    if losing_admin and users_repository.count_active_admins(exclude_user_id=user_id) == 0:
        raise UserValidationError(
            "Ye akela active admin hai — ise badalne se koi bhi user manage nahi kar payega. "
            "Pehle koi doosra admin banayen."
        )
    users_repository.update_profile(
        user_id=user_id,
        display_name=(display_name or "").strip() or row["username"],
        role=role,
        is_active=1 if is_active else 0,
    )
    return to_public(users_repository.get_by_id(user_id))


def check_password(user_id: str, password: str) -> bool:
    """Kya ye us user ka mojooda password hai.

    Apna password badalne wali route ko yehi chahiye tha, aur is ke baghair wo
    route ko seedha `users_repository` se hash mangwana parta — yani api layer
    repository ko chhoo leti (CLAUDE.md §2 ka ulta). Hash is file se bahar nahi
    jata; sirf haan/na jata hai.
    """
    row = users_repository.get_by_id(user_id)
    if not row:
        return False
    return verify_password(password, row["password_hash"])


def list_users() -> List[dict]:
    return [to_public(r) for r in users_repository.list_all()]


def get_user(user_id: str) -> Optional[dict]:
    row = users_repository.get_by_id(user_id)
    return to_public(row) if row else None


def any_users_exist() -> bool:
    """Kya is app ke paas asli users hain. Poore app ka auth mode isi par hai —
    `app/api/auth.py: auth_mode()` dekho."""
    return users_repository.count_active() > 0
