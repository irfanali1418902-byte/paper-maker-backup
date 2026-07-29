"""UI-ARCH ratchet — CSS-debt metrics may only go down.

Companion to ``scripts/css_baseline.py``. These tests are the enforcement half of
the ratchet: they fail the suite the moment a page grows CSS back, a hardcoded hex
reappears, or a frozen ``id`` / ``onclick`` / ``name`` / ``data-*`` is renamed.

They import the measuring module rather than shelling out to it, so they hold
regardless of the working directory pytest was started from — the PowerShell tool
resets the cwd to ``C:\\Users\\MCS`` between calls (CLAUDE.md §12.9).
"""

from __future__ import annotations

import json
import os

import pytest

from scripts import css_baseline
from scripts.css_baseline import (
    BASELINE_PATH,
    INFORMATIONAL_METRICS,
    RATCHETED_METRICS,
    compare,
    compare_inventory,
    compare_js_classes,
    compare_metrics,
    load_baseline,
    measure,
    page_paths,
)

# ── fixtures ──────────────────────────────────────────────────────────────────


@pytest.fixture(scope="module")
def baseline() -> dict:
    return load_baseline()


@pytest.fixture(scope="module")
def current() -> dict:
    return measure()


# ── the baseline artifact itself ──────────────────────────────────────────────


def test_baseline_file_is_committed():
    assert BASELINE_PATH.is_file(), (
        f"{BASELINE_PATH} is missing. It is the ratchet's memory - without it every "
        "metric silently passes. Regenerate with: python scripts/css_baseline.py --write"
    )


def test_baseline_declares_every_tracked_metric(baseline):
    for name in RATCHETED_METRICS + INFORMATIONAL_METRICS:
        assert name in baseline["metrics"], f"baseline is missing metric '{name}'"


def test_baseline_is_valid_json_with_expected_shape(baseline):
    assert set(baseline) >= {"metrics", "per_page", "frozen_inventory"}
    assert baseline["per_page"], "baseline records no pages"


def test_measures_the_nine_real_pages():
    """mockup-modern.html is a design reference and must stay out of the metrics."""
    names = [p.name for p in page_paths()]
    assert len(names) == 9, f"expected 9 real pages, found {len(names)}: {names}"
    assert "mockup-modern.html" not in names


# ── the ratchet ───────────────────────────────────────────────────────────────


@pytest.mark.parametrize("metric", RATCHETED_METRICS)
def test_metric_never_increases(metric, current, baseline):
    was = baseline["metrics"].get(metric)
    assert was is not None, (
        f"'{metric}' is ratcheted but absent from the baseline. Re-baseline with: "
        "python scripts/css_baseline.py --write"
    )
    now = current["metrics"][metric]
    assert now <= was, (
        f"{metric} went UP: {was} -> {now} (+{now - was}). CSS debt may only go down "
        f"(CLAUDE.md §11). If this increase is genuinely correct, it needs a human "
        f"decision and an explicit re-baseline: python scripts/css_baseline.py --write"
    )


def test_no_metric_regressed(current, baseline):
    assert compare_metrics(current, baseline) == []


def test_legacy_css_is_not_ratcheted():
    """99-legacy/ rises during Sprint 1 by design; ratcheting it would fail the plan."""
    assert "legacy_css_lines" in INFORMATIONAL_METRICS
    assert "legacy_css_lines" not in RATCHETED_METRICS


def test_shared_css_is_tracked_but_not_ratcheted(current):
    """The new ITCSS tree must be free to grow, but must not be an invisible hiding place.

    total_css_lines covers page CSS + 99-legacy only. Without shared_css_lines, moving a
    page's <style> block into app.css would read as progress: the ratcheted metrics fall
    and not one line of CSS is gone.
    """
    assert "shared_css_lines" in INFORMATIONAL_METRICS
    assert "shared_css_lines" not in RATCHETED_METRICS
    assert current["metrics"]["shared_css_lines"] > 0, (
        "app.css and theme.css exist and are linked by every page - measuring 0 here "
        "means the shared-CSS blind spot is not actually being watched"
    )


def test_total_hardcoded_hex_survives_extraction(current):
    """The metric that Sprint 1 cannot fake.

    `hardcoded_hex` counts only `<style>` blocks in HTML, so extracting a page drops it
    without removing a single colour - UI-010 took it 324 -> 298 while all 26 values rode
    along into 99-legacy/slo.css. `total_hardcoded_hex` sums all three places a hardcoded
    colour can live, so extraction is flat and only deletion moves it.
    """
    metrics = current["metrics"]
    assert "total_hardcoded_hex" in RATCHETED_METRICS
    assert "stylesheet_hex" in INFORMATIONAL_METRICS
    assert metrics["total_hardcoded_hex"] == (
        metrics["hardcoded_hex"] + metrics["hardcoded_hex_inline"] + metrics["stylesheet_hex"]
    )
    assert metrics["stylesheet_hex"] > 0, (
        "stylesheets exist and contain hex - measuring 0 means the extraction blind spot "
        "is not actually being watched"
    )


def test_total_css_lines_bounds_the_migration(current):
    """Page CSS + legacy CSS is the honest total - Sprint 1 moves lines between them."""
    metrics = current["metrics"]
    assert metrics["total_css_lines"] == metrics["css_lines_in_html"] + metrics["legacy_css_lines"]


# ── the frozen inventory (CLAUDE.md §12.7) ────────────────────────────────────


def test_frozen_inventory_is_unchanged(current, baseline):
    failures = compare_inventory(current, baseline)
    assert failures == [], "frozen inventory changed:\n  " + "\n  ".join(failures)


def test_js_load_bearing_classes_still_present(current):
    failures = compare_js_classes(current)
    assert failures == [], "JS-load-bearing class missing:\n  " + "\n  ".join(failures)


def test_everything_at_once(current, baseline):
    failures = compare(current, baseline)
    assert failures == [], "ratchet failed:\n  " + "\n  ".join(failures)


# ── the ratchet can actually fail ─────────────────────────────────────────────
# A guard that cannot fail is decoration. These prove each comparator bites.


def test_ratchet_catches_a_metric_increase(current):
    """Derived from CURRENT, not from the committed baseline.

    The first version subtracted 1 from the baseline and relied on current == baseline.
    That held only while no task had moved a metric; it broke the moment UI-010 legitimately
    took hardcoded_hex below the baseline, because 298 > 323 is false. Anchoring the fake
    baseline one below *current* keeps the comparator under test no matter how far the real
    numbers have fallen.
    """
    tampered = {"metrics": dict(current["metrics"])}
    tampered["metrics"]["hardcoded_hex"] -= 1
    failures = compare_metrics(current, tampered)
    assert any("hardcoded_hex" in f for f in failures), "an increase slipped through"


def test_ratchet_catches_a_renamed_id(current):
    # Anchored to current, not the baseline - see test_ratchet_catches_a_metric_increase.
    page = next(iter(current["frozen_inventory"]))
    tampered = {"frozen_inventory": {p: list(v) for p, v in current["frozen_inventory"].items()}}
    tampered["frozen_inventory"][page].append('id="a-handler-that-was-renamed-away"')
    failures = compare_inventory(current, tampered)
    assert any("MISSING" in f for f in failures), "a renamed id slipped through"


def test_ratchet_catches_a_deleted_duplicate_handler(current):
    """The same onclick legitimately appears on several buttons - deleting one must fail.

    693 attributes across the 9 pages are only 641 distinct strings. A set comparison
    would wave this through; the Counter comparison is what catches it.

    Anchored to current on both sides - see test_ratchet_catches_a_metric_increase.
    """
    page, attrs = next(
        (p, a) for p, a in current["frozen_inventory"].items() if len(a) != len(set(a))
    )
    duplicated = next(attr for attr in attrs if attrs.count(attr) > 1)
    thinned = list(attrs)
    thinned.remove(duplicated)  # one of N copies, so the attribute is still present

    tampered = {"frozen_inventory": dict(current["frozen_inventory"], **{page: attrs})}
    trimmed = {"frozen_inventory": dict(current["frozen_inventory"], **{page: thinned})}
    failures = compare_inventory(trimmed, tampered)
    assert any("MISSING" in f and duplicated in f for f in failures), (
        f"deleting one copy of {duplicated} on {page} went undetected - "
        "compare_inventory is set-comparing instead of counting"
    )


def test_missing_metric_in_an_old_baseline_fails_loudly(current):
    """A baseline predating a metric must say so, not KeyError and not silently pass."""
    stale = {"metrics": {k: v for k, v in current["metrics"].items() if k != "hardcoded_hex"}}
    failures = compare_metrics(current, stale)
    assert any("hardcoded_hex" in f and "re-baseline" in f for f in failures)


def test_js_class_check_would_notice_a_rename(monkeypatch):
    """Guard the guard: a class name that appears nowhere must be reported."""
    monkeypatch.setattr(
        css_baseline, "JS_LOAD_BEARING_CLASSES", {"taqseem.html": ["definitely-not-a-real-class"]}
    )
    failures = css_baseline.compare_js_classes({"frozen_inventory": {}})
    assert len(failures) == 1
    assert "definitely-not-a-real-class" in failures[0]


def test_ratchet_tolerates_improvement(current, baseline):
    """Metrics going DOWN is the point - it must not be reported as a failure."""
    tampered = {"metrics": {k: v + 100 for k, v in baseline["metrics"].items()}}
    assert compare_metrics(current, tampered) == []


# ── the cwd trap (CLAUDE.md §12.9) ────────────────────────────────────────────


def test_measurement_is_cwd_independent(current, tmp_path):
    """Paths resolve from the project root, never the cwd.

    A cwd-relative glob would find no pages from C:\\Users\\MCS and report a
    triumphant zero for every metric - a ratchet that passes by measuring nothing.
    """
    original = os.getcwd()
    try:
        os.chdir(tmp_path)
        elsewhere = measure()
    finally:
        os.chdir(original)

    assert elsewhere["metrics"] == current["metrics"]
    # Canary: prove pages were actually found, not that any particular metric is
    # non-zero. Every metric here is driven to 0 on purpose -- style_blocks and
    # css_lines_in_html at the end of Sprint 1, the hex and legacy counts by Sprint 6
    # -- so anchoring the canary to one makes this test fail the moment the epic
    # succeeds. It did, at UI-018. The page count is the thing that never legitimately
    # reaches zero.
    assert elsewhere["per_page"], "measured an empty tree"
    assert set(elsewhere["per_page"]) == set(current["per_page"]), "measured a different tree"


def test_baseline_json_is_utf8_and_newline_terminated():
    raw = BASELINE_PATH.read_bytes().decode("utf-8")
    assert raw.endswith("\n")
    json.loads(raw)
