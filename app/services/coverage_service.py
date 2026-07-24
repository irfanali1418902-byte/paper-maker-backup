"""Exam coverage — Hissa 3.

Ek taqseem-exam ke planned SLO mein se kaunse un papers se cover hue jo USI exam ke
hain. Bunyadi usool: coverage sirf `papers.exam_no == us exam` se ginti hai — doosre
exam ke paper mein aaya SLO is exam ke liye covered NAHI (warna taqseem bemani).

Do entry-points:
- `exam_coverage(class, subject, exam_no)` — ek exam ki tafseel (SLO list + covered
  flag + paper_ids + missing). slo-health istemal karta hai.
- `coverage_summary(class, subject)` — saare exams (+ Unassigned=0) ke sirf counts.
  taqseem.html ke column badges.

`_assemble_coverage` core dono (aur Hissa 4 ka draft-check) share karte hain — planned
list + covered_ids set le kar covered/missing/counts banata hai. Evidence (covered_ids)
kahan se aayi — saved papers ya draft — us par core ko farq nahi padta.
"""

from app.repositories import papers_repository, slo_exam_plan_repository
from app.services import taqseem_service


def _assemble_coverage(planned: list, covered_ids: set, paper_map: dict | None = None) -> dict:
    """Shared core (evidence-agnostic). planned = us exam ke SLO rows (list_planned
    shape); covered_ids = jin SLO ka saboot mila; paper_map = {slo_id: [paper_ids]}
    (saved-path) ya None (draft). Returns planned(covered flag+paper_ids) + missing +
    planned_count/covered_count/coverage_percent."""
    planned_out: list = []
    missing: list = []
    covered_count = 0
    for s in planned:
        sid = s["slo_id"]
        is_cov = sid in covered_ids
        planned_out.append({
            "slo_id": sid,
            "slo_code": s["slo_code"],
            "slo_text": s["slo_text"],
            "strand": s.get("strand"),
            "sequence": s.get("sequence"),
            "covered": is_cov,
            "paper_ids": sorted(paper_map.get(sid, [])) if paper_map else [],
        })
        if is_cov:
            covered_count += 1
        else:
            missing.append({
                "slo_code": s["slo_code"],
                "slo_text": s["slo_text"],
                "strand": s.get("strand"),
                "sequence": s.get("sequence"),
            })
    planned_count = len(planned)
    return {
        "planned_count": planned_count,
        "covered_count": covered_count,
        "coverage_percent": round(covered_count / planned_count * 100) if planned_count else None,
        "planned": planned_out,
        "missing": missing,
    }


def exam_coverage(class_name: str, subject: str, exam_no: int) -> dict:
    """Ek exam (1..N) ki tafseeli coverage. covered SLO ke saath un ke paper_ids;
    saath us exam ke saare papers (title samet, 'kis paper mein aaya' ke liye)."""
    planned = slo_exam_plan_repository.list_planned(class_name, subject, exam_no)
    pairs = papers_repository.covered_slo_pairs(exam_no, subject, class_name)

    covered_ids = {p["slo_id"] for p in pairs}
    paper_map: dict = {}
    for p in pairs:
        paper_map.setdefault(p["slo_id"], []).append(p["paper_id"])

    result = _assemble_coverage(planned, covered_ids, paper_map)
    result.update({
        "class_name": class_name,
        "subject": subject,
        "exam_no": exam_no,
        "papers": papers_repository.list_by_exam(exam_no, subject, class_name),
    })
    return result


def coverage_summary(class_name: str, subject: str) -> dict:
    """Saare exams (1..N) + Unassigned (exam_no 0) ke sirf counts — badges ke liye.

    planned buckets taqseem `get_plan` se (wohi 0/NULL/>N ko Unassigned mein daalne ka
    single source-of-truth). covered ek hi query (`covered_pairs_all_exams`) se, phir
    exam_no par group. Har exam ka covered = us exam ke planned SLO ∩ us exam ke papers
    se cover hue SLO. Unassigned ka covered hamesha 0 (koi paper exam_no 0/NULL par
    coverage nahi deta)."""
    plan = taqseem_service.get_plan(class_name, subject)
    pairs = papers_repository.covered_pairs_all_exams(subject, class_name)

    covered_by_exam: dict = {}
    for p in pairs:
        covered_by_exam.setdefault(p["exam_no"], set()).add(p["slo_id"])

    exams_out: list = []
    for e in plan["exams"]:  # exam_no 1..N
        planned_ids = {s["slo_id"] for s in e["slos"]}
        covered = planned_ids & covered_by_exam.get(e["exam_no"], set())
        exams_out.append({
            "exam_no": e["exam_no"],
            "planned_count": len(planned_ids),
            "covered_count": len(covered),
        })

    # Unassigned column (exam_no 0): planned = unassigned SLO; covered hamesha 0.
    exams_out.append({
        "exam_no": 0,
        "planned_count": len(plan["unassigned"]),
        "covered_count": 0,
    })

    return {
        "class_name": class_name,
        "subject": subject,
        "exam_count": plan["exam_count"],
        "exams": exams_out,
    }
