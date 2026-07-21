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
    dashboard,
    export,
    library,
    papers,
    questions,
    school_settings,
    slo,
    stats,
    syllabus,
)
from app.api.auth import require_api_key
from app.core.database import init_db

app = FastAPI(title="AII Smart Paper Maker - Phase 1")


# HISSA 5 — caching headers sirf library WebP par. Ye files content-immutable hain:
# filename UUID hai aur koi route existing {uuid}.webp ko dubara nahi likhta (replace =
# delete + naya upload = naya UUID = nayi URL). Isliye 1-saal `immutable` 100% safe hai,
# koi cache-busting nahi chahiye. HTML/JS ko haath nahi lagate (woh deploy pe badalte hain —
# StaticFiles ka default ETag/304 revalidation unke liye theek hai).
@app.middleware("http")
async def _cache_control_for_immutable_assets(request, call_next):
    response = await call_next(request)
    path = request.url.path
    # Library WebP: filename UUID hai, content kabhi nahi badalta.
    # Bundled fonts (.woff2): woh kabhi nahi badalte. Dono par 1-saal immutable safe.
    # app.css / icons.svg par jaan-boojh kar koi long cache NAHI (deploy pe badal
    # sakti hain) — StaticFiles ka default ETag/304 revalidation unke liye theek hai.
    if (path.startswith("/library/") and path.endswith(".webp")) or (
        path.startswith("/static/fonts/") and path.endswith(".woff2")
    ):
        response.headers["Cache-Control"] = "public, max-age=31536000, immutable"
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

# Har /api router API-key auth ke peeche. Static `/` mount (neeche) khula rehta
# hai taake frontend HTML/JS bina key ke load ho sake.
_api_auth = [Depends(require_api_key)]
# Branding cosmetic shell hai (koi secret/DB/AI-cost nahi) aur har page load par
# chahiye — is liye ye jaan-boojh kar auth ke bahar hai, static `/` ki tarah. Warna
# key set hone se pehle har page par key-gate khul jata.
app.include_router(brand.router)
app.include_router(adaptive_results.router, dependencies=_api_auth)
app.include_router(bloom_suggestions.router, dependencies=_api_auth)
app.include_router(blueprints.router, dependencies=_api_auth)
app.include_router(questions.router, dependencies=_api_auth)
app.include_router(library.router, dependencies=_api_auth)
app.include_router(papers.router, dependencies=_api_auth)
app.include_router(dashboard.router, dependencies=_api_auth)
app.include_router(export.router, dependencies=_api_auth)
app.include_router(syllabus.router, dependencies=_api_auth)
app.include_router(school_settings.router, dependencies=_api_auth)
app.include_router(slo.router, dependencies=_api_auth)
app.include_router(stats.router, dependencies=_api_auth)

# Static frontend ka absolute path lete hain taake uvicorn kahin se bhi
# launch ho, file resolve ho jaye.
_STATIC_DIR = Path(__file__).parent.parent / "static"
# Naye organized assets (app.css, fonts, icons.svg, brand/, js/) `/static/...` par
# serve hote hain. Ye `/` catch-all se PEHLE register hota hai warna root-mount
# `/static/x` ko khud handle karne ki koshish karta. Legacy `/apiClient.js` waghera
# root mount se aate rehte hain.
app.mount("/static", StaticFiles(directory=str(_STATIC_DIR)), name="static-assets")
app.mount("/", StaticFiles(directory=str(_STATIC_DIR), html=True), name="static")
