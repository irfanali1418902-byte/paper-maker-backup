"""Fix 2 — question delete se pehle paper-usage (kaun se papers orphan honge)."""

from fastapi.testclient import TestClient

from app.main import app
from app.repositories import papers_repository, questions_repository
from app.services import paper_service

client = TestClient(app)


def _q(qid: str) -> None:
    questions_repository.insert({
        "id": qid, "subject": "Mathematics", "topic": "Counting",
        "bloom_level": "REMEMBER", "difficulty": "easy",
        "question_type": "short-answer", "marks": 1,
        "question_en": "Q", "question_ur": None,
        "options_en": "[]", "options_ur": "[]",
        "correct_answer_en": None, "correct_answer_ur": None,
        "explanation_en": None, "explanation_ur": None,
        "visual_emoji": None, "visual_count": None,
        "source": "manual",
    })


def _paper(pid: str, qids: list, title="Test Paper") -> None:
    papers_repository.insert(pid, "Mathematics", "Pre Year 1", len(qids), qids, paper_title=title)


# ── repository ────────────────────────────────────────────────────────────────

def test_find_papers_containing_none(test_db):
    _q("q1")
    assert papers_repository.find_papers_containing("q1") == []


def test_find_papers_containing_multiple(test_db):
    _q("q1")
    _paper("p1", ["q1", "qx"], title="Paper A")
    _paper("p2", ["qy", "q1"], title="Paper B")
    _paper("p3", ["qz"], title="Paper C")  # q1 nahi
    got = papers_repository.find_papers_containing("q1")
    assert {p["paper_title"] for p in got} == {"Paper A", "Paper B"}


def test_find_papers_containing_substring_safe(test_db):
    """Ek qid doosre ka substring ho to false-match na ho (quoted-id LIKE)."""
    _paper("p1", ["abc"], title="Short")
    _paper("p2", ["abcdef"], title="Long")
    got = papers_repository.find_papers_containing("abc")
    assert {p["paper_title"] for p in got} == {"Short"}  # 'abcdef' match na kare


# ── service ───────────────────────────────────────────────────────────────────

def test_papers_using_question_titles(test_db):
    _q("q1")
    _paper("p1", ["q1"], title="Mid Term")
    papers_repository.insert("p2", "Mathematics", None, 1, ["q1"], paper_title=None)  # untitled
    res = paper_service.papers_using_question("q1")
    assert res["count"] == 2
    assert "Mid Term" in res["titles"]
    assert "(Untitled)" in res["titles"]


# ── API ───────────────────────────────────────────────────────────────────────

def test_paper_usage_endpoint(test_db):
    _q("q1")
    _paper("p1", ["q1"], title="Paper A")
    resp = client.get("/api/bank/questions/q1/paper-usage")
    assert resp.status_code == 200
    data = resp.json()
    assert data["paper_count"] == 1
    assert data["paper_titles"] == ["Paper A"]


def test_paper_usage_zero(test_db):
    _q("q1")
    resp = client.get("/api/bank/questions/q1/paper-usage")
    assert resp.status_code == 200
    assert resp.json()["paper_count"] == 0
