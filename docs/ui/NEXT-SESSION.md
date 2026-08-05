# NEXT SESSION — start here

> **Updated 2026-08-05 (second update), after `print` was HELD.** Read `docs/ui/STATUS.md`
> first — it is the SOURCE OF TRUTH, and it now contains the `print` decision and the margin
> test's BEFORE numbers. **The exception note that used to be here is gone**: everything below
> is committed, and STATUS.md no longer trails this file.

**Branch:** `feat/ui-architecture` · **Working dir:** `C:\PaperMaker\paper-maker-mvp`

---

## ✅ `print` IS HELD (2026-08-05). Sprint 3 closes at 3 of 9. Start at D34.

**Irfan held `print` on a reported space-token regression** — a right margin moving 48px → 24px
and a `.count-grid` collapsing on Q10. **That report is now retired: D35.** The swap was
performed, AFTER measured, the tree reverted, and **the margin does not move** — `.sheet` is
52.9134px (14mm) on all four sides both ways and no box delta lands on the margin chain.
`.count-grid` exists nowhere in the repo and no legacy file reads `--space-*`.
**Do not schedule Sprint 4 work for space tokens.**

**The hold still stands, on a different and now-measured reason: D36.** `0d04c750` goes
**2 → 3 printed pages** (+6.0% sheet height) — D21/F3's line-height growth crossing an A4
boundary. One more sheet per exam, per student, on the Ctrl+P page. **`print`'s blocker is now
UI-044, the leading decision**, the same one `bank` and D33 wait on.

**State:** the tree is at HEAD. `static/css/pages/print.css` does not exist, the entry file is
parked at `docs/ui/parked-print.css`, `shared_css_lines` is 1616 and `BASELINE.json` is not
re-pinned. The swap-and-revert left nothing behind — `git status` clean, ratchet flat.

## 🛑 THE DECIDING TEST — **both halves are now run**

**The margin test is complete.** `print`'s findings below are labelled F1, F2 and F3, and
**F1 is the ink-colour change — it is NOT margins.** Do not read "F1 done" as "margins
checked". **Nothing in this file's F1/F2/F3 covers the page-margin architecture** — this block
does.

**What was measured 2026-08-05, in print media, BEFORE and AFTER, and does NOT need redoing** —
three real papers, Edge `Edg/151.0.4129.59` at 1280×900, `document.fonts.ready` awaited, two
snapshots per page with **drift 0**:

- `@page { size: a4; margin: 0px }` — present, and **unlayered**, from `99-legacy/print.css`.
- `html`, `body`, `.print-main` — padding, margin and border-width all **0 0 0 0**.
- **`.sheet` padding 52.9134px on all four sides = exactly 14mm.** `print.css`:1-2's
  single-source claim is now measured rather than asserted.
- knobs `--page-margin: 14mm`, `--q-font: 14px`, `--q-gap: 14px` on `documentElement.style`.
- sheet height 6323.81px and **555 elements** on `9ade2655` — both independently reproducing
  the earlier session's numbers.
- **There is no 48px or 24px anywhere on the margin chain.** `.print-main`'s 24px is
  screen-only; `print.css`:219 zeroes it in print.

**And after the swap, measured the same way:** `.sheet` **unchanged at 52.9134px** on all four
sides on all three papers, every ancestor still 0, **zero box deltas on the margin chain**,
knobs identical, and `@page` still applying — confirmed by an import-aware CSSOM walk
(`layer=legacy`) and by all six PDFs carrying an identical A4 MediaBox.

**The 48 padding deltas are named**: 12 form controls × 4 sides, all from
`03-elements/forms.css`:68's `padding: 9px 11px`, all inside `.no-print` chrome (edit modal,
topic strip, library picker) — **zero effect on the printed artefact.**

**What is still NOT done:** a **real printer**. Everything above is `Page.printToPDF`, the right
tool for measuring CSS and not proof of a physical print. Check a real print preview at the page
edges before `print` is unheld — and re-run the harness after UI-044 to confirm all three papers
return to HEAD's page counts (**2 / 6 / 7**).

**Why this is the decisive one and the ink colour is not:** a printed exam paper's margins are
what make it usable — hole-punch edge, binding, the guarantee that nothing is cut off by the
printer. `99-legacy/print.css`:1-2 says in its own comment that the margin is **single-sourced**:
`@page` carries `margin: 0` and **all** of the page margin comes from `.sheet`'s
`padding: var(--page-margin)` (14mm). That comment also records that it was **once double** —
`@page` 14mm plus `.sheet` 14mm = 28mm — so this page has already been broken this way once.

**What WAS verified (do not redo):**

- `@page { size: A4; margin: 0 }` (`print.css`:3) is present and the migration does not touch it.
- The three knobs resolve identically before and after — `--page-margin: 14mm`, `--q-font: 14px`,
  `--q-gap: 14px`. `setVar()` writes them onto `documentElement.style`, an inline declaration
  outranking every layer.

**What was NOT verified — this is the actual gap:**

- **The before/after diff showed `padding-top`, `padding-right`, `padding-bottom` and
  `padding-left` each changing on 12 element-instances, and WHICH elements those are was never
  identified.** If any of them is `.sheet` or sits on the margin chain, the printed margin moved
  and nobody has looked.
- Whether `02-generic/reset.css` or the new tree's space tokens reach `.sheet`, `.print-main` or
  any ancestor carrying the page margin.
- Whether `@page`'s own declarations interact with cascade layers once the legacy file is
  imported into `layer(legacy)` rather than linked unlayered.
- Whether the margin survives a **real printer**, not just `Page.printToPDF` — the PDF was
  produced with `marginTop/Bottom/Left/Right: 0` and `preferCSSPageSize: true`, which is the
  right setting for measuring CSS but is not proof of what a physical print does.

**How to run it:** migrate the page (the entry file is parked and the swap is one line), then
measure `.sheet`'s computed `padding` and box in **print media** before and after, identify all
48 padding deltas by element, and produce the PDF both ways. **Then check a real print preview
at the physical page edges**, not just that the pages count the same.

**`print` does not ship until this is done and looks right.** The Ctrl+P check that already
happened confirmed the paper's *content* was correct; it was not a margin measurement.

---

## ⚠ READ THIS FIRST — the tree is clean, and that is deliberate

**`print`'s history has two chapters and they must not be merged.** In the **first** session it
was migrated, measured, and **Irfan checked it in a real Ctrl+P print preview on two real
papers and said it was correct and should ship** — then it was reverted unshipped, because the
independent review agent (§12 step 5) **died part-way through on an API monthly spend limit**
and §12 forbids committing a shipping change unreviewed. At that point the page was *not* held.

**In the second session (2026-08-05) it was HELD** on a reported `--space-*` margin regression.
**A third pass then measured that report and retired it (D35)** — the swap was performed, the
AFTER half measured, the tree reverted, and the printed margin does not move at all. **The same
run found the real regression, D36**: `0d04c750` gains a printed page. **The hold was right and
its stated reason was wrong**, which is worth remembering the next time a page is held on a
description rather than a measurement.

**State right now:**

| | |
|---|---|
| `static/print.html` | **at HEAD** — its two original `<link>`s |
| `static/css/pages/print.css` | **does not exist** — the entry file is parked at `docs/ui/parked-print.css` |
| `BASELINE.json` | **at HEAD** — nothing shipped, so nothing to re-pin |
| ratchet | `shared_css_lines` **1616**, `unsanctioned_hex` **429**, OK |
| the swap-and-revert | left nothing behind — `git status` clean, every ratchet metric flat |

**The decision has been made: `print` does not ship until UI-044 settles D36.** Start at
**UI-044**; D34 is closed and Sprint 4's order is in `PLAN.md`.

---

## THE `print` FINDINGS — measured this session, none of it yet on the board

### What the migration is

**One line.** `print.html` is the only page in the epic with just two `<link>`s and it **never
linked `/static/theme.css`** (D9). So the swap is its legacy link → the entry file; `app.css`
stays. **−4 bytes, one hunk**, both `<script>` blocks byte-identical (35610 bytes, sha256
`b049c24d8fa93e06`), frozen inventory diff empty (id 53/53, onclick 21/21, name 1/1, data 5/5,
class 142/142).

**Because there is no theme.css to unlink, mechanism 1 does not exist on this page** — no white
slab, no `.tag` chip, no `.summary-row` rule. Everything that moves is the new tree beating
`layer(legacy)`, i.e. **D21 on its own for the first time in the epic**.

### The method changed for this page, and it should stay changed

- **Measure in PRINT media** (`Emulation.setEmulatedMedia({media:'print'})`). Screen media does
  not even apply this page's two `@media print` blocks (`99-legacy/print.css`:215 and :375), so
  a screen measurement describes a page nobody prints.
- **Measure pagination by producing the PDF** (`Page.printToPDF`) and counting its pages — not
  by dividing a document height by 1123. That is the literal Ctrl+P answer.
- **Load the webfont before believing any Urdu line box.** See F2 below; this one bit.

### F1 — the printed page's ink colour changes on every element · **NOT margins**

`rgb(26,26,26)` → `rgb(15,23,42)`. `99-legacy/print.css`:26's `body { color: … }` loses to
`03-elements/typography.css`'s `body { color: var(--color-text) }` in `layer(elements)`.
**400+ printed elements**, near-neutral black → slate-900 blue-black. This is the single most
widespread change and it is on the artefact a teacher hands out.

### F2 — the Urdu that matters, and the Urdu that only looked like it mattered

**`.school-ur` IS exposed. It shipped-nothing only because the field is empty.**
`99-legacy/print.css`:126 `.letterhead .school-ur` sets `"Noto Nastaliq Urdu"` at 19px and **no
`line-height`**, and no ancestor supplies one (`body`:24, `.sheet`:112, `.letterhead`:118 were
each read — none declares it). So it inherits, and `03-elements/typography.css`:41's
`body { line-height: var(--leading-body) }` takes it. Measured in print media with the webfont
loaded first: **`normal` → 27.55px while the glyph line rect stays 47px** — a 47px ink extent
in a 28px box. **This is exactly the mechanism `bank` was HELD for**, on the Ctrl+P page.

It is invisible today only because **`school_name_ur` is empty in this DB**. **The moment any
school fills that field in, every printed letterhead overlaps.** This needs a DEFERRED row of
**recorded as D33** — it is a real finding whether or not `print` ships, because the CSS fact is
true today; only the "live defect" framing depends on shipping.

**The header Urdu Irfan saw is NOT Nastaliq, and that is why it was fine.** `Name / نام:`,
`Class / جماعت:`, `Date / تاریخ:` and `تمام سوالات کے جواب دیں۔` live in `.label` and
`.instructions`, mixed-script spans with **no Urdu class**; both compute to
`"IBM Plex Sans", system-ui, sans-serif`, so the Arabic run takes a **system naskh fallback with
Latin-like metrics**. Measured, same string, same size: **16px line box under its own stack
against 30px forced into Noto Nastaliq Urdu.** Bank's mechanism needs a 2.47× box to overflow a
1.45 leading; a ~1.3× face fits.

**Two things that are NOT the explanation, both checked because a wrong reason on the board
becomes the next session's premise:**

- **`!important` is not protecting the Urdu.** `99-legacy/print.css` has exactly **five**
  `!important` declarations — `:217`, `:218`, `:376`, `:377`, `:378` — and **all five are
  `display: none`**, hiding the sidebar and `.no-print`/modal chrome in print. None touches a
  font, a line-height, or anything Urdu.
- **There is no `print.js` in this project.** The render and knob-injection flow is
  `print.html`'s own inline `<script>`: `setVar`:514, `renderQuestion`:651, `renderSection`:714.
  The migration did not touch it, and that was proven by hashing, not asserted.

### F3 — the new tree's reset/elements layer opens up every line box

`line-height` `normal` → a resolved value on **465 element-instances**. `.qhead` 19 → 21.75px
(×25), `.options` 40 → 43.69px (×7), each `.question` ~2.75px taller. Base size 16 → 15px where
it is inherited — **`.qtext-en` does not move**, because it is pinned by `var(--q-font)`.

**Pagination held: 7 pages before, 7 after**, on the 25-question paper; the sheet grew
6324 → 6425px (+1.6%) without spilling. **That is one paper's margin, not a guarantee.** Nothing
measured how near any other paper sits to a page boundary, and a paper closer to one could
cross it.

### The print knobs are cascade-neutral, confirmed live

`--page-margin: 14mm`, `--q-font: 14px`, `--q-gap: 14px` read identically before and after.
`setVar()` writes them onto `documentElement.style`, an inline declaration that outranks every
layer — UI-018's reasoning, now measured rather than argued.

### One check came back clean

`03-elements/forms.css`:101's `button { font-family: inherit }` — the rule that took `index`'s
Urdu language toggle — has **no print-visible target here**. All 40 buttons sit inside
`.no-print` chrome and all but two already resolve to the body sans.

### Measurement quality, for whoever writes the STATUS.md row

2827 element × property deltas over a **property set of 58 fixed before measuring**, across 549
aligned elements, **0 paths in only one snapshot**, print-media drift **0**, Edge 151 at
1280×900, on a real 25-question paper (25 with images, 27 `<img>`, **555 elements —
independently reproducing the qadam-2 probe's 555**).

**A measurement defect was caught and fixed mid-session, and it is worth repeating as a rule:**
the first reading of the `.school-ur` box said **22px** and was wrong — text was injected and
measured in the same tick, before the `font-display: swap` webfont had arrived, so the number
described a Latin serif fallback. Awaiting `document.fonts.load()` for the real family and size
gives **47px**. It would have understated the exact thing `bank` was held on. **Never measure a
webfont's line box without awaiting the font.**

### Gates, as of the reverted state

pytest **906 passed**, ruff clean, ratchet OK, `unsanctioned_hex` flat at **429** (no hex
reached the entry file's comment — the failure this epic has hit four times).

**Do NOT run `pre-commit run --all-files`.** Its black hook **reformats** rather than checks and
takes ~96 unrelated Python files out of scope. It happened this session and had to be reverted
with `git checkout -- app tests scripts config`. The repo's black state at HEAD is
non-conformant for those files; that is pre-existing and is not this epic's to fix.

---

## Test data — what exists, measured, not assumed

**URL form:** `http://127.0.0.1:8000/static/print.html?paper_id=<UUID>`
The param is **`paper_id`**, not `id`, and IDs are **UUIDs, not numbers**. Using `?id=` renders
a blank page (0 questions, 1-page PDF) — this cost time twice.

| purpose | paper | |
|---|---|---|
| text-only, best for the F1 ink change | `0d04c750-ddaa-406a-a9bb-a154cf487c9d` | 20 Q · 2 sections · 0 images · **2 pages** |
| images + blueprint sections | `a5015cda-8269-4e96-8e87-82da9ccf091f` | 20 Q · 2 sections · 19 images · **6 pages** |
| longest, pagination test | `9ade2655-21e6-449d-943a-ae875542012e` | 25 Q · 1 section · 25 images · **7 pages** |

**`0d04c750`'s page count was corrected on 2026-08-05, and the correction is D36.** This table
said **3 pages**; at HEAD the PDF says **2**, and **migrated it says 3**. The old figure was
almost certainly measured in the *migrated* state during the first `print` session — so it was
never a typo, it was **the pagination regression appearing a session early and being filed as
test data**. The other two reproduce exactly at HEAD and do not move when migrated.

**There is no Urdu paper, and one cannot be picked — it has to be built.** Measured this
session: **all 22 papers contain zero of the bank's 24 Urdu questions** (the board's older text
says 21 papers; it is 22). Those 24 are **Pre Year 1 / Mathematics**, short-answer, all with
images, one per "Introduction of number N" topic, and their `question_en` is **empty** — they
are Urdu-only.

**`school_name_ur` and `address_ur` are both empty**, which is why `.school-ur` renders nothing.
**To see F2 in a real print preview, that field must be filled** (`index.html` → Settings →
School Name (Urdu)). That is a data change and is Irfan's call, not a session's.

---

## It did not ship — and if it is ever unheld, this is the sequence

`print` is HELD (D35). The file stays parked and the page stays at HEAD. **Whoever unholds it:**

1. **Land UI-044 first.** D36 is the blocker and it is a leading decision, not a `print` fix.
2. **Re-run the margin harness** and confirm all three papers return to HEAD's page counts
   (**2 / 6 / 7**). A leading fix that leaves `0d04c750` at 3 has not settled D36. The margin
   itself is already proven clean (D35) and does not need re-measuring.
3. Move `docs/ui/parked-print.css` → `static/css/pages/print.css` (read its header first).
4. `print.html`: second `<link>` → `/static/css/pages/print.css`. One line, −4 bytes.
5. Gates: pytest, ruff, `scripts/css_baseline.py --check`.
6. **Run the review agent and let it finish.** That is the step that stopped the first session.
7. `--check` must pass against HEAD **before** `--write` (UI-031a's rule). Expect
   `shared_css_lines` 1616 → 1722 and nothing else.
8. **Check a real print preview at the physical page edges**, not just that the pages count the
   same. `Page.printToPDF` is the right tool for measuring CSS and is not proof of a physical
   print.

---

## THE ROADMAP FROM HERE — written 2026-08-05, nothing started

Ordered by dependency, not by `PLAN.md`'s duplication count. **Read D34 before starting any
Sprint 4 task**, because the plan as written does not cover three of the five held pages.

**`print` is no longer item 1 — it is held, and Sprint 3 is closed at 3 of 9.** The list below
starts where the work actually starts.

**D34 is CLOSED (2026-08-05)** and Sprint 4 is re-scoped to seven tasks ordered by held pages
released — see `PLAN.md` §Sprint 4 for the table and the per-page blocker map, and STATUS.md for
the summary. The roadmap below now follows that order.

| # | task | rough size | blocked by |
|---|---|---|---|
| **1** | **UI-044** type + leading, incl. the Nastaliq leading decision → releases **`bank`** and **`print`**, settles **D33** | Sprint 4 | nothing |
| **2** | **UI-045** display / hero type step → releases **`landing`** | Sprint 4 | take with #1 — same two files |
| **3** | **Fix D32** — teach `css_orphans.py` to read markup, then re-run the nine-page table | ~30 min, one script | nothing |
| **4** | **UI-041** button + chip/tag/badge — needed by `taqseem` and `index`, completes neither alone | Sprint 4 | nothing |
| **5** | **UI-046** nav + shell → releases **`blueprint`**, completes **`index`** | Sprint 4 | 3 first |
| **6** | **UI-040** card + pagehead → completes **`taqseem`** | Sprint 4 | 4 |
| **7** | Re-migrate the released pages — entry files are parked and already measured | ~15 min each | the task that releases each |
| 8 | UI-042 modal/field · UI-043 tables/domain | Sprint 4 | no held page waits on either |

**Three things worth knowing before picking one:**

- **#1 is the highest-value task in the epic right now.** `bank`'s hold and `print`'s D33 are one
  problem in two places, and the `print` pagination regression comes from the same leading
  change — one task settles all three.
- **#1, #2 and #3 need no review agent**, so they are the cheapest if budget is the constraint.
  Nothing in #3 ships CSS.
- **The old ordering is gone deliberately.** It ran UI-040/041 first by duplication count, which
  would have ended Sprint 4 with `landing`, `bank`, `blueprint` and `print` all still held.

**Do #3 before #7.** `blueprint` is the page whose exposure number D32 moves — it reads nine
theme.css-only tokens from inline `style=""` with no fallback, which the current script cannot
see — so measuring it with a fixed script is cheaper than unholding it twice.

---

## The SIX HELD pages — none is a pending migration

`landing`, `taqseem`, `blueprint`, `bank`, `index`, `print`. All at HEAD, entry files parked in
`docs/ui/` (except `blueprint`, for which none was written). Full detail in STATUS.md.

| page | held on | needs |
|---|---|---|
| `landing` | hero headline shrinks, `reset.css` zeroes the gap under it | a display/hero type step — **owned by no UI-04x task yet** |
| `taqseem` | 16 borrowed `.btn`/`.card`/`.pagehead` rules; buttons fall to UA default | UI-041 button + card |
| `blueprint` | 20 orphan rules that are the whole app shell, plus 21 orphan tokens, plus 9 bare inline reads (D32) | shell/nav components |
| `bank` | Urdu line-height 38px → 21.75px on 24 questions | **the Nastaliq leading decision — same problem as F2 above** |
| `index` | Urdu toggle loses Nastaliq (`forms.css`:101); `.main` loses padding and `overflow` | UI-041 button reset + shell layout |
| `print` | **D36** — `0d04c750` gains a printed page, 2 → 3 (+6.0% sheet height) | **UI-044** — same leading decision as `bank` |

**`print` was held for one reason and stays held for another, and the swap is worth remembering.**
It was held on a reported `--space-*` margin regression; that report is **retired (D35)** — the
margin does not move at all. The run that retired it found **D36** instead, a real pagination
regression from D21/F3's line-height growth. **The hold was right; the stated reason was not.**

**Three of the six pages now converge on UI-044** — `bank` (Urdu line-height), `print` (D36, and
D33's `.school-ur`), and the leading half of what `landing` needs. That is why it is first.

**`bank`'s hold and `print`'s F2 are one problem in two places.** Whichever Sprint 4 task takes
the Nastaliq leading decision should take both, or they will diverge.

---

## Rules for this session (Irfan's, not negotiable)

1. **Stop before every step and ask for a one-word "go".** "What should I do next?" is not
   permission.
2. **Never push.** Irfan pushes from GitHub Desktop. Commit locally only, and only when asked.
3. **Measure, never assert.** The single most repeated failure on this epic is a number — or a
   causal explanation — written down instead of measured. This session added two more instances:
   a webfont line box read before the font loaded, and `!important` credited with protecting
   Urdu it does not touch.
4. Do **not** re-attempt `landing`, `taqseem`, `blueprint`, `bank` or `index`. All five are HELD
   until Sprint 4.
5. Do not start Sprint 5's inline burn-down anywhere. Note that `index.html`:443's Urdu field
   keeps its Nastaliq **only** via an inline `style=""` — one of those 224 attributes is
   accidentally load-bearing.
