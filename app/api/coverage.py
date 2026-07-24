"""HTTP routes for exam coverage (Hissa 3).

Do endpoints:
- GET /api/coverage         — ek exam ki tafseel (SLO list + covered + missing).
- GET /api/coverage-summary — saare exams (+ Unassigned) ke counts (badges).
N global hai (school_settings.exam_count)."""

from fastapi import APIRouter, HTTPException

from app.services import coverage_service, taqseem_service

router = APIRouter()


@router.get("/api/coverage")
def get_coverage(class_name: str, subject: str, exam_no: int):
    """Ek exam (1..N) ki tafseeli coverage. class_name + subject laazmi; exam_no
    1..N se bahar → 400."""
    if not class_name.strip() or not subject.strip():
        raise HTTPException(status_code=400, detail="class_name aur subject dono chahiye.")
    n = taqseem_service.exam_count()
    if exam_no < 1 or exam_no > n:
        raise HTTPException(
            status_code=400, detail=f"exam_no 1 se {n} ke darmiyaan hona chahiye."
        )
    try:
        return coverage_service.exam_coverage(class_name, subject, exam_no)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Coverage fetch fail hui (DB error): {e}"
        ) from e


@router.get("/api/coverage-summary")
def get_coverage_summary(class_name: str, subject: str):
    """Saare exams (1..N) + Unassigned (0) ke sirf counts — taqseem badges ke liye.
    class_name + subject dono laazmi."""
    if not class_name.strip() or not subject.strip():
        raise HTTPException(status_code=400, detail="class_name aur subject dono chahiye.")
    try:
        return coverage_service.coverage_summary(class_name, subject)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Coverage summary fail hui (DB error): {e}"
        ) from e
