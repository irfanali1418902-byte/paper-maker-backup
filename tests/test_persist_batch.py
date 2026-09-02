"""`question_service.persist_batch()` ke tests.

Ye function pehle bilkul untested tha, aur usi khamoshi mein ek khana chhut
raha tha: `learning_outcome` insert-dict mein daala hi nahi jata tha, jabke
`generate_for_topic()` usi `req` se use prompt ke liye parhta hai. Column
`INSERT` mein mojood hai aur `questions_repository.insert()` use
`question_row.get("learning_outcome")` se uthata hai — yani ghair-mojood key
par koi error nahi, khamoshi se `NULL`. Naapa gaya 2026-09-02: is raaste se
aaye **571 ke 571** sawal khaali the (`source='gemini'`, 08-21 se 09-01 tak
ke chhe batch). Bank mein kul 701 khaali hain, magar baqi 130 alag raaste se
aaye — bulk Excel import — aur un ki wajah ye bug nahi.

Note: `persist_batch` ko `scripts/seed_bank.py` aur `app/api/questions.py`
dono bulate hain, is liye ye sirf seeding ka nahi, `/api/generate` ka bhi
raasta hai.
"""

import json

from app.repositories import questions_repository
from app.schemas.requests import GenerateQuestionsRequest
from app.services import question_service


def _ai_question(question_en: str = "What is 2+2?") -> dict:
    """Wohi shakl jo `ai_service` wapas karti hai."""
    return {
        "bloom_level": "REMEMBER",
        "question_type": "multiple-choice",
        "question_en": question_en,
        "question_ur": "دو جمع دو کتنا ہے؟",
        "options_en": ["3", "4", "5", "6"],
        "options_ur": ["3", "4", "5", "6"],
        "correct_answer_en": "4",
        "correct_answer_ur": "4",
        "explanation_en": "Basic addition",
        "explanation_ur": "بنیادی جمع",
        "visual_emoji": None,
        "visual_count": None,
    }


def test_persist_batch_saves_learning_outcome(test_db):
    """Ye wo test hai jis ki ghair-mojoodgi mein khana mahinon khaali gaya."""
    req = GenerateQuestionsRequest(
        subject="Mathematics",
        topic="Counting",
        learning_outcome="Count objects up to 10",
    )

    saved_ids = question_service.persist_batch([_ai_question()], req)

    saved = questions_repository.find_by_id(saved_ids[0])
    assert saved["learning_outcome"] == "Count objects up to 10"


def test_persist_batch_leaves_learning_outcome_null_when_not_given(test_db):
    """Request mein na ho to `NULL` — koi jaali khali string nahi banti."""
    req = GenerateQuestionsRequest(subject="Mathematics", topic="Counting")

    saved_ids = question_service.persist_batch([_ai_question()], req)

    assert questions_repository.find_by_id(saved_ids[0])["learning_outcome"] is None


def test_persist_batch_passes_an_empty_outcome_through_as_empty(test_db):
    """Khali string jyun ki tyun guzarti hai — `NULL` mein nahi badalti.

    Ye farzi haalat nahi: `syllabus_service.py`:158 import ke waqt gaib
    outcome ko `(… or "").strip()` se khali string bana deta hai, aur wohi
    `req.learning_outcome` tak pohanchti hai. Aaj DB mein aisa ek bhi topic
    nahi (310 mein se 0), is liye ye rawaiyya likh kar mehfooz kiya ja raha
    hai — badalna ho to jaan-boojh kar badle, ittefaqan nahi.
    """
    req = GenerateQuestionsRequest(subject="Mathematics", topic="Counting", learning_outcome="")

    saved_ids = question_service.persist_batch([_ai_question()], req)

    assert questions_repository.find_by_id(saved_ids[0])["learning_outcome"] == ""


def test_persist_batch_saves_every_question_in_the_batch(test_db):
    """Har sawal ko wohi `learning_outcome` milta hai — wo topic ka hai, sawal ka nahi."""
    req = GenerateQuestionsRequest(
        subject="Mathematics",
        topic="Counting",
        syllabus_topic_id="topic-1",
        learning_outcome="Count objects up to 10",
    )
    batch = [_ai_question("What is 2+2?"), _ai_question("What is 3+3?")]

    saved_ids = question_service.persist_batch(batch, req)

    assert len(saved_ids) == 2
    assert len(set(saved_ids)) == 2  # har row ka apna uuid
    for qid in saved_ids:
        saved = questions_repository.find_by_id(qid)
        assert saved["learning_outcome"] == "Count objects up to 10"
        assert saved["syllabus_topic_id"] == "topic-1"


def test_persist_batch_still_saves_the_rest_of_the_row(test_db):
    """Ek line jorne se baqi khane na chhuten.

    Poori row nahi — 28 columns mein se wo nau jo `persist_batch` khud tay
    karta hai, aur in mein `marks` sab se aham hai kyunke wo waahid hisaab-shuda
    qeemat hai (`bloom_service.calculate_marks`, `question_service.py`:40).
    """
    req = GenerateQuestionsRequest(
        subject="Mathematics",
        topic="Counting",
        difficulty="easy",
        learning_outcome="Count objects up to 10",
    )

    saved_ids = question_service.persist_batch([_ai_question()], req)
    saved = questions_repository.find_by_id(saved_ids[0])

    assert saved["marks"] == 1  # REMEMBER + multiple-choice + easy
    assert saved["subject"] == "Mathematics"
    assert saved["topic"] == "Counting"
    assert saved["difficulty"] == "easy"
    assert saved["bloom_level"] == "REMEMBER"
    assert saved["question_type"] == "multiple-choice"
    assert saved["question_en"] == "What is 2+2?"
    assert saved["correct_answer_en"] == "4"
    assert json.loads(saved["options_en"]) == ["3", "4", "5", "6"]
