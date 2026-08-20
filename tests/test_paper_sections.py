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


# ---- Ratio Phase 2 — section ke ANDAR qism-wise theek ginti ----------------
#
# PRD R5. `question_types + count` yeh nahi kar sakta: repository ka SQL
# `question_type IN (...) ORDER BY usage_count ASC LIMIT n` hai, to ek section
# mein do qismein daal kar bhi andar ka mix usage counts par chhut jata hai.


def test_type_counts_give_exactly_what_was_asked(client):
    _seed_types()
    r = _generate(
        client,
        [
            {
                "heading": "Mixed",
                "type_counts": [
                    {"question_type": "multiple-choice", "count": 3},
                    {"question_type": "short-answer", "count": 4},
                ],
            }
        ],
    )
    assert r.status_code == 200
    body = r.json()
    by_id = {q["id"]: q for q in body["questions"]}
    got = [by_id[i]["question_type"] for i in body["sections"][0]["question_ids"]]
    assert got.count("multiple-choice") == 3
    assert got.count("short-answer") == 4
    assert len(got) == 7


def test_type_counts_keep_their_order(client):
    """Sawal kaghaz par isi tarteeb mein chhapte hain, isliye type_counts LIST
    hai dict nahi — teacher tay karta hai ke pehle kaunsi qism aaye."""
    _seed_types()
    r = _generate(
        client,
        [
            {
                "heading": "Order",
                "type_counts": [
                    {"question_type": "essay", "count": 2},
                    {"question_type": "true-false", "count": 2},
                ],
            }
        ],
    )
    body = r.json()
    by_id = {q["id"]: q for q in body["questions"]}
    got = [by_id[i]["question_type"] for i in body["sections"][0]["question_ids"]]
    assert got == ["essay", "essay", "true-false", "true-false"]


def test_type_counts_shortfall_names_the_type(client):
    """`shortfall: 2` teacher ko yeh nahi batata ke kaunsi qism kam pari, aur
    type_counts ki poori baat hi qism-wise ginti hai. shortfall_reason blueprint
    ki apni key hai jise print.html pehle se render karta hai."""
    _seed_types()
    r = _generate(
        client,
        [
            {
                "heading": "Kami",
                "type_counts": [
                    {"question_type": "short-answer", "count": 2},
                    {"question_type": "fill-blank", "count": 5},
                ],
            }
        ],
    )
    assert r.status_code == 200
    sec = r.json()["sections"][0]
    assert sec["shortfall"] == 5
    assert "fill-blank" in sec["shortfall_reason"]
    assert "short-answer" not in sec["shortfall_reason"]

    stored = json.loads(papers_repository.find_by_id(r.json()["paper_id"])["sections_meta"])
    assert "shortfall_reason" in stored[0]


def test_simple_section_has_no_shortfall_reason(client):
    """Saada shakl ka bartao 2026-08-20 wala hi rehna chahiye — wahan qism ek
    hi hoti hai, to adad khud kaafi hai aur meta mein nayi key nahi aati."""
    _seed_types()
    # count seeded ginti se zyada, taake shortfall zaroor bane — sawal yeh hai ke
    # SHORTFALL hone par bhi saada shakl reason NAHI likhti.
    r = _generate(client, [{"heading": "A", "question_types": ["essay"], "count": 99}])
    assert r.status_code == 200
    assert r.json()["sections"][0]["shortfall"] > 0
    assert r.json()["sections"][0]["shortfall_reason"] is None
    stored = json.loads(papers_repository.find_by_id(r.json()["paper_id"])["sections_meta"])
    assert set(stored[0]) == {"heading", "question_ids", "marks", "shortfall"}


def test_type_counts_shortfall_counts_the_sum(client):
    _seed_types()
    r = _generate(
        client,
        [
            {
                "heading": "Sum",
                "type_counts": [
                    {"question_type": "fill-blank", "count": 4},
                    {"question_type": "essay", "count": 2},
                ],
            }
        ],
    )
    sec = r.json()["sections"][0]
    assert sec["shortfall"] == 6 - len(sec["question_ids"])


def test_both_shapes_at_once_is_refused(client):
    """Dono ginti tay karte hain — khamoshi se ek chun lena teacher ko aisa
    paper de deta jo usne maanga hi nahi."""
    r = _generate(
        client,
        [
            {
                "heading": "A",
                "question_types": ["essay"],
                "count": 3,
                "type_counts": [{"question_type": "essay", "count": 3}],
            }
        ],
    )
    assert r.status_code == 422


def test_neither_shape_is_refused(client):
    assert _generate(client, [{"heading": "A"}]).status_code == 422


def test_duplicate_type_in_type_counts_is_refused(client):
    """Ek hi qism do dafa: kaun si ginti sahi hai, is ka koi jawab nahi."""
    r = _generate(
        client,
        [
            {
                "heading": "A",
                "type_counts": [
                    {"question_type": "essay", "count": 2},
                    {"question_type": "essay", "count": 3},
                ],
            }
        ],
    )
    assert r.status_code == 422


@pytest.mark.parametrize(
    "bad",
    [
        [{"question_type": "essay", "count": 0}],
        [{"question_type": "not-a-type", "count": 2}],
        [],
    ],
)
def test_bad_type_counts_are_422(client, bad):
    assert _generate(client, [{"heading": "A", "type_counts": bad}]).status_code == 422


def test_type_counts_and_simple_sections_mix_in_one_paper(client):
    """Ek paper mein dono shaklein saath chal saken — warna teacher ko poora
    paper ek hi tareeqe mein likhna parta."""
    _seed_types()
    r = _generate(
        client,
        [
            {"heading": "A", "question_types": ["multiple-choice", "true-false"], "count": 4},
            {
                "heading": "B",
                "type_counts": [
                    {"question_type": "short-answer", "count": 2},
                    {"question_type": "essay", "count": 2},
                ],
            },
        ],
    )
    assert r.status_code == 200
    body = r.json()
    by_id = {q["id"]: q for q in body["questions"]}
    b_types = [by_id[i]["question_type"] for i in body["sections"][1]["question_ids"]]
    assert b_types == ["short-answer", "short-answer", "essay", "essay"]
