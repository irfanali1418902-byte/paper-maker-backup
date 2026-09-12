"""`/api` ka auth — teen modes, aur mode DATA se tay hota hai.

    users   : `users` table mein koi active user hai -> har /api call par ek
              zinda session cookie zaroori. Ye asal authentication hai: system
              ko pata hota hai ke banda KAUN hai, us ka role kya hai, aur har
              login `auth_events` mein darj hota hai.
    key     : koi user nahi, magar PAPER_MAKER_API_KEY set hai -> purana
              behaviour, bilkul waisa ka waisa: `x-api-key` header ka exact
              match.
    open    : na user, na key -> auth OFF + startup par loud warning. Local
              dev frictionless rehta hai.

⚠ MODE EK FLAG SE NAHI, DATA SE BADALTA HAI — aur ye is poore kaam ka sab se
ahem faisla hai. Ek chalti hui school par "auth upgrade" ka matlab hargiz ye
nahi hona chahiye ke kisi subah teachers andar na aa sakein. Jab tak admin
pehla user nahi banata, app haraf ba haraf wahi hai jo pehle thi. Pehla active
user bante hi (UI se ya `scripts/create_admin.py` se) mode `users` ho jata hai
aur shared key /api ke liye mar jati hai.

⚠ KEY MODE MEIN SAB KUCH EK HI SECRET PAR THA. Wahan system ko nahi pata tha
ke banda kaun hai: bees teachers ek hi qeemat jaante the, koi role nahi tha,
aur "ye parcha kis ne mitaya" ka koi jawab nahi tha. Us kami ka aitraaf khud
`static/apiClient.js` (2026-09-08) mein likha hua tha. `users` mode us ko band
karta hai. Key ab bhi mojood hai un school ke liye jinhon ne abhi users nahi
banaye — hataya nahi gaya, sirf peeche chala gaya.

Static frontend `/` har mode mein khula rehta hai — HTML/JS bina auth ke load
hona chahiye, warna login page khud kabhi nahi khulta.
"""

import hmac
import logging
import os

from fastapi import HTTPException, Request, Security
from fastapi.security import APIKeyHeader

from app.services import session_service, user_service

API_KEY_HEADER = "x-api-key"

# Secret yahin, module load par, ek baar read hoti hai. Empty = auth disabled.
API_KEY = os.environ.get("PAPER_MAKER_API_KEY") or ""

# Is se chhoti key par startup warning (crash nahi) — wajah neeche likhi hai.
MIN_KEY_LEN = 20

# auto_error=False: header missing hone par FastAPI khud 403 na de — hum
# apna 401 + Hinglish detail dena chahte hain (aur dev-mode mein pass karna hai).
_api_key_header = APIKeyHeader(name=API_KEY_HEADER, auto_error=False)

_logger = logging.getLogger("uvicorn.error")

# Environment variables jinki maujoodgi batati hai ke hum ek real (public)
# deployment par hain, local dev par nahi. Railway (hamara deploy target) inhe
# production par khud inject karta hai. Kisi bhi doosre host par
# PAPER_MAKER_REQUIRE_API_KEY=1 set karke bhi auth ko mandatory banaya ja sakta hai.
_DEPLOY_ENV_MARKERS = (
    "RAILWAY_ENVIRONMENT",
    "RAILWAY_ENVIRONMENT_NAME",
    "RAILWAY_SERVICE_ID",
)

_AUTH_MISSING_IN_DEPLOY_MSG = (
    "PAPER_MAKER_API_KEY set nahi hai lekin ye ek deployment environment lagta "
    "hai — /api ko bina key ke public karna matlab koi bhi tumhare AI tokens "
    "(paisa) aur DB use kar sakta hai. Deploy ke environment variables mein "
    "PAPER_MAKER_API_KEY (koi lambi random string) set karo. Local dev ke liye "
    "ise unset chhodo — wahan auth off rehti hai."
)


def _is_deployment(env) -> bool:
    """True jab environment ek real deployment lage: ya explicit
    PAPER_MAKER_REQUIRE_API_KEY flag, ya koi known deploy-host marker."""
    if str(env.get("PAPER_MAKER_REQUIRE_API_KEY", "")).strip().lower() in ("1", "true", "yes"):
        return True
    return any(env.get(marker) for marker in _DEPLOY_ENV_MARKERS)


def auth_config_error(api_key: str, env) -> str | None:
    """Misconfiguration detect karta hai aur error message deta hai (warna None).
    Pure + testable. Rule: deployment par key missing = fail-closed. Local dev
    (koi deploy signal nahi, key bhi missing) safe hai."""
    if api_key:
        return None
    if _is_deployment(env):
        return _AUTH_MISSING_IN_DEPLOY_MSG
    return None


# Fail-closed: deploy par key missing ho to app start hi na ho. Silently
# UNPROTECTED chalne se behtar hai loud crash — deploy fix ho jayega.
_config_error = auth_config_error(API_KEY, os.environ)
if _config_error:
    raise RuntimeError(_config_error)

if not API_KEY:
    _logger.warning(
        "PAPER_MAKER_API_KEY set nahi hai — /api endpoints UNPROTECTED hain. "
        "Ye sirf local dev ke liye theek hai. Production deploy se pehle host ke "
        "environment variables mein PAPER_MAKER_API_KEY zaroor set karo."
    )
elif len(API_KEY) < MIN_KEY_LEN:
    # Sirf warning, crash NAHI. Jo key aaj school par chal rahi hai wo agar chhoti
    # nikli to app ka start na hona teachers ko subah subah bahar kar dena hai —
    # us se bura koi "security fix" nahi. Admin ko batao, faisla us ka.
    #
    # KYUN 20. Key ka koi quality check tha hi nahi: `PAPER_MAKER_API_KEY=1234`
    # bhi app khushi se qubool karti thi, aur /api par galat keys maarne par koi
    # rate-limit ya lockout bhi nahi hai (2026-09-12 tak) — yani chhoti key LAN
    # par bethe kisi bhi bande ke liye sirf waqt ki baat hai. 20 harf random
    # us hamle ko na-mumkin bana dete hain. Aaj school ki key 48 harf ki hai,
    # to ye warning wahan chalegi nahi.
    _logger.warning(
        "PAPER_MAKER_API_KEY sirf %d harf ki hai — kam az kam %d harf ki koi "
        "random string rakho. Chhoti key andaze se pata chal sakti hai, aur galat "
        "keys try karne par abhi koi rok (rate-limit/lockout) nahi hai.",
        len(API_KEY),
        MIN_KEY_LEN,
    )


MODE_USERS = "users"
MODE_KEY = "key"
MODE_OPEN = "open"

#: 401 ke saath ye header jata hai. Frontend ko isi se pata chalta hai ke
#: teacher ko login page par bhejna hai ya purana key-gate kholna hai — bina
#: is ke use pehle ek aur request kar ke mode poochhna parta, aur wo jawab har
#: page load par ek extra round-trip hota.
MODE_HEADER = "x-pm-auth-mode"


def auth_mode() -> str:
    """Is waqt ka mode. Har /api request par ek dafa chalti hai.

    ⚠ KOI CACHE JAAN-BOOJH KAR NAHI. Cache rakhne ka matlab hota ke pehla user
    banne ke baad bhi app thori der purane mode par chalti rahe — yani theek us
    lamhe jhooti khuli rehti jab admin ne abhi abhi use band kiya hai. Qeemat
    ek COUNT hai chand rows par, aur har route waise bhi isi DB se parhta hai.
    (Tests ke liye bhi yehi durust hai: wahan har test apni alag DB file par
    chalta hai, aur module-level cache un ke darmiyan reh jata.)
    """
    if user_service.any_users_exist():
        return MODE_USERS
    return MODE_KEY if API_KEY else MODE_OPEN


def current_user(request: Request) -> dict | None:
    """Is request ka user — sirf `users` mode mein milta hai, warna None.

    `require_auth` ise `request.state` par rakh deti hai, to routes bina dobara
    DB chhue `Depends(current_user)` se le sakti hain."""
    return getattr(request.state, "pm_user", None)


def require_auth(request: Request, provided_key: str = Security(_api_key_header)) -> None:
    """Har /api router par lagti hai. Mode ke hisaab se faisla karti hai.

    Nakami par 401 — aur `x-pm-auth-mode` header ke saath, taake frontend
    jaanay ke login page dikhana hai ya key-gate.
    """
    mode = auth_mode()

    if mode == MODE_USERS:
        user = session_service.resolve(request.cookies.get(session_service.COOKIE_NAME, ""))
        if user:
            request.state.pm_user = user
            return
        raise HTTPException(
            status_code=401,
            detail="Login zaroori hai — dobara login karein.",
            headers={MODE_HEADER: MODE_USERS},
        )

    if mode == MODE_OPEN:
        return
    # ⚠ `==` NAHI — `hmac.compare_digest`. Sada `==` pehla mukhtalif harf milte hi
    # ruk jata hai, to jawab ka waqt batata hai ke kitne shuruaati harf sahi the;
    # kaafi requests se key harf-ba-harf nikali ja sakti hai. compare_digest poori
    # lambai par barabar waqt leta hai. (LAN par ye khatra kam hai, magar ROADMAP
    # 2026-08-25 se ye control MOJOOD bata raha tha jab ke tha nahi — 2026-09-12.)
    # `provided_key` None ho sakti hai (header hi nahi aaya) aur compare_digest
    # None par throw karta hai, is liye khali string par gira dete hain. Bytes
    # mein isliye ke str-mode compare_digest sirf ASCII par chalta hai — kisi ne
    # key mein Urdu ya koi non-ASCII harf daala to TypeError = 500, aur auth
    # crash se 401 dena kahin behtar hai.
    if hmac.compare_digest((provided_key or "").encode("utf-8"), API_KEY.encode("utf-8")):
        return
    raise HTTPException(
        status_code=401,
        detail="API key ghalat ya missing hai — x-api-key header mein sahi key bhejein.",
        headers={MODE_HEADER: MODE_KEY},
    )


def require_admin(request: Request, provided_key: str = Security(_api_key_header)) -> None:
    """User-management routes ki dependency. Do soorten, dono zaroori:

      * Users mojood hain -> session chahiye AUR role `admin`. Teacher yahan
        403 par rukta hai, 401 par nahi: wo andar to hai, bas is kaam ka
        ikhtiyar nahi rakhta, aur ye farq us ke liye bhi saaf hona chahiye.

      * Abhi koi user nahi (pehla account banaya ja raha hai) -> mode jo bhi
        mange wahi. Yani key wali school par pehla admin banane ke liye key
        chahiye, aur khuli (local dev) app par kuch nahi.

    ⚠ DOOSRI SOORAT PEHLA ADMIN BANANE KA DARWAZA HAI, aur wo sirf utni der
    khula rehta hai jitni der ek bhi active user na ho. Pehla admin bante hi ye
    raasta apne aap band ho jata hai. Khuli app par ye "koi bhi admin ban sakta
    hai" lagta hai — aur waqai hai, magar wahan pehle se har endpoint khula hai,
    to is se kuch naya nahi khulta. Jahan ye bat mayne rakhti ho, wahan key set
    karo ya pehla admin server par `scripts/create_admin.py` se banao.
    """
    if auth_mode() != MODE_USERS:
        require_auth(request, provided_key)
        return
    user = session_service.resolve(request.cookies.get(session_service.COOKIE_NAME, ""))
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Login zaroori hai — dobara login karein.",
            headers={MODE_HEADER: MODE_USERS},
        )
    request.state.pm_user = user
    if user["role"] != "admin":
        raise HTTPException(
            status_code=403,
            detail="Ye kaam sirf admin kar sakta hai.",
        )


#: Purana naam. `require_api_key` poori app mein ek hi jagah se lagta tha
#: (`app/main.py`), aur ab wahan `require_auth` hai. Ye alias un logon ke liye
#: hai jo bahar se import karte hain (tests, koi script) — hataya nahi, taake
#: kisi ka import khamoshi se na toote.
require_api_key = require_auth
