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

---

## Resolved

| ID | What | Resolved by |
|---|---|---|
| D1 | `@layer` adoption pending a browser check | **Adopted 2026-07-28.** Floor is Edge/Chrome 99 (Mar 2022) and Edge auto-updates, so the deployment clears it by years. Reversible in one line if anything ever renders unstyled. |
| D6 | `config/brand.json` `primary`/`navy` don't match the Modern palette | **Promoted to UI-003.** Verified nothing consumes them, so they are deleted rather than reconciled. |
