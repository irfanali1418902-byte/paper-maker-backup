"""HTTP routes for the image library (shared teacher-uploaded images)."""

import uuid
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse

from app.repositories import library_repository, syllabus_repository
from app.schemas.requests import (
    BulkUpdateMetaRequest,
    BulkUpdateTopicRequest,
    UpdateLibraryImageRequest,
)
from app.schemas.responses import LibraryImage, StatusResponse
from app.services import library_meta_import_service

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
    category: Optional[str] = None,
    question_type: Optional[str] = None,
):
    """Library images list karta hai — subject/grade/topic/category/question_type filter + naam+keywords search."""
    return library_repository.list_by_filters(
        subject=subject,
        grade=grade,
        syllabus_topic_id=syllabus_topic_id,
        q=q,
        category=category,
        question_type=question_type,
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


@router.patch("/api/library/bulk-topic")
def bulk_update_library_topic(body: BulkUpdateTopicRequest):
    """Kai library images ka topic (aur subject/grade) ek saath update karo."""
    if body.syllabus_topic_id is None:
        updated = library_repository.bulk_update_topic(body.image_ids, None, None, None)
    else:
        topic = syllabus_repository.find_by_id(body.syllabus_topic_id)
        if topic is None:
            raise HTTPException(status_code=400, detail="Topic nahi mila.")
        updated = library_repository.bulk_update_topic(
            body.image_ids,
            body.syllabus_topic_id,
            topic["subject"],
            topic.get("grade"),
        )
    return {"updated": updated}


@router.patch("/api/library/bulk-meta")
def bulk_update_library_meta(body: BulkUpdateMetaRequest):
    """Kai library images ke smart tags (keywords, category, question_types) ek saath update karo."""
    fields: dict = {}
    if "keywords" in body.model_fields_set:
        fields["keywords"] = body.keywords
    if "category" in body.model_fields_set:
        fields["category"] = body.category
    if "question_types" in body.model_fields_set:
        fields["question_types"] = body.question_types

    updated = library_repository.bulk_update_meta(body.image_ids, fields, body.keywords_mode)
    return {"updated": updated}


@router.patch("/api/library/{image_id}", response_model=LibraryImage)
def update_library_image(image_id: str, body: UpdateLibraryImageRequest):
    """Library image ka naam, topic, ya smart fields update karo."""
    img = library_repository.find_by_id(image_id)
    if img is None:
        raise HTTPException(status_code=404, detail="Library image nahi mili.")

    updates: dict = {}

    if "name" in body.model_fields_set:
        new_name = (body.name or "").strip()
        if not new_name:
            raise HTTPException(status_code=422, detail="Naam khaali nahi ho sakta.")
        if library_repository.name_exists_excluding(new_name, image_id):
            raise HTTPException(status_code=409, detail="Is naam ki image pehle se maujood hai.")
        updates["name"] = new_name
        updates["name_normalized"] = new_name.lower()

    if "syllabus_topic_id" in body.model_fields_set:
        new_topic_id = body.syllabus_topic_id
        if new_topic_id is None:
            updates["syllabus_topic_id"] = None
            updates["subject"] = None
            updates["grade"] = None
        else:
            topic = syllabus_repository.find_by_id(new_topic_id)
            if topic is None:
                raise HTTPException(status_code=400, detail="Topic nahi mila.")
            updates["syllabus_topic_id"] = new_topic_id
            updates["subject"] = topic["subject"]
            updates["grade"] = topic.get("grade")

    for field in ("keywords", "question_types", "category", "source_book", "page_number"):
        if field in body.model_fields_set:
            updates[field] = getattr(body, field)

    library_repository.update_image(image_id, updates)
    return library_repository.find_by_id(image_id)


@router.post("/api/library/bulk")
def bulk_upload_library_images(
    syllabus_topic_id: Optional[str] = Form(default=None),
    subject: Optional[str] = Form(default=None),
    grade: Optional[str] = Form(default=None),
    uploaded_by: Optional[str] = Form(default=None),
    files: List[UploadFile] = File(...),
):
    """Ek saath kai images library mein add karta hai.
    Har file alag validate hoti hai — ek fail hone se baaki nahi rukti.
    Duplicate naam (case-insensitive) skip kiye jaate hain.
    Returns: {added, skipped, results: [{name, status, reason?}]}"""
    added = 0
    skipped = 0
    results = []

    for upload in files:
        fname = (upload.filename or "").strip()
        name = Path(fname).stem if fname else ""

        if not name:
            skipped += 1
            results.append({"name": fname or "(unnamed)", "status": "skip", "reason": "naam nahi mila"})
            continue

        content_type = upload.content_type or ""
        ext = _ALLOWED_MIME.get(content_type)
        if ext is None:
            skipped += 1
            results.append({"name": fname, "status": "skip", "reason": "sirf JPG/PNG allowed hai"})
            continue

        contents = upload.file.read()
        if len(contents) > _MAX_BYTES:
            skipped += 1
            results.append({"name": fname, "status": "skip", "reason": "2 MB se bada hai"})
            continue

        if library_repository.name_exists(name):
            skipped += 1
            results.append({"name": fname, "status": "skip", "reason": "is naam ki image pehle se hai"})
            continue

        image_id = str(uuid.uuid4())
        dest = _LIBRARY_DIR / f"{image_id}.{ext}"
        dest.write_bytes(contents)

        row = {
            "id": image_id,
            "file_path": f"library/{image_id}.{ext}",
            "name": name,
            "subject": subject.strip() if subject else None,
            "grade": grade.strip() if grade else None,
            "syllabus_topic_id": syllabus_topic_id or None,
            "uploaded_by": uploaded_by.strip() if uploaded_by else None,
        }
        library_repository.insert(row)
        added += 1
        results.append({"name": fname, "status": "ok"})

    return {"added": added, "skipped": skipped, "results": results}


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


@router.get("/api/library/categories")
def list_categories():
    """Library mein maujood saari unique categories wapas karo (filter dropdown ke liye)."""
    return {"categories": library_repository.distinct_categories()}


@router.get("/api/library/question-types")
def list_question_types():
    """Library mein maujood saare unique question_types wapas karo (filter ke liye)."""
    return {"question_types": library_repository.distinct_question_types()}


_META_TEMPLATE = Path(__file__).parent.parent.parent / "static" / "library_meta_import_template.xlsx"


@router.get("/api/library/excel-meta-import/template")
def download_meta_import_template():
    """Excel meta import ka template file download karo (.xlsx)."""
    if not _META_TEMPLATE.exists():
        raise HTTPException(status_code=404, detail="Template file nahi mili.")
    return FileResponse(
        path=str(_META_TEMPLATE),
        filename="library_meta_import_template.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


@router.post("/api/library/excel-meta-import")
def excel_meta_import(file: UploadFile = File(...)):
    """Excel file se image library ka meta (topic/keywords/category/question_types) bulk update karo.

    Returns: {updated, skipped, results: [{row, image_name, status, reason?, warnings?}]}
    """
    fname = (file.filename or "").lower()
    if not (fname.endswith(".xlsx") or fname.endswith(".xls") or fname.endswith(".csv")):
        raise HTTPException(
            status_code=400,
            detail="Sirf .xlsx / .xls / .csv file allowed hai.",
        )

    contents = file.file.read()
    try:
        result = library_meta_import_service.import_meta_from_excel(contents)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return result
