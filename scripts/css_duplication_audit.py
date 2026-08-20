"""css_duplication_audit.py — how much of 99-legacy/ is actually DUPLICATION?

    .venv/Scripts/python.exe scripts/css_duplication_audit.py

Answers the question the drain's scope decision rests on (ROADMAP.md, 2026-08-19).
Every rule block in 99-legacy/*.css falls into one of three buckets:

  page-only   the selector appears in ONE legacy file. No component is possible;
              draining it means moving the rule from 99-legacy/<page>.css to
              pages/<page>.css, and both are already one file per page. That
              removes no duplication and no CSS.
  agree       the selector appears in two or more files AND every one of them
              declares the same thing. A component can take it with no decision.
  disagree    two or more files, different declarations. A decision first, then
              a component — .btn-ghost was five pages and four looks.

At the time the scope was decided this returned 999 / 100 / 495 of 1,594
rule-block lines, i.e. 63% / 6% / 31%, and the 999 were deliberately skipped.
Re-run it to see where the remaining work sits.

⚠ IT COMPARES DECLARATION TEXT, NOT PAINTED OUTPUT. Two files can declare the
same thing and render differently, because the migrated entry files remap some
legacy token names onto the new tree's roles and leave others on the legacy
literals. That happened six times in one sitting on 2026-08-15/16 — two status
palettes, two primary blues, --radius-btn at 10px against 8px. `agree` here means
"worth measuring next", never "safe to extract". Use scripts/css_selector_probe.mjs
before writing anything.
"""
import re
from collections import defaultdict
from pathlib import Path

LEGACY = Path(__file__).resolve().parent.parent / "static" / "css" / "99-legacy"

FAMILIES = [
    ("modal", r"\.modal|\.btn-cancel|\.btn-save|#status\b"),
    ("btn-*", r"\.btn-"),
    ("status-bar", r"\.status-bar"),
    ("page-head", r"\.page-head"),
    ("field/filter", r"\.field-row|\.filter-bar|\.strip-filter|\.type-checks|label|input|select"),
    ("shell/nav", r"\.app-sidebar|\.app-nav|\.sidebar-foot|\bhtml\b|\bbody\b|\.main\b"),
    ("brand", r"\.brand"),
    ("card", r"\.card"),
    ("shortfall", r"\.shortfall-panel"),
    ("chip/pill/row", r"\.chips|\.pill|\.row\b|\.empty-state|td\.code|\.slo-main"),
]


def strip_comments(text):
    return re.sub(r"/\*.*?\*/", "", text, flags=re.S)


def rules(text):
    """Top-level rules, descending into @media. Returns (selector, body, source)."""
    out, i, n = [], 0, len(text)
    while i < n:
        j = text.find("{", i)
        if j == -1:
            break
        sel = text[i:j].strip()
        k, d = j + 1, 1
        while k < n and d:
            if text[k] == "{":
                d += 1
            elif text[k] == "}":
                d -= 1
            k += 1
        body, raw = text[j + 1 : k - 1], text[i:k].strip()
        if sel.startswith(("@media", "@supports")):
            prefix = " ".join(sel.split()) + " | "
            for s, b, r in rules(body):
                out.append((prefix + s, b, r))
        elif not sel.startswith("@"):
            for s in sel.split(","):
                if s.strip():
                    out.append((" ".join(s.split()), body, raw))
        i = k
    return out


def decls(body):
    d, depth, cur = [], 0, ""
    for ch in body:
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
        if ch == ";" and depth == 0:
            d.append(cur.strip())
            cur = ""
        else:
            cur += ch
    if cur.strip():
        d.append(cur.strip())
    return tuple(sorted(re.sub(r"\s+", " ", x).strip() for x in d if ":" in x))


def family(sel):
    core = sel.split(" | ")[-1]
    for name, pat in FAMILIES:
        if re.search(pat, core, re.I):
            return name
    return "other"


def main():
    occurs = defaultdict(dict)
    blocks = {}
    for f in sorted(LEGACY.glob("*.css")):
        txt = strip_comments(f.read_text(encoding="utf-8", errors="replace"))
        rs = rules(txt)
        for sel, body, _ in rs:
            occurs[sel][f.stem] = decls(body)
        seen, bl = set(), []
        for sel, body, raw in rs:
            if id(raw) in seen:
                continue
            bl.append((sel, len(raw.splitlines()), body))
        blocks[f.stem] = bl

    tot = page_only = agree_l = disagree_l = 0
    fam_a = defaultdict(lambda: [0, 0, set()])
    fam_d = defaultdict(lambda: [0, 0, set()])
    for stem, bl in blocks.items():
        for sel, lines, _body in bl:
            tot += lines
            if len(occurs[sel]) < 2:
                page_only += lines
                continue
            fam = family(sel)
            if len(set(occurs[sel].values())) == 1:
                agree_l += lines
                fam_a[fam][0] += lines
                fam_a[fam][1] += 1
                fam_a[fam][2].add(stem)
            else:
                disagree_l += lines
                fam_d[fam][0] += lines
                fam_d[fam][1] += 1
                fam_d[fam][2].add(stem)

    print("=== 99-legacy, by whether a component is even possible ===")
    print(f"  rule-block lines          {tot:>6}")
    for label, v in (("page-only  (SKIPPED, see ROADMAP)", page_only),
                     ("agree      (component, no decision)", agree_l),
                     ("disagree   (decision, then component)", disagree_l)):
        print(f"  {label:<38}{v:>6}   {v / tot * 100:.0f}%")

    for title, fam in (("AGREE — no decision needed", fam_a),
                       ("DISAGREE — a decision each", fam_d)):
        print(f"\n=== {title} ===")
        print(f"  {'family':<16}{'lines':>7}{'rules':>7}  files")
        for k, (ln, rl, fs) in sorted(fam.items(), key=lambda x: -x[1][0]):
            print(f"  {k:<16}{ln:>7}{rl:>7}  {len(fs)}: {','.join(sorted(fs))}")


if __name__ == "__main__":
    main()
