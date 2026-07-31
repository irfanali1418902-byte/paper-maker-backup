# UI-ARCH — Status Board

> **Fresh session: read THIS file first. Do not read PROGRESS.md (2000+ lines).**
> Full plan: `docs/ui/PLAN.md` · Rules: `CLAUDE.md` §11–12 · Parking lot: `docs/ui/DEFERRED.md`

**Branch:** `feat/ui-architecture` · **Baseline tag:** `ui-baseline`
**Last updated:** 2026-07-31 (UI-021) — **Sprint 2 complete**; next is the browser session, then Sprint 3

---

## NEXT TASK → **the browser session** — *not* a code task, and it comes before UI-030

**Sprint 2 is complete.** `main.css` now carries layers 1–4 (`01-settings` → `03-elements`) and
is still linked by **no page**, so the whole foundation exists with zero visual effect. The
next code task is **UI-030** (`04-objects/shell.css` + nav config), but do the browser check
first — it is cheap now and stops being cheap the moment a page's `<link>` changes.

**What the browser session must cover** (open the app, no code changes):

1. **`print.html` Ctrl+P margin — the epic's highest visual risk.** Expect **~14mm, not 28mm**.
   Sprint 1's nine extractions have *never* been opened in a browser; each has its own commit,
   so a revert is still cheap.
2. **The other eight pages, one load each** — no missing stylesheet, no unstyled flash.
3. **`edge://version` ≥ 99.** ADR-001 accepts `@layer`'s hard-fail risk purely on Edge's
   auto-update, and that assumption has never been tested on a school PC.
4. **`@layer` parses at all.** Never verified in a real browser (UI-020 and UI-021 both said so
   rather than claiming it — the Chrome extension was not connected for any of the five agents).
   Zero risk today; it becomes total risk in UI-031.

**Then UI-030** (`docs/ui/PLAN.md`:188): `04-objects/shell.css` + nav config (groups: Papers /
Content / Plan & track / Settings). Two things carried over from UI-021 that UI-030 owns:

- **`html, body { height: 100% }` is UI-030's to land** — it is in the design target (`:16`) and
  in 7 of the 9 legacy files, but height is layout, not one of `reset.css`'s three concerns.
  Without it the flex/grid shell will not fill the viewport. When it lands it newly reaches the
  **two** files that lack it: `landing.css:18` and `print.css` (which uses `display:flex;
  min-height:100vh` instead) — so **check `print.html` in a browser when you add it** (D21).
- **`--weight-medium` (500) is deliberately absent from `tokens.css`.** It is real
  (`static/theme.css .nav a`) and was left out because a primitive with no Tier 2 consumer is
  how that file rots. The nav is UI-030's, so **UI-030 is the task that adds it** — with its
  Tier 2 role in the same commit.

**Sprint 3 (UI-031/032) is where the traps are: D19, D20 and now D21/D22 are one decision.**
`blueprint.html` and `taqseem.html` are the two pages that actually break (D20: 17 and 20
orphaned tokens, none fallback-protected). Add to that list, all landing in the same session:
base type goes **16px → 15px on nine pages** (`typography.css` `body`), `slo`/`slo-health`
tables take the design target's metrics (`tables.css`), and the button appearance reset is
still parked in **UI-041** (D22) so it does *not* land with them.

---

## Previous task → UI-021 — **done; Sprint 2 foundation complete**

**UI-021** (`docs/ui/PLAN.md` §Sprint-2): `02-generic` reset + fonts + `03-elements`
typography / forms / tables. Five new files, `main.css`'s five `@import`s uncommented in
place, **not one `.html` byte touched**. Same shape as UI-020, same zero visual effect.

**The one thing a fresh session must take from it: a "reset" in this tree is not neutral.**
`layer(generic)` and `layer(elements)` both **outrank `layer(legacy)`**, and layer order beats
selector specificity — so a bare element selector in the new tree overrides a *class* rule in
any of the 2115 legacy lines. That is what "legacy demoted" buys, and it is also what makes a
carelessly-ported reset destructive. UI-021 shipped a reset *smaller* than the design target's
for exactly this reason (**D21**), and parked the button appearance reset entirely (**D22**).
No ratchet metric sees this class of break — it counts lines and hex, not whether a list still
indents.

---

## Earlier → UI-020 — **done; the ratchet was ready for it**

**Sprint 1 is complete.** All nine pages load their CSS from `static/css/99-legacy/`.
`style_blocks` **0** · `css_lines_in_html` **0** · `hardcoded_hex` **0** ·
`legacy_css_lines` **2115** across nine files. Not one colour was deleted getting here —
`unsanctioned_hex` is still **429**, exactly where it started. The debt is fully
relocated and none of it is yet repaid. **That is the point.** Sprint 2 begins the
foundation the burn-down needs; the repayment itself is Sprints 5–6.

**UI-020a is done** (see the task log): the hex ratchet now distinguishes the sanctioned Tier 1
palette from everything else, which is what makes UI-020 writable at all. Do not relitigate it.

**UI-020** (`docs/ui/PLAN.md` §Sprint-2): `main.css` + import order + legacy demoted +
`01-settings` 3-tier tokens (Modern palette). Read PLAN.md and ADR-001 before planning —
this is the first task that *authors* CSS rather than moving it, so the rules that governed
Sprint 1 no longer all apply. Expect ADR-001's `@layer` decision (locked 2026-07-28) to
matter here for the first time.

**The contract changes shape at UI-020, and the metrics change with it.** Sprint 1's
invariant was "`total_css_lines` falls by exactly 2, nothing else moves." That is over.
UI-020 *adds* files under `static/css/`, so **`shared_css_lines` must rise** — it has been
flat at 269 through nine tasks and a rise was a FAIL every time. From here it is expected.
Re-read the ratchet's notes below before assuming a moving number is a defect, and set the
expected movement in the plan **before** writing, so the review agent has something to hold
you to.

**What UI-020 must get right, beyond the obvious:**

- **`unsanctioned_hex` must stay flat at 429.** Authoring `tokens.css` raises
  `total_hardcoded_hex` and `token_hex` together and leaves `unsanctioned_hex` alone — that
  is ratchet-neutral and correct. But **any raw hex in `01-settings/theme.css` (Tier 2) will
  fail**, because only `tokens.css` is exempt. Tier 2 reads `var(--tier-1)`, never a literal.
- **Author `tokens.css` one declaration per line.** `PLAN.md` §2's example is a single line,
  which satisfies `test_tokens_file_holds_only_token_hex` vacuously (D17).
- **`total_css_lines` and `legacy_css_lines` stay at 2115.** `01-settings/` is not
  `99-legacy/`; the new tree lands in `shared_css_lines`.
- **No page head is touched.** The single `<link>` to `main.css` is **Sprint 3** (§11 marks
  that rule end-state). UI-020 therefore has zero visual effect by construction.
- `git add static/css/` **explicitly** — new files there are not staged by adding modified
  files alone.
- After UI-020, `test_tokens_file_holds_only_token_hex` stops skipping: expect **906 passed,
  0 skipped**, not 905/1.

Still true, and still the thing that catches real mistakes: `unsanctioned_hex` may only
fall by genuine deletion, and no page may gain a `<style>` block.

---

## Progress

`99-legacy/` lines remaining is the real progress metric. **2133 → 0.**

| Sprint | Tasks | Done | State |
|---|---|---|---|
| 0 Guardrails | UI-000..003 | **4/4** | **done** |
| 1 Extraction | UI-010..018 | **9/9** | **done** |
| 2 Foundation | UI-020..021 | **2/2** | **done** |
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
| UI-018a | Ratchet test — re-anchor the cwd-independence canary | **done** | `549d0e3` | Test only, no metric movement. `test_measurement_is_cwd_independent` guards CLAUDE.md §12.9: a cwd-relative glob finds no pages from `C:\Users\MCS` and reports a triumphant zero for every metric. Its "we found pages" canary was `style_blocks > 0` — which Sprint 1 drives to 0 by design, so at UI-018 it fired on success. Re-anchored to `per_page` non-empty **and** the same page set. Reviewer mutation-tested it: with `page_paths()` swapped for a cwd-relative glob the new canary still catches it, and a second mutation (4 of 9 pages found) is caught only by the set-equality half — so that half is load-bearing, not decoration. It also established there is **no surviving metric** fit for the job: the six per-page metrics are all driven to 0 by the plan, and the five tree-level ones read `.css` directly so they stay non-zero with zero pages found — blind to the trap entirely. Page count is the only correct anchor. Same class as the defect UI-010 fixed |
| UI-018 | Extract `print.html` CSS → `99-legacy/print.css` | **done** | `6075ed0` | **Last extraction of Sprint 1.** 467 lines moved verbatim (20209 chars, sha256 identical both sides); `HEAD` reconstructed byte-for-byte at all **66389 bytes**, the 35711-byte script body identical. Zero drift on any of 467 lines (indent histogram identical). All **87 raw hex** — every one left in the project — moved unconverted, taking `hardcoded_hex` to **0**. **This head has no `theme.css`** (D9), so the `<link>` went to line 8 and none was added; the page carries exactly 2 stylesheets. Print-critical rules verified intact: 1 `@page { size: A4; margin: 0 }`, 2 `@media print`, and the three JS-driven knobs (`--page-margin: 14mm`, `--q-font: 14px`, `--q-gap: 14px`) still defined with their defaults. Reviewer reasoned the cascade explicitly: `setProperty` on `documentElement.style` writes the style attribute, which outranks author *normal* rules regardless of whether they came from a `<style>` or a `<link>` — the move is cascade-neutral. **Corrects a wrong number this board carried**: the UI-017 handoff said "3 `@page` / 3 `@media print`" from a raw grep that counted prose mentions inside CSS comments. Comments stripped, it is **1 and 2**, confirmed by two independent counts. `PLAN.md`'s "5 `@media print`" is wrong too → **D16**, not edited in passing (§12 rule 11). Metrics landed exactly as predicted |
| UI-020a | Ratchet — sanction Tier 1 token hex, ratchet `unsanctioned_hex` | **done** | `4273da6` | Guardrail fix, no CSS authored. **UI-020 was literally unwritable before this.** `total_hardcoded_hex` was ratcheted and summed hex across *every* `.css` under `static/` (`rglob`), but Tier 1 tokens are raw hex by definition, so authoring `01-settings/tokens.css` at all pushed 429 → ~451 and failed `test_metric_never_increases`. Meanwhile ADR-001:98–99 and §11 both define the invariant as "a raw hex outside `01-settings/tokens.css` is a CI failure" — the end state has hex *inside* that file, so this board's own target of 0 was unreachable by construction. Adds `token_hex` (that one file) + `unsanctioned_hex` (everything else, **ratcheted**); `total_hardcoded_hex` keeps its exact definition and goes informational, so every number in this log stays comparable. `RATCHETED_METRICS` is 8 both sides — one swapped, none dropped (reviewer AST-parsed both revisions). **First review FAILED it, and was right**: the new exemption-scope test asserted against `current` rather than the re-measurement, so it held only while `tokens.css` was absent and would have failed the suite deterministically on the very next task — the UI-018a defect class exactly. Reproduced at `assert 431 == (429 - 3)` before fixing, then re-verified invariant with a real `tokens.css` at **1, 5, 22 and 40 hex**: `unsanctioned_hex` pinned at **429** every time, and `total_hardcoded_hex` hit exactly **451** at 22, matching the projection. Second reviewer mutation-tested the exemption four ways (3 of 4 broadenings caught → D18) and proved hex outside `tokens.css` still trips the ratchet as the *only* failure, isolated so line counts stayed flat. Two limits recorded rather than oversold: the tokens-file guard is line-based (**D17** — PLAN.md's own tokens example is a single line, so UI-020 must author one declaration per line or the guard is vacuous) and the scope test cannot catch a `TOKENS_PATH.parent` broadening (**D18**) |
| UI-020 | `main.css` + import order + legacy demoted + `01-settings` 3-tier tokens | **done** | `01a27f6` | **First task in the epic that AUTHORS CSS rather than moving it.** Three new files, 310 insertions, **not one `.html` byte touched** — `main.css` is linked nowhere (verified over HTTP on all nine pages), so this task has zero visual effect by construction and needed no browser check. `main.css` = `@layer legacy, settings, generic, elements, objects, components, utilities` + 11 `@import`s, and **12 code lines total**; the nine `99-legacy/*` come first into the lowest layer, which is what "legacy demoted" means. They are `@import`ed rather than `<link>`ed because **a plain `<link>` is unlayered and unlayered normal declarations outrank every `@layer`** — linking would invert the cascade this file exists to establish. `tokens.css` = 19 Tier 1 primitives, one declaration per line (D17 — PLAN.md's own example is a single line and would satisfy the guard vacuously); `01-settings/theme.css` = 31 Tier 2 roles, **every one a `var()`, zero raw hex**. Reviewers verified 0 dangling refs and **0 unconsumed primitives** — 5 were deleted (`--font-urdu`, `--radius-1`, `--space-1/-4/-7`) to keep that invariant exact, so the space/radius scales have deliberate documented gaps. Palette is 1:1 with `static/theme.css`'s 19 distinct values, nothing invented. **`unsanctioned_hex` flat at 429** — the ratchet UI-020a built did its job on the first try: a hex quoted in a *Tier 2 comment* took it 429 → 430 and was caught before commit. **First review FAILED it** on three false claims in the comments (§12.12): "linked by 8 pages" (it is **7** — D9), "names do NOT collide" (**three do**: `--font-display`/`--font-body`/`--font-data`, and they must NOT be renamed because `blueprint.css`/`taqseem.css` read them), and D19 missing the token half → **D20**. All three measured and fixed, then re-reviewed PASS |
| UI-021 | `02-generic` reset + fonts · `03-elements` typography / forms / tables | **done** | `8ecb3cc` | **Sprint 2 complete.** Five new files (449 lines), `main.css`'s five `@import`s uncommented **in place** — the order is the cascade — and **not one `.html` byte touched**, so zero visual effect again by construction. `shared_css_lines` 573 → **1178**, the only metric that moved; `unsanctioned_hex` **flat at 429** and the new tree carries **zero raw hex**. Tier 1 gained 15 primitives (7 type steps, 2 weights, 2 leadings, `--font-serif`, `--font-nastaliq`) and Tier 2 13 roles, verified **0 dangling refs and 0 unconsumed primitives** — UI-020's invariant held exactly. **It predicted it would add space steps and did NOT**: control padding (9px 11px) and cell padding (10px/11px) are optical one-offs, left literal, and the one structural value needed was already `--space-inset`; the stale prediction was corrected in `tokens.css` rather than left to mislead. All nine `woff2` resolved on disk against `../../fonts/` — `url()` resolves against the *stylesheet*, the first such path in the tree. **The finding that outlives the task is D21: a reset in this tree is not neutral.** `layer(generic)`/`layer(elements)` outrank `layer(legacy)`, so a bare element selector beats a legacy *class* rule; the design target's `* { padding: 0 }` would have flattened `index.css:267`'s RTL list indentation, so the universal padding kill was **not** ported, the margin reset is targeted at block text elements, and `img` gets `max-width` without the usual `display:block` (it would break the inline `.icon` sprite). Each omission is stated in the file that omits it. **D22** parks the button appearance reset for UI-041 — `border:none; background:none; color:inherit` from `layer(elements)` would flatten `.btn-primary`/`.btn-ghost` across eight legacy files. **The first review FAILED it and was right**: the file shipped `font: inherit`, which is not a synonym for `font-family: inherit` — the shorthand also resets size, weight, style, variant, stretch and line-height, dragging every legacy button to 15px/400 and stripping the 600/700 weights they set by class. Fixed to the longhand, then re-reviewed PASS. Review also corrected three counts that were guessed rather than measured (`html, body {height:100%}` is 7 of 9 files, **not 8 — `print.css` is the second exception and it is the Ctrl+P page**; "exactly two pseudo-element rules" was a wrong generalisation from a `::before`-only grep; a Tier 2 comment's "20 unconsumed roles" mixed two different sets). **D23** records that `--font-mono`/`--font-data` name "IBM Plex Mono", which **no `@font-face` declares and no woff2 in the repo provides** — pre-existing since before this epic, always falling through to `ui-monospace`; the fix is a font-asset decision for Irfan, not CSS |
---

## Live metrics — these may only go DOWN

Verified at `ui-baseline`, real app pages only (`mockup-modern.html` is a reference, not a page):

**Enforced since UI-002.** `python scripts/css_baseline.py --check` fails on any increase,
and `tests/test_css_architecture.py` fails the suite. Numbers below are no longer maintained
by hand — run the script.

| metric | key | `ui-baseline` | now (UI-021) | target |
|---|---|---:|---:|---:|
| `<style>` blocks in HTML | `style_blocks` | 9 | **0** ✅ | 0 |
| CSS lines in HTML | `css_lines_in_html` | 2133 | **0** ✅ | 0 |
| page CSS + `99-legacy/` | `total_css_lines` | 2133 | **2115** | 0 |
| inline `style=""` attrs | `inline_style_attrs` | 466 | 466 | ~171 (one-offs only) |
| ⤷ excluding `display:` toggles | `inline_style_non_display` | 385 | 385 | ~171 — **this is the one to drive down** |
| hardcoded hex in `<style>` | `hardcoded_hex` | 324 | **0** ✅ | 0 — *but see below, this one lies* |
| hardcoded hex in `style=""` | `hardcoded_hex_inline` | 76 | 76 | 0 |
| **hex outside `tokens.css`** | `unsanctioned_hex` | 429 | **429** | 0 — **the honest one** |
| `99-legacy/` lines | `legacy_css_lines` | 0 | **2115** | *informational* — peaks ~2133 after Sprint 1 |
| hex in every `.css` | `stylesheet_hex` | 29 | **372** | *informational* |
| hex in `01-settings/tokens.css` | `token_hex` | 0 | **19** | *informational* — the sanctioned palette |
| hex anywhere | `total_hardcoded_hex` | 429 | **448** | *informational* since UI-020a |
| `app.css` + `theme.css` + new tree | `shared_css_lines` | 269 | **1178** | *informational* — grows through Sprint 2 |

**Five are deliberately NOT ratcheted** (`legacy_css_lines`, `stylesheet_hex`, `token_hex`,
`total_hardcoded_hex`, `shared_css_lines`). `99-legacy/` climbs to ~2133 during Sprint 1 and
the new tree grows in Sprint 2, so a downward ratchet on any of them would fail its own
migration.

**`unsanctioned_hex` is the ratcheted hex metric, not `total_hardcoded_hex`** — changed in
UI-020a. This table used to give `total_hardcoded_hex` a target of **0** and call it "the
honest one". That target was never reachable: ADR-001 and `CLAUDE.md` §11 both state the
invariant as *"a raw hex outside `01-settings/tokens.css` is a CI failure"*, so the end state
has hex **inside** that one file, legitimately — Tier 1 primitives are raw values by
definition. Ratcheting a metric that counted them made UI-020 literally unwritable: authoring
the palette at all pushed the number up and failed the suite. So `token_hex` counts that one
file, `unsanctioned_hex` is everything else and is the ratcheted one, and it **baselines at
429** — the same figure `total_hardcoded_hex` carried through all nine Sprint 1 tasks, because
`tokens.css` did not exist yet. It is a continuation, not a reset. `total_hardcoded_hex` keeps
its exact definition and is still reported every run, so every number in the task log below
stays comparable.

**The new hiding place, stated plainly.** Hex laundered *into* `tokens.css` leaves
`unsanctioned_hex` while nothing was repaid. *Authoring* new primitives is ratchet-neutral
(`total_hardcoded_hex` and `token_hex` rise together, `unsanctioned_hex` flat) — that is the
point of the exemption. *Relocating* existing hex into `tokens.css` drops `unsanctioned_hex`
with nothing deleted from the tree, and that is arithmetically identical to the legitimate
Sprint 5–6 burn-down, so no automated check can separate them. `test_tokens_file_holds_only_token_hex`
narrows it — every hex in that file must sit on a custom-property declaration — but the check
is **line-based**, so a one-line or minified rule defeats it (D17), and it cannot judge whether
a primitive is needed. Like `shared_css_lines`, this one is on the reviewer: **watch `token_hex`
move; a large jump wants a reason.**

**`hardcoded_hex` falling is NOT progress during Sprint 1.** It counts only `<style>` blocks
in HTML, so extraction moves hex out of it and into `stylesheet_hex` untouched — UI-010..016
took it 324 → 298 → 273 → 268 → 254 → 211 → 210 → 148 → 87 → **0** without removing one colour. It reaches 0 when the last page is
extracted, with
all 324 still in `99-legacy/`. **`unsanctioned_hex` is the number that has to reach 0**;
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
**Green at UI-018a / UI-018:** `pytest -q` = **902 passed** · `python -m ruff check .` clean ·
`css_baseline.py --check` exit 0. Same clean-`HEAD` treatment for UI-018a. Reviewer served the
app: `/print.html` 200 with 0 `<style>` blocks, 2 stylesheets, no `theme.css`, and
`print.css` 200 at 20209 bytes.
**Green at UI-020a:** `pytest -q` = **905 passed, 1 skipped** · `python -m ruff check .` clean ·
`black --check` clean on both changed files · `css_baseline.py --check` exit 0. Gates run three
times: implementer, plus two independent review agents (the first FAILED the task). The single
skip is `test_tokens_file_holds_only_token_hex`, vacuous only until `tokens.css` exists — it
un-skips in UI-020. Project-wide `black --check .` reports ~95 unformatted files, but that is
**pre-existing at clean `HEAD`** (verified by stashing: identical count), not introduced here.
**Green at UI-020:** `pytest -q` = **906 passed, 0 skipped** · `python -m ruff check .` clean ·
`css_baseline.py --check` exit 0. The skip is gone because `test_tokens_file_holds_only_token_hex`
un-skips once `tokens.css` exists — expect 906/0 from here, not 905/1. Gates run three times
(implementer + two independent review agents; the first FAILED the task). **Not verified: `@layer`
parsing in a real browser** — the Chrome extension was not connected for the implementer or either
reviewer, and all three said so rather than claiming it. No risk today (`main.css` is linked
nowhere); close it in the pre-Sprint-3 browser session.
**Green at UI-021:** `pytest -q` = **906 passed, 0 skipped** · `python -m ruff check .` clean ·
`css_baseline.py --check` exit 0, with `shared_css_lines` re-pinned to **1178** in-task. Gates
run three times (implementer + two independent review agents; the first FAILED the task on
`font: inherit`). **Still not verified: `@layer` in a real browser** — the Chrome extension was
connected for none of the five agents across UI-020 and UI-021, and all five said so rather than
claiming it. Zero risk while `main.css` is linked nowhere; it becomes total risk at UI-031, so
it is item 4 of the browser session above.
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
