"""Sections mode — teacher apne sections khud tay karta hai (A/B/C).

Sawal QISM se section mein jaate hain (Irfan ka faisla, 2026-08-20), aur section
ki shakl `sections_meta` mein waisi hi likhi jaati hai jaisi blueprint likhta hai
— isi liye static/print.html ise bina kisi tabdeeli ke render kar leta hai.

Yahan wo cheezein lock ki ja rahi hain jo khamoshi se toot sakti hain:
  * sections na dene par purana raasta BILKUL waisa (sections_meta NULL rahe)
  * har section sirf apni qism ke sawal uthaye
  * kami par fail NAHI hona — shortfall REPORT karna (blueprint jaisa)
  * sections + custom-ratio ka saaf inkaar, khamosh tarjeeh nahi
"""

import json
import uuid

import pytest
from fastapi.testclient import TestClient

from app.repositories import papers_repository, questions_repository

BLOOM_LEVELS = ["REMEMBER", "UNDERSTAND", "APPLY", "ANALYZE", "EVALUATE", "CREATE"]


@pytest.fixture
def client(test_db):
    from app.main import app

    return TestClient(app)


def _insert(qtype, bloom="UNDERSTAND", subject="Mathematics", marks=3):
    qid = str(uuid.uuid4())
    questions_repository.insert(
        {
            "id": qid,
            "subject": subject,
            "topic": "Fractions",
            "bloom_level": bloom,
            "difficulty": "medium",
            "question_type": qtype,
            "marks": marks,
            "question_en": f"Q-{qid[:4]}",
            "question_ur": "سوال",
            "options_en": json.dumps(["a", "b", "c", "d"]),
            "options_ur": json.dumps(["ا", "ب", "ج", "د"]),
            "correct_answer_en": "a",
            "correct_answer_ur": "ا",
            "explanation_en": "",
            "explanation_ur": "",
            "visual_emoji": None,
            "visual_count": None,
        }
    )
    return qid


def _seed_types():
    """Har Bloom level par har qism ke do sawal.

    Har level par isliye ke calculate_bloom_distribution ginti ko CHHE levels par
    baantta hai; ek hi level par seed karne se baqi buckets khaali lautte aur test
    shortfall naapta jabke wo naapna hi nahi tha.
    """
    ids = {"multiple-choice": [], "true-false": [], "short-answer": [], "essay": []}
    for lvl in BLOOM_LEVELS:
        for qtype in ids:
            for _ in range(2):
                ids[qtype].append(_insert(qtype, bloom=lvl))
    return ids


def _generate(client, sections, **extra):
    body = {"subject": "Mathematics", "sections": sections}
    body.update(extra)
    return client.post("/api/generate-paper", json=body)


# ---- purana raasta na toote ------------------------------------------------


def test_no_sections_leaves_sections_meta_null(client):
    """Sections ke baghair sab kuch bilkul pehle jaisa — sections_meta NULL rahe.

    Yahi wo cheez hai jo print.html ko uske hardcoded A/B split par rakhti hai.
    NULL ke bajaye khaali list likh dena har purane paper ka look badal deta.
    """
    _seed_types()
    r = client.post(
        "/api/generate-paper",
        json={"subject": "Mathematics", "total_questions": 6},
    )
    assert r.status_code == 200
    assert r.json().get("sections") is None

    row = papers_repository.find_by_id(r.json()["paper_id"])
    assert row["sections_meta"] is None


# ---- section ko sirf apni qism mile ----------------------------------------


def test_each_section_only_gets_its_own_types(client):
    _seed_types()
    r = _generate(
        client,
        [
            {"heading": "Section A", "question_types": ["multiple-choice", "true-false"], "count": 4},
            {"heading": "Section B", "question_types": ["short-answer"], "count": 3},
        ],
    )
    assert r.status_code == 200
    body = r.json()
    by_id = {q["id"]: q for q in body["questions"]}

    sec_a, sec_b = body["sections"]
    assert sec_a["heading"] == "Section A"
    assert {by_id[i]["question_type"] for i in sec_a["question_ids"]} <= {
        "multiple-choice",
        "true-false",
    }
    assert {by_id[i]["question_type"] for i in sec_b["question_ids"]} == {"short-answer"}


def test_sections_meta_matches_the_blueprint_shape(client):
    """print.html blueprint ki keys parhta hai; agar yeh shakl badli to sections
    kaghaz par chup-chaap ghayab ho jayenge — 404 nahi, koi error nahi."""
    _seed_types()
    r = _generate(client, [{"heading": "Only", "question_types": ["essay"], "count": 2}])
    assert r.status_code == 200

    stored = json.loads(papers_repository.find_by_id(r.json()["paper_id"])["sections_meta"])
    assert len(stored) == 1
    assert set(stored[0]) == {"heading", "question_ids", "marks", "shortfall"}
    assert stored[0]["heading"] == "Only"


def test_section_marks_and_total_agree_with_questions(client):
    _seed_types()
    r = _generate(
        client,
        [
            {"heading": "A", "question_types": ["multiple-choice"], "count": 3},
            {"heading": "B", "question_types": ["essay"], "count": 2},
        ],
    )
    body = r.json()
    by_id = {q["id"]: q for q in body["questions"]}
    for sec in body["sections"]:
        assert sec["marks"] == sum(by_id[i]["marks"] for i in sec["question_ids"])
    assert body["total_marks"] == sum(s["marks"] for s in body["sections"])


def test_headings_survive_verbatim(client):
    """Heading kaghaz par chhapti hai. Em-dash aur Urdu dono zinda rehne chahiyen."""
    _seed_types()
    heading = "حصہ الف — Objective"
    r = _generate(client, [{"heading": heading, "question_types": ["true-false"], "count": 2}])
    assert r.json()["sections"][0]["heading"] == heading
    stored = json.loads(papers_repository.find_by_id(r.json()["paper_id"])["sections_meta"])
    assert stored[0]["heading"] == heading


# ---- kami par fail nahi, report -------------------------------------------


def test_shortfall_is_reported_not_raised(client):
    """custom-ratio kami par QuestionBankEmpty phenkta hai; sections nahi.

    Wajah asli bank hai: 2026-08-20 ko Mathematics mein short-answer 240,
    multiple-choice 61, true-false 28 aur fill-blank/essay SIFAR the. Hard error
    is feature ko aam halat mein na-qabil-e-istemal bana deta.
    """
    _seed_types()
    r = _generate(client, [{"heading": "Bohat zyada", "question_types": ["true-false"], "count": 99}])
    assert r.status_code == 200
    sec = r.json()["sections"][0]
    assert sec["shortfall"] == 99 - len(sec["question_ids"])
    assert sec["shortfall"] > 0


def test_empty_section_still_appears(client):
    """Khali section ghayab nahi hota — heading aur shortfall ke saath aata hai,
    warna teacher ko pata hi na chale ke us qism ka koi sawal mila hi nahi."""
    _seed_types()
    r = _generate(
        client,
        [
            {"heading": "Bhara", "question_types": ["short-answer"], "count": 2},
            {"heading": "Khali", "question_types": ["fill-blank"], "count": 3},
        ],
    )
    assert r.status_code == 200
    khali = r.json()["sections"][1]
    assert khali["question_ids"] == []
    assert khali["marks"] == 0
    assert khali["shortfall"] == 3


def test_all_sections_empty_is_404(client):
    """Ek bhi sawal na mile to purane raaston jaisa hi 404 — khali paper nahi."""
    _seed_types()
    r = _generate(client, [{"heading": "Kuch nahi", "question_types": ["fill-blank"], "count": 5}])
    assert r.status_code == 404


# ---- validation ------------------------------------------------------------


def test_sections_with_custom_ratio_is_refused(client):
    """Dono ginti tay karte hain. Khamoshi se ek ko tarjeeh dena teacher ko
    aisa paper de deta jo usne maanga hi nahi tha."""
    r = _generate(
        client,
        [{"heading": "A", "question_types": ["multiple-choice"], "count": 2}],
        paper_type="custom-ratio",
        mcq_percent=50,
    )
    assert r.status_code == 422


def test_duplicate_headings_refused(client):
    r = _generate(
        client,
        [
            {"heading": "Section A", "question_types": ["multiple-choice"], "count": 2},
            {"heading": "section a", "question_types": ["essay"], "count": 2},
        ],
    )
    assert r.status_code == 422


@pytest.mark.parametrize(
    "bad",
    [
        {"heading": "", "question_types": ["essay"], "count": 2},
        {"heading": "   ", "question_types": ["essay"], "count": 2},
        {"heading": "A", "question_types": [], "count": 2},
        {"heading": "A", "question_types": ["not-a-type"], "count": 2},
        {"heading": "A", "question_types": ["essay"], "count": 0},
        {"heading": "A", "question_types": ["essay"], "count": -1},
    ],
)
def test_bad_section_specs_are_422(client, bad):
    assert _generate(client, [bad]).status_code == 422


def test_heading_is_stripped(client):
    _seed_types()
    r = _generate(client, [{"heading": "  Padded  ", "question_types": ["essay"], "count": 2}])
    assert r.json()["sections"][0]["heading"] == "Padded"


def test_duplicate_types_within_a_section_collapse(client):
    _seed_types()
    r = _generate(
        client,
        [{"heading": "A", "question_types": ["essay", "essay", "short-answer"], "count": 2}],
    )
    assert r.status_code == 200
    stored = json.loads(papers_repository.find_by_id(r.json()["paper_id"])["sections_meta"])
    assert stored[0]["shortfall"] == 2 - len(stored[0]["question_ids"])
