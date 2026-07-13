"""HISSA C tests — PATCH /api/library/bulk-meta (bulk smart tag update)."""

import io

from fastapi.testclient import TestClient

import app.api.library as library_module
from app.main import app

client = TestClient(app)

_PNG = (
    b"\x89PNG\r\n\x1a\n"
    b"\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
    b"\x08\x02\x00\x00\x00\x90wS\xde"
    b"\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\x18\xd8N"
    b"\x00\x00\x00\x00IEND\xaeB`\x82"
)


def _upload(tmp_path, monkeypatch, name):
    lib = tmp_path / "library"
    lib.mkdir(exist_ok=True)
    monkeypatch.setattr(library_module, "_LIBRARY_DIR", lib)
    resp = client.post(
        "/api/library",
        data={"name": name},
        files={"file": ("img.png", io.BytesIO(_PNG), "image/png")},
    )
    assert resp.status_code == 200
    return resp.json()["id"]


def _get(img_id):
    resp = client.get("/api/library")
    for img in resp.json():
        if img["id"] == img_id:
            return img
    return None


# ---------------------------------------------------------------------------
# 1. Bulk keywords replace
# ---------------------------------------------------------------------------

def test_bulk_keywords_replace(test_db, tmp_path, monkeypatch):
    id1 = _upload(tmp_path, monkeypatch, "ImgA")
    id2 = _upload(tmp_path, monkeypatch, "ImgB")
    # Pehle kuch keywords set karo
    client.patch(f"/api/library/{id1}", json={"keywords": "old1, old2"})
    client.patch(f"/api/library/{id2}", json={"keywords": "old3"})

    resp = client.patch("/api/library/bulk-meta", json={
        "image_ids": [id1, id2],
        "keywords": "new, fresh",
        "keywords_mode": "replace",
    })
    assert resp.status_code == 200
    assert resp.json()["updated"] == 2

    assert _get(id1)["keywords"] == "new, fresh"
    assert _get(id2)["keywords"] == "new, fresh"


# ---------------------------------------------------------------------------
# 2. Bulk keywords append
# ---------------------------------------------------------------------------

def test_bulk_keywords_append(test_db, tmp_path, monkeypatch):
    id1 = _upload(tmp_path, monkeypatch, "AppendA")
    id2 = _upload(tmp_path, monkeypatch, "AppendB")
    client.patch(f"/api/library/{id1}", json={"keywords": "apple, fruit"})
    client.patch(f"/api/library/{id2}", json={"keywords": "mango"})

    resp = client.patch("/api/library/bulk-meta", json={
        "image_ids": [id1, id2],
        "keywords": "red, tropical",
        "keywords_mode": "append",
    })
    assert resp.status_code == 200
    assert resp.json()["updated"] == 2

    kw1 = set(_get(id1)["keywords"].split(", "))
    kw2 = set(_get(id2)["keywords"].split(", "))
    assert {"apple", "fruit", "red", "tropical"} == kw1
    assert {"mango", "red", "tropical"} == kw2


# ---------------------------------------------------------------------------
# 3. Bulk category
# ---------------------------------------------------------------------------

def test_bulk_category(test_db, tmp_path, monkeypatch):
    id1 = _upload(tmp_path, monkeypatch, "CatA")
    id2 = _upload(tmp_path, monkeypatch, "CatB")

    resp = client.patch("/api/library/bulk-meta", json={
        "image_ids": [id1, id2],
        "category": "animal",
    })
    assert resp.status_code == 200
    assert _get(id1)["category"] == "animal"
    assert _get(id2)["category"] == "animal"


# ---------------------------------------------------------------------------
# 4. Bulk question_types
# ---------------------------------------------------------------------------

def test_bulk_question_types(test_db, tmp_path, monkeypatch):
    id1 = _upload(tmp_path, monkeypatch, "QtA")
    id2 = _upload(tmp_path, monkeypatch, "QtB")

    resp = client.patch("/api/library/bulk-meta", json={
        "image_ids": [id1, id2],
        "question_types": "count, colour",
    })
    assert resp.status_code == 200
    assert _get(id1)["question_types"] == "count, colour"
    assert _get(id2)["question_types"] == "count, colour"


# ---------------------------------------------------------------------------
# 5. Empty image_ids → 422
# ---------------------------------------------------------------------------

def test_empty_ids_returns_422(test_db):
    resp = client.patch("/api/library/bulk-meta", json={
        "image_ids": [],
        "keywords": "test",
    })
    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# 6. Partial fields — sirf category (keywords aur qt nahi)
# ---------------------------------------------------------------------------

def test_partial_fields_only_category(test_db, tmp_path, monkeypatch):
    img_id = _upload(tmp_path, monkeypatch, "PartialImg")
    client.patch(f"/api/library/{img_id}", json={"keywords": "existing", "question_types": "count"})

    resp = client.patch("/api/library/bulk-meta", json={
        "image_ids": [img_id],
        "category": "shape",
    })
    assert resp.status_code == 200

    img = _get(img_id)
    assert img["category"] == "shape"
    assert img["keywords"] == "existing"        # nahi badla
    assert img["question_types"] == "count"     # nahi badla


# ---------------------------------------------------------------------------
# 7. No meta field → 422
# ---------------------------------------------------------------------------

def test_no_meta_field_returns_422(test_db, tmp_path, monkeypatch):
    img_id = _upload(tmp_path, monkeypatch, "NoFieldImg")
    resp = client.patch("/api/library/bulk-meta", json={
        "image_ids": [img_id],
    })
    assert resp.status_code == 422
