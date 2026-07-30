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
import re

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
    """The metric Sprint 1 cannot fake — still measured, no longer the ratcheted one.

    `hardcoded_hex` counts only `<style>` blocks in HTML, so extracting a page drops it
    without removing a single colour - UI-010 took it 324 -> 298 while all 26 values rode
    along into 99-legacy/slo.css. `total_hardcoded_hex` sums all three places a hardcoded
    colour can live, so extraction is flat and only deletion moves it.

    UI-020a moved it to informational and ratcheted `unsanctioned_hex` instead; the sum
    identity below is unchanged, which is what keeps every number in the Sprint 1 task log
    comparable.
    """
    metrics = current["metrics"]
    assert "total_hardcoded_hex" in INFORMATIONAL_METRICS
    assert "stylesheet_hex" in INFORMATIONAL_METRICS
    assert metrics["total_hardcoded_hex"] == (
        metrics["hardcoded_hex"] + metrics["hardcoded_hex_inline"] + metrics["stylesheet_hex"]
    )
    assert metrics["stylesheet_hex"] > 0, (
        "stylesheets exist and contain hex - measuring 0 means the extraction blind spot "
        "is not actually being watched"
    )


def test_unsanctioned_hex_is_the_ratcheted_one(current):
    """The end state is zero hex OUTSIDE 01-settings/tokens.css, not zero hex.

    ADR-001 and CLAUDE.md §11 both say "a raw hex outside `01-settings/tokens.css` is a CI
    failure". Tier 1 tokens are raw values by definition, so `total_hardcoded_hex` has a
    floor of "the palette" and 0 was never reachable. Ratcheting it made UI-020 unwritable:
    authoring the tokens file at all would push it above 429 and fail the suite. (The
    projected size of that rise, ~22, is an estimate from the 29 hex in static/theme.css -
    unverified until UI-020 lands.)
    """
    metrics = current["metrics"]
    assert "unsanctioned_hex" in RATCHETED_METRICS
    assert "token_hex" in INFORMATIONAL_METRICS
    assert "total_hardcoded_hex" not in RATCHETED_METRICS
    assert metrics["unsanctioned_hex"] == metrics["total_hardcoded_hex"] - metrics["token_hex"]
    assert metrics["unsanctioned_hex"] > 0, (
        "hex still exists outside tokens.css - measuring 0 here before Sprint 6 means the "
        "subtraction is eating the whole count, not that the debt is repaid"
    )


def test_token_hex_only_exempts_the_one_sanctioned_file(current, tmp_path, monkeypatch):
    """The exemption must be that file and nothing else.

    `unsanctioned_hex` is a subtraction, so anything that wrongly counts as `token_hex`
    silently drains the ratcheted number. Point TOKENS_PATH at a file with a known hex
    count and check the arithmetic tracks it exactly.
    """
    decoy = tmp_path / "tokens.css"
    decoy.write_text(":root { --a:#123456; --b:#abc; --c:#12345678; }\n", encoding="utf-8")

    monkeypatch.setattr(css_baseline, "TOKENS_PATH", decoy)
    assert css_baseline.token_hex_count() == 3
    remeasured = css_baseline.measure()

    # The decoy is outside static/, so it adds nothing to total_hardcoded_hex - the
    # subtraction shows up undiluted.
    assert remeasured["metrics"]["total_hardcoded_hex"] == current["metrics"]["total_hardcoded_hex"]
    # Both sides read the SAME measurement. Comparing against `current` instead would only
    # hold while the real tokens.css is absent: once it exists with T hex, its values stay
    # in stylesheet_hex (it is under static/) and so in total_hardcoded_hex, while pointing
    # TOKENS_PATH at the decoy drops T out of token_hex - so current's unsanctioned is
    # total-T and remeasured's is total-3, and the difference is T, not 0. That is the
    # UI-018a defect exactly: an assertion anchored to a number the plan is about to move.
    # Caught by UI-020a's review agent, which simulated UI-020 by creating the file.
    assert (
        remeasured["metrics"]["unsanctioned_hex"]
        == remeasured["metrics"]["total_hardcoded_hex"] - 3
    )


def test_ratchet_catches_hex_added_outside_the_tokens_file(current):
    """Guard the guard: the exemption must not have opened a general hex amnesty.

    A raw hex authored into any stylesheet other than 01-settings/tokens.css must still
    trip the ratchet exactly as it did before UI-020a.
    """
    tampered = {"metrics": dict(current["metrics"])}
    tampered["metrics"]["unsanctioned_hex"] -= 1
    failures = compare_metrics(current, tampered)
    assert any(
        "unsanctioned_hex" in f for f in failures
    ), "a hex added outside tokens.css slipped through - the exemption is too wide"


def test_tokens_file_holds_only_token_hex():
    """Narrow the new hiding place: tokens.css may hold declarations, not rules.

    Exempting a file from the hex ratchet creates somewhere to launder hex into - the same
    shape as the app.css hole `shared_css_lines` exists to expose.

    **This narrows the hole, it does not close it, and the limit is line-based.** A line
    containing `--name:` is exempt in full, whatever else is on it, so a multi-line rule
    (`.btn {` / `color: #f00;` / `}`) is caught but a one-line or minified equivalent
    (`--x:#fff; } .btn { color:#f00;`) is not. Nor can it tell a needed primitive from a
    pointless one. Measured, not assumed - UI-020a's review agent verified both directions.

    That matters concretely: `docs/ui/PLAN.md`'s own tokens example is written as a single
    `:root { ... }` line, so a session copying its formatting satisfies this vacuously.
    UI-020 therefore authors tokens.css one declaration per line, which is what makes this
    check bite at all. See DEFERRED D17.

    Vacuous until UI-020 authors the file. That is deliberate: the guard lands before the
    thing it guards, so it bites on the very first commit that could abuse it.
    """
    if not css_baseline.TOKENS_PATH.is_file():
        pytest.skip("01-settings/tokens.css does not exist yet (authored in UI-020)")

    offenders = [
        line.strip()
        for line in css_baseline.TOKENS_PATH.read_text(encoding="utf-8").splitlines()
        if css_baseline.HEX_RE.search(line) and not re.search(r"--[\w-]+\s*:", line)
    ]
    assert offenders == [], (
        "hex in tokens.css must sit on a custom-property declaration - these do not, which "
        "means real rules are being parked in the one hex-exempt file:\n  " + "\n  ".join(offenders)
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
