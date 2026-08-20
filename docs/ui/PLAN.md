# EPIC UI-ARCH — CSS architecture rebuild + mockup adoption

**Branch:** `feat/ui-architecture` (one epic branch, one commit per task)
**Baseline tag:** `ui-baseline`
**Design target:** `static/mockup-modern.html` (Modern: indigo `#4f46e5` + teal `#0ea5a4`)
**⚠ ONE PART OF IT IS OVERRIDDEN — the sidebar.** Modern's default is a LIGHT sidebar
(`mockup-modern.html`:38, `--sidebar-bg:#fff`). **Irfan chose navy on 2026-08-13** and the tree
follows him: `05-components/nav.css` reads the `--color-sidebar-*` roles and
`01-settings/theme.css` documents them as the target rather than a leftover. Everything else in
the Modern palette stands. See §Sprint 6.
**Status board:** `docs/ui/STATUS.md` ← *fresh sessions read this first, not this file*

---

## 1. Why this epic exists

The app has a design system (`theme.css`, 213 lines) that ~90% of the styling bypasses.
Every page carries its own `<style>` block, so the same shell, card, button and modal are
redefined 4–9 times and drift independently. Page CSS loads *after* the shared link, so
pages silently win — `index.html` redefines `--line` and `--muted`, the same token names
`theme.css` uses.

Fixing individual pages does not fix this. The cause is the architecture, so the
architecture is what changes.

### Measured baseline (real app pages; `mockup-modern.html` excluded — it is a reference, not a page)

| page | `<style>` blocks | CSS lines | rules | inline `style=""` | hardcoded hex |
|---|---:|---:|---:|---:|---:|
| bank.html | 1 | 368 | 173 | 90 | 62 |
| blueprint.html | 1 | 279 | 113 | 65 | 1 |
| index.html | 1 | 339 | 187 | 224 | 61 |
| landing.html | 1 | 102 | 34 | 0 | 14 |
| library.html | 1 | 253 | 108 | 48 | 43 |
| print.html | 1 | 469 | 179 | 15 | 87 |
| slo-health.html | 1 | 113 | 63 | 7 | 25 |
| slo.html | 1 | 93 | 53 | 13 | 26 |
| taqseem.html | 1 | 117 | 56 | 4 | 5 |
| **TOTAL** | **9** | **2133** | **966** | **466** | **324** |

### Duplication — this is the attack order

| copies | selector |
|---:|---|
| 9× | `:root`, `.brand`, `body`, `*` |
| 8× | `.app-sidebar`, `.sidebar-foot`, `html`, `a` |
| 7× | `.app-nav`, `.app-nav a`, `.app-nav a:hover`, `.brand .name` |
| 6× | `.card`, `.brand small`, `select` |
| 5× | `.btn-ghost`, `.btn-ghost:hover`, `.app-nav a.active` |
| 4× | `.page-head` (+`h1`,`p`), `.modal`, `.modal-close`, `.field-row`, `.card-title`, `label`, `input:focus` |
| 3× | `.btn-primary`, `.status-bar`, `table`, `input[type=text]` |

Naming has already forked: `.page-head` (4 pages) vs `.pagehead` (theme.css);
`.btn-primary`/`.btn-ghost` (5 pages) vs `.btn`/`.btn.ghost` (theme.css). Both halves exist.

### Inline `style=""` profile (466 total)

- **295 (63%)** are repeated patterns → collapse into ~70 classes
- **171 (36%)** are true one-offs → leave alone
- **18** are JS-interpolated → convert to custom properties, do not delete
- **29** are `display:none` paired with JS `.style.display` toggles → **DO NOT convert to classes**, it breaks the JS

---

## 2. Architecture

ITCSS layer order + BEM component naming + a small hand-written utility layer.
Rationale and sources: `docs/adr/ADR-001-css-architecture.md`.

```
static/css/
  main.css                  ← the ONLY <link> in any page; declares import order
  01-settings/
    tokens.css              Tier 1 primitives — raw palette/scales, no meaning
    theme.css               Tier 2 semantic — roles. Components read ONLY this tier
  02-generic/
    reset.css               box-sizing, margin reset, media defaults
    fonts.css               @font-face (absorbs today's static/app.css)
  03-elements/
    typography.css  forms.css  tables.css
  04-objects/
    shell.css               THE app shell — replaces 8 duplicate copies
    grid.css  stack.css     layout only, zero cosmetics
  05-components/
    button.css  card.css  modal.css  field.css  badge.css  nav.css
    table-data.css  section-builder.css  board.css  image-card.css
  06-utilities/
    utilities.css           .u-* single-purpose
    state.css               .is-open .is-loading .has-error
  99-legacy/
    <page>.css              TEMPORARY. Append-never, delete-only.
```

**Load mechanism:** one `<link href="/static/css/main.css">` per page; `main.css` holds the
`@import` order. Single source of truth for the cascade, one line to change in 9 heads, and
no build artifact that can go stale. `99-legacy/*` is imported **first** so everything in the
new tree wins without a single `!important`.

**`@layer` is adopted** (decided 2026-07-28). It is Baseline-widely-available; the floor is
Edge/Chrome 99 — **March 2022** — and Edge auto-updates, so every machine in this deployment
clears it by years. Known risk, accepted: `@layer` *hard-fails* rather than degrading, so a
genuinely ancient browser would render an unstyled page. Mitigation is that the tree behaves
identically without it, so backing it out is one line in `main.css`. If a teacher's PC ever
renders unstyled, that is the first thing to remove.

### Tokens — three tiers

```css
/* 01-settings/tokens.css — TIER 1: raw values, no meaning */
:root { --indigo-600:#4f46e5; --teal-500:#0ea5a4; --slate-900:#0f172a; --space-3:1rem; }

/* 01-settings/theme.css — TIER 2: roles, never a raw hex */
:root { --color-action:var(--indigo-600); --color-accent:var(--teal-500);
        --color-text:var(--slate-900); --space-inset:var(--space-3); }

/* 05-components/button.css — TIER 3: component-scoped, references Tier 2 only */
.button { --button-bg:var(--color-action); background:var(--button-bg); }
.button--danger { --button-bg:var(--color-danger); }
```

**A raw hex outside `01-settings/tokens.css` fails CI.** Not a review convention — a test.

### Class naming

| prefix | meaning | rule |
|---|---|---|
| `js-*` | JavaScript hook | **never appears in a stylesheet** |
| `is-*` / `has-*` | runtime state | always chained: `.modal.is-open`, never a bare `.is-open` rule |
| `block__el--mod` | component | author-time variants only |
| `o-*` | layout object | no cosmetics, ever |
| `u-*` | utility | single-purpose, highest layer |

---

## 3. Migration strategy — strangler fig, never a big-bang rewrite

**Sprint 1 restyles nothing.** It cuts each page's `<style>` block *verbatim* into
`99-legacy/<page>.css` and links it. Zero visual change, mechanical, trivially reviewable —
and it removes all 2133 lines from the HTML immediately.

Then the new tree is built *above* legacy, and components are extracted **strictly by
duplication count** (shell 8× → card 6× → buttons 5× → modal 4×), deleting the corresponding
rules from every legacy file as each component lands. When a page's legacy file reaches zero
lines it is deleted.

**Progress is literally measurable as lines remaining in `99-legacy/`.**
Every task ends with a working app. There is no broken intermediate state.

---

## 4. Sprints and tasks

One task = one session = one commit. Task IDs are permanent; do not renumber.

### Sprint 0 — Guardrails (no page touched)
| ID | Task | Output |
|---|---|---|
| UI-000 | Commit dirty tree, tag `ui-baseline`, cut `feat/ui-architecture` | clean starting point |
| UI-001 | Planning docs: PLAN / STATUS / DEFERRED / ADR-001 + CLAUDE.md §11–12 | this document set |
| UI-002 | `scripts/css_baseline.py` + `docs/ui/BASELINE.json` + `tests/test_css_architecture.py` | **the ratchet** |
| UI-003 | Remove dead `primary`/`navy` from brand config | closes DEFERRED D6 |

**UI-003 note.** `config/brand.json` declares `primary #2E5AAC` / `navy #16294A`. Verified
2026-07-28: **nothing consumes them** — no frontend reads `brand.primary`/`brand.navy`, no test
references brand at all, and `brand.js` uses only `name`/`full_name`/`tagline`. Removing them
touches three files (`config/brand.json`, `app/services/brand_service.py` `_DEFAULTS`,
`app/schemas/responses.py` `BrandResponse`). This is the **one sanctioned backend change** in
this epic — it removes a competing colour source before tokens land in UI-020. Directed by
Irfan 2026-07-28.

### Sprint 1 — Extraction (9 tasks · **zero visual change** · verbatim cut)
| ID | Page | lines/rules |
|---|---|---|
| UI-010 | slo.html | 93 / 53 |
| UI-011 | slo-health.html | 113 / 63 |
| UI-012 | taqseem.html | 117 / 56 |
| UI-013 | landing.html | 102 / 34 |
| UI-014 | library.html | 253 / 108 |
| UI-015 | blueprint.html | 279 / 113 |
| UI-016 | bank.html | 368 / 173 |
| UI-017 | index.html | 339 / 187 |
| UI-018 | **print.html** | 469 / 179 — `@page` + 5 `@media print` + `setProperty`. **Last. Highest risk.** |

### Sprint 2 — Foundation (2 tasks · no visual change)
| ID | Task |
|---|---|
| UI-020 | `main.css` + import order + legacy demoted + `01-settings` 3-tier tokens (Modern palette) |
| UI-021 | `02-generic` reset + fonts (absorb `app.css`) + `03-elements` typography/forms/tables |

### Sprint 3 — Shell (3 tasks · **full mockup shell**: `.app` grid + topbar + grouped nav)
| ID | Task |
|---|---|
| UI-030 | Build `04-objects/shell.css` + nav config (groups: Papers / Content / Plan & track / Settings) |
| UI-031 | Migrate simple pages: slo, slo-health, taqseem, landing, library |
| UI-032 | Migrate complex: blueprint, bank, index (SPA `showScreen` handlers), print |

### Sprint 4 — Components, **ordered by held pages unblocked** (7 tasks)

**This table was re-scoped and re-ordered by D34 (resolved 2026-08-05). It used to hold four
tasks ordered by duplication count, and that ordering would have ended Sprint 4 with three of
the six held pages still held**, because no ID owned nav/shell, the Nastaliq leading decision,
or the display/hero type step. Three IDs are new (UI-044..046) and the order is now "how many
held pages does this task release", not "how many duplicates does it remove".

Sprint 3 closed at **3 of 9 pages migrated**. The other six are HELD and every one of them is
waiting on something below. **A task is not done until the pages it owns are migrated.**

> **A COMPONENT TASK CANNOT RELEASE A PAGE. A MIGRATION DOES.** This column said otherwise in
> every component row and is rewritten — 2026-08-08. A component ships new names into
> `layer(components)`; a page opens only when its markup is re-classed and its `<link>` block
> changes. The claim was measured false three times before the pattern was named: **UI-045** was
> listed as releasing `landing` and does not, **UI-046** as releasing `blueprint` and cannot, and
> **UI-040** as completing `taqseem` and cannot. Per-page counts are in `STATUS.md`
> §"THE SIX HELD PAGES, MEASURED"; the releases themselves live in the migration tasks.

| order | ID | Task | Prepares / releases |
|---:|---|---|---|
| **1a** | **UI-044a** ✅ **DONE 2026-08-05** | **Nastaliq leading** — `--line-height-nastaliq` + `05-components/urdu.css` | **PREPARED, NOT LIVE** — proof-tested on `bank`, activates when `bank` migrates |
| **1b** | **UI-044b** ✅ **done** | **print-media leading** — the half `--leading-body` cannot solve | **PREPARED, NOT LIVE** — in `print`'s parked entry file · settles **D36** |
| **2** | **UI-045** ✅ **DONE 2026-08-07** | **display / hero type step** — `--font-size-8` / `--text-display` + one rule in landing's parked entry file | **nothing alone** — `landing` also needs the icon decision (**`UI-047d`**), which no component can make |
| **3** | UI-041 ✅ **DONE 2026-08-07** — four review rounds, PASS at round 4 | `button` — `.btn--primary` / `.btn--ghost` in `05-components/btn.css`. **Not** `.button`, and **no** chip/tag/badge: `.tag` is live on `slo-health` and JS-queried as the brand tagline, `.chip` on `taqseem` is a domain block for UI-043 | **prepared component, released nothing.** Covers **6 of `taqseem`'s 17** — but **not the gold fill its two `btn gold` buttons need**. **Does not touch `index`** (measured 2026-08-06) |
| **4** | **UI-046** | **nav + shell components** — consumes `04-objects/shell.css` and `config/nav.json` | **prepares component, releases nothing.** Covers **12 of `blueprint`'s 20**; those 12 match 0 elements on all three live pages |
| **5** | UI-040 ✅ **DONE 2026-08-08** | `card` chrome + `pagehead` — 7 rules in `05-components/card.css`, **no bare `.card`** | **prepared component, released nothing.** Gave `taqseem` 7 of its 8 and `blueprint` 3 of its 20; both stay HELD |
| 6 | UI-042 | `modal` (4×) + `field` / form-row (4×) | **prepares component, releases nothing** — settles D26/D27/**D31** |
| 7 | UI-043 | status-bar + domain components (sec/qrow/pin, board/col, imgcard, stat, bloom, sheet). **Tables are already shipped** by `03-elements/tables.css` — see `main.css`:110-114 | **prepares component, releases nothing — and as of 2026-08-12, nothing waits on it either.** This row said it carries `blueprint`'s `.chip` and `index`'s `.tag`. **Measured: it cannot.** `.chip`, `.tag` and `.row` are all live on migrated pages, `layer(components)` outranks `layer(legacy)` (`main.css`:42), and unlike `.card`/`.btn` these are flat rules with no safe descendant to ship. All four go page-scoped in `UI-047b`/`UI-047c`. Evidence in `MEASURED.md` §📐 |

**UI-044a landed as FOUNDATION-FIRST, not as a page release.** The rule and its token are in
the tree and imported by `main.css`, but they reach **nothing**: the only page carrying
`.q-text .qt.rtl` elements is `bank`, which is HELD at HEAD and does not link `main.css`, while
the three pages that do link it carry zero Urdu. It was proof-tested through a temporary swap —
`bank` migrated, measured, reverted — so the value is settled and measured *before* the
migration that will need it, exactly the shape UI-021 used. **Nothing activates until `bank`
migrates.**

**UI-044b and UI-045 were the foundation and are both done. Neither released a page** — this line predicted "two more of the six" and both were measured false.
They are listed separately because they are separately reviewable, but they touch the same two
files (`03-elements/typography.css` and `01-settings/`) and should be taken back to back; doing
either one alone leaves the other's pages held.

**UI-044 (a+b) is the single highest-value task in the sprint.** `bank`'s hold and `print`'s D33 are
**one problem in two places** — Nastaliq inheriting `body { line-height: var(--leading-body) }`
from `layer(elements)` — and whoever takes one must take the other or they will diverge. D36
(`print` gaining a page) comes from the *same* leading change, so it is the third thing this
task settles.

**Why UI-041 is third and not first.** It is needed by two pages and **completes neither on its
own**: `taqseem` also needs UI-040 and UI-041b, and `index` never used `.btn` at all — its
button-shaped blocker is **D22**, which no component can unpark. UI-044a/b and UI-045
were ordered ahead of it because they were expected to complete their pages outright; **all three
are now done and none of them did.**

**Nothing here depends on `--space-*`.** An earlier plan for this sprint assumed a space-token
layer fix was the foundation; **D35 measured that mechanism and it does not exist on this
branch** — no legacy file reads `--space-*` and the printed margin does not move. Do not
schedule work for it.

**Per-page map — the six HELD pages and what releases each:**

> **READ THE "RELEASED BY" COLUMN AS "NEEDS", NOT "OPENS".** Every ID it names is a component
> task, and a component releases nothing — the migration does. Two of its cells were measured
> false in 2026-08-08's scoping and are corrected in the rows themselves; the per-page rule
> counts, the ownership split of `blueprint`'s 20 and `taqseem`'s 17, and **two blockers no task
> owns at all** (the gold button, and `landing`'s icons) are in `STATUS.md`
> §"THE SIX HELD PAGES, MEASURED". **No page below is one task away from opening.**

| page | the actual blocker | released by |
|---|---|---|
| `landing` | **two blockers, not one.** (1) hero headline shrinks and `reset.css` zeroes the gap under it — **fixed by UI-045**, prepared and not yet live. (2) `.icon` 22px → 17px on 11 icons: `99-legacy/landing.css`:26 wins today only by document order and loses to unlayered `static/app.css`:57 the moment the page is layered — **untouched by UI-045**. Both measured 2026-08-07 in a three-state swap | **UI-045 + the icon decision**, or UI-045 plus a decision to accept 17px icons — no component can reach `.icon`; the release is **`UI-047d`** |
| `bank` | Urdu line-height 38px → 21.75px on 24 questions — **fixed by UI-044a, which is prepared and not yet live** | **UI-044a** (done) + Irfan's call on **D31** → UI-042 |
| `print` | D36 — `0d04c750` goes 2 → 3 printed pages (+6.0% sheet height) | **UI-044b** (done, parked) — the release is **`UI-047f`**, and it needs a real printer check |
| ~~`taqseem`~~ ✅ | 17 borrowed `.btn`/`.card`/`.pagehead` rules; buttons fall to UA default | **RELEASED 2026-08-12 by `UI-047a`.** UI-041 + UI-040 + UI-041b covered 15 of the 17. The other two were exceptions and both are answered: the bare `.card` is page-scoped in `taqseem`'s entry file, and `white-space` was **missing from `btn.css` entirely** — found by this task's enumeration, fixed at its own address |
| `index` | Urdu toggle loses Nastaliq (`forms.css`:101); `.main` loses padding and `overflow` | **D22 only** — which no component can unpark — the release is **`UI-047c`**, and it now carries `.tag`, `.row` and `.summary-row` itself. **This row said UI-043 (`.tag`) and that was measured false on 2026-08-12**: `.tag` is live on `landing` and `slo-health` and means three different things across the three pages, so no component can own it. `MEASURED.md` §📐. This row said "UI-046 only", and before that "UI-041 + UI-046" and UI-041 measured it false on 2026-08-06: `index`'s `.gen-btn`/`.ghost-btn` controls come from `99-legacy/index.css`:115/:123 and survive migration untouched — it never used `.btn` at all. **28 elements, 14 each**, of `index.html`'s 39 `<button>`s; this row said "29 buttons", which is the class-**string** count — the 29th is `.ghost-btn` on an `<a>`. Its button-shaped blocker is the `forms.css` reset, which is **D22**, and D22 is parked precisely because no component can unpark it |
| ~~`blueprint`~~ ✅ | 20 orphan rules that are the whole app shell, plus 21 orphan tokens, plus **9 bare inline reads — now measured by the script, not by hand** (D32 resolved 2026-08-08) | **RELEASED 2026-08-13 by `UI-047b`.** UI-040 + UI-046 covered 15 of the 20; `.nav a .icon` is dead, and the `.chip` plus the three `.brand` internals are page-scoped because no component can own them. **UI-043 was struck from this row on 2026-08-12.** Two re-classes turned out to be ADDITIONS, both caught before the edit: `.brand` is kept because `brand.js`:22 queries `.brand .name`, and `.main` is kept because `99-legacy/blueprint.css`:28 sets its `max-width` |

**D32 was run before UI-046, as this line required — resolved 2026-08-08.** `css_orphans.py`
now reads inline `style=""`, and `blueprint`'s exposure is measured rather than hand-counted:
**9 bare markup reads**, reproducing D32's recorded sweep cell for cell across all nine pages.
UI-046 is no longer waiting on anything.

### Sprint 4b — THE MIGRATIONS. **This is where pages actually open.**

**Added 2026-08-08, because these were invisible.** The roadmap carried them as a single line —
*"re-migrate the released pages, ~15 min each"* — sitting at step 7, after everything. That
framing is what let five component tasks ship in a row while the board read as though pages were
being released. **A component prepares; a migration releases. One task per page, each with its
own blockers, and none of them is 15 minutes.**

IDs are a proposal — Sprint 5 already owns UI-050..052, so these take 047.

> **ORDER, REVISED 2026-08-09 — decisions first, then the three pages that need no new CSS.**
> Read from the table below, not asserted: **`landing`, `bank` and `print` need ZERO component
> work** — their components column is "none". They are held on decisions and one printer check.
> Doing them first opens **three of the six pages without writing a line of CSS**, which is the
> cheapest visible progress available. The old order ran components first and ended with five
> component tasks shipped and no page open.
>
> | phase | work | opens |
> |---|---|---|
> | **1** | the four items in `docs/ui/DECISIONS-FOR-IRFAN.md` | — |
> | **2** | `UI-047d` `landing` · `UI-047e` `bank` · `UI-047f` `print` | **3 pages** |
> | ~~**3**~~ ✅ | `UI-041b` ✅ → `UI-047a` ✅ | **`taqseem`** — done 2026-08-12, 7 of 9 pages live |
> | **4** | ~~`UI-046`~~ ✅ → ~~`UI-047b`~~ ✅ opened `blueprint` 2026-08-13. **`UI-047c` opens `index` and nothing blocks it** — the D22 attribution was wrong, see the row above. **`UI-043` is not in this phase**, struck 2026-08-12 | last 2 pages |
> | **5** | Sprint 5, then Sprint 6 | legacy deleted |

> **REVIEW GATE, REVISED 2026-08-09 — three tiers, because one rule was wrong in both directions.**
> 1. **CSS that reaches a live page → the SCRIPT gate, not a review agent.**
>    `css_type_probe.mjs`, 0 element × property deltas on `slo`/`slo-health`/`library`. Evidence:
>    UI-041 ran four review rounds; exactly one finding touched a CSS rule, and the probe returned
>    0 deltas every time. **A script catches breakage; a review catches prose.**
> 2. **Docs that make a NEW claim or a NEW number → ONE round of review. Not four.**
>    Not zero either: `156d4a0` was docs-only, shipped unreviewed, and carried **nine** false
>    claims — corrected in `e602d78`. Skipping review because "it is only docs" is how that
>    happened.
> 3. **Purely mechanical docs (an ID renamed, a number corrected, a stale line deleted) → no
>    review.**
>
> **And numbers go in tables, not paragraphs.** `docs/ui/` is **3,004** lines against **3,495**
> lines of new CSS (re-counted 2026-08-20; the old 2,655 / 1,753 pair was months stale and
> HANDOFF had it flagged). Do not grow it — this ratio was the point, and docs are no longer
> the larger half only because the CSS tree grew, not because the docs shrank.

| ID | page | components it needs | what the migration itself must do | can it start? |
|---|---|---|---|---|
| **UI-047a** ✅ | `taqseem` | none — UI-040 ✅ · UI-041 ✅ · UI-041b ✅ | **DONE 2026-08-12.** 3 buttons re-classed (`btn gold` ×2 → `.btn--accent`, `btn ghost` → `.btn--ghost`), the bare `.card` page-scoped, the 23-name compat block as parked, 2 `.brand` partials. **`.btn--*` live on real markup for the first time** — the probe reports 3/2/2/1 in `layer(components)` against UI-041b's `matches=0`. 0 deltas on all five probed live pages, drift 0, EXPOSURE 17 → 0 | **DONE — and it was opened before it shipped**, which is what the 2026-08-11 attempt was reverted for |
| **UI-047b** ✅ | `blueprint` | none — UI-040 ✅ · UI-046 ✅ | 19-name compat block (covers D32's 9 markup reads too), 3 `.brand` rules, 3 partials, **2 media-query rules**, **plus the page-scoped `.chip`** (9 props — no component can own it, see `MEASURED.md` §📐) | **DONE 2026-08-13.** 3 `<link>`s → 2, ten class attributes re-classed, two of them ADDITIONS not replacements. 0 deltas on all six probed live pages; on `blueprint` theme? **no**, EXPOSURE **20 → 0**. **It verified UI-046** — nine rules from `matches:0` to live |
| **UI-047c** ✅ | `index` | none | `.row` (3 props), `.summary-row:last-child` (`border-bottom`), **the page-scoped `.tag`** (5 props — `font-family`, `font-weight`, `padding`, `border-radius`, `background`; legacy already wins `font-size`/`color`), 4 partials incl. `.main`'s three properties | **DONE 2026-08-13 — 9 of 9 pages.** The smallest migration in the epic despite being the largest page: no compat block, no re-classing, no UI-046. 2,476 deltas, all accounted for. Irfan found the one real defect in the browser — `.app-sidebar` cannot scroll. Previously: **UNBLOCKED 2026-08-13.** The D22 attribution was wrong and `DECISIONS-FOR-IRFAN.md`:67 said so on 2026-08-04 — D22 is a technical constraint for Sprint 6, not a decision. The real blocker was `index`'s two اردو toggle buttons losing Nastaliq (`forms.css`:101 `button { font-family: inherit }` outranks `99-legacy/index.css`:34 by layer order), **answered A: page-scoped in the entry file**. Exactly 2 elements; the `.urdu` input at :444 is safe behind an inline style |
| **UI-047d** ✅ | `landing` | none — UI-045 ✅ | **DONE 2026-08-10.** Icon decision answered **A (accept 17px)**; entry file moved out of `docs/ui/`, one `<link>` swapped. 279 deltas on the page, **0 on every live page**, hero restored to HEAD exactly | **DONE — first page opened since Sprint 3** |
| **UI-047e** ✅ | `bank` | none — UI-044a ✅ | **DONE 2026-08-10.** Three `<link>`s → two. **UI-044a's Urdu fix activated on real markup for the first time — 24 questions, `normal`/38px, unchanged from HEAD**, which is what the page was held for. D31 answered **B**; `library`'s 44 labels changed with it | **DONE** |
| **UI-047f** ✅ | `print` | none — UI-044b ✅ | **DONE 2026-08-11.** Parked entry file activated, 2/6/7 confirmed twice, **plus D33's `.letterhead .school-ur` selector added to `urdu.css`** as that file's header required | **DONE — unheld by a real printer, not a probe.** D33 and D36 both Resolved |

**`UI-041b` ✅ DONE 2026-08-11 — `.btn--accent`, and D7 is now Resolved.** Prepared, not live:
`.btn--` is in zero markup, 0 element × property deltas on all five live pages. **It is not the
two-declaration port this section predicted.** White on `--teal-500` is **3.03:1** and the button
is 15px/700 — under WCAG's large-text threshold, so it needs 4.5:1, and the legacy `.btn.gold`
fails it on `taqseem` today. Irfan chose to darken the fill rather than the text, keeping white
text on both filled variants: a new `--teal-600` at **6.07:1**, beside `.btn--primary`'s 6.29:1.
The filled geometry was split out of `.btn--primary` so the two variants differ in exactly two
declarations. **`UI-047a` is now unblocked.** The original scoping follows.

`taqseem`'s two `btn gold` buttons need a fill
`btn.css` does not carry; `STATUS.md`'s UI-041 ledger row lists it among the four shapes with no
home (accent/gold, with secondary, danger and on-dark). `btn.css`'s header carries no such list —
it points at STATUS.md.
Measured: `theme.css`:120 is two declarations, `background: var(--accent); color: #fff`, and
`--accent` is the same value Tier 2's `--color-accent` already resolves to — so nothing is
invented. **Name it `--accent`, not `--gold`**: D7 records that the `gold` class renders teal and
that the name lies, and carrying the lie into the new tree would be the one avoidable part.
It is a separate task because `btn.css` is a reviewed component and earns its own review.

**Two blockers still belong to nobody**, and both are decisions rather than tasks: `landing`'s
icons (unreachable from any layer — see `STATUS.md` §"THE SIX HELD PAGES, MEASURED") and D31 on
`bank`.

### Sprint 5 — Inline `style=""` burn-down (3 tasks)
| ID | Task |
|---|---|
| UI-050 | `06-utilities` + `state.css`; top-20 patterns (178 instances) |
| UI-051 | Remaining repeated (~117); the 18 JS-interpolated → custom properties |
| UI-052 | `display:none` audit — `.is-hidden` **only** where JS never sets `.style.display` |

### Sprint 6 — Legacy elimination + mockup fidelity (5 tasks)

> **THE PER-PAGE ORDERING IN THIS TABLE IS WRONG, measured 2026-08-13.** Taking `slo` far
> enough to see its load-bearing half showed why: **~108 of the 454 load-bearing rules across
> all nine files are ONE shell** — `.app-nav` and companions 36, `.brand` and its two 30,
> `.app-sidebar` 16, `.sidebar-foot` 15, `.page-head` and its two 11. Draining page by page
> means meeting that same shell nine times. Go **by thing, not by page**. The survey table is
> in `ROADMAP.md`.
>
> **And the shell has drifted into 3–6 versions per selector**, so "extract the duplicate" is
> not one action. There is one clean group: `bank`, `library`, `slo-health` and `slo` are
> byte-identical across all nine desktop shell selectors — **36 rules**. Their `@media`
> overrides are NOT identical; those split into two groups and are D21 territory besides.
>
> **⚠ AND THERE ARE THREE NAVIES IN THIS REPO**, which the shell work has to settle:
> `#16294A` on the six pages whose legacy files carry their own `--navy`; `--slate-950`
> (`#0e1729`) behind `--color-sidebar-bg`, which `blueprint` and `taqseem` read; and `#132244`
> in `mockup-modern.html`:28's non-Modern theme. Nobody has chosen between them.
| ID | Task |
|---|---|
| UI-060..063 | Per page: drain `99-legacy/<page>.css` to zero, delete it, apply mockup screen fidelity **EXCEPT the sidebar, which stays navy — Irfan 2026-08-13**. **STARTED**: `slo.css` 45 rules → 35 (`legacy_css_lines` 2,115 → 2,105, the first movement in that number), all nine files surveyed, and `nav.css` recoloured so blueprint is navy again. **~2,105 lines across nine files remain — this is the epic's work** |
| UI-064 | ~~Delete `theme.css`~~ ✅ **part 1 DONE 2026-08-13** — 212 lines, 0 deltas on all nine pages, `unsanctioned_hex` 429 → 400. Remaining: delete `app.css` (57 lines, still linked by all nine for `@font-face` + the `.icon` sprite); move mockups to `docs/design/`; final sweep |

### Sprint 7 — Optional
| ID | Task |
|---|---|
| UI-070 | `js/shell.js` — dedupe the sidebar **markup** (8 copies), active state from `body[data-page]` |

---

## 5. Definition of Done — per task

A task is done when **all** are true. "It should work" does not count.

1. `pytest -q` green — **run from the project root**, not from `C:\Users\MCS`
2. `ruff check .` and `black --check .` clean
3. `node --check` passes on the page's inline JS (extract `<script>` to a temp `.js`)
4. **Ratchet passes**: `python scripts/css_baseline.py --check` — no metric increased
5. **Frozen inventory diff is empty** (§6)
6. **Independent review agent returns PASS** (see `CLAUDE.md` §12 "Task lifecycle"). A task is
   never handed to Irfan on a FAIL, and never handed over without review at all.
7. Irfan browser-verifies in **incognito, hard refresh (Ctrl+Shift+R)** — against a specific
   click-list the task provides, not a vague "please check"
8. Only after Irfan says OK: `docs/ui/STATUS.md` updated, **then** commit
9. One commit, message `UI-0xx <what>`. **Commit only — never push** (Irfan pushes via GitHub Desktop)
10. A copy-pasteable prompt for the next task's fresh session is emitted

For Sprint 1 tasks additionally: **the rendered page must be visually identical.** It is a
verbatim cut. Any visual difference means the cut was not verbatim — revert and redo.

---

## 6. Frozen inventory — changing any of these is a process violation

Never rename, in any task, unless the task explicitly declares it:

- every `id=`, `onclick=`, `name=`, `data-*` attribute
- the JS-load-bearing classes (JS queries or toggles these — a rename breaks them silently):

```
bank.html        .bp-type-check .q-checkbox .smart-details-arrow .topic-img-thumb
                 drag-over open sel urdu-mode visible
blueprint.html   .pin-sec-sel .sec-card show
index.html       .js-paper-preview .js-status .qtype .screen an-cards lang-ur
library.html     .card-check .lib-card open selected visible
print.html       .opt-en .opt-ur .qhead .suggest-badge open
taqseem.html     .col .col-head .cov-badge show
```

Verify before and after every task; the diff must be empty:
```
grep -oE 'id="[^"]+"|onclick="[^"]+"|data-[a-z-]+="[^"]+"' static/<page>.html | sort > /tmp/before.txt
# ... make the change ...
grep -oE 'id="[^"]+"|onclick="[^"]+"|data-[a-z-]+="[^"]+"' static/<page>.html | sort > /tmp/after.txt
diff /tmp/before.txt /tmp/after.txt   # must be empty
```

Also frozen for this whole epic: **no new routes, no new DB columns, no service/repository
changes.** This is a frontend epic. Backend findings go to `DEFERRED.md`.

---

## 7. Known traps

| Trap | Why it bites |
|---|---|
| `display:none` inline (29×) | Paired with JS `el.style.display='block'`. Converting to a class breaks the toggle. |
| `print.html` `@page` | Margins must come from `.sheet` padding — `@page` does not accept CSS variables. Existing lesson. |
| `print.html` `setProperty` | Live print-settings sliders write custom properties. Preserve exactly. |
| `index.html` is an SPA | 7 screens via `showScreen()`; sidebar has `onclick`, not just `href`. |
| Page `<style>` wins today | It loads after the shared link. Removing it can *reveal* previously-masked shared rules. |
| `.btn.gold` renders teal | Legacy name under the Modern palette. Rename in UI-041; do not "fix" the colour. |
| pytest from wrong cwd | The PowerShell tool resets cwd to `C:\Users\MCS`. Always `Set-Location` first. |

---

## 8. Roles

Per `docs/SDLC-WORKFLOW.md` §4, unchanged. Irfan is product owner and decides scope and
priority; Claude Code implements one task per session, plan-first; verification is shared
(automated suite + Irfan's browser check). **Push is always Irfan, via GitHub Desktop.**
