"""EK-DAFA helper — Pre Year 1 Mathematics questions ke liye slo_code pre-fill.

Yeh app ka hissa NAHI. Sirf Pre Year 1 Math ke question-template mapping par
chalta hai. App code / export route / API / static — kuch nahi chhoota. DB mein
kuch NAHI likhta — sirf ek Excel banata hai jo seedha /api/slo/assign-import par
upload ho sake.

Mapping (text ka skill + number/shape se slo_code):
  Number  "Trace the number N"                 -> N-03 (1-10) / N-11 (11-20) / N-16 (21-24)
          "Count..write" / "How many" /
          "There are N.." / Urdu count+write   -> N-04       / N-12        / N-17
          "Colour the X"                       -> N-06 (sirf 1-10, warna KHAALI)
          "Circle all the X"                   -> N-07 (sirf 1-10, warna KHAALI)
  Shape   "Trace the <shape>"                  -> shape-word se S-01..S-04 / D-01..D-06
          "Name this shape" (MCQ)              -> correct_answer_en ke shape-word se wahi map
  Compare topic 'Concept of "a" and "b"'       -> small/big=C-01, light/heavy=C-02,
                                                  short/tall=C-03, thin/thick=C-04
  Koi rule match na ho                         -> KHAALI (andaaza nahi)

Codes par full prefix "MATH-PY1-" lagta hai (import exact slo_code match karta hai).
Pehle se tagged questions ka maujooda code preserve hota hai (overwrite nahi).

Output: ek .xlsx, DO sheets —
  * "UPLOAD"  : sirf bhare hue slo_code (auto-filled + already-tagged). Yehi upload hoti hai.
  * "MANUAL"  : khaali/unmatched, sirf review ke liye. Upload NAHI hoti.
assign-import pandas se PEHLI sheet (index 0 = UPLOAD) parhta hai — sheet ka naam
nahi maangta. Script aakhir mein isay verify bhi karta hai.

Usage:
    python scripts/prefill_slo_pre_year1_math.py [--db paper_maker.db] [--out scripts/prefill_pre_year1_math.xlsx]
"""

from __future__ import annotations

import argparse
import re
import sqlite3
from collections import Counter
from pathlib import Path

import openpyxl

ROOT = Path(__file__).resolve().parent.parent
CODE_PREFIX = "MATH-PY1-"
PREVIEW_LEN = 80  # export ki tarah question preview
EXPORT_HEADER = ["question_id", "subject", "topic", "question", "slo_code"]
OUT_HEADER = EXPORT_HEADER + ["prefill_rule"]  # 6th col — import ise IGNORE karta hai

# shape-word -> short code (SLO definitions se tasdeeq-shuda)
SHAPE_CODE = {
    "circle": "S-01", "square": "S-02", "rectangle": "S-03", "triangle": "S-04",
    "cylinder": "D-01", "sphere": "D-02", "cube": "D-03", "cuboid": "D-04",
    "cone": "D-05", "ovoid": "D-06",
}

# comparison: dono words (topic mein quoted) -> code
COMPARISON = [
    (("small", "big"), "C-01"),
    (("light", "heavy"), "C-02"),
    (("short", "tall"), "C-03"),
    (("thin", "thick"), "C-04"),
]

TRACE_BY_RANGE = ["N-03", "N-11", "N-16"]   # 1-10, 11-20, 21-24
COUNT_BY_RANGE = ["N-04", "N-12", "N-17"]


def _num_range(n: int) -> int | None:
    """1-10 -> 0, 11-20 -> 1, 21-24 -> 2, warna None."""
    if 1 <= n <= 10:
        return 0
    if 11 <= n <= 20:
        return 1
    if 21 <= n <= 24:
        return 2
    return None


def _extract_number(topic: str, text: str) -> int | None:
    """Pehle topic ke quoted number (Introduction of number "3"..) se, warna text se."""
    m = re.search(r'number\s*"?(\d+)"?', topic, re.IGNORECASE)
    if not m:
        m = re.search(r"(\d+)", text)
    return int(m.group(1)) if m else None


def prefill_one(q: dict, existing: dict[str, list[str]]) -> tuple[str, str]:
    """Return (slo_code_str, rule_label). slo_code_str khali = MANUAL.

    Pehle se tagged questions ka maujooda code lauta deta hai (preserve)."""
    qid = q["id"]
    if qid in existing:
        # Maujooda tag preserve — magar UPLOAD mein nahi jata: yeh purane
        # (shayad test) tags hain, teacher review kare. Code dikhaya jata hai.
        return ", ".join(existing[qid]), "REVIEW_EXISTING_TAG"

    en = (q.get("question_en") or "").strip()
    ur = (q.get("question_ur") or "").strip()
    topic = (q.get("topic") or "")
    t = en.lower()
    tl = topic.lower()

    def full(short: str) -> str:
        return CODE_PREFIX + short

    # Branch priority: NUMBER pehle. (Number-introduction topic ka naam
    # 'Introduction of number "3" it\'s value and shape' hai — usme lafz "shape"
    # bhi hai, is liye "shape in topic" se pehle number-topic detect karna zaroori,
    # warna number-intro questions ghalti se SHAPE branch mein chale jate hain.)
    is_number_topic = bool(re.search(r'number\s*"?\d', tl))

    # ── NUMBER ───────────────────────────────────────────────────────────────
    if is_number_topic:
        n = _extract_number(topic, en)
        r = _num_range(n) if n is not None else None
        if r is None:
            return "", "MANUAL"
        if "trace the number" in t:
            return full(TRACE_BY_RANGE[r]), f"number-trace(N={n})"
        if "colour" in t or "color" in t:
            return (full("N-06"), f"number-colour(N={n})") if r == 0 else ("", "MANUAL")
        if "circle" in t:
            return (full("N-07"), f"number-circle(N={n})") if r == 0 else ("", "MANUAL")
        if ("how many" in t) or ("count" in t and "write" in t) or \
           ("there are" in t) or ("there is" in t):
            return full(COUNT_BY_RANGE[r]), f"number-count(N={n})"
        if not en and ur:  # Urdu count+write jorra (question_en khali)
            return full(COUNT_BY_RANGE[r]), f"number-count-urdu(N={n})"
        return "", "MANUAL"

    # ── COMPARISON ───────────────────────────────────────────────────────────
    if "concept of" in tl:
        for words, code in COMPARISON:
            if all(f'"{w}"' in tl for w in words):
                return full(code), "comparison"
        return "", "MANUAL"

    # ── SHAPE ────────────────────────────────────────────────────────────────
    if "shape" in tl:
        for name, code in SHAPE_CODE.items():
            if f"trace the {name}" in t:
                return full(code), f"shape-trace:{name}"
        if "name this shape" in t:
            ans = (q.get("correct_answer_en") or "").strip().lower()
            if ans in SHAPE_CODE:
                return full(SHAPE_CODE[ans]), f"shape-name:{ans}"
        return "", "MANUAL"

    return "", "MANUAL"


def load_questions(conn: sqlite3.Connection) -> list[dict]:
    """Pre Year 1 Mathematics questions — grade syllabus_topics se (jaisa export grade-filter)."""
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        """SELECT q.* FROM questions q
           JOIN syllabus_topics st ON q.syllabus_topic_id = st.id
           WHERE LOWER(TRIM(st.grade)) = 'pre year 1'
             AND LOWER(TRIM(st.subject)) = 'mathematics'""",
    ).fetchall()
    return [dict(r) for r in rows]


def load_existing_tags(conn: sqlite3.Connection) -> dict[str, list[str]]:
    """question_id -> [maujooda slo_code, ...] (protect: overwrite mat karo)."""
    rows = conn.execute(
        """SELECT qs.question_id AS qid, s.slo_code AS code
           FROM question_slo qs JOIN slo s ON qs.slo_id = s.id
           ORDER BY s.slo_code""",
    ).fetchall()
    out: dict[str, list[str]] = {}
    for r in rows:
        out.setdefault(r["qid"], []).append(r["code"])
    return out


def _preview(q: dict) -> str:
    text = (q.get("question_en") or q.get("question_ur") or "").strip()
    return text[:PREVIEW_LEN] + "…" if len(text) > PREVIEW_LEN else text


def build_workbook(questions: list[dict], existing: dict[str, list[str]]):
    """(wb, summary). UPLOAD sheet PEHLI banti hai taake import (sheet index 0) usi ko parhe."""
    wb = openpyxl.Workbook()
    up = wb.active
    up.title = "UPLOAD"
    up.append(OUT_HEADER)
    man = wb.create_sheet("MANUAL")
    man.append(OUT_HEADER)

    rule_counts: Counter = Counter()
    filled = manual = 0
    for q in questions:
        code, rule = prefill_one(q, existing)
        rule_counts[rule] += 1
        row = [q["id"], q.get("subject", ""), q.get("topic", ""), _preview(q), code, rule]
        # UPLOAD sirf saaf auto-fill; REVIEW_EXISTING_TAG (code hote hue bhi) aur
        # khali/MANUAL sab MANUAL sheet par (review ke liye — upload nahi hote).
        if code and rule != "REVIEW_EXISTING_TAG":
            up.append(row)
            filled += 1
        else:
            man.append(row)
            manual += 1

    summary = {
        "total": len(questions),
        "filled": filled,
        "manual": manual,
        "rules": rule_counts,
    }
    return wb, summary


def verify_first_sheet(path: Path) -> str:
    """import ki tarah pandas se PEHLI sheet parho — confirm UPLOAD hi aati hai
    aur har row ka slo_code bhara hai. (assign-import sheet_name=0 = pehli sheet.)"""
    import pandas as pd
    df = pd.read_excel(path, dtype=str, keep_default_na=False)  # sheet_name=0 default
    cols = [c.strip().lower() for c in df.columns]
    if not {"question_id", "slo_code"} <= set(cols):
        return "GARBAR: pehli sheet mein required columns nahi!"
    blanks = (df["slo_code"].astype(str).str.strip() == "").sum()
    return (f"pehli sheet = UPLOAD, rows={len(df)}, khali slo_code={blanks} "
            f"(0 hona chahiye)")


def main() -> None:
    ap = argparse.ArgumentParser(description="Pre Year 1 Math SLO pre-fill Excel banao (read-only)")
    ap.add_argument("--db", default=str(ROOT / "paper_maker.db"), help="SQLite DB path")
    ap.add_argument("--out", default=str(ROOT / "scripts" / "prefill_pre_year1_math.xlsx"),
                    help="Output .xlsx path")
    args = ap.parse_args()

    db_path = Path(args.db)
    if not db_path.exists():
        raise SystemExit(f"DB nahi mila: {db_path}")

    conn = sqlite3.connect(str(db_path))
    try:
        questions = load_questions(conn)
        existing = load_existing_tags(conn)
    finally:
        conn.close()  # sirf padha — kuch likha nahi

    if not questions:
        raise SystemExit("Pre Year 1 Mathematics ka koi question nahi mila — DB check karo.")

    wb, summary = build_workbook(questions, existing)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    wb.save(out_path)

    # ── console summary ──────────────────────────────────────────────────────
    print(f"\nOutput: {out_path}")
    print(f"Total Pre Year 1 Math questions   : {summary['total']}")
    print(f"  UPLOAD sheet (auto-filled)      : {summary['filled']}")
    print(f"  MANUAL sheet (khali + review)   : {summary['manual']}")
    print("\nRule-wise breakdown:")
    for rule, cnt in sorted(summary["rules"].items(), key=lambda kv: (-kv[1], kv[0])):
        print(f"  {cnt:>4}  {rule}")

    print("\nVerify (import pehli sheet se parhega):")
    print(f"  {verify_first_sheet(out_path)}")
    print("\nAgla qadam: UPLOAD sheet wali file /api/slo/assign-import par upload karo. "
          "prefill_rule column import IGNORE karta hai — delete karne ki zaroorat NAHI.")


if __name__ == "__main__":
    main()
