"""Excel-based hafta-war plan — R7 Marhala 2.

Do cheezein:
  * build_template_xlsx() — us (subject, grade) ke topics ka sheet
                            (syllabus_topic_id + title + current week_no)
  * import_assignments()  — bhari hui sheet parh kar plan replace-set

`question_slo_import_service` ka aaina: header lower-case, `syllabus_topic_id` se
match (title se NAHI), ghalat/gayab id par us row ka saaf error -- chup-chaap
corruption kabhi nahi. Tafseel: docs/TOPIC_WEEK_PLAN.md §7
"""

from __future__ import annotations

import io
import re

import openpyxl
import pandas as pd
from openpyxl.comments import Comment

from app.repositories import topic_week_plan_repository
from app.services import topic_week_service

TEMPLATE_HEADER = ["syllabus_topic_id", "subtopic_title", "unit_no", "week_no"]


def template_filename(subject: str | None = None, grade: str | None = None) -> str:
    """Dynamic filename -- `question_slo_import_service.export_filename` ka aaina.
    Misal subject='Mathematics', grade='Pre Year 2' ->
    'topic_week_plan_Mathematics_Pre_Year_2.xlsx'."""
    parts = [p.strip() for p in (subject, grade) if p and p.strip()]
    if not parts:
        return "topic_week_plan.xlsx"
    slug = "_".join(re.sub(r"[^A-Za-z0-9]+", "_", p).strip("_") for p in parts)
    return f"topic_week_plan_{slug}.xlsx"


def build_template_xlsx(subject: str, grade: str) -> bytes:
    """Us (subject, grade) ke SAARE topics ka sheet -- bin-plan wale bhi
    (week_no khali). Teacher sirf `week_no` column bharta hai.

    Current week_no pehle se bhara jata hai, taake ye file "template" bhi ho aur
    "export" bhi: dobara download kar ke sirf badalne wali rows chheri ja sakein.
    Yehi SLO export ka bartao hai (wahan current slo_code bhara aata hai)."""
    rows = topic_week_plan_repository.list_resolved(subject, grade)

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "topic_week_plan"
    # SINGLE machine-readable header (pandas isi ko parhta hai). Tanbeeh Excel
    # cell-comment se -- alag note-row NAHI, warna re-upload par header toot jata.
    ws.append(TEMPLATE_HEADER)
    ws["A1"].comment = Comment(
        "MAT CHHEDO — import isi syllabus_topic_id se match karta hai, title se nahi. "
        "Ghalat ya gayab id par woh row error degi (chup-chaap kharab nahi hoti). "
        "Sirf week_no column bharo.",
        "PaperMaker",
    )
    ws["D1"].comment = Comment(
        "Hafte ki ginti (1 se N tak; N = school settings ka week_count, default 36). "
        "0 = abhi kisi hafte mein nahi. "
        "CELL KHALI CHHOR DO to us topic ka plan HAT jayega.",
        "PaperMaker",
    )
    for r in rows:
        ws.append([
            r["syllabus_topic_id"],
            r.get("subtopic_title", ""),
            r.get("unit_no", ""),
            r.get("week_no") if r.get("week_no") is not None else "",
        ])
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


def import_assignments(file_bytes: bytes, filename: str) -> dict:
    """Bhari hui sheet parh kar har topic ka hafta replace-set karo.

    Returns { updated, cleared, errors:[...], warnings:[...] }.
      * syllabus_topic_id khali/unknown -> ERROR (row skip) -- sheet chheri gayi.
      * week_no khali                   -> us topic ka plan CLEAR (row delete).
      * week_no ginti nahi / range se bahar -> ERROR (row skip).

    Aakhri surat SLO import se jaan-boojh kar mukhtalif hai: wahan unknown
    slo_code sirf WARNING hai kyunke baqi links phir bhi ban jate hain. Yahan
    week_no poori row ka maqsad hai -- ghalat hua to karne ko kuch bacha hi
    nahi, aur chup-chaap 0 (Unassigned) likh dena teacher ko dhoka dena hoga.
    """
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if not file_bytes:
        return {"updated": 0, "cleared": 0, "errors": ["File khali hai (0 bytes)."], "warnings": []}
    try:
        if ext == "csv":
            df = pd.read_csv(io.BytesIO(file_bytes), dtype=str, keep_default_na=False)
        elif ext in {"xlsx", "xls"}:
            df = pd.read_excel(io.BytesIO(file_bytes), dtype=str, keep_default_na=False)
        else:
            return {"updated": 0, "cleared": 0,
                    "errors": [f"Format '{ext}' support nahi (xlsx/csv)."], "warnings": []}
    except Exception:  # noqa: BLE001
        return {"updated": 0, "cleared": 0,
                "errors": ["File corrupt ya invalid — template dobara download karein."],
                "warnings": []}

    df.columns = [str(c).strip().lower() for c in df.columns]

    missing = {"syllabus_topic_id", "week_no"} - set(df.columns)
    if missing:
        return {
            "updated": 0,
            "cleared": 0,
            "errors": [f"Zaroori columns missing: {', '.join(sorted(missing))}. "
                       "Template ka header (syllabus_topic_id, week_no) mat badlo."],
            "warnings": [],
        }

    n = topic_week_service._week_count()
    errors: list = []
    warnings: list = []
    to_assign: list = []
    to_clear: list = []

    # Saari rows pehle parho, phir ek dafa likho. Aadha-likha plan sab se bura
    # nateeja hai: teacher ko pata nahi chalta kaunsi rows lag gayin.
    for idx, row in df.iterrows():
        row_num = int(idx) + 2
        topic_id = str(row.get("syllabus_topic_id", "")).strip()
        week_raw = str(row.get("week_no", "")).strip()

        if not topic_id:
            continue
        if topic_id.lower() == "syllabus_topic_id":  # stray header-literal
            continue

        if not week_raw:
            to_clear.append((row_num, topic_id))
            continue

        try:
            week_no = int(float(week_raw))  # Excel "3.0" bhi qubool
        except (TypeError, ValueError):
            errors.append(f"row {row_num}: week_no '{week_raw}' ginti nahi hai.")
            continue
        if week_no < 0 or week_no > n:
            errors.append(f"row {row_num}: week_no {week_no} hadd se bahar hai (0 se {n}).")
            continue

        to_assign.append((row_num, topic_id, week_no))

    # Ek hi DB round mein tasdeeq -- har row par query nahi.
    all_ids = [t for _, t, _ in to_assign] + [t for _, t in to_clear]
    known = topic_week_plan_repository.existing_topic_ids(all_ids)

    assignments = []
    for row_num, topic_id, week_no in to_assign:
        if topic_id not in known:
            errors.append(
                f"row {row_num}: syllabus_topic_id '{topic_id}' kisi topic se match nahi "
                "(template chheri gayi?)."
            )
            continue
        assignments.append({"syllabus_topic_id": topic_id, "week_no": week_no, "position": None})

    clear_ids = []
    for row_num, topic_id in to_clear:
        if topic_id not in known:
            errors.append(
                f"row {row_num}: syllabus_topic_id '{topic_id}' kisi topic se match nahi "
                "(template chheri gayi?)."
            )
            continue
        clear_ids.append(topic_id)

    topic_week_plan_repository.overwrite_assignments(assignments)
    cleared = topic_week_plan_repository.clear_assignments(clear_ids)

    return {
        "updated": len(assignments),
        "cleared": cleared,
        "errors": errors,
        "warnings": warnings,
    }
