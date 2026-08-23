"""HTTP routes for the hafta-war plan (syllabus topic -> hafta). R7 Marhala 1.

`app/api/taqseem.py` ka aaina -- error mapping wahan se liya gaya hai:
ValueError -> 400, NotFound -> 404, baqi sab -> 500 with a DB-error message.
"""

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import Response

from app.schemas.requests import TopicWeekMoveRequest
from app.services import topic_coverage_service, topic_week_import_service, topic_week_service

router = APIRouter()

_XLSX_MEDIA = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


@router.get("/api/topic-plan")
def get_topic_plan(subject: str, grade: str):
    """Ek (subject, grade) ka resolved hafta-war plan. Dono laazmi (plan
    per-subject-per-grade hai). N global (school_settings.week_count).

    Plan-less topics bhi aate hain -- Unassigned bucket mein -- taake teacher ko
    dikhe ke kitna kaam baqi hai."""
    if not subject.strip() or not grade.strip():
        raise HTTPException(status_code=400, detail="subject aur grade dono chahiye.")
    try:
        return topic_week_service.get_plan(subject, grade)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Hafta-war plan fetch fail hui (DB error): {e}"
        ) from e


@router.get("/api/topic-plan/template")
def download_topic_plan_template(subject: str, grade: str):
    """Us (subject, grade) ke topics ka Excel — syllabus_topic_id + title +
    current week_no. Teacher sirf `week_no` column bharta hai aur
    /api/topic-plan/assign-import par wapas upload karta hai.

    Route ko PATCH /{topic_id} se PEHLE rakhna zaroori hai, warna "template"
    ek topic_id samjha jayega."""
    if not subject.strip() or not grade.strip():
        raise HTTPException(status_code=400, detail="subject aur grade dono chahiye.")
    xlsx = topic_week_import_service.build_template_xlsx(subject, grade)
    filename = topic_week_import_service.template_filename(subject, grade)
    return Response(
        content=xlsx,
        media_type=_XLSX_MEDIA,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.post("/api/topic-plan/assign-import")
def import_topic_plan(file: UploadFile = File(...)):
    """Bhari hui sheet se topics ka hafta replace-set karo.
    Returns: {updated, cleared, errors, warnings}."""
    fname = (file.filename or "").lower()
    if not (fname.endswith(".xlsx") or fname.endswith(".xls") or fname.endswith(".csv")):
        raise HTTPException(status_code=400, detail="Sirf .xlsx / .xls / .csv file allowed hai.")
    contents = file.file.read()
    return topic_week_import_service.import_assignments(contents, file.filename or "plan.xlsx")


@router.get("/api/topic-plan/coverage")
def get_topic_coverage(subject: str, grade: str):
    """Hafta-war coverage: har hafte ke planned topics mein se kitne kisi paper
    mein aa chuke. R7 Marhala 3.

    "covered" GLOBAL hai, hafta-war nahi -- `papers` mein `week_no` column hai hi
    nahi. Tafseel `topic_coverage_service` ke docstring mein; wo faisla wahan darj
    hai kyunke report parhne wale ko us ka pata hona zaroori hai.

    `/template` ki tarah ye route bhi PATCH /{topic_id} se PEHLE hona chahiye,
    warna "coverage" ek topic_id samjha jayega."""
    if not subject.strip() or not grade.strip():
        raise HTTPException(status_code=400, detail="subject aur grade dono chahiye.")
    try:
        return topic_coverage_service.coverage(subject, grade)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Coverage fetch fail hui (DB error): {e}"
        ) from e


@router.patch("/api/topic-plan/{topic_id}")
def move_topic(topic_id: str, body: TopicWeekMoveRequest):
    """Ek topic ka hafta badlo/set karo. week_no 0 = Unassigned; range 0..N se
    bahar -> 400; topic_id na mile -> 404. N global (school_settings.week_count)."""
    try:
        return topic_week_service.move_topic(topic_id, body.week_no)
    except topic_week_service.TopicNotFoundError as e:
        raise HTTPException(status_code=404, detail=f"Topic nahi mila: {e}") from e
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Topic move fail hui (DB error): {e}"
        ) from e
