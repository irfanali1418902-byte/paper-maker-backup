# ROADMAP & AUDIT FINDINGS — July 2026
**Basis:** fresh audit of repo @ commit f6bed81 (ratio merge) · 242 tests passing · prod live & verified

---

## A. Audit Snapshot — What's HEALTHY ✅

- **Tests:** 242 passing; services, repositories, and routes all covered; guard paths tested.
- **Security:** git history clean of secrets (`.env*`, `*.db`, `*.zip` ignored); auth fail-closed in prod; timing-safe key compare; Gemini key in header not URL; app key already rotated once successfully.
- **Architecture:** clean layering (api → services → repositories → core) consistently followed; env reads at module boundary.
- **Process:** last three releases followed branch → plan-first → verify → PR → deploy — keep this.
- **Docs:** README, ARCHITECTURE, PROJECT, USER_STORIES exist and are substantial.

## B. Audit Findings — What NEEDS FIXING ⚠️ (with priority)

### P0 — Hygiene & risk (do first, ~1 short session)
| # | Finding | Action |
|---|---------|--------|
| H1 | `.env.txt` (318 B) on disk — likely an old key copy. Untracked, but a leak-in-waiting. | Check contents → delete file. If it held a real Gemini key, rotate that key when aistudio access works. |
| H2 | `maker.zip` (1.4 MB) in repo root on disk | Delete (backups don't live in the working tree). |
| H3 | Loose root scripts: `import_syllabus.py`, `seed_large_class.py` | Move to `scripts/` + one-line README each. |
| H4 | Fixture CSVs in root (4 files, one named `…csv.csv`) and git-tracked | Move to `tests/fixtures/` (or `data/`), fix double extension, update any paths. |
| H5 | `master` not protected on GitHub | Enable branch protection: require PR, forbid direct push. |
| H6 | `API_VERSIONING.md` (8 KB) — over-long for current stage | Trim to one paragraph; add small `DECISIONS.md` for future ADRs. |

### P1 — Product robustness (next 1–2 sessions)
| # | Finding | Action |
|---|---------|--------|
| ~~R1~~ ⚠ | ~~Prod question bank thin on subjective types~~ | **AUZAAR BAN GAYA 2026-08-21** (`scripts/seed_bank.py`), magar **kaam adhoora hai**: sirf Math Grade 4 seed hua (11/11 topics). Syllabus ke 8 subject×grade joron mein se **5 abhi bhi bilkul khali** hain — Geography G8, Science G7, Math G5, G6, Pre Year 2, Pre Year 3. Row tab band karein jab wo bhi ho jayen. |
| ~~R2~~ ✅ | ~~Export tests don't assert content (Urdu text, marks, sections)~~ | **DONE (PR #6):** docx content assertions for EN/UR question text, options, total-marks value. Sections deferred — feature not built yet. **⚠ YEH ROW AB TAAREEKH HAI, ZINDA TESTS NAHI:** DOCX/PDF export `e2bdcc4` mein delete ho chuka aur uske saath ye assertions bhi. Aaj paper ka output browser print hai (`static/print.html`), aur sections 2026-08-20 ko ban chuke (order 1 dekhein). |
| ~~R3~~ ✅ | ~~Adaptive papers ignore paper_type/ratio — undefined interaction~~ | **DONE (PR #8):** adaptive now honors `paper_type` (mcq/mixed/subjective) via the shared `_PAPER_TYPE_FILTERS`; `custom-ratio` deliberately rejected for adaptive (422 via `_reject_ratio_for_adaptive` validator) — weakness-distribution × ratio-split combo left out of scope. Tested: type filter + custom-ratio rejection. |
| ~~R4~~ ✅ | ~~Provider fallback (Gemini→Anthropic) untested~~ | **DONE (PR #6):** locked actual behavior — selection-by-priority (no runtime fallback exists); mocked-HTTP error-wrapping + no-key-leak tests. |

### P2 — Ops decision (before Railway day ~28)
| # | Finding | Action |
|---|---------|--------|
| O1 | Railway credit expires; card not added (correct) | Pick target (Render free tier suggested) → write MIGRATION.md → dry-run: deploy from GitHub, copy volume DB, set 4 env vars, smoke test → switch. |

## C. Feature Roadmap (after P0/P1)

| Order | Feature | Why | Size |
|-------|---------|-----|------|
| ~~1~~ ✅ | ~~**Sections mode (A/B/C)** — headings + per-section marks in UI/print/Word~~ | **DONE 2026-08-20** (`e2e517a`). Teacher generate screen par apne sections banata hai (naam, qismein, ginti); `sections_meta` paper ke saath store hoti hai aur `print.html` use pehle se render karta hai. **"Word" is row ka stale hissa tha** — DOCX/PDF export `e2bdcc4` mein jaan-boojh kar delete hua ("621 lines nothing calls, and a LibreOffice dependency") aur Irfan browser se print karta hai, to daira UI + print raha. Kami par paper fail nahi hota, shortfall report hota hai. Tafseel PROGRESS.md 2026-08-20 | M–L |
| 2 | **Ratio Phase 2** — exact counts per type (3/4/3) | Finer control; builds on ratio v1 | S–M |
| ~~3~~ ✅ | ~~**Prod seeding tool** — one-click "build starter bank" per class~~ | **DONE 2026-08-21** as `scripts/seed_bank.py` (CLI, dry-run by default), NOT a UI button — "one-click" jaan-boojh kar multawi, taake pehle naapa ja sake ke sawal kaam ke aate hain. Bank 459 → 502; Math Grade 4 ab 11/11 topics. Is ne do asal bug bhi benaqab kiye, dono fix ho chuke: (a) AI maangne par bhi `essay` nahi banata tha kyunke prompt ke JSON namoone mein sirf mcq/short-answer thay; (b) `advanced` Bloom taqseem chhote papers par ULTI chalti thi. Tafseel PROGRESS.md 2026-08-21 | S |
| 4 | **Lesson Plan module** — plans linked to topics + coverage report | Your original vision; new module, do after core is polished | L |
| 5 | Per-student adaptive papers | Extends F10; still open after R3 (adaptive is whole-class only) | M |
| 6 | Syllabus PDF auto-extract | Convenience | M |
| 7 | Adaptive × custom-ratio | Deferred by R3 (currently 422-rejected); needs a weakness-distribution × ratio-split design before it's safe to allow | M |

## D. Suggested Session Plan (step-by-step)

```
Session 1  → P0 cleanup (H1–H6) — one branch chore/repo-hygiene, one PR
Session 2  → R2 + R4 tests; decide & implement R3 (adaptive×type)
Session 3  → R1 prod seeding + full prod regression checklist
Session 4  → O1 migration dry-run (MIGRATION.md) — before credit deadline
Session 5+ → Feature roadmap order 1 (Sections mode): plan-first → build   ✅ 2026-08-20
Aage      → order 2 (Ratio Phase 2). Sections ke qareeb hai: dono ginti tay
             karte hain, aur GeneratePaperRequest un dono ko ek saath lene se
             saaf inkaar karta hai (422) — us faisle ko dobara mat kholo bina
             yeh tay kiye ke teacher ko kaunsa jeetna chahiye.   ✅ 2026-08-21
             → order 3 (seeding tool)                            ✅ 2026-08-21
Aage      → baqi 5 khali syllabi seed karo (R1), phir order 4 (Lesson Plan).
             Seeding ka auzaar tayyar hai — sirf chalana hai:
             python -m scripts.seed_bank --subject X --grade Y --write
```

> **2026-08-20 ka note — is list ke daawe naapne par ghalat nikalte hain.**
> Order 1 ki row kehti thi "UI/print/**Word**" jabke Word export mahine pehle
> delete ho chuka tha, aur uska aadha kaam (`sections_meta` column, print ka
> renderer, blueprint papers) **pehle se bana hua tha**. Kaam uthane se pehle
> repo mein naap lo ke kya mojood hai — row par bharosa mat karo.

## E. Standing Reminders

- Gemini key rotation still pending (aistudio access issue) — retry occasionally.
- Any future key that appears in chat/screenshot = rotate.
- Update this file at the end of every session (it is the living plan).
