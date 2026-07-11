"""Hardcoded blueprint presets — starting templates for common exam patterns.

Each preset is a dict matching the BlueprintSection schema.
Teacher picks one → sections load in the builder → then edits.
"""

from __future__ import annotations

PRESETS: dict[str, dict] = {
    "nce_pre_year": {
        "id": "nce_pre_year",
        "name": "NCE Pre-Year Pattern",
        "subject": None,
        "grade": None,
        "sections": [
            {
                "heading": "Section A — Objective (MCQ)",
                "question_types": ["multiple-choice"],
                "topic_ids": [],
                "count": 20,
                "marks_each": 1,
                "source_filter": "manual",
            },
            {
                "heading": "Section B — Fill in the Blank",
                "question_types": ["fill-in-the-blank"],
                "topic_ids": [],
                "count": 10,
                "marks_each": 1,
                "source_filter": "manual",
            },
            {
                "heading": "Section C — Short Answer",
                "question_types": ["short-answer"],
                "topic_ids": [],
                "count": 8,
                "marks_each": 3,
                "source_filter": "manual",
            },
        ],
    },
    "matric_board": {
        "id": "matric_board",
        "name": "Matric Board Pattern (Grade 9–10)",
        "subject": None,
        "grade": None,
        "sections": [
            {
                "heading": "Section A — Objective (MCQ)",
                "question_types": ["multiple-choice"],
                "topic_ids": [],
                "count": 15,
                "marks_each": 1,
                "source_filter": "manual",
            },
            {
                "heading": "Section B — True / False",
                "question_types": ["true-false"],
                "topic_ids": [],
                "count": 10,
                "marks_each": 1,
                "source_filter": "manual",
            },
            {
                "heading": "Section C — Short Answer",
                "question_types": ["short-answer"],
                "topic_ids": [],
                "count": 6,
                "marks_each": 5,
                "source_filter": "manual",
            },
        ],
    },
    "quick_quiz": {
        "id": "quick_quiz",
        "name": "Quick Quiz (Mixed)",
        "subject": None,
        "grade": None,
        "sections": [
            {
                "heading": "Section A — MCQ",
                "question_types": ["multiple-choice"],
                "topic_ids": [],
                "count": 10,
                "marks_each": 1,
                "source_filter": "manual",
            },
            {
                "heading": "Section B — True / False",
                "question_types": ["true-false"],
                "topic_ids": [],
                "count": 5,
                "marks_each": 1,
                "source_filter": "manual",
            },
        ],
    },
}


def list_presets() -> list[dict]:
    return list(PRESETS.values())


def get_preset(preset_id: str) -> dict | None:
    return PRESETS.get(preset_id)
