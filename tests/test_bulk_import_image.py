"""HISSA B tests — image column in Excel bulk import.

Strategy:
- Seed a real library image row (via library_repository.insert) so the
  service can find it by name.
- Monkeypatch bulk_import_service._LIBRARY_DIR and _UPLOADS_DIR to tmp_path
  so no real files are touched.
- Rows use a 13-column header that includes 'image'.
- Topic "Tides" is seeded in syllabus_topics so topic-match warnings don't
  pollute assertions that check warnings == [].
"""

from __future__ import annotations

import io
import uuid
from pathlib import Path

import openpyxl
import pytest
from fastapi.testclient import TestClient

import app.services.bulk_import_service as svc
from app.core.database import get_connection
from app.main import app
from app.repositories import library_repository, questions_repository

# ---------------------------------------------------------------------------
# Minimal valid PNG bytes (1×1 pixel)
# ---------------------------------------------------------------------------
_PNG = (
    b"\x89PNG\r\n\x1a\n"
    b"\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
    b"\x08\x02\x00\x00\x00\x90wS\xde"
    b"\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\x18\xd8N"
    b"\x00\x00\x00\x00IEND\xaeB`\x82"
)

HEADER = [
    "type", "question", "option_a", "option_b", "option_c", "option_d",
    "correct", "marks", "subject", "class", "topic", "is_urdu", "image",
]

_TOPIC_ID = "topic-tides-001"
_TOPIC_NAME = "Tides"


def _make_xlsx(rows: list[list]) -> bytes:
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(HEADER)
    for row in rows:
        ws.append(row)
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


def _short_row(image_name: str = "", topic: str = _TOPIC_NAME) -> list:
    return ["short", "Explain photosynthesis.", "", "", "", "", "Process by plants",
            1, "Biology", "7", topic, "no", image_name]


def _seed_topic():
    conn = get_connection()
    conn.execute(
        "INSERT OR IGNORE INTO syllabus_topics "
        "(id, subject, grade, unit_no, unit_title, subtopic_title, activity_type) "
        "VALUES (?,?,?,?,?,?,?)",
        (_TOPIC_ID, "Biology", "7", 1, "Oceans", _TOPIC_NAME, "activity"),
    )
    conn.commit()
    conn.close()


def _seed_library_image(tmp_lib: Path, *, name: str, topic_id: str = "") -> dict:
    """Insert a library row + write a real PNG file into tmp_lib."""
    img_id = str(uuid.uuid4())
    fname = f"{img_id}.png"
    (tmp_lib / fname).write_bytes(_PNG)
    row = {
        "id": img_id,
        "file_path": f"library/{fname}",
        "name": name,
        "subject": None,
        "grade": None,
        "syllabus_topic_id": topic_id or None,
        "uploaded_by": None,
    }
    library_repository.insert(row)
    return row


@pytest.fixture
def client(test_db):
    _seed_topic()
    return TestClient(app)


@pytest.fixture
def dirs(tmp_path, monkeypatch):
    lib = tmp_path / "library"
    lib.mkdir()
    ups = tmp_path / "uploads"
    ups.mkdir()
    monkeypatch.setattr(svc, "_LIBRARY_DIR", lib)
    monkeypatch.setattr(svc, "_UPLOADS_DIR", ups)
    return lib, ups


def _do_import(client, rows):
    return client.post(
        "/api/questions/bulk-import",
        files={"file": ("q.xlsx", _make_xlsx(rows),
                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_image_name_match_sets_image_path(test_db, client, dirs):
    lib, ups = dirs
    _seed_library_image(lib, name="oranges5")

    res = _do_import(client, [_short_row("oranges5")])
    assert res.status_code == 200
    data = res.json()
    assert data["added"] == 1
    assert data["warnings"] == []

    q = questions_repository.list_by_filters()[0]
    assert q["image_path"] is not None
    assert q["image_path"].startswith("uploads/")
    assert q["image_path"].endswith(".png")


def test_image_name_match_copies_file_to_uploads(test_db, client, dirs):
    lib, ups = dirs
    _seed_library_image(lib, name="diagram1")

    _do_import(client, [_short_row("diagram1")])

    q = questions_repository.list_by_filters()[0]
    dest = ups / Path(q["image_path"]).name
    assert dest.exists()
    assert dest.read_bytes() == _PNG


def test_blank_image_column_no_image_no_warning(test_db, client, dirs):
    res = _do_import(client, [_short_row("")])
    data = res.json()
    assert data["added"] == 1
    assert not any("image" in w.lower() for w in data["warnings"])
    q = questions_repository.list_by_filters()[0]
    assert q["image_path"] is None


def test_wrong_image_name_warning_not_skip(test_db, client, dirs):
    """Unknown image name → question imported (not skipped) + 1 warning."""
    res = _do_import(client, [_short_row("does_not_exist")])
    data = res.json()
    assert data["added"] == 1
    assert data["skipped"] == 0
    assert len(data["warnings"]) == 1
    assert "does_not_exist" in data["warnings"][0]
    assert "nahi mili" in data["warnings"][0]


def test_image_case_insensitive_match(test_db, client, dirs):
    lib, ups = dirs
    _seed_library_image(lib, name="OrangeS5")

    res = _do_import(client, [_short_row("oranges5")])
    data = res.json()
    assert data["added"] == 1
    assert data["warnings"] == []

    q = questions_repository.list_by_filters()[0]
    assert q["image_path"] is not None


def test_image_column_absent_backward_compat(test_db, client, dirs):
    """Excel without 'image' column → imports fine, no image, no warnings."""
    old_header = [
        "type", "question", "option_a", "option_b", "option_c", "option_d",
        "correct", "marks", "subject", "class", "topic", "is_urdu",
    ]
    row = ["short", "What is a tide?", "", "", "", "", "Rise and fall", 1,
           "Biology", "7", _TOPIC_NAME, "no"]
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(old_header)
    ws.append(row)
    buf = io.BytesIO()
    wb.save(buf)

    res = client.post(
        "/api/questions/bulk-import",
        files={"file": ("old.xlsx", buf.getvalue(),
                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
    )
    data = res.json()
    assert data["added"] == 1
    assert data["warnings"] == []
    q = questions_repository.list_by_filters()[0]
    assert q["image_path"] is None


def test_topic_scoped_image_match_preferred(test_db, client, dirs):
    """Two library images with same name but different topics — topic-matched one used."""
    lib, ups = dirs
    _seed_library_image(lib, name="graph1", topic_id="")          # global
    _seed_library_image(lib, name="graph1", topic_id=_TOPIC_ID)   # topic-scoped

    res = _do_import(client, [_short_row("graph1", topic=_TOPIC_NAME)])
    data = res.json()
    assert data["added"] == 1
    assert data["warnings"] == []

    q = questions_repository.list_by_filters()[0]
    assert q["image_path"] is not None
    assert q["syllabus_topic_id"] == _TOPIC_ID
