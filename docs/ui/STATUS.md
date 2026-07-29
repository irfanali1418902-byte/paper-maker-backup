# UI-ARCH — Status Board

> **Fresh session: read THIS file first. Do not read PROGRESS.md (2000+ lines).**
> Full plan: `docs/ui/PLAN.md` · Rules: `CLAUDE.md` §11–12 · Parking lot: `docs/ui/DEFERRED.md`

**Branch:** `feat/ui-architecture` · **Baseline tag:** `ui-baseline`
**Last updated:** 2026-07-29 (UI-017)

---

## NEXT TASK → UI-018 — **last of Sprint 1, and the highest-risk page**

**`print.html`** (469 lines / 179 rules — the `<style>` block is lines 8–476, inner 467).
The largest block in the project and the last one standing.

**This head has NO `theme.css`.** Line 7 is `app.css`, line 8 is the `<style>` itself. So the
`<link>` lands at **line 8**, not 9 — and you do **not** add the missing `theme.css`, because
adding a stylesheet is a visual change. This is D9, and UI-013 already walked into it on
`landing.html`; `landing.css` is therefore the closest reference for the head shape, while
`bank.css`/`index.css` are closest in size. Read the actual head before writing anything.

**Why this one is riskiest.** It is the only page whose CSS decides what comes out of a
printer, and the teacher prints from the browser (Ctrl+P / `print.html`) — a broken rule here
is invisible on screen and only shows up on paper. Measured in the block, not taken from
`PLAN.md`: **3 `@page` rules** and **3 `@media print` blocks**. `PLAN.md` §Sprint-1 says "5
`@media print`". **Do not silently reconcile that** (§12 rule 11) — count them yourself and,
if the code is right, say so in the task log rather than editing PLAN.md in passing. There is
also **1 `setProperty`** call in the page's JS, so a custom property is being driven at
runtime; find it and confirm the extraction leaves it working.

Verified clean in advance: **0 `url()`** in the block, so no relative-path hazard.

**87 raw hex — every remaining one in the project.** After this task `hardcoded_hex` reaches
**0** and the whole 324 sits in `99-legacy/`, exactly as the metric notes below predict. That
is the extraction finishing, not colours being deleted: **`total_hardcoded_hex` stays flat at
429**. Do not tokenise one of them.

Cut the `<style>` block **verbatim** into `static/css/99-legacy/print.css` and replace it
with `<link rel="stylesheet" href="/static/css/99-legacy/print.css">` **in the block's own
slot (line 8)**. Cascade order is what makes "zero visual change" true — a `<style>` block and
a `<link>` share origin and specificity, so document order is the only thing holding the
result identical.

**The browser check must include an actual print preview**, not just the screen render:
Ctrl+P and confirm A4 sizing, margins (`@page { margin: 0 }` with the margin carried by
`.sheet` padding — see the block's own opening comment), and page breaks. A green pytest run
proves nothing about paper.

Not one declaration edited, reordered, re-indented or "improved" in transit. Both review
agents byte-compare this (CLAUDE.md §12, review point 6). Extract with a script, not by
retyping, and normalise CRLF/LF on both sides when you verify.

**`git add static/css/` explicitly.** The directory is tracked now, but a new file in it is
not picked up by staging modified files alone. A commit missing it ships a page linking a
404 stylesheet that renders unstyled — while every local gate still passes, because the file
is in your working tree.

Expected movement, and nothing else: `style_blocks` 1 → **0** · `css_lines_in_html` 469 → **0**
· `legacy_css_lines` 1648 → **2115** · `total_css_lines` 2117 → **2115** (exactly −2) ·
`hardcoded_hex` 87 → **0** · `stylesheet_hex` 266 → **353** ·
`total_hardcoded_hex` **flat at 429** · `shared_css_lines` **flat at 269** ·
all three inline metrics **flat** (466 / 385 / 76).
The 87-hex swing between `hardcoded_hex` and `stylesheet_hex` must net to zero. If
`total_hardcoded_hex` moves or `shared_css_lines` rises, the CSS went somewhere it should
not have.

**Sprint 1 ends here.** `style_blocks` and `css_lines_in_html` both reach 0, and
`legacy_css_lines` peaks at 2115 — the debt fully relocated, none of it yet repaid. That
is the plan working. The burn-down starts in Sprint 2.

---

## Progress

`99-legacy/` lines remaining is the real progress metric. **2133 → 0.**

| Sprint | Tasks | Done | State |
|---|---|---|---|
| 0 Guardrails | UI-000..003 | **4/4** | **done** |
| 1 Extraction | UI-010..018 | 8/9 | in progress |
| 2 Foundation | UI-020..021 | 0/2 | not started |
| 3 Shell | UI-030..032 | 0/3 | not started |
| 4 Components | UI-040..043 | 0/4 | not started |
| 5 Inline burn-down | UI-050..052 | 0/3 | not started |
| 6 Legacy kill | UI-060..064 | 0/5 | not started |
| 7 Optional | UI-070 | 0/1 | not started |

### Task log

| ID | Task | Status | Commit | Note |
|---|---|---|---|---|
| UI-000 | Commit baseline, tag, branch | **done** | `addb2fb`, `985f47b` | tagged `ui-baseline`; tree had been dirty (theme.css Modern rewrite + 7 link lines + untracked mockups) |
| UI-001 | Planning docs + CLAUDE.md §11–12 | **done** | `6c381fa` | this document set |
| UI-002 | Ratchet test + BASELINE.json | **done** | `b215666` | 26 tests, 900 passed. 3 extra metrics added (see below). Reviewed twice; 2nd pass found the JS-class check is JS-side only → D11 |
| UI-003 | Remove dead `primary`/`navy` from brand config | **done** | `2eba2f8` | closes D6. Re-verified unused at implementation. Also fixed `api/brand.py` docstring; logo.svg's same hex → D13 |
| UI-010 | Extract `slo.html` CSS → `99-legacy/slo.css` | **done** | `cbd567a` | 91 lines moved verbatim, two reviewers byte-compared. Fixed 2 ratchet defects the first real extraction exposed: `hardcoded_hex` blind to `.css` files → added `total_hardcoded_hex`; a ratchet test anchored to `baseline` broke once a metric legitimately moved |
| UI-011 | Extract `slo-health.html` CSS → `99-legacy/slo-health.css` | **done** | `c05da55` | 111 lines moved verbatim; byte-compared against the original `<style>` inner, exact match at 5754 chars. Metrics landed exactly as predicted. Was built in a prior session but left **uncommitted** — caught at the start of UI-012, verified and committed then |
| UI-012 | Extract `taqseem.html` CSS → `99-legacy/taqseem.css` | **done** | `93f51b9` | 115 lines moved verbatim (6482 chars, exact match). Reviewer substituted the block back in at the `<link>` site and reconstructed `HEAD` byte-for-byte — proves both the verbatim cut and that nothing outside the block moved. Metrics landed exactly as predicted |
| UI-013 | Extract `landing.html` CSS → `99-legacy/landing.css` | **done** | `a9e876c` | 100 lines moved verbatim (3766 chars, exact match); `HEAD` reconstructed byte-for-byte. **This page had no `theme.css` link** — head one line shorter, so the `<link>` went to line 8; none was added, since adding one is a visual change. Metrics landed exactly as predicted |
| UI-013a | `CLAUDE.md` §11 — mark hard rules as end-state | **done** | `4a56b5b` | Docs only, no metric movement. §11's "one `<link>` per page" and "raw hex = CI failure" read as flat rules, but every Sprint 1 page necessarily breaks both in transit — a fresh session could "fix" it mid-sprint and revert a reviewed extraction. Adds an END-STATE preamble and marks the three affected rules with the sprint that retires each. Raised by UI-012's reviewer; committed separately so the extraction diff stayed reviewable |
| UI-014 | Extract `library.html` CSS → `99-legacy/library.css` | **done** | `19448a6` | 251 lines moved verbatim (11677 chars, exact match); `HEAD` reconstructed byte-for-byte at all **67668 bytes**. Largest extraction so far, 2.5× UI-013 — no re-indent or trailing-whitespace drift on any of the 251 lines. The ~39k script body byte-identical (39296 both sides). Found and deferred **D14** (`.pg-btn` reads `var(--text)`, which is defined nowhere) rather than fixing it. Metrics landed exactly as predicted |
| UI-015 | Extract `blueprint.html` CSS → `99-legacy/blueprint.css` | **done** | `5c7f752` | 277 lines moved verbatim (13378 chars, exact match); `HEAD` reconstructed byte-for-byte at all **66883 bytes**, the 46511-byte `<script>` body byte-identical. **First already-token-clean page** — its `:root` aliases onto `theme.css` tokens, so the whole block carried exactly one raw hex (`#fff` in `.btn-primary`), left untouched. `hardcoded_hex` therefore moved only 211 → 210, as predicted. Found and deferred **D15** (a `@media (max-width:760px)` block styling `.app-sidebar`/`.app-nav`/`.sidebar-foot`/`.bp-main`, none of which exist anywhere) rather than fixing it. Metrics landed exactly as predicted |
| UI-016 | Extract `bank.html` CSS → `99-legacy/bank.css` | **done** | `fcdfda1` | 366 lines moved verbatim (18015 chars, sha256 identical both sides); `HEAD` reconstructed byte-for-byte at all **94162 bytes**, the ~1830-line `<script>` body proven untouched. **Largest extraction of the sprint**, ~1.5× UI-014 — reviewer classified drift per line across all 366 and found none, with the indent-depth histogram (`{2: 214, 4: 124}`, 338 indented lines) identical on both sides. All **62 raw hex moved unconverted** in the same order (`var(` flat at 90), the inverse of UI-015's token-clean page. Reviewer additionally served the app and confirmed `/static/css/99-legacy/bank.css` returns **200, text/css, 18015 bytes** — the first live 404-check of the sprint. Frozen inventory 152 → 152. Metrics landed exactly as predicted |

| UI-017a | Ratchet — frozen inventory counted CSS attribute selectors as markup | **done** | `6c2829c` | Guardrail fix, no metric movement. `FROZEN_ATTR_RE` ran over the raw page source including `<style>` blocks, so a quoted attribute *selector* (`.modal-overlay[data-open="1"]`) was indistinguishable from a real markup attribute — extracting the block read as vanished handlers and failed two tests on a correct task. index.html had six (`[data-active="1"]` ×5, `[data-open="1"]`). Now scans markup only, via the `STYLE_ELEMENT_RE` that already existed. Effect surgical: index.html 269 → 263, other eight pages byte-identical, no ratcheted metric moved. Reviewer **mutation-tested** it rather than accepting the argument — five renames (`id`, `onclick`, `data-nav`, `data-lang-opt`, a dropped `data-active`) are all still caught — and found the decisive fact: `data-open="1"` never appears in index.html markup at all, JS sets it at runtime and the markup's `data-open="0"` survives in the inventory. Split from UI-017 so a self-referential guardrail change got reviewed on its own, per UI-013a precedent |
| UI-017 | Extract `index.html` CSS → `99-legacy/index.css` | **done** | `36f3c61` | 337 lines moved verbatim (17681 chars, exact match); `HEAD` reconstructed byte-for-byte at all **130737 bytes**, with all 3 `<script>` blocks (1712 lines) identical. Zero drift on any of 337 lines. All **61 raw hex** moved unconverted (`var(` flat at 87). **Scope trap held**: this page holds 224 of the project's 466 inline `style=""` attrs and 57 of the 76 inline hex — the full inline value sequence is byte-identical, so Sprint 5's work was not started early. The block's `@font-face` uses only `local()` and the block has **0 `url()`**, so relocating the CSS could not break a relative path — worth checking on every future move, since `url()` resolves against the stylesheet, not the document. Exposed the ratchet defect fixed in UI-017a. Reviewer served the app: `/` returns 200 with 0 `<style>` blocks and all three stylesheets 200. Metrics landed exactly as predicted |
---

## Live metrics — these may only go DOWN

Verified at `ui-baseline`, real app pages only (`mockup-modern.html` is a reference, not a page):

**Enforced since UI-002.** `python scripts/css_baseline.py --check` fails on any increase,
and `tests/test_css_architecture.py` fails the suite. Numbers below are no longer maintained
by hand — run the script.

| metric | key | `ui-baseline` | now (UI-017) | target |
|---|---|---:|---:|---:|
| `<style>` blocks in HTML | `style_blocks` | 9 | **1** | 0 |
| CSS lines in HTML | `css_lines_in_html` | 2133 | **469** | 0 |
| page CSS + `99-legacy/` | `total_css_lines` | 2133 | **2117** | 0 |
| inline `style=""` attrs | `inline_style_attrs` | 466 | 466 | ~171 (one-offs only) |
| ⤷ excluding `display:` toggles | `inline_style_non_display` | 385 | 385 | ~171 — **this is the one to drive down** |
| hardcoded hex in `<style>` | `hardcoded_hex` | 324 | **87** | 0 — *but see below, this one lies* |
| hardcoded hex in `style=""` | `hardcoded_hex_inline` | 76 | 76 | 0 |
| **hex anywhere** | `total_hardcoded_hex` | 429 | **429** | 0 — **the honest one** |
| `99-legacy/` lines | `legacy_css_lines` | 0 | **1648** | *informational* — peaks ~2133 after Sprint 1 |
| hex in every `.css` | `stylesheet_hex` | 29 | **266** | *informational* |
| `app.css` + `theme.css` + new tree | `shared_css_lines` | 269 | 269 | *informational* — must grow in Sprint 2 |

**Three are deliberately NOT ratcheted** (`legacy_css_lines`, `stylesheet_hex`,
`shared_css_lines`). `99-legacy/` climbs to ~2133 during Sprint 1 and the new tree grows in
Sprint 2, so a downward ratchet on any of them would fail its own migration.

**`hardcoded_hex` falling is NOT progress during Sprint 1.** It counts only `<style>` blocks
in HTML, so extraction moves hex out of it and into `stylesheet_hex` untouched — UI-010..016
took it 324 → 298 → 273 → 268 → 254 → 211 → 210 → 148 → 87 without removing one colour. It reaches 0 when the last page is
extracted, with
all 324 still in `99-legacy/`. **`total_hardcoded_hex` is the number that has to reach 0**;
it is flat at 429 through extraction and only moves when a hex is genuinely deleted.

**`total_css_lines` drops exactly 2 per page extracted, not 0.** `css_lines_in_html` counts
the `<style>` and `</style>` lines; a `.css` file has neither. Expect **2133 → 2115** across
Sprint 1. A drop larger than 2 on an extraction task means CSS was deleted rather than moved.

**Watch `shared_css_lines` when reviewing.** `total_css_lines` covers page CSS + `99-legacy/`
only, so moving a page's `<style>` block into `app.css` instead of `99-legacy/` passes the
ratchet with three metrics falling and nothing removed. A page shrinking while
`shared_css_lines` jumps by the same amount is debt relocated, not repaid — no automated
check can tell the difference, so that one is on the reviewer.

**Green baseline at `ui-baseline`:** `pytest -q` = 874 passed · `ruff check .` clean.
**Green at UI-002:** `pytest -q` = 900 passed (874 + 26) · `ruff check .` clean ·
`css_baseline.py --check` exit 0.
**Green at UI-011:** `pytest -q` = **902 passed** · `ruff check .` clean ·
`css_baseline.py --check` exit 0.
**Green at UI-012:** `pytest -q` = **902 passed** · `ruff check .` clean ·
`css_baseline.py --check` exit 0. Gates run twice — by the implementing session and
independently by the review agent.
**Green at UI-013:** `pytest -q` = **902 passed** · `ruff check .` clean ·
`css_baseline.py --check` exit 0. Both runs independent (implementer + review agent).
Note `ruff` is not on PATH in this environment — use `python -m ruff check .`.
**Green at UI-014:** `pytest -q` = **902 passed** · `python -m ruff check .` clean ·
`css_baseline.py --check` exit 0. Both runs independent.
**Green at UI-015:** `pytest -q` = **902 passed** · `python -m ruff check .` clean ·
`css_baseline.py --check` exit 0. Both runs independent (implementer + review agent).
**Green at UI-016:** `pytest -q` = **902 passed** · `python -m ruff check .` clean ·
`css_baseline.py --check` exit 0. Both runs independent; the reviewer also served the app
and confirmed the new stylesheet returns 200, not 404.
**Green at UI-017a / UI-017:** `pytest -q` = **902 passed** · `python -m ruff check .` clean ·
`css_baseline.py --check` exit 0, both gates run at each of the two commits. UI-017a was
built and verified on a clean `HEAD` (extraction stashed) so its own commit is green in
isolation, not only in combination.
**Re-pin `BASELINE.json` (`css_baseline.py --write`) as part of every extraction task** —
UI-010..012 did, UI-013 missed it and had to fix it in the close commit; UI-014 and UI-015
did it in-task. Skipping it leaves the next task comparing against numbers two tasks stale.

---

## Decisions locked (do not relitigate)

| Decision | Choice | When |
|---|---|---|
| Palette | **Modern** — indigo `#4f46e5` + teal `#0ea5a4` | 2026-07-28 |
| Design target | `static/mockup-modern.html` | 2026-07-28 |
| Shell fidelity | **Full mockup shell** — `.app` grid + topbar + grouped nav | 2026-07-28 |
| Architecture | ITCSS order + BEM naming + small utility layer | ADR-001 |
| Load mechanism | one `<link>` → `main.css`, `@import` inside | ADR-001 |
| `@layer` | **adopted** — floor is Edge/Chrome 99 (Mar 2022), Edge auto-updates | 2026-07-28 |
| Review gate | every task passes an **independent review agent** before Irfan sees it | 2026-07-28 |
| Dirty tree | committed as-is, tagged `ui-baseline` | 2026-07-28 |
| Branching | one epic branch, one commit per task | 2026-07-28 |
| Push | **never by Claude** — Irfan, via GitHub Desktop | standing |

---

## Blocked / needs Irfan

| # | Item | Needed for |
|---|---|---|
| — | nothing currently blocked | |

---

## How to start a session

1. Read this file. Take **only** the task named under NEXT TASK.
2. Read `CLAUDE.md` §11–12 (rules) and the one page/file that task owns. Nothing else.
3. State a 2-line plan. Wait for go-ahead.
4. Implement — anchored `Edit`s only, inside the declared scope.
5. Self-check all gates, then **spawn the independent review agent**. It can FAIL you;
   on FAIL, fix and re-review. Never hand over a failed or unreviewed task.
6. On PASS, hand to Irfan with a **specific click-list** for his browser check.
7. Only after Irfan says OK: update this file (task log, metrics, NEXT TASK), then commit.
   Never push.
8. Emit a copy-pasteable prompt for the next task's fresh session.
