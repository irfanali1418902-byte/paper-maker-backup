"""Tests: PATCH /api/questions/{id} — print.html edit modal ka save flow.

Root bug: saveQuestion() mein question_ur/correct_answer_en/correct_answer_ur
empty string ("") payload mein aata tha → _not_blank validator 422 raise karta
tha → answer_lines kabhi save nahi hoti thi.
"""
from __future__ import annotations

import uuid

from fastapi.testclient import TestClient

from app.core.database import get_connection
from app.main import app

client = TestClient(app)


def _insert_question(
    question_en: str = "What is 2+2?",
    question_ur: str | None = None,
    question_type: str = "short-answer",
    answer_lines: int | None = None,
    source: str = "gemini",
) -> str:
    qid = str(uuid.uuid4())
    conn = get_connection()
    conn.execute(
        """INSERT INTO questions
           (id, subject, topic, bloom_level, difficulty, question_type, marks,
            question_en, question_ur, options_en, options_ur,
            correct_answer_en, correct_answer_ur, explanation_en, explanation_ur,
            visual_emoji, visual_count, source, answer_lines, status)
           VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (qid, "Math", "Numbers", "REMEMBER", "easy", question_type, 1,
         question_en, question_ur, "[]", "[]",
         None, None, None, None, None, None, source, answer_lines, "published"),
    )
    conn.commit()
    conn.close()
    return qid


def _patch(qid: str, payload: dict):
    return client.patch(
        f"/api/questions/{qid}",
        json=payload,
        headers={"Content-Type": "application/json"},
    )


# ── Core fix: sirf non-empty fields bhejo ─────────────────────────────────────

def test_answer_lines_saves_without_question_ur(test_db):
    """English-only question (question_ur=NULL): payload mein question_ur nahi
    hona chahiye — warna _not_blank 422 raise karta hai."""
    qid = _insert_question(question_ur=None, answer_lines=None)
    res = _patch(qid, {"question_en": "What is 2+2?", "marks": 1, "answer_lines": 3})
    assert res.status_code == 200, res.json()
    data = res.json()
    assert data["answer_lines"] == 3


def test_answer_lines_saves_to_zero(test_db):
    """answer_lines=0 (None/no space) — valid value, save hona chahiye."""
    qid = _insert_question(answer_lines=2)
    res = _patch(qid, {"question_en": "What is 2+2?", "marks": 1, "answer_lines": 0})
    assert res.status_code == 200
    assert res.json()["answer_lines"] == 0


def test_answer_lines_update_2_to_6(test_db):
    qid = _insert_question(answer_lines=2)
    res = _patch(qid, {"question_en": "What is 2+2?", "marks": 1, "answer_lines": 6})
    assert res.status_code == 200
    assert res.json()["answer_lines"] == 6


def test_empty_string_question_ur_rejected(test_db):
    """Purana bug: question_ur='' (empty string) → 422. Yeh behaviour theek hai —
    frontend ko empty string send nahi karna chahiye."""
    qid = _insert_question()
    res = _patch(qid, {"question_en": "Q?", "marks": 1, "question_ur": ""})
    assert res.status_code == 422


def test_save_without_optional_fields_succeeds(test_db):
    """Sirf question_en + marks — baaki optional fields absent rahein to OK."""
    qid = _insert_question()
    res = _patch(qid, {"question_en": "What is 2+2?", "marks": 2})
    assert res.status_code == 200
    assert res.json()["marks"] == 2


def test_save_with_answer_lines_and_bilingual(test_db):
    """Bilingual question (question_ur bhi hai): answer_lines ke saath save."""
    qid = _insert_question(question_ur="دو جمع دو؟")
    res = _patch(qid, {
        "question_en": "What is 2+2?",
        "question_ur": "دو جمع دو؟",
        "marks": 1,
        "answer_lines": 4,
    })
    assert res.status_code == 200
    assert res.json()["answer_lines"] == 4


def test_answer_lines_persists_in_db(test_db):
    """Save ke baad DB mein value actually change honi chahiye."""
    from app.repositories import questions_repository
    qid = _insert_question(answer_lines=0)
    _patch(qid, {"question_en": "What is 2+2?", "marks": 1, "answer_lines": 8})
    row = questions_repository.find_by_id(qid)
    assert row["answer_lines"] == 8


def test_valid_answer_line_values(test_db):
    """Sab valid values (0,2,3,4,6,8) save honi chahiye."""
    for val in [0, 2, 3, 4, 6, 8]:
        qid = _insert_question()
        res = _patch(qid, {"question_en": "Q?", "marks": 1, "answer_lines": val})
        assert res.status_code == 200, f"val={val} failed"
        assert res.json()["answer_lines"] == val
