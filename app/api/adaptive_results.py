"""HTTP routes for the adaptive results pipeline."""

from typing import Optional

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import Response
from pydantic import BaseModel

from app.services import adaptive_results_service
from app.services.exceptions import ResultsValidationError

router = APIRouter()

_XLSX_CONTENT_TYPE = (
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)


class GenerateAdaptiveRequest(BaseModel):
    total_questions: int = 20
    language: Optional[str] = None


@router.get("/api/adaptive/template/{paper_id}")
def download_template(paper_id: str):
    """Download a blank .xlsx results template for this paper."""
    try:
        content = adaptive_results_service.build_excel_template(paper_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
    if content is None:
        raise HTTPException(status_code=404, detail="Paper nahi mila.")
    return Response(
        content=content,
        media_type=_XLSX_CONTENT_TYPE,
        headers={"Content-Disposition": f'attachment; filename="results_{paper_id}.xlsx"'},
    )


@router.post("/api/adaptive/upload/{paper_id}")
async def upload_results(paper_id: str, file: UploadFile = File(...)):
    """Upload filled-in results sheet (CSV or XLSX).
    Re-uploading replaces previous data. Returns warning if student count is low."""
    file_bytes = await file.read()
    try:
        result = adaptive_results_service.upload_results(paper_id, file.filename or "upload.xlsx", file_bytes)
    except ResultsValidationError as e:
        raise HTTPException(status_code=400, detail=e.errors) from e
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
    if result is None:
        raise HTTPException(status_code=404, detail="Paper nahi mila.")
    return result


@router.get("/api/adaptive/analysis/{paper_id}")
def get_analysis(paper_id: str):
    """Topic-wise, Bloom-wise, student-wise performance breakdown."""
    try:
        analysis = adaptive_results_service.get_analysis(paper_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
    if analysis is None:
        raise HTTPException(
            status_code=404,
            detail="Is paper ka koi result upload nahi hua ya paper exist nahi karta.",
        )
    return analysis


@router.post("/api/adaptive/generate/{paper_id}")
def generate_adaptive_paper(paper_id: str, req: GenerateAdaptiveRequest):
    """Generate a topic-weighted adaptive paper and save to My Papers."""
    try:
        new_paper_id = adaptive_results_service.generate_paper(
            paper_id=paper_id,
            total_questions=req.total_questions,
            language=req.language,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
    if new_paper_id is None:
        raise HTTPException(
            status_code=404,
            detail="Paper nahi mila, ya is paper ke results upload nahi hue, ya bank mein matching questions nahi.",
        )
    return {"paper_id": new_paper_id}
