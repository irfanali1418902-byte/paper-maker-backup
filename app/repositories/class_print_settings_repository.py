"""SQL access for class_print_settings (per-class print overrides, class_key PK).

class_key is the normalized class name (see app.core.text_norm.normalize_class) —
callers normalize before hitting this layer. Row absent = no per-class override
(service falls back to the global school_settings print defaults)."""

from typing import Optional

from app.core.database import get_connection


def get(class_key: str) -> Optional[dict]:
    conn = get_connection()
    cur = conn.cursor()
    row = cur.execute(
        "SELECT * FROM class_print_settings WHERE class_key = ?", (class_key,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def upsert(class_key: str, font_size: int, q_gap: int, page_margin: int) -> None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """INSERT INTO class_print_settings (class_key, font_size, q_gap, page_margin)
           VALUES (?, ?, ?, ?)
           ON CONFLICT(class_key) DO UPDATE SET
             font_size=excluded.font_size,
             q_gap=excluded.q_gap,
             page_margin=excluded.page_margin""",
        (class_key, font_size, q_gap, page_margin),
    )
    conn.commit()
    conn.close()
