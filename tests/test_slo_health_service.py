"""SLO Health service — Marhala 2 Hissa C. Seed-based, koi hardcoded DB count nahi."""

from app.repositories import (
    question_slo_repository,
    questions_repository,
    slo_repository,
    syllabus_repository,
)
from app.services import slo_health_service


def _topic(tid: str, subject: str = "Mathematics", grade: str = "Pre Year 1") -> None:
    syllabus_repository.insert(
        topic_id=tid, subject=subject, grade=grade, unit_no=1,
        unit_title="Unit", page_range="1-2", subtopic_title=f"Sub {tid}",
        activity_type="reading", page_no=1, learning_outcome="LO",
    )


def _q(qid: str, subject: str = "Mathematics", status: str = "published",
       topic_id: str | None = None) -> None:
    questions_repository.insert({
        "id": qid, "subject": subject, "topic": "Counting",
        "bloom_level": "REMEMBER", "difficulty": "easy",
        "question_type": "short-answer", "marks": 1,
        "question_en": "Q", "question_ur": None,
        "options_en": "[]", "options_ur": "[]",
        "correct_answer_en": None, "correct_answer_ur": None,
        "explanation_en": None, "explanation_ur": None,
        "visual_emoji": None, "visual_count": None,
        "status": status, "syllabus_topic_id": topic_id,
    })


def _slo(sid: str, code: str, strand: str = "Number", cls: str = "Pre Year 1",
         subject: str = "Mathematics", bloom: str | None = None) -> None:
    slo_repository.insert({
        "id": sid, "class": cls, "subject": subject,
        "slo_code": code, "slo_text": f"Outcome {code}",
        "bloom_level": bloom, "strand": strand,
    })


def _line(health: dict, nclass: str, nsubject: str) -> dict:
    return next(h for h in health["health_lines"]
               if h["norm_class"] == nclass and h["norm_subject"] == nsubject)


def test_draft_note_present(test_db):
    health = slo_health_service.compute_health()
    assert "draft" in health["draft_note"].lower()


def test_slo_without_question_listed(test_db):
    _slo("s1", "N-01", strand="Number")
    health = slo_health_service.compute_health()
    line = _line(health, "pre year 1", "mathematics")
    assert line["slo_count"] == 1
    assert line["covered_count"] == 0
    assert line["uncovered_count"] == 1
    grp = next(g for g in health["slos_without_question"]
               if g["norm_class"] == "pre year 1")
    assert grp["total"] == 1
    assert [b["slo_code"] for st in grp["by_strand"] for b in st["slos"]] == ["N-01"]


def test_published_question_covers_slo(test_db):
    _q("q1")
    _slo("s1", "N-01")
    question_slo_repository.replace_for_question("q1", ["s1"])
    health = slo_health_service.compute_health()
    line = _line(health, "pre year 1", "mathematics")
    assert line["covered_count"] == 1
    # covered ho gaya to Part-2 mein na aaye
    assert all(g["norm_class"] != "pre year 1" or g["total"] == 0
               for g in health["slos_without_question"])


def test_draft_question_does_not_cover(test_db):
    """SLO sirf ek DRAFT question se juda ho to woh covered NA ho."""
    _q("q1", status="draft")
    _slo("s1", "N-01")
    question_slo_repository.replace_for_question("q1", ["s1"])
    health = slo_health_service.compute_health()
    line = _line(health, "pre year 1", "mathematics")
    assert line["covered_count"] == 0
    assert line["uncovered_count"] == 1


def test_untagged_question_class_na_maloom(test_db):
    """Bina syllabus_topic ke published question -> class na-maloom untagged bucket."""
    _q("q1")  # koi topic nahi, koi SLO link nahi
    health = slo_health_service.compute_health()
    bucket = next(u for u in health["untagged_questions"]
                  if u["norm_subject"] == "mathematics")
    assert bucket["class"] == "(class na-maloom)"
    assert bucket["count"] == 1


def test_untagged_question_with_grade(test_db):
    """Topic-linked question ka grade class ban jaye (na-maloom nahi)."""
    _topic("t1", grade="Grade 4")
    _q("q1", topic_id="t1")
    health = slo_health_service.compute_health()
    bucket = next(u for u in health["untagged_questions"]
                  if u["norm_class"] == "grade 4")
    assert bucket["count"] == 1
    assert bucket["class"] == "Grade 4"


def test_bloom_null_bucket(test_db):
    """bloom_level NULL SLO by_bloom mein '(bloom na-maloom)' bucket mein jaye."""
    _slo("s1", "N-01", bloom=None)
    _slo("s2", "N-02", bloom="apply")
    health = slo_health_service.compute_health()
    grp = next(g for g in health["slos_without_question"]
               if g["norm_class"] == "pre year 1")
    buckets = {b["bloom"]: b["count"] for b in grp["by_bloom"]}
    assert buckets.get("(bloom na-maloom)") == 1
    assert buckets.get("apply") == 1


def test_import_pending_from_syllabus(test_db):
    """Jis syllabus grade/subject ka SLO nahi woh import_pending mein; jiska hai woh nahi."""
    _topic("t1", subject="Geography", grade="Grade 8")   # koi SLO nahi
    _topic("t2", subject="Mathematics", grade="Pre Year 1")
    _slo("s1", "N-01", cls="Pre Year 1", subject="Mathematics")
    health = slo_health_service.compute_health()
    pending_keys = {(p["norm_class"], p["norm_subject"]) for p in health["import_pending"]}
    assert ("grade 8", "geography") in pending_keys
    assert ("pre year 1", "mathematics") not in pending_keys


def test_case_normalize_subject_and_class(test_db):
    """SLO 'Mathematics'/'Pre Year 1' aur question 'math'/grade 'pre year 1 '
    ek hi health line mein aayen (case/alias normalize)."""
    _topic("t1", subject="Math", grade="pre year 1 ")
    _q("q1", subject="math", topic_id="t1")
    _slo("s1", "N-01", cls="Pre Year 1", subject="Mathematics")
    question_slo_repository.replace_for_question("q1", ["s1"])
    health = slo_health_service.compute_health()
    line = _line(health, "pre year 1", "mathematics")
    assert line["slo_count"] == 1
    assert line["covered_count"] == 1
    assert line["question_count"] == 1
    assert line["tagged_count"] == 1


def test_filter_narrows_sections(test_db):
    _slo("s1", "N-01", cls="Pre Year 1", subject="Mathematics")
    _slo("s2", "G-01", cls="Grade 7", subject="Science")
    all_health = slo_health_service.compute_health()
    assert {h["norm_class"] for h in all_health["health_lines"]} >= {"pre year 1", "grade 7"}

    filtered = slo_health_service.compute_health(class_filter="Grade 7")
    assert {h["norm_class"] for h in filtered["health_lines"]} == {"grade 7"}
    # dropdown lists filter ke bawajood poore rahein
    assert set(filtered["classes"]) >= {"Pre Year 1", "Grade 7"}


def test_multi_class_general_no_hardcode(test_db):
    """Do alag class/subject dono apni health line paayen — koi hardcode nahi."""
    _q("q1", subject="Science", topic_id="t1")
    _topic("t1", subject="Science", grade="Grade 7")
    _slo("s1", "SCI-01", cls="Grade 7", subject="Science")
    question_slo_repository.replace_for_question("q1", ["s1"])
    _slo("s2", "N-01", cls="Pre Year 1", subject="Mathematics")
    health = slo_health_service.compute_health()
    sci = _line(health, "grade 7", "science")
    assert sci["covered_count"] == 1
    math = _line(health, "pre year 1", "mathematics")
    assert math["covered_count"] == 0
