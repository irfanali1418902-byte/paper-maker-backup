# NEXT SESSION — start here

> **Updated 2026-08-07, after UI-041 closed at round 4 and UI-045 shipped.** Read `docs/ui/STATUS.md` first — it is
> the SOURCE OF TRUTH and it is current. This file is the orientation layer: what is done,
> what is next, and the traps. **The probes that produced every number are now repo files —
> see `docs/ui/PROBES.md`.**

**Branch:** `feat/ui-architecture` · **Working dir:** `C:\PaperMaker\paper-maker-mvp`

---

## ▶ START HERE — **UI-046.** UI-041 and UI-045 are both DONE, and neither released a page.

**UI-041's re-review PASSED at round 4 on 2026-08-07 and the task is closed.** It took four
rounds — FAIL, FAIL, FAIL, PASS-with-notes — and the reason is the useful part of this entry.

| | |
|---|---|
| what was reviewed | `a420ee0` + `8b9b055` + the closing commit — **eight files**, not the "seven" this block used to say |
| how many findings touched a CSS rule | **one, in round 1** — the `:focus-visible` ring, removed because its premise was false |
| what rounds 2, 3 and 4 found | **prose, citations and counts.** Nothing else |
| proof the CSS never moved | strip the comments and `btn.css`'s declarations are **byte-identical across all three states** — 882 chars at `a420ee0`, at `8b9b055`, and after the round-3 remediation |
| effect on live pages | **zero, throughout.** `.btn--` matches nothing on `slo`, `slo-health` or `library`; re-measured after every edit at 0 element × property deltas over 44 properties |

**The lesson, because it will repeat on UI-040.** Round 3's blocking finding was *created by
round 2's fix*: a summary line saying UI-041 was "done" while the same board said DoD #6 was
unmet. Blocking findings fell 3 → 1 → 1 while notes rose 0 → 3 → 7. Each remediation added
prose, and prose that makes precise numeric claims is surface for the next reviewer to land on.
**The button was fine after round 1. The 165 lines written about it were not.** On the next
component, shrink the prose rather than defend it.

**UI-040 and the `taqseem` migration are now unblocked** — `btn.css` is a reviewed foundation.

---

## UI-045 — **DONE 2026-08-07.** Built, swap-proven, reverted. It released nothing

**Both findings below were written before the build and both survived it.** (a) is what shipped;
(b) is the reason `landing` is still HELD.

### (a) UI-045 = one Tier 1 step, one Tier 2 role, and ONE RULE in `parked-landing.css`

**Decided by Irfan 2026-08-07.** Do **not** create `05-components/hero.css`. **Shipped exactly
as scoped**, and proven by migrating `landing`, measuring, and reverting:

| | `font-size` | `line-height` | `margin-bottom` | `h1` height | `.icon` |
|---|---|---|---|---|---|
| HEAD | 30px | 36px | 12px | 72px | 11 at **22px** |
| migrated, no rule | 24px | 26.4px | 0px | 52.78px | 11 at **17px** |
| migrated + rule | **30px** | **36px** | **12px** | **72px** | 11 at **17px** |

The rule's isolated effect is **8 element × property deltas**. The live-page gate ran at
**314,996 comparisons, 0 deltas, drift 0**.

```
01-settings/tokens.css    --font-size-8: 30px          measured from 99-legacy/landing.css:48
01-settings/theme.css     --text-display: var(--font-size-8)
docs/ui/parked-landing.css
  @layer components { .hero h1 { font-size: …; line-height: 1.2; margin-bottom: 12px } }
```

**PREPARED, NOT LIVE — the UI-044b shape**, and for the same reason: the rule lives in a page
entry file that is not under `static/`, so it cannot reach a live page. It activates in the
commit that migrates `landing`.

**Why the rule cannot go in `03-elements/typography.css`:** that file takes element selectors
only, by its own contract, and the hero is `.hero h1` — a class.

**Why it needs three declarations, not one.** The token alone does not restore the page. Read,
not assumed:

| | HEAD (`99-legacy/landing.css`:48) | migrated, no rule | why it moves |
|---|---|---|---|
| `font-size` | 30px | 24px (`--text-heading-1`) | `layer(elements)` beats `layer(legacy)`; layer order is decided before specificity, so `.hero h1` loses to bare `h1` |
| `line-height` | 1.2 | **1.1** (`--leading-heading` → `--line-height-tight`) | same mechanism. **This one is easy to miss** — the board only ever recorded the size |
| `margin-bottom` | 12px | 0 | `02-generic/reset.css`:79-91 zeroes `h1` margins in `layer(generic)`, also above legacy |

**`line-height: 1.2` and `margin-bottom: 12px` stay literal, deliberately** —
`03-elements/typography.css`:68-72 already states the rule: a scale is tokenised because it
repeats across files; a single heading's optical nudge on a single page is not a scale. Only the
size is a scale step, which is what "display type step" names.

**Reach, measured:** `.hero` appears in **zero** markup on `slo`, `slo-health` and `library` —
only `landing.html`:13-14. **But `01-settings/` DOES reach all three live pages**, so the two new
token names must still be measured inert rather than assumed inert. Nothing reads them yet, which
is the reason to expect zero and not the proof of it.

### (b) **`landing` needs TWO tasks, not one. `PLAN.md`:246 and `STATUS.md`:391 are wrong.**

Both say **UI-045 releases `landing`**. It does not. UI-045 fixes the hero. **The second blocker
is untouched by it:**

`docs/ui/parked-landing.css`:41-60 — `99-legacy/landing.css`:26 declares `.icon { width: 22px;
height: 22px }`, the only page in the project that overrides the sprite size. **Today it wins
purely by document order**: it and `static/app.css`:57 (17px) are both unlayered `<link>`s and
landing's is second. The moment landing's file moves into `layer(legacy)`, `app.css` — still
unlayered, still linked, because it owns `.icon` until the nav component — outranks it. **Measured
before and after at the time: 11 icons at 22px → 11 at 17px.** Not predicted, measured.

**That belongs to `UI-046` (nav + shell / icon), or to an explicit "keep 17px" decision from
Irfan.** The parked file says the same thing and calls it his call. So:

> **`landing` is released by UI-045 + UI-046, or by UI-045 plus a decision to accept 17px icons.**

**This is D34's pattern repeating** — a held page whose second blocker no task ID owns, hidden
behind a board line that names only the first. D34 was raised, resolved, and the same shape
survived inside one of its own rows. **`PLAN.md`:246 and `STATUS.md`:391 are corrected in the
UI-045 commit**, as this block said they must be.

**And it was confirmed by measurement, not left as a reading**: the icons are 17px in the
migrated state **with** UI-045's rule applied, exactly as they are without it.

---

## THEN — **UI-046** (nav + shell / icon). It releases `blueprint`, completes `index`, and is `landing`'s second half.

**The ordering rule this sprint was re-scoped around is *which task completes a page by
itself*, and UI-045 has just failed that test in practice** — it was listed here as releasing
`landing` and it does not.

| candidate | completes, on its own |
|---|---|
| ~~UI-045~~ — hero / display type. **DONE 2026-08-07** | **nothing.** This row said "`landing` — one small task, one page released". Measured false: the hero is restored exactly, and the 11 icons still go 22px → 17px, so `landing` needs UI-046 too |
| ~~UI-041~~ — button. **DONE 2026-08-07, re-review PASSED at round 4** | **nothing**, as predicted. And the `index` half of this row was measured false: `index` never used `.btn` — its buttons are `.gen-btn`/`.ghost-btn` from its own legacy file, so **UI-046 alone releases it** |
| UI-041 **+** UI-040 | `taqseem` only — and UI-041's half is now done |

**`UI-043` is not button/card.** Button is **UI-041**, card is **UI-040**. UI-043 is tables +
status-bar + domain components, it is order 7, and it releases **no held page**. The "button/card
opens 4 pages" count does not hold: the widest single lever is UI-041, and it completes nothing
alone.

**`urdu.css` has nothing to do with button/card, and this is the trap worth knowing.**
`taqseem` carries **zero** Urdu — no `Nastaliq`, `urdu` or `.rtl` match anywhere in its legacy
file — so `05-components/urdu.css` can never affect it. **`bank` is the only page that
activates that file**, and `bank` does not need button or card: its technical blocker (the Urdu
line-height) is already solved by UI-044a. It is HELD purely on Irfan's call pending **D31**,
whose home is UI-042. **So the shortest path to seeing `urdu.css` live is `bank`'s migration —
a decision, not a task.**


Sprint 3 closed at **3 of 9** migrated. Six pages are HELD. **UI-044a and UI-044b are both
done and NEITHER SHIPPED A VISIBLE CHANGE** — read the next section before assuming any page
was fixed.

| done | what | where it lives | live? |
|---|---|---|---|
| **UI-044a** | Nastaliq leading — `.q-text .qt.rtl { line-height: var(--leading-nastaliq) }` | `05-components/urdu.css` (in `static/`) | **no** — only `bank` has those elements and it is HELD at HEAD, so it never loads the file |
| **UI-044b** | print leading — `@media print { body { line-height: normal } }` | `docs/ui/parked-print.css` | **no** — not under `static/` at all |

**Both are PREPARED, NOT LIVE, and that is deliberate** (foundation-first, the shape UI-021
used). Each was proof-tested through a temporary swap — migrate the page, measure, revert —
so the values are settled before the migration that needs them. **Neither is a page release.**

## ✅ `print` — HELD, and the reason changed once already

It was held on a reported `--space-*` margin regression. **That report is retired: D35** — the
swap was performed, AFTER measured, the tree reverted, and the printed margin does not move at
all (`.sheet` is 52.9134px = 14mm on all four sides both ways, zero box deltas on the margin
chain). `.count-grid` exists nowhere in the repo and no legacy file reads `--space-*`.
**Do not schedule any Sprint 4 work for space tokens.**

**The same run found the real regression, D36** — `0d04c750` goes 2 → 3 printed pages — and
**UI-044b has now solved it**, in `docs/ui/parked-print.css`, proof-tested at 2 / 6 / 7. D36
stays OPEN because the fix is not live; **move it to Resolved in the commit that migrates
`print`, not before.**

**The hold was right and its stated reason was wrong.** That is the lesson worth carrying:
hold a page on a measurement, not on a description.

**State:** the tree is at HEAD. `static/css/pages/print.css` does not exist, the entry file is
parked at `docs/ui/parked-print.css`, `shared_css_lines` is **1685** and `BASELINE.json` is
pinned there. Every swap-and-revert this epic has done left nothing behind — `git status`
clean, ratchet flat.

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
edges before `print` is unheld. UI-044b has already restored the page counts to **2 / 6 / 7**
in the parked entry file; re-run `scripts/css_print_probe.mjs` when the migration lands to
confirm it still holds.

**Why margins were the decisive question at all:** a printed exam paper's margins are what make
it usable — hole-punch edge, binding, the guarantee that nothing is cut off. `print.css`:1-2
records that the margin is **single-sourced** (`@page` at 0, all of it from `.sheet`'s
`padding: var(--page-margin)`) and that it was **once double** — `@page` 14mm plus `.sheet`
14mm = 28mm — so this page has been broken this way before. It is now measured and it holds.

*(A block here used to list "what was NOT verified" — the unnamed 48 padding deltas, whether
the reset reached `.sheet`, whether `@page` survives the layer import, and how to run the test.
All of it is done and the answers are above. Removed rather than left, because it contradicted
the paragraph 20 lines above it.)*

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

**The decision has been made: `print` does not ship until D36's fix is actually live** — it is
written and proof-tested in `docs/ui/parked-print.css`, and it activates with the migration.
Start at **UI-045** or **UI-041**; D34 is closed and Sprint 4's order is in `PLAN.md`.

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

1. **The D36 fix is already in the parked entry file** (UI-044b) and needs no new decision.
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

## THE PROBES ARE NOW REPO FILES — `docs/ui/PROBES.md`

Every number on this board was produced by one of five CDP drivers, and they now live in
`scripts/` instead of a session scratchpad. **This epic lost a set of measurement scripts
exactly that way once** — the first `print` session wrote them to a scratchpad and the next
session had only the prose method. Read `docs/ui/PROBES.md` before measuring anything; it
lists what each probe answers, what is hardcoded in it (Edge's path, the base URL, three
database-specific paper UUIDs), and the eight rules they encode — each of which exists
because getting it wrong once put a wrong number on this board.

**When a page migrates, add it to the page list in `css_type_probe.mjs` and
`css_print_probe.mjs`.** Otherwise the regression gate silently stops covering it.

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
| ~~1~~ | ~~**UI-044a/b** type + leading~~ — **DONE 2026-08-05/06**, both prepared-not-live | — | — |
| ~~2~~ | ~~**UI-045** display / hero type step~~ — **DONE 2026-08-07**, prepared-not-live. **Released nothing**: it restores the hero exactly and leaves `landing`'s 11 icons at 17px | — | — |
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
| `print` | **D36** — `0d04c750` gains a printed page, 2 → 3 (+6.0% sheet height) | **fix written (UI-044b), not live** — activates on migration |

**`print` was held for one reason and stays held for another, and the swap is worth remembering.**
It was held on a reported `--space-*` margin regression; that report is **retired (D35)** — the
margin does not move at all. The run that retired it found **D36** instead, a real pagination
regression from D21/F3's line-height growth. **The hold was right; the stated reason was not.**

**UI-044a/b, UI-041 and UI-045 are all done and NONE of them released a page.** `bank`'s Urdu
leading and `print`'s D36 are solved in files those pages do not load; UI-041 completes no page
alone; and **UI-045 was predicted to release `landing` and does not** — the hero is restored
exactly, the 11 icons still fall 22px → 17px. **The next task that actually releases a page is
`UI-046`** (`blueprint`, and `index`, and `landing`'s remaining half).

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
