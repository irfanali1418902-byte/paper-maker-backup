"""School settings (singleton row id=1)."""

from app.repositories import settings_repository
from app.schemas.requests import SchoolSettings


def get_settings() -> dict:
    """Returns the saved settings, or model defaults if nothing has been
    saved yet (frontend always gets a populated shape)."""
    saved = settings_repository.get()
    if not saved:
        return SchoolSettings().model_dump()
    return saved


def save_settings(settings: SchoolSettings) -> None:
    settings_repository.upsert(
        school_name=settings.school_name,
        school_name_ur=settings.school_name_ur,
        address=settings.address,
        address_ur=settings.address_ur,
        logo_base64=settings.logo_base64,
        accent_color=settings.accent_color,
        phone=settings.phone,
        email=settings.email,
        principal_name=settings.principal_name,
        session_start_month=settings.session_start_month,
        exam_count=settings.exam_count,
        class_size=settings.class_size,
        min_analysis_percent=settings.min_analysis_percent,
        weak_topic_threshold=settings.weak_topic_threshold,
        print_font_size=settings.print_font_size,
        print_q_gap=settings.print_q_gap,
        print_page_margin=settings.print_page_margin,
    )
