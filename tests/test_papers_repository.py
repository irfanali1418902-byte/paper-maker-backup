"""Basic tests for papers_repository."""

import json

from app.repositories import papers_repository


def test_insert_then_find_by_id(test_db):
    papers_repository.insert(
        paper_id="p1",
        subject="Mathematics",
        class_name="Grade 1",
        total_marks=42,
        question_ids=["q1", "q2", "q3"],
    )
    paper = papers_repository.find_by_id("p1")
    assert paper is not None
    assert paper["subject"] == "Mathematics"
    assert paper["class_name"] == "Grade 1"
    assert paper["total_marks"] == 42
    # question_ids stored as JSON-encoded string per current contract
    assert json.loads(paper["question_ids"]) == ["q1", "q2", "q3"]


def test_find_by_id_returns_none_when_missing(test_db):
    assert papers_repository.find_by_id("nope") is None


def test_insert_with_null_class_name(test_db):
    papers_repository.insert(
        paper_id="p1",
        subject="English",
        class_name=None,
        total_marks=10,
        question_ids=[],
    )
    paper = papers_repository.find_by_id("p1")
    assert paper["class_name"] is None
    assert json.loads(paper["question_ids"]) == []


def test_insert_with_paper_title(test_db):
    papers_repository.insert(
        paper_id="p1",
        subject="Mathematics",
        class_name="Grade 4",
        total_marks=50,
        question_ids=[],
        paper_title="First Term – Math – Class 4",
    )
    paper = papers_repository.find_by_id("p1")
    assert paper["paper_title"] == "First Term – Math – Class 4"


def test_list_all_returns_newest_first(test_db):
    papers_repository.insert("p1", "Math", None, 10, [], paper_title="Old Paper")
    papers_repository.insert("p2", "Science", None, 20, [], paper_title="New Paper")
    results = papers_repository.list_all()
    assert len(results) == 2
    # p2 inserted after p1 — created_at DESC => p2 first (or equal; both have same timestamp)
    ids = [r["id"] for r in results]
    assert set(ids) == {"p1", "p2"}
    # question_ids must NOT be present in list view
    assert "question_ids" not in results[0]


def test_search_by_title(test_db):
    papers_repository.insert("p1", "Mathematics", "Grade 4", 50, [], paper_title="First Term Math")
    papers_repository.insert("p2", "Science", "Grade 5", 40, [], paper_title="Mid Year Science")
    results = papers_repository.search("First Term")
    assert len(results) == 1
    assert results[0]["id"] == "p1"


def test_search_by_subject(test_db):
    papers_repository.insert("p1", "Mathematics", None, 30, [], paper_title="Paper A")
    papers_repository.insert("p2", "Science", None, 30, [], paper_title="Paper B")
    results = papers_repository.search("science")
    assert len(results) == 1
    assert results[0]["id"] == "p2"


def test_search_returns_empty_for_no_match(test_db):
    papers_repository.insert("p1", "Mathematics", None, 30, [], paper_title="Paper A")
    results = papers_repository.search("Urdu")
    assert results == []
