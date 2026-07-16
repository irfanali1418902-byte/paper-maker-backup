"""Bloom's Taxonomy suggestion route."""

from fastapi import APIRouter, HTTPException

from app.core.bloom_standards import get_bloom_suggestion

router = APIRouter()


@router.get("/api/bloom-suggestion/{class_name}")
def bloom_suggestion(class_name: str):
    """Return Bloom distribution suggestion for a class. 404 if no match."""
    result = get_bloom_suggestion(class_name)
    if result is None:
        raise HTTPException(status_code=404, detail="Is class ke liye koi tajweez nahi.")
    return result
