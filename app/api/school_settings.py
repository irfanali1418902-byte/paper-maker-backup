"""HTTP routes for school settings (singleton)."""

from fastapi import APIRouter, HTTPException

from app.schemas.requests import ClassPrintSettingsSave, SchoolSettings
from app.schemas.responses import PrintSettingsResolved, StatusResponse
from app.services import class_print_settings_service, settings_service

router = APIRouter()


@router.get("/api/school-settings", response_model=SchoolSettings)
def get_school_settings():
    try:
        return settings_service.get_settings()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Settings fetch fail hui (DB error): {e}"
        ) from e


@router.post("/api/school-settings", response_model=StatusResponse)
def save_school_settings(settings: SchoolSettings):
    try:
        settings_service.save_settings(settings)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Settings save fail hui (DB error): {e}"
        ) from e
    return {"status": "saved"}


@router.get("/api/print-settings", response_model=PrintSettingsResolved)
def get_print_settings(class_name: str = ""):
    """Ek class ke resolved print knobs — per-class row ho to woh, warna global
    school_settings defaults (row-level fallback). print.html paper.class_name
    ke saath call karta hai."""
    try:
        return class_print_settings_service.get_print_settings(class_name)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Print settings fetch fail hui (DB error): {e}"
        ) from e


@router.post("/api/print-settings", response_model=StatusResponse)
def save_print_settings(body: ClassPrintSettingsSave):
    """Ek class ke print knobs mehfooz karo (upsert). Value-bounds schema par
    enforce hoti hain (out-of-range = 422). Blank class = 400."""
    try:
        class_print_settings_service.save_print_settings(
            class_name=body.class_name,
            font_size=body.font_size,
            q_gap=body.q_gap,
            page_margin=body.page_margin,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Print settings save fail hui (DB error): {e}"
        ) from e
    return {"status": "saved"}
