"""Tests for PATCH /api/library/{image_id} — naam aur topic edit."""

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
    b"\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\x18\xd8N"
    b"\x00\x00\x00\x00IEND\xaeB`\x82"
)


def _upload(tmp_path, monkeypatch, *, name="TestImg", subject="Math", grade="5", topic_id=None):
    lib = tmp_path / "library"
    lib.mkdir(exist_ok=True)
    monkeypatch.setattr(library_module, "_LIBRARY_DIR", lib)
    resp = client.post(
        "/api/library",
        data={"name": name, "subject": subject, "grade": grade,
              "syllabus_topic_id": topic_id or ""},
        files={"file": ("img.png", io.BytesIO(_PNG), "image/png")},
    )
    assert resp.status_code == 200
    return resp.json()


def _insert_topic(topic_id: str, subject: str = "Science", grade: str = "6") -> None:
    """Test mein seedha DB mein topic insert karo (API bypass)."""
    conn = get_connection()
    conn.execute(
        "INSERT INTO syllabus_topics (id, subject, grade, unit_no, unit_title,"
        " subtopic_title, activity_type) VALUES (?,?,?,?,?,?,?)",
        (topic_id, subject, grade, 1, "Unit 1", "Sub 1", "activity"),
    )
    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# Naam rename — success
# ---------------------------------------------------------------------------

def test_rename_updates_name_and_normalized(test_db, tmp_path, monkeypatch):
    img = _upload(tmp_path, monkeypatch, name="OldName")
    resp = client.patch(f"/api/library/{img['id']}", json={"name": "newname"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "newname"

    row = library_repository.find_by_id(img["id"])
    assert row["name"] == "newname"
    assert row["name_normalized"] == "newname"


def test_rename_normalizes_mixed_case(test_db, tmp_path, monkeypatch):
    img = _upload(tmp_path, monkeypatch, name="OldName")
    resp = client.patch(f"/api/library/{img['id']}", json={"name": "  Oranges5  "})
    assert resp.status_code == 200
    row = library_repository.find_by_id(img["id"])
    assert row["name"] == "Oranges5"
    assert row["name_normalized"] == "oranges5"


def test_rename_same_name_allowed(test_db, tmp_path, monkeypatch):
    """Apna hi naam dobara save karna valid hai — duplicate nahi lagta."""
    img = _upload(tmp_path, monkeypatch, name="MyImage")
    resp = client.patch(f"/api/library/{img['id']}", json={"name": "MyImage"})
    assert resp.status_code == 200


# ---------------------------------------------------------------------------
# Naam rename — errors
# ---------------------------------------------------------------------------

def test_rename_duplicate_returns_409(test_db, tmp_path, monkeypatch):
    _upload(tmp_path, monkeypatch, name="FirstImg")
    img2 = _upload(tmp_path, monkeypatch, name="SecondImg")
    resp = client.patch(f"/api/library/{img2['id']}", json={"name": "FirstImg"})
    assert resp.status_code == 409


def test_rename_blank_name_returns_422(test_db, tmp_path, monkeypatch):
    img = _upload(tmp_path, monkeypatch, name="SomeName")
    resp = client.patch(f"/api/library/{img['id']}", json={"name": "   "})
    assert resp.status_code == 422


def test_patch_no_fields_returns_422(test_db, tmp_path, monkeypatch):
    img = _upload(tmp_path, monkeypatch, name="SomeName")
    resp = client.patch(f"/api/library/{img['id']}", json={})
    assert resp.status_code == 422


def test_patch_unknown_image_returns_404(test_db, tmp_path, monkeypatch):
    lib = tmp_path / "library"
    lib.mkdir(exist_ok=True)
    monkeypatch.setattr(library_module, "_LIBRARY_DIR", lib)
    resp = client.patch("/api/library/does-not-exist", json={"name": "abc"})
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Topic change
# ---------------------------------------------------------------------------

def test_topic_change_syncs_subject_and_grade(test_db, tmp_path, monkeypatch):
    img = _upload(tmp_path, monkeypatch, name="Img1", subject="Math", grade="5")
    _insert_topic("topic-sci-6", subject="Science", grade="6")

    resp = client.patch(f"/api/library/{img['id']}", json={"syllabus_topic_id": "topic-sci-6"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["syllabus_topic_id"] == "topic-sci-6"
    assert data["subject"] == "Science"
    assert data["grade"] == "6"


def test_topic_null_clears_topic_and_subject_grade(test_db, tmp_path, monkeypatch):
    _insert_topic("topic-x")
    img = _upload(tmp_path, monkeypatch, name="Img2", topic_id="topic-x")

    resp = client.patch(f"/api/library/{img['id']}", json={"syllabus_topic_id": None})
    assert resp.status_code == 200
    data = resp.json()
    assert data["syllabus_topic_id"] is None
    assert data["subject"] is None
    assert data["grade"] is None


def test_invalid_topic_returns_400(test_db, tmp_path, monkeypatch):
    img = _upload(tmp_path, monkeypatch, name="Img3")
    resp = client.patch(f"/api/library/{img['id']}", json={"syllabus_topic_id": "non-existent-topic"})
    assert resp.status_code == 400


# ---------------------------------------------------------------------------
# Naam + Topic ek saath
# ---------------------------------------------------------------------------

def test_rename_and_topic_change_together(test_db, tmp_path, monkeypatch):
    _insert_topic("topic-eng-7", subject="English", grade="7")
    img = _upload(tmp_path, monkeypatch, name="OldImg", subject="Math", grade="5")

    resp = client.patch(
        f"/api/library/{img['id']}",
        json={"name": "newimg", "syllabus_topic_id": "topic-eng-7"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "newimg"
    assert data["syllabus_topic_id"] == "topic-eng-7"
    assert data["subject"] == "English"
    assert data["grade"] == "7"
