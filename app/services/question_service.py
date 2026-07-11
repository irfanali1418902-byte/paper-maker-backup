"""Orchestrates question generation (AI call + persistence)."""

import json
import uuid

from app.repositories import questions_repository
from app.schemas.requests import (
    GenerateQuestionsRequest,
    ManualQuestionRequest,
    ManualQuestionUpdateRequest,
    UpdateQuestionRequest,
)
from app.services import ai_service, bloom_service


def generate_for_topic(req: GenerateQuestionsRequest) -> list[dict]:
    """Asks the AI for a batch of questions for this topic, using the
    requested Bloom distribution. Returns the raw AI-generated dicts —
    persistence is a separate step so the route can distinguish AI failure
    (502) from DB failure (500)."""
    dist_type = bloom_service.resolve_distribution_type(req.bloom_distribution, req.difficulty)
    distribution = bloom_service.calculate_bloom_distribution(dist_type, req.total_questions)
    return ai_service.generate_questions_from_ai(
        topic=req.topic,
        subject=req.subject,
        bloom_distribution=distribution,
        question_types=req.question_types,
        difficulty=req.difficulty,
        learning_outcome=req.learning_outcome,
    )


def persist_batch(ai_questions: list[dict], req: GenerateQuestionsRequest) -> list[str]:
    """Saves AI-generated questions to the bank. Returns the IDs of inserted
    rows."""
    saved_ids: list[str] = []
    for q in ai_questions:
        qid = str(uuid.uuid4())
        marks = bloom_service.calculate_marks(
            q.get("bloom_level", "UNDERSTAND"),
            q.get("question_type", "multiple-choice"),
            req.difficulty,
        )
        questions_repository.insert(
            {
                "id": qid,
                "subject": req.subject,
                "topic": req.topic,
                "bloom_level": q.get("bloom_level"),
                "difficulty": req.difficulty,
                "question_type": q.get("question_type"),
                "marks": marks,
                "question_en": q.get("question_en"),
                "question_ur": q.get("question_ur"),
                "options_en": json.dumps(q.get("options_en", [])),
                "options_ur": json.dumps(q.get("options_ur", [])),
                "correct_answer_en": q.get("correct_answer_en"),
                "correct_answer_ur": q.get("correct_answer_ur"),
                "explanation_en": q.get("explanation_en"),
                "explanation_ur": q.get("explanation_ur"),
                "visual_emoji": q.get("visual_emoji"),
                "visual_count": q.get("visual_count"),
                "syllabus_topic_id": req.syllabus_topic_id,
            }
        )
        saved_ids.append(qid)
    return saved_ids


def update_question(question_id: str, req: UpdateQuestionRequest) -> bool:
    """Sirf diye gaye fields DB mein update karta hai. False = question nahi mila."""
    fields = req.model_dump(exclude_none=True)
    return questions_repository.update(question_id, fields)


def save_manual_question(req: ManualQuestionRequest, resolved_subject: str, resolved_topic: str) -> str:
    """Teacher ka manually likhaa question bank mein save karta hai. Returns new question id."""
    qid = str(uuid.uuid4())
    options_json = json.dumps(req.options or [])
    questions_repository.insert(
        {
            "id": qid,
            "subject": resolved_subject,
            "topic": resolved_topic,
            "bloom_level": req.bloom_level,
            "difficulty": req.difficulty,
            "question_type": req.question_type,
            "marks": req.marks,
            "question_en": None if req.is_urdu else req.question_text,
            "question_ur": req.question_text if req.is_urdu else None,
            "options_en": "[]" if req.is_urdu else options_json,
            "options_ur": options_json if req.is_urdu else "[]",
            "correct_answer_en": None if req.is_urdu else req.correct_answer,
            "correct_answer_ur": req.correct_answer if req.is_urdu else None,
            "explanation_en": None,
            "explanation_ur": None,
            "visual_emoji": None,
            "visual_count": None,
            "syllabus_topic_id": req.syllabus_topic_id,
            "answer_lines": req.answer_lines,
            "image_path": None,
            "image_size": None,
            "source": "manual",
        }
    )
    return qid


def update_manual_question(question_id: str, req: ManualQuestionUpdateRequest) -> bool:
    """Sirf source='manual' wale questions update karta hai. False = nahi mila ya gemini hai."""
    existing = questions_repository.find_by_id(question_id)
    if not existing or existing.get("source") != "manual":
        return False

    # Is question ka language direction infer karo
    is_urdu = bool(existing.get("question_ur")) and not bool(existing.get("question_en"))
    if req.is_urdu is not None:
        is_urdu = req.is_urdu

    fields: dict = {}
    if req.question_text is not None:
        if is_urdu:
            fields["question_ur"] = req.question_text
            fields["question_en"] = None
        else:
            fields["question_en"] = req.question_text
            fields["question_ur"] = None

    if req.options is not None:
        opts_json = json.dumps(req.options)
        if is_urdu:
            fields["options_ur"] = opts_json
            fields["options_en"] = "[]"
        else:
            fields["options_en"] = opts_json
            fields["options_ur"] = "[]"

    if req.correct_answer is not None:
        if is_urdu:
            fields["correct_answer_ur"] = req.correct_answer
            fields["correct_answer_en"] = None
        else:
            fields["correct_answer_en"] = req.correct_answer
            fields["correct_answer_ur"] = None

    if req.marks is not None:
        fields["marks"] = req.marks
    if req.answer_lines is not None:
        fields["answer_lines"] = req.answer_lines

    if fields:
        questions_repository.update(question_id, fields)
    return True


def delete_manual_question(question_id: str) -> bool:
    """Sirf source='manual' wala question delete karta hai."""
    return questions_repository.delete(question_id)


def list_questions(
    subject: str | None = None,
    topic: str | None = None,
    bloom_level: str | None = None,
    syllabus_topic_id: str | None = None,
) -> list:
    return questions_repository.list_by_filters(
        subject=subject, topic=topic, bloom_level=bloom_level, syllabus_topic_id=syllabus_topic_id
    )
