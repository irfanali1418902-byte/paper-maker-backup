"""EK-DAFA helper — naye Pre Year 1 Math questions ka topic + syllabus_topic_id remap.

Yeh app ka hissa NAHI. Sirf ek data-fix: naya upload hue Pre Year 1 Math questions
ka `questions.topic` free-text + `questions.syllabus_topic_id` ko syllabus ke SAHI
row par le aata hai. App code / routes / services / static — kuch nahi chhoota.

DEFAULT DRY-RUN: sirf dikhata hai kya badlega (kitne rows, purana topic -> naya
topic + naya syllabus_topic_id). `--apply` par hi likhta (ek transaction).

Mapping ka usool — PAGE se, andaaza nahi:
  Har target question ke `page_number` se Pre Year 1 Math syllabus row (jiska
  `page_no` == question ka page_number) dhoondte hain, aur:
    * questions.syllabus_topic_id = us row ka id
    * questions.topic            = us row ka subtopic_title
  Duplicate review-topics (jaise "Practice and Review of number and value" kai
  pages par) is tarah page_number se apni-apni sahi row par jaate hain.

Target set:
  subject Math/Mathematics AND created_at is cluster ka (naya upload) AND abhi
  tak untagged (koi question_slo link nahi).

SKIP (jaan-boojh kar): "Comparison of groups" wale questions — syllabus mein
un ka koi topic hai hi nahi (Unit 2 sirf size/weight). Inka faisla Hissa 2 mein
alag hoga; page-map inhe galat row (page 13 = Practice/Review) par bhej deta,
is liye topic-naam se skip karte hain.

Usage:
    python scripts/remap_new_question_topics.py [--db paper_maker.db]        # dry-run
    python scripts/remap_new_question_topics.py --apply                      # likho
"""

from __future__ import annotations

import argparse
import sqlite3
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

CREATED_PREFIX = "2026-07-19 14"        # naya upload cluster (created_at LIKE '...%')
GRADE = "pre year 1"
SKIP_TOPIC_SUBSTR = "comparison of groups"   # lower-case substring — Hissa 2 tak skip


def load_targets(conn: sqlite3.Connection) -> list[dict]:
    """Naya-upload, untagged Pre Year 1 Math questions."""
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        """SELECT id, topic, page_number, syllabus_topic_id
           FROM questions q
           WHERE LOWER(TRIM(subject)) IN ('math', 'mathematics')
             AND created_at LIKE ?
             AND NOT EXISTS (SELECT 1 FROM question_slo qs WHERE qs.question_id = q.id)""",
        (CREATED_PREFIX + "%",),
    ).fetchall()
    return [dict(r) for r in rows]


def load_syllabus_by_page(conn: sqlite3.Connection) -> tuple[dict[int, dict], list[int]]:
    """page_no -> syllabus row (Pre Year 1 Math). Agar koi page_no par ek se zyada
    row ho to woh page 'ambiguous' list mein — mapping us par nahi lagti."""
    rows = conn.execute(
        """SELECT id, page_no, subtopic_title
           FROM syllabus_topics
           WHERE LOWER(TRIM(grade)) = ? AND LOWER(TRIM(subject)) = 'mathematics'""",
        (GRADE,),
    ).fetchall()
    by_page: dict[int, dict] = {}
    seen: Counter = Counter()
    for r in rows:
        seen[r["page_no"]] += 1
        by_page[r["page_no"]] = dict(r)
    ambiguous = [p for p, c in seen.items() if c > 1]
    return by_page, ambiguous


def plan(targets: list[dict], by_page: dict[int, dict], ambiguous: list[int]) -> dict:
    """Har target ko ek bucket mein daalo: skip / unmapped / unchanged / change."""
    changes: list[dict] = []
    unchanged: list[dict] = []
    skipped: list[dict] = []
    unmapped: list[dict] = []

    for q in targets:
        topic = q.get("topic") or ""
        if SKIP_TOPIC_SUBSTR in topic.lower():
            skipped.append(q)
            continue
        page = q.get("page_number")
        row = by_page.get(page) if page is not None else None
        if row is None or page in ambiguous:
            unmapped.append(q)
            continue
        new_topic = row["subtopic_title"]
        new_id = row["id"]
        rec = {
            "id": q["id"], "page": page,
            "old_topic": topic, "new_topic": new_topic,
            "old_id": q.get("syllabus_topic_id"), "new_id": new_id,
        }
        if topic == new_topic and q.get("syllabus_topic_id") == new_id:
            unchanged.append(rec)
        else:
            changes.append(rec)

    return {"changes": changes, "unchanged": unchanged,
            "skipped": skipped, "unmapped": unmapped}


def _p(s) -> str:
    return str(s).encode("ascii", "replace").decode()


def print_report(targets, result, ambiguous) -> None:
    changes, unchanged = result["changes"], result["unchanged"]
    skipped, unmapped = result["skipped"], result["unmapped"]

    print(f"\nTarget (naya upload, untagged PY1 Math): {len(targets)}")
    print(f"  will CHANGE   : {len(changes)}")
    print(f"  already OK    : {len(unchanged)}  (topic + id pehle se sahi)")
    print(f"  SKIP (Comparison of groups, Hissa 2): {len(skipped)}")
    print(f"  UNMAPPED (koi syllabus page-row nahi): {len(unmapped)}")
    if ambiguous:
        print(f"  !! ambiguous syllabus pages (>1 row): {sorted(ambiguous)}")

    if changes:
        print("\nCHANGES — grouped (old topic -> new topic @ page, new syllabus_topic_id):")
        grouped: dict = defaultdict(lambda: {"n": 0, "new_id": None})
        for c in changes:
            key = (c["old_topic"], c["page"], c["new_topic"])
            grouped[key]["n"] += 1
            grouped[key]["new_id"] = c["new_id"]
        for (old_t, page, new_t), v in sorted(grouped.items(), key=lambda kv: -kv[1]["n"]):
            print(f"\n  [{v['n']}]  page {page}")
            print(f"        old topic : {_p(old_t)!r}")
            print(f"        new topic : {_p(new_t)!r}")
            print(f"        new id    : {v['new_id']}")

    if skipped:
        print("\nSKIPPED topics (chhoR diye):")
        for t, c in Counter(_p(q.get("topic")) for q in skipped).most_common():
            print(f"  {c:>3}  {t!r}")

    if unmapped:
        print("\nUNMAPPED (page par syllabus row nahi mila):")
        for q in unmapped:
            print(f"  id={q['id']}  page={q.get('page_number')}  topic={_p(q.get('topic'))!r}")


def apply_changes(conn: sqlite3.Connection, changes: list[dict]) -> int:
    cur = conn.cursor()
    for c in changes:
        cur.execute(
            "UPDATE questions SET topic = ?, syllabus_topic_id = ? WHERE id = ?",
            (c["new_topic"], c["new_id"], c["id"]),
        )
    conn.commit()
    return len(changes)


def main() -> None:
    ap = argparse.ArgumentParser(description="Naye PY1 Math questions ka topic+syllabus_topic_id remap (default dry-run)")
    ap.add_argument("--db", default=str(ROOT / "paper_maker.db"), help="SQLite DB path")
    ap.add_argument("--apply", action="store_true", help="Sach-much likho (warna sirf dry-run)")
    args = ap.parse_args()

    db_path = Path(args.db)
    if not db_path.exists():
        raise SystemExit(f"DB nahi mila: {db_path}")

    conn = sqlite3.connect(str(db_path))
    try:
        targets = load_targets(conn)
        by_page, ambiguous = load_syllabus_by_page(conn)
        if not targets:
            raise SystemExit("Koi target question nahi mila — created_at cluster / subject check karo.")
        result = plan(targets, by_page, ambiguous)
        print_report(targets, result, ambiguous)

        if args.apply:
            n = apply_changes(conn, result["changes"])
            print(f"\nAPPLIED: {n} rows update ho gaye (topic + syllabus_topic_id).")
        else:
            print("\n(DRY-RUN — kuch nahi likha. Apply karne ke liye --apply do.)")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
