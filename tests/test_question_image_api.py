"""Tests for POST /api/questions/{id}/image and DELETE /api/questions/{id}/image.

_UPLOADS_DIR is monkeypatched to tmp_path so static/uploads/ never gets touched.
The test_db fixture (conftest.py) gives each test its own fresh SQLite file.
"""

import io

import pytest
from fastapi.testclient import TestClient

import app.api.questions as questions_module
from app.main import app
from app.repositories import questions_repository

client = TestClient(app)

# Minimal 1x1 valid PNG bytes (binary-safe, will pass content-type check)
_PNG_BYTES = (
    b"\x89PNG\r\n\x1a\n"
    b"\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
    b"\x08\x02\x00\x00\x00\x90wS\xde"
    b"\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\x18\xd8N"
    b"\x00\x00\x00\x00IEND\xaeB`\x82"
)

# Minimal 1x1 JFIF JPEG bytes
_JPG_BYTES = (
    b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00"
    b"\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t"
    b"\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a"
    b"\x1f\x1e\x1d\x1a\x1c\x1c $.' \",#\x1c\x1c(7),01444\x1f'9=82<.342\x1eB"
    b"\xb4\x00\x00\x00\x00\xff\xd9"
)


def _insert_question(qid: str = "test-q-001") -> dict:
    """Minimal question row — only mandatory columns."""
    row = {
        "id": qid,
        "subject": "Science",
        "topic": "Plants",
        "bloom_level": "remember",
        "difficulty": "easy",
        "question_type": "short-answer",
        "marks": 2,
        "question_en": "What is photosynthesis?",
        "question_ur": None,
        "options_en": None,
        "options_ur": None,
        "correct_answer_en": None,
        "correct_answer_ur": None,
        "explanation_en": None,
        "explanation_ur": None,
        "visual_emoji": None,
        "visual_count": None,
        "image_path": None,
    }
    questions_repository.insert(row)
    return row


# ---------------------------------------------------------------------------
# Successful upload — PNG
# ---------------------------------------------------------------------------

def test_upload_png_returns_200_and_sets_image_path(test_db, tmp_path, monkeypatch):
    uploads = tmp_path / "uploads"
    uploads.mkdir()
    monkeypatch.setattr(questions_module, "_UPLOADS_DIR", uploads)
    _insert_question("q-png")

    resp = client.post(
        "/api/questions/q-png/image",
        files={"file": ("photo.png", io.BytesIO(_PNG_BYTES), "image/png")},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["image_path"] == "uploads/q-png.png"

    # File must exist on disk
    assert (uploads / "q-png.png").exists()

    # DB must also reflect the path
    q = questions_repository.find_by_id("q-png")
    assert q["image_path"] == "uploads/q-png.png"


# ---------------------------------------------------------------------------
# Successful upload — JPG
# ---------------------------------------------------------------------------

def test_upload_jpg_returns_200_and_sets_image_path(test_db, tmp_path, monkeypatch):
    uploads = tmp_path / "uploads"
    uploads.mkdir()
    monkeypatch.setattr(questions_module, "_UPLOADS_DIR", uploads)
    _insert_question("q-jpg")

    resp = client.post(
        "/api/questions/q-jpg/image",
        files={"file": ("pic.jpg", io.BytesIO(_JPG_BYTES), "image/jpeg")},
    )
    assert resp.status_code == 200
    assert resp.json()["image_path"] == "uploads/q-jpg.jpg"
    assert (uploads / "q-jpg.jpg").exists()


# ---------------------------------------------------------------------------
# Size > 2 MB -> 400
# ---------------------------------------------------------------------------

def test_upload_oversized_file_returns_400(test_db, tmp_path, monkeypatch):
    uploads = tmp_path / "uploads"
    uploads.mkdir()
    monkeypatch.setattr(questions_module, "_UPLOADS_DIR", uploads)
    _insert_question("q-big")

    big = b"x" * (2 * 1024 * 1024 + 1)
    resp = client.post(
        "/api/questions/q-big/image",
        files={"file": ("big.png", io.BytesIO(big), "image/png")},
    )
    assert resp.status_code == 400
    # No image file must be written in uploads dir
    assert not any(uploads.iterdir())


# ---------------------------------------------------------------------------
# Wrong MIME -> 400
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("mime", ["text/plain", "image/gif", "application/pdf"])
def test_upload_wrong_mime_returns_400(test_db, tmp_path, monkeypatch, mime):
    uploads = tmp_path / "uploads"
    uploads.mkdir()
    monkeypatch.setattr(questions_module, "_UPLOADS_DIR", uploads)
    _insert_question(f"q-bad-{mime.replace('/', '-')}")

    resp = client.post(
        f"/api/questions/q-bad-{mime.replace('/', '-')}/image",
        files={"file": ("file.dat", io.BytesIO(b"garbage"), mime)},
    )
    assert resp.status_code == 400
    assert not any(uploads.iterdir())


# ---------------------------------------------------------------------------
# Non-existent question_id -> 404
# ---------------------------------------------------------------------------

def test_upload_unknown_question_returns_404(test_db, tmp_path, monkeypatch):
    uploads = tmp_path / "uploads"
    uploads.mkdir()
    monkeypatch.setattr(questions_module, "_UPLOADS_DIR", uploads)

    resp = client.post(
        "/api/questions/does-not-exist/image",
        files={"file": ("x.png", io.BytesIO(_PNG_BYTES), "image/png")},
    )
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Delete: image_path NULL in DB + file removed from disk
# ---------------------------------------------------------------------------

def test_delete_clears_db_and_removes_file(test_db, tmp_path, monkeypatch):
    uploads = tmp_path / "uploads"
    uploads.mkdir()
    monkeypatch.setattr(questions_module, "_UPLOADS_DIR", uploads)
    _insert_question("q-del")

    # Upload first
    client.post(
        "/api/questions/q-del/image",
        files={"file": ("img.png", io.BytesIO(_PNG_BYTES), "image/png")},
    )
    assert (uploads / "q-del.png").exists()

    # Now delete
    resp = client.delete("/api/questions/q-del/image")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"

    # File must be gone
    assert not (uploads / "q-del.png").exists()

    # DB must be NULL
    q = questions_repository.find_by_id("q-del")
    assert q["image_path"] is None


# ---------------------------------------------------------------------------
# Replace: .png -> .jpg => old .png must not remain (orphan check)
# ---------------------------------------------------------------------------

def test_replace_png_with_jpg_removes_old_png(test_db, tmp_path, monkeypatch):
    uploads = tmp_path / "uploads"
    uploads.mkdir()
    monkeypatch.setattr(questions_module, "_UPLOADS_DIR", uploads)
    _insert_question("q-replace")

    # Upload PNG first
    client.post(
        "/api/questions/q-replace/image",
        files={"file": ("orig.png", io.BytesIO(_PNG_BYTES), "image/png")},
    )
    assert (uploads / "q-replace.png").exists()

    # Replace with JPG
    resp = client.post(
        "/api/questions/q-replace/image",
        files={"file": ("new.jpg", io.BytesIO(_JPG_BYTES), "image/jpeg")},
    )
    assert resp.status_code == 200

    # Old PNG must be gone
    assert not (uploads / "q-replace.png").exists()
    # New JPG must exist
    assert (uploads / "q-replace.jpg").exists()
    # DB reflects new path
    q = questions_repository.find_by_id("q-replace")
    assert q["image_path"] == "uploads/q-replace.jpg"
