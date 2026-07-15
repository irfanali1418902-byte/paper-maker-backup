"""HTTP routes for question generation and listing."""

from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.repositories import library_repository, questions_repository
from app.schemas.requests import (
    BulkUpdateQuestionMetaRequest,
    CopyFromLibraryRequest,
    GenerateQuestionsRequest,
    ManualQuestionRequest,
    ManualQuestionUpdateRequest,
    UpdateQuestionRequest,
)
from app.schemas.responses import GenerateQuestionsResponse, Question, StatusResponse
from app.services import bulk_import_service, question_service, syllabus_service

_UPLOADS_DIR = Path(__file__).parent.parent.parent / "static" / "uploads"
_UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

_LIBRARY_DIR = Path(__file__).parent.parent.parent / "static" / "library"

_ALLOWED_MIME = {"image/jpeg": "jpg", "image/png": "png"}
_MAX_BYTES = 2 * 1024 * 1024  # 2 MB

router = APIRouter()


@router.post("/api/generate-questions", response_model=GenerateQuestionsResponse)
def generate_questions(req: GenerateQuestionsRequest):
    """Topic dekar AI se Bloom-tagged bilingual questions generate karta hai
    aur question bank (SQLite) mein save karta hai.

    Agar syllabus_topic_id diya jaye, to subject/topic/difficulty usi
    syllabus_topics row se khud-bakhud le liye jaate hain (manual typing
    ki zaroorat nahi)."""
    if req.syllabus_topic_id:
        topic = syllabus_service.get_topic(req.syllabus_topic_id)
        if not topic:
            raise HTTPException(status_code=404, detail="syllabus_topic_id nahi mila.")
        req.subject = topic["subject"]
        req.topic = topic["subtopic_title"]
        req.difficulty = topic["suggested_difficulty"]
        req.learning_outcome = topic.get("learning_outcome")

    if not req.subject or not req.topic:
        raise HTTPException(
            status_code=400,
            detail="subject aur topic dono zaroori hain (ya syllabus_topic_id den).",
        )

    try:
        ai_questions = question_service.generate_for_topic(req)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"AI generation fail hui: {e}") from e

    try:
        saved_ids = question_service.persist_batch(ai_questions, req)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Question save fail hui (DB error): {e}"
        ) from e

    return {"saved_count": len(saved_ids), "question_ids": saved_ids}


@router.patch("/api/questions/bulk-meta")
def bulk_update_question_meta(req: BulkUpdateQuestionMetaRequest):
    """Kai questions ke smart tags ek saath update karo (keywords, status, source_book, etc.)."""
    count = question_service.bulk_update_question_meta(req)
    return {"updated": count}


@router.patch("/api/questions/{question_id}", response_model=Question)
def update_question(question_id: str, req: UpdateQuestionRequest):
    """Teacher ek existing question ka text, options, correct answer ya marks fix kar sakta hai."""
    found = question_service.update_question(question_id, req)
    if not found:
        raise HTTPException(status_code=404, detail="Question nahi mila.")
    return questions_repository.find_by_id(question_id)


@router.post("/api/questions/{question_id}/image", response_model=Question)
def upload_question_image(question_id: str, file: UploadFile = File(...)):
    """Teacher question ke saath ek image upload karta hai (JPG/PNG, max 2 MB).
    Pehle us question ki koi bhi purani image (kisi bhi ext mein) delete hoti hai,
    phir nayi file {question_id}.{ext} naam se static/uploads/ mein save hoti hai."""
    if questions_repository.find_by_id(question_id) is None:
        raise HTTPException(status_code=404, detail="Question nahi mila.")

    content_type = file.content_type or ""
    ext = _ALLOWED_MIME.get(content_type)
    if ext is None:
        raise HTTPException(
            status_code=400,
            detail="Sirf JPG aur PNG images allowed hain. / Only JPG and PNG images are allowed.",
        )

    contents = file.file.read()
    if len(contents) > _MAX_BYTES:
        raise HTTPException(
            status_code=400,
            detail="Image ka size 2 MB se zyada nahi hona chahiye. / Image must be under 2 MB.",
        )

    # Purani image (kisi bhi extension mein) delete karo
    for old_ext in _ALLOWED_MIME.values():
        old_file = _UPLOADS_DIR / f"{question_id}.{old_ext}"
        if old_file.exists():
            old_file.unlink()

    dest = _UPLOADS_DIR / f"{question_id}.{ext}"
    dest.write_bytes(contents)

    image_path = f"uploads/{question_id}.{ext}"
    questions_repository.update(question_id, {"image_path": image_path})
    return questions_repository.find_by_id(question_id)


@router.delete("/api/questions/{question_id}/image", response_model=StatusResponse)
def delete_question_image(question_id: str):
    """Question se image hata deta hai — DB mein NULL, file disk se delete."""
    q = questions_repository.find_by_id(question_id)
    if q is None:
        raise HTTPException(status_code=404, detail="Question nahi mila.")

    if q.get("image_path"):
        file_path = _UPLOADS_DIR / Path(q["image_path"]).name
        if file_path.exists():
            file_path.unlink()

    questions_repository.update(question_id, {"image_path": None})
    return {"status": "ok"}


@router.post("/api/questions/{question_id}/image-from-library", response_model=Question)
def copy_library_image_to_question(question_id: str, body: CopyFromLibraryRequest):
    """Library se ek image chunkar us question ke saath attach karta hai.
    File static/library/ se static/uploads/{question_id}.{ext} mein copy hoti hai.
    (Option B: uploads mein copy — library image delete hone par paper safe rehta hai.)"""
    if questions_repository.find_by_id(question_id) is None:
        raise HTTPException(status_code=404, detail="Question nahi mila.")

    img = library_repository.find_by_id(body.image_id)
    if img is None:
        raise HTTPException(status_code=404, detail="Library image nahi mili.")

    src = _LIBRARY_DIR / Path(img["file_path"]).name
    if not src.exists():
        raise HTTPException(status_code=404, detail="Library image file disk par nahi mili.")

    ext = Path(img["file_path"]).suffix.lstrip(".")

    # Delete any existing image for this question (all extensions)
    for old_ext in _ALLOWED_MIME.values():
        old = _UPLOADS_DIR / f"{question_id}.{old_ext}"
        if old.exists():
            old.unlink()

    dest = _UPLOADS_DIR / f"{question_id}.{ext}"
    dest.write_bytes(src.read_bytes())

    questions_repository.update(question_id, {
        "image_path": f"uploads/{question_id}.{ext}",
        "image_size": body.image_size or "medium",
    })
    return questions_repository.find_by_id(question_id)


@router.post("/api/bank/questions", response_model=Question, status_code=201)
def create_manual_question(req: ManualQuestionRequest):
    """Teacher ka khud likha question bank mein save karta hai (source='manual').
    syllabus_topic_id diya ho to subject/topic usi se resolve hote hain."""
    resolved_subject = req.subject or ""
    resolved_topic = req.topic or ""

    if req.syllabus_topic_id:
        topic_row = syllabus_service.get_topic(req.syllabus_topic_id)
        if not topic_row:
            raise HTTPException(status_code=404, detail="syllabus_topic_id nahi mila.")
        resolved_subject = topic_row["subject"]
        resolved_topic = topic_row["subtopic_title"]

    if not resolved_subject or not resolved_topic:
        raise HTTPException(
            status_code=400,
            detail="syllabus_topic_id ya phir subject aur topic dono zaroori hain.",
        )

    qid = question_service.save_manual_question(req, resolved_subject, resolved_topic)
    return questions_repository.find_by_id(qid)


@router.patch("/api/bank/questions/{question_id}", response_model=Question)
def update_manual_question(question_id: str, req: ManualQuestionUpdateRequest):
    """Sirf source='manual' wale question update karta hai — gemini questions is route se nahi badle."""
    found = question_service.update_manual_question(question_id, req)
    if not found:
        raise HTTPException(
            status_code=404,
            detail="Manual question nahi mila (ya ye Gemini-generated hai, jo is route se edit nahi hota).",
        )
    return questions_repository.find_by_id(question_id)


@router.delete("/api/bank/questions/{question_id}", response_model=StatusResponse)
def delete_manual_question(question_id: str):
    """Sirf source='manual' wala question delete karta hai — gemini questions protected hain."""
    deleted = question_service.delete_manual_question(question_id)
    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Manual question nahi mila (ya ye Gemini-generated hai, jo delete nahi hota).",
        )
    return {"status": "ok"}


@router.post("/api/questions/bulk-import")
def bulk_import_questions(file: UploadFile = File(...)):
    """Excel (.xlsx) ya CSV file se questions bulk mein import karta hai.
    Har row ek manual question banta hai. Ek galat row se poori file fail nahi hoti —
    sirf woh row skip hoti hai aur report mein wajah aati hai."""
    allowed_ext = {"xlsx", "xls", "csv"}
    ext = (file.filename or "").rsplit(".", 1)[-1].lower()
    if ext not in allowed_ext:
        raise HTTPException(
            status_code=400,
            detail="Sirf .xlsx, .xls, ya .csv files allowed hain.",
        )
    try:
        contents = file.file.read()
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail="File padhne mein masla aaya — dobara try karein.",
        ) from e
    return bulk_import_service.import_from_bytes(contents, file.filename or "upload.xlsx")


@router.get("/api/questions", response_model=List[Question])
def list_questions(
    subject: Optional[str] = None,
    topic: Optional[str] = None,
    bloom_level: Optional[str] = None,
    syllabus_topic_id: Optional[str] = None,
    q: Optional[str] = None,
    status: Optional[str] = None,
):
    """Question bank browse karne ke liye. syllabus_topic_id se filter karo to
    sirf usi topic ke linked questions aayein ge (hierarchy picker ke liye).
    q se question text/keywords mein search karo; status se published/draft/archived filter karo."""
    return question_service.list_questions(
        subject=subject, topic=topic, bloom_level=bloom_level,
        syllabus_topic_id=syllabus_topic_id, q=q, status=status,
    )
