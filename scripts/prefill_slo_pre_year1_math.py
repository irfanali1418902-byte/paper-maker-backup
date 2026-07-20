"""EK-DAFA helper — Pre Year 1 Mathematics questions ke liye slo_code pre-fill.

Yeh app ka hissa NAHI. Sirf Pre Year 1 Math ke question-template mapping par
chalta hai. App code / export route / API / static — kuch nahi chhoota. DB mein
kuch NAHI likhta — sirf ek Excel banata hai jo seedha /api/slo/assign-import par
upload ho sake.

Branching TEXT par hai (topic par nahi) — question_en.lower() se rule chunte hain.
Number/range sirf tie-break: pehle text ka number, warna topic ka quoted number,
warna correct_answer_en ka number (count-match jaise sawaalon ke liye).

Mapping (text ka skill -> slo_code; range 1-10 / 11-20 / 21-24):
  Number  "Read and trace the number(s)"       -> N-03 / N-11 / N-16
          "Count..write" / "How many" /
          "There are N.." / Urdu count+write   -> N-04 / N-12 / N-17
          "Colour the X"  (number-intro)       -> N-06 (sirf 1-10, warna KHAALI)
          "Circle all the X" (number-intro)    -> N-07 (sirf 1-10, warna KHAALI)
          "Recite the numbers"                 -> N-01 / N-09 / N-14
          "Point to and identify the numeral"  -> N-02 / N-10 / N-15
          "Match the numeral" / "which number
           matches a group of N objects"       -> N-05 / N-13 / N-18
          "Count the X and match"              -> N-17 (<=20) / N-18 (21-24)
          "Write the number word" (N<=10)      -> N-08
          "Write the missing number"           -> N-21
          "Which number comes after"           -> N-22
          "Which number comes before"          -> N-23
          "Which number comes between"         -> N-24
          "Count backward" / "backward from"   -> N-25
          "Match each number..same number" /
           "Write the numbers from..in order" /
           "Say the numbers..in order"         -> N-19
          "out of order" / "out of sequence"   -> N-20
  Write   "Trace the standing/sleeping/
           slanting lines"                     -> W-01
          "Trace the .. curves"                -> W-02
          "Hold the pencil" / "without going
           outside"                            -> W-03
  Solid   "Trace the <solid>"                  -> D-01..D-06 (shape-word)
          "Match the <solid>"                  -> D-07
          "Name a solid shape..everyday" /
           "which solid shape"                 -> D-08
  Flat    "Trace the <flat>"                   -> S-01..S-04 (shape-word)
          "Trace and draw the <flat>"          -> S-05
          "Colour the <flat>"                  -> S-06
          "Match the <flat>"                   -> S-07
          "Name a flat shape..everyday" /
           "which flat shape"                  -> S-08
          "Name this shape" (MCQ)              -> correct_answer_en ke shape-word se map
  Compare topic 'Concept of "a" and "b"'       -> small/big=C-01, light/heavy=C-02,
                                                  short/tall=C-03, thin/thick=C-04
          "which group has more" / "more or
           less" / "circle the group that has" -> C-05
          "equal number" / "match the
           groups..equal"                      -> C-06
  Koi rule match na ho                         -> KHAALI (andaaza nahi)

NOT: object-colour/circle (11-24, jaise "Colour the ice creams") ke liye rule
nahi — N-06/N-07 sirf 1-10 par lagte hain, in ke liye SLO nahi, is liye MANUAL.

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

FLAT_WORDS = {"circle", "square", "rectangle", "triangle"}
SOLID_WORDS = {"cube", "cone", "sphere", "ovoid", "cuboid", "cylinder"}

# comparison: dono words (topic mein quoted) -> code
COMPARISON = [
    (("small", "big"), "C-01"),
    (("light", "heavy"), "C-02"),
    (("short", "tall"), "C-03"),
    (("thin", "thick"), "C-04"),
]

# range index 0/1/2 -> 1-10 / 11-20 / 21-24
TRACE_BY_RANGE = ["N-03", "N-11", "N-16"]
COUNT_BY_RANGE = ["N-04", "N-12", "N-17"]
RECITE_BY_RANGE = ["N-01", "N-09", "N-14"]
POINT_BY_RANGE = ["N-02", "N-10", "N-15"]
NUMERAL_GROUP_BY_RANGE = ["N-05", "N-13", "N-18"]   # match numeral <-> group of objects


def _num_range(n: int) -> int | None:
    """1-10 -> 0, 11-20 -> 1, 21-24 -> 2, warna None."""
    if 1 <= n <= 10:
        return 0
    if 11 <= n <= 20:
        return 1
    if 21 <= n <= 24:
        return 2
    return None


def _extract_number(text: str, topic: str = "", answer: str = "") -> int | None:
    """Tie-break number: pehle text ka pehla number, warna topic ka quoted
    number (Introduction of number "3"..), warna correct_answer ka number
    (count-the-X-and-match jaise sawaal jinke text mein number nahi hota)."""
    m = re.search(r"(\d+)", text)
    if not m:
        m = re.search(r'number\s*"?(\d+)"?', topic, re.IGNORECASE)
    if not m:
        m = re.search(r"(\d+)", answer)
    return int(m.group(1)) if m else None


def prefill_one(q: dict, existing: dict[str, list[str]]) -> tuple[str, str]:
    """Return (slo_code_str, rule_label). slo_code_str khali = MANUAL.

    Branching question TEXT par hai; topic/answer sirf range tie-break.
    Pehle se tagged questions ka maujooda code lauta deta hai (preserve)."""
    qid = q["id"]
    if qid in existing:
        # Maujooda tag preserve — magar UPLOAD mein nahi jata: yeh purane
        # (shayad test) tags hain, teacher review kare. Code dikhaya jata hai.
        return ", ".join(existing[qid]), "REVIEW_EXISTING_TAG"

    en = (q.get("question_en") or "").strip()
    ur = (q.get("question_ur") or "").strip()
    topic = (q.get("topic") or "")
    ans = (q.get("correct_answer_en") or "").strip()
    t = en.lower()
    tl = topic.lower()

    def full(short: str) -> str:
        return CODE_PREFIX + short

    n = _extract_number(en, topic, ans)   # text -> topic -> answer
    r = _num_range(n) if n is not None else None

    # ── PRE-WRITING (W) ──────────────────────────────────────────────────────
    if "trace the standing" in t or "trace the sleeping" in t or "trace the slanting" in t:
        return full("W-01"), "write-lines"
    if "trace the" in t and "curve" in t:
        return full("W-02"), "write-curves"
    if "hold the pencil" in t or "without going outside" in t:
        return full("W-03"), "write-grip"

    # ── SHAPE: flat + solid (text ke shape-word par) ─────────────────────────
    for name, code in SHAPE_CODE.items():
        if f"trace the {name}" in t:              # "Trace the circle/cube.."
            return full(code), f"shape-trace:{name}"
    if any(f"trace and draw the {w}" in t for w in FLAT_WORDS):
        return full("S-05"), "flat-trace-draw"
    if any(f"colour the {w}" in t for w in FLAT_WORDS):
        return full("S-06"), "flat-colour"
    if any(f"match the {w}" in t for w in FLAT_WORDS):
        return full("S-07"), "flat-match"
    if any(f"match the {w}" in t for w in SOLID_WORDS):
        return full("D-07"), "solid-match"
    if "name a flat shape" in t or "which flat shape" in t:
        return full("S-08"), "flat-everyday"
    if "name a solid shape" in t or "which solid shape" in t:
        return full("D-08"), "solid-everyday"
    if "name this shape" in t:
        a = ans.lower()
        if a in SHAPE_CODE:
            return full(SHAPE_CODE[a]), f"shape-name:{a}"
        return "", "MANUAL"

    # ── COMPARISON (C) ───────────────────────────────────────────────────────
    if "concept of" in tl:                        # topic-based small/big.. (purana)
        for words, code in COMPARISON:
            if all(f'"{w}"' in tl for w in words):
                return full(code), "comparison"
        return "", "MANUAL"
    if "which group has more" in t or "more or less" in t or "circle the group that has" in t:
        return full("C-05"), "compare-more"
    if "equal number" in t or ("equal" in t and "match the groups" in t):
        return full("C-06"), "compare-equal"

    # ── NUMBER (N): text-based skills ────────────────────────────────────────
    if "read and trace the number" in t and r is not None:
        return full(TRACE_BY_RANGE[r]), f"number-trace(N={n})"
    if "trace the number" in t and r is not None:     # purana "Trace the number N"
        return full(TRACE_BY_RANGE[r]), f"number-trace(N={n})"
    if "recite the numbers" in t and r is not None:
        return full(RECITE_BY_RANGE[r]), f"number-recite(N={n})"
    if "point to and identify the numeral" in t and r is not None:
        return full(POINT_BY_RANGE[r]), f"number-point(N={n})"
    if "write the missing number" in t:
        return full("N-21"), "number-missing"
    if "which number comes after" in t:
        return full("N-22"), "number-after"
    if "which number comes before" in t:
        return full("N-23"), "number-before"
    if "which number comes between" in t:
        return full("N-24"), "number-between"
    if "count backward" in t or "backward from" in t or "numbers backward" in t:
        return full("N-25"), "number-backward"
    if "number word" in t:
        return (full("N-08"), f"number-word(N={n})") if (n or 0) <= 10 else ("", "MANUAL")
    if ("match the numeral" in t or "which number matches a group" in t) and r is not None:
        return full(NUMERAL_GROUP_BY_RANGE[r]), f"numeral-group(N={n})"
    if re.search(r"count the \w+ and match", t) and r is not None:
        code = "N-18" if r == 2 else "N-17"
        return full(code), f"count-match(N={n})"
    if ("match each number" in t and "same number" in t) \
       or ("write the numbers from" in t and "in order" in t) \
       or ("say the numbers" in t and "in" in t and "order" in t):
        return full("N-19"), "number-sequence"
    if "out of order" in t or "out of sequence" in t:
        return full("N-20"), "number-out-of-order"

    # ── NUMBER-INTRO (quoted number topic): purane colour/circle/count rules ─
    # In ke text mein number nahi hota; range topic se aata hai. Object-colour/
    # circle (11-24) yahin r!=0 hone se MANUAL rehte hain — N-06/N-07 sirf 1-10.
    is_number_topic = bool(re.search(r'number\s*"?\d', tl))
    if is_number_topic and r is not None:
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
