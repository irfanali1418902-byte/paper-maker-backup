"""HISSA 1 tests — library_meta_import_service.import_meta_from_excel."""

from __future__ import annotations

import io
import uuid

import openpyxl
import pytest

from app.repositories import library_repository
from app.services import library_meta_import_service as svc

# ── Excel builder ─────────────────────────────────────────────────────────────

META_HEADER = ["image_name", "topic", "subject", "class", "keywords", "category", "question_types"]


def _make_xlsx(rows: list[list], header: list[str] = META_HEADER) -> bytes:
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(header)
    for row in rows:
        ws.append(row)
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


# ── DB helpers ────────────────────────────────────────────────────────────────

def _insert_image(name: str, **kwargs) -> str:
    img_id = str(uuid.uuid4())
    library_repository.insert({
        "id": img_id,
        "file_path": f"library/{img_id}.png",
        "name": name,
        **kwargs,
    })
    return img_id


def _insert_topic(subject: str, grade: str, title: str) -> str:
    topic_id = str(uuid.uuid4())
    from app.core.database import get_connection
    conn = get_connection()
    conn.execute(
        """INSERT INTO syllabus_topics
           (id, subject, grade, unit_no, unit_title, page_range,
            subtopic_title, activity_type, page_no, learning_outcome)
           VALUES (?,?,?,?,?,?,?,?,?,?)""",
        (topic_id, subject, grade, 1, "Unit 1", "1-5", title, "classwork", 1, ""),
    )
    conn.commit()
    conn.close()
    return topic_id


def _get_image(img_id: str) -> dict:
    return library_repository.find_by_id(img_id)


# ── Tests ─────────────────────────────────────────────────────────────────────

def test_happy_path_all_fields(test_db):
    img_id = _insert_image("apple_c")
    topic_id = _insert_topic("Math", "3", "Shapes")

    xlsx = _make_xlsx([
        ["apple_c", "Shapes", "Math", "3", "round, red", "fruit", "Count, Colour"],
    ])
    result = svc.import_meta_from_excel(xlsx)

    assert result["updated"] == 1
    assert result["skipped"] == 0

    img = _get_image(img_id)
    assert img["keywords"] == "round, red"
    assert img["category"] == "fruit"
    assert img["question_types"] == "Count, Colour"
    assert img["syllabus_topic_id"] == topic_id
    assert img["subject"] == "Math"
    assert img["grade"] == "3"


def test_missing_image_name_column_raises(test_db):
    xlsx = _make_xlsx([["apple_c", "Shapes"]], header=["img", "topic"])
    with pytest.raises(ValueError, match="image_name"):
        svc.import_meta_from_excel(xlsx)


def test_image_not_found_is_skipped(test_db):
    xlsx = _make_xlsx([["ghost_img", None, None, None, "kw", None, None]])
    result = svc.import_meta_from_excel(xlsx)

    assert result["updated"] == 0
    assert result["skipped"] == 1
    assert result["results"][0]["reason"] == "image library mein nahi mili"


def test_empty_cells_do_not_overwrite_existing(test_db):
    img_id = _insert_image("ball_c")
    library_repository.update_image(img_id, {"keywords": "original_kw", "category": "toy"})

    # keywords aur category column bhi nahi di (sirf image_name)
    xlsx = _make_xlsx([["ball_c", None, None, None, None, None, None]])
    result = svc.import_meta_from_excel(xlsx)

    # koi field nahi di → skip
    assert result["skipped"] == 1
    img = _get_image(img_id)
    assert img["keywords"] == "original_kw"
    assert img["category"] == "toy"


def test_partial_columns_only_keywords(test_db):
    img_id = _insert_image("cat_c")
    xlsx = _make_xlsx(
        [["cat_c", None, None, None, "furry, animal", None, None]],
    )
    result = svc.import_meta_from_excel(xlsx)

    assert result["updated"] == 1
    img = _get_image(img_id)
    assert img["keywords"] == "furry, animal"
    assert img["category"] is None  # chhua nahi


def test_topic_resolved_with_subject_grade_hint(test_db):
    _insert_topic("Science", "4", "Plants")
    math_topic_id = _insert_topic("Math", "4", "Plants")  # same naam, alag subject

    img_id = _insert_image("leaf_c")
    xlsx = _make_xlsx([["leaf_c", "Plants", "Math", "4", None, None, None]])
    svc.import_meta_from_excel(xlsx)

    img = _get_image(img_id)
    assert img["syllabus_topic_id"] == math_topic_id
    assert img["subject"] == "Math"


def test_topic_resolved_global_when_no_hint(test_db):
    topic_id = _insert_topic("English", "2", "Animals")
    img_id = _insert_image("dog_c")

    # subject/class column blank
    xlsx = _make_xlsx([["dog_c", "Animals", None, None, None, None, None]])
    svc.import_meta_from_excel(xlsx)

    img = _get_image(img_id)
    assert img["syllabus_topic_id"] == topic_id


def test_topic_not_found_adds_warning_rest_still_updates(test_db):
    img_id = _insert_image("horse_c")
    xlsx = _make_xlsx([["horse_c", "NonExistentTopic", None, None, "fast", "animal", None]])
    result = svc.import_meta_from_excel(xlsx)

    # Row update hua (keywords+category ke liye), topic skip hua
    assert result["updated"] == 1
    entry = result["results"][0]
    assert entry["status"] == "ok"
    assert any("topic" in w for w in entry["warnings"])

    img = _get_image(img_id)
    assert img["keywords"] == "fast"
    assert img["category"] == "animal"
    assert img["syllabus_topic_id"] is None


def test_mixed_rows_correct_counts(test_db):
    _insert_image("img_a")
    _insert_image("img_b")
    # img_c library mein nahi

    xlsx = _make_xlsx([
        ["img_a", None, None, None, "kw1", None, None],
        ["img_b", None, None, None, "kw2", None, None],
        ["img_c", None, None, None, "kw3", None, None],
    ])
    result = svc.import_meta_from_excel(xlsx)

    assert result["updated"] == 2
    assert result["skipped"] == 1


def test_empty_image_name_row_skipped(test_db):
    xlsx = _make_xlsx([
        ["", None, None, None, "kw", None, None],
    ])
    result = svc.import_meta_from_excel(xlsx)
    assert result["skipped"] == 1
    assert "khali" in result["results"][0]["reason"]


def test_invalid_file_bytes_raises(test_db):
    with pytest.raises(ValueError, match="Excel parse nahi hua"):
        svc.import_meta_from_excel(b"this is not excel")
