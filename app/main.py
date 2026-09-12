"""
AII Smart Paper Maker — Phase 1 MVP, layered.
Run karne ke liye: uvicorn app.main:app --reload --port 8000
Phir browser mein: http://localhost:8000
"""

import os
from pathlib import Path

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api import (
    adaptive_results,
    bloom_suggestions,
    blueprints,
    brand,
    coverage,
    dashboard,
    library,
    papers,
    questions,
    school_settings,
    slo,
    stats,
    syllabus,
    taqseem,
    topic_plan,
    users,
)
from app.api.auth import API_KEY, require_auth
from app.core.database import init_db

# ── /docs, /redoc, /openapi.json — sirf khuli (dev) app par ──────────────────
#
# FastAPI ye teenon by-default banata hai aur teenon AUTH SE BAHAR hote hain:
# routers par lagi dependency un par nahi lagti. Yani key/session set hone ke
# baad bhi koi bhi bina kuch diye poora API surface parh sakta tha — har route,
# har field, har delete/patch ka poora naqsha. Wo khud data nahi hai, magar
# hamla karne wale ka pehla kaam yehi naqsha banana hota hai, aur hum use
# mehman-nawazi se de rahe the.
#
# Faisla: jahan auth ki koi soorat mojood hai (key set hai, ya fail-closed flag
# laga hai), wahan docs band. Local dev par — jahan na key hai na flag — docs
# chalte rehte hain, kyunke wahan wo rozana ka auzaar hain.
#
# ⚠ USERS MODE IS FAISLE MEIN NAHI AA SAKTA, aur ye majboori hai, kotahi nahi:
# ye faisla app BANTE waqt hota hai (startup), jabke users mode DB ki mojooda
# haalat par hai aur wo chalte chalte badalti hai. Amal mein ye khatra nahi:
# jo school users bana raha hai us ne key bhi set ki hoti hai (school-PC setup
# guide dono ek saath kehti hai). Jis din ye galat sabit ho, asal hal docs ko
# `Depends(require_auth)` wale apne route par khud serve karna hai.
_DEPLOYISH = bool(API_KEY) or str(
    os.environ.get("PAPER_MAKER_REQUIRE_API_KEY", "")
).strip().lower() in ("1", "true", "yes")

app = FastAPI(
    title="AII Smart Paper Maker - Phase 1",
    docs_url=None if _DEPLOYISH else "/docs",
    redoc_url=None if _DEPLOYISH else "/redoc",
    openapi_url=None if _DEPLOYISH else "/openapi.json",
)


# Cache-Control policy (priority order):
#   1. Library WebP + bundled fonts → 1-saal immutable. Content-immutable hain:
#      filename UUID hai / font kabhi nahi badalta (replace = naya UUID = nayi URL).
#      Ye jaan-boojh kar hain — inhe haath nahi lagana.
#   2. /api/* → no-store. Warna browser purana GET (e.g. /api/school-settings) cache
#      se padh kar stale value dikhata hai (Class Size 30 save, F5 par 25 — asal DB
#      theek, sirf UI cached response padh raha tha).
#   3. App code (HTML + JS + CSS) → no-cache (har load par revalidate; ETag se 304
#      sasta rehta hai). StaticFiles default sirf ETag/Last-Modified deta tha (koi
#      Cache-Control nahi) → heuristic cache par normal F5 purana index.html AUR
#      alag-serve hone wali `apiClient.js`/js files serve kar deta tha. Sirf HTML par
#      no-cache kaafi nahi — inline JS to HTML mein hai, magar apiClient.js/js/*.js
#      alag files hain; wo stale rahein to naya code load hi na ho. no-cache = purana
#      JS band. (Hashed-immutable assets upar branch 1 mein pehle nikal jaate hain.)
_NO_CACHE_TYPES = ("text/html", "javascript", "text/css")


@app.middleware("http")
async def _cache_control_headers(request, call_next):
    response = await call_next(request)
    path = request.url.path
    ctype = response.headers.get("content-type", "")
    if (path.startswith("/library/") and path.endswith(".webp")) or (
        path.startswith("/static/fonts/") and path.endswith(".woff2")
    ):
        response.headers["Cache-Control"] = "public, max-age=31536000, immutable"
    elif path.startswith("/api/"):
        response.headers["Cache-Control"] = "no-store"
    elif any(t in ctype for t in _NO_CACHE_TYPES):
        response.headers["Cache-Control"] = "no-cache"
    return response

# Cross-origin origins env se (comma-separated). Frontend same-origin (`/`) se
# serve hota hai, is liye default mein koi cross-origin allow NAHI karte —
# same-origin requests ko CORS ki zaroorat nahi. Agar API ko kisi doosri domain
# se call karna ho to PAPER_MAKER_ALLOWED_ORIGINS mein woh origins do (warna
# wildcard `*` chhodne se koi bhi site browser se API hit kar sakti hai).
_origins_env = os.environ.get("PAPER_MAKER_ALLOWED_ORIGINS", "").strip()
_allowed_origins = [o.strip() for o in _origins_env.split(",") if o.strip()]

if _allowed_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=_allowed_origins,
        allow_methods=["*"],
        allow_headers=["*"],
    )

init_db()

# Har /api router auth ke peeche. Mode (session / key / khula) `require_auth`
# khud tay karti hai — dekho app/api/auth.py. Static `/` mount (neeche) khula
# rehta hai taake frontend HTML/JS bina auth ke load ho sake.
_api_auth = [Depends(require_auth)]
# Branding cosmetic shell hai (koi secret/DB/AI-cost nahi) aur har page load par
# chahiye — is liye ye jaan-boojh kar auth ke bahar hai, static `/` ki tarah. Warna
# key set hone se pehle har page par key-gate khul jata.
app.include_router(brand.router)
# ⚠ AUTH DEPENDENCY KE BAGHAIR, AUR YE LAAZMI HAI: is router mein login khud
# hai. Har route apni zaroorat andar se lagati hai (login/me khule, baqi
# require_auth/require_admin ke peeche) — tafseel app/api/users.py ke sar par.
app.include_router(users.router)
app.include_router(adaptive_results.router, dependencies=_api_auth)
app.include_router(bloom_suggestions.router, dependencies=_api_auth)
app.include_router(blueprints.router, dependencies=_api_auth)
app.include_router(questions.router, dependencies=_api_auth)
app.include_router(library.router, dependencies=_api_auth)
app.include_router(papers.router, dependencies=_api_auth)
app.include_router(dashboard.router, dependencies=_api_auth)
app.include_router(syllabus.router, dependencies=_api_auth)
app.include_router(school_settings.router, dependencies=_api_auth)
app.include_router(slo.router, dependencies=_api_auth)
app.include_router(stats.router, dependencies=_api_auth)
app.include_router(taqseem.router, dependencies=_api_auth)
app.include_router(coverage.router, dependencies=_api_auth)
app.include_router(topic_plan.router, dependencies=_api_auth)

# Static frontend ka absolute path lete hain taake uvicorn kahin se bhi
# launch ho, file resolve ho jaye.
_STATIC_DIR = Path(__file__).parent.parent / "static"
# Naye organized assets (css/, fonts, icons.svg, brand/, js/) `/static/...` par
# serve hote hain. Ye `/` catch-all se PEHLE register hota hai warna root-mount
# `/static/x` ko khud handle karne ki koshish karta. Legacy `/apiClient.js` waghera
# root mount se aate rehte hain.
app.mount("/static", StaticFiles(directory=str(_STATIC_DIR)), name="static-assets")
app.mount("/", StaticFiles(directory=str(_STATIC_DIR), html=True), name="static")
