"""Hafta-war coverage -- planned (topic_week_plan) vs covered (papers). R7 Marhala 3.

`coverage_service` ka aaina, magar EK BUNYADI FARQ ke saath jo naap kar nikla aur
jise samjhe baghair ye file parhna gumraah karega.

    SLO KI TARAF:  covered ka apna exam hota hai. `papers.exam_no` mojood hai, to
                   "exam 3 ke paper ne exam 2 ka SLO cover kiya" ek asal sawal hai
                   aur `covered_pairs_all_exams` (exam_no, slo_id) jodi deti hai.

    TOPIC KI TARAF: `papers` mein `week_no` column HAI HI NAHI (naapa 2026-08-23).
                   To "hafta 3 ke paper" jaisi koi cheez wujood mein nahi. covered
                   ek GLOBAL set hai: topic kisi bhi paper mein aa gaya to covered.

Irfan ka faisla (2026-08-23): yehi tareef durust hai, kyunke jis sawal ka jawab
teacher dhoondh raha hai wo hai *"jo maine hafta 3 mein parhaya, us ka imtihan kabhi
liya bhi?"* -- na ke "hafta 3 ke paper mein aaya?". Doosri tareef (hafta -> exam
mapping) ke liye repo mein data hai hi nahi: na `school_settings` mein week->exam hai,
na session ka calendar. Wo apna alag faisla aur apna alag scope hai.

`_assemble_coverage` IS FILE NE CHHUA NAHI. Spec sec 8 ne usay parameterize karne ko
kaha tha; wajah ke saath us se hata gaya -- tafseel `coverage_service.bucket_row` ke
docstring mein. Wahan se sirf `bucket_row` (aath lines) share hoti hai.
"""

from app.repositories import papers_repository, topic_week_plan_repository
from app.services import coverage_service, topic_week_service


def coverage(subject: str, grade: str) -> dict:
    """Har hafte (1..N) + Unassigned(0) ka planned vs covered.

    Bucketing ka rule bilkul `topic_week_service.get_plan()` jaisa hai -- week_no
    NULL / 0 / >N sab Unassigned. Dono ek hi tarah bucket karein, warna page ka
    board aur report alag ginti dikhayenge.

    UNASSIGNED KA covered YAHAN ASAL GINTI HAI, ZABARDASTI 0 NAHI -- aur yehi
    `coverage_summary` se doosra farq hai. Wahan Unassigned SLO ka covered 0 forced
    hai kyunke "kisi exam mein nahi rakha" ka matlab hai us exam ke liye cover ho hi
    nahi sakta. Yahan covered ka koi hafta hai hi nahi (upar dekhein), to "jis topic
    ka hafta tay nahi magar paper mein aa chuka" ek asal aur kaam ki soorat hai --
    usay 0 dikhana teacher se maloomat chupana hoga.
    """
    n = topic_week_service.week_count()

    resolved = topic_week_plan_repository.list_resolved(subject, grade)
    planned_by_week: dict = {i: set() for i in range(0, n + 1)}
    for r in resolved:
        w = r["week_no"]
        bucket = w if (w is not None and 1 <= w <= n) else 0
        planned_by_week[bucket].add(r["syllabus_topic_id"])

    # Ek query, poore subject+grade ke liye -- per-week query ki zaroorat nahi
    # kyunke covered ka koi hafta hai hi nahi.
    pairs = papers_repository.covered_topic_pairs(subject, grade)
    covered_ids = {p["syllabus_topic_id"] for p in pairs}
    paper_map: dict = {}
    for p in pairs:
        paper_map.setdefault(p["syllabus_topic_id"], []).append(p["paper_id"])

    weeks: list = []
    for i in range(1, n + 1):
        planned_ids = planned_by_week[i]
        row = coverage_service.bucket_row(planned_ids, len(planned_ids & covered_ids))
        weeks.append({"week_no": i, **row})

    unassigned_ids = planned_by_week[0]
    weeks.append({
        "week_no": 0,
        **coverage_service.bucket_row(
            unassigned_ids, len(unassigned_ids & covered_ids), unassigned=True
        ),
    })

    # Total poore (subject, grade) ka hai -- weeks ke jorr ka nahi. Dono barabar hi
    # hote hain (har topic theek ek bucket mein jata hai), magar isay `resolved` se
    # nikalna is barabari par bharosa nahi karta.
    all_planned = {r["syllabus_topic_id"] for r in resolved}
    covered_total = len(all_planned & covered_ids)

    return {
        "subject": subject,
        "grade": grade,
        "week_count": n,
        "total_topics": len(all_planned),
        "covered_topics": covered_total,
        "coverage_percent": (
            round(covered_total / len(all_planned) * 100) if all_planned else None
        ),
        "weeks": weeks,
        "paper_map": paper_map,
    }
