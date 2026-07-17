"""HISSA 2 tests — POST /api/library/excel-meta-import + GET …/template."""

from __future__ import annotations

import io

import openpyxl
from fastapi.testclient import TestClient

import app.api.library as library_module
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

HEADER = ["image_name", "topic", "subject", "class", "keywords", "category", "question_types"]


def _make_xlsx(rows: list[list]) -> bytes:
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(HEADER)
    for row in rows:
        ws.append(row)
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


def _upload_image(tmp_path, monkeypatch, name: str) -> str:
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


def _post_excel(xlsx_bytes: bytes, filename: str = "meta.xlsx"):
    return client.post(
        "/api/library/excel-meta-import",
        files={"file": (filename, io.BytesIO(xlsx_bytes),
                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
    )


# ── Template download ─────────────────────────────────────────────────────────

def test_template_download_returns_xlsx(test_db):
    resp = client.get("/api/library/excel-meta-import/template")
    assert resp.status_code == 200
    assert "spreadsheetml" in resp.headers["content-type"]
    assert resp.content[:4] == b"PK\x03\x04"  # xlsx ZIP magic bytes


# ── Happy path ────────────────────────────────────────────────────────────────

def test_post_updates_image(test_db, tmp_path, monkeypatch):
    img_id = _upload_image(tmp_path, monkeypatch, "mango_c")
    xlsx = _make_xlsx([["mango_c", None, None, None, "yellow, sweet", "fruit", "Count"]])

    resp = _post_excel(xlsx)
    assert resp.status_code == 200
    data = resp.json()
    assert data["updated"] == 1
    assert data["skipped"] == 0

    img = library_repository.find_by_id(img_id)
    assert img["keywords"] == "yellow, sweet"
    assert img["category"] == "fruit"
    assert img["question_types"] == "Count"


# ── Validation errors ─────────────────────────────────────────────────────────

def test_wrong_extension_rejected(test_db):
    resp = client.post(
        "/api/library/excel-meta-import",
        files={"file": ("data.docx", io.BytesIO(b"dummy"), "application/octet-stream")},
    )
    assert resp.status_code == 400
    assert "xlsx" in resp.json()["detail"].lower() or "xls" in resp.json()["detail"].lower()


def test_missing_image_name_column_returns_400(test_db):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(["wrong_col", "keywords"])
    ws.append(["abc", "kw"])
    buf = io.BytesIO()
    wb.save(buf)

    resp = _post_excel(buf.getvalue())
    assert resp.status_code == 400
    assert "image_name" in resp.json()["detail"]


def test_corrupt_file_returns_400(test_db):
    resp = _post_excel(b"not an excel file")
    assert resp.status_code == 400


# ── Skip behaviour ────────────────────────────────────────────────────────────

def test_image_not_found_skipped_in_summary(test_db, tmp_path, monkeypatch):
    _upload_image(tmp_path, monkeypatch, "real_img")
    xlsx = _make_xlsx([
        ["real_img", None, None, None, "kw", None, None],
        ["ghost_img", None, None, None, "kw", None, None],
    ])
    resp = _post_excel(xlsx)
    assert resp.status_code == 200
    data = resp.json()
    assert data["updated"] == 1
    assert data["skipped"] == 1
    skip_entry = next(r for r in data["results"] if r["status"] == "skip")
    assert skip_entry["image_name"] == "ghost_img"
