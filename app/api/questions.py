"""HTTP routes for question generation and listing."""

from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.repositories import library_repository, questions_repository
from app.schemas.requests import (
    CopyFromLibraryRequest,
    GenerateQuestionsRequest,
    UpdateQuestionRequest,
)
from app.schemas.responses import GenerateQuestionsResponse, Question, StatusResponse
from app.services import question_service, syllabus_service

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


@router.get("/api/questions", response_model=List[Question])
def list_questions(
    subject: Optional[str] = None,
    topic: Optional[str] = None,
    bloom_level: Optional[str] = None,
    syllabus_topic_id: Optional[str] = None,
):
    """Question bank browse karne ke liye. syllabus_topic_id se filter karo to
    sirf usi topic ke linked questions aayein ge (hierarchy picker ke liye)."""
    return question_service.list_questions(
        subject=subject, topic=topic, bloom_level=bloom_level, syllabus_topic_id=syllabus_topic_id
    )
