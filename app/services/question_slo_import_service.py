"""Excel-based SLO tagging — KAAM A.

Do cheezein:
  * resolve_slo_codes()  — shared: "MATH-01, MATH-02" -> ([slo_id,...], [unknown_code,...])
  * build_export_xlsx()  — sab questions ka sheet (question_id + current slo_code)
  * import_assignments() — filled sheet parh kar (question_id -> SLO links) replace-set

Purane 200+ questions ke liye: pehle export download, slo_code column bharo/edit,
wapas upload. question_id se match (text se nahi) — export column edit/delete par
import saaf error deta hai (koi silent corruption nahi).
"""

from __future__ import annotations

import io
import re

import openpyxl
import pandas as pd
from openpyxl.comments import Comment

from app.repositories import question_slo_repository, questions_repository, slo_repository

EXPORT_HEADER = ["question_id", "subject", "topic", "question", "slo_code"]
_PREVIEW_LEN = 80


def resolve_slo_codes(codes_str: str) -> tuple[list, list]:
    """Comma-separated slo_code string -> (valid slo_ids [de-duped, order-preserved],
    unknown codes). Case/whitespace-insensitive. Khali -> ([], [])."""
    slo_ids: list = []
    unknown: list = []
    for raw in (codes_str or "").split(","):
        code = raw.strip()
        if not code:
            continue
        slo = slo_repository.find_by_code_normalized(code)
        if slo:
            slo_ids.append(slo["id"])
        else:
            unknown.append(code)
    return list(dict.fromkeys(slo_ids)), unknown


# ── export ────────────────────────────────────────────────────────────────────

def export_filename(grade: str | None = None, subject: str | None = None) -> str:
    """Export ke liye dynamic filename. Filter tokens ko `_` se join, unsafe chars
    ko `_` — misal grade='Pre Year 1', subject='Mathematics' ->
    'slo_assign_export_Pre_Year_1_Mathematics.xlsx'. Koi filter na ho to purana
    'slo_assign_export.xlsx'."""
    parts = [p.strip() for p in (grade, subject) if p and p.strip()]
    if not parts:
        return "slo_assign_export.xlsx"
    slug = "_".join(re.sub(r"[^A-Za-z0-9]+", "_", p).strip("_") for p in parts)
    return f"slo_assign_export_{slug}.xlsx"


def build_export_xlsx(grade: str | None = None, subject: str | None = None) -> bytes:
    """Questions ka Excel: question_id (KEY — mat chhedo), subject, topic,
    question preview, aur current slo_code (comma-separated). Teacher slo_code
    column bhar/edit kar ke wapas upload karta hai.

    Optional grade/subject filter (dono khali = sab questions, backward compatible)
    `questions_repository.list_for_slo_export` par delegate hota hai."""
    questions = questions_repository.list_for_slo_export(grade=grade, subject=subject)
    codes_map = question_slo_repository.all_codes_by_question()

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "slo_assign"
    # SINGLE machine-readable header (pandas isi ko header parhta hai). Teacher ko
    # question_id na chhedne ki tanbeeh Excel cell-comment se (parsing safe) +
    # SLO page ke UI warning se — alag note-row nahi (warna re-upload par header toot jata).
    ws.append(EXPORT_HEADER)
    ws["A1"].comment = Comment(
        "MAT CHHEDO — import isi question_id se match karta hai. "
        "Ghalat ya gayab id par woh row error degi (chup-chaap kharab nahi hoti). "
        "Sirf slo_code column bharo/edit karo.",
        "PaperMaker",
    )
    for q in questions:
        text = (q.get("question_en") or q.get("question_ur") or "").strip()
        if len(text) > _PREVIEW_LEN:
            text = text[:_PREVIEW_LEN] + "…"
        ws.append([
            q["id"], q.get("subject", ""), q.get("topic", ""),
            text, ", ".join(codes_map.get(q["id"], [])),
        ])
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


# ── assign import ─────────────────────────────────────────────────────────────

def import_assignments(file_bytes: bytes, filename: str) -> dict:
    """Filled export sheet parh kar har question ke SLO links replace-set karo.

    Returns { updated, errors:[...], warnings:[...] }.
      * question_id khali/unknown  -> ERROR (row skip) — export chheri gayi.
      * slo_code unknown           -> WARNING (baaqi link ban jate).
      * slo_code khali             -> us question ke links CLEAR (replace-set []).
    """
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if not file_bytes:
        return {"updated": 0, "errors": ["File khali hai (0 bytes)."], "warnings": []}
    try:
        if ext == "csv":
            df = pd.read_csv(io.BytesIO(file_bytes), dtype=str, keep_default_na=False)
        elif ext in {"xlsx", "xls"}:
            df = pd.read_excel(io.BytesIO(file_bytes), dtype=str, keep_default_na=False)
        else:
            return {"updated": 0, "errors": [f"Format '{ext}' support nahi (xlsx/csv)."], "warnings": []}
    except Exception:  # noqa: BLE001
        return {"updated": 0, "errors": ["File corrupt ya invalid — export dobara download karein."], "warnings": []}

    df.columns = [str(c).strip().lower() for c in df.columns]

    # Required: question_id + slo_code (export ka clean single header).
    missing = {"question_id", "slo_code"} - set(df.columns)
    if missing:
        return {
            "updated": 0,
            "errors": [f"Zaroori columns missing: {', '.join(sorted(missing))}. "
                       "Export sheet ka header (question_id, slo_code) mat badlo."],
            "warnings": [],
        }

    errors: list = []
    warnings: list = []
    updated = 0

    for idx, row in df.iterrows():
        row_num = int(idx) + 2
        qid = str(row.get("question_id", "")).strip()
        codes = str(row.get("slo_code", "")).strip()

        # Khali line chup-chaap skip; stray header-literal ('question_id') defensive skip
        if not qid:
            continue
        if qid.lower() == "question_id":
            continue
        if questions_repository.find_by_id(qid) is None:
            errors.append(f"row {row_num}: question_id '{qid}' kisi question se match nahi (export chheri gayi?).")
            continue

        slo_ids, unknown = resolve_slo_codes(codes)
        for code in unknown:
            warnings.append(f"row {row_num}: slo_code '{code}' maujood nahi — link nahi bana.")
        question_slo_repository.replace_for_question(qid, slo_ids)
        updated += 1

    return {"updated": updated, "errors": errors, "warnings": warnings}
