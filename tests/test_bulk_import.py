"""Tests for bulk import: POST /api/questions/bulk-import."""

from __future__ import annotations

import io

import openpyxl
import pytest
from fastapi.testclient import TestClient

from app.repositories import questions_repository  # noqa: E402

# ── helpers ───────────────────────────────────────────────────────────────────

HEADER = [
    "type", "question", "option_a", "option_b", "option_c", "option_d",
    "correct", "marks", "subject", "class", "topic", "is_urdu",
]


def _make_xlsx(rows: list[list]) -> bytes:
    """Build a minimal .xlsx in memory from header + data rows."""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(HEADER)
    for row in rows:
        ws.append(row)
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


def _make_csv(rows: list[list]) -> bytes:
    lines = [",".join(str(c) for c in HEADER)]
    for row in rows:
        lines.append(",".join(str(c) for c in row))
    return "\n".join(lines).encode()


def _mcq_row(
    question="What is H2O?",
    opt_a="Water", opt_b="Salt", opt_c="Sugar", opt_d="Oil",
    correct="a", marks=1, subject="Science", cls="5", topic="Water Cycle",
    is_urdu="no",
):
    return ["mcq", question, opt_a, opt_b, opt_c, opt_d, correct, marks,
            subject, cls, topic, is_urdu]


def _tf_row(question="The sky is blue.", correct="true", **kwargs):
    defaults = dict(marks=1, subject="Science", cls="5", topic="Atmosphere", is_urdu="no")
    defaults.update(kwargs)
    return ["tf", question, "", "", "", "", correct, defaults["marks"],
            defaults["subject"], defaults["cls"], defaults["topic"], defaults["is_urdu"]]


def _short_row(question="Explain gravity.", correct="Force of attraction", **kwargs):
    defaults = dict(marks=2, subject="Physics", cls="8", topic="Forces", is_urdu="no")
    defaults.update(kwargs)
    return ["short", question, "", "", "", "", correct, defaults["marks"],
            defaults["subject"], defaults["cls"], defaults["topic"], defaults["is_urdu"]]


def _fill_row(question="The capital of Pakistan is ___.", correct="Islamabad", **kwargs):
    defaults = dict(marks=1, subject="Pakistan Studies", cls="6", topic="Cities", is_urdu="no")
    defaults.update(kwargs)
    return ["fill", question, "", "", "", "", correct, defaults["marks"],
            defaults["subject"], defaults["cls"], defaults["topic"], defaults["is_urdu"]]


@pytest.fixture
def client(test_db):
    from app.main import app
    return TestClient(app)


def _upload_xlsx(client, rows):
    data = _make_xlsx(rows)
    return client.post(
        "/api/questions/bulk-import",
        files={"file": ("questions.xlsx", data,
                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
    )


def _upload_csv(client, rows):
    data = _make_csv(rows)
    return client.post(
        "/api/questions/bulk-import",
        files={"file": ("questions.csv", data, "text/csv")},
    )


# ── happy path ────────────────────────────────────────────────────────────────

class TestHappyPath:
    def test_single_mcq_xlsx(self, client):
        res = _upload_xlsx(client, [_mcq_row()])
        assert res.status_code == 200
        body = res.json()
        assert body["added"] == 1
        assert body["skipped"] == 0
        assert body["errors"] == []

    def test_single_mcq_csv(self, client):
        res = _upload_csv(client, [_mcq_row()])
        assert res.status_code == 200
        assert res.json()["added"] == 1

    def test_multiple_rows_all_valid(self, client):
        rows = [_mcq_row(), _tf_row(), _short_row(), _fill_row()]
        res = _upload_xlsx(client, rows)
        assert res.status_code == 200
        assert res.json()["added"] == 4
        assert res.json()["skipped"] == 0

    def test_questions_actually_in_db(self, client):
        before = questions_repository.count_all()
        _upload_xlsx(client, [_mcq_row(), _tf_row()])
        after = questions_repository.count_all()
        assert after - before == 2

    def test_mcq_correct_answer_resolved_to_text(self, client):
        """correct='b' should store option_b text, not the letter 'b'."""
        res = _upload_xlsx(client, [
            _mcq_row(opt_a="H2O", opt_b="NaCl", opt_c="CO2", opt_d="O2", correct="b"),
        ])
        assert res.status_code == 200
        qs = questions_repository.list_by_filters(subject="Science")
        latest = max(qs, key=lambda q: q["id"])
        assert latest["correct_answer_en"] == "NaCl"

    def test_marks_stored_correctly(self, client):
        _upload_xlsx(client, [_mcq_row(marks=3)])
        qs = questions_repository.list_by_filters(subject="Science")
        latest = max(qs, key=lambda q: q["id"])
        assert latest["marks"] == 3

    def test_source_is_manual(self, client):
        _upload_xlsx(client, [_mcq_row()])
        qs = questions_repository.list_by_filters(subject="Science")
        latest = max(qs, key=lambda q: q["id"])
        assert latest["source"] == "manual"

    def test_tf_row_imports(self, client):
        res = _upload_xlsx(client, [_tf_row()])
        assert res.json()["added"] == 1

    def test_short_row_imports(self, client):
        res = _upload_xlsx(client, [_short_row()])
        assert res.json()["added"] == 1

    def test_fill_row_imports(self, client):
        res = _upload_xlsx(client, [_fill_row()])
        assert res.json()["added"] == 1


# ── is_urdu ───────────────────────────────────────────────────────────────────

class TestIsUrdu:
    def test_is_urdu_yes_goes_to_question_ur(self, client):
        rows = [["mcq", "پانی کیا ہے؟", "پانی", "نمک", "چینی", "تیل",
                 "a", 1, "Science", "5", "Water", "yes"]]
        res = _upload_xlsx(client, rows)
        assert res.json()["added"] == 1
        qs = questions_repository.list_by_filters(subject="Science")
        latest = max(qs, key=lambda q: q["id"])
        assert latest["question_ur"] == "پانی کیا ہے؟"
        assert latest["question_en"] is None

    def test_is_urdu_no_goes_to_question_en(self, client):
        _upload_xlsx(client, [_mcq_row(is_urdu="no")])
        qs = questions_repository.list_by_filters(subject="Science")
        latest = max(qs, key=lambda q: q["id"])
        assert latest["question_en"] is not None
        assert latest["question_ur"] is None


# ── marks defaults ────────────────────────────────────────────────────────────

class TestMarksDefaults:
    def test_blank_marks_defaults_to_1(self, client):
        row = _mcq_row(marks="")
        res = _upload_xlsx(client, [row])
        assert res.json()["added"] == 1
        qs = questions_repository.list_by_filters(subject="Science")
        latest = max(qs, key=lambda q: q["id"])
        assert latest["marks"] == 1

    def test_zero_marks_becomes_1(self, client):
        row = _mcq_row(marks=0)
        res = _upload_xlsx(client, [row])
        assert res.json()["added"] == 1

    def test_invalid_marks_string_defaults_to_1(self, client):
        row = _mcq_row(marks="abc")
        res = _upload_xlsx(client, [row])
        assert res.json()["added"] == 1


# ── per-row validation errors ─────────────────────────────────────────────────

class TestValidationErrors:
    def test_blank_question_skipped(self, client):
        rows = [_mcq_row(question="")]
        res = _upload_xlsx(client, rows)
        assert res.json()["added"] == 0
        assert res.json()["skipped"] == 1
        assert "question" in res.json()["errors"][0].lower()

    def test_invalid_type_skipped(self, client):
        rows = [["essay", "Explain something", "", "", "", "", "", 2,
                 "English", "7", "Writing", "no"]]
        res = _upload_xlsx(client, rows)
        assert res.json()["skipped"] == 1
        assert "essay" in res.json()["errors"][0]

    def test_empty_type_skipped(self, client):
        rows = [["", "Some question", "", "", "", "", "", 1,
                 "Science", "5", "Topic", "no"]]
        res = _upload_xlsx(client, rows)
        assert res.json()["skipped"] == 1

    def test_mcq_missing_option_a_skipped(self, client):
        row = _mcq_row(opt_a="")
        res = _upload_xlsx(client, [row])
        assert res.json()["skipped"] == 1
        assert "option_a" in res.json()["errors"][0]

    def test_mcq_missing_multiple_options_skipped(self, client):
        row = _mcq_row(opt_c="", opt_d="")
        res = _upload_xlsx(client, [row])
        assert res.json()["skipped"] == 1

    def test_mcq_wrong_correct_letter_skipped(self, client):
        row = _mcq_row(correct="e")
        res = _upload_xlsx(client, [row])
        assert res.json()["skipped"] == 1
        assert "a/b/c/d" in res.json()["errors"][0]

    def test_tf_wrong_correct_skipped(self, client):
        row = _tf_row(correct="maybe")
        res = _upload_xlsx(client, [row])
        assert res.json()["skipped"] == 1
        assert "true/false" in res.json()["errors"][0]

    def test_row_number_in_error(self, client):
        """Error must mention which row failed (2 = first data row)."""
        res = _upload_xlsx(client, [_mcq_row(question="")])
        assert "row 2" in res.json()["errors"][0]

    def test_row_number_second_row(self, client):
        rows = [_mcq_row(), _mcq_row(question="")]
        res = _upload_xlsx(client, rows)
        assert res.json()["added"] == 1
        assert res.json()["skipped"] == 1
        assert "row 3" in res.json()["errors"][0]


# ── mixed valid + invalid ─────────────────────────────────────────────────────

class TestMixed:
    def test_one_bad_does_not_abort_rest(self, client):
        rows = [
            _mcq_row(),
            _mcq_row(question=""),    # bad
            _tf_row(),
        ]
        res = _upload_xlsx(client, rows)
        assert res.json()["added"] == 2
        assert res.json()["skipped"] == 1

    def test_all_bad_returns_zero_added(self, client):
        rows = [_mcq_row(question=""), _tf_row(correct="maybe")]
        res = _upload_xlsx(client, rows)
        assert res.json()["added"] == 0
        assert res.json()["skipped"] == 2


# ── topic matching ────────────────────────────────────────────────────────────

class TestTopicMatching:
    def test_unknown_topic_still_imports_with_warning(self, client):
        row = _mcq_row(topic="Completely Unknown Topic XYZ")
        res = _upload_xlsx(client, [row])
        body = res.json()
        assert body["added"] == 1
        assert body["skipped"] == 0
        assert any("nahi mila" in w for w in body["warnings"])

    def test_unknown_topic_topic_id_is_null_in_db(self, client):
        _upload_xlsx(client, [_mcq_row(topic="No Such Topic 99999")])
        qs = questions_repository.list_by_filters(subject="Science")
        latest = max(qs, key=lambda q: q["id"])
        assert latest["syllabus_topic_id"] is None

    def test_blank_topic_imports_without_warning(self, client):
        row = _mcq_row(topic="")
        res = _upload_xlsx(client, [row])
        assert res.json()["added"] == 1
        assert res.json()["warnings"] == []

    def test_warning_contains_topic_name(self, client):
        row = _mcq_row(topic="Mysterio Topic")
        res = _upload_xlsx(client, [row])
        assert any("Mysterio Topic" in w for w in res.json()["warnings"])


# ── file format errors ────────────────────────────────────────────────────────

class TestFileFormat:
    def test_unsupported_extension_rejected(self, client):
        res = client.post(
            "/api/questions/bulk-import",
            files={"file": ("questions.pdf", b"%PDF-1.4 fake", "application/pdf")},
        )
        assert res.status_code == 400

    def test_corrupt_xlsx_returns_error(self, client):
        res = client.post(
            "/api/questions/bulk-import",
            files={"file": ("questions.xlsx", b"this is not an xlsx file",
                            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
        )
        assert res.status_code == 200
        body = res.json()
        assert body["added"] == 0
        assert len(body["errors"]) > 0

    def test_missing_required_column(self, client):
        """A file without 'question' column should fail gracefully."""
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.append(["type", "option_a", "subject"])  # no 'question' column
        ws.append(["mcq", "Option A", "Science"])
        buf = io.BytesIO()
        wb.save(buf)
        res = client.post(
            "/api/questions/bulk-import",
            files={"file": ("bad.xlsx", buf.getvalue(),
                            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
        )
        assert res.status_code == 200
        body = res.json()
        assert body["added"] == 0
        assert any("missing" in e.lower() for e in body["errors"])

    def test_empty_file_xlsx(self, client):
        """Header row only, no data — 0 added, 0 skipped."""
        res = _upload_xlsx(client, [])
        body = res.json()
        assert body["added"] == 0
        assert body["skipped"] == 0

    def test_csv_valid_import(self, client):
        res = _upload_csv(client, [_mcq_row(), _tf_row()])
        assert res.json()["added"] == 2


# ── question type mapping ─────────────────────────────────────────────────────

class TestQuestionTypeMapping:
    def test_mcq_maps_to_multiple_choice(self, client):
        _upload_xlsx(client, [_mcq_row()])
        qs = questions_repository.list_by_filters(subject="Science")
        latest = max(qs, key=lambda q: q["id"])
        assert latest["question_type"] == "multiple-choice"

    def test_tf_maps_to_true_false(self, client):
        _upload_xlsx(client, [_tf_row()])
        qs = questions_repository.list_by_filters(subject="Science")
        latest = max(qs, key=lambda q: q["id"])
        assert latest["question_type"] == "true-false"

    def test_short_maps_to_short_answer(self, client):
        _upload_xlsx(client, [_short_row()])
        qs = questions_repository.list_by_filters(subject="Physics")
        latest = max(qs, key=lambda q: q["id"])
        assert latest["question_type"] == "short-answer"

    def test_fill_maps_to_fill_in_the_blank(self, client):
        _upload_xlsx(client, [_fill_row()])
        qs = questions_repository.list_by_filters(subject="Pakistan Studies")
        latest = max(qs, key=lambda q: q["id"])
        assert latest["question_type"] == "fill-in-the-blank"
