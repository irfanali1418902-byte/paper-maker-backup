"""Fix 1 regression-guard — Generator ka buildPaper() paper mein class_name bheje.

Yeh line frontend se chup-chaap gayab ho sakti hai (aur phir SLO coverage ka
universe kabhi nahi banega). Isliye content-level guard: index.html ke buildPaper
function mein 'class_name' + 'gradeSelect' mojood hone chahiye.
"""

from pathlib import Path

_INDEX = Path(__file__).parent.parent / "static" / "index.html"


def _build_paper_body() -> str:
    """buildPaper() ka source region nikaalo (function se agle async function tak)."""
    html = _INDEX.read_text(encoding="utf-8")
    start = html.index("function buildPaper")
    # agle top-level function tak (buildPaper ke baad wala)
    nxt = html.index("\nasync function ", start + 10)
    return html[start:nxt]


def test_build_paper_sends_class_name(test_db):
    region = _build_paper_body()
    assert "class_name:" in region, "buildPaper() ne class_name bhejna band kar diya!"
    assert "gradeSelect" in region, "class_name gradeSelect se aana chahiye"


def test_generate_paper_request_accepts_class_name():
    """Backend wiring guard — GeneratePaperRequest class_name accept karti hai."""
    from app.schemas.requests import GeneratePaperRequest
    req = GeneratePaperRequest(subject="Mathematics", class_name="Pre Year 1")
    assert req.class_name == "Pre Year 1"
