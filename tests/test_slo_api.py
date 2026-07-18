"""SLO Marhala 0 — API tests: POST /api/slo/import, GET /api/slo, GET …/template."""

from __future__ import annotations

import io

import openpyxl
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

HEADER = ["class", "subject", "slo_code", "slo_text", "bloom_level", "strand", "book_pages"]


def _make_xlsx(rows: list[list]) -> bytes:
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(HEADER)
    for row in rows:
        ws.append(row)
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


def _post_import(xlsx_bytes: bytes, filename: str = "slo.xlsx"):
    return client.post(
        "/api/slo/import",
        files={"file": (filename, io.BytesIO(xlsx_bytes),
                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
    )


# ── template download ───────────────────────────────────────────────────────────

def test_template_download_returns_xlsx(test_db):
    resp = client.get("/api/slo/template")
    assert resp.status_code == 200
    assert "spreadsheetml" in resp.headers["content-type"]
    assert resp.content[:4] == b"PK\x03\x04"  # xlsx ZIP magic bytes


# ── import happy path + summary shape ───────────────────────────────────────────

def test_import_returns_summary(test_db):
    xlsx = _make_xlsx([
        ["Pre Year 1", "Mathematics", "MATH-PY1-N-01",
         "Students will be able to count objects from 1 to 10.", "", "Number", "12"],
        ["Pre Year 1", "Mathematics", "MATH-PY1-S-01",
         "Students will be able to recognize a square.", "", "Flat Shape", "30"],
    ])
    resp = _post_import(xlsx)
    assert resp.status_code == 200
    data = resp.json()
    assert data["added"] == 2
    assert data["updated"] == 0
    assert data["errors"] == 0
    assert len(data["results"]) == 2


def test_reimport_updates(test_db):
    xlsx = _make_xlsx([
        ["Pre Year 1", "Mathematics", "MATH-PY1-N-01",
         "Students will be able to count to 10.", "", "Number", ""],
    ])
    _post_import(xlsx)
    resp = _post_import(xlsx)
    data = resp.json()
    assert data["added"] == 0
    assert data["updated"] == 1


# ── list endpoint ───────────────────────────────────────────────────────────────

def test_list_slos_with_filters(test_db):
    xlsx = _make_xlsx([
        ["Pre Year 1", "Mathematics", "MATH-PY1-N-01",
         "Students will be able to count to 10.", "", "Number", ""],
        ["Pre Year 1", "Mathematics", "MATH-PY1-S-01",
         "Students will be able to recognize a circle.", "", "Flat Shape", ""],
    ])
    _post_import(xlsx)

    resp = client.get("/api/slo", params={"class_name": "Pre Year 1", "subject": "Mathematics"})
    assert resp.status_code == 200
    assert resp.json()["total"] == 2

    resp = client.get("/api/slo", params={"strand": "Number"})
    assert resp.json()["total"] == 1
    assert resp.json()["slos"][0]["slo_code"] == "MATH-PY1-N-01"


# ── validation ──────────────────────────────────────────────────────────────────

def test_wrong_extension_rejected(test_db):
    resp = client.post(
        "/api/slo/import",
        files={"file": ("data.docx", io.BytesIO(b"dummy"), "application/octet-stream")},
    )
    assert resp.status_code == 400


def test_missing_column_returns_400(test_db):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(["class", "subject", "slo_code"])  # slo_text missing
    ws.append(["Pre Year 1", "Mathematics", "MATH-PY1-N-09"])
    buf = io.BytesIO()
    wb.save(buf)

    resp = _post_import(buf.getvalue())
    assert resp.status_code == 400
    assert "slo_text" in resp.json()["detail"]
