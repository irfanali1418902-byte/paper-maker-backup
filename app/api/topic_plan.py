"""HTTP routes for the hafta-war plan (syllabus topic -> hafta). R7 Marhala 1.

`app/api/taqseem.py` ka aaina -- error mapping wahan se liya gaya hai:
ValueError -> 400, NotFound -> 404, baqi sab -> 500 with a DB-error message.
"""

from fastapi import APIRouter, HTTPException

from app.schemas.requests import TopicWeekMoveRequest
from app.services import topic_week_service

router = APIRouter()


@router.get("/api/topic-plan")
def get_topic_plan(subject: str, grade: str):
    """Ek (subject, grade) ka resolved hafta-war plan. Dono laazmi (plan
    per-subject-per-grade hai). N global (school_settings.week_count).

    Plan-less topics bhi aate hain -- Unassigned bucket mein -- taake teacher ko
    dikhe ke kitna kaam baqi hai."""
    if not subject.strip() or not grade.strip():
        raise HTTPException(status_code=400, detail="subject aur grade dono chahiye.")
    try:
        return topic_week_service.get_plan(subject, grade)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Hafta-war plan fetch fail hui (DB error): {e}"
        ) from e


@router.patch("/api/topic-plan/{topic_id}")
def move_topic(topic_id: str, body: TopicWeekMoveRequest):
    """Ek topic ka hafta badlo/set karo. week_no 0 = Unassigned; range 0..N se
    bahar -> 400; topic_id na mile -> 404. N global (school_settings.week_count)."""
    try:
        return topic_week_service.move_topic(topic_id, body.week_no)
    except topic_week_service.TopicNotFoundError as e:
        raise HTTPException(status_code=404, detail=f"Topic nahi mila: {e}") from e
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Topic move fail hui (DB error): {e}"
        ) from e
