"""Orchestrates paper assembly from the question bank."""

import json
import uuid
from datetime import date
from typing import Optional

from app.repositories import papers_repository, questions_repository
from app.schemas.requests import AdaptivePaperRequest, BankPaperRequest, GeneratePaperRequest
from app.services import adaptive_service, bloom_service, dashboard_service, item_analysis_service
from app.services.exceptions import QuestionBankEmpty

# paper_type -> allowed question_type values. None = koi filter nahi (sab types).
# "subjective" ka inclusion-list rakha hai (na ke "not mcq") taake generation ki
# vocabulary controlled rahe; naye subjective type aayein to yahan add karo.
_PAPER_TYPE_FILTERS: dict[str, list[str] | None] = {
    "mcq": ["multiple-choice"],
    "subjective": ["short-answer", "essay", "fill-blank"],
    "mixed": None,
}

# custom-ratio ke do groups jinke beech ratio banta hai. MCQ group deliberately
# true-false ko bhi shamil karta hai (objective questions) — ye _PAPER_TYPE_FILTERS
# ke "mcq" (sirf multiple-choice) se alag hai, aur ye jaan-boojh kar hai.
_RATIO_MCQ_GROUP = ["multiple-choice", "true-false"]
_RATIO_SUBJECTIVE_GROUP = ["short-answer", "essay", "fill-blank"]


def assemble_balanced_paper(req: GeneratePaperRequest) -> dict | None:
    """Picks Bloom-balanced questions (least-used first), bumps their
    usage_count, persists the paper. Returns the paper dict, or None if no
    questions matched any bucket (caller maps that to 404)."""
    if req.sections:
        return _assemble_by_sections(req)
    if req.paper_type == "custom-ratio":
        return _assemble_by_ratio(req)

    distribution = bloom_service.calculate_bloom_distribution(
        req.bloom_distribution, req.total_questions
    )
    question_types = _PAPER_TYPE_FILTERS.get(req.paper_type)
    selected_ids, selected_questions = _pick_questions(
        req.subject, distribution, req.difficulty, question_types, req.language_filter, req.grade
    )
    if not selected_questions:
        return None

    title = _resolve_title(req.paper_title, req.subject, req.class_name)
    paper_id, total_marks = _persist_paper(
        subject=req.subject,
        class_name=req.class_name,
        selected_ids=selected_ids,
        selected_questions=selected_questions,
        paper_title=title,
        exam_no=req.exam_no,
    )
    return {
        "paper_id": paper_id,
        "total_marks": total_marks,
        "questions": selected_questions,
        "balance_summary": item_analysis_service.summarize_paper_balance(selected_questions),
    }


def assemble_adaptive_paper(req: AdaptivePaperRequest) -> dict | None:
    """Builds a paper weighted toward the Bloom levels a class scored worst on,
    learned from the source paper's latest results upload. Returns None (caller
    maps to 404) if the source paper/results don't exist or the bank is empty."""
    source_paper = papers_repository.find_by_id(req.source_paper_id)
    if source_paper is None:
        return None
    dashboard = dashboard_service.get_latest_dashboard_for_paper(req.source_paper_id)
    if dashboard is None or not dashboard["bloom_breakdown"]:
        return None

    subject = source_paper["subject"]
    breakdown = dashboard["bloom_breakdown"]
    distribution = adaptive_service.build_adaptive_distribution(breakdown, req.total_questions)

    question_types = _PAPER_TYPE_FILTERS.get(req.paper_type)
    # Grade filter yahan JAAN-BOOJH KAR nahi hai. `AdaptivePaperRequest` mein
    # `grade` hai hi nahi, aur usay yahan eejaad karna ghalat hoga: adaptive apna
    # subject source paper se leta hai taake wo weakness signal se alag na ho
    # jaye, magar `papers` row mein grade nahi — sirf free-text `class_name` hai.
    # To grade "wahi jo source paper ka tha" bharosay se nikala hi nahi ja sakta.
    # Ye alag faisla hai (2026-08-21), aur usay tab karna jab papers row mein
    # grade darj hone lage.
    selected_ids, selected_questions = _pick_questions(
        subject, distribution, req.difficulty, question_types
    )
    if not selected_questions:
        return None

    title = _resolve_title(None, subject, req.class_name)
    paper_id, total_marks = _persist_paper(
        subject=subject,
        class_name=req.class_name,
        selected_ids=selected_ids,
        selected_questions=selected_questions,
        paper_title=title,
        exam_no=req.exam_no,
    )
    return {
        "paper_id": paper_id,
        "total_marks": total_marks,
        "questions": selected_questions,
        "balance_summary": item_analysis_service.summarize_paper_balance(selected_questions),
        "adaptive_summary": adaptive_service.summarize(breakdown, distribution),
    }


def assemble_bank_paper(req: BankPaperRequest) -> dict | None:
    """Teacher ke manual questions se paper banao — bina Gemini, bina Bloom distribution.
    syllabus_topic_id diya jaye to sirf us topic ke, warna subject ke sab questions.
    Returns None agar koi matching question nahi mila (route 404 bhejta hai)."""
    # Resolve subject from syllabus_topic_id when subject not provided directly
    resolved_subject = req.subject or ""
    if req.syllabus_topic_id and not resolved_subject:
        from app.services import syllabus_service  # local import — no circular dependency

        topic_row = syllabus_service.get_topic(req.syllabus_topic_id)
        if topic_row:
            resolved_subject = topic_row["subject"]

    source_arg = None if req.source_filter == "all" else req.source_filter

    questions = questions_repository.find_for_bank_paper(
        subject=resolved_subject or None,
        syllabus_topic_id=req.syllabus_topic_id,
        question_types=req.question_types,
        source=source_arg,
        grade=req.grade,
    )

    if not questions:
        return None

    if req.total_questions:
        questions = questions[: req.total_questions]  # already ordered by usage_count ASC

    selected_ids = [q["id"] for q in questions]
    title = _resolve_title(req.paper_title, resolved_subject, req.class_name)
    paper_id, total_marks = _persist_paper(
        subject=resolved_subject,
        class_name=req.class_name,
        selected_ids=selected_ids,
        selected_questions=questions,
        paper_title=title,
        exam_no=req.exam_no,
    )

    for qid in selected_ids:
        questions_repository.increment_usage_count(qid)

    return {
        "paper_id": paper_id,
        "total_marks": total_marks,
        "questions": questions,
        "balance_summary": item_analysis_service.summarize_paper_balance(questions),
    }


def list_papers(query: Optional[str] = None) -> dict:
    """Return all papers (or filtered by query) for the My Papers list."""
    rows = papers_repository.search(query) if query else papers_repository.list_all()
    return {"papers": rows, "total": len(rows)}


def papers_using_question(question_id: str) -> dict:
    """Delete-warning ke liye — is question ko kitne aur kaun se papers use karte.
    Returns {count, titles}. Untitled papers ko '(Untitled)' de dete."""
    papers = papers_repository.find_papers_containing(question_id)
    titles = [(p.get("paper_title") or "(Untitled)") for p in papers]
    return {"count": len(papers), "titles": titles}


def get_paper_with_questions(paper_id: str) -> dict | None:
    paper = papers_repository.find_by_id(paper_id)
    if not paper:
        return None
    question_ids = json.loads(paper["question_ids"])
    questions: list[dict] = []
    for qid in question_ids:
        q = questions_repository.find_by_id(qid)
        if q:
            questions.append(q)
    _annotate_expected_difficulty(questions)
    return {
        "paper": paper,
        "questions": questions,
        "balance_summary": item_analysis_service.summarize_paper_balance(questions),
    }


def replace_question(paper_id: str, old_question_id: str, new_question_id: str) -> dict | None:
    """Swap one question in a paper for another from the bank, in place (order
    preserved), recompute total_marks, and persist. Returns the updated paper
    dict (same shape as assemble_balanced_paper), or None if the paper doesn't
    exist (route maps to 404). Raises ValueError for bad question ids (400)."""
    paper = papers_repository.find_by_id(paper_id)
    if paper is None:
        return None

    question_ids = json.loads(paper["question_ids"])
    if old_question_id not in question_ids:
        raise ValueError("Purana question is paper mein nahi hai.")
    if questions_repository.find_by_id(new_question_id) is None:
        raise ValueError("Naya question bank mein nahi mila.")

    question_ids[question_ids.index(old_question_id)] = new_question_id

    questions: list[dict] = []
    for qid in question_ids:
        q = questions_repository.find_by_id(qid)
        if q:
            questions.append(q)
    _annotate_expected_difficulty(questions)
    total_marks = sum(q["marks"] for q in questions)

    papers_repository.update_question_ids(paper_id, question_ids, total_marks)
    questions_repository.increment_usage_count(new_question_id)

    return {
        "paper_id": paper_id,
        "total_marks": total_marks,
        "questions": questions,
        "balance_summary": item_analysis_service.summarize_paper_balance(questions),
    }


def _assemble_by_sections(req: GeneratePaperRequest) -> dict | None:
    """Sections mode: har section apni qism ke sawal apni ginti tak uthata hai,
    aur sections_meta paper row mein likhi jaati hai.

    Yahan `sections_meta` ki shakl EEJAAD nahi ki ja rahi — wo pehle se tay hai.
    blueprint_paper_service.py use likhti hai aur static/print.html use parhta
    hai; ye function bas usi shakl mein likhta hai, isliye print par sections
    apne aap chalne lagte hain aur wahan ek line badalne ki zaroorat nahi.

    SHORTFALL YAHAN ERROR NAHI HAI, aur ye custom-ratio se jaan-boojh kar alag
    hai. Ratio kam questions par QuestionBankEmpty phenkta hai; blueprint kami
    bardasht karta hai aur print.html us ke liye shortfall panel pehle se render
    karta hai. Sections blueprint wala rawaiya apnate hain, do wajahon se:
      * teacher ne heading khud likhi hai — usay dikhna chahiye ke us section
        mein kya mila, na ke poora paper fail ho jaye
      * bank mein sab types barabar nahi hain (2026-08-20: short-answer 370,
        multiple-choice 61, true-false 28, aur fill-blank/essay SIFAR), to
        hard error is feature ko aam halat mein na-qabil-e-istemal bana deta
    Har section ka Bloom balance apne andar banta hai, poore paper par nahi —
    ye qism-se-taqseem ka laazmi nateeja hai, side effect nahi.
    """
    selected_ids: list[str] = []
    selected_questions: list[dict] = []
    sections_meta: list[dict] = []

    for spec in req.sections or []:
        if spec.type_counts:
            # Ratio Phase 2 (PRD R5): har qism apni ginti tak alag uthti hai.
            # Ek hi _pick_questions call mein saari qismein daalna yeh nahi kar
            # sakta — repository `question_type IN (...) ORDER BY usage_count`
            # karti hai, to andar ka mix usage counts par chhut jata hai.
            # Tarteeb type_counts ki hai: sawal kaghaz par isi tarteeb mein aayenge.
            ids: list[str] = []
            questions: list[dict] = []
            gaps: list[str] = []
            for tc in spec.type_counts:
                dist = bloom_service.calculate_bloom_distribution(req.bloom_distribution, tc.count)
                t_ids, t_qs = _pick_questions(
                    req.subject,
                    dist,
                    req.difficulty,
                    [tc.question_type],
                    req.language_filter,
                    req.grade,
                )
                ids.extend(t_ids)
                questions.extend(t_qs)
                if len(t_qs) < tc.count:
                    gaps.append(f"{tc.question_type}: {tc.count} maange, {len(t_qs)} mile")
        else:
            distribution = bloom_service.calculate_bloom_distribution(
                req.bloom_distribution, spec.count
            )
            ids, questions = _pick_questions(
                req.subject,
                distribution,
                req.difficulty,
                list(spec.question_types or []),
                req.language_filter,
                req.grade,
            )
            gaps = []

        selected_ids.extend(ids)
        selected_questions.extend(questions)

        section_meta = {
            "heading": spec.heading,
            "question_ids": ids,
            "marks": sum(q["marks"] for q in questions),
            "shortfall": spec.wanted - len(questions),
        }
        # `shortfall_reason` blueprint ki key hai aur print.html use PEHLE SE
        # render karta hai (sf-reason). Sirf ek adad — "2 kam" — teacher ko yeh
        # nahi batata ke kaunsi qism kam pari, aur type_counts ki poori baat hi
        # qism-wise ginti hai. Isliye jahan qism-wise maanga gaya wahan wajah
        # bhi qism-wise likhi jaati hai; kaghaz par wo apne aap aa jaati hai.
        if gaps:
            section_meta["shortfall_reason"] = " · ".join(gaps)
        sections_meta.append(section_meta)

    # Ek bhi sawal na mila to purane raaston jaisa hi 404 — caller isay map karta hai.
    if not selected_questions:
        return None

    title = _resolve_title(req.paper_title, req.subject, req.class_name)
    paper_id, total_marks = _persist_paper(
        subject=req.subject,
        class_name=req.class_name,
        selected_ids=selected_ids,
        selected_questions=selected_questions,
        paper_title=title,
        exam_no=req.exam_no,
        sections_meta=sections_meta,
    )
    return {
        "paper_id": paper_id,
        "total_marks": total_marks,
        "questions": selected_questions,
        "sections": sections_meta,
        "balance_summary": item_analysis_service.summarize_paper_balance(selected_questions),
    }


def _assemble_by_ratio(req: GeneratePaperRequest) -> dict | None:
    """custom-ratio: total_questions ko MCQ vs Subjective groups mein mcq_percent
    ke hisaab se baant kar, har group ke andar wahi Bloom distribution laga kar
    questions pick karta hai. Ek group ke liye questions bilkul na milein to
    QuestionBankEmpty (group-named message) raise hoti hai."""
    if req.mcq_percent is None:
        raise ValueError("custom-ratio ke liye mcq_percent (0-100) dena zaroori hai.")

    mcq_count, subj_count = _split_by_ratio(req.total_questions, req.mcq_percent)

    selected_ids: list[str] = []
    selected_questions: list[dict] = []
    for group_count, group_types, group_label in (
        (mcq_count, _RATIO_MCQ_GROUP, "MCQ"),
        (subj_count, _RATIO_SUBJECTIVE_GROUP, "Subjective"),
    ):
        if group_count <= 0:
            continue
        distribution = bloom_service.calculate_bloom_distribution(
            req.bloom_distribution, group_count
        )
        ids, questions = _pick_questions(
            req.subject, distribution, req.difficulty, group_types, req.language_filter, req.grade
        )
        if not questions:
            raise QuestionBankEmpty(
                f"Is subject mein {group_label} questions kaafi nahi (chahiye the {group_count}). "
                "Pehle us type ke questions generate karo, ya ratio badlo."
            )
        selected_ids.extend(ids)
        selected_questions.extend(questions)

    if not selected_questions:
        return None

    title = _resolve_title(req.paper_title, req.subject, req.class_name)
    paper_id, total_marks = _persist_paper(
        subject=req.subject,
        class_name=req.class_name,
        selected_ids=selected_ids,
        selected_questions=selected_questions,
        paper_title=title,
        exam_no=req.exam_no,
    )
    return {
        "paper_id": paper_id,
        "total_marks": total_marks,
        "questions": selected_questions,
        "balance_summary": item_analysis_service.summarize_paper_balance(selected_questions),
    }


def _split_by_ratio(total: int, mcq_percent: int) -> tuple[int, int]:
    """total ko (mcq_count, subjective_count) mein baanto. Half-up rounding MCQ par;
    subjective = total - mcq taake sum hamesha exact rahe (koi rounding drift nahi)."""
    mcq = int(total * mcq_percent / 100 + 0.5)
    mcq = max(0, min(total, mcq))  # clamp (defensive; percent Pydantic se 0-100 aata hai)
    return mcq, total - mcq


def _pick_questions(
    subject: str,
    distribution: dict,
    difficulty: str | None,
    question_types: list[str] | None = None,
    language_filter: str | None = None,
    grade: str | None = None,
) -> tuple[list[str], list[dict]]:
    """Pick least-used questions per Bloom level for the given distribution,
    bumping each picked question's usage_count. Shared by balanced + adaptive.
    question_types diya jaye to sirf un types se pick hota hai (paper_type filter).

    grade diya jaye to sirf usi syllabus grade ke questions uthte hain. Ye
    2026-08-21 ko dala gaya, kyunke us se pehle grade kahin filter karta hi nahi
    tha: `class_name` sirf paper ke title aur row tak jata tha, aur "Grade 4" ka
    paper poore Mathematics bank se uthata tha. Naapa gaya — 10-sawal balanced
    Grade 4 paper mein 8 mein se sirf 2 sawal Grade 4 ke aate the, baqi Pre Year 1
    ke ("Count the candies and match with the correct number").
    """
    selected_ids: list[str] = []
    selected_questions: list[dict] = []
    for level, count in distribution.items():
        if count <= 0:
            continue
        rows = questions_repository.find_least_used(
            subject=subject,
            bloom_level=level,
            difficulty=difficulty,
            limit=count,
            question_types=question_types,
            language_filter=language_filter,
            grade=grade,
        )
        for row in rows:
            selected_ids.append(row["id"])
            selected_questions.append(row)
            questions_repository.increment_usage_count(row["id"])
    return selected_ids, selected_questions


def _resolve_title(paper_title: Optional[str], subject: str, class_name: Optional[str]) -> str:
    """Return teacher-supplied title, or auto-generate from subject+class+date."""
    if paper_title and paper_title.strip():
        return paper_title.strip()
    parts = [subject]
    if class_name:
        parts.append(class_name)
    parts.append(date.today().strftime("%d %b %Y"))
    return " – ".join(parts)


def _persist_paper(
    subject: str,
    class_name: str | None,
    selected_ids: list[str],
    selected_questions: list[dict],
    paper_title: Optional[str] = None,
    exam_no: Optional[int] = None,
    sections_meta: Optional[list[dict]] = None,
) -> tuple[str, int]:
    """Annotate expected difficulty, persist the paper row, return (id, marks).
    exam_no: paper kis exam se tag hua (coverage ke liye). None = Unassigned.
    sections_meta: sirf sections mode bhejta hai. None rehne par column NULL
    rehta hai aur print.html apne hardcoded A/B split par girta hai — yani har
    purana raasta bilkul waisa ka waisa.
    NOTE: saare callers keyword args bhejte hain — positional se exam_no ghalat
    parameter (paper_title) mein na chala jaye."""
    _annotate_expected_difficulty(selected_questions)
    paper_id = str(uuid.uuid4())
    total_marks = sum(q["marks"] for q in selected_questions)
    papers_repository.insert(
        paper_id=paper_id,
        subject=subject,
        class_name=class_name,
        total_marks=total_marks,
        question_ids=selected_ids,
        paper_title=paper_title,
        exam_no=exam_no,
        sections_meta=sections_meta,
    )
    return paper_id, total_marks


def _annotate_expected_difficulty(questions: list[dict]) -> None:
    """Har question dict mein Bloom-derived expected_difficulty aur stored
    difficulty ke saath mismatch flag add karta hai (in-place)."""
    for q in questions:
        q["expected_difficulty"] = item_analysis_service.expected_difficulty(q["bloom_level"])
        q["difficulty_mismatch"] = item_analysis_service.is_difficulty_mismatch(
            q.get("difficulty"), q["bloom_level"]
        )
