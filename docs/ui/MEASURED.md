# MEASURED — the findings that outlived `NEXT-SESSION.md`

**This file is an extract, not a new document.** `docs/ui/NEXT-SESSION.md` was deleted on
2026-08-20 (798 lines). Its name had been a lie since 2026-08-12, it misled a session on
2026-08-14, and it carried its own banner saying so. **But roughly 285 of its lines were
measurements that had not expired, and eleven places in this repo cite them as evidence** —
`PLAN.md` (×3), `ROADMAP.md`, `STATUS.md` (×3), `DEFERRED.md` (×2), `PROGRESS.md`, and
`scripts/css_margin_probe.mjs` (×2). Deleting the file outright would have turned every one of
those into a dangling reference. Those lines are below, verbatim.

**What was dropped:** everything that said what was DONE or what was NEXT. That was the half
that lied — "7 of 9 live", `UI-046` as "the next task", six HELD pages, `index` blocked,
`print` unshipped with no `pages/print.css`. All of it was overtaken.

**The rule its own banner gave, which is why this file exists:**

> If a sentence says what is DONE or what is NEXT, do not believe it.
> If it says how something WORKS or how it was MEASURED, it is still good.

**That rule still applies here.** These sections were written 2026-08-05 to 2026-08-12 and are
preserved as they were. Where one states a state — a ratchet figure, a gate count, whether a
file exists — read it as the reading taken that day, not as today's. The mechanisms, the
methods and the paper UUIDs are the point.

One lesson from the dropped half is worth carrying: **`print` was held on a described
regression rather than a measured one. The hold turned out to be right and its stated reason
turned out to be wrong** (D35 retired the reason, D36 found the real defect). Worth remembering
the next time a page is held on a description.

---

### 📐 `UI-043` CAME OFF THE CRITICAL PATH — measured 2026-08-12, and this is the evidence
The board said `blueprint` and `index` both wait on `UI-043` for its `.chip` and its `.tag`.
**They do not, and no component task can give them those rules.** Four rules are at stake:

| rule | needed by | can a component own it? | how that was established |
|---|---|---|---|
| `.tag` | `index` ×2 | **no** | **measured — 21 element × property deltas on `landing`** |
| `.row` | `index` ×1 | **no** | **measured — 2 deltas on `taqseem`**, `gap` 12px → 10px |
| `.chip` | `blueprint` ×1 | **no** | mechanism measured twice above; the two rules compared line by line. **Not probe-measurable — see below** |
| `.summary-row` + `:last-child` | `index` | yes | it exists only on `index`, so componentising it buys nothing |

**THE MECHANISM IS MEASURED, NOT REASONED.** `main.css`:42 orders the layers
`legacy, settings, generic, elements, objects, components, utilities` — legacy is lowest — so a
`layer(components)` rule should beat the legacy file painting those elements. **That reading was
then tested rather than trusted**: the three rules were written into a `layer(components)` file
at `theme.css`'s own values, `css_type_probe` was run against a same-browser control, and the
rules were reverted. `landing` moved 21 deltas and `taqseem` moved 2. The cascade reading was
right, and it is no longer only a reading.

**THE FIRST RUN GAVE A FALSE ALL-CLEAR ON `.row`, AND THE REASON IS THE USEFUL PART.** It
returned 0 deltas everywhere except `landing`, which read as "`.row` is safe". It was not — the
probe's page list did not include `taqseem`, the only live page whose legacy `.row` sets a
different `gap`. `slo` and `slo-health` returned 0 because their legacy `gap` already equals the
component value, which is agreement, not absence of a collision. **A 0 from a probe that is not
looking at the page is not a 0.** `taqseem` is now in the list — see `css_type_probe.mjs`:33.

**`.chip` CANNOT BE PROBE-MEASURED AT ALL, and that is a property of the page, not a gap in
effort.** `taqseem` has **no static `.chip`** — the class exists only inside `chipHtml()`'s
template string at `taqseem.html`:126, so the chips are absent from every snapshot until real
data renders them. An earlier count of "`.chip` ×1 on `taqseem`" was counting that template
string as markup. What can be compared is the two declarations, and they are not variants of one
component — they are two different components wearing one name:

```
99-legacy/taqseem.css:72   display:flex; flex-direction:column; gap:6px;
                           border:1px solid; border-radius:var(--radius-sm); padding:8px 9px
static/theme.css:127       display:inline-flex; align-items:center; gap:5px;
                           border-radius:999px; padding:3px 9px; font-size:11.5px
```

A standing block that holds a code, a strand, a sequence and a `<select>`, against a flat pill.
A component `.chip` would collapse the first into the second.

**`.tag` is the same failure three times over.** The brand tagline on `index` (×2, both
`data-i18n="brand.tag"`), the hero tagline on `landing` (which `brand.js`:27 queries as
`.brand .tag:not([data-i18n])`), and a JS-rendered **SLO code badge** on `slo-health`:165.

**What each page actually loses**, read against its own legacy file rather than assumed —
`index`'s `.brand .tag` and `.topbar .tag` (both 0,2,0) already win `font-size` and `color`, so
the exposure is the five properties they do not set: `font-family`, `font-weight`, `padding`,
`border-radius`, `background` — the pill shape. `.row` loses all three of `display`,
`align-items`, `gap`, because `.topbar .row` is inside `index.css`:304's `@media (max-width:
760px)` and does not apply at desktop width. `.summary-row` loses `border-bottom`, the separator
between rows.

**So the four rules are page-scoped rules, and they belong to `UI-047b` and `UI-047c`** — the
same place `taqseem`'s bare `.card` went. **`UI-043`'s remaining scope is real but nothing waits
on it**: tables are already shipped by `03-elements/tables.css` (`main.css`:110-114), and the
domain families `PLAN.md`:220 lists — sec/qrow/pin, board/col, imgcard, stat, bloom, sheet — are
duplication work for Sprint 5/6. This file's own §"parked" row said "no held page waits on
either" all along; it read as stale and it was right.

**Take `UI-047a`'s lesson into whatever is next: enumerate before writing.** That task's step 1
found a declaration missing from `btn.css` — `white-space`, twelve of thirteen ported and the
thirteenth simply absent — that four rounds of review on UI-041 had not. **The same method is
what took `UI-043` off the critical path an hour later.** Listing what a page loses when
`theme.css` goes and checking each line against the tree costs one probe run.

Read `STATUS.md` §"THE SIX HELD PAGES, MEASURED" before choosing — every per-page number is
there, measured, including **two blockers that are decisions rather than tasks**.

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

