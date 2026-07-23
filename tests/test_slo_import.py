"""SLO Marhala 0 — service-level tests: bloom auto-suggest + Excel add/update/errors."""

from __future__ import annotations

import io

import openpyxl

from app.core.bloom_standards import suggest_bloom_from_text
from app.repositories import slo_repository
from app.services import slo_import_service

HEADER = ["class", "subject", "slo_code", "slo_text", "bloom_level", "strand", "book_pages"]


def _make_xlsx(rows: list[list], header: list[str] = HEADER) -> bytes:
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(header)
    for row in rows:
        ws.append(row)
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


# ── bloom auto-suggest (verb -> level) ──────────────────────────────────────────

def test_bloom_suggest_remember_verbs():
    assert suggest_bloom_from_text("Students will be able to count objects 1 to 10.") == "remember"
    assert suggest_bloom_from_text("Students will be able to identify numbers.") == "remember"
    assert suggest_bloom_from_text("Students will be able to recognize flat shapes.") == "remember"


def test_bloom_suggest_understand_and_apply():
    assert suggest_bloom_from_text("Students will be able to describe a pattern.") == "understand"
    assert suggest_bloom_from_text("Students will be able to solve a simple sum.") == "apply"


def test_bloom_suggest_unknown_verb_returns_none():
    # "trace"/"hold" map mein nahi — khali chhoro, default "remember" MAT karo.
    assert suggest_bloom_from_text("Students will be able to trace vertical lines.") is None
    assert suggest_bloom_from_text("") is None


# ── add (new slo_code) ──────────────────────────────────────────────────────────

def test_import_adds_new_slo_with_autosuggested_bloom(test_db):
    xlsx = _make_xlsx([
        ["Pre Year 1", "Mathematics", "MATH-PY1-N-01",
         "Students will be able to count objects from 1 to 10.", "", "Number", "12-14"],
    ])
    result = slo_import_service.import_slos_from_excel(xlsx)
    assert result == {"added": 1, "updated": 0, "errors": 0, "results": result["results"]}

    row = slo_repository.find_by_code("MATH-PY1-N-01")
    assert row["class"] == "Pre Year 1"
    assert row["subject"] == "Mathematics"
    assert row["strand"] == "Number"
    assert row["bloom_level"] == "remember"  # verb "count" se auto-suggest


def test_teacher_bloom_value_not_overwritten(test_db):
    xlsx = _make_xlsx([
        ["Pre Year 1", "Mathematics", "MATH-PY1-N-02",
         "Students will be able to count to 20.", "analyze", "Number", ""],
    ])
    slo_import_service.import_slos_from_excel(xlsx)
    row = slo_repository.find_by_code("MATH-PY1-N-02")
    # "count" -> remember hota, lekin teacher ki "analyze" value rehni chahiye.
    assert row["bloom_level"] == "analyze"


def test_unknown_verb_leaves_bloom_empty(test_db):
    xlsx = _make_xlsx([
        ["Pre Year 1", "Mathematics", "MATH-PY1-W-01",
         "Students will be able to trace vertical lines.", "", "Pre-writing", ""],
    ])
    slo_import_service.import_slos_from_excel(xlsx)
    row = slo_repository.find_by_code("MATH-PY1-W-01")
    assert row["bloom_level"] is None


# ── update (duplicate slo_code) ─────────────────────────────────────────────────

def test_duplicate_slo_code_updates_not_duplicates(test_db):
    first = _make_xlsx([
        ["Pre Year 1", "Mathematics", "MATH-PY1-C-01",
         "Students will be able to compare two groups.", "", "Comparison", ""],
    ])
    slo_import_service.import_slos_from_excel(first)
    original = slo_repository.find_by_code("MATH-PY1-C-01")

    # Draft correction: wording + strand badle, same slo_code.
    second = _make_xlsx([
        ["Pre Year 1", "Mathematics", "MATH-PY1-C-01",
         "Students will be able to compare two groups as more or less.", "", "Comparison", ""],
    ])
    result = slo_import_service.import_slos_from_excel(second)
    assert result["added"] == 0
    assert result["updated"] == 1

    row = slo_repository.find_by_code("MATH-PY1-C-01")
    assert row["slo_text"] == "Students will be able to compare two groups as more or less."
    # created_at update mein badalna nahi chahiye.
    assert row["created_at"] == original["created_at"]
    # Sirf ek row honi chahiye (duplicate nahi bani).
    assert len(slo_repository.list_by_filters(class_name="Pre Year 1")) == 1


# ── errors: required fields ─────────────────────────────────────────────────────

def test_missing_required_field_counts_as_error(test_db):
    xlsx = _make_xlsx([
        ["Pre Year 1", "Mathematics", "MATH-PY1-N-03", "", "", "Number", ""],  # slo_text khali
        ["Pre Year 1", "Mathematics", "MATH-PY1-N-04",
         "Students will be able to write numbers 1 to 5.", "", "Number", ""],
    ])
    result = slo_import_service.import_slos_from_excel(xlsx)
    assert result["added"] == 1
    assert result["errors"] == 1
    err = next(r for r in result["results"] if r["status"] == "error")
    assert "slo_text" in err["reason"]


def test_missing_required_column_raises(test_db):
    # slo_text column hi nahi.
    xlsx = _make_xlsx(
        [["Pre Year 1", "Mathematics", "MATH-PY1-N-05", "Number"]],
        header=["class", "subject", "slo_code", "strand"],
    )
    try:
        slo_import_service.import_slos_from_excel(xlsx)
        raise AssertionError("ValueError expected")
    except ValueError as exc:
        assert "slo_text" in str(exc)


def test_extra_book_pages_column_ignored(test_db):
    # book_pages column maujood hai — koi error nahi, add ho jaye.
    xlsx = _make_xlsx([
        ["Pre Year 1", "Mathematics", "MATH-PY1-S-01",
         "Students will be able to recognize a circle.", "", "Flat Shape", "30-31"],
    ])
    result = slo_import_service.import_slos_from_excel(xlsx)
    assert result["added"] == 1
    assert result["errors"] == 0


# ── sequence (optional, INTEGER — asal kitab ki tarteeb) ─────────────────────────

SEQ_HEADER = ["class", "subject", "slo_code", "slo_text", "bloom_level", "strand", "sequence"]


def test_sequence_integer_stored(test_db):
    xlsx = _make_xlsx([
        ["Pre Year 1", "Mathematics", "MATH-PY1-N-10",
         "Students will be able to count to 10.", "", "Number", "5"],
    ], header=SEQ_HEADER)
    result = slo_import_service.import_slos_from_excel(xlsx)
    assert result["added"] == 1 and result["errors"] == 0
    assert slo_repository.find_by_code("MATH-PY1-N-10")["sequence"] == 5


def test_sequence_empty_is_null(test_db):
    xlsx = _make_xlsx([
        ["Pre Year 1", "Mathematics", "MATH-PY1-N-11",
         "Students will be able to count to 20.", "", "Number", ""],
    ], header=SEQ_HEADER)
    slo_import_service.import_slos_from_excel(xlsx)
    assert slo_repository.find_by_code("MATH-PY1-N-11")["sequence"] is None


def test_sequence_whole_float_coerced_to_int(test_db):
    # Excel numeric cell "3.0" ban jaata hai — poora number qubool, int mein.
    xlsx = _make_xlsx([
        ["Pre Year 1", "Mathematics", "MATH-PY1-N-12",
         "Students will be able to count backward.", "", "Number", "3.0"],
    ], header=SEQ_HEADER)
    slo_import_service.import_slos_from_excel(xlsx)
    assert slo_repository.find_by_code("MATH-PY1-N-12")["sequence"] == 3


def test_sequence_non_numeric_is_error(test_db):
    xlsx = _make_xlsx([
        ["Pre Year 1", "Mathematics", "MATH-PY1-N-13",
         "Students will be able to count on.", "", "Number", "abc"],
    ], header=SEQ_HEADER)
    result = slo_import_service.import_slos_from_excel(xlsx)
    assert result["added"] == 0 and result["errors"] == 1
    err = next(r for r in result["results"] if r["status"] == "error")
    assert "sequence" in err["reason"]
    # ghalat value chupke null nahi honi chahiye — row bilkul add na ho.
    assert slo_repository.find_by_code("MATH-PY1-N-13") is None


def test_sequence_refreshed_on_reimport(test_db):
    first = _make_xlsx([
        ["Pre Year 1", "Mathematics", "MATH-PY1-N-14",
         "Students will be able to order numbers.", "", "Number", "7"],
    ], header=SEQ_HEADER)
    slo_import_service.import_slos_from_excel(first)
    second = _make_xlsx([
        ["Pre Year 1", "Mathematics", "MATH-PY1-N-14",
         "Students will be able to order numbers.", "", "Number", "9"],
    ], header=SEQ_HEADER)
    result = slo_import_service.import_slos_from_excel(second)
    assert result["updated"] == 1
    assert slo_repository.find_by_code("MATH-PY1-N-14")["sequence"] == 9
