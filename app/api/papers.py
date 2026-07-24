"""HTTP routes for paper assembly and retrieval."""

from typing import Optional

from fastapi import APIRouter, File, HTTPException, Query, Response, UploadFile

from app.schemas.requests import (
    AdaptivePaperRequest,
    BankPaperRequest,
    BlueprintPaperRequest,
    GeneratePaperRequest,
    ReplaceQuestionRequest,
)
from app.schemas.responses import (
    AdaptivePaperResponse,
    GeneratePaperResponse,
    PaperResponse,
    PapersListResponse,
)
from app.services import (
    blueprint_paper_service,
    paper_service,
    result_service,
    slo_coverage_service,
    slo_shortfall_service,
)
from app.services.exceptions import QuestionBankEmpty, ResultsValidationError

router = APIRouter()


@router.get("/api/papers", response_model=PapersListResponse)
def list_papers(q: Optional[str] = Query(default=None, description="Search by title or subject")):
    """My Papers list — all papers newest first, optionally filtered by title/subject."""
    try:
        return paper_service.list_papers(q)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Papers list fetch fail hui: {e}") from e


@router.post("/api/bank-paper", response_model=GeneratePaperResponse)
def generate_bank_paper(req: BankPaperRequest):
    """Teacher ke manual questions se paper banao — bina Gemini, bina API.
    syllabus_topic_id diya jaye to sirf us topic ke questions; source_filter='manual'
    (default) matlab sirf teacher-written, 'all' matlab manual + gemini dono."""
    try:
        result = paper_service.assemble_bank_paper(req)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Bank paper assemble fail: {e}") from e
    if result is None:
        raise HTTPException(
            status_code=404,
            detail=(
                "Is topic/subject mein koi manual question nahi mila. "
                "Pehle Question Bank mein questions add karo (/bank.html)."
            ),
        )
    return result


@router.post("/api/blueprint-paper")
def generate_blueprint_paper(req: BlueprintPaperRequest):
    """Blueprint se paper banao — section-by-section, partial-friendly.
    blueprint_id diya jaye to saved blueprint use hota hai;
    warna inline sections_input list use hoti hai."""
    # Resolve sections list
    if req.blueprint_id:
        from app.repositories import blueprints_repository
        bp = blueprints_repository.find_by_id(req.blueprint_id)
        if bp is None:
            raise HTTPException(status_code=404, detail="Blueprint nahi mila.")
        sections = bp["sections"]
        resolved_subject = req.subject or bp.get("subject")
        resolved_grade = req.grade or bp.get("grade")
    else:
        sections = [s.model_dump() for s in req.sections_input]
        resolved_subject = req.subject
        resolved_grade = req.grade

    # Bloom-standard tier: grade (syllabus class) sabse reliable; na ho to free-text
    # class_name par gir jao.
    class_tier = resolved_grade or req.class_name

    try:
        result = blueprint_paper_service.assemble_blueprint_paper(
            blueprint_id=req.blueprint_id,
            sections_input=sections,
            subject=resolved_subject,
            class_name=req.class_name,
            paper_title=req.paper_title,
            class_tier=class_tier,
            exam_no=req.exam_no,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Blueprint paper assemble fail: {e}") from e

    if result is None:
        raise HTTPException(
            status_code=404,
            detail=(
                "Blueprint ke kisi bhi section mein questions nahi mile. "
                "Pehle Question Bank mein questions add karo (/bank.html)."
            ),
        )
    return result


@router.post("/api/generate-paper", response_model=GeneratePaperResponse)
def generate_paper(req: GeneratePaperRequest):
    """Question bank se Bloom + difficulty distribution ke hisaab se balanced
    paper assemble karta hai. Least-used questions ko priority deta hai
    (taake repetition kam ho)."""
    try:
        result = paper_service.assemble_balanced_paper(req)
    except QuestionBankEmpty as e:
        # custom-ratio: kisi group (MCQ/Subjective) ke questions bank mein nahi.
        raise HTTPException(status_code=404, detail=str(e)) from e
    except ValueError as e:
        # e.g. custom-ratio bina mcq_percent ke — well-formed request, bad content.
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Paper assemble fail hui (DB error): {e}"
        ) from e
    if result is None:
        if req.paper_type != "mixed":
            raise HTTPException(
                status_code=404,
                detail=(
                    f"Is subject mein '{req.paper_type}' type ke kaafi questions nahi. "
                    "Generate karte waqt woh question type chuno, ya 'Mixed' use karo."
                ),
            )
        raise HTTPException(
            status_code=404,
            detail="Is subject/Bloom-level ke liye question bank khali hai. Pehle /api/generate-questions se questions banayen.",
        )
    return result


@router.post("/api/generate-adaptive-paper", response_model=AdaptivePaperResponse)
def generate_adaptive_paper(req: AdaptivePaperRequest):
    """Source paper ke latest results se class ki kamzor Bloom levels nikaal kar
    un par zyada weight wala naya paper banata hai (Phase 3 adaptive)."""
    try:
        result = paper_service.assemble_adaptive_paper(req)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Adaptive paper assemble fail hui (DB error): {e}"
        ) from e
    if result is None:
        raise HTTPException(
            status_code=404,
            detail=(
                "Adaptive paper nahi ban saka. Source paper ya uske results nahi mile, "
                "ya in Bloom-levels ke liye question bank khali hai."
            ),
        )
    return result


@router.post("/api/paper/{paper_id}/replace-question", response_model=GeneratePaperResponse)
def replace_question(paper_id: str, req: ReplaceQuestionRequest):
    """Manual question selection: ek question ko bank ke doosre se replace
    karta hai, total_marks + balance recompute karke persist karta hai."""
    try:
        result = paper_service.replace_question(paper_id, req.old_question_id, req.new_question_id)
    except ValueError as e:
        # Bad question ids (old not in paper / new not in bank) — client error.
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Question replace fail hui (DB error): {e}"
        ) from e
    if result is None:
        raise HTTPException(status_code=404, detail="Paper nahi mila.")
    return result


@router.get("/api/paper/{paper_id}", response_model=PaperResponse)
def get_paper(paper_id: str):
    try:
        result = paper_service.get_paper_with_questions(paper_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Paper fetch fail hui (DB error): {e}") from e
    if result is None:
        raise HTTPException(status_code=404, detail="Paper nahi mila.")
    return result


@router.get("/api/paper/{paper_id}/slo-coverage")
def get_paper_slo_coverage(paper_id: str):
    """Is paper ke sawalon se kaun se SLO cover hue + class/subject ke kaun se
    reh gaye (strand-wise), untagged sawalon ki ginti samet. Live compute (JOIN)."""
    try:
        result = slo_coverage_service.compute_coverage(paper_id)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"SLO coverage compute fail hui (DB error): {e}"
        ) from e
    if result is None:
        raise HTTPException(status_code=404, detail="Paper nahi mila.")
    return result


@router.get("/api/paper/{paper_id}/bloom-shortfall")
def get_paper_bloom_shortfall(paper_id: str):
    """Is paper ka asal Bloom distribution (SLO ke bloom_level se) vs class standard
    (Pre-Primary 70/30 wagaira) — per-Bloom kami (shortfall). App adjust NAHI karta,
    sirf report. Live compute (JOIN). Class/standard/tag na ho to graceful message."""
    try:
        result = slo_shortfall_service.compute_shortfall(paper_id)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Bloom shortfall compute fail hui (DB error): {e}"
        ) from e
    if result is None:
        raise HTTPException(status_code=404, detail="Paper nahi mila.")
    return result


@router.get("/api/paper/{paper_id}/result-template")
def get_result_template(paper_id: str):
    """Empty CSV template — roll_no, student_name, then one column per
    question in paper order with max marks in the header. Teacher fills
    this in offline aur baad mein upload karte hain (Phase 2 analyzer)."""
    try:
        csv_bytes = result_service.build_result_template_csv(paper_id)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Result template generate fail hui (DB error): {e}",
        ) from e
    if csv_bytes is None:
        raise HTTPException(status_code=404, detail="Paper nahi mila.")

    return Response(
        content=csv_bytes,
        media_type="text/csv",
        headers={
            "Content-Disposition": f'attachment; filename="paper-{paper_id}-results.csv"',
        },
    )


@router.post("/api/paper/{paper_id}/upload-results")
def upload_results(paper_id: str, file: UploadFile = File(...)):
    """Teacher ka filled-in CSV/xlsx (template hi format mein) accept karta
    hai, validate karta hai, aur result_uploads + student_question_results
    mein save karta hai. Validation errors saari ek hi response mein wapas
    aati hain (400) — teacher pura sheet ek hi pass mein fix kare."""
    contents = file.file.read()

    try:
        result = result_service.import_results(paper_id, file.filename, contents)
    except ResultsValidationError as e:
        # Pass the structured per-row errors straight through so the
        # frontend can render them inline against the spreadsheet.
        raise HTTPException(status_code=400, detail=e.errors) from e
    except ValueError as e:
        # Unparseable file / wrong extension — well-formed request, bad content.
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Results upload fail hui (DB error): {e}"
        ) from e

    if result is None:
        raise HTTPException(status_code=404, detail="Paper nahi mila.")
    return result
