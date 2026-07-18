"""question_slo_repository — link table (question <-> SLO) CRUD, Marhala 1."""

import json

from app.repositories import (
    question_slo_repository,
    questions_repository,
    slo_repository,
)


def _make_question(qid: str = "q1") -> None:
    questions_repository.insert({
        "id": qid,
        "subject": "Mathematics",
        "topic": "Counting",
        "bloom_level": "REMEMBER",
        "difficulty": "easy",
        "question_type": "multiple-choice",
        "marks": 1,
        "question_en": "What is 2+2?",
        "question_ur": None,
        "options_en": json.dumps(["3", "4"]),
        "options_ur": "[]",
        "correct_answer_en": "4",
        "correct_answer_ur": None,
        "explanation_en": None,
        "explanation_ur": None,
        "visual_emoji": None,
        "visual_count": None,
    })


def _make_slo(slo_id: str, code: str, strand: str = "Number") -> None:
    slo_repository.insert({
        "id": slo_id,
        "class": "Pre Year 1",
        "subject": "Mathematics",
        "slo_code": code,
        "slo_text": f"Outcome {code}",
        "bloom_level": None,
        "strand": strand,
    })


def test_replace_and_list(test_db):
    _make_question("q1")
    _make_slo("s1", "MATH-01")
    _make_slo("s2", "MATH-02")

    question_slo_repository.replace_for_question("q1", ["s1", "s2"])

    ids = question_slo_repository.list_slo_ids_for_question("q1")
    assert set(ids) == {"s1", "s2"}

    slos = question_slo_repository.list_slos_for_question("q1")
    assert [s["slo_code"] for s in slos] == ["MATH-01", "MATH-02"]  # slo_code se sorted


def test_replace_is_a_full_set(test_db):
    _make_question("q1")
    _make_slo("s1", "MATH-01")
    _make_slo("s2", "MATH-02")

    question_slo_repository.replace_for_question("q1", ["s1", "s2"])
    question_slo_repository.replace_for_question("q1", ["s2"])  # s1 hat jaye

    assert question_slo_repository.list_slo_ids_for_question("q1") == ["s2"]


def test_replace_with_empty_clears(test_db):
    _make_question("q1")
    _make_slo("s1", "MATH-01")
    question_slo_repository.replace_for_question("q1", ["s1"])
    question_slo_repository.replace_for_question("q1", [])
    assert question_slo_repository.list_slo_ids_for_question("q1") == []


def test_duplicate_slo_ids_idempotent(test_db):
    _make_question("q1")
    _make_slo("s1", "MATH-01")
    question_slo_repository.replace_for_question("q1", ["s1", "s1", "s1"])
    assert question_slo_repository.list_slo_ids_for_question("q1") == ["s1"]


def test_reverse_lookup(test_db):
    _make_question("q1")
    _make_question("q2")
    _make_slo("s1", "MATH-01")
    question_slo_repository.replace_for_question("q1", ["s1"])
    question_slo_repository.replace_for_question("q2", ["s1"])
    assert set(question_slo_repository.list_question_ids_for_slo("s1")) == {"q1", "q2"}


def test_existing_slo_ids_filters_unknown(test_db):
    _make_slo("s1", "MATH-01")
    valid = question_slo_repository.existing_slo_ids(["s1", "ghost"])
    assert valid == {"s1"}


def test_orphan_link_excluded_from_join(test_db):
    """Agar link row mein aisa slo_id ho jo slo table mein nahi (orphan),
    INNER JOIN usay list se khud nikaal deta hai — crash nahi."""
    _make_question("q1")
    # DELETE se pehle valid slo bana kar link karte hain, phir slo delete
    _make_slo("s1", "MATH-01")
    question_slo_repository.replace_for_question("q1", ["s1"])
    # SLO ko seedha DB se uda do
    from app.core.database import get_connection
    conn = get_connection()
    conn.execute("DELETE FROM slo WHERE id = 's1'")
    conn.commit()
    conn.close()
    assert question_slo_repository.list_slos_for_question("q1") == []
    # id-only list phir bhi link row dikhata hai (JOIN nahi)
    assert question_slo_repository.list_slo_ids_for_question("q1") == ["s1"]
