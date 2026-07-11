"""HISSA 3 confirmation tests.

Ye tests prove karte hain ke:
1. find_least_used manual questions ko shamil karta hai (source filter nahi)
2. Topic-linked manual questions syllabus_topic_id se milte hain
3. POST /api/bank-paper — bina Gemini, sirf manual questions se paper banta hai
4. Print type rendering — already in HISSA 1, yahan backend confirm karte hain
   (fill-blank/true-false/short-answer question_type DB mein sahi store hoti hai)
"""

import json
import uuid

import pytest
from fastapi.testclient import TestClient

from app.repositories import questions_repository


@pytest.fixture
def client(test_db):
    from app.main import app
    return TestClient(app)


# ── Helpers ──────────────────────────────────────────────────────────────────

def _insert_manual(subject="Science", topic="Planets", bloom="REMEMBER",
                   qtype="short-answer", syllabus_topic_id=None):
    qid = str(uuid.uuid4())
    questions_repository.insert({
        "id": qid,
        "subject": subject,
        "topic": topic,
        "bloom_level": bloom,
        "difficulty": "medium",
        "question_type": qtype,
        "marks": 2,
        "question_en": f"Manual Q {qid[:4]}",
        "question_ur": None,
        "options_en": "[]",
        "options_ur": "[]",
        "correct_answer_en": None,
        "correct_answer_ur": None,
        "explanation_en": None,
        "explanation_ur": None,
        "visual_emoji": None,
        "visual_count": None,
        "syllabus_topic_id": syllabus_topic_id,
        "source": "manual",
    })
    return qid


def _insert_gemini(subject="Science", topic="Planets", bloom="REMEMBER"):
    qid = str(uuid.uuid4())
    questions_repository.insert({
        "id": qid,
        "subject": subject,
        "topic": topic,
        "bloom_level": bloom,
        "difficulty": "medium",
        "question_type": "multiple-choice",
        "marks": 1,
        "question_en": f"Gemini Q {qid[:4]}",
        "question_ur": None,
        "options_en": json.dumps(["A", "B", "C", "D"]),
        "options_ur": "[]",
        "correct_answer_en": "A",
        "correct_answer_ur": None,
        "explanation_en": None,
        "explanation_ur": None,
        "visual_emoji": None,
        "visual_count": None,
        # source defaults to 'gemini'
    })
    return qid


# ── GAP 1: find_least_used includes manual questions ─────────────────────────

class TestFindLeastUsedIncludesManual:
    def test_manual_question_returned_by_find_least_used(self, test_db):
        """source filter nahi — manual questions bloom+subject match par milte hain."""
        qid = _insert_manual(subject="Science", topic="Planets", bloom="REMEMBER")
        results = questions_repository.find_least_used(
            subject="Science", bloom_level="REMEMBER", difficulty=None, limit=10
        )
        ids = [r["id"] for r in results]
        assert qid in ids

    def test_manual_and_gemini_both_returned(self, test_db):
        m_id = _insert_manual(subject="History", topic="Mughal", bloom="UNDERSTAND")
        g_id = _insert_gemini(subject="History", topic="Mughal", bloom="UNDERSTAND")
        results = questions_repository.find_least_used(
            subject="History", bloom_level="UNDERSTAND", difficulty=None, limit=10
        )
        ids = [r["id"] for r in results]
        assert m_id in ids
        assert g_id in ids

    def test_source_field_present_in_result(self, test_db):
        _insert_manual(subject="Math", topic="Fractions", bloom="APPLY")
        results = questions_repository.find_least_used(
            subject="Math", bloom_level="APPLY", difficulty=None, limit=5
        )
        assert all("source" in r for r in results)
        manual_rows = [r for r in results if r["source"] == "manual"]
        assert len(manual_rows) >= 1


# ── GAP 2: Topic filter via find_for_bank_paper ───────────────────────────────

class TestTopicFilter:
    def test_topic_linked_manual_question_found(self, test_db):
        fake_topic_id = "topic-xyz-123"
        qid = _insert_manual(subject="Science", syllabus_topic_id=fake_topic_id)
        results = questions_repository.find_for_bank_paper(
            syllabus_topic_id=fake_topic_id, source="manual"
        )
        ids = [r["id"] for r in results]
        assert qid in ids

    def test_different_topic_excluded(self, test_db):
        qid1 = _insert_manual(subject="Science", syllabus_topic_id="topic-A")
        qid2 = _insert_manual(subject="Science", syllabus_topic_id="topic-B")
        results = questions_repository.find_for_bank_paper(syllabus_topic_id="topic-A", source="manual")
        ids = [r["id"] for r in results]
        assert qid1 in ids
        assert qid2 not in ids

    def test_source_manual_excludes_gemini(self, test_db):
        topic = "topic-shared"
        m_id = _insert_manual(subject="Science", syllabus_topic_id=topic)
        _insert_gemini(subject="Science")  # no topic_id, different insert
        # Insert gemini with same topic_id manually
        g2_id = str(uuid.uuid4())
        questions_repository.insert({
            "id": g2_id, "subject": "Science", "topic": "Planets",
            "bloom_level": "REMEMBER", "difficulty": "medium",
            "question_type": "multiple-choice", "marks": 1,
            "question_en": "Gemini Q", "question_ur": None,
            "options_en": "[]", "options_ur": "[]",
            "correct_answer_en": None, "correct_answer_ur": None,
            "explanation_en": None, "explanation_ur": None,
            "visual_emoji": None, "visual_count": None,
            "syllabus_topic_id": topic,
            # source defaults to 'gemini'
        })
        results = questions_repository.find_for_bank_paper(syllabus_topic_id=topic, source="manual")
        ids = [r["id"] for r in results]
        assert m_id in ids
        assert g2_id not in ids

    def test_source_all_includes_both(self, test_db):
        topic = "topic-mixed"
        m_id = _insert_manual(subject="Science", syllabus_topic_id=topic)
        g_id = str(uuid.uuid4())
        questions_repository.insert({
            "id": g_id, "subject": "Science", "topic": "Planets",
            "bloom_level": "REMEMBER", "difficulty": "medium",
            "question_type": "multiple-choice", "marks": 1,
            "question_en": "Gemini Q2", "question_ur": None,
            "options_en": "[]", "options_ur": "[]",
            "correct_answer_en": None, "correct_answer_ur": None,
            "explanation_en": None, "explanation_ur": None,
            "visual_emoji": None, "visual_count": None,
            "syllabus_topic_id": topic,
        })
        results = questions_repository.find_for_bank_paper(syllabus_topic_id=topic, source=None)
        ids = [r["id"] for r in results]
        assert m_id in ids
        assert g_id in ids


# ── GAP 3: POST /api/bank-paper — bina Gemini ────────────────────────────────

class TestBankPaperRoute:
    def test_bank_paper_from_manual_questions(self, client, test_db):
        """Manual questions hain to paper banta hai — Gemini ka koi call nahi."""
        _insert_manual(subject="Science", topic="Planets")
        _insert_manual(subject="Science", topic="Planets")
        res = client.post("/api/bank-paper", json={
            "subject": "Science",
            "source_filter": "manual",
        })
        assert res.status_code == 200
        data = res.json()
        assert data["paper_id"]
        assert len(data["questions"]) == 2
        assert all(q.get("source") == "manual" for q in data["questions"])

    def test_bank_paper_total_questions_limit(self, client, test_db):
        for _ in range(5):
            _insert_manual(subject="History", topic="Mughal")
        res = client.post("/api/bank-paper", json={
            "subject": "History",
            "total_questions": 3,
            "source_filter": "manual",
        })
        assert res.status_code == 200
        assert len(res.json()["questions"]) == 3

    def test_bank_paper_by_topic_id(self, client, test_db):
        topic_id = "syllabus-topic-ch5"
        _insert_manual(subject="Science", syllabus_topic_id=topic_id)
        _insert_manual(subject="Science", syllabus_topic_id=topic_id)
        _insert_manual(subject="Science", syllabus_topic_id="other-topic")  # should NOT appear
        res = client.post("/api/bank-paper", json={
            "syllabus_topic_id": topic_id,
            "source_filter": "manual",
        })
        assert res.status_code == 200
        data = res.json()
        assert len(data["questions"]) == 2

    def test_bank_paper_no_questions_returns_404(self, client, test_db):
        """Koi manual question nahi — 404."""
        res = client.post("/api/bank-paper", json={
            "subject": "Physics",
            "source_filter": "manual",
        })
        assert res.status_code == 404

    def test_bank_paper_source_all_includes_gemini(self, client, test_db):
        _insert_manual(subject="Biology", topic="Cells")
        _insert_gemini(subject="Biology", topic="Cells")
        res = client.post("/api/bank-paper", json={
            "subject": "Biology",
            "source_filter": "all",
        })
        assert res.status_code == 200
        sources = {q.get("source") for q in res.json()["questions"]}
        assert "manual" in sources
        assert "gemini" in sources

    def test_bank_paper_requires_subject_or_topic(self, client):
        """Na subject, na topic — 422."""
        res = client.post("/api/bank-paper", json={"source_filter": "manual"})
        assert res.status_code == 422

    def test_bank_paper_question_type_filter(self, client, test_db):
        _insert_manual(subject="Science", topic="X", qtype="multiple-choice")
        _insert_manual(subject="Science", topic="X", qtype="short-answer")
        res = client.post("/api/bank-paper", json={
            "subject": "Science",
            "question_types": ["short-answer"],
            "source_filter": "manual",
        })
        assert res.status_code == 200
        types = {q["question_type"] for q in res.json()["questions"]}
        assert types == {"short-answer"}


# ── GAP 4: Print type rendering (backend confirm) ─────────────────────────────

class TestPrintTypeRendering:
    """Backend side confirm: sab 4 types DB mein sahi store hoti hain
    aur response mein sahi question_type wapas aati hai (print.html JS use karta hai)."""

    @pytest.mark.parametrize("qtype", ["multiple-choice", "fill-blank", "true-false", "short-answer"])
    def test_question_type_stored_and_returned(self, client, test_db, qtype):
        create = client.post("/api/bank/questions", json={
            "question_text": f"Test question for {qtype}",
            "question_type": qtype,
            "subject": "Science",
            "topic": "Test Topic",
            "options": ["A", "B", "C"] if qtype == "multiple-choice" else None,
            "correct_answer": "A" if qtype == "multiple-choice" else (
                "True" if qtype == "true-false" else None
            ),
        })
        assert create.status_code == 201
        create.json()["id"]

        # Bank paper route se paper banao aur confirm karo type sahi hai
        _insert_manual(subject="Science", topic="Test Topic", qtype=qtype)
        res = client.post("/api/bank-paper", json={
            "subject": "Science", "source_filter": "manual",
            "question_types": [qtype],
        })
        assert res.status_code == 200
        for q in res.json()["questions"]:
            assert q["question_type"] == qtype
