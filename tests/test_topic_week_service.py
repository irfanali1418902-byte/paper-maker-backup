"""topic_week_service — hafta-war plan ki business logic. R7 Marhala 1."""

import pytest

from app.repositories import syllabus_repository, topic_week_plan_repository
from app.services import topic_week_service


def _topic(topic_id: str, title: str, unit_no: int = 1, page_no=None,
           subject: str = "Mathematics", grade: str = "Pre Year 2") -> None:
    syllabus_repository.insert(
        topic_id=topic_id,
        subject=subject,
        grade=grade,
        unit_no=unit_no,
        unit_title="Mathematics",
        page_range="",
        subtopic_title=title,
        activity_type="Introduction",
        page_no=page_no,
        learning_outcome="",
    )


# ---- _week_count — taqseem ke _exam_count() jaisa bartao ----


def test_week_count_defaults_to_36_when_unset(test_db):
    assert topic_week_service._week_count() == 36


@pytest.mark.parametrize("bad", [None, "", "teen", [], {}])
def test_week_count_falls_back_on_garbage(test_db, monkeypatch, bad):
    """int() na bane to default -- crash nahi. Yehi _exam_count() ka usool hai."""
    monkeypatch.setattr(
        topic_week_service.settings_service, "get_settings", lambda: {"week_count": bad}
    )
    assert topic_week_service._week_count() == 36


@pytest.mark.parametrize("bad", [0, -5])
def test_week_count_rejects_less_than_one(test_db, monkeypatch, bad):
    monkeypatch.setattr(
        topic_week_service.settings_service, "get_settings", lambda: {"week_count": bad}
    )
    assert topic_week_service._week_count() == 36


def test_week_count_uses_the_setting_when_valid(test_db, monkeypatch):
    monkeypatch.setattr(
        topic_week_service.settings_service, "get_settings", lambda: {"week_count": 12}
    )
    assert topic_week_service._week_count() == 12


# ---- get_plan ----


def test_get_plan_buckets_topics_by_week(test_db, monkeypatch):
    monkeypatch.setattr(topic_week_service, "_week_count", lambda: 4)
    _topic("t1", "Number 50")
    _topic("t2", "Small and big")
    topic_week_plan_repository.overwrite_assignments([
        {"syllabus_topic_id": "t1", "week_no": 1, "position": None},
        {"syllabus_topic_id": "t2", "week_no": 3, "position": None},
    ])

    plan = topic_week_service.get_plan("Mathematics", "Pre Year 2")

    assert plan["week_count"] == 4
    assert len(plan["weeks"]) == 4
    assert [t["syllabus_topic_id"] for t in plan["weeks"][0]["topics"]] == ["t1"]
    assert [t["syllabus_topic_id"] for t in plan["weeks"][2]["topics"]] == ["t2"]
    assert plan["weeks"][1]["topics"] == []
    assert plan["unassigned"] == []
    assert plan["total"] == 2


def test_get_plan_has_plan_is_false_before_anything_is_assigned(test_db):
    _topic("t1", "Number 50")

    plan = topic_week_service.get_plan("Mathematics", "Pre Year 2")

    assert plan["has_plan"] is False
    assert plan["total"] == 1
    assert [t["syllabus_topic_id"] for t in plan["unassigned"]] == ["t1"]


def test_get_plan_has_plan_is_true_once_any_row_exists(test_db):
    _topic("t1", "Number 50")
    topic_week_plan_repository.overwrite_assignments(
        [{"syllabus_topic_id": "t1", "week_no": 0, "position": None}]
    )

    plan = topic_week_service.get_plan("Mathematics", "Pre Year 2")

    # week_no 0 = Unassigned bucket, magar plan "ban chuka" hai.
    assert plan["has_plan"] is True
    assert [t["syllabus_topic_id"] for t in plan["unassigned"]] == ["t1"]


def test_get_plan_puts_out_of_range_weeks_in_unassigned(test_db, monkeypatch):
    """N ghat jaye (misal 36 -> 4) to purane hafte >N ho jaate hain. Wo topics
    gum nahi hone chahiye -- Unassigned mein aayen. Yehi taqseem ka bartao hai."""
    monkeypatch.setattr(topic_week_service, "_week_count", lambda: 4)
    _topic("t1", "Purana hafta 30")
    topic_week_plan_repository.overwrite_assignments(
        [{"syllabus_topic_id": "t1", "week_no": 30, "position": None}]
    )

    plan = topic_week_service.get_plan("Mathematics", "Pre Year 2")

    assert [t["syllabus_topic_id"] for t in plan["unassigned"]] == ["t1"]
    assert all(w["topics"] == [] for w in plan["weeks"])


def test_get_plan_on_empty_syllabus_does_not_crash(test_db, monkeypatch):
    """Khali data par crash nahi -- PRD §6 ka usool."""
    monkeypatch.setattr(topic_week_service, "_week_count", lambda: 3)

    plan = topic_week_service.get_plan("Mathematics", "Grade 9")

    assert plan["total"] == 0
    assert plan["has_plan"] is False
    assert len(plan["weeks"]) == 3
    assert plan["unassigned"] == []


# ---- move_topic ----


def test_move_topic_sets_the_week(test_db):
    _topic("t1", "Number 50")

    result = topic_week_service.move_topic("t1", 5)

    assert result == {"syllabus_topic_id": "t1", "week_no": 5}
    rows = topic_week_plan_repository.list_resolved("Mathematics", "Pre Year 2")
    assert rows[0]["week_no"] == 5


def test_move_topic_to_zero_is_unassigned_not_an_error(test_db):
    _topic("t1", "Number 50")
    topic_week_service.move_topic("t1", 5)

    topic_week_service.move_topic("t1", 0)

    plan = topic_week_service.get_plan("Mathematics", "Pre Year 2")
    assert [t["syllabus_topic_id"] for t in plan["unassigned"]] == ["t1"]


def test_move_topic_clears_stale_position(test_db):
    """Hafta badalne ke baad purani jagah ki tarteeb be-maani hai."""
    _topic("t1", "Number 50")
    topic_week_plan_repository.overwrite_assignments(
        [{"syllabus_topic_id": "t1", "week_no": 1, "position": 7}]
    )

    topic_week_service.move_topic("t1", 2)

    rows = topic_week_plan_repository.list_resolved("Mathematics", "Pre Year 2")
    assert rows[0]["position"] is None


def test_move_topic_unknown_id_raises_not_found(test_db):
    with pytest.raises(topic_week_service.TopicNotFoundError):
        topic_week_service.move_topic("ghost", 1)


@pytest.mark.parametrize("bad_week", [-1, 37, 999])
def test_move_topic_rejects_out_of_range(test_db, bad_week):
    """Range se bahar chup-chaap Unassigned mein girana teacher ko dhoka dena hai."""
    _topic("t1", "Number 50")

    with pytest.raises(ValueError):
        topic_week_service.move_topic("t1", bad_week)


@pytest.mark.parametrize("bad_week", ["teen", None, [], {}])
def test_move_topic_rejects_non_numbers(test_db, bad_week):
    _topic("t1", "Number 50")

    with pytest.raises(ValueError):
        topic_week_service.move_topic("t1", bad_week)


def test_move_topic_rejects_before_writing_anything(test_db):
    """Ghalat input par DB mein aadha kaam na ho jaye."""
    _topic("t1", "Number 50")

    with pytest.raises(ValueError):
        topic_week_service.move_topic("t1", 999)

    rows = topic_week_plan_repository.list_resolved("Mathematics", "Pre Year 2")
    assert rows[0]["week_no"] is None
