"""Exam-wise SLO coverage — Marhala 3.

Taqseem (slo_exam_plan) kehta hai kaunsa SLO kis exam mein hona chahiye (planned).
Papers (papers.exam_no + question_slo links) kehte hain waqai kya cover hua. Ye
service dono ko milata hai: har exam ke liye planned vs covered, remaining, strand
breakdown. Sab LIVE compute — koi stored snapshot nahi (plan/paper baad mein badle
to report khud sahi rahe).

Core `_assemble_coverage` DB-FREE hai (sirf planned + covered_ids + papers leta hai)
taake Hissa 4 (Blueprint tajweez) isay draft question_ids se nikale covered_ids ke
saath dobara istemal kar sake — bina refactor. exam_coverage/coverage_summary DB se
data la kar core ko feed karte hain.
"""

from app.repositories import papers_repository, slo_exam_plan_repository
from app.services import settings_service


def _exam_count() -> int:
    """N = school_settings.exam_count (>=1, warna 8). taqseem_service._exam_count ka
    hi rule — dono ek hi N par chalen (drift na ho)."""
    settings = settings_service.get_settings()
    n = settings.get("exam_count") if isinstance(settings, dict) else getattr(settings, "exam_count", None)
    try:
        n = int(n)
    except (TypeError, ValueError):
        n = 8
    return n if n >= 1 else 8


def _slo_brief(s: dict) -> dict:
    """SLO row se sirf UI-zaroori fields (report payload halka rakho)."""
    return {
        "slo_id": s["slo_id"],
        "slo_code": s.get("slo_code"),
        "slo_text": s.get("slo_text"),
        "strand": s.get("strand"),
    }


def _assemble_coverage(planned: list, covered_ids: set, paper_map: dict) -> dict:
    """PURE core — koi DB query nahi. Coverage math + shape banata hai.

    planned      : is exam ke universe SLO (list_planned se) — poore slo fields.
    covered_ids  : jo slo_id waqai cover ho gaye unka SET (membership-test).
    paper_map    : {slo_id: [paper_id, ...]} — kaunsa SLO kin papers mein aaya
                   (slo-health drill-down). Har covered SLO ke brief mein paper_ids
                   chip jaate. Hissa 4 draft-reuse mein {} de sakte (koi saved paper
                   nahi) — result shape phir bhi wahi.

    total == 0 (is exam ke liye koi SLO planned nahi) => coverage_percent None
    (slo_coverage_service jaisa — 0/0 ko 0% nahi dikhate)."""
    total = len(planned)
    covered = [s for s in planned if s["slo_id"] in covered_ids]
    remaining = [s for s in planned if s["slo_id"] not in covered_ids]

    strands: dict = {}
    for s in planned:
        key = s.get("strand") or "(no strand)"
        st = strands.setdefault(key, {"strand": s.get("strand"), "total": 0, "covered": 0})
        st["total"] += 1
        if s["slo_id"] in covered_ids:
            st["covered"] += 1

    return {
        "total_slos": total,
        "covered_slos": len(covered),
        "coverage_percent": round(len(covered) / total * 100) if total else None,
        "covered": [{**_slo_brief(s), "paper_ids": paper_map.get(s["slo_id"], [])} for s in covered],
        "remaining": [_slo_brief(s) for s in remaining],
        "strands": sorted(strands.values(), key=lambda x: x["strand"] or ""),
    }


def exam_coverage(class_name: str, subject: str, exam_no: int) -> dict:
    """Ek exam ka mukammal coverage. DB se planned/covered/papers la kar core ko deta.
    covered_slo_pairs subject+class-filtered hai (doosre subject/class leak nahi)."""
    planned = slo_exam_plan_repository.list_planned(class_name, subject, exam_no)

    # (slo_id, paper_id) jodiyan -> covered_ids SET (membership) + paper_map
    # {slo_id: [paper_ids]} (drill-down) — dono ek hi query se.
    pairs = papers_repository.covered_slo_pairs(exam_no, subject, class_name)
    covered_ids = {row["slo_id"] for row in pairs}
    paper_map: dict = {}
    for row in pairs:
        paper_map.setdefault(row["slo_id"], []).append(row["paper_id"])

    result = _assemble_coverage(planned, covered_ids, paper_map)

    # list_by_exam ALAG — id->title map taake UI paper_id ki jagah naam dikhaye.
    paper_titles = {
        p["id"]: (p.get("paper_title") or "(Untitled)")
        for p in papers_repository.list_by_exam(exam_no, subject, class_name)
    }
    result.update({
        "class": class_name, "subject": subject, "exam_no": exam_no,
        "paper_titles": paper_titles,
    })
    return result


def coverage_summary(class_name: str, subject: str) -> dict:
    """Saare exams (1..N) + Unassigned(0) ka ek-nazar summary: har exam ke planned vs
    covered count. taqseem jaisa bucketing (exam_no NULL/0/>N => Unassigned).

    Efficiency: covered_pairs_all_exams() EK query mein saari (exam, slo) jodi laata
    hai, phir exam_no par bucket — N alag covered_slo_pairs calls se bachne ko.

    Unassigned (exam 0): planned count dikhta hai (kitne SLO abhi kisi exam mein nahi),
    magar covered HAMESHA 0 — Unassigned SLO ko exam-sense mein 'cover' nahi karte."""
    n = _exam_count()

    # planned SLO ids ko exam-bucket mein daalo (taqseem rule: 1..N warna Unassigned=0)
    resolved = slo_exam_plan_repository.list_resolved(class_name, subject)
    planned_by_exam: dict = {i: set() for i in range(0, n + 1)}
    for r in resolved:
        e = r["exam_no"]
        bucket = e if (e is not None and 1 <= e <= n) else 0
        planned_by_exam[bucket].add(r["slo_id"])

    # covered slo_id ko exam_no par bucket (ek hi query)
    covered_by_exam: dict = {}
    for pair in papers_repository.covered_pairs_all_exams(subject, class_name):
        covered_by_exam.setdefault(pair["exam_no"], set()).add(pair["slo_id"])

    exams: list = []
    for i in range(1, n + 1):
        planned_ids = planned_by_exam[i]
        covered_count = len(planned_ids & covered_by_exam.get(i, set()))
        exams.append(_summary_row(i, planned_ids, covered_count))

    # Unassigned column aakhir mein — covered forced 0
    unassigned_ids = planned_by_exam[0]
    exams.append(_summary_row(0, unassigned_ids, 0, unassigned=True))

    return {
        "class": class_name,
        "subject": subject,
        "exam_count": n,
        "exams": exams,
    }


def _summary_row(exam_no: int, planned_ids: set, covered_count: int, unassigned: bool = False) -> dict:
    planned = len(planned_ids)
    return {
        "exam_no": exam_no,
        "unassigned": unassigned,
        "planned": planned,
        "covered": covered_count,
        "coverage_percent": round(covered_count / planned * 100) if planned else None,
    }
