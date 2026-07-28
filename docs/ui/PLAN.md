# EPIC UI-ARCH — CSS architecture rebuild + mockup adoption

**Branch:** `feat/ui-architecture` (one epic branch, one commit per task)
**Baseline tag:** `ui-baseline`
**Design target:** `static/mockup-modern.html` (Modern: indigo `#4f46e5` + teal `#0ea5a4`)
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

**No `@layer` for now.** It is Baseline-widely-available but it *hard-fails* on old browsers —
an unsupported browser discards the whole block and renders an unstyled page. The tree behaves
identically with or without it, so this is a one-line upgrade once someone reads
`chrome://version` on an actual school PC (anything ≥ 99 is fine). See DEFERRED.md.

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

### Sprint 4 — Components, by duplication count (4 tasks)
| ID | Task |
|---|---|
| UI-040 | `card` (6×) + unify `.page-head` → `.card`/`pagehead` (4×) |
| UI-041 | `button` (`.btn-primary`/`.btn-ghost` 5× → BEM `.button`) + chip / tag / badge |
| UI-042 | `modal` (4×) + `field` / form-row (4×) |
| UI-043 | tables + status-bar + domain components (sec/qrow/pin, board/col, imgcard, stat, bloom, sheet) |

### Sprint 5 — Inline `style=""` burn-down (3 tasks)
| ID | Task |
|---|---|
| UI-050 | `06-utilities` + `state.css`; top-20 patterns (178 instances) |
| UI-051 | Remaining repeated (~117); the 18 JS-interpolated → custom properties |
| UI-052 | `display:none` audit — `.is-hidden` **only** where JS never sets `.style.display` |

### Sprint 6 — Legacy elimination + mockup fidelity (5 tasks)
| ID | Task |
|---|---|
| UI-060..063 | Per page: drain `99-legacy/<page>.css` to zero, delete it, apply mockup screen fidelity |
| UI-064 | Delete `theme.css` + `app.css`; move mockups to `docs/design/`; final sweep |

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
6. Browser-verified in **incognito, hard refresh (Ctrl+Shift+R)** — clicked, not just loaded
7. `docs/ui/STATUS.md` updated **before** the commit
8. One commit, message `UI-0xx <what>`. **Commit only — never push** (Irfan pushes via GitHub Desktop)

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
