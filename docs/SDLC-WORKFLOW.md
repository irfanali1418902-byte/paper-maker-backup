# SDLC WORKFLOW — Software-House Process (Solo + Claude Code Edition)
**Project:** AII Smart Paper Maker · **Date:** July 2026

This is the standing process for ALL future work. It encodes what already worked well (auth, question-types, ratio releases) as the official rulebook.

---

## 1. Idea → Release Pipeline

```
1. IDEA        → write 3–5 lines in ROADMAP.md (what/why/who benefits)
2. REQUIREMENT → add/update entry in PRD (feature table) — one paragraph is enough
3. DESIGN      → ask Claude Code for a PLAN FIRST (files to touch, risks, options)
                 ✋ human go-ahead required before any code
4. BUILD       → feature branch: feat/<name>   (never on master)
5. VERIFY      → pytest green + ruff/black clean + live curl + browser click-test
6. RELEASE     → push → PR → merge (--no-ff) → branch cleanup → auto-deploy
7. CONFIRM     → prod smoke checklist (TEST-PLAN §3) + update docs
```

**One logical change per commit. One feature per branch. Master always deployable.**

## 2. Branch & Git Rules

- `master` = production. Direct pushes forbidden (enable GitHub branch protection — pending task R3).
- Branch names: `feat/…`, `fix/…`, `chore/…`, `docs/…`.
- Merge style: clean `--no-ff` merge after tests pass post-merge too.
- After merge: delete branch local + remote, prune.

## 3. Definition of Done (DoD)

A feature is DONE only when ALL are true:
1. Tests: new logic has unit tests; routes have route tests; full suite green.
2. Lint: ruff + black clean (pre-commit hooks pass).
3. Guards: empty/invalid inputs return friendly, typed messages — no crashes.
4. i18n: every new UI string in EN + Urdu, RTL verified.
5. Live verified: curl (API) + browser (UI) on the real running app.
6. Docs: PRD feature table + README (if user-facing) + this package updated.
7. Deployed & prod-smoke-checked.

## 4. Roles (adapted for solo + AI)

| Software-house role | Here |
|---------------------|------|
| Product owner | Irfan — decides WHAT and priority |
| Tech lead / reviewer | Claude (chat) — reviews plans, risks, order |
| Developer | Claude Code — implements on branch, plan-first |
| QA | Shared: automated suite + Irfan's browser checklist |
| DevOps | ~~Railway auto-deploy; env vars in dashboard only~~ **Koi deploy nahi — O1 band, 2026-08-31.** App local chalti hai; Irfan GitHub Desktop se `backup` remote par push karta hai. Env vars local `.env` mein |

## 5. Security Rules (standing)

- Secrets ONLY in env vars / `.env` (gitignored). Never in chat, screenshots, commits, URLs, or logs.
- Key rotation procedure: generate → update host env → redeploy → verify → revoke old.
- Any key that appears in a chat/screenshot is considered LEAKED → rotate.
- CORS: explicit origins only. Auth: fail-closed in prod (key set), open only in local dev.

## 6. Environment & Release Map

| Env | Where | DB | Auth |
|-----|-------|----|------|
| Local dev | localhost:8000 | local paper_maker.db | off (no key set) |
| ~~Production~~ | ~~Railway (→ future: Render)~~ | ~~volume DB (separate!)~~ | ~~on (key set)~~ |

⛔ **2026-08-31 — "Production" row band. Koi prod environment hai hi nahi**, aur ye
row us ke hone ka farz karati thi (`docs/ROADMAP.md` ki pehli chetawni ne 2026-08-25 ko
yehi naapa tha). Aaj **ek hi environment hai: local**, aur ek `backup` git remote — jo
hosting nahi, backup hai. Cloud plan band hai (O1) aur `docs/MIGRATION.md` par ⛔ banner
laga hai. Aage ki simt **school PC / Docker package** hai; jab wo aaye to yahan uski apni
row banegi — Railway/Render ki nahi.

~~Rule: **never assume local data exists in prod.** Seed prod deliberately.~~
**Ab is ka ulta laazim hai: ek hi DB hai, `paper_maker.db`, aur wohi teacher ka asal
data hai.** Seeding se pehle backup lo — `paper_maker_backup_before_*.db` ka namoona
repo root mein mojood hai.

## 7. Session Discipline (Claude Code)

- Start: `git status` → read CLAUDE.local.md → state ONE clear goal.
- Big new task after a finished one: `/clear` (fresh context), keep CLAUDE.local.md updated as the memory.
- End: commit, update CLAUDE.local.md "Pending" list, run tests.

## 8. Documentation Set (this package)

| Doc | Update when |
|-----|-------------|
| BRD | business goal/constraint changes (rare) |
| PRD | any feature added/changed (every release) |
| SRS | API/schema/env contract changes |
| TEST-PLAN | new gap found or closed |
| ROADMAP | continuously — the living to-do |
| SDLC-WORKFLOW (this) | process changes only |

Location: keep all in repo under `docs/` so they version with the code.
