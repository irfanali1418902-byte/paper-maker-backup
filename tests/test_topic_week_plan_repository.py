"""topic_week_plan_repository — SQL layer. R7 Marhala 1."""

import pytest

from app.repositories import syllabus_repository, topic_week_plan_repository


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


def test_list_resolved_returns_planless_topics_too(test_db):
    """LEFT JOIN ka poora maqsad: bina plan wale topics bhi aayen (week_no None),
    warna teacher ko kabhi pata na chale ke kitna kaam baqi hai."""
    _topic("t1", "Number 50")
    _topic("t2", "Small and big")
    topic_week_plan_repository.overwrite_assignments(
        [{"syllabus_topic_id": "t1", "week_no": 3, "position": None}]
    )

    rows = topic_week_plan_repository.list_resolved("Mathematics", "Pre Year 2")

    assert len(rows) == 2
    by_id = {r["syllabus_topic_id"]: r for r in rows}
    assert by_id["t1"]["week_no"] == 3
    assert by_id["t2"]["week_no"] is None


def test_list_resolved_orders_planned_before_unplanned(test_db):
    """COALESCE(week_no, 9999): plan wale pehle, bin-plan aakhir mein."""
    _topic("t1", "Zed topic")
    _topic("t2", "Alpha topic")
    topic_week_plan_repository.overwrite_assignments(
        [{"syllabus_topic_id": "t1", "week_no": 1, "position": None}]
    )

    rows = topic_week_plan_repository.list_resolved("Mathematics", "Pre Year 2")

    assert [r["syllabus_topic_id"] for r in rows] == ["t1", "t2"]


def test_list_resolved_falls_back_to_syllabus_order(test_db):
    """Bin-plan topics syllabus ki apni tarteeb par aayen (unit_no -> page_no),
    alphabet par nahi -- warna "Number 10" aur "Number 9" ulte ho jayenge."""
    _topic("t1", "Zed", unit_no=1, page_no=5)
    _topic("t2", "Alpha", unit_no=1, page_no=9)
    _topic("t3", "Mid", unit_no=2, page_no=1)

    rows = topic_week_plan_repository.list_resolved("Mathematics", "Pre Year 2")

    assert [r["syllabus_topic_id"] for r in rows] == ["t1", "t2", "t3"]


def test_list_resolved_is_scoped_to_subject_and_grade(test_db):
    _topic("t1", "Mine")
    _topic("t2", "Doosri grade", grade="Pre Year 3")
    _topic("t3", "Doosra subject", subject="English")

    rows = topic_week_plan_repository.list_resolved("Mathematics", "Pre Year 2")

    assert [r["syllabus_topic_id"] for r in rows] == ["t1"]


def test_list_planned_is_inner_join(test_db):
    """list_planned coverage ka 'universe' hai -- sirf woh topics jinka plan is
    hafte mein hai. Bin-plan topics yahan nahi aane chahiye."""
    _topic("t1", "Planned")
    _topic("t2", "Not planned")
    topic_week_plan_repository.overwrite_assignments(
        [{"syllabus_topic_id": "t1", "week_no": 2, "position": None}]
    )

    rows = topic_week_plan_repository.list_planned("Mathematics", "Pre Year 2", 2)

    assert [r["syllabus_topic_id"] for r in rows] == ["t1"]
    assert topic_week_plan_repository.list_planned("Mathematics", "Pre Year 2", 3) == []


def test_list_planned_respects_teacher_position(test_db):
    _topic("t1", "Pehla", unit_no=1, page_no=1)
    _topic("t2", "Doosra", unit_no=1, page_no=2)
    topic_week_plan_repository.overwrite_assignments([
        {"syllabus_topic_id": "t1", "week_no": 1, "position": 2},
        {"syllabus_topic_id": "t2", "week_no": 1, "position": 1},
    ])

    rows = topic_week_plan_repository.list_planned("Mathematics", "Pre Year 2", 1)

    assert [r["syllabus_topic_id"] for r in rows] == ["t2", "t1"]


def test_overwrite_assignments_upserts_not_duplicates(test_db):
    """PK par ON CONFLICT: dobara likhna row badalta hai, nayi row nahi banata.
    Excel dobara upload karna is par khara hai (Marhala 2)."""
    _topic("t1", "Number 50")
    topic_week_plan_repository.overwrite_assignments(
        [{"syllabus_topic_id": "t1", "week_no": 3, "position": None}]
    )
    topic_week_plan_repository.overwrite_assignments(
        [{"syllabus_topic_id": "t1", "week_no": 7, "position": None}]
    )

    rows = topic_week_plan_repository.list_resolved("Mathematics", "Pre Year 2")

    assert len(rows) == 1
    assert rows[0]["week_no"] == 7


def test_overwrite_assignments_empty_list_is_a_noop(test_db):
    assert topic_week_plan_repository.overwrite_assignments([]) == 0


def test_clear_assignments_removes_the_row(test_db):
    """week_no NOT NULL hai, is liye "clear" ka matlab row ka na hona hai --
    0 likhna nahi (0 ka apna matlab Unassigned hai)."""
    _topic("t1", "Number 50")
    topic_week_plan_repository.overwrite_assignments(
        [{"syllabus_topic_id": "t1", "week_no": 3, "position": None}]
    )

    deleted = topic_week_plan_repository.clear_assignments(["t1"])

    assert deleted == 1
    rows = topic_week_plan_repository.list_resolved("Mathematics", "Pre Year 2")
    assert rows[0]["week_no"] is None


def test_clear_assignments_empty_list_is_a_noop(test_db):
    assert topic_week_plan_repository.clear_assignments([]) == 0


def test_existing_topic_ids_reports_only_real_ones(test_db):
    _topic("t1", "Real")

    found = topic_week_plan_repository.existing_topic_ids(["t1", "ghost"])

    assert found == {"t1"}
    assert topic_week_plan_repository.existing_topic_ids([]) == set()


@pytest.mark.parametrize("week_no", [0, 1, 36])
def test_week_no_boundaries_round_trip(test_db, week_no):
    """0 (Unassigned) aur N dono DB tak jaate hain -- range ka faisla service ka
    hai, repository ka nahi."""
    _topic("t1", "Number 50")
    topic_week_plan_repository.overwrite_assignments(
        [{"syllabus_topic_id": "t1", "week_no": week_no, "position": None}]
    )

    rows = topic_week_plan_repository.list_resolved("Mathematics", "Pre Year 2")

    assert rows[0]["week_no"] == week_no
