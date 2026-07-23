"""Per-class print settings resolution (Marhala 4A).

get_print_settings(class_name) resolves the three print knobs (font_size, q_gap,
page_margin) for a given paper's class. Row-level fallback: if the class has a
class_print_settings row, its values win; otherwise the global defaults from
school_settings (print_font_size / print_q_gap / print_page_margin) apply.

class_name is the paper's free-text class (papers.class_name); it is normalized
here via normalize_class so "Class 5" / "class 5" resolve to one key."""

from app.core.text_norm import normalize_class
from app.repositories import class_print_settings_repository
from app.services import settings_service


def get_print_settings(class_name: str | None) -> dict:
    """Returns {"font_size", "q_gap", "page_margin"} for the class, falling back
    to the global school_settings print defaults when no per-class row exists."""
    key = normalize_class(class_name)
    row = class_print_settings_repository.get(key) if key else None
    if row:
        return {
            "font_size": row["font_size"],
            "q_gap": row["q_gap"],
            "page_margin": row["page_margin"],
        }

    globals_ = settings_service.get_settings()
    return {
        "font_size": globals_["print_font_size"],
        "q_gap": globals_["print_q_gap"],
        "page_margin": globals_["print_page_margin"],
    }


def save_print_settings(class_name: str, font_size: int, q_gap: int, page_margin: int) -> str:
    """Ek class ke print knobs upsert karta hai (normalize_class se key). Returns
    the normalized class_key. Blank class -> ValueError (per-class ke liye class
    laazmi; route ise 400 mein badalta hai). Value-bounds schema enforce karti hai."""
    key = normalize_class(class_name)
    if not key:
        raise ValueError("class_name khali nahi ho sakta — per-class settings ke liye class laazmi hai.")
    class_print_settings_repository.upsert(key, font_size, q_gap, page_margin)
    return key
