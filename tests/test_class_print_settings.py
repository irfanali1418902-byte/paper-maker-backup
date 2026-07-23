"""Marhala 4A — per-class print settings: migration columns, resolution
service (row-level fallback + class-name normalization), and the
GET /api/print-settings endpoint.
"""

import pytest
from fastapi.testclient import TestClient

from app.repositories import class_print_settings_repository, settings_repository
from app.services import class_print_settings_service


@pytest.fixture
def client(test_db):
    from app.main import app

    return TestClient(app)


def _save_globals(font=14, gap=14, margin=14):
    settings_repository.upsert(
        school_name="S",
        school_name_ur="",
        address="",
        address_ur="",
        logo_base64=None,
        accent_color="#000",
        print_font_size=font,
        print_q_gap=gap,
        print_page_margin=margin,
    )


# ---- migration --------------------------------------------------------------


def test_school_settings_has_print_default_columns(test_db):
    """init_db migration must add print_* columns with DEFAULT 14."""
    _save_globals()  # writes without setting print_* -> defaults apply
    saved = settings_repository.get()
    assert saved["print_font_size"] == 14
    assert saved["print_q_gap"] == 14
    assert saved["print_page_margin"] == 14


# ---- resolution: fallback ---------------------------------------------------


def test_fresh_db_returns_model_defaults(test_db):
    """No settings row, no class row -> SchoolSettings() defaults 14/14/14."""
    assert class_print_settings_service.get_print_settings("Class 5") == {
        "font_size": 14,
        "q_gap": 14,
        "page_margin": 14,
    }


def test_no_class_row_falls_back_to_global(test_db):
    _save_globals(font=16, gap=18, margin=20)
    assert class_print_settings_service.get_print_settings("Class 5") == {
        "font_size": 16,
        "q_gap": 18,
        "page_margin": 20,
    }


@pytest.mark.parametrize("class_name", ["", "   ", None])
def test_blank_class_falls_back_to_global(test_db, class_name):
    _save_globals(font=16, gap=18, margin=20)
    assert class_print_settings_service.get_print_settings(class_name) == {
        "font_size": 16,
        "q_gap": 18,
        "page_margin": 20,
    }


# ---- resolution: per-class row wins -----------------------------------------


def test_class_row_overrides_global(test_db):
    _save_globals(font=16, gap=18, margin=20)
    class_print_settings_repository.upsert("class 5", font_size=13, q_gap=10, page_margin=12)
    assert class_print_settings_service.get_print_settings("Class 5") == {
        "font_size": 13,
        "q_gap": 10,
        "page_margin": 12,
    }


@pytest.mark.parametrize("lookup", ["Class 5", "class 5", "  CLASS 5 ", "CLASS 5"])
def test_lookup_is_normalized(test_db, lookup):
    """normalize_class collapses case/whitespace so one row serves all forms."""
    class_print_settings_repository.upsert("class 5", font_size=13, q_gap=10, page_margin=12)
    assert class_print_settings_service.get_print_settings(lookup)["font_size"] == 13


def test_other_class_still_gets_global(test_db):
    _save_globals(font=16, gap=18, margin=20)
    class_print_settings_repository.upsert("class 5", font_size=13, q_gap=10, page_margin=12)
    assert class_print_settings_service.get_print_settings("Grade 2") == {
        "font_size": 16,
        "q_gap": 18,
        "page_margin": 20,
    }


def test_repository_upsert_replaces_existing(test_db):
    class_print_settings_repository.upsert("class 5", 13, 10, 12)
    class_print_settings_repository.upsert("class 5", 20, 22, 24)
    row = class_print_settings_repository.get("class 5")
    assert (row["font_size"], row["q_gap"], row["page_margin"]) == (20, 22, 24)


# ---- endpoint ---------------------------------------------------------------


def test_endpoint_returns_global_when_no_class_row(client):
    r = client.get("/api/print-settings", params={"class_name": "Class 5"})
    assert r.status_code == 200
    assert r.json() == {"font_size": 14, "q_gap": 14, "page_margin": 14}


def test_endpoint_returns_class_override(client):
    class_print_settings_repository.upsert("class 5", font_size=13, q_gap=10, page_margin=12)
    r = client.get("/api/print-settings", params={"class_name": "Class 5"})
    assert r.status_code == 200
    assert r.json() == {"font_size": 13, "q_gap": 10, "page_margin": 12}


def test_endpoint_without_class_name_uses_global_default(client):
    r = client.get("/api/print-settings")
    assert r.status_code == 200
    assert r.json() == {"font_size": 14, "q_gap": 14, "page_margin": 14}


# ---- POST endpoint (Marhala 4B) --------------------------------------------


def test_post_saves_then_get_returns_it(client):
    r = client.post(
        "/api/print-settings",
        json={"class_name": "Pre year 1", "font_size": 18, "q_gap": 20, "page_margin": 16},
    )
    assert r.status_code == 200
    assert r.json() == {"status": "saved"}

    g = client.get("/api/print-settings", params={"class_name": "Pre year 1"})
    assert g.json() == {"font_size": 18, "q_gap": 20, "page_margin": 16}


def test_post_normalizes_class_key(client):
    """Save with one casing, read with another -> same row."""
    client.post(
        "/api/print-settings",
        json={"class_name": "  PRE YEAR 1 ", "font_size": 12, "q_gap": 8, "page_margin": 11},
    )
    g = client.get("/api/print-settings", params={"class_name": "pre year 1"})
    assert g.json() == {"font_size": 12, "q_gap": 8, "page_margin": 11}


def test_post_upsert_overwrites(client):
    payload = {"class_name": "Class 5", "font_size": 14, "q_gap": 14, "page_margin": 14}
    client.post("/api/print-settings", json=payload)
    client.post("/api/print-settings", json={**payload, "font_size": 19, "q_gap": 24, "page_margin": 22})
    g = client.get("/api/print-settings", params={"class_name": "Class 5"})
    assert g.json() == {"font_size": 19, "q_gap": 24, "page_margin": 22}


def test_post_blank_class_is_400(client):
    r = client.post(
        "/api/print-settings",
        json={"class_name": "   ", "font_size": 14, "q_gap": 14, "page_margin": 14},
    )
    assert r.status_code == 400


@pytest.mark.parametrize(
    "field,value",
    [
        ("font_size", 10), ("font_size", 21),
        ("q_gap", 5), ("q_gap", 31),
        ("page_margin", 9), ("page_margin", 26),
    ],
)
def test_post_out_of_bounds_is_422(client, field, value):
    payload = {"class_name": "Class 5", "font_size": 14, "q_gap": 14, "page_margin": 14}
    payload[field] = value
    r = client.post("/api/print-settings", json=payload)
    assert r.status_code == 422
    # Rejected value must not have been persisted.
    g = client.get("/api/print-settings", params={"class_name": "Class 5"})
    assert g.json() == {"font_size": 14, "q_gap": 14, "page_margin": 14}


@pytest.mark.parametrize("bound", [11, 20])
def test_post_accepts_boundary_font(client, bound):
    r = client.post(
        "/api/print-settings",
        json={"class_name": "Class 5", "font_size": bound, "q_gap": 14, "page_margin": 14},
    )
    assert r.status_code == 200
