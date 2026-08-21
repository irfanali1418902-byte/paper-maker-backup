"""D40 — teacher haath se essay likh sake.

`ManualQuestionRequest` ka apna Literal chhota tha: usme `essay` nahi tha, jabke
`_PAPER_TYPE_FILTERS`, `_RATIO_SUBJECTIVE_GROUP`, `bloom_service` ("essay": 3),
`ai_service` aur `print.html` ka `answerSpace()` sab use jaante hain. Nateeja ye
ke 2026-08-21 tak bank mein AI ke banaye 11 essay maujood the aur teacher un jaisa
ek bhi khud nahi likh sakta tha.

Ab wo Literal shared `QuestionType` hi use karta hai, to farq dobara paida nahi
ho sakta -- aur yehi neeche wali pehli test naapti hai.
"""

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client(test_db):
    from app.main import app

    return TestClient(app)


def _essay_payload(**overrides) -> dict:
    payload = {
        "question_text": "Explain why 247 rounds to 250 to the nearest 10 but 200 to the nearest 100.",
        "is_urdu": False,
        "question_type": "essay",
        "marks": 6,
        "bloom_level": "ANALYZE",
        "subject": "Mathematics",
        "topic": "Rounding",
    }
    payload.update(overrides)
    return payload


# ---- schema ------------------------------------------------------------------


def test_manual_request_uses_the_shared_question_type_list():
    """Asal fix yehi hai. Do alag Literal rakhne se hi wo farq paida hua tha, to
    test qeematon ki nahi -- ek hi source hone ki tasdeeq karti hai."""
    from app.schemas.requests import ManualQuestionRequest, QuestionType

    field = ManualQuestionRequest.model_fields["question_type"]
    assert field.annotation is QuestionType


def test_every_app_question_type_is_writable_by_hand():
    """Koi bhi qism jo app jaanti hai, teacher likh bhi sakta ho. Nayi qism add
    karne wale ko yahan aa kar sochna paregi."""
    from typing import get_args

    from app.schemas.requests import ManualQuestionRequest, QuestionType

    assert set(get_args(ManualQuestionRequest.model_fields["question_type"].annotation)) == set(
        get_args(QuestionType)
    )


# ---- API ---------------------------------------------------------------------


class TestCreateManualEssay:
    def test_save_essay(self, client):
        res = client.post("/api/bank/questions", json=_essay_payload())
        assert res.status_code == 201
        data = res.json()
        assert data["question_type"] == "essay"
        assert data["source"] == "manual"
        assert data["marks"] == 6

    def test_essay_needs_no_options(self, client):
        """MCQ ka 2-options wala validator essay par nahi lagna chahiye."""
        res = client.post("/api/bank/questions", json=_essay_payload())
        assert res.status_code == 201
        assert res.json()["options_en"] in ("[]", None)

    def test_urdu_essay(self, client):
        res = client.post(
            "/api/bank/questions",
            json=_essay_payload(
                question_text="کُل اعداد کا موازنہ کرنے کا طریقہ بیان کریں۔", is_urdu=True
            ),
        )
        assert res.status_code == 201
        data = res.json()
        assert data["question_ur"] == "کُل اعداد کا موازنہ کرنے کا طریقہ بیان کریں۔"
        assert data["question_en"] is None

    def test_essay_keeps_answer_lines(self, client):
        """print.html ka answerSpace() essay par 5 lines + diagram box deta hai jab
        answer_lines None ho, aur teacher ki chuni hui ginti par diagram box hata
        deta hai -- to ye qeemat waqai kaghaz par asar daalti hai."""
        res = client.post("/api/bank/questions", json=_essay_payload(answer_lines=12))
        assert res.status_code == 201
        assert res.json()["answer_lines"] == 12

    def test_essay_with_a_model_answer(self, client):
        """Form abhi model answer nahi poochta (short-answer bhi nahi poochta),
        magar API use qubool karti hai -- bulk import aur AI dono bhejte hain."""
        res = client.post(
            "/api/bank/questions",
            json=_essay_payload(correct_answer="Compare digits from the left."),
        )
        assert res.status_code == 201
        assert res.json()["correct_answer_en"] == "Compare digits from the left."

    def test_unknown_type_is_still_rejected(self, client):
        """Literal barhaya gaya hai, khola nahi."""
        res = client.post("/api/bank/questions", json=_essay_payload(question_type="paragraph"))
        assert res.status_code == 422


# ---- frontend wiring ---------------------------------------------------------
#
# essay ka apna form section JAAN-BOOJH KAR nahi banaya. Us ke liye teen naye id
# chahiye the (sec-essay / q-essay-text / q-essay-lines), jo CSS ratchet ka frozen
# inventory badal dete aur `--write` maangte -- aur wo scripts/css_baseline.py ke
# apne docstring ke mutabiq "a conversation, not a command" hai. essay isliye
# short-answer ka section share karta hai; zaroorat dono ki ek hi hai.


def _bank_html() -> str:
    from pathlib import Path

    return (Path(__file__).parent.parent / "static" / "bank.html").read_text(encoding="utf-8")


def test_essay_is_offered_in_the_add_form():
    assert '<option value="essay">' in _bank_html()


def test_essay_maps_to_a_real_form_section():
    """TYPE_SECTIONS mein essay ka entry na ho to onTypeChange() koi section nahi
    dikhayega aur textarea milega hi nahi -- form khamoshi se mar jayega."""
    html = _bank_html()
    start = html.index("const TYPE_SECTIONS")
    region = html[start : start + 400]
    assert "'essay': 'sec-short'" in region
    assert 'id="sec-short"' in html


def test_essay_can_be_filtered_in_the_list():
    """Bank mein AI ke essay pehle se maujood the aur list mein filter hi nahi ho
    sakte the."""
    html = _bank_html()
    start = html.index('id="lType"')
    assert '<option value="essay">' in html[start : start + 400]


def test_essay_has_its_own_badge():
    """Warna typeBadge() ka fallback essay ko short-answer jaisa dikhata hai."""
    html = _bank_html()
    start = html.index("function typeBadge")
    assert "badge-essay" in html[start : start + 500]

    from pathlib import Path

    css = (Path(__file__).parent.parent / "static" / "css" / "99-legacy" / "bank.css").read_text(
        encoding="utf-8"
    )
    assert ".badge-essay" in css
