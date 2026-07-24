"""POST /api/taqseem/move — per-move SLO assignment. Hissa 2, Tukda 3.

exam_no 0 = Unassigned (valid); range 0..N se bahar = 400; slo_id na mile = 404;
position optional. Sirf isi SLO ki row badalti hai.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.repositories import settings_repository, slo_repository
from app.services import taqseem_service

CLASS = "Pre Year 1"
SUBJECT = "Mathematics"


def _set_exam_count(n: int) -> None:
    settings_repository.upsert(
        school_name="Test", school_name_ur="", address="", address_ur="",
        logo_base64=None, accent_color="#0e4d3c", exam_count=n,
    )


def _make_slo(slo_id: str, code: str, sequence=None) -> None:
    slo_repository.insert({
        "id": slo_id, "class": CLASS, "subject": SUBJECT,
        "slo_code": code, "slo_text": f"Outcome {code}",
        "bloom_level": None, "strand": "Number", "sequence": sequence,
    })


def _exam_of(slo_id: str) -> int:
    plan = taqseem_service.get_plan(CLASS, SUBJECT)
    for e in plan["exams"]:
        if any(s["slo_id"] == slo_id for s in e["slos"]):
            return e["exam_no"]
    return 0


def test_move_to_exam(test_db):
    _set_exam_count(4)
    _make_slo("a", "M-01", sequence=1)

    res = taqseem_service.move_slo("a", 3, position=2)
    assert res == {"slo_id": "a", "exam_no": 3, "position": 2}
    assert _exam_of("a") == 3


def test_move_to_unassigned_zero_ok(test_db):
    _set_exam_count(4)
    _make_slo("a", "M-01", sequence=1)
    taqseem_service.move_slo("a", 2)  # pehle exam 2 mein
    assert _exam_of("a") == 2

    taqseem_service.move_slo("a", 0)  # ab Unassigned
    plan = taqseem_service.get_plan(CLASS, SUBJECT)
    assert "a" in {s["slo_id"] for s in plan["unassigned"]}


def test_move_position_optional(test_db):
    _set_exam_count(4)
    _make_slo("a", "M-01", sequence=1)
    res = taqseem_service.move_slo("a", 1)  # position na diya
    assert res["position"] is None
    assert _exam_of("a") == 1


def test_exam_no_above_n_rejected(test_db):
    _set_exam_count(4)
    _make_slo("a", "M-01", sequence=1)
    with pytest.raises(ValueError):  # N=4, 5 out of range
        taqseem_service.move_slo("a", 5)


def test_exam_no_negative_rejected(test_db):
    _set_exam_count(4)
    _make_slo("a", "M-01", sequence=1)
    with pytest.raises(ValueError):
        taqseem_service.move_slo("a", -1)


def test_missing_slo_raises(test_db):
    _set_exam_count(4)
    with pytest.raises(taqseem_service.SloNotFoundError):
        taqseem_service.move_slo("ghost", 1)


# --- route-level status codes ---

def test_route_move_ok(test_db):
    _set_exam_count(4)
    _make_slo("a", "M-01", sequence=1)
    client = TestClient(app)
    resp = client.post("/api/taqseem/move", json={"slo_id": "a", "exam_no": 2})
    assert resp.status_code == 200
    assert resp.json()["exam_no"] == 2


def test_route_out_of_range_400(test_db):
    _set_exam_count(4)
    _make_slo("a", "M-01", sequence=1)
    client = TestClient(app)
    resp = client.post("/api/taqseem/move", json={"slo_id": "a", "exam_no": 99})
    assert resp.status_code == 400


def test_route_missing_slo_404(test_db):
    _set_exam_count(4)
    client = TestClient(app)
    resp = client.post("/api/taqseem/move", json={"slo_id": "ghost", "exam_no": 1})
    assert resp.status_code == 404
