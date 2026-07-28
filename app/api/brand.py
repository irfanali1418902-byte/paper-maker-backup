"""HTTP route for app branding (name, tagline, logo). No colours — see UI-003."""

from fastapi import APIRouter, HTTPException

from app.schemas.responses import BrandResponse
from app.services import brand_service

router = APIRouter()


@router.get("/api/brand", response_model=BrandResponse)
def get_brand():
    """Frontend ke liye branding — startup par config/brand.json se load hoti hai."""
    try:
        return brand_service.get_brand()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Brand config fetch fail hui: {e}") from e
