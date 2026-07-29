# UI-ARCH — Deferred / Parking Lot

Anything found mid-task that is **out of scope for that task** lands here instead of being
fixed inline. This file is the pressure-release valve that makes the "one task, one page,
no drive-by fixes" rule survivable.

**Rule: if you find it and it is not your task, write it here and move on.**
Do not fix it. Do not "just quickly" fix it. Adding a row here is the correct outcome.

Format: `| ID | What | Found in | Why deferred | Proposed home |`

---

## Open

| ID | What | Found in | Why deferred | Proposed home |
|---|---|---|---|---|
| D2 | 31 stale git branches (`feature/*`, `hissa-*`, `fix/*`) | audit 2026-07-28 | git hygiene, unrelated to UI | a `chore/branch-cleanup` session |
| D3 | `docs/SDLC-WORKFLOW.md` §4/§6 still describe Railway auto-deploy | audit 2026-07-28 | Railway/Northflank is dead; Irfan pushes via GitHub Desktop, no auto-deploy | doc fix, after this epic |
| D4 | `IMPLEMENTATION_HANDOFF.md`, `REDESIGN_SPEC_blueprint.md`, `ROLLOUT_all_pages.md` all specify the **Classic navy/gold** palette, superseded by Modern | audit 2026-07-28 | three stale specs will mislead a future session | archive to `docs/design/archive/` in UI-064 |
| D5 | `mockup-modern.html` + `papermaker-mockup.html` are served as live app URLs | audit 2026-07-28 | they are design references, not pages | move to `docs/design/` in UI-064 |
| D7 | `.btn.gold` renders **teal** under the Modern palette — the class name lies | audit 2026-07-28 | rename is scheduled, not a bug | UI-041 (button component) |
| D8 | `landing.html` exists but `/` still serves `index.html`; landing is unreachable in normal use | audit 2026-07-28 | routing/product decision, not styling | ask Irfan after the epic |
| D9 | `print.html` and `landing.html` never loaded `theme.css` at all | audit 2026-07-28 | resolved naturally by the migration | UI-013 / UI-018 |
| D10 | Repo root holds 11 `paper_maker*.db` backups + `app.zip` / `.claude.zip` / `config.zip` | audit 2026-07-28 | working-tree hygiene; backups should not live in the repo root | a `chore/repo-hygiene` session (ROADMAP H2 already tracks this) |
| D11 | `compare_js_classes` only catches **JS-side** renames. All 32 load-bearing class names appear in a `<script>` body, so the `class="..."` half of the search is doing no work; a class renamed **in markup only**, with stale JS left behind, passes the check. Measured, not theoretical. | UI-002 review 2026-07-28 | closing it needs per-class, per-half baseline state — a design change to `BASELINE.json`, not a tweak. The docstring states the limit honestly, and the frozen id/onclick/data-* inventory (which *is* exact) already covers the attribute half of the threat | a follow-up ratchet task, or fold into UI-050 when inline styles are burned down |
| D12 | CSS built in JS is invisible to every metric — `el.style.cssText = ...`, `sheet.insertRule(...)`, or a template literal with no literal `<style>` tag. No `<style>` element, no `style=` attribute, no `.css` file, so `shared_css_lines` does not close it either | UI-002 review 2026-07-28 | no occurrences today; detecting it reliably means parsing JS, which is well beyond a line-counting ratchet | revisit only if a page starts generating CSS at runtime |
| D13 | `static/brand/logo.svg` hardcodes `fill="#2E5AAC"` — the same Classic blue deleted from the brand config in UI-003 | UI-003 review 2026-07-28 | an SVG cannot read a CSS token or the API, so this is an asset change (recolour or `fill="currentColor"`), not a CSS one. No ratchet metric counts it: the ratchet reads `.html` and `.css` only | UI-064, alongside the other asset/palette reconciliation |
| D14 | `.pg-btn` reads `color: var(--text)`, but `--text` is defined **nowhere** — not in the block, not in `app.css`, not in `theme.css` (grep is empty). The declaration is inert; pagination buttons inherit their colour instead, which happens to look right. Now at `99-legacy/library.css:232` | UI-014 2026-07-29 | pre-existing, not caused by the extraction. Fixing it mid-Sprint-1 would be a real visual change inside a task whose entire contract is *zero* visual change — and the fix is a token decision (`--ink`? `--muted`? delete the line?), not a typo | UI-050/051 inline burn-down, or whenever `.pg-btn` becomes a real component |

---

## Resolved

| ID | What | Resolved by |
|---|---|---|
| D1 | `@layer` adoption pending a browser check | **Adopted 2026-07-28.** Floor is Edge/Chrome 99 (Mar 2022) and Edge auto-updates, so the deployment clears it by years. Reversible in one line if anything ever renders unstyled. |
| D6 | `config/brand.json` `primary`/`navy` don't match the Modern palette | **Done in UI-003** (`2eba2f8`). Deleted rather than reconciled — nothing consumed them, re-verified at implementation: `brand.js` reads only `full_name`/`tagline`, no Python indexes the keys, no test touches the endpoint. The `--navy` declarations in the pages are local CSS vars, not reads of `brand.json`. |
