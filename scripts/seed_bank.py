"""Build a starter question bank for one subject+grade from its syllabus.

ROADMAP feature #3. The problem it solves, measured on 2026-08-21:

    syllabus_topics covers 8 subject+grade pairs (310 topics)
    only 2 of those 8 have a single question in the bank
    fill-blank and essay are ZERO across the whole bank

So a teacher can load a syllabus and still not be able to generate a paper.
This walks a syllabus's topics and generates a spread of question types for
each one, going through the same service layer the /api/generate-questions
route uses -- no raw SQL, no bypassed validation.

Usage:
    # plan only, nothing written, no AI calls, no cost:
    python -m scripts.seed_bank --subject Mathematics --grade "Grade 4"

    # actually seed:
    python -m scripts.seed_bank --subject Mathematics --grade "Grade 4" --write

DRY RUN IS THE DEFAULT. --write is what spends money and touches the bank,
because one careless command here is 310 topics' worth of AI calls.

Already-seeded topics are skipped, so a re-run tops up rather than
duplicating. Pass --include-seeded to override that.

Rate limits: there is a --delay between topics, and the run stops itself after
a few consecutive rate-limit failures rather than burning the rest of the list
on calls that cannot succeed. Because seeded topics are skipped, recovering is
just running the same command again later.

CHETAWNI -- pehle syllabus naap lo. 2026-08-21 ko `syllabus_topics` ki paanch
rows (Geography G8, Science G7, Math G4/G5/G6) bilkul ek jaisi nikleen: wohi 11
Grade-4 maths topics. Un par seed karne se "Geography" ke naam par hisaab ke 44
sawal ban gaye jo delete karne pare. Ye script topic ka title waise hi maan leti
hai jaisa `syllabus_topics` mein likha hai -- wo galat ho to sawal bhi galat
banenge, aur script ko pata nahi chalega.
"""

import argparse
import time
from collections import Counter

from app.core.database import init_db
from app.schemas.requests import GenerateQuestionsRequest
from app.services import question_service, syllabus_service

#: Har topic ke darmiyan wafqa. YAHAN RETRY NAHI HAI, aur jaan-boojh kar nahi hai:
#: `ai_service._with_retry` pehle se 429/503/529 par 3 koshishein karta hai
#: (backoff 2s, 4s). Us ke ooper apni retry lagana un koshishon ko zarb de dega.
#: Jo cheez wahan NAHI hai wo yeh wafqa hai — free-tier ka quota per-minute hota
#: hai, aur 6 second us ke reset ke liye kaafi nahi. Naapa gaya 2026-08-21:
#: 44 calls tez tez chalne ke baad agli poori run (11 topics) 429 par zaya gayi.
DEFAULT_DELAY_SECONDS = 4.0

#: print() ke andar escape likhne se bacha jata hai.
NEWLINE = chr(10)

#: Itni musalsal rate-limit nakaamiyon ke baad run rok di jati hai. Us Science
#: run mein 11 ke 11 topics fail hue — har ek ne 3 koshishein ki, yani 33 be-faida
#: calls. Quota khatam ho to agla topic bhi nahi chalega; rukna hi theek hai.
MAX_CONSECUTIVE_RATE_LIMITS = 3

#: Mirrors schemas.requests.QuestionType. Kept as a plain tuple so the script
#: can validate --types itself and fail before spending anything on AI.
VALID_TYPES = (
    "multiple-choice",
    "true-false",
    "short-answer",
    "fill-blank",
    "essay",
)

#: Default spread deliberately leads with the two types the bank has none of.
#: A starter bank that is 100% short-answer (which is what English already is)
#: cannot fill a sections-mode paper.
DEFAULT_TYPES = ("multiple-choice", "short-answer", "fill-blank", "essay")

#: PER-GRADE MARKS KA PAIMANA. AI har sawal ke apne marks tajweez karta hai aur wo
#: kuch grades ke liye ghalat hote hain -- Pre Year 1 par 2026-09-06 ki run mein 24 ke
#: 24 sawal 3/4/6/7 marks par aaye, jab ke us grade ka har sawal 1 mark ka hai.
#: **Ye TEESRI dafa tha.** Har dafa ka hal ek `UPDATE` tha jo kisi ko YAAD rakhna parta
#: tha; ab wo qaida yahan hai aur persist se PEHLE lagta hai.
#:
#: WARNING -- IS MAP MEIN SIRF WO GRADES HAIN JIN KA PAIMANA DB SE NAAPA GAYA.
#: 2026-09-06 ko poora bank naapa gaya:
#:
#:     Pre Year 1   369 sawal, SAB marks=1        <- qaida saaf hai
#:     Pre Year 2   348 sawal, marks 1..7 phaila  <- koi qaida nahi
#:     Pre Year 3   348 sawal, marks 1..7 phaila  <- koi qaida nahi
#:     Grade 4       43 sawal, marks 1..8 phaila  <- koi qaida nahi
#:
#: Yani "pre-school ka matlab 1 mark" SACH NAHI HAI -- sirf PY1 us par hai, aur PY2/PY3
#: kabhi normalise nahi kiye gaye. Unhein bhi karna chahiye ya nahi, ye ~696 rows ka
#: DATA ka faisla hai aur Irfan ka hai, is script ka nahi: DEFERRED.md D67.
#: YAHAN ANDAZA MAT LAGAO -- grade ka paimana NAAP kar hi is map mein daalo.
GRADE_MARKS = {
    "Pre Year 1": 1,
}


def resolve_marks_target(grade: str, override: str) -> int | None:
    """Is run ke liye marks ka hadaf, ya None agar koi qaida na ho.

    `override` CLI se: "auto" (GRADE_MARKS dekho), "keep" (kuch mat karo), ya ek adad.
    """
    if override == "keep":
        return None
    if override == "auto":
        return GRADE_MARKS.get(grade)
    return int(override)


def apply_marks_scale(questions: list[dict], target: int | None) -> int:
    """Har sawal ke marks hadaf par le aata hai. Kitne badle, wo lautata hai.

    Persist se PEHLE chalta hai, taake ghalat qadr bank mein pahunche hi na -- baad ki
    `UPDATE` par bharosa karna hi wo tareeqa tha jo teen dafa nakaam hua.
    """
    if target is None:
        return 0
    changed = 0
    for q in questions:
        if q.get("marks") != target:
            q["marks"] = target
            changed += 1
    return changed


#: Cap on topics per invocation. The biggest syllabus here is 87 topics; at
#: four questions each that is one command turning into 87 AI calls.
DEFAULT_MAX_TOPICS = 10


def parse_types(raw: str) -> list[str]:
    """Splits and validates --types, rejecting unknown names up front."""
    types = [t.strip() for t in raw.split(",") if t.strip()]
    if not types:
        raise SystemExit("--types khali hai.")
    unknown = [t for t in types if t not in VALID_TYPES]
    if unknown:
        raise SystemExit(
            f"Yeh question type(s) mojood nahi: {', '.join(unknown)}.\n"
            f"Chalne wale: {', '.join(VALID_TYPES)}"
        )
    return types


def available_syllabi() -> str:
    """A printable list of loaded subject+grade pairs, for error messages."""
    rows = syllabus_service.list_grades()
    if not rows:
        return "  (koi syllabus load nahi hua)"
    return "\n".join(f"  {r['subject']} / {r['grade']}" for r in rows)


def topic_is_seeded(topic_id: str) -> bool:
    """True if this syllabus topic already has questions in the bank."""
    return bool(question_service.list_questions(syllabus_topic_id=topic_id))


def select_topics(
    subject: str, grade: str, max_topics: int, include_seeded: bool
) -> tuple[list, int]:
    """Returns (topics to seed, how many were skipped as already-seeded)."""
    topics = syllabus_service.list_topics(subject=subject, grade=grade)
    if not topics:
        raise SystemExit(
            f"'{subject}' / '{grade}' ka koi syllabus topic nahi mila.\n"
            f"Mojood syllabi:\n{available_syllabi()}"
        )

    if include_seeded:
        pending, skipped = topics, 0
    else:
        pending = [t for t in topics if not topic_is_seeded(t["id"])]
        skipped = len(topics) - len(pending)

    return pending[:max_topics], skipped


def seed_topic(topic: dict, args) -> tuple[list[str], list[dict]]:
    """Generates and persists one topic's questions.

    Returns (saved ids, the raw AI dicts, kitne sawalon ke marks theek kiye) --
    the caller needs the raw dicts to count which types actually came back, which
    the saved ids alone cannot say.

    Difficulty comes from the book's own activity tagging via
    `suggested_difficulty` unless --difficulty overrides it -- the same rule
    the API route follows when it is handed a syllabus_topic_id.
    """
    req = GenerateQuestionsRequest(
        subject=topic["subject"],
        topic=topic["subtopic_title"],
        syllabus_topic_id=topic["id"],
        total_questions=args.per_topic,
        bloom_distribution=args.bloom,
        question_types=args.types,
        difficulty=args.difficulty or topic["suggested_difficulty"],
        learning_outcome=topic.get("learning_outcome"),
    )
    ai_questions = question_service.generate_for_topic(req)
    # Marks ka paimana persist se PEHLE -- GRADE_MARKS ka note dekho.
    fixed = apply_marks_scale(ai_questions, resolve_marks_target(args.grade, args.marks))
    return question_service.persist_batch(ai_questions, req), ai_questions, fixed


def is_rate_limited(err: Exception) -> bool:
    """True agar ye nakaami provider ke rate-limit/busy hone se hai.

    Pehle asal HTTP status dekhta hai (wahi tareeqa jo `ai_service._with_retry`
    use karta hai), aur sirf uske na milne par message par girta hai — kyunke
    `_with_retry` apni aakhri exception dobara raise karta hai, to cause-chain
    aam tor par bacha rehta hai.
    """
    status = getattr(getattr(err.__cause__, "response", None), "status_code", None)
    if status is not None:
        return status in (429, 503, 529)
    return "429" in str(err) or "busy/overloaded" in str(err)


def report_types(counts: Counter, requested: list[str]) -> None:
    """Prints what actually landed, and names any requested type the AI never
    produced. This check is the point of the script: asking for essays is not
    the same as getting them, and the bank being short on a type is exactly
    the bug being fixed."""
    print("\nQism ke hisaab se jo waqai bana:")
    for qtype in VALID_TYPES:
        if counts.get(qtype):
            print(f"  {qtype:<18} {counts[qtype]:>4}")

    missing = [t for t in requested if not counts.get(t)]
    if missing:
        print(
            f"\n  WARNING: maanga gaya magar ek bhi nahi aaya: {', '.join(missing)}.\n"
            "  AI ne yeh qismein nazarandaaz kar di hain -- prompt dekhna paregi\n"
            "  (app/services/ai_service.py), sirf dobara chalane se theek nahi hoga."
        )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Seed a starter question bank for one subject+grade from its syllabus"
    )
    parser.add_argument("--subject", required=True, help='e.g. "Mathematics"')
    parser.add_argument("--grade", required=True, help='e.g. "Grade 4"')
    parser.add_argument("--per-topic", type=int, default=4, help="Questions per topic (default 4)")
    parser.add_argument(
        "--types",
        default=",".join(DEFAULT_TYPES),
        help=f"Comma-separated (default: {','.join(DEFAULT_TYPES)})",
    )
    parser.add_argument(
        "--max-topics",
        type=int,
        default=DEFAULT_MAX_TOPICS,
        help=f"Cap on topics this run (default {DEFAULT_MAX_TOPICS})",
    )
    parser.add_argument(
        "--bloom", default="balanced", help="balanced | foundational | advanced (default balanced)"
    )
    parser.add_argument(
        "--difficulty",
        default=None,
        help="Override; default is each topic's own suggested_difficulty",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=DEFAULT_DELAY_SECONDS,
        help=f"Seconds between topics, provider ko saans dene ke liye (default {DEFAULT_DELAY_SECONDS})",
    )
    parser.add_argument(
        "--marks",
        default="auto",
        help=(
            "Marks ka paimana: auto (grade ka apna qaida, GRADE_MARKS), "
            "keep (AI jo de wahi), ya ek adad. Default auto."
        ),
    )
    parser.add_argument(
        "--include-seeded",
        action="store_true",
        help="Also seed topics that already have questions",
    )
    parser.add_argument(
        "--write",
        action="store_true",
        help="Actually call the AI and write to the bank (default is a dry run)",
    )
    args = parser.parse_args()

    if args.per_topic < 1:
        raise SystemExit("--per-topic kam se kam 1 hona chahiye.")
    args.types = parse_types(args.types)

    init_db()

    topics, skipped = select_topics(args.subject, args.grade, args.max_topics, args.include_seeded)

    print(f"{args.subject} / {args.grade}")
    if skipped:
        print(f"  {skipped} topic pehle se seeded hain -- chhode ja rahe hain.")
    if not topics:
        print("  Seed karne ko kuch nahi bacha. (--include-seeded se dobara chala sakte hain.)")
        return

    # ASCII hi rehne dein: Windows console cp1252 par hai aur '×' / '·' wahan
    # '?' ban kar chhapte hain -- naapa gaya 2026-08-21.
    print(f"  {len(topics)} topic x {args.per_topic} sawal = {len(topics) * args.per_topic} sawal")
    print(f"  {len(topics)} AI call, qismein: {', '.join(args.types)}")

    if not args.write:
        print("\nDRY RUN -- kuch nahi likha gaya, koi AI call nahi hui.")
        print("Chalane ke liye wahi command --write ke saath dobara den.")
        return

    counts: Counter = Counter()
    saved_total = 0
    failed: list[tuple[str, str]] = []
    consecutive_rate_limits = 0
    stopped_early = False
    processed = 0
    marks_fixed_total = 0

    for i, topic in enumerate(topics, 1):
        processed = i
        title = topic["subtopic_title"]
        print(f"\n[{i}/{len(topics)}] {title}")
        try:
            saved_ids, ai_questions, fixed = seed_topic(topic, args)
            marks_fixed_total += fixed
        except Exception as e:
            # Ek topic ka fail hona poori run ko nahi girata -- 10 mein se 9
            # ban jayen to woh 9 bank mein rehne chahiyen.
            print(f"  FAIL: {e}")
            failed.append((title, str(e)))

            if is_rate_limited(e):
                consecutive_rate_limits += 1
                if consecutive_rate_limits >= MAX_CONSECUTIVE_RATE_LIMITS:
                    # Quota khatam hai -- baqi topics bhi isi tarah fail honge, aur
                    # har ek teen koshishein karega. Rukna hi behtar hai.
                    stopped_early = True
                    print(
                        f"\n  RUK GAYE: musalsal {consecutive_rate_limits} dafa rate limit."
                        "\n  Provider ka quota khatam lagta hai. Thodi der baad wahi command"
                        "\n  dobara chalayen -- jo topics ban chuke hain wo khud chhut jayenge."
                    )
                    break
            else:
                consecutive_rate_limits = 0
            continue

        consecutive_rate_limits = 0
        for q in ai_questions:
            counts[q.get("question_type")] += 1
        saved_total += len(saved_ids)
        print(f"  saved {len(saved_ids)}")

        # Wafqa sirf topics ke DARMIYAN -- aakhri ke baad rukna bekaar hai.
        if args.delay > 0 and i < len(topics):
            time.sleep(args.delay)

    print(f"\n{'=' * 52}")
    succeeded = processed - len(failed)
    print(f"Kul mehfooz: {saved_total} sawal, {succeeded}/{processed} topics")
    if stopped_early:
        print(f"Run beech mein ruki -- {len(topics) - processed} topics chhu-e bhi nahi gaye.")

    if marks_fixed_total:
        target = resolve_marks_target(args.grade, args.marks)
        print(
            NEWLINE + f"Marks theek kiye: {marks_fixed_total} sawal -> {target}."
            + NEWLINE + "  AI ne is grade ke liye ghalat marks diye thay; paimana"
            + NEWLINE + "  GRADE_MARKS se laga -- persist se PEHLE, UPDATE se nahi."
        )

    if saved_total:
        report_types(counts, args.types)

    if failed:
        print(f"\n{len(failed)} topic fail hue:")
        for title, err in failed:
            print(f"  {title}: {err}")


if __name__ == "__main__":
    main()
