"""EK-DAFA helper — 'Comparison of groups' ke liye naya Pre Year 1 Math syllabus
topic banata hai, aur us naye upload ke 10 questions ko us par joRta hai.

Yeh app ka hissa NAHI. App code / routes / services / static — kuch nahi chhoota.

FAISLA (kyun naya topic, force-fit nahi):
  Quantity ka muqabla (zyada / kam / barabar) size aur weight ke muqable se ALAG
  skill hai. Syllabus ka "Unit 2: Comparison Concepts" abhi sirf small/big,
  light/heavy, short/tall, thin/thick rakhta hai — yeh sab ek cheez ki khasoosiyat
  (attribute) ka muqabla hain. Groups ka muqabla ginti (counting) ka kaam hai.
  Kisi maujooda size/weight topic par force-fit karne se aage Grade 1-2 ka data
  aate waqt gadbad hogi — is liye alag topic banate hain (usi Unit 2 ke andar).

DEFAULT DRY-RUN: sirf dikhata kya banega/badlega. `--apply` par hi likhta (ek transaction).

IDEMPOTENT: naya row UNIQUE(subject, grade, unit_no, subtopic_title, page_no) se
pehchana jata — dobara chalao to duplicate row NAHI banta, mojood id reuse hoti.

Naya row (baqi columns Unit 2 pattern ke mutabiq):
  grade='Pre Year 1', subject='Mathematics', unit='Unit 2: Comparison Concepts',
  unit_no=1, unit_title='Mathematics', page_range='1-80', activity_type='Introduction',
  page_no=13, subtopic_title = learning_outcome = questions ka asal topic string
  ('Comparison of groups — more, less and equal' — DB se hi liya, em-dash exact).

Usage:
    python scripts/add_comparison_groups_topic.py [--db paper_maker.db]   # dry-run
    python scripts/add_comparison_groups_topic.py --apply                 # likho
"""

from __future__ import annotations

import argparse
import sqlite3
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

CREATED_PREFIX = "2026-07-19 14"           # naya upload cluster
TOPIC_MATCH = "comparison of groups"       # lower-case substring — target pehchan

# Naye syllabus row ke fixed columns (Unit 2 pattern). subtopic_title/learning_outcome
# runtime par questions ke asal topic se aate (em-dash exact rakhne ke liye).
NEW_ROW = {
    "subject": "Mathematics",
    "grade": "Pre Year 1",
    "unit_no": 1,
    "unit_title": "Mathematics",
    "page_range": "1-80",
    "activity_type": "Introduction",
    "page_no": 13,
    "unit": "Unit 2: Comparison Concepts",
}


def _p(s) -> str:
    return str(s).encode("ascii", "replace").decode()


def load_targets(conn: sqlite3.Connection) -> list[dict]:
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        """SELECT id, topic, syllabus_topic_id
           FROM questions q
           WHERE LOWER(TRIM(subject)) IN ('math', 'mathematics')
             AND created_at LIKE ?
             AND LOWER(topic) LIKE ?""",
        (CREATED_PREFIX + "%", f"%{TOPIC_MATCH}%"),
    ).fetchall()
    return [dict(r) for r in rows]


def find_existing_topic(conn: sqlite3.Connection, subtopic: str) -> dict | None:
    """UNIQUE key se dekho ke naya row pehle se maujood to nahi (idempotency)."""
    row = conn.execute(
        """SELECT * FROM syllabus_topics
           WHERE subject = ? AND grade = ? AND unit_no = ?
             AND subtopic_title = ? AND page_no = ?""",
        (NEW_ROW["subject"], NEW_ROW["grade"], NEW_ROW["unit_no"], subtopic, NEW_ROW["page_no"]),
    ).fetchone()
    return dict(row) if row else None


def insert_topic(conn: sqlite3.Connection, subtopic: str) -> str:
    topic_id = str(uuid.uuid4())
    conn.execute(
        """INSERT INTO syllabus_topics
           (id, subject, grade, unit_no, unit_title, page_range,
            subtopic_title, activity_type, page_no, learning_outcome, unit)
           VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
        (
            topic_id, NEW_ROW["subject"], NEW_ROW["grade"], NEW_ROW["unit_no"],
            NEW_ROW["unit_title"], NEW_ROW["page_range"], subtopic,
            NEW_ROW["activity_type"], NEW_ROW["page_no"], subtopic, NEW_ROW["unit"],
        ),
    )
    return topic_id


def main() -> None:
    ap = argparse.ArgumentParser(
        description="'Comparison of groups' naya PY1 Math syllabus topic + 10 questions link (default dry-run)"
    )
    ap.add_argument("--db", default=str(ROOT / "paper_maker.db"), help="SQLite DB path")
    ap.add_argument("--apply", action="store_true", help="Sach-much likho (warna dry-run)")
    args = ap.parse_args()

    db_path = Path(args.db)
    if not db_path.exists():
        raise SystemExit(f"DB nahi mila: {db_path}")

    conn = sqlite3.connect(str(db_path))
    try:
        targets = load_targets(conn)
        if not targets:
            raise SystemExit("Koi 'Comparison of groups' target question nahi mila — check karo.")

        # subtopic_title questions ke asal topic se (em-dash exact). Ek se zyada
        # distinct topic aaye to ruk jao — pehchan galat ho sakti.
        distinct_topics = sorted({q["topic"] for q in targets})
        if len(distinct_topics) != 1:
            raise SystemExit(f"Ek se zyada distinct target topic mile: {[_p(t) for t in distinct_topics]}")
        subtopic = distinct_topics[0]

        existing = find_existing_topic(conn, subtopic)
        topic_id = existing["id"] if existing else None

        to_change = [q for q in targets if q.get("syllabus_topic_id") != topic_id or topic_id is None]
        unchanged = [q for q in targets if topic_id is not None and q.get("syllabus_topic_id") == topic_id]

        # ── report ──────────────────────────────────────────────────────────
        print(f"\nTarget questions ('Comparison of groups'): {len(targets)}")
        print("\nSyllabus row:")
        print(f"  subtopic_title : {_p(subtopic)!r}")
        print(f"  unit           : {NEW_ROW['unit']!r}  (grade={NEW_ROW['grade']}, subject={NEW_ROW['subject']}, page_no={NEW_ROW['page_no']})")
        if existing:
            print(f"  status         : PEHLE SE MAUJOOD (id={existing['id']}) — naya nahi banega")
        else:
            print("  status         : NAYA banega (abhi id nahi — apply par uuid milega)")

        print(f"\n  questions to LINK (syllabus_topic_id set): {len(to_change)}")
        print(f"  already linked                            : {len(unchanged)}")

        if args.apply:
            if existing is None:
                topic_id = insert_topic(conn, subtopic)
                print(f"\n  -> naya syllabus row daala: id={topic_id}")
            cur = conn.cursor()
            for q in to_change:
                cur.execute(
                    "UPDATE questions SET syllabus_topic_id = ? WHERE id = ?",
                    (topic_id, q["id"]),
                )
            conn.commit()
            print(f"  -> {len(to_change)} questions ka syllabus_topic_id set ho gaya.")
            print("\nAPPLIED.")
        else:
            print("\n(DRY-RUN — kuch nahi likha. Apply karne ke liye --apply do.)")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
