"""Tests for Blueprint HISSA 1: presets API, blueprint CRUD, DB migration safety."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client(test_db):
    from app.main import app
    return TestClient(app)


# ── helper ────────────────────────────────────────────────────────────────────

def _section(heading="Section A", types=None, count=5, marks=1):
    return {
        "heading": heading,
        "question_types": types or ["multiple-choice"],
        "topic_ids": [],
        "count": count,
        "marks_each": marks,
        "source_filter": "manual",
    }


def _save(client, name="My Blueprint", subject="Science", grade="7", sections=None):
    return client.post("/api/blueprints", json={
        "name": name,
        "subject": subject,
        "grade": grade,
        "sections": sections or [_section()],
    })


# ── presets ───────────────────────────────────────────────────────────────────

class TestPresets:
    def test_list_presets_returns_list(self, client):
        res = client.get("/api/blueprint-presets")
        assert res.status_code == 200
        data = res.json()
        assert "presets" in data
        assert len(data["presets"]) >= 2

    def test_preset_has_required_fields(self, client):
        res = client.get("/api/blueprint-presets")
        for preset in res.json()["presets"]:
            assert "id" in preset
            assert "name" in preset
            assert "sections" in preset
            assert len(preset["sections"]) >= 1

    def test_each_section_has_question_types_list(self, client):
        res = client.get("/api/blueprint-presets")
        for preset in res.json()["presets"]:
            for sec in preset["sections"]:
                assert isinstance(sec["question_types"], list)
                assert len(sec["question_types"]) >= 1

    def test_get_preset_by_id(self, client):
        res = client.get("/api/blueprint-presets/nce_pre_year")
        assert res.status_code == 200
        assert res.json()["id"] == "nce_pre_year"

    def test_get_preset_not_found(self, client):
        res = client.get("/api/blueprint-presets/nonexistent_preset")
        assert res.status_code == 404

    def test_nce_preset_has_3_sections(self, client):
        res = client.get("/api/blueprint-presets/nce_pre_year")
        assert len(res.json()["sections"]) == 3

    def test_matric_preset_exists(self, client):
        res = client.get("/api/blueprint-presets/matric_board")
        assert res.status_code == 200
        assert "Matric" in res.json()["name"]

    def test_preset_sections_have_count_and_marks(self, client):
        res = client.get("/api/blueprint-presets/nce_pre_year")
        for sec in res.json()["sections"]:
            assert sec["count"] >= 1
            assert sec["marks_each"] >= 1


# ── save blueprint ────────────────────────────────────────────────────────────

class TestSaveBlueprint:
    def test_save_returns_201(self, client):
        res = _save(client)
        assert res.status_code == 201

    def test_save_returns_blueprint_with_id(self, client):
        res = _save(client)
        data = res.json()
        assert "id" in data
        assert data["name"] == "My Blueprint"

    def test_save_sections_stored_correctly(self, client):
        sections = [
            _section("Sec A", ["multiple-choice"], 10, 1),
            _section("Sec B", ["short-answer"], 5, 3),
        ]
        res = _save(client, sections=sections)
        assert res.status_code == 201
        stored = res.json()["sections"]
        assert len(stored) == 2
        assert stored[0]["heading"] == "Sec A"
        assert stored[1]["question_types"] == ["short-answer"]

    def test_question_types_is_list(self, client):
        res = _save(client, sections=[_section(types=["fill-in-the-blank"])])
        assert res.status_code == 201
        sec = res.json()["sections"][0]
        assert isinstance(sec["question_types"], list)

    def test_multi_type_section_stored(self, client):
        """One section with multiple types (fill + short) — stored as list."""
        res = _save(client, sections=[_section(types=["fill-in-the-blank", "short-answer"])])
        assert res.status_code == 201
        assert res.json()["sections"][0]["question_types"] == ["fill-in-the-blank", "short-answer"]

    def test_save_without_subject_grade(self, client):
        res = client.post("/api/blueprints", json={
            "name": "Generic Blueprint",
            "sections": [_section()],
        })
        assert res.status_code == 201
        data = res.json()
        assert data["subject"] is None
        assert data["grade"] is None

    def test_save_empty_name_rejected(self, client):
        res = client.post("/api/blueprints", json={
            "name": "   ",
            "sections": [_section()],
        })
        assert res.status_code == 422

    def test_save_empty_sections_rejected(self, client):
        res = client.post("/api/blueprints", json={
            "name": "No sections",
            "sections": [],
        })
        assert res.status_code == 422

    def test_save_empty_question_types_rejected(self, client):
        res = client.post("/api/blueprints", json={
            "name": "Bad section",
            "sections": [{"heading": "A", "question_types": [], "count": 5, "marks_each": 1}],
        })
        assert res.status_code == 422

    def test_invalid_source_filter_rejected(self, client):
        sec = _section()
        sec["source_filter"] = "invalid"
        res = client.post("/api/blueprints", json={"name": "BP", "sections": [sec]})
        assert res.status_code == 422


# ── get blueprint ─────────────────────────────────────────────────────────────

class TestGetBlueprint:
    def test_get_by_id(self, client):
        saved_id = _save(client).json()["id"]
        res = client.get(f"/api/blueprints/{saved_id}")
        assert res.status_code == 200
        assert res.json()["id"] == saved_id

    def test_get_not_found(self, client):
        res = client.get("/api/blueprints/nonexistent-id")
        assert res.status_code == 404

    def test_get_sections_deserialised_as_list(self, client):
        saved_id = _save(client, sections=[_section(), _section("B")]).json()["id"]
        res = client.get(f"/api/blueprints/{saved_id}")
        assert isinstance(res.json()["sections"], list)
        assert len(res.json()["sections"]) == 2


# ── list blueprints ───────────────────────────────────────────────────────────

class TestListBlueprints:
    def test_list_returns_all(self, client):
        _save(client, name="BP1")
        _save(client, name="BP2")
        res = client.get("/api/blueprints")
        assert res.status_code == 200
        names = [b["name"] for b in res.json()["blueprints"]]
        assert "BP1" in names and "BP2" in names

    def test_list_filter_by_subject(self, client):
        _save(client, name="Sci BP", subject="Science")
        _save(client, name="Math BP", subject="Mathematics")
        res = client.get("/api/blueprints?subject=Science")
        names = [b["name"] for b in res.json()["blueprints"]]
        assert "Sci BP" in names
        assert "Math BP" not in names

    def test_list_empty_initially(self, client):
        res = client.get("/api/blueprints")
        assert res.status_code == 200
        assert res.json()["blueprints"] == []


# ── delete blueprint ──────────────────────────────────────────────────────────

class TestDeleteBlueprint:
    def test_delete_existing(self, client):
        saved_id = _save(client).json()["id"]
        res = client.delete(f"/api/blueprints/{saved_id}")
        assert res.status_code == 200
        assert res.json()["status"] == "ok"

    def test_delete_removes_from_list(self, client):
        saved_id = _save(client).json()["id"]
        client.delete(f"/api/blueprints/{saved_id}")
        res = client.get("/api/blueprints")
        ids = [b["id"] for b in res.json()["blueprints"]]
        assert saved_id not in ids

    def test_delete_not_found(self, client):
        res = client.delete("/api/blueprints/nonexistent-id")
        assert res.status_code == 404


# ── DB migration safety ───────────────────────────────────────────────────────

class TestMigrationSafety:
    def test_sections_meta_column_exists_on_papers(self, client, test_db):
        """sections_meta column added to papers table without breaking existing rows."""
        from app.core.database import get_connection
        conn = get_connection()
        cols = {row[1] for row in conn.execute("PRAGMA table_info(papers)").fetchall()}
        conn.close()
        assert "sections_meta" in cols

    def test_blueprints_table_exists(self, client, test_db):
        from app.core.database import get_connection
        conn = get_connection()
        tables = {row[0] for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()}
        conn.close()
        assert "blueprints" in tables

    def test_old_paper_sections_meta_is_null(self, client, test_db):
        """Papers created before blueprint feature have sections_meta=NULL — no crash."""
        import uuid

        from app.core.database import get_connection
        from app.repositories import papers_repository
        pid = str(uuid.uuid4())
        papers_repository.insert(
            paper_id=pid, subject="Science", class_name=None,
            total_marks=10, question_ids=[], paper_title="Old Paper",
        )
        conn = get_connection()
        row = conn.execute("SELECT sections_meta FROM papers WHERE id = ?", (pid,)).fetchone()
        conn.close()
        assert row["sections_meta"] is None
