"""Hissa 5-A: bloom_standards.get_bloom_suggestion canonical values ka guard.

blueprint.html ka BLOOM_STD frontend mirror manually sync hota hai — yeh test us
source-of-truth ke exact percentages pin karta taake drift pakda jaye (agar Python
badle to yeh fail ho, mirror update yaad dilaye)."""

from app.core.bloom_standards import get_bloom_suggestion


def test_pre_primary_distribution():
    s = get_bloom_suggestion("Pre Year 1")
    assert s["group"] == "Pre-Primary"
    assert s["distribution"] == {
        "remember": 70, "understand": 30, "apply": 0, "analyze": 0, "evaluate": 0,
    }


def test_primary_distribution():
    s = get_bloom_suggestion("Grade 3")
    assert s["group"] == "Primary"
    assert s["distribution"] == {
        "remember": 30, "understand": 35, "apply": 25, "analyze": 10, "evaluate": 0,
    }


def test_middle_distribution():
    s = get_bloom_suggestion("Class 8")
    assert s["group"] == "Middle"
    assert s["distribution"] == {
        "remember": 20, "understand": 30, "apply": 30, "analyze": 20, "evaluate": 0,
    }


def test_matric_distribution():
    s = get_bloom_suggestion("Grade 10")
    assert s["group"] == "Matric"
    assert s["distribution"] == {
        "remember": 15, "understand": 25, "apply": 30, "analyze": 20, "evaluate": 10,
    }


def test_normalize_matches_variants():
    # lower + spaces/dash/underscore collapse — frontend normalizeClassName ka mirror
    for variant in ["grade 1", "Grade  1", "GRADE-1", "grade_1", " grade 1 "]:
        assert get_bloom_suggestion(variant)["group"] == "Primary"


def test_unknown_class_returns_none():
    assert get_bloom_suggestion("Class 99") is None
    assert get_bloom_suggestion("") is None
