"""Tests for POST /api/questions/{id}/image-from-library.

Monkeypatches both _UPLOADS_DIR and _LIBRARY_DIR in questions module.
Library image file is placed in tmp_path/library/ manually (no API call
needed for setup — we just need the file on disk and a DB row).
"""

from pathlib import Path

from fastapi.testclient import TestClient

import app.api.questions as questions_module
from app.main import app
from app.repositories import library_repository, questions_repository

client = TestClient(app)

_PNG = (
    b"\x89PNG\r\n\x1a\n"
    b"\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
    b"\x08\x02\x00\x00\x00\x90wS\xde"
    b"\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\x18\xd8N"
    b"\x00\x00\x00\x00IEND\xaeB`\x82"
)
_JPG = (
    b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00"
    b"\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t"
    b"\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a"
    b"\x1f\x1e\x1d\x1a\x1c\x1c $.' \",#\x1c\x1c(7),01444\x1f'9=82<.342\x1eB"
    b"\xb4\x00\x00\x00\x00\xff\xd9"
)


def _insert_question(qid: str) -> None:
    questions_repository.insert({
        "id": qid, "subject": "Science", "topic": "Cells",
        "bloom_level": "remember", "difficulty": "easy",
        "question_type": "short-answer", "marks": 2,
        "question_en": "What is a cell?", "question_ur": None,
        "options_en": None, "options_ur": None,
        "correct_answer_en": None, "correct_answer_ur": None,
        "explanation_en": None, "explanation_ur": None,
        "visual_emoji": None, "visual_count": None, "image_path": None,
    })


def _seed_library_image(lib_dir: Path, image_id: str, ext: str = "png", data: bytes = _PNG) -> None:
    """Creates library DB row + file on disk."""
    fname = f"{image_id}.{ext}"
    (lib_dir / fname).write_bytes(data)
    library_repository.insert({
        "id": image_id,
        "file_path": f"library/{fname}",
        "name": "Test lib image",
        "subject": "Science",
        "grade": "5",
        "syllabus_topic_id": "topic-test",
        "uploaded_by": None,
    })


# ---------------------------------------------------------------------------
# Success — PNG
# ---------------------------------------------------------------------------

def test_copy_png_library_image_to_question(test_db, tmp_path, monkeypatch):
    uploads = tmp_path / "uploads"
    uploads.mkdir()
    lib = tmp_path / "library"
    lib.mkdir()
    monkeypatch.setattr(questions_module, "_UPLOADS_DIR", uploads)
    monkeypatch.setattr(questions_module, "_LIBRARY_DIR", lib)

    _insert_question("q-lib-1")
    _seed_library_image(lib, "img-001", ext="png")

    resp = client.post("/api/questions/q-lib-1/image-from-library",
                       json={"image_id": "img-001", "image_size": "medium"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["image_path"] == "uploads/q-lib-1.png"
    assert data["image_size"] == "medium"
    assert (uploads / "q-lib-1.png").exists()
    # Library file must NOT be deleted
    assert (lib / "img-001.png").exists()


# ---------------------------------------------------------------------------
# Success — JPG
# ---------------------------------------------------------------------------

def test_copy_jpg_library_image_to_question(test_db, tmp_path, monkeypatch):
    uploads = tmp_path / "uploads"
    uploads.mkdir()
    lib = tmp_path / "library"
    lib.mkdir()
    monkeypatch.setattr(questions_module, "_UPLOADS_DIR", uploads)
    monkeypatch.setattr(questions_module, "_LIBRARY_DIR", lib)

    _insert_question("q-lib-2")
    _seed_library_image(lib, "img-002", ext="jpg", data=_JPG)

    resp = client.post("/api/questions/q-lib-2/image-from-library",
                       json={"image_id": "img-002", "image_size": "large"})
    assert resp.status_code == 200
    assert resp.json()["image_path"] == "uploads/q-lib-2.jpg"
    assert resp.json()["image_size"] == "large"
    assert (uploads / "q-lib-2.jpg").exists()


# ---------------------------------------------------------------------------
# Default image_size = "medium"
# ---------------------------------------------------------------------------

def test_copy_default_size_is_medium(test_db, tmp_path, monkeypatch):
    uploads = tmp_path / "uploads"
    uploads.mkdir()
    lib = tmp_path / "library"
    lib.mkdir()
    monkeypatch.setattr(questions_module, "_UPLOADS_DIR", uploads)
    monkeypatch.setattr(questions_module, "_LIBRARY_DIR", lib)

    _insert_question("q-lib-3")
    _seed_library_image(lib, "img-003")

    resp = client.post("/api/questions/q-lib-3/image-from-library",
                       json={"image_id": "img-003"})
    assert resp.status_code == 200
    assert resp.json()["image_size"] == "medium"


# ---------------------------------------------------------------------------
# Replace: old upload file removed when extension changes
# ---------------------------------------------------------------------------

def test_copy_replaces_existing_upload(test_db, tmp_path, monkeypatch):
    uploads = tmp_path / "uploads"
    uploads.mkdir()
    lib = tmp_path / "library"
    lib.mkdir()
    monkeypatch.setattr(questions_module, "_UPLOADS_DIR", uploads)
    monkeypatch.setattr(questions_module, "_LIBRARY_DIR", lib)

    _insert_question("q-lib-4")

    # Pre-place an old PNG upload
    (uploads / "q-lib-4.png").write_bytes(_PNG)
    questions_repository.update("q-lib-4", {"image_path": "uploads/q-lib-4.png"})

    # Library image is JPG
    _seed_library_image(lib, "img-004", ext="jpg", data=_JPG)

    resp = client.post("/api/questions/q-lib-4/image-from-library",
                       json={"image_id": "img-004", "image_size": "small"})
    assert resp.status_code == 200
    assert not (uploads / "q-lib-4.png").exists()   # old PNG removed
    assert (uploads / "q-lib-4.jpg").exists()        # new JPG present


# ---------------------------------------------------------------------------
# Unknown question → 404
# ---------------------------------------------------------------------------

def test_copy_unknown_question_returns_404(test_db, tmp_path, monkeypatch):
    uploads = tmp_path / "uploads"
    uploads.mkdir()
    lib = tmp_path / "library"
    lib.mkdir()
    monkeypatch.setattr(questions_module, "_UPLOADS_DIR", uploads)
    monkeypatch.setattr(questions_module, "_LIBRARY_DIR", lib)

    _seed_library_image(lib, "img-x")
    resp = client.post("/api/questions/ghost-q/image-from-library",
                       json={"image_id": "img-x"})
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Unknown library image → 404
# ---------------------------------------------------------------------------

def test_copy_unknown_library_image_returns_404(test_db, tmp_path, monkeypatch):
    uploads = tmp_path / "uploads"
    uploads.mkdir()
    lib = tmp_path / "library"
    lib.mkdir()
    monkeypatch.setattr(questions_module, "_UPLOADS_DIR", uploads)
    monkeypatch.setattr(questions_module, "_LIBRARY_DIR", lib)

    _insert_question("q-lib-5")
    resp = client.post("/api/questions/q-lib-5/image-from-library",
                       json={"image_id": "no-such-image"})
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Library file missing from disk → 404
# ---------------------------------------------------------------------------

def test_copy_missing_disk_file_returns_404(test_db, tmp_path, monkeypatch):
    uploads = tmp_path / "uploads"
    uploads.mkdir()
    lib = tmp_path / "library"
    lib.mkdir()
    monkeypatch.setattr(questions_module, "_UPLOADS_DIR", uploads)
    monkeypatch.setattr(questions_module, "_LIBRARY_DIR", lib)

    _insert_question("q-lib-6")
    # Insert DB row but do NOT create the file
    library_repository.insert({
        "id": "img-ghost",
        "file_path": "library/img-ghost.png",
        "name": "Ghost", "subject": None, "grade": None,
        "syllabus_topic_id": None, "uploaded_by": None,
    })

    resp = client.post("/api/questions/q-lib-6/image-from-library",
                       json={"image_id": "img-ghost"})
    assert resp.status_code == 404
