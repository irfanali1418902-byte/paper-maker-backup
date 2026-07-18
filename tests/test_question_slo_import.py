"""Excel bulk-assign for existing questions (KAAM A Part 2) — export + import."""

from __future__ import annotations

import io

import openpyxl

from app.repositories import question_slo_repository, questions_repository, slo_repository
from app.services import question_slo_import_service


def _q(qid: str, text="Count to 10") -> None:
    questions_repository.insert({
        "id": qid, "subject": "Mathematics", "topic": "Counting",
        "bloom_level": "REMEMBER", "difficulty": "easy",
        "question_type": "short-answer", "marks": 1,
        "question_en": text, "question_ur": None,
        "options_en": "[]", "options_ur": "[]",
        "correct_answer_en": None, "correct_answer_ur": None,
        "explanation_en": None, "explanation_ur": None,
        "visual_emoji": None, "visual_count": None,
    })


def _slo(slo_id: str, code: str) -> None:
    slo_repository.insert({
        "id": slo_id, "class": "Pre Year 1", "subject": "Mathematics",
        "slo_code": code, "slo_text": f"Outcome {code}",
        "bloom_level": None, "strand": "Number",
    })


def _assign_xlsx(rows: list[list], header=None) -> bytes:
    """rows: [[question_id, slo_code], ...]. Default header = machine header."""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(header or ["question_id", "subject", "topic", "question", "slo_code"])
    for r in rows:
        ws.append(r)
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


# ── resolver ──────────────────────────────────────────────────────────────────

def test_resolve_slo_codes(test_db):
    _slo("s1", "MATH-01")
    _slo("s2", "MATH-02")
    ids, unknown = question_slo_import_service.resolve_slo_codes("MATH-01, ghost, math-02")
    assert set(ids) == {"s1", "s2"}
    assert unknown == ["ghost"]


def test_resolve_dedupes(test_db):
    _slo("s1", "MATH-01")
    ids, unknown = question_slo_import_service.resolve_slo_codes("MATH-01, MATH-01")
    assert ids == ["s1"]
    assert unknown == []


# ── export ────────────────────────────────────────────────────────────────────

def test_export_includes_id_and_current_codes(test_db):
    _q("q1")
    _slo("s1", "MATH-01")
    question_slo_repository.replace_for_question("q1", ["s1"])
    xlsx = question_slo_import_service.build_export_xlsx()
    wb = openpyxl.load_workbook(io.BytesIO(xlsx))
    ws = wb.active
    rows = list(ws.iter_rows(values_only=True))
    # row 1 = machine header, row 2+ = data
    assert rows[0] == ("question_id", "subject", "topic", "question", "slo_code")
    data = [r for r in rows[1:] if r[0] == "q1"]
    assert len(data) == 1
    assert data[0][4] == "MATH-01"  # current slo_code


# ── assign import ─────────────────────────────────────────────────────────────

def test_assign_links_by_id(test_db):
    _q("q1")
    _slo("s1", "MATH-01")
    res = question_slo_import_service.import_assignments(
        _assign_xlsx([["q1", "", "", "", "MATH-01"]]), "a.xlsx")
    assert res["updated"] == 1
    assert res["errors"] == []
    assert question_slo_repository.list_slo_ids_for_question("q1") == ["s1"]


def test_assign_replace_set_edit(test_db):
    _q("q1")
    _slo("s1", "MATH-01")
    _slo("s2", "MATH-02")
    question_slo_repository.replace_for_question("q1", ["s1"])
    # re-upload with MATH-02 only → replace (s1 hat jaye)
    question_slo_import_service.import_assignments(
        _assign_xlsx([["q1", "", "", "", "MATH-02"]]), "a.xlsx")
    assert question_slo_repository.list_slo_ids_for_question("q1") == ["s2"]


def test_assign_empty_code_clears(test_db):
    _q("q1")
    _slo("s1", "MATH-01")
    question_slo_repository.replace_for_question("q1", ["s1"])
    question_slo_import_service.import_assignments(
        _assign_xlsx([["q1", "", "", "", ""]]), "a.xlsx")
    assert question_slo_repository.list_slo_ids_for_question("q1") == []


def test_assign_unknown_question_id_errors(test_db):
    _slo("s1", "MATH-01")
    res = question_slo_import_service.import_assignments(
        _assign_xlsx([["ghost-id", "", "", "", "MATH-01"]]), "a.xlsx")
    assert res["updated"] == 0
    assert any("ghost-id" in e for e in res["errors"])


def test_assign_empty_question_id_skipped_quietly(test_db):
    """Khali line (question_id blank) chup-chaap skip — error nahi."""
    _q("q1")
    _slo("s1", "MATH-01")
    res = question_slo_import_service.import_assignments(
        _assign_xlsx([["", "", "", "", "MATH-01"], ["q1", "", "", "", "MATH-01"]]), "a.xlsx")
    assert res["updated"] == 1
    assert res["errors"] == []


def test_assign_unknown_code_warns(test_db):
    _q("q1")
    res = question_slo_import_service.import_assignments(
        _assign_xlsx([["q1", "", "", "", "GHOST-99"]]), "a.xlsx")
    assert res["updated"] == 1
    assert any("GHOST-99" in w for w in res["warnings"])
    assert question_slo_repository.list_slo_ids_for_question("q1") == []


def test_assign_missing_column_errors(test_db):
    _q("q1")
    # header without slo_code
    res = question_slo_import_service.import_assignments(
        _assign_xlsx([["q1"]], header=["question_id"]), "a.xlsx")
    assert res["updated"] == 0
    assert any("slo_code" in e for e in res["errors"])


def test_export_then_assign_roundtrip_by_id(test_db):
    """Real workflow: export → slo_code bhar ke wapas import (id se match)."""
    _q("q1", text="Q one")
    _q("q2", text="Q two")
    _slo("s1", "MATH-01")
    xlsx = question_slo_import_service.build_export_xlsx()
    wb = openpyxl.load_workbook(io.BytesIO(xlsx))
    ws = wb.active
    # slo_code column (5th) bharo q1 ke liye (data row 2 se — single header)
    for row in ws.iter_rows(min_row=2):
        if row[0].value == "q1":
            row[4].value = "MATH-01"
    buf = io.BytesIO()
    wb.save(buf)
    res = question_slo_import_service.import_assignments(buf.getvalue(), "a.xlsx")
    assert res["errors"] == []
    assert question_slo_repository.list_slo_ids_for_question("q1") == ["s1"]
    assert question_slo_repository.list_slo_ids_for_question("q2") == []
