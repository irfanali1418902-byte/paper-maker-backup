"""GET /api/topic-plan + PATCH /api/topic-plan/{id} — R7 Marhala 1."""

from fastapi.testclient import TestClient

from app.main import app
from app.repositories import syllabus_repository, topic_week_plan_repository

client = TestClient(app)


def _topic(topic_id: str, title: str, subject: str = "Mathematics",
           grade: str = "Pre Year 2") -> None:
    syllabus_repository.insert(
        topic_id=topic_id,
        subject=subject,
        grade=grade,
        unit_no=1,
        unit_title="Mathematics",
        page_range="",
        subtopic_title=title,
        activity_type="Introduction",
        page_no=None,
        learning_outcome="",
    )


def test_get_topic_plan_returns_weeks_and_unassigned(test_db):
    _topic("t1", "Number 50")
    _topic("t2", "Small and big")
    topic_week_plan_repository.overwrite_assignments(
        [{"syllabus_topic_id": "t1", "week_no": 2, "position": None}]
    )

    res = client.get("/api/topic-plan", params={"subject": "Mathematics", "grade": "Pre Year 2"})

    assert res.status_code == 200
    body = res.json()
    assert body["subject"] == "Mathematics"
    assert body["grade"] == "Pre Year 2"
    assert body["total"] == 2
    assert body["has_plan"] is True
    assert [t["syllabus_topic_id"] for t in body["weeks"][1]["topics"]] == ["t1"]
    assert [t["syllabus_topic_id"] for t in body["unassigned"]] == ["t2"]


def test_get_topic_plan_includes_titles_for_the_ui(test_db):
    """UI ko id ke saath title chahiye, warna teacher ko sirf uuid dikhenge."""
    _topic("t1", "Number 50")

    res = client.get("/api/topic-plan", params={"subject": "Mathematics", "grade": "Pre Year 2"})

    topic = res.json()["unassigned"][0]
    assert topic["subtopic_title"] == "Number 50"


def test_get_topic_plan_empty_syllabus_is_200_not_a_crash(test_db):
    res = client.get("/api/topic-plan", params={"subject": "Mathematics", "grade": "Grade 9"})

    assert res.status_code == 200
    assert res.json()["total"] == 0


def test_get_topic_plan_requires_subject_and_grade(test_db):
    assert client.get("/api/topic-plan", params={"subject": "  ", "grade": "Pre Year 2"}).status_code == 400
    assert client.get("/api/topic-plan", params={"subject": "Mathematics", "grade": " "}).status_code == 400
    # Bilkul gair-maujood param = FastAPI ki apni validation (422)
    assert client.get("/api/topic-plan", params={"subject": "Mathematics"}).status_code == 422


def test_patch_moves_a_topic(test_db):
    _topic("t1", "Number 50")

    res = client.patch("/api/topic-plan/t1", json={"week_no": 6})

    assert res.status_code == 200
    assert res.json() == {"syllabus_topic_id": "t1", "week_no": 6}


def test_patch_to_week_zero_is_allowed(test_db):
    _topic("t1", "Number 50")

    assert client.patch("/api/topic-plan/t1", json={"week_no": 0}).status_code == 200


def test_patch_unknown_topic_is_404(test_db):
    res = client.patch("/api/topic-plan/ghost", json={"week_no": 1})

    assert res.status_code == 404
    assert "nahi mila" in res.json()["detail"]


def test_patch_out_of_range_week_is_400(test_db):
    _topic("t1", "Number 50")

    res = client.patch("/api/topic-plan/t1", json={"week_no": 999})

    assert res.status_code == 400
    assert "0 se 36" in res.json()["detail"]


def test_patch_non_integer_week_is_422(test_db):
    """Shape ki ghalti Pydantic pakadta hai, service tak pahunchti hi nahi."""
    _topic("t1", "Number 50")

    assert client.patch("/api/topic-plan/t1", json={"week_no": "teen"}).status_code == 422
    assert client.patch("/api/topic-plan/t1", json={}).status_code == 422


def test_topic_plan_is_scoped_to_its_grade(test_db):
    """Pre Year 2 ka plan Pre Year 3 ke topics na dikhaye -- syllabus mein har
    grade ke apne 87 topics hain."""
    _topic("t1", "PY2 ka topic", grade="Pre Year 2")
    _topic("t2", "PY3 ka topic", grade="Pre Year 3")

    res = client.get("/api/topic-plan", params={"subject": "Mathematics", "grade": "Pre Year 2"})

    ids = [t["syllabus_topic_id"] for t in res.json()["unassigned"]]
    assert ids == ["t1"]


# ---- Marhala 2: template + import ----


def test_template_downloads_as_xlsx(test_db):
    _topic("t1", "Number 50")

    res = client.get("/api/topic-plan/template",
                     params={"subject": "Mathematics", "grade": "Pre Year 2"})

    assert res.status_code == 200
    assert "spreadsheetml" in res.headers["content-type"]
    assert "topic_week_plan_Mathematics_Pre_Year_2.xlsx" in res.headers["content-disposition"]
    assert res.content[:2] == b"PK"  # xlsx = zip


def test_template_path_resolves_to_the_template_handler(test_db):
    """`/api/topic-plan/template` template hi de, kisi `{topic_id}` handler ko na
    jaye.

    AAJ ye fail nahi ho sakti aur ye baat saaf likhi jani chahiye: `{topic_id}`
    wala akela route PATCH hai, to GET /template us se takra hi nahi sakta.
    Ye pehra AAGE ke liye hai -- Marhala 3/4 mein GET /api/topic-plan/{topic_id}
    aana bilkul mumkin hai, aur agar wo /template se pehle likha gaya to
    "template" ek topic id samjha jayega aur 404 milega. Tab ye test bolegi."""
    _topic("t1", "Number 50")

    res = client.get("/api/topic-plan/template",
                     params={"subject": "Mathematics", "grade": "Pre Year 2"})

    assert res.status_code == 200
    assert res.headers["content-type"].startswith("application/vnd")


def test_template_requires_subject_and_grade(test_db):
    assert client.get("/api/topic-plan/template",
                      params={"subject": " ", "grade": "Pre Year 2"}).status_code == 400


def test_import_assigns_weeks_end_to_end(test_db):
    import io as _io

    import openpyxl as _openpyxl

    _topic("t1", "Number 50")
    wb = _openpyxl.Workbook()
    ws = wb.active
    ws.append(["syllabus_topic_id", "subtopic_title", "unit_no", "week_no"])
    ws.append(["t1", "Number 50", 1, 5])
    buf = _io.BytesIO()
    wb.save(buf)

    res = client.post(
        "/api/topic-plan/assign-import",
        files={"file": ("plan.xlsx", buf.getvalue(),
                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
    )

    assert res.status_code == 200
    assert res.json()["updated"] == 1

    plan = client.get("/api/topic-plan",
                      params={"subject": "Mathematics", "grade": "Pre Year 2"}).json()
    assert [t["syllabus_topic_id"] for t in plan["weeks"][4]["topics"]] == ["t1"]


def test_import_rejects_wrong_file_type(test_db):
    res = client.post(
        "/api/topic-plan/assign-import",
        files={"file": ("plan.txt", b"kuch bhi", "text/plain")},
    )

    assert res.status_code == 400
    assert "allowed" in res.json()["detail"]
