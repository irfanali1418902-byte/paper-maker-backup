"""Assembles a paper from a Blueprint — section by section, partial-friendly.

Design rules:
- Har section ke liye available questions fetch karo; jitne hain utne use karo.
- Shortfall (maange zyada, mile kam) note karo — poora paper nahi rokta.
- Error sirf tab jab poore paper mein zero questions mile (sab sections khaali).
- sections_meta JSON paper row mein store hoti hai (print.html ke liye).
- Questions ki image_path automatic saath aati hai — koi extra step nahi.
"""

from __future__ import annotations

import uuid
from datetime import date
from typing import Optional

from app.core.database import get_connection
from app.repositories import papers_repository, questions_repository
from app.services import item_analysis_service


def assemble_blueprint_paper(
    blueprint_id: Optional[str],
    sections_input: list[dict],
    subject: Optional[str],
    class_name: Optional[str],
    paper_title: Optional[str],
) -> dict | None:
    """Core assembly — called by route with either a saved blueprint_id
    (sections_input ignored) or inline sections_input list.

    Returns assembled paper dict, or None if every section yielded zero
    questions (caller maps to 404).

    sections_input element shape:
        heading, question_types (list), topic_ids (list), count,
        marks_each, source_filter
    """
    all_question_ids: list[str] = []
    all_questions: list[dict] = []
    sections_meta: list[dict] = []
    shortfall_notes: list[str] = []

    for sec in sections_input:
        heading       = sec.get("heading", "Section")
        qtypes        = sec.get("question_types") or []
        topic_ids     = sec.get("topic_ids") or []
        wanted        = int(sec.get("count", 1))
        marks_each    = int(sec.get("marks_each", 1))
        source_filter = sec.get("source_filter", "manual")
        source_arg    = None if source_filter == "all" else source_filter

        # Fetch candidates for this section
        candidates = _fetch_section_candidates(
            subject=subject,
            topic_ids=topic_ids,
            question_types=qtypes,
            source=source_arg,
        )

        # Slice to wanted count (already ordered by usage_count ASC)
        picked = candidates[:wanted]
        found  = len(picked)

        if found < wanted:
            shortfall_notes.append(
                f"{heading}: {wanted} maange, {found} mile"
            )

        # Bump usage counts
        for q in picked:
            questions_repository.increment_usage_count(q["id"])

        sec_qids = [q["id"] for q in picked]
        sec_marks = sum(marks_each for _ in picked)

        sections_meta.append({
            "heading":      heading,
            "question_ids": sec_qids,
            "marks":        sec_marks,
            "shortfall":    wanted - found,
        })

        all_question_ids.extend(sec_qids)
        all_questions.extend(picked)

    # If every section is empty — caller sends 404
    if not all_questions:
        return None

    # Annotate difficulty mismatch (same as other paper types)
    _annotate_expected_difficulty(all_questions)

    total_marks = sum(q["marks"] for q in all_questions)
    resolved_title = _resolve_title(paper_title, subject or "", class_name)

    paper_id = str(uuid.uuid4())
    papers_repository.insert(
        paper_id=paper_id,
        subject=subject or "",
        class_name=class_name,
        total_marks=total_marks,
        question_ids=all_question_ids,
        paper_title=resolved_title,
        sections_meta=sections_meta,
    )

    return {
        "paper_id":       paper_id,
        "total_marks":    total_marks,
        "questions":      all_questions,
        "sections_meta":  sections_meta,
        "shortfall_notes": shortfall_notes,
        "balance_summary": item_analysis_service.summarize_paper_balance(all_questions),
    }


# ── private helpers ───────────────────────────────────────────────────────────

def _fetch_section_candidates(
    subject: Optional[str],
    topic_ids: list[str],
    question_types: list[str],
    source: Optional[str],
) -> list[dict]:
    """Fetch questions matching this section's criteria, least-used first.

    topic_ids=[] means no topic filter (any topic).
    topic_ids=[id1, id2] uses IN (...) — multiple topics allowed.
    """
    if not topic_ids:
        # No topic filter — delegate to existing find_for_bank_paper
        return questions_repository.find_for_bank_paper(
            subject=subject or None,
            syllabus_topic_id=None,
            question_types=question_types or None,
            source=source,
        )

    # Multiple topic_ids — build IN query directly
    conn = get_connection()
    query = "SELECT * FROM questions WHERE 1=1"
    params: list = []

    if subject:
        query += " AND subject = ?"
        params.append(subject)

    placeholders = ",".join("?" for _ in topic_ids)
    query += f" AND syllabus_topic_id IN ({placeholders})"
    params.extend(topic_ids)

    if question_types:
        type_placeholders = ",".join("?" for _ in question_types)
        query += f" AND question_type IN ({type_placeholders})"
        params.extend(question_types)

    if source:
        query += " AND source = ?"
        params.append(source)

    query += " ORDER BY usage_count ASC"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def _resolve_title(paper_title: Optional[str], subject: str, class_name: Optional[str]) -> str:
    if paper_title and paper_title.strip():
        return paper_title.strip()
    parts = [subject] if subject else []
    if class_name:
        parts.append(class_name)
    parts.append(date.today().strftime("%d %b %Y"))
    return " – ".join(parts) if parts else "Blueprint Paper"


def _annotate_expected_difficulty(questions: list[dict]) -> None:
    for q in questions:
        q["expected_difficulty"] = item_analysis_service.expected_difficulty(q["bloom_level"])
        q["difficulty_mismatch"] = item_analysis_service.is_difficulty_mismatch(
            q.get("difficulty"), q["bloom_level"]
        )
