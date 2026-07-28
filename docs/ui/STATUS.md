# UI-ARCH — Status Board

> **Fresh session: read THIS file first. Do not read PROGRESS.md (2000+ lines).**
> Full plan: `docs/ui/PLAN.md` · Rules: `CLAUDE.md` §11–12 · Parking lot: `docs/ui/DEFERRED.md`

**Branch:** `feat/ui-architecture` · **Baseline tag:** `ui-baseline`
**Last updated:** 2026-07-28 (UI-001)

---

## NEXT TASK → UI-002

Build the ratchet: `scripts/css_baseline.py` + `docs/ui/BASELINE.json` +
`tests/test_css_architecture.py`. Nothing visual. This must land before any page is touched,
because it is what stops a later session from undoing the work.

---

## Progress

`99-legacy/` lines remaining is the real progress metric. **2133 → 0.**

| Sprint | Tasks | Done | State |
|---|---|---|---|
| 0 Guardrails | UI-000..002 | 2/3 | in progress |
| 1 Extraction | UI-010..018 | 0/9 | not started |
| 2 Foundation | UI-020..021 | 0/2 | not started |
| 3 Shell | UI-030..032 | 0/3 | not started |
| 4 Components | UI-040..043 | 0/4 | not started |
| 5 Inline burn-down | UI-050..052 | 0/3 | not started |
| 6 Legacy kill | UI-060..064 | 0/5 | not started |
| 7 Optional | UI-070 | 0/1 | not started |

### Task log

| ID | Task | Status | Commit | Note |
|---|---|---|---|---|
| UI-000 | Commit baseline, tag, branch | **done** | — | tree was dirty: theme.css Modern rewrite + 7 link lines |
| UI-001 | Planning docs + CLAUDE.md §11–12 | **done** | — | this document set |
| UI-002 | Ratchet test + BASELINE.json | next | — | |

---

## Live metrics — these may only go DOWN

Verified at `ui-baseline`, real app pages only (`mockup-modern.html` is a reference, not a page):

| metric | baseline | now | target |
|---|---:|---:|---:|
| `<style>` blocks in HTML | 9 | 9 | 0 |
| CSS lines in HTML | 2133 | 2133 | 0 |
| inline `style=""` attrs | 466 | 466 | ~171 (one-offs only) |
| hardcoded hex in pages | 324 | 324 | 0 |
| `99-legacy/` lines | 0 | 0 | 0 (peaks at 2133 after Sprint 1) |

**Green baseline at `ui-baseline`:** `pytest -q` = 874 passed · `ruff check .` clean.

---

## Decisions locked (do not relitigate)

| Decision | Choice | When |
|---|---|---|
| Palette | **Modern** — indigo `#4f46e5` + teal `#0ea5a4` | 2026-07-28 |
| Design target | `static/mockup-modern.html` | 2026-07-28 |
| Shell fidelity | **Full mockup shell** — `.app` grid + topbar + grouped nav | 2026-07-28 |
| Architecture | ITCSS order + BEM naming + small utility layer | ADR-001 |
| Load mechanism | one `<link>` → `main.css`, `@import` inside | ADR-001 |
| `@layer` | **not used** — hard-fails on old browsers; revisit after checking a school PC | ADR-001 |
| Dirty tree | committed as-is, tagged `ui-baseline` | 2026-07-28 |
| Branching | one epic branch, one commit per task | 2026-07-28 |
| Push | **never by Claude** — Irfan, via GitHub Desktop | standing |

---

## Blocked / needs Irfan

| # | Item | Needed for |
|---|---|---|
| B1 | Read `chrome://version` on an actual school PC (need ≥ 99) | whether `@layer` can be adopted — one-line change, not urgent |

---

## How to start a session

1. Read this file. Take **only** the task named under NEXT TASK.
2. Read `CLAUDE.md` §11–12 (rules) and the one page/file that task owns. Nothing else.
3. State a 2-line plan. Wait for go-ahead.
4. Implement. Verify per `PLAN.md` §5 Definition of Done.
5. Update this file — task log row, metrics, NEXT TASK — **then** commit. Never push.
