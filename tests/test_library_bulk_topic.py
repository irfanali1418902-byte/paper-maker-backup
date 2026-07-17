"""Tests for PATCH /api/library/bulk-topic — kai images ka topic ek saath."""

import io

from fastapi.testclient import TestClient

import app.api.library as library_module
from app.core.database import get_connection
from app.main import app
from app.repositories import library_repository

client = TestClient(app)

_PNG = (
    b"\x89PNG\r\n\x1a\n"
    b"\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
    b"\x08\x02\x00\x00\x00\x90wS\xde"
    b"\x00\x00\x00\x0cIDATx\x9cc\xf8\xff\xff?\x00\x05\xfe\x02\xfe\r\xefF\xb8"
    b"\x00\x00\x00\x00IEND\xaeB`\x82"
)


def _upload(tmp_path, monkeypatch, *, name, subject="Math", grade="5", topic_id=None):
    lib = tmp_path / "library"
    lib.mkdir(exist_ok=True)
    monkeypatch.setattr(library_module, "_LIBRARY_DIR", lib)
    resp = client.post(
        "/api/library",
        data={"name": name, "subject": subject, "grade": grade,
              "syllabus_topic_id": topic_id or ""},
        files={"file": (f"{name}.png", io.BytesIO(_PNG), "image/png")},
    )
    assert resp.status_code == 200
    return resp.json()


def _insert_topic(topic_id: str, subject: str = "Science", grade: str = "6") -> None:
    conn = get_connection()
    conn.execute(
        "INSERT INTO syllabus_topics (id, subject, grade, unit_no, unit_title,"
        " subtopic_title, activity_type) VALUES (?,?,?,?,?,?,?)",
        (topic_id, subject, grade, 1, "Unit 1", "Sub 1", "activity"),
    )
    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# Success
# ---------------------------------------------------------------------------

def test_bulk_topic_updates_all_images(test_db, tmp_path, monkeypatch):
    img1 = _upload(tmp_path, monkeypatch, name="img1", subject="Math", grade="5")
    img2 = _upload(tmp_path, monkeypatch, name="img2", subject="Math", grade="5")
    img3 = _upload(tmp_path, monkeypatch, name="img3", subject="Math", grade="5")
    _insert_topic("topic-sci-6", subject="Science", grade="6")

    resp = client.patch(
        "/api/library/bulk-topic",
        json={"image_ids": [img1["id"], img2["id"], img3["id"]], "syllabus_topic_id": "topic-sci-6"},
    )
    assert resp.status_code == 200
    assert resp.json()["updated"] == 3

    for img_id in (img1["id"], img2["id"], img3["id"]):
        row = library_repository.find_by_id(img_id)
        assert row["syllabus_topic_id"] == "topic-sci-6"
        assert row["subject"] == "Science"
        assert row["grade"] == "6"


# ---------------------------------------------------------------------------
# Topic null — unlink
# ---------------------------------------------------------------------------

def test_bulk_topic_null_unlinks_all(test_db, tmp_path, monkeypatch):
    _insert_topic("topic-abc")
    img1 = _upload(tmp_path, monkeypatch, name="x1", topic_id="topic-abc")
    img2 = _upload(tmp_path, monkeypatch, name="x2", topic_id="topic-abc")

    resp = client.patch(
        "/api/library/bulk-topic",
        json={"image_ids": [img1["id"], img2["id"]], "syllabus_topic_id": None},
    )
    assert resp.status_code == 200
    assert resp.json()["updated"] == 2

    for img_id in (img1["id"], img2["id"]):
        row = library_repository.find_by_id(img_id)
        assert row["syllabus_topic_id"] is None
        assert row["subject"] is None
        assert row["grade"] is None


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------

def test_bulk_topic_empty_ids_returns_422(test_db, tmp_path, monkeypatch):
    lib = tmp_path / "library"
    lib.mkdir(exist_ok=True)
    monkeypatch.setattr(library_module, "_LIBRARY_DIR", lib)
    resp = client.patch(
        "/api/library/bulk-topic",
        json={"image_ids": [], "syllabus_topic_id": "topic-x"},
    )
    assert resp.status_code == 422


def test_bulk_topic_invalid_topic_returns_400(test_db, tmp_path, monkeypatch):
    img = _upload(tmp_path, monkeypatch, name="anyimg")
    resp = client.patch(
        "/api/library/bulk-topic",
        json={"image_ids": [img["id"]], "syllabus_topic_id": "non-existent"},
    )
    assert resp.status_code == 400


def test_bulk_topic_partial_invalid_ids_updates_valid_only(test_db, tmp_path, monkeypatch):
    """Invalid IDs silently skip — sirf matching rows update hoti hain."""
    img = _upload(tmp_path, monkeypatch, name="realimg")
    _insert_topic("topic-eng-7", subject="English", grade="7")

    resp = client.patch(
        "/api/library/bulk-topic",
        json={"image_ids": [img["id"], "fake-id-1", "fake-id-2"], "syllabus_topic_id": "topic-eng-7"},
    )
    assert resp.status_code == 200
    assert resp.json()["updated"] == 1

    row = library_repository.find_by_id(img["id"])
    assert row["syllabus_topic_id"] == "topic-eng-7"
