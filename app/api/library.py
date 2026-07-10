"""HTTP routes for the image library (shared teacher-uploaded images)."""

import uuid
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.repositories import library_repository
from app.schemas.responses import LibraryImage, StatusResponse

router = APIRouter()

_LIBRARY_DIR = Path(__file__).parent.parent.parent / "static" / "library"
_LIBRARY_DIR.mkdir(parents=True, exist_ok=True)

_ALLOWED_MIME = {"image/jpeg": "jpg", "image/png": "png"}
_MAX_BYTES = 2 * 1024 * 1024  # 2 MB


@router.post("/api/library", response_model=LibraryImage)
def upload_library_image(
    name: str = Form(...),
    subject: Optional[str] = Form(default=None),
    grade: Optional[str] = Form(default=None),
    syllabus_topic_id: Optional[str] = Form(default=None),
    uploaded_by: Optional[str] = Form(default=None),
    file: UploadFile = File(...),
):
    """Library mein ek nayi image add karta hai — naam + optional tags ke saath."""
    if not name.strip():
        raise HTTPException(status_code=400, detail="Image ka naam khali nahi ho sakta.")

    content_type = file.content_type or ""
    ext = _ALLOWED_MIME.get(content_type)
    if ext is None:
        raise HTTPException(
            status_code=400,
            detail="Sirf JPG aur PNG images allowed hain. / Only JPG and PNG allowed.",
        )

    contents = file.file.read()
    if len(contents) > _MAX_BYTES:
        raise HTTPException(
            status_code=400,
            detail="Image 2 MB se chhhoti honi chahiye. / Image must be under 2 MB.",
        )

    image_id = str(uuid.uuid4())
    dest = _LIBRARY_DIR / f"{image_id}.{ext}"
    dest.write_bytes(contents)

    row = {
        "id": image_id,
        "file_path": f"library/{image_id}.{ext}",
        "name": name.strip(),
        "subject": subject.strip() if subject else None,
        "grade": grade.strip() if grade else None,
        "syllabus_topic_id": syllabus_topic_id or None,
        "uploaded_by": uploaded_by.strip() if uploaded_by else None,
    }
    library_repository.insert(row)
    return library_repository.find_by_id(image_id)


@router.get("/api/library", response_model=List[LibraryImage])
def list_library_images(
    subject: Optional[str] = None,
    grade: Optional[str] = None,
    syllabus_topic_id: Optional[str] = None,
    q: Optional[str] = None,
):
    """Library images list karta hai — subject/grade/topic filter + naam search."""
    return library_repository.list_by_filters(
        subject=subject, grade=grade, syllabus_topic_id=syllabus_topic_id, q=q
    )


@router.delete("/api/library/{image_id}", response_model=StatusResponse)
def delete_library_image(image_id: str):
    """Library se image hata deta hai — DB row delete + file disk se remove."""
    img = library_repository.find_by_id(image_id)
    if img is None:
        raise HTTPException(status_code=404, detail="Library image nahi mili.")

    file_path = _LIBRARY_DIR / Path(img["file_path"]).name
    if file_path.exists():
        file_path.unlink()

    library_repository.delete(image_id)
    return {"status": "ok"}


@router.get("/api/library/topics-with-images")
def topics_with_images(ids: str = ""):
    """Comma-separated syllabus_topic_ids mein se har topic ka image count wapas karta hai.
    Auto-suggest ke liye: frontend ek batch call mein saare topic IDs check karta hai.
    Response: {"topics": {"topic-id-1": 2, "topic-id-2": 1}} — sirf jinke images hain."""
    if not ids.strip():
        return {"topics": {}}
    id_list = [i.strip() for i in ids.split(",") if i.strip()]
    counts = library_repository.topic_image_counts(id_list)
    return {"topics": counts}
