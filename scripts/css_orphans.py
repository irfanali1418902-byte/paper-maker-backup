"""Orphan-token check — the TOKEN half of the two measurements UI-032 needs per page.

A page on the old tree carries three ``<link>``s, one of them ``/static/theme.css``.
Migrating it drops that link. **What breaks is whatever the page was silently taking
from that file** — and it takes two different kinds of thing:

1. **tokens** — ``var(--x)`` reads whose ``--x`` is declared in ``static/theme.css`` and
   nowhere in the page's own ``99-legacy/<page>.css``. That is D20, and it is what this
   script measures.
2. **whole rules** — ``.btn``/``.card``/``.pagehead`` declarations the page never
   redeclares. **No grep over custom properties can see those**, so this script cannot
   either. That half needs the live DOM and is a separate measurement; ``taqseem``
   (UI-031c) passed the check below and still could not ship because of it.

**So a clean run here is half a page's answer, not a page's answer.** See the NEXT TASK
block in ``docs/ui/STATUS.md``.

Usage — run from anywhere; paths resolve off ``__file__``, not the cwd (UI-018a)::

    python scripts/css_orphans.py                  # all nine pages
    python scripts/css_orphans.py blueprint bank   # just these
    python scripts/css_orphans.py --names          # also list the token names

Why the orphan count is broken into columns rather than reported as one number: the
board's per-page figures (``slo`` 0, ``library`` 0, ``taqseem`` 26) are not all the same
quantity, and collapsing them hides the distinction that decides the work.

``library.css`` reads ``--text``, which **is declared nowhere in the project** (D14). It
is therefore read-but-not-declared, yet unlinking ``static/theme.css`` cannot change it —
it was already falling through before the migration. Counting it as exposure gives
``library`` 1 where the board says 0.

So the number that matters is ``supplied`` — read here, not declared here, declared in
``static/theme.css``, **and that file actually linked by this page**. Those are the values
that change when the link goes. The last condition is not pedantry: ``theme?`` is measured
off the page's own ``<link>``s because ``landing`` and ``print`` never carried the file
(D9), so their orphans are already falling through today and unlinking cannot touch them.
Assume the link instead of measuring it and ``print`` — the Ctrl+P page — reports exposure
it does not have.

``dead`` is everything orphaned that is *not* exposure, for either reason: declared
nowhere in the project (the D14 shape, ``library``'s ``--text``), or declared in
``static/theme.css`` but on a page that does not load it. Worth knowing, not this epic's
to fix.

``app.css`` needs no column: it declares **zero** custom properties, so it supplies none
of this and the old stylesheet is the only source in play.

``compat`` narrows it once more. An orphan already declared by the new tree
(``01-settings/tokens.css`` + ``01-settings/theme.css``) keeps resolving after the swap,
just from a different owner — the three ``--font-*`` names are the deliberate collision
UI-020 documented. Only the rest need a compatibility block in the page's entry file, so
``compat`` is the size of that block. On ``taqseem`` this reproduces the measured split:
26 orphans, 3 covered by Tier 2, **23** in the block that was written.

``collide`` is the other direction, and it is not a failure — it is a change of owner. A
name the page *declares* that the new tree also declares means the page keeps winning
today (``layer(legacy)`` holds its own declaration) but the value now exists twice. Zero
on all five pages measured so far.

``fallback`` counts orphans read as ``var(--x, something)``. Those degrade to the
fallback rather than to nothing, which is the difference between a changed colour and an
unpainted element.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
LEGACY_DIR = PROJECT_ROOT / "static" / "css" / "99-legacy"
PAGES_DIR = PROJECT_ROOT / "static"

# The OLD stylesheet — the one a migration unlinks. Not to be confused with
# static/css/01-settings/theme.css, the Tier 2 palette, which must load (D29: two files
# carry this basename and the Network panel shows only the last segment).
OLD_THEME = PROJECT_ROOT / "static" / "theme.css"

# The new tree's declarations, both files together — a name in either survives the swap.
NEW_TREE = (
    PROJECT_ROOT / "static" / "css" / "01-settings" / "tokens.css",
    PROJECT_ROOT / "static" / "css" / "01-settings" / "theme.css",
)

PAGES = (
    "bank",
    "blueprint",
    "index",
    "landing",
    "library",
    "print",
    "slo",
    "slo-health",
    "taqseem",
)

# Comments first, always. A raw grep over this project has already counted prose inside a
# CSS comment as code twice (UI-018's @page count, UI-020's hex-in-a-comment).
COMMENT_RE = re.compile(r"/\*.*?\*/", re.DOTALL)

# A declaration is a custom property followed by a colon. A read never is: var() puts the
# name before "," or ")", so the two cannot be confused by this pattern.
DECL_RE = re.compile(r"(--[A-Za-z0-9_-]+)\s*:")
READ_RE = re.compile(r"var\(\s*(--[A-Za-z0-9_-]+)\s*([,)])")

# Whether the page actually links the old stylesheet. Measured, not assumed: landing and
# print never had it (D9), so their orphans are already falling through to whatever comes
# next and a migration cannot change them. Assuming the link would report exposure on the
# one page whose Ctrl+P output is the epic's highest-consequence artefact.
THEME_LINK_RE = re.compile(r"""<link[^>]+href=["'](?:/static/theme\.css)["']""", re.I)


def _source(path: Path) -> str:
    """File text with comments removed, or "" if the file does not exist."""
    if not path.is_file():
        return ""
    return COMMENT_RE.sub(" ", path.read_text(encoding="utf-8"))


def declared_names(path: Path) -> set[str]:
    return set(DECL_RE.findall(_source(path)))


def read_names(path: Path) -> dict[str, bool]:
    """``{name: has_fallback}`` for every ``var()`` read in the file."""
    out: dict[str, bool] = {}
    for name, nxt in READ_RE.findall(_source(path)):
        out[name] = out.get(name, False) or nxt == ","
    return out


def measure(page: str) -> dict:
    legacy = LEGACY_DIR / f"{page}.css"
    if not legacy.is_file():
        raise SystemExit(f"no such legacy file: {legacy}")

    declares = declared_names(legacy)
    reads = read_names(legacy)

    theme_names = declared_names(OLD_THEME)
    new_names: set[str] = set()
    for path in NEW_TREE:
        new_names |= declared_names(path)

    html = PAGES_DIR / f"{page}.html"
    links_theme = bool(THEME_LINK_RE.search(html.read_text(encoding="utf-8"))) \
        if html.is_file() else False

    orphans = {n: fb for n, fb in reads.items() if n not in declares}
    # An orphan is only exposure if the old stylesheet is both declaring it AND loaded
    # here. On a page that never linked it, the value is already unresolved today.
    supplied = {n: fb for n, fb in orphans.items() if n in theme_names and links_theme}
    dead = {n: fb for n, fb in orphans.items() if n not in supplied}
    covered = {n for n in supplied if n in new_names}
    compat = {n for n in supplied if n not in new_names}

    return {
        "page": page,
        "links_theme": links_theme,
        "declares": declares,
        "reads": reads,
        "orphans": orphans,
        "supplied": supplied,
        "dead": dead,
        "covered": covered,
        "compat": compat,
        "fallback": {n for n, fb in supplied.items() if fb},
        "collide": declares & new_names,
    }


HEADERS = ("page", "theme?", "decl", "reads", "orphan", "supplied", "covered", "compat",
           "dead", "fallbk", "collide")


def _cells(r: dict) -> list[str]:
    return [
        r["page"],
        "yes" if r["links_theme"] else "no",
        str(len(r["declares"])),
        str(len(r["reads"])),
        str(len(r["orphans"])),
        str(len(r["supplied"])),
        str(len(r["covered"])),
        str(len(r["compat"])),
        str(len(r["dead"])),
        str(len(r["fallback"])),
        str(len(r["collide"])),
    ]


def print_table(rows: list[dict]) -> None:
    table = [list(HEADERS)] + [_cells(r) for r in rows]
    widths = [max(len(row[i]) for row in table) for i in range(len(HEADERS))]

    def fmt(cells: list[str]) -> str:
        return "  ".join(c.ljust(w) if i == 0 else c.rjust(w)
                         for i, (c, w) in enumerate(zip(cells, widths)))

    print(fmt(table[0]))
    print("  ".join("-" * w for w in widths))
    for cells in table[1:]:
        print(fmt(cells))


def print_names(rows: list[dict]) -> None:
    for r in rows:
        if not (r["orphans"] or r["collide"]):
            continue
        print()
        print(f"--- {r['page']}")
        if r["compat"]:
            print(f"  compat block needed ({len(r['compat'])}):")
            for n in sorted(r["compat"]):
                fb = "  [has fallback]" if r["orphans"][n] else ""
                print(f"    {n}{fb}")
        if r["covered"]:
            print(f"  orphan, already declared by the new tree ({len(r['covered'])}):")
            for n in sorted(r["covered"]):
                print(f"    {n}")
        if r["dead"]:
            why = ("static/theme.css is not linked here (D9), so these already fall "
                   "through today" if r["links_theme"] is False
                   else "declared NOWHERE in the project — D14 shape")
            print(f"  orphan but NOT exposure — {why} ({len(r['dead'])}):")
            for n in sorted(r["dead"]):
                fb = "  [has fallback]" if r["orphans"][n] else ""
                print(f"    {n}{fb}")
        if r["collide"]:
            print(f"  declared here AND by the new tree — owner changes ({len(r['collide'])}):")
            for n in sorted(r["collide"]):
                print(f"    {n}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("pages", nargs="*", default=None,
                        help="page names; default is all nine")
    parser.add_argument("--names", action="store_true",
                        help="list the token names behind the counts")
    args = parser.parse_args(argv)

    pages = args.pages or list(PAGES)
    unknown = [p for p in pages if p not in PAGES]
    if unknown:
        raise SystemExit(f"unknown page(s): {', '.join(unknown)}\nknown: {', '.join(PAGES)}")

    if not OLD_THEME.is_file():
        print(f"WARNING: {OLD_THEME} not found — 'supplied' will read 0 for every page.",
              file=sys.stderr)

    rows = [measure(p) for p in pages]
    print_table(rows)
    if args.names:
        print_names(rows)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
