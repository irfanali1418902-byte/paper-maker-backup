"""SLO Health — Marhala 2 Hissa C.

Dono taraf ka gap ek jagah:
  (a) SLO jinke paas koi (published) question nahi — strand-wise + bloom-wise.
  (b) (published) questions jinke paas koi SLO tag nahi — class/subject-wise.
Plus per class/subject health line, aur "SLO import baqi" (syllabus ke woh
grade/subject jinka SLO define hi nahi).

General hai — SAARI classes/subjects/strands ke liye chalta hai; koi class/
subject/strand hardcode nahi. Live compute (JOIN), snapshot NAHI (coverage/
shortfall jaisa).

Ahem faisle (tay-shuda):
  * Covered = SLO ke paas >=1 linked PUBLISHED question. draft/archived shumar NAHI.
  * Questions par class column nahi hoti — grade `syllabus_topic` se aata hai; jis
    question ka topic-link nahi uska grade na-maloom -> "(class na-maloom)" bucket.
  * Bloom NULL wale SLO -> "(bloom na-maloom)" bucket (silently REMEMBER nahi maante).
  * Case normalize har jagah: class, subject, bloom.
  * import_pending = syllabus (`list_distinct_subject_grade`) ke woh combos jinka
    SLO group nahi.
"""

from typing import Optional

from app.core.text_norm import normalize_class, normalize_subject
from app.repositories import (
    question_slo_repository,
    questions_repository,
    slo_repository,
    syllabus_repository,
)

# Pseudo-labels — bucket ke naam khud "class"/"strand"/"bloom" ki tarah barte hain
# taake filter aur display uniform rahein. na-maloom class ka norm-key iske
# lower-case se banta (normalize_class(_NO_CLASS)) — filter par bhi match ho jaye.
_NO_CLASS = "(class na-maloom)"
_NO_STRAND = "(no strand)"
_NO_BLOOM = "(bloom na-maloom)"

DRAFT_NOTE = "Sirf published questions shumar hote hain — draft/archived nahi ginte."


def _norm_bloom(bloom: Optional[str]) -> str:
    return (bloom or "").strip().lower()


def _class_key(grade: Optional[str]) -> str:
    """Question ka grade -> class norm-key. Khali grade -> na-maloom bucket."""
    if grade and str(grade).strip():
        return normalize_class(grade)
    return normalize_class(_NO_CLASS)


def _class_label(grade: Optional[str]) -> str:
    return grade if (grade and str(grade).strip()) else _NO_CLASS


def compute_health(
    class_filter: Optional[str] = None,
    subject_filter: Optional[str] = None,
) -> dict:
    """SLO health dict. Filter (class/subject) diye jayen to sections un tak
    narrow hote hain; dropdown lists (classes/subjects) hamesha POORE (unfiltered)
    taake teacher wapas kisi aur class par ja sake."""
    slos = slo_repository.list_all()
    covered_ids = question_slo_repository.slo_ids_with_published_questions()
    questions = questions_repository.list_published_with_grade_and_tag()
    syllabus_combos = syllabus_repository.list_distinct_subject_grade()

    # ---- SLO side: (norm_class, norm_subject) -> {display, slos:[...]} ----
    slo_groups: dict = {}
    for s in slos:
        key = (normalize_class(s["class"]), normalize_subject(s["subject"]))
        g = slo_groups.setdefault(key, {"class": s["class"], "subject": s["subject"], "slos": []})
        g["slos"].append(s)

    # ---- Question side: (norm_class, norm_subject) -> {display, total, tagged} ----
    q_groups: dict = {}
    for q in questions:
        key = (_class_key(q.get("grade")), normalize_subject(q["subject"]))
        g = q_groups.setdefault(key, {"class": _class_label(q.get("grade")),
                                      "subject": q["subject"], "total": 0, "tagged": 0})
        g["total"] += 1
        if q["is_tagged"]:
            g["tagged"] += 1

    # ---- dropdown labels (POORE data se, filter se pehle) ----
    class_display: dict = {}
    subject_display: dict = {}
    for (nc, ns), g in list(slo_groups.items()) + list(q_groups.items()):
        class_display.setdefault(nc, g["class"])
        subject_display.setdefault(ns, g["subject"])
    for combo in syllabus_combos:
        nc = _class_key(combo["grade"])
        ns = normalize_subject(combo["subject"])
        class_display.setdefault(nc, _class_label(combo["grade"]))
        if combo["subject"]:
            subject_display.setdefault(ns, combo["subject"])

    # ---- Part 1: har class/subject ki health line ----
    health_lines = []
    for key in set(slo_groups) | set(q_groups):
        sg, qg = slo_groups.get(key), q_groups.get(key)
        slo_list = sg["slos"] if sg else []
        slo_count = len(slo_list)
        covered = sum(1 for s in slo_list if s["id"] in covered_ids)
        q_count = qg["total"] if qg else 0
        tagged = qg["tagged"] if qg else 0
        health_lines.append({
            "class": (sg or qg)["class"],
            "subject": (sg or qg)["subject"],
            "norm_class": key[0],
            "norm_subject": key[1],
            "slo_count": slo_count,
            "covered_count": covered,
            "uncovered_count": slo_count - covered,
            "coverage_percent": round(covered / slo_count * 100) if slo_count else None,
            "question_count": q_count,
            "tagged_count": tagged,
            "untagged_count": q_count - tagged,
            "has_slo": slo_count > 0,
        })

    # ---- Part 2: SLO jinke paas koi question nahi (strand-wise + bloom-wise) ----
    slos_without_question = []
    for key, sg in slo_groups.items():
        uncovered = [s for s in sg["slos"] if s["id"] not in covered_ids]
        if not uncovered:
            continue
        by_strand: dict = {}
        by_bloom: dict = {}
        for s in uncovered:
            strand = s.get("strand") or _NO_STRAND
            bloom = _norm_bloom(s["bloom_level"]) or _NO_BLOOM
            by_strand.setdefault(strand, []).append(
                {"slo_code": s["slo_code"], "slo_text": s["slo_text"], "bloom": bloom}
            )
            by_bloom[bloom] = by_bloom.get(bloom, 0) + 1
        slos_without_question.append({
            "class": sg["class"],
            "subject": sg["subject"],
            "norm_class": key[0],
            "norm_subject": key[1],
            "total": len(uncovered),
            "by_strand": sorted(
                ({"strand": k, "count": len(v), "slos": v} for k, v in by_strand.items()),
                key=lambda x: x["strand"],
            ),
            "by_bloom": sorted(
                ({"bloom": k, "count": c} for k, c in by_bloom.items()),
                key=lambda x: x["bloom"],
            ),
        })

    # ---- Part 3: questions jinke paas SLO tag nahi (class/subject-wise ginti) ----
    untagged_questions = []
    for key, qg in q_groups.items():
        untagged = qg["total"] - qg["tagged"]
        if untagged <= 0:
            continue
        untagged_questions.append({
            "class": qg["class"],
            "subject": qg["subject"],
            "norm_class": key[0],
            "norm_subject": key[1],
            "count": untagged,
        })

    # ---- Part 4: SLO import baqi (syllabus combo jinka SLO group nahi) ----
    slo_keys = set(slo_groups)
    import_pending = []
    seen_pending: set = set()
    for combo in syllabus_combos:
        key = (_class_key(combo["grade"]), normalize_subject(combo["subject"]))
        if key in slo_keys or key in seen_pending:
            continue
        seen_pending.add(key)
        import_pending.append({
            "grade": combo["grade"],
            "subject": combo["subject"],
            "norm_class": key[0],
            "norm_subject": key[1],
        })

    # ---- filter (dropdown labels chhoR kar baaqi sab) ----
    cf = normalize_class(class_filter) if (class_filter and class_filter.strip()) else None
    sf = normalize_subject(subject_filter) if (subject_filter and subject_filter.strip()) else None
    if cf is not None or sf is not None:
        def _keep(row: dict) -> bool:
            return (cf is None or row["norm_class"] == cf) and \
                   (sf is None or row["norm_subject"] == sf)
        health_lines = [r for r in health_lines if _keep(r)]
        slos_without_question = [r for r in slos_without_question if _keep(r)]
        untagged_questions = [r for r in untagged_questions if _keep(r)]
        import_pending = [r for r in import_pending if _keep(r)]

    return {
        "draft_note": DRAFT_NOTE,
        "classes": sorted(class_display.values()),
        "subjects": sorted(subject_display.values()),
        "health_lines": sorted(health_lines, key=lambda r: (r["class"] or "", r["subject"] or "")),
        "slos_without_question": sorted(
            slos_without_question, key=lambda r: (r["class"] or "", r["subject"] or "")
        ),
        "untagged_questions": sorted(
            untagged_questions, key=lambda r: (r["class"] or "", r["subject"] or "")
        ),
        "import_pending": sorted(
            import_pending, key=lambda r: ((r["grade"] or ""), (r["subject"] or ""))
        ),
    }
