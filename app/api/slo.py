"""HTTP routes for SLO (Student Learning Outcomes) — Marhala 0: table + Excel import."""

from pathlib import Path
from typing import Optional

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import FileResponse, Response

from app.repositories import slo_repository
from app.services import (
    question_slo_import_service,
    slo_health_service,
    slo_import_service,
)

_XLSX_MEDIA = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

router = APIRouter()

_SLO_TEMPLATE = Path(__file__).parent.parent.parent / "static" / "slo_import_template.xlsx"


@router.get("/api/slo")
def list_slos(
    class_name: Optional[str] = None,
    subject: Optional[str] = None,
    strand: Optional[str] = None,
):
    """SLO list karo — class/subject/strand filter (sab optional)."""
    slos = slo_repository.list_by_filters(
        class_name=class_name, subject=subject, strand=strand
    )
    return {"slos": slos, "total": len(slos)}


@router.get("/api/slo-health")
def get_slo_health(class_name: Optional[str] = None, subject: Optional[str] = None):
    """SLO Health — dono taraf ka gap: bina (published) question wale SLO +
    bina SLO tag wale (published) questions, plus per class/subject health line
    aur "SLO import baqi". Optional class/subject filter. Live compute (JOIN)."""
    try:
        return slo_health_service.compute_health(
            class_filter=class_name, subject_filter=subject
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"SLO health compute fail hui (DB error): {e}"
        ) from e


@router.get("/api/slo/template")
def download_slo_template():
    """SLO Excel import ka template file download karo (.xlsx)."""
    if not _SLO_TEMPLATE.exists():
        raise HTTPException(status_code=404, detail="Template file nahi mili.")
    return FileResponse(
        path=str(_SLO_TEMPLATE),
        filename="slo_import_template.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


@router.get("/api/questions/slo-export")
def export_questions_for_slo_assign(
    grade: Optional[str] = None,
    subject: Optional[str] = None,
):
    """Questions ka Excel (question_id + current slo_code) — bulk-assign ke liye.
    Teacher slo_code column bhar/edit kar ke /api/slo/assign-import par upload karta hai.

    Optional filter: `?grade=Pre Year 1&subject=Math` (dono optional, khali = sab
    questions). subject 'Math'/'Mathematics' dono match; grade syllabus_topics par
    JOIN. Filename filter ke hisab se dynamic."""
    xlsx = question_slo_import_service.build_export_xlsx(grade=grade, subject=subject)
    filename = question_slo_import_service.export_filename(grade=grade, subject=subject)
    return Response(
        content=xlsx,
        media_type=_XLSX_MEDIA,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.post("/api/slo/assign-import")
def assign_slos_import(file: UploadFile = File(...)):
    """Filled export sheet se questions ke SLO links replace-set karo.
    Returns: {updated, errors, warnings}."""
    fname = (file.filename or "").lower()
    if not (fname.endswith(".xlsx") or fname.endswith(".xls") or fname.endswith(".csv")):
        raise HTTPException(status_code=400, detail="Sirf .xlsx / .xls / .csv file allowed hai.")
    contents = file.file.read()
    return question_slo_import_service.import_assignments(contents, file.filename or "assign.xlsx")


@router.post("/api/slo/import")
def import_slos(file: UploadFile = File(...)):
    """Excel file se SLO bulk add/update karo.

    Returns: {added, updated, errors, results: [{row, slo_code, status, reason?}]}
    """
    fname = (file.filename or "").lower()
    if not (fname.endswith(".xlsx") or fname.endswith(".xls") or fname.endswith(".csv")):
        raise HTTPException(
            status_code=400,
            detail="Sirf .xlsx / .xls / .csv file allowed hai.",
        )

    contents = file.file.read()
    try:
        result = slo_import_service.import_slos_from_excel(contents)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return result
