"""Bulk question upload — slo_code column (KAAM A Part 1) + duplicate-on-reupload."""

from __future__ import annotations

import io

import openpyxl

from app.repositories import question_slo_repository, questions_repository, slo_repository
from app.services import bulk_import_service

HEADER = ["type", "question", "subject", "class", "topic", "slo_code"]


def _xlsx(rows: list[list]) -> bytes:
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(HEADER)
    for r in rows:
        ws.append(r)
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


def _slo(slo_id: str, code: str) -> None:
    slo_repository.insert({
        "id": slo_id, "class": "Pre Year 1", "subject": "Mathematics",
        "slo_code": code, "slo_text": f"Outcome {code}",
        "bloom_level": None, "strand": "Number",
    })


def _only_question_id(subject="Mathematics") -> str:
    qs = questions_repository.list_by_filters(subject=subject)
    assert len(qs) == 1
    return qs[0]["id"]


def test_single_slo_code_links(test_db):
    _slo("s1", "MATH-01")
    res = bulk_import_service.import_from_bytes(
        _xlsx([["short", "Count to 10", "Mathematics", "Pre Year 1", "", "MATH-01"]]),
        "q.xlsx",
    )
    assert res["added"] == 1
    qid = _only_question_id()
    assert question_slo_repository.list_slo_ids_for_question(qid) == ["s1"]


def test_multiple_comma_separated(test_db):
    _slo("s1", "MATH-01")
    _slo("s2", "MATH-02")
    res = bulk_import_service.import_from_bytes(
        _xlsx([["short", "Q", "Mathematics", "Pre Year 1", "", "MATH-01, MATH-02"]]),
        "q.xlsx",
    )
    assert res["added"] == 1
    qid = _only_question_id()
    assert set(question_slo_repository.list_slo_ids_for_question(qid)) == {"s1", "s2"}


def test_unknown_code_warns_but_imports(test_db):
    _slo("s1", "MATH-01")
    res = bulk_import_service.import_from_bytes(
        _xlsx([["short", "Q", "Mathematics", "Pre Year 1", "", "MATH-01, GHOST-99"]]),
        "q.xlsx",
    )
    # question phir bhi imported, sirf ghost link nahi bana
    assert res["added"] == 1
    assert any("GHOST-99" in w for w in res["warnings"])
    qid = _only_question_id()
    assert question_slo_repository.list_slo_ids_for_question(qid) == ["s1"]


def test_empty_slo_code_no_link(test_db):
    res = bulk_import_service.import_from_bytes(
        _xlsx([["short", "Q", "Mathematics", "Pre Year 1", "", ""]]),
        "q.xlsx",
    )
    assert res["added"] == 1
    qid = _only_question_id()
    assert question_slo_repository.list_slo_ids_for_question(qid) == []


def test_case_insensitive_code(test_db):
    _slo("s1", "MATH-01")
    res = bulk_import_service.import_from_bytes(
        _xlsx([["short", "Q", "Mathematics", "Pre Year 1", "", " math-01 "]]),
        "q.xlsx",
    )
    assert res["added"] == 1
    qid = _only_question_id()
    assert question_slo_repository.list_slo_ids_for_question(qid) == ["s1"]


def test_reupload_duplicates_the_question(test_db):
    """DOCUMENTED trap: bulk import upsert nahi karta — har row naya uuid.
    Same file dobara upload = QUESTION duplicate (2 rows). SLO links har copy
    par sahi hain (replace-set), magar question khud do baar ban jata hai.
    Isi liye purane questions ke liye slo-export/assign-import (id se) use karo."""
    _slo("s1", "MATH-01")
    xlsx = _xlsx([["short", "Q dup test", "Mathematics", "Pre Year 1", "", "MATH-01"]])
    bulk_import_service.import_from_bytes(xlsx, "q.xlsx")
    bulk_import_service.import_from_bytes(xlsx, "q.xlsx")  # same file again
    qs = questions_repository.list_by_filters(subject="Mathematics")
    assert len(qs) == 2  # DUPLICATE — pre-existing behavior, KAAM A ne change nahi kiya
    # dono par link sahi (multiply nahi hua)
    for q in qs:
        assert question_slo_repository.list_slo_ids_for_question(q["id"]) == ["s1"]
