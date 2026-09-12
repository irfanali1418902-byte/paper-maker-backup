"""Sessions: login, lockout, aur "ye request kis ki hai" (SEC-02).

YE FILE US SURAKH KO BAND KARTI HAI JO `static/apiClient.js` KHUD APNE UPAR
LIKH KAR MAAN CHUKI THI: wahan 2026-09-08 ka idle auto-lock sirf BROWSER mein
tha. Key localStorage se mit jati thi, magar server ke nazdeek wo key us ke
baad bhi utni hi durust thi -- yani jo banda DevTools se qeemat copy kar leta,
uske liye lock ka koi wajood nahi tha. Ab waqt ka faisla server karta hai
(`sessions.last_seen_at`), aur browser ka lock sirf us ka aaina hai.

Teen faisle jo yahan tay hue, aur teenon ki wajah:

  * IDLE 30 MINUTE. Wahi adad jo browser wale lock par pehle se tha, taake do
    jagah do waqt na hon. Sabab wahi hai jo apiClient.js par likha hai: school
    ka PC kai teachers share karte hain, aur asal khatra "banda uth kar chala
    gaya" hai.

  * SAKHT HADD 12 GHANTE. Idle ghadi har request par aage barhti hai, to ek
    khula hua tab (ya kal ko koi polling page) hamesha zinda reh sakta hai.
    Barri hadd us silsile ko kaatti hai. 12 ghante = ek school ka din, yani
    kisi teacher ki session us ke apne din ke andar khatam nahi hoti.

  * LOCKOUT: 5 nakaam, 15 minute. Naam par, IP par nahi -- wajah
    `auth_events_repository.count_recent_failures()` par likhi hai.

⚠ COOKIE MEIN KHAAM TOKEN JATA HAI, DB MEIN US KA SHA-256. Dono ek hi cheez
nahi. DB ki koi copy (backup file, bheja hua .db, chori) kisi ke haath lagne
par us se koi session churai nahi ja sakti. Ye poora faida is ek line par hai:
kabhi `sessions_repository` ko khaam token mat bhejna.
"""

import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

from app.repositories import auth_events_repository, sessions_repository, users_repository
from app.services import user_service
from app.services.exceptions import LoginFailed

#: Bekari ki hadd -- itni der koi request na aaye to session khatam.
IDLE_MINUTES = 30
#: Sakht hadd -- chahe banda kitna hi active ho, itni der baad dobara login.
ABSOLUTE_HOURS = 12
#: Itni nakaam koshishon ke baad account itni der ke liye band.
MAX_FAILURES = 5
LOCKOUT_MINUTES = 15

#: Cookie ka naam. Frontend ise kabhi parhta nahi (HttpOnly hai) -- ye sirf
#: server aur browser ke darmiyan hai.
COOKIE_NAME = "pm_session"


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _stamp(dt: datetime) -> str:
    """Wohi shakal jo sqlite ka CURRENT_TIMESTAMP deta hai (UTC, bina timezone
    ke). Is shakal mein tareekhon ki string-taqabul waqt ki tarteeb hi deti
    hai, is liye `expires_at <= ?` jaisi SQL bilkul theek chalti hai."""
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def _hash_token(token: str) -> str:
    """SHA-256 -- yahan password wali scrypt ki zaroorat NAHI, aur ye farq
    samajhna zaroori hai. Password insaan ka chuna hua aur andaze ke qabil
    hota hai, is liye us par hash ka mehnga hona hi bachao hai. Token 32 random
    bytes hai; use andaze se paana mumkin hi nahi, to sirf ek tez one-way hash
    kaafi hai (aur wo har request par chalta hai, to tez hona zaroori bhi hai)."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def now_stamp() -> str:
    """Abhi ka waqt, DB wali shakal mein. API layer ise log likhne ke liye use
    karti hai — warna wahan `_stamp(_now())` likhna parta, yani do private
    functions bahar se, jo is file ke andar ka maamla hai."""
    return _stamp(_now())


def log_event(event: str, username: str = "", user_id: str = "", ip: str = "", detail: str = "") -> None:
    """Auth ka koi waqia log karo. API layer ka repository tak seedha pahunchne
    ka koi kaam nahi (api -> services -> repositories, CLAUDE.md §2) — ye wahi
    darwaza hai."""
    auth_events_repository.insert(
        at=now_stamp(), event=event, username=username, user_id=user_id, ip=ip, detail=detail
    )


def recent_events(limit: int = 100) -> list[dict]:
    """Admin ke log view ke liye aakhri events."""
    return auth_events_repository.list_recent(limit)


def is_locked_out(username: str) -> bool:
    since = _stamp(_now() - timedelta(minutes=LOCKOUT_MINUTES))
    return auth_events_repository.count_recent_failures(username, since) >= MAX_FAILURES


def login(username: str, password: str, ip: str = "") -> tuple[str, dict]:
    """Kamiyabi par `(token, user)`. Har nakami par `LoginFailed`.

    Tarteeb ahem hai: lockout ka check password jaanchne se PEHLE hai, warna
    lock lagne ke baad bhi har koshish par ek scrypt hash chalta rehta (yani
    hamlawar server ka CPU khench sakta tha).
    """
    name = (username or "").strip().lower()
    now = _now()

    # Purani, mari hui sessions yahin saaf hoti hain -- alag se koi chalta hua
    # scheduler rakhne se behtar hai ise us lamhe karna jab koi waise bhi aa
    # raha ho. Table chhoti rehti hai aur ek purza kam.
    sessions_repository.delete_expired(_stamp(now))

    if is_locked_out(name):
        auth_events_repository.insert(
            at=_stamp(now), event=auth_events_repository.LOCKED_OUT, username=name, ip=ip
        )
        raise LoginFailed(
            f"Bohat zyada ghalat koshishein — ye account {LOCKOUT_MINUTES} minute ke liye "
            "band hai. Thori der baad dobara koshish karein.",
            locked=True,
        )

    row = users_repository.get_by_username(name)
    ok = bool(row) and bool(row["is_active"]) and user_service.verify_password(password, row["password_hash"])
    if not ok:
        auth_events_repository.insert(
            at=_stamp(now),
            event=auth_events_repository.LOGIN_FAIL,
            username=name,
            ip=ip,
            # Wajah log mein darj hai (admin ko chahiye), magar jawab mein NAHI
            # jati -- LoginFailed ka docstring dekho.
            detail="unknown-user" if not row else ("inactive" if not row["is_active"] else "bad-password"),
        )
        raise LoginFailed("Username ya password ghalat hai.")

    token = secrets.token_urlsafe(32)
    sessions_repository.insert(
        token_hash=_hash_token(token),
        user_id=row["id"],
        created_at=_stamp(now),
        expires_at=_stamp(now + timedelta(hours=ABSOLUTE_HOURS)),
    )
    users_repository.touch_login(row["id"], _stamp(now))
    auth_events_repository.clear_failures(name)
    auth_events_repository.insert(
        at=_stamp(now),
        event=auth_events_repository.LOGIN_OK,
        username=name,
        user_id=row["id"],
        ip=ip,
    )
    return token, user_service.to_public(row)


def resolve(token: str) -> Optional[dict]:
    """Cookie se user. Na mile / mari hui ho to `None`, aur us soorat mein row
    DB se bhi nikal jati hai.

    Har /api request par chalti hai, is liye yahan sirf wahi kaam hai jo har
    request par hona hi chahiye: ek SELECT, aur (jab waqt waqai aage barha ho)
    ek UPDATE. `last_seen_at` har request par likhna is se kahin mehnga hota --
    bees teachers ka har click ek write banata, jabke faisla minute ki sathh
    par hota hai.
    """
    if not token:
        return None
    token_hash = _hash_token(token)
    row = sessions_repository.get_with_user(token_hash)
    if not row:
        return None

    now = _now()
    now_s = _stamp(now)

    # Sakht hadd.
    if row["expires_at"] <= now_s:
        sessions_repository.delete(token_hash)
        return None

    # Bekari ki hadd.
    if row["last_seen_at"] <= _stamp(now - timedelta(minutes=IDLE_MINUTES)):
        sessions_repository.delete(token_hash)
        return None

    # Admin ne is beech account band kar diya ho to pehle se khuli session bhi
    # yahin mar jati hai -- "band kar diya" ka matlab abhi hona chahiye, us ke
    # browser band karne par nahi.
    if not row["is_active"]:
        sessions_repository.delete(token_hash)
        return None

    # Ghadi tab aage barhao jab kam az kam ek minute guzar chuka ho. Isi se
    # har click ek DB write nahi banta; 30 minute ki hadd par ek minute ki
    # gol-mol ka koi asar nahi.
    if row["last_seen_at"] < _stamp(now - timedelta(minutes=1)):
        sessions_repository.touch(token_hash, now_s)

    return {
        "id": row["user_id"],
        "username": row["username"],
        "display_name": row["display_name"] or row["username"],
        "role": row["role"],
        "is_active": bool(row["is_active"]),
        "token_hash": token_hash,
    }


def logout(token: str, ip: str = "") -> None:
    """Session khatam. Jo token na mile us par bhi khamoshi -- logout ka jawab
    kabhi ye na bataye ke wo token asli tha ya nahi."""
    if not token:
        return
    token_hash = _hash_token(token)
    row = sessions_repository.get_with_user(token_hash)
    sessions_repository.delete(token_hash)
    if row:
        auth_events_repository.insert(
            at=_stamp(_now()),
            event=auth_events_repository.LOGOUT,
            username=row["username"],
            user_id=row["user_id"],
            ip=ip,
        )


def change_password(user_id: str, new_password: str, keep_token: str = "", ip: str = "") -> None:
    """Password badlo AUR us user ki saari sessions khatam karo.

    ⚠ SESSIONS KA KHATAM HONA IS KAAM KA HISSA HAI, alag qadam nahi. Password
    badalne ki asal wajah aksar yehi hoti hai ke kisi aur ko pata chal gaya --
    agar us ki pehle se khuli session zinda rahe to naya password sirf ek
    rasm hai. Isi liye ye kaam yahan hai, `user_service.set_password()` mein
    nahi: sessions ka malik yehi service hai.

    `keep_token` wo session hai jis se ye tabdeeli ki ja rahi hai. Apna
    password badalne wale teacher ko usi lamhe bahar phenkna bila wajah ki
    sazaa hai, is liye us ki apni session bach jati hai. Admin jab kisi AUR ka
    password badle to keep_token khali hota hai aur us bande ki har session
    jati hai -- theek wohi natija jo maqsood hai.
    """
    user_service.set_password(user_id, new_password)
    keep_hash = _hash_token(keep_token) if keep_token else ""
    # Ek ek kar ke mitate hain, "sab mita kar apni wapas daal do" NAHI. Wo
    # pehla draft tha aur us mein ek khamoshi wala bug tha: dobara daali gayi
    # row ka `last_seen_at` `created_at` par reset ho jata (repository insert
    # dono ek hi qeemat se bharti hai), yani subah 8 baje bani hui session
    # dopahar mein password badalte hi "chaar ghante se bekaar" ban kar agle
    # hi request par mar jati. Jis bande ko bachana maqsood tha, wohi bahar.
    for r in sessions_repository.list_for_user(user_id):
        if keep_hash and r["token_hash"] == keep_hash:
            continue
        sessions_repository.delete(r["token_hash"])
    row = users_repository.get_by_id(user_id)
    auth_events_repository.insert(
        at=_stamp(_now()),
        event=auth_events_repository.PASSWORD_CHANGED,
        username=row["username"] if row else "",
        user_id=user_id,
        ip=ip,
    )


def end_all_sessions(user_id: str) -> int:
    """Us bande ki har session khatam. Role badalne / account band karne par
    chalti hai -- naya role purani session par lagu hona chahiye, aur band kiye
    hue account ki session ka zinda rehna to khula tazaad hai."""
    return sessions_repository.delete_for_user(user_id)
