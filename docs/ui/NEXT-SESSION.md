# NEXT SESSION — start here

> **Updated 2026-08-05, end of the `print` session.** Read `docs/ui/STATUS.md` first — it is
> the SOURCE OF TRUTH for every committed number. **This file is the exception right now:**
> the `print` work below is **measured but UNCOMMITTED**, so STATUS.md does not yet contain
> any of it. If this file and STATUS.md disagree about `print`, this file is newer.

**Branch:** `feat/ui-architecture` · **Working dir:** `C:\PaperMaker\paper-maker-mvp`

---

## ⚠ READ THIS FIRST — the tree is clean, and that is deliberate

`print` was migrated, measured, and **Irfan checked it in a real Ctrl+P print preview on two
real papers and said it was correct and should ship.** It was then **reverted anyway**, and
nothing was committed. That is not a failure and `print` is **not HELD** — it is the one page
in this epic that passed everything and simply ran out of session.

**Why it was not committed:** the independent review agent (§12 step 5) was spawned and **died
part-way through on an API monthly spend limit**. §12 says self-verification is not enough, and
this would have been a *shipping* change, so it was stopped rather than committed unreviewed.

**State right now:**

| | |
|---|---|
| `static/print.html` | **at HEAD** — its two original `<link>`s |
| `static/css/pages/print.css` | **removed** — parked at `docs/ui/parked-print.css` |
| `docs/ui/STATUS.md`, `DEFERRED.md`, `BASELINE.json` | **at HEAD** — all reverted |
| ratchet | `shared_css_lines` back at **1616**, `unsanctioned_hex` **429**, OK |
| this file | **the only modification in the tree, and it is uncommitted** |

**So the first thing to decide next session is not technical: does `print` ship?** Everything
needed to answer it is below. If yes, the work is ~15 minutes (restore the parked file, swap
one line, re-run gates, run the review agent, write STATUS.md, re-pin BASELINE).

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

### F1 — the printed page's ink colour changes on every element

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
| text-only, best for the F1 ink change | `0d04c750-ddaa-406a-a9bb-a154cf487c9d` | 20 Q · 2 sections · 0 images · **3 pages** |
| images + blueprint sections | `a5015cda-8269-4e96-8e87-82da9ccf091f` | 20 Q · 2 sections · 19 images · **6 pages** |
| longest, pagination test | `9ade2655-21e6-449d-943a-ae875542012e` | 25 Q · 1 section · 25 images · **7 pages** |

**There is no Urdu paper, and one cannot be picked — it has to be built.** Measured this
session: **all 22 papers contain zero of the bank's 24 Urdu questions** (the board's older text
says 21 papers; it is 22). Those 24 are **Pre Year 1 / Mathematics**, short-answer, all with
images, one per "Introduction of number N" topic, and their `question_en` is **empty** — they
are Urdu-only.

**`school_name_ur` and `address_ur` are both empty**, which is why `.school-ur` renders nothing.
**To see F2 in a real print preview, that field must be filled** (`index.html` → Settings →
School Name (Urdu)). That is a data change and is Irfan's call, not a session's.

---

## If `print` ships next session

1. Move `docs/ui/parked-print.css` → `static/css/pages/print.css` (read its header first).
2. `print.html`: second `<link>` → `/static/css/pages/print.css`. One line, −4 bytes.
3. Gates: pytest, ruff, `scripts/css_baseline.py --check`.
4. **Run the review agent and let it finish.** That is the step that stopped this session.
5. STATUS.md: close UI-032, `print` live, four of nine pages migrated, Sprint 3 complete, and
   the five HELD pages become Sprint 4's input. Add the `.school-ur` DEFERRED row.
6. `--check` must pass against HEAD **before** `--write` (UI-031a's rule). Expect
   `shared_css_lines` 1616 → 1722 and nothing else.

## If it does not ship

Leave the file parked and say why on the board. Nothing is broken either way — the page is at
HEAD and the ratchet is at baseline.

---

## ⚠ This file is uncommitted

Everything above exists **only in the working tree**. Nothing was committed this session,
because nothing shipped. **If this handoff should survive, it needs a docs-only commit** —
otherwise a `git checkout` or a fresh clone loses it, and the `print` measurements would have
to be redone from scratch. The measurement scripts themselves lived in a session scratchpad and
are already gone; the method is described above precisely enough to rebuild them.

---

## THE ROADMAP FROM HERE — written 2026-08-05, nothing started

Ordered by dependency, not by `PLAN.md`'s duplication count. **Read D34 before starting any
Sprint 4 task**, because the plan as written does not cover three of the five held pages.

| # | task | rough size | blocked by |
|---|---|---|---|
| **1** | **Finish `print`** — restore the parked entry file, one-line swap, gates, **review agent**, STATUS.md, re-pin. **Closes Sprint 3.** | ~15 min | the review agent needs API budget — this is what stopped the last session |
| **2** | **Close Sprint 4's scope gap (D34)** — give IDs to nav components, the Nastaliq/leading decision, and the display/hero type step, and settle the order | ~20 min, docs only | nothing |
| **3** | **Fix D32** — teach `css_orphans.py` to read markup, then re-run the nine-page table | ~30 min, one script | nothing |
| **4** | **UI-041** button + chip/tag/badge | Sprint 4 | 2 |
| **5** | **UI-040** card + pagehead | Sprint 4 | 2 |
| **6** | Re-migrate **`taqseem`** and **`index`** — entry files are parked and already measured | ~15 min each | 4, 5 |
| **7** | **nav components** (needs an ID — D34) → unblocks **`blueprint`** | Sprint 4 | 2, and 3 first |
| **8** | **type + leading** (needs an ID — D34) → unblocks **`landing`** and **`bank`**, and settles **D33** | Sprint 4 | 2 |

**Two things worth knowing before picking one:**

- **#1 is the only item blocked on anything outside the repo.** #2 and #3 need no review agent and
  are independent of whether `print` ships, so they are the cheapest things to do if budget is the
  constraint.
- **#4 is placed before #5 deliberately, against `PLAN.md`'s order.** Buttons open three pages
  (`taqseem`, `index`, part of `blueprint`); cards open two. If only one Sprint 4 task gets done,
  it should be the button one.

**Do #3 before #7.** `blueprint` is the page whose exposure number D32 moves — it reads nine
theme.css-only tokens from inline `style=""` with no fallback, which the current script cannot
see — so measuring it with a fixed script is cheaper than unholding it twice.

---

## The five HELD pages — unchanged, and none is a pending migration

`landing`, `taqseem`, `blueprint`, `bank`, `index`. All at HEAD, entry files parked in
`docs/ui/` (except `blueprint`, for which none was written). Full detail in STATUS.md.

| page | held on | needs |
|---|---|---|
| `landing` | hero headline shrinks, `reset.css` zeroes the gap under it | a display/hero type step — **owned by no UI-04x task yet** |
| `taqseem` | 16 borrowed `.btn`/`.card`/`.pagehead` rules; buttons fall to UA default | UI-041 button + card |
| `blueprint` | 20 orphan rules that are the whole app shell, plus 21 orphan tokens, plus 9 bare inline reads (D32) | shell/nav components |
| `bank` | Urdu line-height 38px → 21.75px on 24 questions | **the Nastaliq leading decision — same problem as F2 above** |
| `index` | Urdu toggle loses Nastaliq (`forms.css`:101); `.main` loses padding and `overflow` | UI-041 button reset + shell layout |

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
