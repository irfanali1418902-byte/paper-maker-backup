"""App branding config, loaded once at import from config/brand.json.

Startup par ek dafa file parhi jaati hai — har request par nahi. File missing
ya kharab ho to app crash NA ho: safe defaults use hote hain aur ek warning
log hoti hai. Frontend (brand.js) `/api/brand` se yeh values leta hai."""

import json
import logging
from pathlib import Path

_logger = logging.getLogger("uvicorn.error")

_BRAND_PATH = Path(__file__).resolve().parents[2] / "config" / "brand.json"

# Safe fallback — brand.json na mile ya kharab ho to yeh chalta hai. Values
# config/brand.json se match karti hain taake fallback par bhi UI theek dikhe.
_DEFAULTS: dict = {
    "name": "Parcha",
    "full_name": "Parcha Paper Maker",
    "tagline": "Exam paper generator",
    "logo": "/static/brand/logo.svg",
    "primary": "#2E5AAC",
    "navy": "#16294A",
}


def _load_brand() -> dict:
    try:
        with open(_BRAND_PATH, encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        _logger.warning("brand.json nahi mili (%s) — default branding use ho rahi hai.", _BRAND_PATH)
        return dict(_DEFAULTS)
    except (json.JSONDecodeError, OSError) as e:
        _logger.warning("brand.json parh nahi paye (%s) — default branding use ho rahi hai.", e)
        return dict(_DEFAULTS)
    # Missing keys ko defaults se bhar do taake response shape hamesha poora rahe.
    return {**_DEFAULTS, **data}


# Module load par ek dafa. Immutable snapshot — request handlers isay sirf parhte hain.
_BRAND: dict = _load_brand()


def get_brand() -> dict:
    """Loaded branding ka copy — startup par parhi gayi thi."""
    return dict(_BRAND)
