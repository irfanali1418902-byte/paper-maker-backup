"""HTTP routes for exam-wise SLO coverage. Marhala 4.

Taqseem (planned) vs papers (covered) — coverage_service compute karti hai; ye
sirf HTTP layer hai (validation + error shape), taqseem.py/papers.py jaisa.
"""

from fastapi import APIRouter, HTTPException

from app.services import coverage_service

router = APIRouter()


@router.get("/api/coverage")
def get_coverage(class_name: str, subject: str, exam_no: int):
    """Ek exam ka mukammal coverage (planned vs covered, remaining, strands, paper
    drill-down). class_name + subject dono laazmi; exam_no laazmi (koi default nahi —
    UI hamesha bhejta hai, missing par FastAPI 422). exam_no range 0..N (0 = Unassigned;
    N = school_settings.exam_count). N _exam_count() se — taqseem/service jaisa hi rule."""
    if not class_name.strip() or not subject.strip():
        raise HTTPException(status_code=400, detail="class_name aur subject dono chahiye.")
    n = coverage_service._exam_count()
    if not (0 <= exam_no <= n):
        raise HTTPException(
            status_code=400, detail=f"exam_no 0..{n} ke darmiyan hona chahiye (0 = Unassigned)."
        )
    try:
        return coverage_service.exam_coverage(class_name, subject, exam_no)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Coverage fetch fail hui (DB error): {e}"
        ) from e


@router.get("/api/coverage-summary")
def get_coverage_summary(class_name: str, subject: str):
    """Saare exams (1..N) + Unassigned(0) ka ek-nazar summary: har exam ke planned vs
    covered count. class_name + subject dono laazmi. N + bucketing service khud
    handle karti (Unassigned covered hamesha 0)."""
    if not class_name.strip() or not subject.strip():
        raise HTTPException(status_code=400, detail="class_name aur subject dono chahiye.")
    try:
        return coverage_service.coverage_summary(class_name, subject)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Coverage summary fail hui (DB error): {e}"
        ) from e
