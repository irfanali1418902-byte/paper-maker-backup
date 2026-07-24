"""SQL access for the school_settings table (single-row id=1 upsert)."""

from typing import Optional

from app.core.database import get_connection


def get() -> Optional[dict]:
    conn = get_connection()
    cur = conn.cursor()
    row = cur.execute("SELECT * FROM school_settings WHERE id = 1").fetchone()
    conn.close()
    return dict(row) if row else None


def upsert(
    school_name: str,
    school_name_ur: str,
    address: str,
    address_ur: str,
    logo_base64: Optional[str],
    accent_color: str,
    phone: str = "",
    email: str = "",
    principal_name: str = "",
    session_start_month: int = 3,
    exam_count: int = 8,
    class_size: int = 25,
    min_analysis_percent: int = 60,
    weak_topic_threshold: int = 60,
    print_font_size: int = 14,
    print_q_gap: int = 14,
    print_page_margin: int = 14,
) -> None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """INSERT INTO school_settings
               (id, school_name, school_name_ur, address, address_ur, logo_base64, accent_color,
                phone, email, principal_name, session_start_month, exam_count,
                class_size, min_analysis_percent, weak_topic_threshold,
                print_font_size, print_q_gap, print_page_margin)
           VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
           ON CONFLICT(id) DO UPDATE SET
             school_name=excluded.school_name, school_name_ur=excluded.school_name_ur,
             address=excluded.address, address_ur=excluded.address_ur,
             logo_base64=excluded.logo_base64, accent_color=excluded.accent_color,
             phone=excluded.phone, email=excluded.email,
             principal_name=excluded.principal_name,
             session_start_month=excluded.session_start_month,
             exam_count=excluded.exam_count,
             class_size=excluded.class_size,
             min_analysis_percent=excluded.min_analysis_percent,
             weak_topic_threshold=excluded.weak_topic_threshold,
             print_font_size=excluded.print_font_size,
             print_q_gap=excluded.print_q_gap,
             print_page_margin=excluded.print_page_margin""",
        (school_name, school_name_ur, address, address_ur, logo_base64, accent_color,
         phone, email, principal_name, session_start_month, exam_count,
         class_size, min_analysis_percent, weak_topic_threshold,
         print_font_size, print_q_gap, print_page_margin),
    )
    conn.commit()
    conn.close()
