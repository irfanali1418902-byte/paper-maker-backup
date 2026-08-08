"""Orphan check — BOTH measurements UI-032 needs per page: tokens and whole rules.

A page on the old tree carries three ``<link>``s, one of them ``/static/theme.css``.
Migrating it drops that link. **What breaks is whatever the page was silently taking
from that file** — and it takes two different kinds of thing:

1. **tokens** — ``var(--x)`` reads whose ``--x`` is declared in ``static/theme.css`` and
   nowhere in the page's own ``99-legacy/<page>.css``. That is D20; it is a grep, and it
   is the default mode of this script.
2. **whole rules** — ``.btn``/``.card``/``.pagehead`` declarations the page never
   redeclares. **No grep over custom properties can see those.** That half needs the live
   DOM and is ``--rules`` below; ``taqseem`` (UI-031c) passed check 1 and still could not
   ship because of it.

**So a clean token run is half a page's answer, not a page's answer.** See the NEXT TASK
block in ``docs/ui/STATUS.md``.

Usage — run from anywhere; paths resolve off ``__file__``, not the cwd (UI-018a)::

    python scripts/css_orphans.py                  # tokens, all nine pages
    python scripts/css_orphans.py blueprint bank   # just these
    python scripts/css_orphans.py --names          # also list the token names

    # the RULE half — needs a served app and launches its own headless Edge
    uvicorn app.main:app                           # in another shell, 127.0.0.1:8000
    python scripts/css_orphans.py --rules blueprint bank index --names
    python scripts/css_orphans.py --rules print --paper-id 12

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
import json
import re
import shutil
import subprocess
import sys
import tempfile
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

# D32 — THE MARKUP PASS. Everything above reads stylesheets only, so a var() inside an
# inline style="" is invisible to it and a page can measure 0 orphan tokens while still
# losing a value when /static/theme.css is unlinked. Found on bank (--line, twice) and
# blueprint (nine names, none with a fallback).
#
# This pass is READ-ONLY on the markup: it parses .html to count reads and never writes
# one. HTML comments are blanked first — a style="" inside <!-- --> is not live, and
# counting it would report exposure a browser never sees.
HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
INLINE_STYLE_RE = re.compile(r"""\bstyle\s*=\s*(["'])(.*?)\1""", re.I | re.DOTALL)


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


def markup_read_names(path: Path) -> dict[str, bool]:
    """``{name: has_fallback}`` for every ``var()`` read inside an inline ``style=""``.

    D32. The same READ_RE as the stylesheet pass, applied to the attribute bodies only —
    so a name is counted once per page however many attributes carry it, and a name with a
    fallback anywhere is treated as having one. The file is only read.

    THE RULE IS TEXTUAL, NOT SEMANTIC, and mkBare is therefore not the whole runtime
    picture. It counts any style="…" string in the file, including ones inside <script>
    that build HTML — three of blueprint's nine come from JS at blueprint.html:330-395 —
    and it does NOT see a style set through the DOM, e.g. blueprint.html:341's
    `box.style.cssText = '…var(--yellow)…'`. Those two names are bare theme.css-only reads
    at runtime; they understate nothing on the board today only because they are already
    inside blueprint's 21 stylesheet orphan tokens. Widening this to the DOM is a
    different task from the one D32 scoped.
    """
    if not path.is_file():
        return {}
    text = HTML_COMMENT_RE.sub(" ", path.read_text(encoding="utf-8"))
    out: dict[str, bool] = {}
    for _quote, body in INLINE_STYLE_RE.findall(text):
        for name, nxt in READ_RE.findall(body):
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

    # D32 — the markup pass, kept in its OWN keys. Nothing above is recomputed and no
    # markup read is folded into `reads`/`orphans`/`supplied`: the two sources answer
    # different questions and merging them would hide which one a number came from.
    markup_reads = markup_read_names(html)
    markup_orphans = {n: fb for n, fb in markup_reads.items()
                      if n not in declares and n not in new_names}
    markup_bare = {n for n, fb in markup_orphans.items() if not fb}

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
        "markup_reads": markup_reads,
        "markup_orphans": markup_orphans,
        "markup_bare": markup_bare,
    }


# The last three are D32's markup pass and are deliberately the RIGHTMOST columns, after
# every stylesheet figure: mkRead = var() names read from inline style="", mkOrph = those
# neither the page's legacy file nor the new tree declares, mkBare = of those, the ones
# with no fallback. mkBare is the number that matters — it is the whole difference between
# bank (one read, fallback present) and blueprint (nine, none).
HEADERS = ("page", "theme?", "decl", "reads", "orphan", "supplied", "covered", "compat",
           "dead", "fallbk", "collide", "mkRead", "mkOrph", "mkBare")


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
        str(len(r["markup_reads"])),
        str(len(r["markup_orphans"])),
        str(len(r["markup_bare"])),
    ]


def print_table(rows: list[dict]) -> None:
    table = [list(HEADERS)] + [_cells(r) for r in rows]
    widths = [max(len(row[i]) for row in table) for i in range(len(HEADERS))]

    def fmt(cells: list[str]) -> str:
        return "  ".join(c.ljust(w) if i == 0 else c.rjust(w)
                         for i, (c, w) in enumerate(zip(cells, widths, strict=True)))

    print(fmt(table[0]))
    print("  ".join("-" * w for w in widths))
    for cells in table[1:]:
        print(fmt(cells))


def print_names(rows: list[dict]) -> None:
    for r in rows:
        if not (r["orphans"] or r["collide"] or r["markup_orphans"]):
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
        if r["markup_orphans"]:
            # D32. Reported separately from every set above, and split by fallback,
            # because that split is the finding: a bare read loses its value outright when
            # static/theme.css goes, a read with a fallback quietly drops to the fallback.
            bare = sorted(r["markup_bare"])
            withfb = sorted(n for n in r["markup_orphans"] if n not in r["markup_bare"])
            print(f"  read from inline style=\"\", declared by neither this page's legacy "
                  f"file nor the new tree ({len(r['markup_orphans'])}):")
            if bare:
                print(f"    NO FALLBACK — lost outright when static/theme.css goes ({len(bare)}):")
                for n in bare:
                    print(f"      {n}")
            if withfb:
                print(f"    has a fallback — drops to it, silently ({len(withfb)}):")
                for n in withfb:
                    print(f"      {n}")


# =============================================================================
# The RULE half (--rules)
# =============================================================================
#
# What is being measured, stated before any number is produced: a rule in
# static/theme.css is EXPOSURE for a page when all three hold —
#
#   (a) the page links /static/theme.css at all          (measured, D9; landing and
#                                                          print never did)
#   (b) the rule's selector matches >=1 element in the page's LIVE DOM
#   (c) the page's own 99-legacy/<page>.css does not redeclare that selector
#
# (c) is exact normalised-selector equality, and that is deliberately the CONSERVATIVE
# direction: a page that covers the same elements through a differently-spelled selector
# still shows up here. So every orphan rule is listed with the properties it carries and
# with any near-miss in the legacy file, because the last step of this judgement is a
# human's, not a grep's. Over-reporting is recoverable; under-reporting ships a page with
# no buttons.

# Comments blanked but offsets preserved, so a rule can be cited by line number.
def _source_lines(path: Path) -> str:
    if not path.is_file():
        return ""
    text = path.read_text(encoding="utf-8")
    return COMMENT_RE.sub(lambda m: re.sub(r"[^\n]", " ", m.group(0)), text)


PROP_RE = re.compile(r"(?:^|;)\s*([-a-zA-Z]+)\s*:")

# State pseudo-classes describe a moment, not a page. `.btn:hover` still belongs to a
# page that has a `.btn`, and querySelectorAll would report 0 for it because nothing is
# hovered in a headless probe. They are stripped for MATCHING and kept in the reported
# selector. Longest alternatives first: `:focus` would otherwise eat the head of
# `:focus-visible` and leave `-visible` behind.
STATE_PSEUDO_RE = re.compile(
    r":(?:focus-visible|focus-within|placeholder-shown|read-only|read-write"
    r"|indeterminate|default|optional|required|disabled|enabled|checked|active"
    r"|visited|hover|focus|target|valid|invalid|link)\b"
)
PSEUDO_ELEMENT_RE = re.compile(r"::[-a-zA-Z]+(?:\([^)]*\))?")


def split_selectors(prelude: str) -> list[str]:
    """Split a selector list on commas that are not inside (), [] or quotes."""
    out, buf, depth, quote = [], [], 0, ""
    for ch in prelude:
        if quote:
            buf.append(ch)
            if ch == quote:
                quote = ""
            continue
        if ch in "\"'":
            quote = ch
            buf.append(ch)
        elif ch in "([":
            depth += 1
            buf.append(ch)
        elif ch in ")]":
            depth -= 1
            buf.append(ch)
        elif ch == "," and depth == 0:
            out.append("".join(buf).strip())
            buf = []
        else:
            buf.append(ch)
    if "".join(buf).strip():
        out.append("".join(buf).strip())
    return [s for s in out if s]


ATTR_QUOTE_RE = re.compile(r"""\[\s*([-\w]+)\s*([~^$*|]?=)\s*["']?([^"'\]]*)["']?\s*\]""")


def norm_selector(sel: str) -> str:
    """Whitespace, case, combinator spacing and attribute quoting normalised.

    Attribute quotes are stripped because the two files spell the same selector two
    ways: ``static/theme.css`` writes ``input[type=text]`` and
    ``03-elements/forms.css`` writes ``input[type="text"]``. Left alone, the same rule
    reads as two and the page reports an orphan it does not have.
    """
    s = re.sub(r"\s+", " ", sel.strip()).lower()
    s = ATTR_QUOTE_RE.sub(lambda m: f"[{m.group(1)}{m.group(2)}{m.group(3)}]", s)
    return re.sub(r"\s*([>+~])\s*", r" \1 ", s)


def probe_selector(sel: str) -> tuple[str, bool]:
    """``(selector querySelectorAll can answer, was it state-only)``."""
    s = PSEUDO_ELEMENT_RE.sub("", sel)
    s = STATE_PSEUDO_RE.sub("", s).strip()
    if not s or s in {">", "+", "~"}:
        return "*", True
    return s, False


def parse_rules(text: str, media: str = "", rules: list | None = None,
                counter: list | None = None, line_base: int = 0) -> list[dict]:
    """Flat list of ``{block, media, selector, props, line}`` for one stylesheet.

    One record per selector, because ``querySelectorAll`` takes one selector at a time —
    but each carries the ``block`` (the ``{}`` it came from) it belongs to, and **the
    block is the unit everything is counted in**. `taqseem`'s hand measurement said "20
    rules matched, 16 redeclared nowhere" counting blocks; `input[type=text], select,
    textarea …` is five selectors and one rule, so counting selectors would report a
    different number for the same fact and nothing would be comparable.

    ``@media``/``@supports`` bodies are recursed into and carry their condition; every
    other at-rule (``@font-face``, ``@keyframes``, ``@page``) declares no selector that
    can match a page element and is skipped whole.
    """
    if rules is None:
        rules = []
    if counter is None:
        counter = [0]
    i, n = 0, len(text)
    while i < n:
        brace = text.find("{", i)
        if brace == -1:
            break
        prelude = text[i:brace].strip()
        depth, k = 1, brace + 1
        while k < n and depth:
            if text[k] == "{":
                depth += 1
            elif text[k] == "}":
                depth -= 1
            k += 1
        body = text[brace + 1:k - 1]
        if prelude.startswith("@"):
            at = prelude.split(None, 1)[0].lower()
            if at in ("@media", "@supports"):
                inner = prelude if not media else f"{media} AND {prelude}"
                parse_rules(body, inner, rules, counter,
                            line_base + text.count("\n", 0, brace + 1))
        elif prelude:
            line = line_base + text.count("\n", 0, brace) + 1
            props = [p.lower() for p in PROP_RE.findall(body)]
            block = counter[0]
            counter[0] += 1
            for sel in split_selectors(prelude):
                rules.append({"block": block, "media": media, "selector": sel,
                              "props": props, "line": line})
        i = k
    return rules


def theme_rules() -> list[dict]:
    """Every rule in the OLD stylesheet, tagged for how it should be counted."""
    out = []
    for idx, r in enumerate(parse_rules(_source_lines(OLD_THEME))):
        probe, state_only = probe_selector(r["selector"])
        r = dict(r)
        r["id"] = f"r{idx}"
        r["norm"] = norm_selector(r["selector"])
        r["probe"] = probe
        r["state_only"] = state_only
        # :root is the token rule. It matches every page trivially and everything it
        # carries is already counted by the TOKEN half — counting it here as well would
        # double-count the one thing both checks can see.
        r["is_token_rule"] = r["norm"] in (":root", "html", ":where(:root)")
        out.append(r)
    return out


def legacy_selectors(page: str) -> dict[str, set[str]]:
    """``{normalised selector: every property the page declares on it}``.

    The properties are the half a selector-only check gets wrong in the safe direction.
    ``index.css``:144 declares ``.summary-row`` — so a selector-equality check calls
    theme.css's ``.summary-row`` redeclared and safe — but it declares display,
    justify-content, font-size and padding and **not** ``border-bottom``, which is the
    dashed rule between the rows. Unlink theme.css and those separators go, on a page
    reported clean.
    """
    out: dict[str, set[str]] = {}
    for r in parse_rules(_source_lines(LEGACY_DIR / f"{page}.css")):
        out.setdefault(norm_selector(r["selector"]), set()).update(r["props"])
    return out


def _class_tokens(sel: str) -> list[str]:
    return re.findall(r"\.([A-Za-z0-9_-]+)", sel)


def near_misses(sel: str, legacy: set[str], limit: int = 3) -> list[str]:
    """Legacy selectors mentioning this rule's last class — the human's next glance.

    Matched on a class-name boundary, not as a substring: ``.ch`` inside ``.chip`` is a
    different class and offering it as a near-miss is the same shape of noise this epic
    keeps failing on.
    """
    classes = _class_tokens(sel)
    if not classes:
        return []
    key = re.compile(rf"\.{re.escape(classes[-1])}(?![\w-])")
    return sorted(s for s in legacy if key.search(s))[:limit]


def measure_rules(page: str, counts: dict[str, int], rules: list[dict]) -> dict:
    html = PAGES_DIR / f"{page}.html"
    links_theme = bool(THEME_LINK_RE.search(html.read_text(encoding="utf-8"))) \
        if html.is_file() else False
    legacy = legacy_selectors(page)

    # Group the per-selector probe results back into the rule blocks they came from.
    blocks: dict[int, dict] = {}
    invalid = []
    for r in rules:
        if r["is_token_rule"]:
            continue
        n = counts.get(r["id"], 0)
        if n < 0:
            invalid.append(r)
            continue
        b = blocks.setdefault(r["block"], {
            "block": r["block"], "line": r["line"], "media": r["media"],
            "props": r["props"], "selectors": [], "hits": [], "orphan_sels": [],
        })
        b["selectors"].append(r)
        if n > 0:
            b["hits"].append((r, n))
            if r["norm"] not in legacy:
                b["orphan_sels"].append(r)
            else:
                # Redeclared — but with which properties? Custom properties are the
                # TOKEN half's business and are excluded here.
                missing = {p for p in r["props"] if not p.startswith("--")} \
                    - legacy[r["norm"]]
                if missing:
                    b.setdefault("partial_sels", []).append((r, sorted(missing)))

    matched, redeclared, partial, orphan, media_scoped = [], [], [], [], []
    for b in sorted(blocks.values(), key=lambda x: x["block"]):
        if not b["hits"]:
            continue
        if b["media"]:
            # Only applies at that viewport, so it is not part of the headline count for
            # a page measured at one width. Reported, never mixed in.
            media_scoped.append(b)
            continue
        matched.append(b)
        # A block is only safe when every selector of it that reaches this page is
        # redeclared by the page's own file. One uncovered selector still takes its
        # declarations away when the link goes.
        if b["orphan_sels"]:
            orphan.append(b)
        elif b.get("partial_sels"):
            partial.append(b)
        else:
            redeclared.append(b)

    return {
        "page": page,
        "links_theme": links_theme,
        "matched": matched,
        "redeclared": redeclared,
        "partial": partial,
        "orphan": orphan,
        "state_only": [b for b in orphan
                       if all(x["state_only"] for x in b["orphan_sels"])],
        "exposure": orphan if links_theme else [],
        "media_scoped": media_scoped,
        "invalid": invalid,
        "legacy": legacy,
    }


# `state` is broken out of `orphan` so a run here stays comparable with the hand
# measurement this method was validated against. `taqseem` was measured by hand at 20
# matched / 16 orphan; this script reports 21 / 17, and the whole of the difference is
# `:focus-visible` — a state-only rule with no elements of its own, which a
# querySelectorAll method can only report as universal and a hand method never listed.
# It applies identically to all nine pages, so it is real but it is not a page's finding.
RULE_HEADERS = ("page", "theme?", "elems", "match", "redecl", "partial", "orphan",
                "state", "EXPOSURE", "media", "drift")


def print_rule_table(rows: list[dict], probe: dict) -> None:
    table = [list(RULE_HEADERS)]
    for r in rows:
        p = probe["pages"].get(r["page"], {})
        table.append([
            r["page"],
            "yes" if r["links_theme"] else "no",
            str(p.get("elements", "?")),
            str(len(r["matched"])),
            str(len(r["redeclared"])),
            str(len(r["partial"])),
            str(len(r["orphan"])),
            str(len(r["state_only"])),
            str(len(r["exposure"])),
            str(len(r["media_scoped"])),
            str(len(p.get("drift", []) or [])),
        ])
    widths = [max(len(row[i]) for row in table) for i in range(len(RULE_HEADERS))]

    def fmt(cells: list[str]) -> str:
        return "  ".join(c.ljust(w) if i == 0 else c.rjust(w)
                         for i, (c, w) in enumerate(zip(cells, widths, strict=True)))

    print(fmt(table[0]))
    print("  ".join("-" * w for w in widths))
    for cells in table[1:]:
        print(fmt(cells))


def print_rule_names(rows: list[dict], probe: dict) -> None:
    for r in rows:
        p = probe["pages"].get(r["page"], {})
        print()
        print(f"--- {r['page']}  ({p.get('url', '?')})")
        if p.get("errors"):
            for e in p["errors"]:
                print(f"  !! {e}")
        if p.get("screens"):
            for name, s in p["screens"].items():
                state = f"{s['elements']} elems" if s.get("ok") else f"FAILED: {s.get('error')}"
                print(f"  screen {name}: {state}")
        if r["invalid"]:
            print(f"  selectors the engine rejected ({len(r['invalid'])}):")
            for x in r["invalid"]:
                print(f"    theme.css:{x['line']}  {x['selector']}")
        if not r["links_theme"]:
            print("  /static/theme.css is NOT linked here (D9) — the rules below already")
            print("  fail to apply today, so a migration cannot change them. EXPOSURE = 0.")
        if r["orphan"]:
            print(f"  matched here, redeclared NOWHERE in 99-legacy/{r['page']}.css "
                  f"({len(r['orphan'])} rules):")
            for b in r["orphan"]:
                sels = ", ".join(x["selector"] for x in b["selectors"])
                print(f"    theme.css:{b['line']:<4} {sels}")
                for x, n in b["hits"]:
                    covered = "redeclared" if x["norm"] in r["legacy"] else "ORPHAN"
                    state = " [state-only]" if x["state_only"] else ""
                    print(f"        {x['selector']}  ×{n}  {covered}{state}")
                print(f"        props: {', '.join(dict.fromkeys(b['props']))}")
                for x in b["orphan_sels"]:
                    for hint in near_misses(x["selector"], r["legacy"]):
                        print(f"        near-miss in legacy: {hint}")
        if r["partial"]:
            print(f"  selector redeclared but NOT every property — the properties below "
                  f"still go when the link goes ({len(r['partial'])} rules):")
            for b in r["partial"]:
                print(f"    theme.css:{b['line']:<4} "
                      f"{', '.join(x['selector'] for x in b['selectors'])}")
                for x, missing in b["partial_sels"]:
                    print(f"        {x['selector']}  missing from legacy: "
                          f"{', '.join(missing)}")
        if r["redeclared"]:
            print(f"  matched and fully redeclared by the page itself — safe "
                  f"({len(r['redeclared'])} rules):")
            for b in r["redeclared"]:
                print(f"    {', '.join(x['selector'] for x in b['selectors'])}")
        if r["media_scoped"]:
            print(f"  matched inside a media query — not counted at this viewport "
                  f"({len(r['media_scoped'])} rules):")
            for b in r["media_scoped"]:
                mark = "" if not b["orphan_sels"] else "   NOT redeclared"
                sels = ", ".join(x["selector"] for x in b["selectors"])
                print(f"    {b['media']}  {sels}{mark}")


def find_edge() -> str:
    candidates = [
        Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
        Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
    ]
    for c in candidates:
        if c.is_file():
            return str(c)
    found = shutil.which("msedge") or shutil.which("chrome")
    if found:
        return found
    raise SystemExit("no Edge/Chrome found; pass --edge <path to msedge.exe>")


def page_url(page: str, base: str, paper_id: str | None) -> str:
    if page == "print":
        if not paper_id:
            raise SystemExit(
                "print.html renders nothing without ?paper_id= — it is the Ctrl+P page and "
                "must be measured on a real exam paper, never a blank one (STATUS.md). "
                "Pass --paper-id <id>."
            )
        return f"{base}/print.html?paper_id={paper_id}"
    return f"{base}/{page}.html"


def run_probe(pages: list[str], args) -> dict:
    probe_input = {
        "edge": args.edge or find_edge(),
        "viewport": {"width": args.width, "height": args.height},
        "settleMs": args.settle,
        "screenSettleMs": args.screen_settle,
        "pages": [
            {
                "page": p,
                "url": page_url(p, args.base_url.rstrip("/"), args.paper_id),
                # index.html holds 7 screens; six are not in the default view.
                "screens": INDEX_SCREENS if p == "index" else [],
            }
            for p in pages
        ],
        "probes": [{"id": r["id"], "sel": r["probe"]}
                   for r in theme_rules() if not r["is_token_rule"]],
    }
    with tempfile.TemporaryDirectory() as tmp:
        in_path = Path(tmp) / "probe-in.json"
        in_path.write_text(json.dumps(probe_input), encoding="utf-8")
        node = shutil.which("node")
        if not node:
            raise SystemExit("node not on PATH — the DOM half needs it to drive Edge")
        proc = subprocess.run(
            [node, str(Path(__file__).with_name("css_rules_probe.mjs")), str(in_path)],
            capture_output=True, text=True, encoding="utf-8",
        )
    if proc.returncode != 0:
        raise SystemExit(f"probe failed:\n{proc.stderr}")
    if proc.stderr.strip():
        print(proc.stderr.strip(), file=sys.stderr)
    return json.loads(proc.stdout)


INDEX_SCREENS = ("generate", "mypapers", "analytics", "adaptive", "results", "settings",
                 "syllabus")


def rules_main(pages: list[str], args) -> int:
    rules = theme_rules()
    if args.from_json:
        probe = json.loads(Path(args.from_json).read_text(encoding="utf-8"))
    else:
        probe = run_probe(pages, args)
    if args.json:
        Path(args.json).write_text(json.dumps(probe, indent=1), encoding="utf-8")

    rows = []
    for p in pages:
        rec = probe["pages"].get(p)
        if rec is None:
            print(f"WARNING: no probe result for {p}", file=sys.stderr)
            continue
        if "counts" not in rec:
            print(f"WARNING: {p} produced no counts: {rec.get('errors')}", file=sys.stderr)
            continue
        rows.append(measure_rules(p, rec["counts"], rules))

    probed = {r["block"] for r in rules if not r["is_token_rule"]}
    skipped = {r["block"] for r in rules if r["is_token_rule"]}
    print(f"static/theme.css: {len(probed)} rules probed "
          f"({len(rules)} selectors; {len(skipped)} token rule(s) excluded — "
          f"the TOKEN half counts those)")
    print(f"browser: {probe.get('browser', '?')}")
    print()
    print_rule_table(rows, probe)
    if args.names:
        print_rule_names(rows, probe)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("pages", nargs="*", default=None,
                        help="page names; default is all nine")
    parser.add_argument("--names", action="store_true",
                        help="list the token/rule names behind the counts")
    parser.add_argument("--rules", action="store_true",
                        help="run the RULE half instead: needs a served app, drives Edge")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--paper-id", default=None,
                        help="required for print.html — measure a real exam paper")
    parser.add_argument("--edge", default=None, help="path to msedge.exe")
    parser.add_argument("--width", type=int, default=1280)
    parser.add_argument("--height", type=int, default=900)
    parser.add_argument("--settle", type=int, default=2500,
                        help="ms to wait after load before probing")
    parser.add_argument("--screen-settle", type=int, default=1200,
                        help="ms to wait after showScreen() on the SPA")
    parser.add_argument("--json", default=None, help="write the raw probe result here")
    parser.add_argument("--from-json", default=None,
                        help="re-report from a saved probe result, no browser")
    args = parser.parse_args(argv)

    pages = args.pages or list(PAGES)
    unknown = [p for p in pages if p not in PAGES]
    if unknown:
        raise SystemExit(f"unknown page(s): {', '.join(unknown)}\nknown: {', '.join(PAGES)}")

    if not OLD_THEME.is_file():
        print(f"WARNING: {OLD_THEME} not found — 'supplied' will read 0 for every page.",
              file=sys.stderr)

    if args.rules:
        return rules_main(pages, args)

    rows = [measure(p) for p in pages]
    print_table(rows)
    if args.names:
        print_names(rows)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
