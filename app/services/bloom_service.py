"""
Bloom's Taxonomy distribution + marks calculation engine.

Distribution percentages yahan se reuse ki gayi hain (Harsha20033 repo se
reverse-engineer kar ke), kyunki ye exact wahi standard split hai jo
original spec document mein bhi diya gaya tha (20/20/20/15/15/10).
"""

import math

BLOOM_LEVELS = {
    "REMEMBER": {
        "name": "Remember",
        "code": "CO1",
        "description": "Recall facts and basic concepts",
    },
    "UNDERSTAND": {
        "name": "Understand",
        "code": "CO2",
        "description": "Explain ideas and concepts",
    },
    "APPLY": {"name": "Apply", "code": "CO3", "description": "Use information in new situations"},
    "ANALYZE": {"name": "Analyze", "code": "CO4", "description": "Draw connections among ideas"},
    "EVALUATE": {"name": "Evaluate", "code": "CO5", "description": "Justify a stand or decision"},
    "CREATE": {"name": "Create", "code": "CO6", "description": "Produce new or original work"},
}


def resolve_distribution_type(requested: str, difficulty: str) -> str:
    """Easy papers default to a foundational (lower-order) Bloom spread so the
    questions actually sit at the difficulty the teacher asked for. An explicit
    non-default choice (foundational/advanced) is left untouched — only the
    neutral 'balanced' default gets steered by difficulty."""
    if difficulty == "easy" and requested == "balanced":
        return "foundational"
    return requested


#: Har distribution ka apna hissa. Ginti in se `ceil` kar ke banti hai — AUR
#: surplus ki katai bhi inhi se hoti hai. Ye do kaam ek jagah rakhna hi asal
#: baat hai: katai ki SIMT hardcode karna wo bug tha jo `advanced` ko ulta
#: chala raha tha (tafseel neeche).
_DISTRIBUTION_SHARES = {
    "balanced": {
        "REMEMBER": 0.20,
        "UNDERSTAND": 0.20,
        "APPLY": 0.20,
        "ANALYZE": 0.15,
        "EVALUATE": 0.15,
        "CREATE": 0.10,
    },
    "foundational": {
        "REMEMBER": 0.40,
        "UNDERSTAND": 0.30,
        "APPLY": 0.20,
        "ANALYZE": 0.10,
        "EVALUATE": 0.0,
        "CREATE": 0.0,
    },
    "advanced": {
        "REMEMBER": 0.10,
        "UNDERSTAND": 0.15,
        "APPLY": 0.20,
        "ANALYZE": 0.25,
        "EVALUATE": 0.20,
        "CREATE": 0.10,
    },
}


def calculate_bloom_distribution(dist_type: str, total_questions: int) -> dict:
    """Given a distribution type (balanced/foundational/advanced) and a total
    question count, returns how many questions should belong to each Bloom
    level."""
    shares = _DISTRIBUTION_SHARES.get(dist_type, _DISTRIBUTION_SHARES["balanced"])
    result = {level: math.ceil(total_questions * share) for level, share in shares.items()}

    # Rounding (ceil on each level) can push the total slightly above
    # total_questions, especially for small counts — trim the surplus off
    # the largest buckets (looping, since one bucket alone may not be
    # enough) so the paper always has exactly the requested number.
    #
    # KATAI DISTRIBUTION KE APNE HISSE SE HOTI HAI — KISI TAY-SHUDA SIMT SE NAHI.
    # Yahan do bug guzar chuke hain, dono ek hi din naape gaye (2026-08-21), aur
    # doosra pehle ki adhoori fix se paida hua tha:
    #
    # BUG 1 — katai neeche se shuru hoti thi. `max(result, key=result.get)` barabar
    # qeematon mein PEHLI key deta hai, aur dict REMEMBER -> CREATE chalta hai.
    # Chhoti ginti par har level `ceil` se 1 hota hai, to:
    #
    #     balanced, 3   ->  ANALYZE 1  EVALUATE 1  CREATE 1   (buniyadi levels saaf)
    #
    # BUG 2 — us ka ilaj `max(reversed(order), ...)` tha, yani "hamesha ooper se
    # kaato". Wo `balanced`/`foundational` par theek chala aur unhi par naapa gaya.
    # `advanced` par kisi ne nahi naapa, aur wahan ye BILKUL ULTA hai — us ka sab
    # se kam-ahem level REMEMBER (10%) hai, jo NEECHE hai:
    #
    #     advanced, 3   ->  REMEMBER 1  UNDERSTAND 1  APPLY 1  (sab se asaan sawal)
    #     advanced, 1   ->  REMEMBER 1
    #
    # Teacher "advanced" maangta tha aur usay buniyadi sawal milte the. Ek hardcoded
    # simt dono ko theek kar hi nahi sakti — `balanced` ki kam-ahem levels ooper hain,
    # `advanced` ki neeche. Isi liye ab simt ka koi zikr nahi: jo level apni
    # distribution mein SAB SE KAM hissa rakhta hai, wahi pehle kata hai. Ye khud
    # ba khud teeno ke liye durust simt chun leta hai.
    #
    # DONO BUG PURANE TESTS SE GUZAR GAYE. Wo JORH naapte hain (`sum == total`) aur
    # ye ke chhe keys mojood hain — kabhi ye nahi ke sawal KIS level par gaya.
    # Ginti hamesha theek thi; paper nahi.
    order = list(result)  # REMEMBER -> CREATE, the dict's own order
    surplus = sum(result.values()) - total_questions
    while surplus > 0:
        # Tarteeb: (1) sab se bari bucket, taake shakl mutanasib rahe; (2) barabari
        # mein wo level jis ka hissa sab se kam hai; (3) phir bhi barabari ho to
        # ooncha level (yani `balanced` 10 par wahi purana nateeja).
        trim_level = min(
            order,
            key=lambda lvl: (-result[lvl], shares[lvl], -order.index(lvl)),
        )
        if result[trim_level] == 0:
            break  # nothing left to trim, total_questions is unreachable with this split
        # EK EK KAR KE, `min(surplus, bucket)` se nahi. Poori bucket lene se wo level
        # khali ho jata tha jis ki us distribution ko sab se zyada zaroorat hai —
        # `foundational` 3 par REMEMBER isi tarah gaya tha (40% hissa 2 par ceil hota
        # hai, yani sab se bari bucket, aur poori ki poori chali jati thi).
        result[trim_level] -= 1
        surplus -= 1

    return result


def calculate_marks(bloom_level: str, question_type: str, difficulty: str) -> int:
    """Simple heuristic: higher cognitive levels and harder difficulty get
    more marks. Tweak these numbers freely once you have real exam data."""
    base = {"REMEMBER": 1, "UNDERSTAND": 2, "APPLY": 3, "ANALYZE": 4, "EVALUATE": 4, "CREATE": 5}
    type_bonus = {
        "essay": 3,
        "short-answer": 1,
        "multiple-choice": 0,
        "true-false": 0,
        "fill-blank": 0,
    }
    diff_bonus = {"easy": 0, "medium": 1, "hard": 2}
    return (
        base.get(bloom_level, 2) + type_bonus.get(question_type, 0) + diff_bonus.get(difficulty, 1)
    )
