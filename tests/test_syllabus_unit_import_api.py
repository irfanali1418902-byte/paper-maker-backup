"""HISSA 4 tests — POST /api/syllabus/excel-unit-import + GET .../template."""

from __future__ import annotations

import io
import uuid

import openpyxl
from fastapi.testclient import TestClient

from app.core.database import get_connection
from app.main import app
from app.repositories import syllabus_repository

client = TestClient(app)

HEADER = ["topic", "subject", "class", "unit"]


def _make_xlsx(rows: list[list]) -> bytes:
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(HEADER)
    for row in rows:
        ws.append(row)
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


def _insert_topic(subtopic: str, subject: str = "Math", grade: str = "Grade 4") -> str:
    tid = str(uuid.uuid4())
    conn = get_connection()
    conn.execute(
        """INSERT INTO syllabus_topics
           (id, subject, grade, unit_no, unit_title, page_range,
            subtopic_title, activity_type, page_no, learning_outcome)
           VALUES (?,?,?,?,?,?,?,?,?,?)""",
        (tid, subject, grade, 1, "Old", "1-5", subtopic, "classwork", 1, ""),
    )
    conn.commit()
    conn.close()
    return tid


def _post_excel(xlsx_bytes: bytes, filename: str = "units.xlsx"):
    return client.post(
        "/api/syllabus/excel-unit-import",
        files={"file": (filename, io.BytesIO(xlsx_bytes),
                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
    )


# ── Template download ─────────────────────────────────────────────────────────

def test_template_download_returns_xlsx(test_db):
    resp = client.get("/api/syllabus/excel-unit-import/template")
    assert resp.status_code == 200
    assert "spreadsheetml" in resp.headers["content-type"]
    assert resp.content[:4] == b"PK\x03\x04"


# ── Happy path ────────────────────────────────────────────────────────────────

def test_post_updates_topic_unit(test_db):
    tid = _insert_topic("Fractions")
    xlsx = _make_xlsx([["Fractions", "Math", "Grade 4", "Unit 3: Fractions"]])

    resp = _post_excel(xlsx)
    assert resp.status_code == 200
    data = resp.json()
    assert data["updated"] == 1
    assert data["skipped"] == 0

    row = syllabus_repository.find_by_id(tid)
    assert row["unit"] == "Unit 3: Fractions"


# ── Validation errors ─────────────────────────────────────────────────────────

def test_wrong_extension_rejected(test_db):
    resp = client.post(
        "/api/syllabus/excel-unit-import",
        files={"file": ("data.docx", io.BytesIO(b"dummy"), "application/octet-stream")},
    )
    assert resp.status_code == 400


def test_missing_topic_column_returns_400(test_db):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(["subject", "unit"])
    ws.append(["Math", "Unit 1"])
    buf = io.BytesIO()
    wb.save(buf)

    resp = _post_excel(buf.getvalue())
    assert resp.status_code == 400
    assert "topic" in resp.json()["detail"]


# ── Skip behaviour ────────────────────────────────────────────────────────────

def test_topic_not_found_skipped(test_db):
    _insert_topic("Addition")
    xlsx = _make_xlsx([
        ["Addition",    "Math", "Grade 4", "Unit 1"],
        ["GhostTopic",  "Math", "Grade 4", "Unit 1"],
    ])
    resp = _post_excel(xlsx)
    assert resp.status_code == 200
    data = resp.json()
    assert data["updated"] == 1
    assert data["skipped"] == 1
