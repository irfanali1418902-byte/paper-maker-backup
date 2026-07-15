"""HTTP routes for syllabus topic listing + PDF import."""

from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse

from app.schemas.responses import (
    SubjectGrade,
    SyllabusImportResponse,
    SyllabusTopic,
    SyllabusZipImportResponse,
    TopicItem,
)
from app.services import syllabus_service, syllabus_unit_import_service
from app.services.exceptions import AIGenerationFailed

_UNIT_TEMPLATE = Path(__file__).parent.parent.parent / "static" / "syllabus_unit_import_template.xlsx"

router = APIRouter()


@router.get("/api/syllabus-grades", response_model=List[SubjectGrade])
def list_syllabus_grades():
    """Database mein jo bhi subject+grade combinations imported hain, unki list deta hai (dropdown ke liye)."""
    try:
        return syllabus_service.list_grades()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Syllabus grades fetch fail hui (DB error): {e}"
        ) from e


@router.post("/api/syllabus/upload-pdf", response_model=SyllabusImportResponse)
def upload_syllabus_pdf(
    subject: str = Form(...),
    grade: str = Form(...),
    file: UploadFile = File(...),
):
    """Teacher ek syllabus/textbook PDF upload karta hai; app text nikaal kar
    AI se topics structure karwati hai aur syllabus_topics mein save karti hai.
    Duplicate topics skip ho jaate hain."""
    if not subject.strip() or not grade.strip():
        raise HTTPException(status_code=400, detail="subject aur grade dono zaroori hain.")
    if not (file.filename or "").lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Sirf .pdf file upload karen.")

    pdf_bytes = file.file.read()

    try:
        result = syllabus_service.import_from_pdf(pdf_bytes, subject.strip(), grade.strip())
    except ValueError as e:
        # Bad/scanned/unreadable PDF — well-formed request, unusable content.
        raise HTTPException(status_code=400, detail=str(e)) from e
    except AIGenerationFailed as e:
        raise HTTPException(status_code=502, detail=f"AI extraction fail hui: {e}") from e
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Syllabus PDF save fail hui (DB error): {e}"
        ) from e

    return {"subject": subject.strip(), "grade": grade.strip(), **result}


@router.post("/api/syllabus/upload-zip", response_model=SyllabusZipImportResponse)
def upload_syllabus_zip(
    subject: str = Form(...),
    grade: str = Form(...),
    file: UploadFile = File(...),
):
    """Teacher ek ZIP upload karta hai jisme multiple syllabus PDFs aur/ya
    images (JPG/PNG) hoti hain; har file se AI topics nikaal kar save karti
    hai. Har file ka natija alag-alag wapas aata hai (ek file fail ho to
    baaki chalti rehti hain)."""
    if not subject.strip() or not grade.strip():
        raise HTTPException(status_code=400, detail="subject aur grade dono zaroori hain.")
    if not (file.filename or "").lower().endswith(".zip"):
        raise HTTPException(status_code=400, detail="Sirf .zip file upload karen.")

    zip_bytes = file.file.read()

    try:
        result = syllabus_service.import_from_zip(zip_bytes, subject.strip(), grade.strip())
    except ValueError as e:
        # Bad/empty ZIP — well-formed request, unusable content.
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Syllabus ZIP save fail hui (DB error): {e}"
        ) from e

    return {"subject": subject.strip(), "grade": grade.strip(), **result}


@router.get("/api/topics", response_model=List[TopicItem])
def list_topics_for_picker(
    subject: Optional[str] = None,
    grade: Optional[str] = None,
    from_page: Optional[int] = None,
    to_page: Optional[int] = None,
):
    """Subject → Class → Topic hierarchy picker ke liye lightweight topic list.
    from_page/to_page se page range filter kar sakte hain (syllabus_topics.page_no).
    Frontend in topics ka id lekar /api/generate-questions ya /api/questions mein
    syllabus_topic_id pass karta hai."""
    try:
        raw = syllabus_service.list_topics(subject=subject, grade=grade, from_page=from_page, to_page=to_page)
        return [
            {
                "id": t["id"],
                "subject": t["subject"],
                "grade": t.get("grade"),
                "unit_no": t["unit_no"],
                "unit_title": t["unit_title"],
                "subtopic_title": t["subtopic_title"],
                "suggested_difficulty": t["suggested_difficulty"],
                "page_no": t.get("page_no"),
                "unit": t.get("unit"),
            }
            for t in raw
        ]
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Topics fetch fail hui (DB error): {e}"
        ) from e


@router.get("/api/syllabus-topics", response_model=List[SyllabusTopic])
def list_syllabus_topics(subject: Optional[str] = None, grade: Optional[str] = None):
    """Real textbook se import kiye gaye topics list karta hai, dropdown ke
    liye. Har topic ke saath suggested difficulty bhi deta hai (book ke apne
    Introduction/Identification/Practice/Review tagging se mapped)."""
    try:
        return syllabus_service.list_topics(subject=subject, grade=grade)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Syllabus topics fetch fail hui (DB error): {e}"
        ) from e


@router.get("/api/syllabus/excel-unit-import/template")
def download_unit_import_template():
    """Excel unit import ka template file download karo (.xlsx)."""
    if not _UNIT_TEMPLATE.exists():
        raise HTTPException(status_code=404, detail="Template file nahi mili.")
    return FileResponse(
        path=str(_UNIT_TEMPLATE),
        filename="syllabus_unit_import_template.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


@router.post("/api/syllabus/excel-unit-import")
def excel_unit_import(file: UploadFile = File(...)):
    """Excel se topics ka unit field bulk update karo.

    Columns: topic (zaroori), subject (optional), class (optional), unit (zaroori).
    Returns: {updated, skipped, results: [{row, subtopic_title, status, reason?}]}
    """
    fname = (file.filename or "").lower()
    if not (fname.endswith(".xlsx") or fname.endswith(".xls") or fname.endswith(".csv")):
        raise HTTPException(status_code=400, detail="Sirf .xlsx / .xls / .csv file allowed hai.")

    contents = file.file.read()
    try:
        result = syllabus_unit_import_service.import_units_from_excel(contents)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return result
