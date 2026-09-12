"""API-key auth for the /api surface.

Ek shared key per deployment (`PAPER_MAKER_API_KEY`), jo har /api request ke
`x-api-key` header mein aati hai. Yeh auth-secret ka owning boundary hai — key
sirf yahin, ek dafa read hoti hai (jaise ai_service apni provider keys ke liye
karti hai).

Behaviour deliberately do-modes hai:
  - PAPER_MAKER_API_KEY set    -> har /api call par sahi key zaroori (warna 401).
  - PAPER_MAKER_API_KEY unset  -> auth OFF + startup par loud warning. Local dev
    frictionless rehta hai; production mein .env mein key set karte hi poora
    /api surface lock ho jata hai. (Static frontend `/` par hamesha khula rehta
    hai — HTML/JS bina key ke load hona chahiye.)
"""

import hmac
import logging
import os

from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader

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


def require_api_key(provided_key: str = Security(_api_key_header)) -> None:
    """FastAPI dependency: /api routers par lagti hai. Key configure na ho to
    dev-mode (pass). Warna `x-api-key` header ka exact match zaroori."""
    if not API_KEY:
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
    )
