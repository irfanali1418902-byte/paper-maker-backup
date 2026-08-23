"""CSS architecture ratchet — the numbers UI-ARCH drives to zero.

Measures the CSS-debt metrics across the nine real pages in ``static/`` and compares
them to ``docs/ui/BASELINE.json``. **Metrics may only go DOWN.** This is what stops a
later session from quietly reintroducing the 2133 lines of duplicated page CSS that
this epic exists to remove — see ``docs/ui/PLAN.md`` and ``CLAUDE.md`` §11.

Usage — run from the project root::

    python scripts/css_baseline.py            # print the table
    python scripts/css_baseline.py --check    # exit 1 if anything regressed
    python scripts/css_baseline.py --write    # re-baseline (a human decision)

``--write`` is deliberately not something a task runs on its own. Re-baselining
*upward* means the ratchet failed to hold; that is a conversation, not a command.

Two metrics need their direction explained, because the obvious reading is wrong:

``legacy_css_lines`` is **informational, not ratcheted.** Sprint 1 moves every page's
``<style>`` block verbatim into ``static/css/99-legacy/<page>.css``, so this number
climbs to ~2133 before Sprint 6 drains it back to zero. Ratcheting it downward would
fail the very migration it is meant to measure.

``total_css_lines`` (page CSS + legacy CSS) *is* ratcheted. Sprint 1 moves lines
between those two buckets, so the total stays flat; Sprint 6 deletes them, so it
falls. Ratcheting the total plus ``css_lines_in_html`` means page CSS can only shrink
and ``99-legacy/`` is free to absorb the difference in between — which is the shape of
the plan.

**Read ``total_css_lines`` narrowly: it is page CSS + legacy CSS, not all the CSS in
the tree.** It deliberately excludes ``app.css``, ``theme.css`` and the new ITCSS tree,
because those are supposed to *grow* during Sprint 2 and ratcheting them downward would
fail the migration. That leaves one way to cheat the ratchet — move a page's ``<style>``
block into ``app.css`` rather than ``99-legacy/``, and both page-CSS metrics fall while
nothing is actually removed. ``shared_css_lines`` exists to make that visible: it is
reported every run, and a page shrinking while it jumps by the same amount is debt being
relocated, not repaid. No automated check can distinguish the two, so this one is on the
reviewer.

``unsanctioned_hex`` is the ratcheted hex metric, not ``total_hardcoded_hex``. The
architecture's end state is **not** zero hex in the tree — it is zero hex *outside*
``static/css/01-settings/tokens.css``. ADR-001 and CLAUDE.md §11 both put it that way:
"a raw hex outside ``01-settings/tokens.css`` is a CI failure". Tier 1 design tokens are
raw values by definition, so the one sanctioned file has to hold them, and ratcheting a
metric that counts them made UI-020 unwritable — authoring the palette at all pushes
``total_hardcoded_hex`` above 429 and fails the suite. (Projected at ~451 from the 29 hex
in ``static/theme.css``; an estimate, not a measurement, until UI-020 lands.)

So ``token_hex`` counts the hex in that one file, ``unsanctioned_hex`` is everything else,
and it is the ratcheted one. It baselines at **429** — the same number
``total_hardcoded_hex`` carried through all of Sprint 1, because ``tokens.css`` did not
exist yet — and it still only falls by genuine deletion. Sprints 5–6 drive it to 0, which
is reachable; 0 for ``total_hardcoded_hex`` never was. ``total_hardcoded_hex`` keeps its
exact definition and is still reported every run, so every number in the task log stays
comparable; it is simply informational now.

**This creates one new hiding place, and it is the same shape as the ``app.css`` one
above.** Hex laundered *into* ``tokens.css`` leaves ``unsanctioned_hex`` while nothing was
repaid. Two different moves look identical to the arithmetic:

- *authoring* new primitives — ``total_hardcoded_hex`` and ``token_hex`` rise together,
  ``unsanctioned_hex`` flat. Ratchet-neutral, and the point of the exemption.
- *relocating* existing hex into ``tokens.css`` — ``total_hardcoded_hex`` flat,
  ``unsanctioned_hex`` falls with nothing deleted from the tree. This is **also** the
  legitimate Sprint 5–6 burn-down move, so no automated check can separate the two.

``test_tokens_file_holds_only_token_hex`` narrows it — every hex in that file must sit on a
custom-property declaration — but that check is **line-based**: a line containing ``--name:``
is exempt in full, so a multi-line rule is caught and a one-line or minified equivalent is
not. It cannot judge whether a primitive is needed either. So this stays a reviewer's job,
like ``shared_css_lines``: watch ``token_hex`` move, and a large jump wants a reason.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PAGES_DIR = PROJECT_ROOT / "static"
LEGACY_DIR = PROJECT_ROOT / "static" / "css" / "99-legacy"
# The one file allowed to hold raw hex (ADR-001, CLAUDE.md §11). Does not exist until
# UI-020 authors it; token_hex is 0 until then, so unsanctioned_hex == total_hardcoded_hex
# for every number Sprint 1 recorded.
TOKENS_PATH = PROJECT_ROOT / "static" / "css" / "01-settings" / "tokens.css"
BASELINE_PATH = PROJECT_ROOT / "docs" / "ui" / "BASELINE.json"

# mockup-modern.html is the design reference, not a served page. Counting it would
# make the metrics move when nobody touched the app.
EXCLUDED_PAGES = frozenset({"mockup-modern.html"})

# ── how each metric is measured ───────────────────────────────────────────────
# These regexes are the definitions. Changing one silently re-defines the metric
# and invalidates every committed number, so treat them as frozen too.

STYLE_ELEMENT_RE = re.compile(r"<style[^>]*>.*?</style>", re.S | re.I)
STYLE_INNER_RE = re.compile(r"<style[^>]*>(.*?)</style>", re.S | re.I)
# Single-quoted form matches zero attributes today; accepted anyway so introducing one
# later cannot silently drop it out of the count.
INLINE_STYLE_RE = re.compile(r"""\sstyle=(?:"([^"]*)"|'([^']*)')""")
# 4- and 8-digit forms also match nothing today. Longest-first alternation matters:
# put {3} first and #aabbcc scores as #aab plus junk.
# Known false positive from the 4-digit branch: an all-hex CSS id selector. `#face{`
# and `#dead ` count as colours. None exist today. The failure direction is the safe
# one - a false positive raises hardcoded_hex and trips the ratchet loudly rather than
# passing silently - but if this ever fails for a reason that looks insane, look for a
# new id like #faded before you doubt the metric.
HEX_RE = re.compile(
    r"#(?:[0-9a-fA-F]{8}|[0-9a-fA-F]{6}|[0-9a-fA-F]{4}|[0-9a-fA-F]{3})(?![0-9a-fA-F])"
)
CLASS_ATTR_RE = re.compile(r"""\sclass=(?:"([^"]*)"|'([^']*)')""")
SCRIPT_BODY_RE = re.compile(r"<script[^>]*>(.*?)</script>", re.S | re.I)

# Inline styles that drive `display` are paired with JS `el.style.display = '...'`.
# CLAUDE.md §11 says leave them alone, so they are exempt from the burn-down target
# and tracked separately — otherwise the ~171 target is unreachable by construction.
DISPLAY_DECL_RE = re.compile(r"\bdisplay\s*:", re.I)

# The frozen inventory (CLAUDE.md §12.7). A renamed id breaks a handler silently —
# nothing throws, the button just stops working.
#
# D39: this listed `onclick` only, which left 39% of the inline handlers it exists to
# protect outside the guard — `onchange` (61) and `oninput` (20) across static/*.html.
# That gap is not theoretical: UI-046's own `oninput="setPrintRange()"` went in unguarded
# on 2026-08-20 and the ratchet said nothing. `onchange`/`oninput` sit on dropdowns and
# search boxes, so the gap was widest on exactly the filter-heavy pages.
# `onsubmit`/`onkey*`/`onblur`/`onfocus` have zero occurrences today and add zero
# entries; they are listed so the next page that grows one is guarded from its first
# commit rather than after the next silent breakage.
FROZEN_HANDLERS = (
    "onclick",
    "onchange",
    "oninput",
    "onsubmit",
    "onkeyup",
    "onkeydown",
    "onkeypress",
    "onblur",
    "onfocus",
)
FROZEN_ATTR_RE = re.compile(
    r'\b(?:id|name|' + "|".join(FROZEN_HANDLERS) + r')="[^"]*"|\bdata-[a-z0-9-]+="[^"]*"'
)

# Metrics the ratchet enforces. Everything else in the report is informational.
RATCHETED_METRICS = (
    "style_blocks",
    "css_lines_in_html",
    "total_css_lines",
    "inline_style_attrs",
    "inline_style_non_display",
    "hardcoded_hex",
    "hardcoded_hex_inline",
    # Not total_hardcoded_hex: the sanctioned Tier 1 palette in 01-settings/tokens.css is
    # part of the end state, so ratcheting a metric that counts it forbids the tokens file
    # from existing. See the module docstring.
    "unsanctioned_hex",
)

INFORMATIONAL_METRICS = (
    "legacy_css_lines",
    "shared_css_lines",
    "stylesheet_hex",
    "token_hex",
    "total_hardcoded_hex",
)

# JS queries or toggles these classes; a rename breaks them silently.
# Source of truth: docs/ui/PLAN.md §6.
JS_LOAD_BEARING_CLASSES = {
    "bank.html": [
        "bp-type-check",
        "drag-over",
        "open",
        "q-checkbox",
        "sel",
        "smart-details-arrow",
        "topic-img-thumb",
        "urdu-mode",
        "visible",
    ],
    "blueprint.html": ["pin-sec-sel", "sec-card", "show"],
    "index.html": ["an-cards", "js-paper-preview", "js-status", "lang-ur", "qtype", "screen"],
    "library.html": ["card-check", "lib-card", "open", "selected", "visible"],
    "print.html": ["opt-en", "opt-ur", "qhead", "suggest-badge", "open"],
    "taqseem.html": ["col", "col-head", "cov-badge", "show"],
}


# ── measurement ───────────────────────────────────────────────────────────────


def page_paths() -> list[Path]:
    """The real app pages, sorted. Absolute paths — never relative to the cwd.

    The PowerShell tool resets the working directory to ``C:\\Users\\MCS`` between
    calls (CLAUDE.md §12.9), so anything cwd-relative here would measure an empty
    tree and report a triumphant zero.
    """
    return sorted(p for p in PAGES_DIR.glob("*.html") if p.name not in EXCLUDED_PAGES)


def legacy_css_line_count() -> int:
    """Lines across ``static/css/99-legacy/*.css``. Zero until Sprint 1 creates it."""
    if not LEGACY_DIR.is_dir():
        return 0
    return sum(
        len(path.read_text(encoding="utf-8").splitlines())
        for path in sorted(LEGACY_DIR.glob("*.css"))
    )


def stylesheet_hex_count() -> int:
    """Hardcoded hex across **every** stylesheet under ``static/``.

    ``hardcoded_hex`` only sees `<style>` blocks in HTML, which is correct for what it
    measures - "hex still sitting in a page" - and it legitimately falls to 0 during
    Sprint 1. But the hex does not disappear when a page is extracted; it rides along
    into ``99-legacy/<page>.css``. UI-010 proved it: moving slo.html's block dropped
    ``hardcoded_hex`` 324 -> 298 without one colour being removed.

    So this counts the other side of that move, and ``total_hardcoded_hex`` adds the
    three buckets together. Extraction is then flat, and only real deletion moves it.
    """
    return sum(
        len(HEX_RE.findall(path.read_text(encoding="utf-8")))
        for path in sorted(PAGES_DIR.rglob("*.css"))
    )


def token_hex_count() -> int:
    """Hardcoded hex in ``static/css/01-settings/tokens.css`` — the sanctioned ones.

    Tier 1 design tokens *are* raw values; that file is the single place ADR-001 permits
    them. Counting them separately is what lets ``unsanctioned_hex`` be ratcheted without
    forbidding the palette from existing at all.

    Returns 0 while the file is absent, so every Sprint 1 number stays reproducible.
    """
    if not TOKENS_PATH.is_file():
        return 0
    return len(HEX_RE.findall(TOKENS_PATH.read_text(encoding="utf-8")))


def shared_css_line_count() -> int:
    """Lines in every stylesheet under ``static/`` that is *not* ``99-legacy/``.

    Today that is ``app.css`` + ``theme.css``; from Sprint 2 it is also the new
    ITCSS tree. **Informational, never ratcheted** — the new tree is supposed to
    grow, so ratcheting this downward would fail the migration it is measuring.

    It is reported anyway because it is the one place CSS debt can hide: without
    it, a session could move a page's ``<style>`` block into ``app.css`` instead of
    ``99-legacy/``, and both ``css_lines_in_html`` and ``total_css_lines`` would
    fall while not one line of CSS actually went away. Watch this number move in
    step with the ratcheted ones; a page shrinking while this jumps by the same
    amount is debt being relocated, not repaid.
    """
    return sum(
        len(path.read_text(encoding="utf-8").splitlines())
        for path in sorted(PAGES_DIR.rglob("*.css"))
        # `not in parents`, not `parent !=`: a file at 99-legacy/nested/x.css would
        # otherwise be counted here AND missed by legacy_css_line_count's flat glob.
        if LEGACY_DIR not in path.parents
    )


def measure_page(source: str) -> dict[str, int]:
    """Measure one page's HTML source."""
    style_elements = STYLE_ELEMENT_RE.findall(source)
    style_bodies = STYLE_INNER_RE.findall(source)
    # Two alternation groups (double- and single-quoted); exactly one is ever non-empty.
    inline_values = [double or single for double, single in INLINE_STYLE_RE.findall(source)]

    return {
        "style_blocks": len(style_elements),
        # Inclusive of the <style> and </style> lines: that whole span is what has to
        # leave the file, and it is the span the 2133 baseline was measured over.
        "css_lines_in_html": sum(len(el.splitlines()) for el in style_elements),
        "inline_style_attrs": len(inline_values),
        "inline_style_non_display": sum(
            1 for value in inline_values if not DISPLAY_DECL_RE.search(value)
        ),
        "hardcoded_hex": sum(len(HEX_RE.findall(body)) for body in style_bodies),
        # Without this, a colour can be moved out of a <style> block into a style=""
        # attribute: hardcoded_hex falls, nothing improved. This closes that door.
        "hardcoded_hex_inline": sum(len(HEX_RE.findall(value)) for value in inline_values),
    }


def measure() -> dict:
    """Measure the whole tree: totals, per-page breakdown, and the frozen inventory."""
    per_page: dict[str, dict[str, int]] = {}
    inventory: dict[str, list[str]] = {}

    for path in page_paths():
        source = path.read_text(encoding="utf-8")
        per_page[path.name] = measure_page(source)
        # Markup only. A page's CSS can carry quoted attribute selectors —
        # `.modal-overlay[data-open="1"]` — that FROZEN_ATTR_RE cannot tell from a real
        # attribute. Scanning the raw source counts those as markup, so extracting the
        # <style> block reads as vanished handlers and fails a correct task. The
        # inventory is about markup; the CSS half is covered by the verbatim-move check.
        inventory[path.name] = sorted(FROZEN_ATTR_RE.findall(STYLE_ELEMENT_RE.sub("", source)))

    totals = {key: sum(page[key] for page in per_page.values()) for key in measure_page("")}
    totals["legacy_css_lines"] = legacy_css_line_count()
    totals["shared_css_lines"] = shared_css_line_count()
    totals["total_css_lines"] = totals["css_lines_in_html"] + totals["legacy_css_lines"]
    totals["stylesheet_hex"] = stylesheet_hex_count()
    # Every place a hardcoded colour can live. Relocation between the three buckets is
    # flat; only deleting a hex moves this. Informational since UI-020a - its floor is the
    # sanctioned Tier 1 palette, not 0.
    totals["total_hardcoded_hex"] = (
        totals["hardcoded_hex"] + totals["hardcoded_hex_inline"] + totals["stylesheet_hex"]
    )
    totals["token_hex"] = token_hex_count()
    # The ratcheted one: hex outside the single file allowed to hold it. Subtraction, not a
    # re-count, so the two can never drift apart - and tokens.css is inside PAGES_DIR, so
    # its hex is already in stylesheet_hex exactly once.
    totals["unsanctioned_hex"] = totals["total_hardcoded_hex"] - totals["token_hex"]

    return {"metrics": totals, "per_page": per_page, "frozen_inventory": inventory}


# ── comparison ────────────────────────────────────────────────────────────────


def load_baseline(path: Path = BASELINE_PATH) -> dict:
    """Read the committed baseline."""
    return json.loads(path.read_text(encoding="utf-8"))


def compare_metrics(current: dict, baseline: dict) -> list[str]:
    """Failures where a ratcheted metric went UP. Flat and down are both fine."""
    failures = []
    for name in RATCHETED_METRICS:
        now, was = current["metrics"][name], baseline["metrics"].get(name)
        if was is None:
            failures.append(f"{name}: absent from the baseline - re-baseline with --write")
            continue
        if now > was:
            failures.append(f"{name}: {was} -> {now} (+{now - was}) - metrics may only go DOWN")
    return failures


def compare_inventory(current: dict, baseline: dict) -> list[str]:
    """Failures where a frozen id / onclick / name / data-* changed.

    Missing entries are the dangerous direction — a renamed id breaks a handler with
    no error anywhere. Additions fail too (CLAUDE.md §12.7: the inventory does not
    change), but they are reported separately because the fix differs: declare the
    addition in the task scope, then re-baseline with ``--write``.

    Counted, not set-compared. 693 attributes across the 9 pages are only 641 distinct
    strings — the same ``onclick="save()"`` legitimately appears on several buttons. A
    set comparison would let one of two identical handlers be deleted without a word.
    """
    failures = []
    for page in sorted(set(current["frozen_inventory"]) | set(baseline["frozen_inventory"])):
        now = Counter(current["frozen_inventory"].get(page, []))
        was = Counter(baseline["frozen_inventory"].get(page, []))
        for attr, count in sorted((was - now).items()):
            suffix = f" (x{count})" if count > 1 else ""
            failures.append(
                f"{page}: MISSING {attr}{suffix} - renaming this breaks a handler silently"
            )
        for attr, count in sorted((now - was).items()):
            suffix = f" (x{count})" if count > 1 else ""
            failures.append(
                f"{page}: ADDED {attr}{suffix} - declare it in the task scope, then --write"
            )
    return failures


def compare_js_classes(current: dict) -> list[str]:
    """Failures where a JS-load-bearing class vanished from its page's markup or JS.

    **This is a JS-side rename tripwire. Measured, not assumed.** It searches
    ``class="..."`` attribute values and ``<script>`` bodies — not the whole file,
    because a whole-file search also passes on a CSS selector, a comment, or the word
    in ordinary English, which makes it decoration.

    But all 32 of the names below currently appear in a ``<script>`` body, and *none*
    of them depends on the ``class=`` half to pass. So in practice this reduces to
    "does the string still appear in this page's JS", and it fails asymmetrically:

    - renamed in JS (or in both JS and markup) -> detected
    - renamed in **markup only**, JS left stale -> **not detected**

    That last case is markup/JS drift, which is exactly the silent breakage this guard
    is named for. Closing it needs per-class, per-half baseline state; tracked in
    ``docs/ui/DEFERRED.md``. Until then this narrows the window, it does not close it —
    clicking the thing remains the real verification (CLAUDE.md §12.10).
    """
    failures = []
    for page, classes in sorted(JS_LOAD_BEARING_CLASSES.items()):
        path = PAGES_DIR / page
        if not path.is_file():
            failures.append(f"{page}: page is missing entirely")
            continue
        source = path.read_text(encoding="utf-8")
        class_values = [double or single for double, single in CLASS_ATTR_RE.findall(source)]
        searchable = " ".join(class_values + SCRIPT_BODY_RE.findall(source))
        for name in classes:
            if not re.search(rf"(?<![\w-]){re.escape(name)}(?![\w-])", searchable):
                failures.append(
                    f"{page}: JS-load-bearing class '{name}' no longer appears in markup or JS"
                )
    return failures


def compare(current: dict, baseline: dict) -> list[str]:
    """Every failure, in severity order: metrics, then inventory, then JS classes."""
    return (
        compare_metrics(current, baseline)
        + compare_inventory(current, baseline)
        + compare_js_classes(current)
    )


# ── reporting ─────────────────────────────────────────────────────────────────


def format_report(current: dict, baseline: dict | None) -> str:
    """Human-readable table. ``baseline`` may be None when none is committed yet."""
    lines = ["", f"CSS baseline - {len(current['per_page'])} pages under {PAGES_DIR}", ""]
    lines.append(f"  {'metric':<26} {'baseline':>9} {'now':>9}  {'delta':>7}")
    lines.append(f"  {'-' * 26} {'-' * 9} {'-' * 9}  {'-' * 7}")

    for name in RATCHETED_METRICS + INFORMATIONAL_METRICS:
        now = current["metrics"][name]
        # A metric added after the baseline was written has no "was". Report it rather
        # than crashing - a tool that dies on an older baseline teaches people to skip it.
        was = None if baseline is None else baseline["metrics"].get(name)
        if was is None:
            lines.append(f"  {name:<26} {'-':>9} {now:>9}  {'-':>7}")
            continue
        delta = now - was
        marker = "" if name in INFORMATIONAL_METRICS else ("  FAIL" if delta > 0 else "")
        lines.append(f"  {name:<26} {was:>9} {now:>9}  {delta:>+7}{marker}")

    lines.append("")
    lines.append("  legacy_css_lines / shared_css_lines are informational - see the module")
    lines.append("  docstring. legacy rises during Sprint 1 by design; the new ITCSS tree")
    lines.append("  grows shared_css_lines from Sprint 2.")
    lines.append("  unsanctioned_hex is the ratcheted hex metric - total_hardcoded_hex minus")
    lines.append("  the sanctioned Tier 1 palette in 01-settings/tokens.css (token_hex).")
    lines.append("")
    return "\n".join(lines)


# ── cli ───────────────────────────────────────────────────────────────────────


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="CSS architecture ratchet - metrics may only go down."
    )
    parser.add_argument(
        "--check", action="store_true", help="exit 1 if any ratcheted metric increased"
    )
    parser.add_argument(
        "--write", action="store_true", help="overwrite BASELINE.json with current numbers"
    )
    args = parser.parse_args(argv)

    current = measure()
    baseline = load_baseline() if BASELINE_PATH.is_file() else None

    if args.write:
        payload = {
            "_comment": (
                "Committed CSS-debt baseline for the UI-ARCH epic. Ratcheted metrics may "
                "only go DOWN; see scripts/css_baseline.py for how each is measured. "
                "Regenerate with: python scripts/css_baseline.py --write"
            ),
            "metrics": current["metrics"],
            "per_page": current["per_page"],
            "frozen_inventory": current["frozen_inventory"],
        }
        BASELINE_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        print(f"wrote {BASELINE_PATH}")
        return 0

    print(format_report(current, baseline))

    if not args.check:
        return 0

    if baseline is None:
        print(f"FAIL: no baseline at {BASELINE_PATH} - run --write once to create it")
        return 1

    failures = compare(current, baseline)
    if failures:
        print("RATCHET FAILED:\n")
        for failure in failures:
            print(f"  - {failure}")
        print("")
        return 1

    print("  ratchet OK - nothing regressed\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
