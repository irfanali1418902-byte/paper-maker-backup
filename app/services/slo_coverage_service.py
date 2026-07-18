"""Paper SLO coverage — Marhala 2 Hissa A.

Ek paper ke sawalon se kaun se SLO cover hue, aur us class/subject ke kaun se
reh gaye — sab LIVE compute (JOIN), koi stored snapshot nahi (link/SLO baad me
badle to report khud sahi rahe). class match CASE/whitespace-insensitive
(papers.class_name free-text hai) — data ko haath nahi lagate.
"""

import json

from app.repositories import papers_repository, question_slo_repository, slo_repository


def compute_coverage(paper_id: str) -> dict | None:
    """Returns coverage dict, ya None agar paper na mile (route -> 404)."""
    paper = papers_repository.find_by_id(paper_id)
    if paper is None:
        return None

    question_ids = json.loads(paper["question_ids"])
    subject = paper["subject"]
    class_name = paper.get("class_name")

    # --- covered: paper ke sawalon se jude distinct SLO (kisi bhi class/subject) ---
    links = question_slo_repository.list_links_for_questions(question_ids)
    covered_map: dict = {}          # slo_id -> {slo fields, question_ids:[...]}
    linked_qids: set = set()
    for row in links:
        linked_qids.add(row["question_id"])
        sid = row["slo_id"]
        if sid not in covered_map:
            covered_map[sid] = {
                "slo_id": sid,
                "slo_code": row["slo_code"],
                "slo_text": row["slo_text"],
                "strand": row["strand"],
                "question_ids": [],
            }
        covered_map[sid]["question_ids"].append(row["question_id"])

    covered = sorted(covered_map.values(), key=lambda s: s["slo_code"] or "")
    covered_ids = set(covered_map.keys())

    # untagged: paper ke woh sawal jinke koi SLO link nahi (200+ purane) —
    # chhupate nahi, alag ginti; coverage % SLOs par banta hai, sawalon par nahi.
    distinct_qids = list(dict.fromkeys(question_ids))
    untagged_questions = sum(1 for q in distinct_qids if q not in linked_qids)

    result = {
        "paper_id": paper_id,
        "class": class_name,
        "subject": subject,
        "covered": covered,
        "covered_slos": len(covered),
        "untagged_questions": untagged_questions,
    }

    # --- universe: is class+subject ke saare SLO (normalized match) ---
    if not class_name or not str(class_name).strip():
        result.update(_no_universe(
            "Is paper mein class set nahi — 'reh gaye SLO' nahi nikaal sakte."
        ))
        return result

    universe = slo_repository.list_by_class_subject_normalized(class_name, subject)
    if not universe:
        result.update(_no_universe(
            f"'{class_name}' / '{subject}' ke liye koi SLO define nahi — "
            "sirf tagged SLO dikhaye ja rahe, 'reh gaye' nahi nikaal sakte."
        ))
        return result

    # Universe available — remaining + strand breakdown
    total = len(universe)
    covered_in_universe = [u for u in universe if u["id"] in covered_ids]
    remaining = [
        {"slo_code": u["slo_code"], "slo_text": u["slo_text"], "strand": u["strand"]}
        for u in universe if u["id"] not in covered_ids
    ]

    strands: dict = {}
    for u in universe:
        key = u["strand"] or "(no strand)"
        s = strands.setdefault(key, {"strand": u["strand"], "total": 0,
                                     "covered": 0, "covered_list": [], "remaining_list": []})
        s["total"] += 1
        entry = {"slo_code": u["slo_code"], "slo_text": u["slo_text"]}
        if u["id"] in covered_ids:
            s["covered"] += 1
            s["covered_list"].append(entry)
        else:
            s["remaining_list"].append(entry)

    result.update({
        "universe_available": True,
        "total_slos": total,
        "covered_in_universe": len(covered_in_universe),
        "coverage_percent": round(len(covered_in_universe) / total * 100),
        "remaining": remaining,
        "strands": sorted(strands.values(), key=lambda s: s["strand"] or ""),
    })
    return result


def _no_universe(message: str) -> dict:
    """Universe na ho to graceful shape — remaining/strands khali, covered-only."""
    return {
        "universe_available": False,
        "universe_message": message,
        "total_slos": 0,
        "covered_in_universe": 0,
        "coverage_percent": None,
        "remaining": [],
        "strands": [],
    }
