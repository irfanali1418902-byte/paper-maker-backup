"""Chhote text-normalize helpers — compare-time (data ko haath nahi lagate).

`normalize_subject` subject naam ko ek canonical shakl deta hai taake teacher
ke "Math" / "Mathematics" / " MATHEMATICS " sab ek hi cheez match karein.
Hardcoded if-else nahi — alias dict (nayi alias add karna aasaan)."""

from __future__ import annotations

# canonical -> uske alias(es). Sab lower/stripped compare hote hain.
_SUBJECT_ALIASES = {
    "mathematics": {"math", "maths", "mathematic"},
}

# reverse lookup: alias -> canonical (module load par ek dafa banta)
_ALIAS_TO_CANONICAL = {
    alias: canonical
    for canonical, aliases in _SUBJECT_ALIASES.items()
    for alias in aliases
}


def normalize_subject(subject: str | None) -> str:
    """Subject ko canonical lower-case form mein laao. Khali -> "".

    Alias (e.g. 'Math') apne canonical ('mathematics') par map hota hai;
    anjaan subject sirf lower/trim ho kar wapas aata (koi guess nahi)."""
    key = (subject or "").strip().lower()
    if not key:
        return ""
    return _ALIAS_TO_CANONICAL.get(key, key)
