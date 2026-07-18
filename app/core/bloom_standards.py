"""Bloom's Taxonomy class-wise soft suggestions."""

import re

_GROUPS: dict[str, dict] = {
    "Pre-Primary": {
        "classes": ["play group", "nursery", "kg", "pre year 1", "pre year 2", "pre year 3"],
        "distribution": {"remember": 70, "understand": 30, "apply": 0, "analyze": 0, "evaluate": 0},
    },
    "Primary": {
        "classes": ["class 1", "class 2", "class 3", "class 4", "class 5",
                    "grade 1", "grade 2", "grade 3", "grade 4", "grade 5"],
        "distribution": {"remember": 30, "understand": 35, "apply": 25, "analyze": 10, "evaluate": 0},
    },
    "Middle": {
        "classes": ["class 6", "class 7", "class 8",
                    "grade 6", "grade 7", "grade 8"],
        "distribution": {"remember": 20, "understand": 30, "apply": 30, "analyze": 20, "evaluate": 0},
    },
    "Matric": {
        "classes": ["class 9", "class 10",
                    "grade 9", "grade 10"],
        "distribution": {"remember": 15, "understand": 25, "apply": 30, "analyze": 20, "evaluate": 10},
    },
}


def _normalize(name: str) -> str:
    """Lowercase, strip, collapse spaces/dashes/underscores to single space."""
    return re.sub(r"[\s\-_]+", " ", name.strip().lower())


def get_bloom_suggestion(class_name: str) -> dict | None:
    """Return {group, distribution} for the given class, or None if not matched."""
    key = _normalize(class_name)
    for group, data in _GROUPS.items():
        if key in data["classes"]:
            return {"group": group, "distribution": dict(data["distribution"])}
    return None


# SLO text ke pehle verb se Bloom level ki soft-suggestion (SLO import ke liye).
# Sirf tajweez — teacher override kar sakta hai. Verb pehchan mein na aaye to None.
_VERB_BLOOM: dict[str, str] = {
    # remember
    "define": "remember", "list": "remember", "identify": "remember",
    "name": "remember", "recall": "remember", "count": "remember",
    "write": "remember", "recognize": "remember",
    # understand
    "describe": "understand", "explain": "understand",
    "classify": "understand", "match": "understand",
    # apply
    "solve": "apply", "use": "apply", "apply": "apply",
    "demonstrate": "apply", "draw": "apply",
    # analyze
    "analyze": "analyze", "compare": "analyze",
    "differentiate": "analyze", "sort": "analyze",
}

# "Students will be able to <verb> ..." jaise phrasing mein verb tak pahunchne ke
# liye ye filler words skip karte hain.
_BLOOM_FILLERS = frozenset({
    "students", "student", "learners", "learner", "the", "a", "an", "to",
    "will", "be", "able", "can", "should", "and", "or", "of",
})


def suggest_bloom_from_text(slo_text: str) -> str | None:
    """SLO text ke pehle content-verb se Bloom level suggest karo.

    Filler words (students/will/be/able/to/...) skip karke pehla asal shabd
    dekha jaata hai; agar woh known verb hai to uska level, warna None. Verb
    match na ho to None hi rehta hai — "remember" default MAT karo, taake galat
    label khamoshi se na lag jaye (teacher khud bhar de).
    """
    if not slo_text:
        return None
    for word in re.findall(r"[a-zA-Z]+", slo_text.lower()):
        if word in _BLOOM_FILLERS:
            continue
        return _VERB_BLOOM.get(word)  # pehla content shabd: mapped level ya None
    return None
