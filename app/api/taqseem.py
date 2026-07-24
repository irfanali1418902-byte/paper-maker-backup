"""HTTP routes for taqseem (SLO -> exam plan). Hissa 2."""

from fastapi import APIRouter, HTTPException

from app.schemas.requests import TaqseemGenerateRequest, TaqseemMoveRequest
from app.services import taqseem_service

router = APIRouter()


@router.get("/api/taqseem")
def get_taqseem(class_name: str, subject: str):
    """Ek (class, subject) ka resolved exam plan. class_name + subject dono laazmi
    (taqseem per-class-per-subject hai). N global (school_settings.exam_count)."""
    if not class_name.strip() or not subject.strip():
        raise HTTPException(status_code=400, detail="class_name aur subject dono chahiye.")
    try:
        return taqseem_service.get_plan(class_name, subject)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Taqseem fetch fail hui (DB error): {e}"
        ) from e


@router.post("/api/taqseem/generate")
def generate_taqseem(body: TaqseemGenerateRequest):
    """Auto-taqseem: is (class, subject) ke SLO ko sequence par N exams mein baant do.
    Maujooda plan overwrite hota hai — response `overwritten` count wapas karta hai
    (frontend confirm/summary ke liye). N global (school_settings.exam_count)."""
    if not body.class_name.strip() or not body.subject.strip():
        raise HTTPException(status_code=400, detail="class_name aur subject dono chahiye.")
    try:
        return taqseem_service.generate_plan(body.class_name, body.subject)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Taqseem generate fail hui (DB error): {e}"
        ) from e


@router.post("/api/taqseem/move")
def move_taqseem(body: TaqseemMoveRequest):
    """Ek SLO ko exam mein daalo/badlo (drag/drop). exam_no 0 = Unassigned; range
    0..N se bahar → 400; slo_id na mile → 404. N global (school_settings.exam_count)."""
    try:
        return taqseem_service.move_slo(body.slo_id, body.exam_no, body.position)
    except taqseem_service.SloNotFoundError as e:
        raise HTTPException(status_code=404, detail=f"SLO nahi mila: {e}") from e
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Taqseem move fail hui (DB error): {e}"
        ) from e
