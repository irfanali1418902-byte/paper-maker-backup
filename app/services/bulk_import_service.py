"""Bulk question import from Excel (.xlsx) or CSV files.

Each row becomes one manual question (source='manual').
Validation is per-row — one bad row never aborts the whole file.
"""

from __future__ import annotations

import io
import json
import uuid
from difflib import get_close_matches
from pathlib import Path
from typing import Optional

import pandas as pd

from app.core.database import get_connection
from app.repositories import library_repository, questions_repository

_LIBRARY_DIR = Path(__file__).parent.parent.parent / "static" / "library"
_UPLOADS_DIR = Path(__file__).parent.parent.parent / "static" / "uploads"
_UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

# ── constants ────────────────────────────────────────────────────────────────

VALID_TYPES = {"mcq", "fill", "tf", "short"}
MCQ_CORRECT = {"a", "b", "c", "d"}
TF_CORRECT = {"true", "false"}
VALID_BLOOM = {"REMEMBER", "UNDERSTAND", "APPLY", "ANALYZE", "EVALUATE", "CREATE"}
VALID_DIFFICULTIES = {"easy", "medium", "hard"}
VALID_STATUSES = {"published", "draft", "archived"}

REQUIRED_COLUMNS = {
    "type", "question", "subject",
}

# ── topic lookup helpers ──────────────────────────────────────────────────────

def _all_topic_titles() -> list[str]:
    """Fetch every distinct subtopic_title from syllabus_topics."""
    conn = get_connection()
    rows = conn.execute("SELECT DISTINCT subtopic_title FROM syllabus_topics").fetchall()
    conn.close()
    return [r[0] for r in rows if r[0]]


def _find_topic_id(topic_name: str, subject: str, grade: str) -> Optional[str]:
    """Case-insensitive, strip-whitespace match against subtopic_title.
    Tries subject+grade first, then subject-only, then global."""
    if not topic_name:
        return None
    needle = topic_name.strip().lower()
    conn = get_connection()
    rows = conn.execute(
        "SELECT id, subject, grade, subtopic_title FROM syllabus_topics"
    ).fetchall()
    conn.close()

    # Build normalised lookup: normalised_title → list of (id, subject, grade)
    normalised: dict[str, list[tuple[str, str, str]]] = {}
    for row in rows:
        key = row["subtopic_title"].strip().lower()
        normalised.setdefault(key, []).append((row["id"], row["subject"], row["grade"]))

    candidates = normalised.get(needle)
    if not candidates:
        return None

    # Prefer subject + grade match, then subject-only, then first
    for tid, s, g in candidates:
        if s == subject and g == grade:
            return tid
    for tid, s, _g in candidates:
        if s == subject:
            return tid
    return candidates[0][0]


def _suggest_topic(topic_name: str) -> Optional[str]:
    """Return a close match from syllabus_topics for the error report."""
    if not topic_name:
        return None
    needle = topic_name.strip().lower()
    titles = _all_topic_titles()
    normalised = [t.strip().lower() for t in titles]
    matches = get_close_matches(needle, normalised, n=1, cutoff=0.6)
    if not matches:
        return None
    # Return original casing
    idx = normalised.index(matches[0])
    return titles[idx]


# ── image lookup helper ───────────────────────────────────────────────────────

def _find_library_image(image_name: str, topic_id: Optional[str]) -> Optional[dict]:
    """Topic-scoped naam match pehle, phir global. None agar koi nahi mila."""
    if not image_name:
        return None
    if topic_id:
        hit = library_repository.find_by_name_and_topic(image_name, topic_id)
        if hit:
            return hit
    return library_repository.find_by_name(image_name)


# ── per-row validation ────────────────────────────────────────────────────────

def _cell(row: pd.Series, col: str) -> str:
    """Safe string extraction: NaN/None → empty string, strip whitespace."""
    val = row.get(col, "")
    if pd.isna(val):
        return ""
    return str(val).strip()


def _validate_row(row: pd.Series, row_num: int) -> tuple[Optional[dict], list[str]]:
    """Validate one DataFrame row.

    Returns (question_dict, warnings_list) on success, or (None, [error]) on failure.
    row_num is 1-indexed (header = row 1, first data row = row 2).
    """
    msgs: list[str] = []

    qtype = _cell(row, "type").lower()
    question = _cell(row, "question")
    subject = _cell(row, "subject")
    grade = _cell(row, "class")
    topic_name = _cell(row, "topic")
    correct_raw = _cell(row, "correct")
    is_urdu_raw = _cell(row, "is_urdu").lower()
    marks_raw = _cell(row, "marks")
    image_name = _cell(row, "image")  # optional; empty string if column absent

    # ── required field checks ────────────────────────────────────────────────
    if not question:
        return None, [f"row {row_num}: question column khaali hai"]

    if qtype not in VALID_TYPES:
        label = qtype or "(khaali)"
        return None, [f"row {row_num}: type '{label}' valid nahi (mcq/fill/tf/short hona chahiye)"]

    # ── MCQ-specific ─────────────────────────────────────────────────────────
    opt_a = _cell(row, "option_a")
    opt_b = _cell(row, "option_b")
    opt_c = _cell(row, "option_c")
    opt_d = _cell(row, "option_d")

    if qtype == "mcq":
        missing_opts = [
            lbl for lbl, val in [("option_a", opt_a), ("option_b", opt_b),
                                  ("option_c", opt_c), ("option_d", opt_d)]
            if not val
        ]
        if missing_opts:
            return None, [f"row {row_num}: MCQ mein {', '.join(missing_opts)} missing hai"]

        if correct_raw.lower() not in MCQ_CORRECT:
            return None, [
                f"row {row_num}: MCQ ka correct '{correct_raw}' valid nahi "
                f"(a/b/c/d hona chahiye)"
            ]

    # ── TF-specific ──────────────────────────────────────────────────────────
    if qtype == "tf" and correct_raw.lower() not in TF_CORRECT:
        return None, [
            f"row {row_num}: true/false ka correct '{correct_raw}' valid nahi "
            f"(true/false hona chahiye)"
        ]

    # ── marks (silent default = 1) ────────────────────────────────────────────
    try:
        marks = int(float(marks_raw)) if marks_raw else 1
        if marks < 1:
            marks = 1
    except ValueError:
        marks = 1

    # ── is_urdu ──────────────────────────────────────────────────────────────
    is_urdu = is_urdu_raw in {"yes", "1", "true", "haan"}

    # ── bloom_level (optional, default UNDERSTAND) ────────────────────────────
    bloom_raw = _cell(row, "bloom_level").upper()
    if bloom_raw and bloom_raw not in VALID_BLOOM:
        msgs.append(
            f"row {row_num}: bloom_level '{bloom_raw}' valid nahi "
            f"(REMEMBER/UNDERSTAND/APPLY/ANALYZE/EVALUATE/CREATE), 'UNDERSTAND' use kiya"
        )
        bloom_level = "UNDERSTAND"
    else:
        bloom_level = bloom_raw or "UNDERSTAND"

    # ── difficulty (optional, default medium) ────────────────────────────────
    difficulty_raw = _cell(row, "difficulty").lower()
    if difficulty_raw and difficulty_raw not in VALID_DIFFICULTIES:
        msgs.append(
            f"row {row_num}: difficulty '{difficulty_raw}' valid nahi "
            f"(easy/medium/hard), 'medium' use kiya"
        )
        difficulty = "medium"
    else:
        difficulty = difficulty_raw or "medium"

    # ── status (optional, default published) ─────────────────────────────────
    status_raw = _cell(row, "status").lower()
    if status_raw and status_raw not in VALID_STATUSES:
        msgs.append(
            f"row {row_num}: status '{status_raw}' valid nahi "
            f"(published/draft/archived), 'published' use kiya"
        )
        status = "published"
    else:
        status = status_raw or "published"

    # ── estimated_time (optional, must be int ≥ 1) ───────────────────────────
    estimated_time: Optional[int] = None
    et_raw = _cell(row, "estimated_time")
    if et_raw:
        try:
            et = int(float(et_raw))
            if et >= 1:
                estimated_time = et
            else:
                msgs.append(
                    f"row {row_num}: estimated_time '{et_raw}' 1 se kam hai, None rakha"
                )
        except ValueError:
            msgs.append(
                f"row {row_num}: estimated_time '{et_raw}' number nahi hai, None rakha"
            )

    # ── page_number (optional, must be int ≥ 1) ──────────────────────────────
    page_number: Optional[int] = None
    pn_raw = _cell(row, "page_number")
    if pn_raw:
        try:
            pn = int(float(pn_raw))
            if pn >= 1:
                page_number = pn
            else:
                msgs.append(
                    f"row {row_num}: page_number '{pn_raw}' 1 se kam hai, None rakha"
                )
        except ValueError:
            msgs.append(
                f"row {row_num}: page_number '{pn_raw}' number nahi hai, None rakha"
            )

    # ── plain text optional fields ────────────────────────────────────────────
    learning_outcome: Optional[str] = _cell(row, "learning_outcome") or None
    keywords: Optional[str] = _cell(row, "keywords") or None
    source_book: Optional[str] = _cell(row, "source_book") or None

    # ── topic matching ────────────────────────────────────────────────────────
    topic_id = _find_topic_id(topic_name, subject, grade) if topic_name else None
    if topic_name and topic_id is None:
        suggestion = _suggest_topic(topic_name)
        if suggestion:
            msgs.append(
                f"row {row_num}: topic '{topic_name}' syllabus mein nahi mila "
                f"(kya aap ka matlab '{suggestion}' tha?), topic_id=NULL rakha"
            )
        else:
            msgs.append(
                f"row {row_num}: topic '{topic_name}' syllabus mein nahi mila, "
                f"topic_id=NULL rakha"
            )

    # ── build question dict ───────────────────────────────────────────────────
    # MCQ: map a/b/c/d letter to actual option text for correct_answer
    if qtype == "mcq":
        opts = [opt_a, opt_b, opt_c, opt_d]
        letter_to_opt = {"a": opt_a, "b": opt_b, "c": opt_c, "d": opt_d}
        correct_text = letter_to_opt[correct_raw.lower()]
        options_list = opts
    else:
        options_list = []
        correct_text = correct_raw

    options_json = json.dumps(options_list)

    q: dict = {
        "id": str(uuid.uuid4()),
        "subject": subject,
        "topic": topic_name,
        "bloom_level": bloom_level,
        "difficulty": difficulty,
        "question_type": _map_type(qtype),
        "marks": marks,
        "question_en": None if is_urdu else question,
        "question_ur": question if is_urdu else None,
        "options_en": "[]" if is_urdu else options_json,
        "options_ur": options_json if is_urdu else "[]",
        "correct_answer_en": None if is_urdu else correct_text,
        "correct_answer_ur": correct_text if is_urdu else None,
        "explanation_en": None,
        "explanation_ur": None,
        "visual_emoji": None,
        "visual_count": None,
        "syllabus_topic_id": topic_id,
        "image_path": None,
        "image_size": None,
        "source": "manual",
        "learning_outcome": learning_outcome,
        "estimated_time": estimated_time,
        "keywords": keywords,
        "source_book": source_book,
        "page_number": page_number,
        "status": status,
        "_image_name": image_name,  # internal — resolved after insert
    }
    return q, msgs


def _map_type(qtype: str) -> str:
    """Excel shorthand → internal question_type value."""
    return {
        "mcq": "multiple-choice",
        "fill": "fill-in-the-blank",
        "tf": "true-false",
        "short": "short-answer",
    }[qtype]


# ── public API ────────────────────────────────────────────────────────────────

def import_from_bytes(file_bytes: bytes, filename: str) -> dict:
    """Parse Excel/CSV bytes, validate each row, insert valid ones.

    Returns:
        {
            "added": int,
            "skipped": int,
            "errors": ["row N: reason", ...],   # hard skips
            "warnings": ["row N: note", ...],   # soft (imported but with caveat)
        }
    """
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

    try:
        if ext == "csv":
            df = pd.read_csv(io.BytesIO(file_bytes), dtype=str, keep_default_na=False)
        elif ext in {"xlsx", "xls"}:
            df = pd.read_excel(io.BytesIO(file_bytes), dtype=str, keep_default_na=False)
        else:
            return {
                "added": 0, "skipped": 0,
                "errors": [f"File format '{ext}' support nahi hai (xlsx/csv chahiye)"],
                "warnings": [],
            }
    except Exception as e:  # noqa: BLE001
        return {
            "added": 0, "skipped": 0,
            "errors": [f"File parse nahi hua: {e}"],
            "warnings": [],
        }

    # Normalise column names: lowercase + strip
    df.columns = [str(c).strip().lower() for c in df.columns]

    # Check required columns present
    missing_cols = REQUIRED_COLUMNS - set(df.columns)
    if missing_cols:
        return {
            "added": 0, "skipped": 0,
            "errors": [f"Zaroori columns missing hain: {', '.join(sorted(missing_cols))}"],
            "warnings": [],
        }

    errors: list[str] = []
    warnings: list[str] = []
    added = 0

    for idx, row in df.iterrows():
        row_num = int(idx) + 2  # header=1, first data row=2
        q_dict, msgs = _validate_row(row, row_num)

        if q_dict is None:
            errors.extend(msgs)
            continue

        warnings.extend(msgs)

        image_name = q_dict.pop("_image_name", "")
        questions_repository.insert(q_dict)
        added += 1

        if image_name:
            lib_img = _find_library_image(image_name, q_dict.get("syllabus_topic_id"))
            if lib_img:
                _attach_library_image(q_dict["id"], lib_img)
            else:
                warnings.append(
                    f"row {row_num}: image '{image_name}' library mein nahi mili,"
                    " bina image ke daala"
                )

    return {
        "added": added,
        "skipped": len(errors),
        "errors": errors,
        "warnings": warnings,
    }


def _attach_library_image(question_id: str, lib_img: dict) -> None:
    """Library image ko uploads/ mein copy karo aur question se link karo."""
    from app.repositories import questions_repository as qr

    src = _LIBRARY_DIR / Path(lib_img["file_path"]).name
    if not src.exists():
        return
    ext = src.suffix.lstrip(".")
    dest = _UPLOADS_DIR / f"{question_id}.{ext}"
    dest.write_bytes(src.read_bytes())
    qr.update(question_id, {"image_path": f"uploads/{question_id}.{ext}"})
