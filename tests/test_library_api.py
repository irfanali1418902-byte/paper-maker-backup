"""Tests for /api/library endpoints.

_LIBRARY_DIR monkeypatched to tmp_path — static/library/ never touched.
test_db fixture gives each test a fresh SQLite file.
"""

import io

from fastapi.testclient import TestClient

import app.api.library as library_module
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
_JPG = (
    b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00"
    b"\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t"
    b"\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a"
    b"\x1f\x1e\x1d\x1a\x1c\x1c $.' \",#\x1c\x1c(7),01444\x1f'9=82<.342\x1eB"
    b"\xb4\x00\x00\x00\x00\xff\xd9"
)


def _upload(tmp_path, monkeypatch, *, name="Diagram", subject="Science",
            grade="5", topic_id=None, data=_PNG, mime="image/png"):
    lib = tmp_path / "library"
    lib.mkdir(exist_ok=True)
    monkeypatch.setattr(library_module, "_LIBRARY_DIR", lib)
    return client.post(
        "/api/library",
        data={"name": name, "subject": subject, "grade": grade,
              "syllabus_topic_id": topic_id or ""},
        files={"file": ("img.png", io.BytesIO(data), mime)},
    )


# ---------------------------------------------------------------------------
# Successful upload
# ---------------------------------------------------------------------------

def test_upload_png_returns_200_and_file_saved(test_db, tmp_path, monkeypatch):
    lib = tmp_path / "library"
    lib.mkdir()
    monkeypatch.setattr(library_module, "_LIBRARY_DIR", lib)

    resp = client.post(
        "/api/library",
        data={"name": "Cell diagram", "subject": "Biology", "grade": "9"},
        files={"file": ("cell.png", io.BytesIO(_PNG), "image/png")},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "Cell diagram"
    assert data["subject"] == "Biology"
    assert data["file_path"].startswith("library/")
    assert data["file_path"].endswith(".png")

    fname = data["file_path"].split("/")[1]
    assert (lib / fname).exists()


def test_upload_jpg_accepted(test_db, tmp_path, monkeypatch):
    lib = tmp_path / "library"
    lib.mkdir()
    monkeypatch.setattr(library_module, "_LIBRARY_DIR", lib)

    resp = client.post(
        "/api/library",
        data={"name": "Map"},
        files={"file": ("map.jpg", io.BytesIO(_JPG), "image/jpeg")},
    )
    assert resp.status_code == 200
    assert resp.json()["file_path"].endswith(".jpg")


# ---------------------------------------------------------------------------
# Validation rejections
# ---------------------------------------------------------------------------

def test_upload_wrong_mime_returns_400(test_db, tmp_path, monkeypatch):
    lib = tmp_path / "library"
    lib.mkdir()
    monkeypatch.setattr(library_module, "_LIBRARY_DIR", lib)

    resp = client.post(
        "/api/library",
        data={"name": "bad"},
        files={"file": ("x.gif", io.BytesIO(b"GIF89a"), "image/gif")},
    )
    assert resp.status_code == 400
    assert not any(lib.iterdir())


def test_upload_oversized_returns_400(test_db, tmp_path, monkeypatch):
    lib = tmp_path / "library"
    lib.mkdir()
    monkeypatch.setattr(library_module, "_LIBRARY_DIR", lib)

    resp = client.post(
        "/api/library",
        data={"name": "big"},
        files={"file": ("big.png", io.BytesIO(b"x" * (2 * 1024 * 1024 + 1)), "image/png")},
    )
    assert resp.status_code == 400
    assert not any(lib.iterdir())


def test_upload_blank_name_returns_400(test_db, tmp_path, monkeypatch):
    lib = tmp_path / "library"
    lib.mkdir()
    monkeypatch.setattr(library_module, "_LIBRARY_DIR", lib)

    resp = client.post(
        "/api/library",
        data={"name": "   "},
        files={"file": ("x.png", io.BytesIO(_PNG), "image/png")},
    )
    assert resp.status_code == 400


# ---------------------------------------------------------------------------
# List + filter
# ---------------------------------------------------------------------------

def test_list_returns_all_images(test_db, tmp_path, monkeypatch):
    lib = tmp_path / "library"
    lib.mkdir()
    monkeypatch.setattr(library_module, "_LIBRARY_DIR", lib)

    client.post("/api/library", data={"name": "A", "subject": "Math"},
                files={"file": ("a.png", io.BytesIO(_PNG), "image/png")})
    client.post("/api/library", data={"name": "B", "subject": "Science"},
                files={"file": ("b.png", io.BytesIO(_PNG), "image/png")})

    resp = client.get("/api/library")
    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_list_filters_by_subject(test_db, tmp_path, monkeypatch):
    lib = tmp_path / "library"
    lib.mkdir()
    monkeypatch.setattr(library_module, "_LIBRARY_DIR", lib)

    client.post("/api/library", data={"name": "A", "subject": "Math"},
                files={"file": ("a.png", io.BytesIO(_PNG), "image/png")})
    client.post("/api/library", data={"name": "B", "subject": "Science"},
                files={"file": ("b.png", io.BytesIO(_PNG), "image/png")})

    resp = client.get("/api/library?subject=Math")
    assert len(resp.json()) == 1
    assert resp.json()[0]["name"] == "A"


def test_list_search_by_name(test_db, tmp_path, monkeypatch):
    lib = tmp_path / "library"
    lib.mkdir()
    monkeypatch.setattr(library_module, "_LIBRARY_DIR", lib)

    client.post("/api/library", data={"name": "Cell diagram"},
                files={"file": ("a.png", io.BytesIO(_PNG), "image/png")})
    client.post("/api/library", data={"name": "Map of Pakistan"},
                files={"file": ("b.png", io.BytesIO(_PNG), "image/png")})

    resp = client.get("/api/library?q=cell")
    assert len(resp.json()) == 1
    assert "Cell" in resp.json()[0]["name"]


# ---------------------------------------------------------------------------
# Delete
# ---------------------------------------------------------------------------

def test_delete_removes_db_row_and_file(test_db, tmp_path, monkeypatch):
    lib = tmp_path / "library"
    lib.mkdir()
    monkeypatch.setattr(library_module, "_LIBRARY_DIR", lib)

    up = client.post("/api/library", data={"name": "Del me"},
                     files={"file": ("d.png", io.BytesIO(_PNG), "image/png")})
    image_id = up.json()["id"]
    fname = up.json()["file_path"].split("/")[1]
    assert (lib / fname).exists()

    resp = client.delete(f"/api/library/{image_id}")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"

    assert not (lib / fname).exists()
    assert library_repository.find_by_id(image_id) is None


def test_delete_unknown_id_returns_404(test_db, tmp_path, monkeypatch):
    lib = tmp_path / "library"
    lib.mkdir()
    monkeypatch.setattr(library_module, "_LIBRARY_DIR", lib)

    resp = client.delete("/api/library/does-not-exist")
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# topics-with-images batch check
# ---------------------------------------------------------------------------

def test_topics_with_images_returns_matched_ids(test_db, tmp_path, monkeypatch):
    lib = tmp_path / "library"
    lib.mkdir()
    monkeypatch.setattr(library_module, "_LIBRARY_DIR", lib)

    client.post("/api/library",
                data={"name": "T1 img", "syllabus_topic_id": "topic-1"},
                files={"file": ("t1.png", io.BytesIO(_PNG), "image/png")})
    client.post("/api/library",
                data={"name": "T2 img", "syllabus_topic_id": "topic-2"},
                files={"file": ("t2.png", io.BytesIO(_PNG), "image/png")})

    resp = client.get("/api/library/topics-with-images?ids=topic-1,topic-3")
    assert resp.status_code == 200
    topics = resp.json()["topics"]
    assert "topic-1" in topics
    assert "topic-3" not in topics
    assert "topic-2" not in topics


def test_topics_with_images_returns_counts(test_db, tmp_path, monkeypatch):
    lib = tmp_path / "library"
    lib.mkdir()
    monkeypatch.setattr(library_module, "_LIBRARY_DIR", lib)

    # Upload 2 images for topic-1, 1 for topic-2
    for name in ("A", "B"):
        client.post("/api/library",
                    data={"name": name, "syllabus_topic_id": "topic-1"},
                    files={"file": (f"{name}.png", io.BytesIO(_PNG), "image/png")})
    client.post("/api/library",
                data={"name": "C", "syllabus_topic_id": "topic-2"},
                files={"file": ("c.png", io.BytesIO(_PNG), "image/png")})

    resp = client.get("/api/library/topics-with-images?ids=topic-1,topic-2,topic-99")
    assert resp.status_code == 200
    topics = resp.json()["topics"]
    assert topics["topic-1"] == 2
    assert topics["topic-2"] == 1
    assert "topic-99" not in topics


def test_topics_with_images_empty_ids_returns_empty(test_db, tmp_path, monkeypatch):
    lib = tmp_path / "library"
    lib.mkdir()
    monkeypatch.setattr(library_module, "_LIBRARY_DIR", lib)

    resp = client.get("/api/library/topics-with-images")
    assert resp.status_code == 200
    assert resp.json()["topics"] == {}


# ---------------------------------------------------------------------------
# Bulk upload — /api/library/bulk
# ---------------------------------------------------------------------------

def _bulk(tmp_path, monkeypatch, files, *, topic_id=None, subject=None, grade=None):
    lib = tmp_path / "library"
    lib.mkdir(exist_ok=True)
    monkeypatch.setattr(library_module, "_LIBRARY_DIR", lib)
    form = {}
    if topic_id:
        form["syllabus_topic_id"] = topic_id
    if subject:
        form["subject"] = subject
    if grade:
        form["grade"] = grade
    return client.post("/api/library/bulk", data=form, files=files), lib


def test_bulk_upload_all_added(test_db, tmp_path, monkeypatch):
    files = [
        ("files", ("alpha.png", io.BytesIO(_PNG), "image/png")),
        ("files", ("beta.png",  io.BytesIO(_PNG), "image/png")),
    ]
    resp, lib = _bulk(tmp_path, monkeypatch, files)
    assert resp.status_code == 200
    data = resp.json()
    assert data["added"] == 2
    assert data["skipped"] == 0
    assert len(list(lib.iterdir())) == 2


def test_bulk_upload_skips_duplicate_name(test_db, tmp_path, monkeypatch):
    # First batch: add alpha
    files1 = [("files", ("alpha.png", io.BytesIO(_PNG), "image/png"))]
    resp1, lib = _bulk(tmp_path, monkeypatch, files1)
    assert resp1.json()["added"] == 1

    # Second batch: alpha again + gamma (new)
    files2 = [
        ("files", ("alpha.png", io.BytesIO(_PNG), "image/png")),
        ("files", ("gamma.png", io.BytesIO(_PNG), "image/png")),
    ]
    resp2, _ = _bulk(tmp_path, monkeypatch, files2)
    data = resp2.json()
    assert data["added"] == 1
    assert data["skipped"] == 1
    skip = [r for r in data["results"] if r["status"] == "skip"]
    assert len(skip) == 1
    assert "alpha" in skip[0]["name"]


def test_bulk_upload_skips_wrong_mime(test_db, tmp_path, monkeypatch):
    files = [
        ("files", ("ok.png",  io.BytesIO(_PNG),           "image/png")),
        ("files", ("bad.gif", io.BytesIO(b"GIF89a"),      "image/gif")),
    ]
    resp, _ = _bulk(tmp_path, monkeypatch, files)
    data = resp.json()
    assert data["added"] == 1
    assert data["skipped"] == 1
    skip = [r for r in data["results"] if r["status"] == "skip"]
    assert "JPG/PNG" in skip[0]["reason"]


def test_bulk_upload_skips_oversized(test_db, tmp_path, monkeypatch):
    big = b"x" * (2 * 1024 * 1024 + 1)
    files = [
        ("files", ("big.png", io.BytesIO(big), "image/png")),
        ("files", ("ok.png",  io.BytesIO(_PNG), "image/png")),
    ]
    resp, _ = _bulk(tmp_path, monkeypatch, files)
    data = resp.json()
    assert data["added"] == 1
    assert data["skipped"] == 1


def test_bulk_upload_name_normalized_stored(test_db, tmp_path, monkeypatch):
    """Insert via bulk — name_normalized must equal lower(strip(stem))."""
    files = [("files", ("My Diagram.png", io.BytesIO(_PNG), "image/png"))]
    resp, _ = _bulk(tmp_path, monkeypatch, files)
    assert resp.json()["added"] == 1

    rows = library_repository.list_by_filters(q="My Diagram")
    assert len(rows) == 1
    assert rows[0]["name_normalized"] == "my diagram"


def test_bulk_upload_topic_tagged(test_db, tmp_path, monkeypatch):
    files = [("files", ("pic.png", io.BytesIO(_PNG), "image/png"))]
    resp, _ = _bulk(tmp_path, monkeypatch, files, topic_id="topic-xyz")
    assert resp.json()["added"] == 1

    rows = library_repository.list_by_filters()
    assert rows[0]["syllabus_topic_id"] == "topic-xyz"


def test_bulk_upload_per_file_result_list(test_db, tmp_path, monkeypatch):
    files = [
        ("files", ("first.png",  io.BytesIO(_PNG), "image/png")),
        ("files", ("second.png", io.BytesIO(_PNG), "image/png")),
    ]
    resp, _ = _bulk(tmp_path, monkeypatch, files)
    results = resp.json()["results"]
    assert len(results) == 2
    assert all(r["status"] == "ok" for r in results)


def test_bulk_upload_case_insensitive_duplicate(test_db, tmp_path, monkeypatch):
    """'Alpha' and 'alpha' refer to the same image — second must be skipped."""
    files1 = [("files", ("Alpha.png", io.BytesIO(_PNG), "image/png"))]
    _bulk(tmp_path, monkeypatch, files1)

    files2 = [("files", ("alpha.png", io.BytesIO(_PNG), "image/png"))]
    resp, _ = _bulk(tmp_path, monkeypatch, files2)
    data = resp.json()
    assert data["added"] == 0
    assert data["skipped"] == 1
