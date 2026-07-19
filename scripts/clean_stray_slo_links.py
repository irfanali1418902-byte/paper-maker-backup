"""EK-DAFA cleanup — Pre Year 1 Mathematics questions par lage GHALAT question_slo
links hatao (pichhle browser-test ka kachra: number questions par D-01/C-01/S-01/
W-01/N-01 wagaira). Yeh wahi links hain jo prefill script ne REVIEW_EXISTING_TAG
mark kiye the.

Bilkul EHTIYAAT ke saath:
  * Default = DRY-RUN — sirf dikhata hai kaun se links delete honge, kuch NAHI hatata.
  * Delete sirf tab hota hai jab `--delete` flag diya jaye (soch-samajh kar).
  * Delete usi (question_id, slo_id) jodon par hota hai jo dry-run mein dikhe —
    dry-run aur delete ka set bilkul ek jaisa (koi surprise nahi).

Target BILKUL precise hai: sirf "How many ... are there?" wale MCQ jinpar
count-family (N-04/N-12/N-17) ke ALAWA koi code laga hai. Teacher ke bulk-upload
kiye 161 SAHI tags is filter mein NAHI aate (dry-run isay tasdeeq karta hai).

App code / route / API / static — kuch nahi chhoota. Sirf question_slo table ke
yeh 8 links (aur woh bhi confirm par). questions/slo tables bilkul untouched.

Usage:
    python scripts/clean_stray_slo_links.py            # dry-run (safe)
    python scripts/clean_stray_slo_links.py --delete   # actually delete
"""

from __future__ import annotations

import argparse
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Count-family SLO — "How many X are there?" ka SAHI code inhi mein hota hai.
COUNT_CODES = ("MATH-PY1-N-04", "MATH-PY1-N-12", "MATH-PY1-N-17")

# Target = SIRF ghalat (test-kachra) links: "How many ... are there?" MCQ jinpar
# count-family ke ALAWA koi code laga hai (D-01/C-01/S-01/W-01/N-01 wagaira).
# (Baqi 161 sahi tags — jo teacher ne bulk-upload kiye — is filter mein NAHI aate.)
_PLACEHOLDERS = ", ".join("?" for _ in COUNT_CODES)
TARGET_SQL = f"""
SELECT qs.question_id AS qid, qs.slo_id AS sid,
       q.topic AS topic, q.question_en AS en, q.question_ur AS ur,
       s.slo_code AS slo_code, s.strand AS strand
FROM question_slo qs
JOIN questions q        ON qs.question_id = q.id
JOIN syllabus_topics st ON q.syllabus_topic_id = st.id
JOIN slo s              ON qs.slo_id = s.id
WHERE LOWER(TRIM(st.grade)) = 'pre year 1'
  AND LOWER(TRIM(st.subject)) = 'mathematics'
  AND q.question_en LIKE 'How many%are there?'
  AND s.slo_code NOT IN ({_PLACEHOLDERS})
ORDER BY q.topic
"""


def _preview(en: str | None, ur: str | None) -> str:
    text = (en or ur or "").strip()
    return text[:50] + "…" if len(text) > 50 else text


def main() -> None:
    ap = argparse.ArgumentParser(description="Pre Year 1 Math ke ghalat SLO links hatao")
    ap.add_argument("--db", default=str(ROOT / "paper_maker.db"), help="SQLite DB path")
    ap.add_argument("--delete", action="store_true",
                    help="Waqai delete karo (bina iske sirf dry-run)")
    args = ap.parse_args()

    try:  # Urdu text console par safe print ho
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:  # noqa: BLE001
        pass

    db_path = Path(args.db)
    if not db_path.exists():
        raise SystemExit(f"DB nahi mila: {db_path}")

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(TARGET_SQL, COUNT_CODES).fetchall()
        total = conn.execute("SELECT COUNT(*) FROM question_slo").fetchone()[0]

        print(f"\nDB: {db_path}")
        print(f"question_slo mein kul links: {total} (inme se sirf ghalat target honge)")
        print("Target: 'How many..are there?' MCQ jinpar count-family ke ALAWA code laga hai\n")
        if not rows:
            print("Koi aisa link nahi mila — kuch karne ki zaroorat nahi.")
            return

        print(f"{len(rows)} link(s) {'DELETE honge' if args.delete else 'delete HO SAKTE hain (dry-run)'}:\n")
        print(f"  {'slo_code':<16} {'strand':<13} topic / question")
        print(f"  {'-'*16} {'-'*13} {'-'*40}")
        for r in rows:
            print(f"  {r['slo_code']:<16} {(r['strand'] or ''):<13} "
                  f"{(r['topic'] or '')[:38]}")
            print(f"  {'':<16} {'':<13} Q: {_preview(r['en'], r['ur'])}")

        if not args.delete:
            print("\n[DRY-RUN] Kuch DELETE nahi hua. Waqai hatane ke liye:")
            print("    python scripts/clean_stray_slo_links.py --delete")
            return

        # ── actual delete: sirf dry-run wale exact (qid, sid) jode ────────────
        pairs = [(r["qid"], r["sid"]) for r in rows]
        conn.executemany(
            "DELETE FROM question_slo WHERE question_id = ? AND slo_id = ?", pairs
        )
        conn.commit()
        remaining = conn.execute("SELECT COUNT(*) FROM question_slo").fetchone()[0]
        print(f"\n[DELETED] {len(pairs)} link(s) hata diye. "
              f"question_slo mein ab {remaining} link(s) baqi.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
