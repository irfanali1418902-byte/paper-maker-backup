"""HTTP routes for blueprint CRUD and preset listing."""

import uuid
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from app.repositories import blueprints_repository
from app.schemas.requests import SaveBlueprintRequest
from app.services import blueprint_presets

router = APIRouter()


@router.get("/api/blueprint-presets")
def list_presets():
    """Hardcoded exam pattern presets — teacher inhe starting point ke tor par use karta hai."""
    return {"presets": blueprint_presets.list_presets()}


@router.get("/api/blueprint-presets/{preset_id}")
def get_preset(preset_id: str):
    preset = blueprint_presets.get_preset(preset_id)
    if preset is None:
        raise HTTPException(status_code=404, detail="Preset nahi mila.")
    return preset


@router.post("/api/blueprints", status_code=201)
def save_blueprint(req: SaveBlueprintRequest):
    """Teacher ka customised blueprint DB mein save karta hai."""
    blueprint_id = str(uuid.uuid4())
    sections_raw = [s.model_dump() for s in req.sections]
    blueprints_repository.insert(
        blueprint_id=blueprint_id,
        name=req.name,
        subject=req.subject,
        grade=req.grade,
        sections=sections_raw,
    )
    return blueprints_repository.find_by_id(blueprint_id)


@router.get("/api/blueprints")
def list_blueprints(subject: Optional[str] = Query(default=None)):
    """Saved blueprints list — optionally subject se filter karo."""
    return {"blueprints": blueprints_repository.list_all(subject=subject)}


@router.get("/api/blueprints/{blueprint_id}")
def get_blueprint(blueprint_id: str):
    bp = blueprints_repository.find_by_id(blueprint_id)
    if bp is None:
        raise HTTPException(status_code=404, detail="Blueprint nahi mila.")
    return bp


@router.delete("/api/blueprints/{blueprint_id}")
def delete_blueprint(blueprint_id: str):
    deleted = blueprints_repository.delete(blueprint_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Blueprint nahi mila.")
    return {"status": "ok"}
