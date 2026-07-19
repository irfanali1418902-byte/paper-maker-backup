"""Paper Bloom shortfall — Marhala 2 Hissa B.

Ek paper ke sawalon ka ASAL Bloom distribution (SLO ke bloom_level se) nikaal kar
class ke standard (Pre-Primary 70/30 wagaira) se compare karta hai, aur per-Bloom
KAMI (shortfall) dikhata hai. **App khud kuch adjust NAHI karta** — sirf report;
teacher 3 option mein se chunta hai (UI).

Ahem faisle (Marhala 2B):
  * Bloom source = SLO ka bloom_level (question ka apna NAHI — woh auto-derive/mashkook).
  * Multi-SLO question → uske SLOs mein se SABSE UNCHA (highest) Bloom.
  * Denominator N = paper ke "classifiable" questions (SLO-tagged AND bloom maloom).
  * Untagged (koi SLO link nahi) aur bloom-unknown (SLO tagged par bloom NULL) —
    DO alag ginti, distribution se bahar (denominator mein nahi).
  * Case-insensitive: har bloom `LOWER(TRIM)` — questions 'REMEMBER', slo 'remember',
    standard 'remember' sab ek jagah aayen (warna ginti zero).
  * Live compute (JOIN), stored snapshot NAHI — coverage service jaisa.
"""

import json
from collections import Counter

from app.core import bloom_standards
from app.repositories import papers_repository, question_slo_repository

# Bloom taxonomy tarteeb — "highest" resolve karne aur display order ke liye.
_BLOOM_ORDER = ["remember", "understand", "apply", "analyze", "evaluate"]
_RANK = {b: i for i, b in enumerate(_BLOOM_ORDER)}


def _norm(bloom: str | None) -> str:
    """Compare-time normalize — lower + strip. None/khali -> ''."""
    return (bloom or "").strip().lower()


def _largest_remainder(percents: dict, total: int) -> dict:
    """percent-distribution (sum 100) ko integer counts mein baanto jo THEEK `total`
    tak jorien (Hamilton / largest-remainder). total=0 -> sab 0."""
    if total <= 0:
        return {b: 0 for b in percents}
    raw = {b: percents[b] * total / 100 for b in percents}
    floor = {b: int(raw[b]) for b in percents}
    leftover = total - sum(floor.values())
    # sabse bari fractional remainder wale blooms ko ek-ek extra do
    order = sorted(percents, key=lambda b: (raw[b] - floor[b], _RANK.get(b, 99)), reverse=True)
    for b in order[:leftover]:
        floor[b] += 1
    return floor


def _no_distribution(paper_id, paper, question_ids, untagged, bloom_unknown, message):
    """Graceful shape — distribution nahi bana (class set nahi / standard nahi /
    sab untagged). Coverage ke _no_universe jaisa: counts phir bhi dikhao, panel
    ZERO na dikhaye — saaf message de."""
    return {
        "paper_id": paper_id,
        "class": paper.get("class_name"),
        "subject": paper.get("subject"),
        "group": None,
        "distribution_available": False,
        "message": message,
        "size": len(question_ids),
        "classifiable_questions": 0,
        "untagged_questions": untagged,
        "bloom_unknown_questions": bloom_unknown,
        "multi_slo_questions": 0,
        "target_percent": {},
        "bloom_rows": [],
        "total_short": 0,
    }


def compute_shortfall(paper_id: str) -> dict | None:
    """Returns shortfall dict, ya None agar paper na mile (route -> 404)."""
    paper = papers_repository.find_by_id(paper_id)
    if paper is None:
        return None

    question_ids = list(dict.fromkeys(json.loads(paper["question_ids"])))
    class_name = paper.get("class_name")

    # --- har question ka Bloom (SLO se, highest) + untagged/unknown ginti ---
    rows = question_slo_repository.list_slo_blooms_for_questions(question_ids)
    links_by_q: Counter = Counter()          # question_id -> kitne SLO link
    blooms_by_q: dict = {}                    # question_id -> [normalized bloom, ...] (non-null)
    for r in rows:
        qid = r["question_id"]
        links_by_q[qid] += 1
        b = _norm(r["bloom_level"])
        if b:
            blooms_by_q.setdefault(qid, []).append(b)

    tagged_qids = set(links_by_q)
    untagged = sum(1 for q in question_ids if q not in tagged_qids)
    # SLO tagged hai par uska/unka bloom sab NULL -> bloom-unknown
    bloom_unknown = sum(1 for q in tagged_qids if not blooms_by_q.get(q))

    # classifiable: tagged AND koi known bloom -> highest level lo
    actual: Counter = Counter()
    multi_slo = 0
    classifiable = 0
    for qid, blooms in blooms_by_q.items():
        ranked = [b for b in blooms if b in _RANK]
        if not ranked:
            continue  # bloom value tha par taxonomy se bahar -> unknown jaisa
        top = max(ranked, key=lambda b: _RANK[b])
        actual[top] += 1
        classifiable += 1
        if links_by_q[qid] > 1:
            multi_slo += 1

    # --- graceful exits (panel zero na dikhaye) ---
    if not class_name or not str(class_name).strip():
        return _no_distribution(paper_id, paper, question_ids, untagged, bloom_unknown,
                                "Is paper mein class set nahi — Bloom standard nahi laga sakte.")
    target = bloom_standards.get_bloom_suggestion(class_name)
    if target is None:
        return _no_distribution(paper_id, paper, question_ids, untagged, bloom_unknown,
                                f"'{class_name}' ke liye Bloom standard define nahi.")
    if classifiable == 0:
        return _no_distribution(paper_id, paper, question_ids, untagged, bloom_unknown,
                                "Bloom distribution nahi bana sakte — is paper ke questions tagged nahi.")

    # --- target counts (largest-remainder over classifiable N) + per-bloom rows ---
    percents = target["distribution"]  # {remember:70, understand:30, apply:0, ...} (lowercase)
    needed = _largest_remainder(percents, classifiable)

    blooms_seen = [b for b in _BLOOM_ORDER if percents.get(b, 0) > 0 or actual.get(b, 0) > 0]
    bloom_rows = []
    total_short = 0
    for b in blooms_seen:
        need = needed.get(b, 0)
        have = actual.get(b, 0)
        short = max(0, need - have)
        total_short += short
        bloom_rows.append({"bloom": b, "needed": need, "actual": have, "short": short})

    return {
        "paper_id": paper_id,
        "class": class_name,
        "subject": paper.get("subject"),
        "group": target["group"],
        "distribution_available": True,
        "size": len(question_ids),
        "classifiable_questions": classifiable,
        "untagged_questions": untagged,
        "bloom_unknown_questions": bloom_unknown,
        "multi_slo_questions": multi_slo,
        "target_percent": dict(percents),
        "bloom_rows": bloom_rows,
        "total_short": total_short,
    }
