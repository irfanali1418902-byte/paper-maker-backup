"""Taqseem (SLO -> exam plan) business logic. Hissa 2.

Ek (class, subject) ke SLO ko N exams mein resolve karta hai. N global hai
(school_settings.exam_count). exam_no 0 / NULL / >N = Unassigned bucket."""

from app.repositories import slo_exam_plan_repository, slo_repository
from app.services import settings_service


class SloNotFoundError(Exception):
    """Move-target SLO id DB mein maujood nahi (route ise 404 banata hai)."""


def _exam_count() -> int:
    settings = settings_service.get_settings()
    n = settings.get("exam_count") if isinstance(settings, dict) else getattr(settings, "exam_count", None)
    try:
        n = int(n)
    except (TypeError, ValueError):
        n = 8
    return n if n >= 1 else 8


def exam_count() -> int:
    """Global N (school_settings.exam_count). Public wrapper — coverage route jaisi
    jagahon ke liye jahan exam_no ki range (1..N) validate karni hoti hai."""
    return _exam_count()


def get_plan(class_name: str, subject: str) -> dict:
    """Resolved taqseem: har exam (1..N) ke SLO + Unassigned bucket.

    has_plan = koi assignment row maujood (yani generate chal chuka). exam_no NULL
    (plan-less), 0 (Unassigned), ya >N (N ghatne se nikla) — sab Unassigned mein.
    """
    rows = slo_exam_plan_repository.list_resolved(class_name, subject)
    n = _exam_count()

    has_plan = any(r["exam_no"] is not None for r in rows)
    exams = [{"exam_no": i, "slos": []} for i in range(1, n + 1)]
    unassigned: list = []

    for r in rows:
        e = r["exam_no"]
        if e is not None and 1 <= e <= n:
            exams[e - 1]["slos"].append(r)
        else:
            unassigned.append(r)

    return {
        "class_name": class_name,
        "subject": subject,
        "exam_count": n,
        "has_plan": has_plan,
        "total": len(rows),
        "exams": exams,
        "unassigned": unassigned,
    }


def generate_plan(class_name: str, subject: str) -> dict:
    """Auto-taqseem: us (class, subject) ke SLO ko N exams mein baraabar baant do.

    Usool:
    - sequence NULL wale SLO kisi exam mein NAHI jaate — exam_no 0 (Unassigned) rehte
      hain (in ki asal teaching-tarteeb maloom nahi, is liye auto-split se bahar).
    - sequence-wale SLO **sequence ASC** par: total = un ki ginti, base = total//N,
      rem = total%N. Pehle `rem` exams ko base+1, baaqi ko base SLO milte hain.
    - Poora regenerate: har SLO ka assignment overwrite hota hai. `overwritten` =
      kitne SLO ka pehle se plan row tha (frontend confirm/summary ke liye).
    """
    rows = slo_exam_plan_repository.list_resolved(class_name, subject)
    n = _exam_count()

    # LEFT JOIN: exam_no None => is SLO ka abhi koi plan row nahi. Non-None = pehle
    # se assign (0/1..N sab), yani regenerate use overwrite karega.
    overwritten = sum(1 for r in rows if r["exam_no"] is not None)

    # list_resolved exam_no ke hisaab se sorted deta hai; split ke liye khaalis
    # sequence chahiye, is liye yahan dobara sort (tie par slo_code — deterministic).
    assigned = sorted(
        (r for r in rows if r["sequence"] is not None),
        key=lambda r: (r["sequence"], r["slo_code"]),
    )
    unassigned = [r for r in rows if r["sequence"] is None]

    total = len(assigned)
    base, rem = divmod(total, n)
    sizes = [base + 1 if i < rem else base for i in range(n)]

    plan_rows: list = []
    idx = 0
    for exam_no, size in enumerate(sizes, start=1):
        for position, r in enumerate(assigned[idx:idx + size], start=1):
            plan_rows.append({"slo_id": r["slo_id"], "exam_no": exam_no, "position": position})
        idx += size

    # NULL-sequence SLO: sab exam_no 0 (Unassigned), position None.
    for r in unassigned:
        plan_rows.append({"slo_id": r["slo_id"], "exam_no": 0, "position": None})

    slo_exam_plan_repository.overwrite_assignments(plan_rows)

    return {
        "class_name": class_name,
        "subject": subject,
        "exam_count": n,
        "total": len(rows),
        "assigned": total,
        "unassigned": len(unassigned),
        "overwritten": overwritten,
    }


def move_slo(slo_id: str, exam_no: int, position=None) -> dict:
    """Ek SLO ka assignment set karo (per-move, drag/drop ke liye).

    - exam_no 0 = Unassigned (valid). Range: 0 <= exam_no <= N (N global).
      Range se bahar par ValueError (route → 400).
    - slo_id maujood na ho to SloNotFoundError (route → 404).
    - position optional: diya jaye to exam ke andar us jagah, warna None (get_plan
      sequence par fall back karta hai). Sirf isi SLO ki row upsert hoti hai — baaqi
      siblings ki positions nahi chhedi jaatin (re-pack Tukda 4/page ka kaam).
    """
    n = _exam_count()
    if exam_no < 0 or exam_no > n:
        raise ValueError(f"exam_no 0 se {n} ke darmiyaan hona chahiye (0 = Unassigned).")
    if slo_repository.find_by_id(slo_id) is None:
        raise SloNotFoundError(slo_id)

    slo_exam_plan_repository.overwrite_assignments(
        [{"slo_id": slo_id, "exam_no": exam_no, "position": position}]
    )
    return {"slo_id": slo_id, "exam_no": exam_no, "position": position}
