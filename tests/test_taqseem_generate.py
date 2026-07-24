"""POST /api/taqseem/generate — auto-taqseem (SLO -> N exams). Hissa 2, Tukda 2.

Split usool: sequence ASC; base = total//N, rem = total%N; pehle `rem` exams ko
base+1. NULL-sequence SLO kisi exam mein nahi jaate (exam_no 0). Maujooda plan
overwrite hota hai; response `overwritten` count deta hai.
"""

from app.repositories import settings_repository, slo_repository
from app.services import taqseem_service

CLASS = "Pre Year 1"
SUBJECT = "Mathematics"


def _set_exam_count(n: int) -> None:
    settings_repository.upsert(
        school_name="Test", school_name_ur="", address="", address_ur="",
        logo_base64=None, accent_color="#0e4d3c", exam_count=n,
    )


def _make_slo(slo_id: str, code: str, sequence=None, strand="Number") -> None:
    slo_repository.insert({
        "id": slo_id,
        "class": CLASS,
        "subject": SUBJECT,
        "slo_code": code,
        "slo_text": f"Outcome {code}",
        "bloom_level": None,
        "strand": strand,
        "sequence": sequence,
    })


def _exam_of(slo_id: str) -> int:
    """Us SLO ka resolved exam_no (0 = unassigned)."""
    plan = taqseem_service.get_plan(CLASS, SUBJECT)
    for e in plan["exams"]:
        if any(s["slo_id"] == slo_id for s in e["slos"]):
            return e["exam_no"]
    return 0


def test_even_split(test_db):
    _set_exam_count(4)
    for i in range(1, 9):  # 8 SLO, seq 1..8
        _make_slo(f"s{i}", f"M-{i:02d}", sequence=i)

    res = taqseem_service.generate_plan(CLASS, SUBJECT)
    assert res["exam_count"] == 4
    assert res["assigned"] == 8
    assert res["unassigned"] == 0
    assert res["overwritten"] == 0  # pehli dafa, koi purana plan nahi

    plan = taqseem_service.get_plan(CLASS, SUBJECT)
    assert [len(e["slos"]) for e in plan["exams"]] == [2, 2, 2, 2]


def test_uneven_split_front_loaded(test_db):
    """total=10, N=4 -> base=2, rem=2 -> pehle 2 exams ko 3, baaqi ko 2."""
    _set_exam_count(4)
    for i in range(1, 11):
        _make_slo(f"s{i}", f"M-{i:02d}", sequence=i)

    taqseem_service.generate_plan(CLASS, SUBJECT)
    plan = taqseem_service.get_plan(CLASS, SUBJECT)
    assert [len(e["slos"]) for e in plan["exams"]] == [3, 3, 2, 2]


def test_null_sequence_stays_unassigned(test_db):
    _set_exam_count(3)
    _make_slo("a", "M-01", sequence=1)
    _make_slo("b", "M-02", sequence=2)
    _make_slo("nx", "M-99", sequence=None)  # NULL seq
    _make_slo("ny", "M-98", sequence=None)

    res = taqseem_service.generate_plan(CLASS, SUBJECT)
    assert res["assigned"] == 2
    assert res["unassigned"] == 2

    plan = taqseem_service.get_plan(CLASS, SUBJECT)
    unassigned_ids = {s["slo_id"] for s in plan["unassigned"]}
    assert unassigned_ids == {"nx", "ny"}  # NULL-seq dono unassigned
    # assigned wale kisi exam mein
    assert _exam_of("a") in (1, 2, 3)
    assert _exam_of("b") in (1, 2, 3)


def test_split_orders_by_sequence_not_slo_code(test_db):
    """slo_code ulta hai, sequence seedha — split sequence par hona chahiye."""
    _set_exam_count(3)
    _make_slo("a", "M-90", sequence=1)  # code bada, seq pehla
    _make_slo("b", "M-50", sequence=2)
    _make_slo("c", "M-10", sequence=3)  # code chhota, seq aakhri

    taqseem_service.generate_plan(CLASS, SUBJECT)
    # seq 1->exam1, seq 2->exam2, seq 3->exam3 (agar slo_code se hota to ulta hota)
    assert _exam_of("a") == 1
    assert _exam_of("b") == 2
    assert _exam_of("c") == 3


def test_regenerate_reports_overwritten(test_db):
    _set_exam_count(2)
    for i in range(1, 5):
        _make_slo(f"s{i}", f"M-{i:02d}", sequence=i)

    first = taqseem_service.generate_plan(CLASS, SUBJECT)
    assert first["overwritten"] == 0

    second = taqseem_service.generate_plan(CLASS, SUBJECT)
    assert second["overwritten"] == 4  # sab 4 ka pehle plan tha


def test_more_exams_than_slos(test_db):
    """N > total -> pehle `total` exams ko 1-1, baaqi khaali."""
    _set_exam_count(5)
    _make_slo("a", "M-01", sequence=1)
    _make_slo("b", "M-02", sequence=2)

    taqseem_service.generate_plan(CLASS, SUBJECT)
    plan = taqseem_service.get_plan(CLASS, SUBJECT)
    assert [len(e["slos"]) for e in plan["exams"]] == [1, 1, 0, 0, 0]


def test_route_blank_class_400(test_db):
    from fastapi.testclient import TestClient

    from app.main import app

    client = TestClient(app)
    resp = client.post("/api/taqseem/generate", json={"class_name": "  ", "subject": "Math"})
    assert resp.status_code == 400
