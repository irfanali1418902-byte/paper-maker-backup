"""Hafta-war plan (syllabus topic -> hafta) business logic. R7 Marhala 1.

Ek (subject, grade) ke topics ko N hafton mein resolve karta hai. N global hai
(school_settings.week_count). week_no 0 / NULL / >N = Unassigned bucket.

`taqseem_service` ka aaina -- usool wahan se liye gaye hain taake dono plan ek jaise
chalein. Farq sirf itna hai ke yahan **auto-generate nahi hai**: Irfan ka faisla hai
ke plan Excel se bharega (docs/TOPIC_WEEK_PLAN.md §0), aur andhi taqseem ye nahi
jaanti kaunsa topic bhaari hai.
"""

from app.repositories import topic_week_plan_repository
from app.services import settings_service

WEEK_COUNT_DEFAULT = 36


class TopicNotFoundError(Exception):
    """Move-target topic id DB mein maujood nahi (route ise 404 banata hai)."""


def _week_count() -> int:
    """N = school_settings.week_count (>=1, warna 36). Bilkul taqseem_service ke
    _exam_count() ka usool -- dono ek hi tarah galat/khali value sambhalein.

    `week_count` abhi `SchoolSettings` model mein nahi hai (sirf DB column), is liye
    settings dict mein na hone ki soorat bilkul mumkin hai -- .get() usi ke liye."""
    settings = settings_service.get_settings()
    if isinstance(settings, dict):
        n = settings.get("week_count")
    else:
        n = getattr(settings, "week_count", None)
    try:
        n = int(n)
    except (TypeError, ValueError):
        n = WEEK_COUNT_DEFAULT
    return n if n >= 1 else WEEK_COUNT_DEFAULT


def get_plan(subject: str, grade: str) -> dict:
    """Resolved plan: har hafta (1..N) ke topics + Unassigned bucket.

    has_plan = koi assignment row maujood. week_no NULL (plan-less), 0 (Unassigned),
    ya >N (N ghatne se nikla) -- sab Unassigned mein. Yehi taqseem_service.get_plan()
    ka bartao hai."""
    rows = topic_week_plan_repository.list_resolved(subject, grade)
    n = _week_count()

    has_plan = any(r["week_no"] is not None for r in rows)
    weeks = [{"week_no": i, "topics": []} for i in range(1, n + 1)]
    unassigned: list = []

    for r in rows:
        w = r["week_no"]
        if w is not None and 1 <= w <= n:
            weeks[w - 1]["topics"].append(r)
        else:
            unassigned.append(r)

    return {
        "subject": subject,
        "grade": grade,
        "week_count": n,
        "has_plan": has_plan,
        "total": len(rows),
        "weeks": weeks,
        "unassigned": unassigned,
    }


def move_topic(topic_id: str, week_no: int) -> dict:
    """Ek topic ka hafta badlo (ya pehli dafa set karo).

    week_no 0 = Unassigned (row rehti hai, magar bucket ke bahar). N se bara ya
    manfi qubool NAHI -- ValueError, jise route 400 banata hai (taqseem/move ka
    hi mapping: ValueError -> 400, NotFound -> 404). Ye taqseem ke
    move se sakht hai jaan-boojh kar: wahan >N purane plan se nikal sakta hai,
    yahan seedha teacher ka input hai aur chup-chaap Unassigned mein girana use
    dhoka dega.

    position jaan-boojh kar clear (None): hafta badalne ke baad purani jagah ki
    tarteeb be-maani hai. Marhala 4 ka UI chahe to alag se set kar sakta hai."""
    n = _week_count()
    try:
        week_no = int(week_no)
    except (TypeError, ValueError) as e:
        raise ValueError(f"week_no ginti honi chahiye, mila: {week_no!r}") from e
    if week_no < 0 or week_no > n:
        raise ValueError(f"week_no 0 se {n} ke darmiyan hona chahiye, mila: {week_no}")

    if not topic_week_plan_repository.existing_topic_ids([topic_id]):
        raise TopicNotFoundError(topic_id)

    topic_week_plan_repository.overwrite_assignments(
        [{"syllabus_topic_id": topic_id, "week_no": week_no, "position": None}]
    )
    return {"syllabus_topic_id": topic_id, "week_no": week_no}
