"""HTTP routes for login, logout, aur user management (SEC-02).

⚠ YE ROUTER GLOBAL AUTH DEPENDENCY KE BAGHAIR REGISTER HOTA HAI (`app/main.py`),
aur ye lazmi hai: login khud us darwaze ka naam hai jise kholne ke liye login
chahiye hota. Is liye har route apni zaroorat khud batati hai —

    /api/auth/me        : khula (mode + "main kaun hoon")
    /api/auth/login     : khula (lockout us ke andar hai)
    /api/auth/logout    : khula (cookie ho to khatam, na ho to khamoshi)
    /api/auth/password  : apna password — `require_auth`
    /api/users*         : `require_admin`
    /api/auth/events    : `require_admin`

Jo bhi is file mein nayi route likhe, wo pehle ye tay kare ke us par kaun si
dependency lagegi — yahan "kuch na likhna" ka matlab "sab ke liye khula" hai,
jabke baqi poori app mein ulta hai.
"""

from fastapi import APIRouter, Depends, HTTPException, Request, Response

from app.api.auth import MODE_HEADER, auth_mode, current_user, require_admin, require_auth
from app.schemas.requests import (
    LoginRequest,
    PasswordChangeRequest,
    UserCreateRequest,
    UserUpdateRequest,
)
from app.schemas.responses import AuthEvent, AuthMeResponse, StatusResponse, UserPublic
from app.services import session_service, user_service
from app.services.exceptions import LoginFailed, UserValidationError

router = APIRouter()


def _client_ip(request: Request) -> str:
    """Log ke liye IP. School ke LAN par ye seedha teacher ki machine hoti hai.

    ⚠ `X-Forwarded-For` JAAN-BOOJH KAR NAHI PARHA JATA. Wo header koi bhi client
    khud bhej sakta hai, aur us par bharosa tab hi ho sakta hai jab saamne koi
    aisa proxy ho jo use hamesha khud likhta ho. Is app ke saamne aisa kuch nahi
    (uvicorn seedha LAN par sunta hai — `start-school.bat`), to use parhna log
    mein hamlawar ka likha hua jhoot daalna hota. Jis din koi asli reverse proxy
    lage, us din ye function badle — tab tak `client.host` hi sach hai.
    """
    return request.client.host if request.client else ""


def _set_session_cookie(request: Request, response: Response, token: str) -> None:
    """Session cookie — HttpOnly, SameSite=Lax.

    HttpOnly: JavaScript ise parh hi nahi sakta. Purani `pm_api_key` bilkul
    ulta thi (localStorage, har script ke liye khuli) — us ka matlab tha ke ek
    XSS poori key uthaa kar le ja sakti thi. Ab jo cheez churai ja sakti hai wo
    browser se bahar hi nahi nikalti.

    SameSite=Lax: kisi doosri site ka form is app par POST kare to cookie saath
    nahi jati — yani CSRF ka aam raasta yahin band hai. App ke apne page se
    (same-site fetch) cookie normal jati hai.

    `secure` sirf https par. School ka LAN aaj plain http hai (`start-school.bat`
    http://192.168.x.x:8000 chhapta hai); wahan `secure=True` lagane ka matlab
    hota ke browser cookie bhejta hi nahi aur koi login kaam hi na kare. Is liye
    ye request ki apni scheme se tay hota hai: jis din https lage, cookie us din
    khud ba khud secure ho jayegi, bina kisi code change ke.
    """
    response.set_cookie(
        key=session_service.COOKIE_NAME,
        value=token,
        httponly=True,
        samesite="lax",
        secure=request.url.scheme == "https",
        max_age=session_service.ABSOLUTE_HOURS * 3600,
        path="/",
    )


@router.get("/api/auth/me", response_model=AuthMeResponse)
def whoami(request: Request):
    """Mode + mojooda user. Frontend har page par sab se pehle yehi poochta hai."""
    mode = auth_mode()
    user = None
    if mode == "users":
        resolved = session_service.resolve(request.cookies.get(session_service.COOKIE_NAME, ""))
        if resolved:
            full = user_service.get_user(resolved["id"])
            user = full
    return {"mode": mode, "user": user}


@router.post("/api/auth/login", response_model=UserPublic)
def login(body: LoginRequest, request: Request, response: Response):
    try:
        token, user = session_service.login(
            username=body.username, password=body.password, ip=_client_ip(request)
        )
    except LoginFailed as e:
        # 429 lockout par, 401 baqi sab par. Farq sirf HTTP ka nahi: frontend
        # lockout wale paighaam ko waisa hi dikhata hai jaisa hai ("15 minute
        # baad"), jabke 401 par sirf "dobara koshish karein" kehta hai.
        raise HTTPException(status_code=429 if e.locked else 401, detail=str(e)) from e
    _set_session_cookie(request, response, token)
    return user


@router.post("/api/auth/logout", response_model=StatusResponse)
def logout(request: Request, response: Response):
    session_service.logout(
        request.cookies.get(session_service.COOKIE_NAME, ""), ip=_client_ip(request)
    )
    # Cookie ka mitana bhi utna hi zaroori hai jitna DB ki row ka: warna browser
    # har request par ek mari hui cookie bhejta rehta hai aur har jawab 401 ke
    # saath aata hai — kaam to theek chalta, magar log bekaar ki nakamiyon se
    # bhar jata aur asli masla us mein chhup jata.
    response.delete_cookie(key=session_service.COOKIE_NAME, path="/")
    return {"status": "logged-out"}


@router.post("/api/auth/password", response_model=StatusResponse, dependencies=[Depends(require_auth)])
def change_own_password(body: PasswordChangeRequest, request: Request):
    """Apna password badlo. Purana password zaroori hai — wajah
    `PasswordChangeRequest` ke docstring mein hai."""
    user = current_user(request)
    if not user:
        # Sirf `users` mode mein is endpoint ka matlab hai. Key/open mode mein
        # koi "apna" account hota hi nahi.
        raise HTTPException(
            status_code=400,
            detail="Is app par abhi users nahi bane — password badalne ko koi account nahi.",
            headers={MODE_HEADER: auth_mode()},
        )
    if not user_service.get_user(user["id"]):
        raise HTTPException(status_code=404, detail="User nahi mila.")
    if not user_service.check_password(user["id"], body.current_password):
        raise HTTPException(status_code=401, detail="Purana password ghalat hai.")
    try:
        session_service.change_password(
            user_id=user["id"],
            new_password=body.new_password,
            # Apni session bach jati hai — apna password badalne par khud ko
            # bahar phenkna bila wajah ki sazaa hai.
            keep_token=request.cookies.get(session_service.COOKIE_NAME, ""),
            ip=_client_ip(request),
        )
    except UserValidationError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return {"status": "password-changed"}


# ── User management — sab `require_admin` ke peeche ──────────────────────────


@router.get("/api/users", response_model=list[UserPublic], dependencies=[Depends(require_admin)])
def list_users():
    return user_service.list_users()


@router.post("/api/users", response_model=UserPublic, dependencies=[Depends(require_admin)])
def create_user(body: UserCreateRequest, request: Request):
    """Naya account. Pehla account banane ka raasta bhi yehi hai — `require_admin`
    us soorat ko khud sambhalti hai (us ka docstring parho)."""
    try:
        user = user_service.create_user(
            username=body.username,
            password=body.password,
            display_name=body.display_name,
            role=body.role,
        )
    except UserValidationError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    actor = current_user(request)
    session_service.log_event(
        event="user_created",
        username=user["username"],
        user_id=user["id"],
        ip=_client_ip(request),
        detail=f"banaya: {actor['username'] if actor else 'bootstrap'}",
    )
    return user


@router.patch("/api/users/{user_id}", response_model=UserPublic, dependencies=[Depends(require_admin)])
def update_user(user_id: str, body: UserUpdateRequest, request: Request):
    try:
        user = user_service.update_user(
            user_id=user_id,
            display_name=body.display_name,
            role=body.role,
            is_active=body.is_active,
        )
    except UserValidationError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    # Role badla ya account band hua — dono soorton mein purani session ka
    # zinda rehna ghalat hai. Ek teacher jise abhi admin banaya gaya us ka naya
    # ikhtiyar agli request par chahiye; aur band kiye gaye account ka andar
    # baitha rehna to khula tazaad hai. (Doosri soorat `session_service.resolve`
    # bhi pakarti hai; ye us se pehle, yahin, saaf kar deta hai.)
    session_service.end_all_sessions(user_id)
    actor = current_user(request)
    session_service.log_event(
        event="user_updated",
        username=user["username"],
        user_id=user["id"],
        ip=_client_ip(request),
        detail=f"badla: {actor['username'] if actor else 'bootstrap'}; "
        f"role={user['role']}; active={user['is_active']}",
    )
    return user


@router.post(
    "/api/users/{user_id}/password",
    response_model=StatusResponse,
    dependencies=[Depends(require_admin)],
)
def reset_user_password(user_id: str, body: PasswordChangeRequest, request: Request):
    """Admin kisi ka password reset kare. `current_password` yahan nahi maanga
    jata (admin ke paas wo hai hi nahi) — aur us bande ki saari sessions khatam
    ho jati hain, kyunke reset ki asal wajah aksar yehi hoti hai."""
    if not user_service.get_user(user_id):
        raise HTTPException(status_code=404, detail="User nahi mila.")
    try:
        session_service.change_password(
            user_id=user_id, new_password=body.new_password, ip=_client_ip(request)
        )
    except UserValidationError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return {"status": "password-changed"}


@router.get("/api/auth/events", response_model=list[AuthEvent], dependencies=[Depends(require_admin)])
def list_auth_events(limit: int = 100):
    """Aakhri auth events — kaun aaya, kab, kahan se, aur kis naam par nakaam
    koshishein ho rahi hain. Yehi wo sawal hai jis ka jawab shared key wale
    daur mein kahin tha hi nahi."""
    return session_service.recent_events(min(max(limit, 1), 500))
