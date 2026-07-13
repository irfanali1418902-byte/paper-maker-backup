"""Smart Question Bank HISSA B — bulk import with new optional columns.

Tests:
1. New columns imported correctly (keywords, status, bloom_level, etc.)
2. Old Excel (no new columns) → zero warnings, backward compat
3. Invalid status → default 'published' + warning, row still imported
4. Invalid estimated_time → None + warning, row still imported
5. Keywords imported correctly
6. Old CSV (no new columns) → zero warnings
"""

from __future__ import annotations

import io

import openpyxl
import pytest
from fastapi.testclient import TestClient

# ── helpers ───────────────────────────────────────────────────────────────────

OLD_HEADER = [
    "type", "question", "option_a", "option_b", "option_c", "option_d",
    "correct", "marks", "subject", "class", "topic", "is_urdu",
]

NEW_HEADER = OLD_HEADER + [
    "bloom_level", "difficulty", "keywords", "learning_outcome",
    "estimated_time", "source_book", "page_number", "status",
]


def _xlsx(header: list, rows: list[list]) -> bytes:
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(header)
    for row in rows:
        ws.append(row)
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


def _csv(header: list, rows: list[list]) -> bytes:
    lines = [",".join(str(c) for c in header)]
    for row in rows:
        lines.append(",".join(str(c) for c in row))
    return "\n".join(lines).encode()


def _short_old(question="Explain gravity."):
    """Minimal short-answer row with OLD header (no new columns)."""
    return ["short", question, "", "", "", "", "", 2, "Physics", "8", "", "no"]


def _short_new(question="Explain gravity.", **extras):
    """Short-answer row with NEW header. extras override defaults."""
    defaults = {
        "bloom_level": "APPLY",
        "difficulty": "medium",
        "keywords": "gravity, force",
        "learning_outcome": "Describe gravity",
        "estimated_time": 5,
        "source_book": "NCERT Physics 8",
        "page_number": 30,
        "status": "published",
    }
    defaults.update(extras)
    base = ["short", question, "", "", "", "", "", 2, "Physics", "8", "", "no"]
    return base + [
        defaults["bloom_level"], defaults["difficulty"], defaults["keywords"],
        defaults["learning_outcome"], defaults["estimated_time"],
        defaults["source_book"], defaults["page_number"], defaults["status"],
    ]


@pytest.fixture
def client(test_db):
    from app.main import app
    return TestClient(app)


def _upload_xlsx(client, header, rows):
    data = _xlsx(header, rows)
    return client.post(
        "/api/questions/bulk-import",
        files={"file": ("questions.xlsx", data,
                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
    )


def _upload_csv(client, header, rows):
    data = _csv(header, rows)
    return client.post(
        "/api/questions/bulk-import",
        files={"file": ("questions.csv", data, "text/csv")},
    )


# ── tests ─────────────────────────────────────────────────────────────────────

def test_new_columns_imported_correctly(client, test_db):
    """All 8 new optional columns should be saved to the DB."""
    from app.repositories import questions_repository

    resp = _upload_xlsx(client, NEW_HEADER, [_short_new()])
    assert resp.status_code == 200
    body = resp.json()
    assert body["added"] == 1
    assert body["skipped"] == 0

    rows = questions_repository.list_by_filters()
    assert len(rows) == 1
    q = rows[0]
    assert q["bloom_level"] == "APPLY"
    assert q["difficulty"] == "medium"
    assert q["keywords"] == "gravity, force"
    assert q["learning_outcome"] == "Describe gravity"
    assert q["estimated_time"] == 5
    assert q["source_book"] == "NCERT Physics 8"
    assert q["page_number"] == 30
    assert q["status"] == "published"


def test_old_excel_backward_compat_no_warnings(client, test_db):
    """Old Excel file with no new columns must import cleanly — zero warnings."""
    resp = _upload_xlsx(client, OLD_HEADER, [_short_old()])
    assert resp.status_code == 200
    body = resp.json()
    assert body["added"] == 1
    assert body["skipped"] == 0
    assert body["warnings"] == []


def test_invalid_status_defaults_to_published_with_warning(client, test_db):
    """Row with bad status value must still import; status defaults to 'published'."""
    from app.repositories import questions_repository

    resp = _upload_xlsx(client, NEW_HEADER, [_short_new(status="xyz")])
    assert resp.status_code == 200
    body = resp.json()
    assert body["added"] == 1
    assert body["skipped"] == 0
    assert any("status" in w and "xyz" in w for w in body["warnings"])

    q = questions_repository.list_by_filters()[0]
    assert q["status"] == "published"


def test_invalid_estimated_time_is_none_with_warning(client, test_db):
    """Row with non-numeric estimated_time imports; estimated_time saved as None."""
    from app.repositories import questions_repository

    resp = _upload_xlsx(client, NEW_HEADER, [_short_new(estimated_time="abc")])
    assert resp.status_code == 200
    body = resp.json()
    assert body["added"] == 1
    assert body["skipped"] == 0
    assert any("estimated_time" in w for w in body["warnings"])

    q = questions_repository.list_by_filters()[0]
    assert q["estimated_time"] is None


def test_keywords_imported(client, test_db):
    """Keywords field saved exactly as provided."""
    from app.repositories import questions_repository

    resp = _upload_xlsx(client, NEW_HEADER, [_short_new(keywords="newton, laws, motion")])
    assert resp.status_code == 200
    q = questions_repository.list_by_filters()[0]
    assert q["keywords"] == "newton, laws, motion"


def test_old_csv_backward_compat_no_warnings(client, test_db):
    """Old CSV without new columns imports cleanly — zero warnings, no skips."""
    resp = _upload_csv(client, OLD_HEADER, [_short_old("Define inertia.")])
    assert resp.status_code == 200
    body = resp.json()
    assert body["added"] == 1
    assert body["skipped"] == 0
    assert body["warnings"] == []
