"""Blueprint Bloom guidance — Marhala 2B (Blueprint-page, soft).

Blueprint se paper banate waqt paper ke ASAL Bloom mix ko class-standard se compare
karta hai. Bloom source = har question ka APNA bloom_level (Question Bank wala) — SLO
ka NAHI. Guidance soft hai: kisi Bloom level par 10% se ZYADA farq par hi teacher ko
batao, warna khamosh. App khud kuch adjust NAHI karta — sirf report + do options (UI).

Ahem faisle:
  * bloom_level khali/na-maloom questions ALAG gine jaate hain (`no_bloom`) — report
    mein saaf dikhte hain. Percentages SIRF un questions par jinka bloom set hai
    (`with_bloom`); warna numbers jhoot bolenge.
  * Threshold: |actual% - standard%| STRICTLY > 10 => farq. THEEK 10% par koi warning
    nahi (epsilon se float-noise ignore karte hain).
  * Class -> tier: bloom_standards.get_bloom_suggestion (grade/class string se). Tier
    na mile / with_bloom == 0 -> graceful (available False), crash nahi.
  * Case-insensitive: har bloom lower+strip; standard keys bhi lowercase.
"""

from collections import Counter
from typing import Optional

from app.core import bloom_standards
from app.repositories import questions_repository

# Farq flag karne ki hadd (%). Isse ZYADA (strictly) par hi warning.
SHORTFALL_THRESHOLD_PCT = 10

# Float-noise ke liye chhota margin — 40.0 - 30 == 10.0 ko ">10" na samjho.
_EPSILON = 1e-9

# Taxonomy tarteeb — display order aur valid-bloom check dono ke liye.
_BLOOM_ORDER = ["remember", "understand", "apply", "analyze", "evaluate", "create"]
_RANK = {b: i for i, b in enumerate(_BLOOM_ORDER)}


def _norm(bloom: Optional[str]) -> str:
    """Compare-time normalize — lower + strip. None/khali -> ''."""
    return (bloom or "").strip().lower()


def _compute_mix(questions: list[dict]) -> tuple[Counter, int, int]:
    """Har question ka apna bloom_level gino. Return (counts, with_bloom, no_bloom).

    counts sirf un blooms ki jo taxonomy mein hain; bloom khali ya na-maloom sab
    `no_bloom` mein (alag ginti, distribution se bahar)."""
    counts: Counter = Counter()
    no_bloom = 0
    for q in questions:
        b = _norm(q.get("bloom_level"))
        if b in _RANK:
            counts[b] += 1
        else:
            no_bloom += 1
    with_bloom = sum(counts.values())
    return counts, with_bloom, no_bloom


def _unavailable(message, group, total, with_bloom, no_bloom, subject) -> dict:
    """Graceful shape — standard nahi laga sakte. Counts phir bhi wapas taake teacher
    ko dikhe kitne questions the / kitno ka bloom nahi tha."""
    return {
        "available": False,
        "message": message,
        "group": group,
        "subject": subject,
        "total_questions": total,
        "with_bloom": with_bloom,
        "no_bloom": no_bloom,
        "target_percent": {},
        "rows": [],
        "shortfalls": [],
        "has_shortfall": False,
        "threshold_percent": SHORTFALL_THRESHOLD_PCT,
    }


def compute_bloom_guidance(
    questions: list[dict],
    class_tier: Optional[str],
    subject: Optional[str] = None,
) -> dict:
    """Paper ke questions ka Bloom mix vs class standard — soft guidance dict.

    class_tier: grade/class string jisse standard tier map hota hai.
    subject: diya jaye to under-represented Bloom ke liye bank mein maujood questions
             ki ginti (`bank_available`) bhi bharo — pointer ke liye. None -> ginti skip
             (pure/test-friendly path).
    """
    total = len(questions)
    counts, with_bloom, no_bloom = _compute_mix(questions)

    if not class_tier or not str(class_tier).strip():
        return _unavailable(
            "Class set nahi — Bloom standard nahi laga sakte.",
            None, total, with_bloom, no_bloom, subject,
        )
    target = bloom_standards.get_bloom_suggestion(class_tier)
    if target is None:
        return _unavailable(
            f"'{class_tier}' ke liye Bloom standard define nahi.",
            None, total, with_bloom, no_bloom, subject,
        )
    if with_bloom == 0:
        return _unavailable(
            "Sab questions ka Bloom set nahi — mix compute nahi ho sakta.",
            target["group"], total, with_bloom, no_bloom, subject,
        )

    percents = target["distribution"]  # lowercase keys, e.g. {remember:70, understand:30, ...}
    rows: list[dict] = []
    shortfalls: list[dict] = []
    for b in _BLOOM_ORDER:
        tgt = percents.get(b, 0)
        cnt = counts.get(b, 0)
        if tgt == 0 and cnt == 0:
            continue  # is level ka na standard hai na koi question — chhupa do
        raw_pct = cnt / with_bloom * 100
        diff_raw = raw_pct - tgt
        rows.append({
            "bloom": b,
            "actual_count": cnt,
            "actual_percent": round(raw_pct, 1),
            "target_percent": tgt,
            "diff": round(diff_raw, 1),
        })
        if abs(diff_raw) - SHORTFALL_THRESHOLD_PCT > _EPSILON:
            direction = "under" if diff_raw < 0 else "over"
            sf = {
                "bloom": b,
                "actual_percent": round(raw_pct, 1),
                "target_percent": tgt,
                "gap": round(abs(diff_raw), 1),
                "direction": direction,
            }
            # Sirf under-represented ke liye bank pointer — teacher woh Bloom ke
            # questions add kar ke farq kam kar sakta hai. subject na ho to skip.
            if direction == "under" and subject:
                sf["bank_available"] = len(questions_repository.list_by_filters(
                    subject=subject, bloom_level=b.upper(), status="published",
                ))
            shortfalls.append(sf)

    return {
        "available": True,
        "message": None,
        "group": target["group"],
        "subject": subject,
        "total_questions": total,
        "with_bloom": with_bloom,
        "no_bloom": no_bloom,
        "target_percent": {b: percents[b] for b in _BLOOM_ORDER if percents.get(b, 0) > 0},
        "rows": rows,
        "shortfalls": shortfalls,
        "has_shortfall": bool(shortfalls),
        "threshold_percent": SHORTFALL_THRESHOLD_PCT,
    }
