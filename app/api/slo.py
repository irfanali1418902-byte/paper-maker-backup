"""HTTP routes for SLO (Student Learning Outcomes) — Marhala 0: table + Excel import."""

from pathlib import Path
from typing import Optional

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import FileResponse

from app.repositories import slo_repository
from app.services import slo_import_service

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
