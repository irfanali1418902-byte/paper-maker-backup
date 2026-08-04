# NEXT SESSION — start here

> Written at the end of the `taqseem`/UI-031c session (2026-08-03) so the next session needs
> no copy-paste handover. **Read `docs/ui/STATUS.md` first — it is the SOURCE OF TRUTH.**
> This file only says *what to do next and what not to do*; every number lives in STATUS.md.
>
> **Updated 2026-08-04 — qadam 1 (TOKEN) and qadam 2 (RULE) are BOTH DONE, and `blueprint` is
> HELD on Irfan's call.** Both checks are scripts now and both have been run on all four pages.
> **UI-032's measurement is finished; nothing was migrated.** Every number is in STATUS.md's
> NEXT TASK block. What remains is three migrations: `bank`, `index`, `print`.

**Branch:** `feat/ui-architecture` · **Working dir:** `C:\PaperMaker\paper-maker-mvp`

---

## THE NEXT SESSION'S TASK

**Measurement is over and `blueprint`'s decision has been taken. Migrate `bank`, `index`,
`print` — one at a time, with a browser open, and stop for a "go" before each.**

**`blueprint` is HELD** (Irfan's call, 2026-08-04) — **do not migrate it, do not re-measure
it.** It measured 20 orphan rules that are the entire application shell (`.app` grid, `.top`,
`.nav`, `.brand .logo/b/small`, `.card > .ch/.cb`, `.chip`) *plus* 21 orphan tokens, the first
page exposed on both halves at once. `taqseem` lost its buttons; `blueprint` would lose the
grid that puts the page together. The rule half is Sprint 4's shell/nav work and the token half
is already covered by `docs/ui/parked-taqseem.css`'s block, so it is a scheduling hold, not an
unsolved problem. **The decision was taken before any entry file was written, so nothing is
parked for it and `blueprint.html` is untouched at HEAD.** Three pages are now held —
`landing`, `taqseem`, `blueprint` — and none of them is a pending migration.

**The three that are clear:** rule exposure **0 / 3 / 0**, token exposure **0 / 0 / 0**.
`index`'s three are `.tag` (×2), `.row`, `.summary-row:last-child`, each with a named near-miss
in `index.css`. `print` is 0 by D9 (it never linked the file) but it is still the Ctrl+P page —
check its output on a real exam paper. **Read the `partial` column in STATUS.md before each
one**: a page that redeclares a *selector* may not redeclare the *properties* (the white-slab
`.brand`, `index`'s `.summary-row` border), and the before/after diff is what settles those.
Copy `pages/slo.css` and read its header first.

Rules 1–5 at the bottom of this file still apply, **except** that rule 1's "migrate nothing"
was scoped to the measurement task and is now spent for `bank`/`index`/`print`. It still holds
for `blueprint`, `landing` and `taqseem`.

---

## What happened in the sessions before this one

**2026-08-04 (qadam 1 + 2):** both orphan checks were turned into `scripts/css_orphans.py` and
run over every page. No CSS, HTML or `<link>` was touched. Commits `64484d9` and `8adcf17`.

**2026-08-03 (UI-031c):**
`taqseem` was taken as UI-031c, fully measured, and then **HELD on Irfan's call** — it is not a
failure and not a pending migration. Its finished entry file is parked at
`docs/ui/parked-taqseem.css` (read its header before ever touching that page). Everything is
committed. `taqseem.html` is untouched at HEAD; `BASELINE.json` was not re-pinned, because
nothing shipped.

The reason it was held is the whole point of the next task: **it passed the token check and
still could not ship**, because it borrows 16 whole *rules* (`.btn*`, `.card*`, `.pagehead*`,
two `input`/`:focus`) from `static/theme.css` that its own legacy file redeclares nowhere.
Dropping the link removed its buttons and card chrome. No grep over custom properties can see
that.

---

## UI-032 — the four pages still on their old `<link>`s · **MEASURED, NOTHING MIGRATED**

**`blueprint`, `bank`, `index`, `print`** (three of nine pages are live on the new tree —
`slo`, `slo-health`, `library`; `landing` and `taqseem` are HELD).

**The measurement task is complete.** Both checks ran over all four pages, changing no file, so
it is now known which pages are repetitions of `slo`/`slo-health`/`library` (`bank`, `index`,
`print`) and which is a decision like `taqseem` (`blueprint`). The two sections below are the
record of how, and stay here so the checks can be re-run rather than re-invented.

### Check 1 — orphan TOKEN · **DONE 2026-08-04, and it is a script now**

```
python scripts/css_orphans.py --names
```

`scripts/css_orphans.py` does what this file previously described as "two greps": per page
it collects the names `99-legacy/<page>.css` declares (`--name:`) and reads (`var(--name)`),
and reports the difference. **Re-run it rather than trusting the table below** — that is why
it was written as a script and not prose (the epic's most repeated failure is a number
asserted instead of measured).

```
page        theme?  decl  reads  orphan  supplied  covered  compat  dead  fallbk  collide
bank           yes    19     19       0         0        0       0     0       0        0
blueprint      yes    18     37      21        21        2      19     0       0        0
index          yes    27     21       0         0        0       0     0       0        0
landing         no    12     10       0         0        0       0     0       0        0
library         no    19     20       1         0        0       0     1       0        0
print           no    12     13       1         0        0       0     1       0        0
slo             no    17     15       0         0        0       0     0       0        0
slo-health      no    17     15       0         0        0       0     0       0        0
taqseem        yes    15     29      26        26        3      23     0       0        0
```

`supplied` is the real D20 exposure: read here, not declared here, declared in
`/static/theme.css`, **and that file actually linked by this page**. `compat` is how many
tokens the entry file's compatibility block needs; `covered` is the ones Tier 2 already
declares. `collide` (a name declared both here and by the new tree) is **0 on all nine**.

**Validated against three already-measured pages before any new number was believed:**
`taqseem` 26 / 3 / **23** — matching UI-031c's hand measurement and the block actually
written in `docs/ui/parked-taqseem.css`; `slo-health` declares 17, reads 15, orphans 0;
`library`'s single orphan is `--text`, declared nowhere in the project (D14), which is why
the board correctly calls that page 0.

**Four findings:**

1. **`blueprint` is 21, not 17.** D20's 17 was an estimate never re-measured — the same
   shape as `taqseem`'s "20", which measured 26. All 21 names are declared zero times in
   `blueprint.css`, verified separately by grep.
2. **`bank` and `index` have zero token exposure.** `bank` is the largest legacy file (366
   lines) and had never been checked either way; it declares its own 19. `index` declares
   27, reads 21.
3. **`print` is zero, for two independent reasons.** Its one orphan `--accent` is read with
   a fallback at all four sites (`var(--accent, #0e4d3c)`), *and* `print.html` never linked
   `/static/theme.css` at all (D9) — so it already resolves to the fallback today and a
   migration cannot change it. Only four pages link that file: `bank`, `blueprint`, `index`,
   `taqseem`.
4. **`blueprint`'s 19 are an exact subset of `taqseem`'s 23** — the difference is `--shadow`
   and the three `--sidebar-*`. So `docs/ui/parked-taqseem.css`'s compatibility block
   already covers `blueprint`; it does not need a new one authored.

`app.css` declares **0** custom properties, so `/static/theme.css` is the only supplier in
play. `python scripts/css_baseline.py --check` → ratchet OK, nothing moved.

### Check 2 — orphan RULE · **DONE 2026-08-04, and it is a `--rules` mode now**

```
uvicorn app.main:app                                        # 127.0.0.1:8000, first
python scripts/css_orphans.py --rules blueprint bank index print --paper-id <id> --names
```

It does what this file described by hand: parses `static/theme.css`, runs every selector
through `querySelectorAll` against the **live** page in headless Edge, and subtracts what the
page's own `99-legacy/<page>.css` redeclares. It drives the browser through
`scripts/css_rules_probe.mjs`. 118 rule blocks probed (`:root` excluded — that is the token
half's). **Re-run it rather than trusting any number written down.**

**The four verdicts — full table, per-page detail and the `partial` column are in STATUS.md's
NEXT TASK block:**

| page | rules match / redecl / partial / **orphan** | **EXPOSURE** | verdict |
|---|---:|---:|---|
| `blueprint` | 29 / 6 / 3 / **20** | **20** | **DECISION** |
| `bank` | 6 / 3 / 2 / **1** | **0** | repetition |
| `index` | 11 / 2 / 4 / **5** | **3** | repetition |
| `print` | 5 / 0 / 2 / **3** | **0** by D9 | safe by construction |

**The method was validated against `taqseem` before any new page was believed** — 21/17 where
UI-031c measured 20/16 by hand, the whole difference being `:focus-visible`, a state-only rule
a `querySelectorAll` method can only report as universal. It is its own column and is never a
page's finding. Drift was 0 on all four across two probes, and a fresh-launch second run
reproduced every count.

Two things this check taught, both worth keeping:

- **Selector equality is not property equality**, and that error reports a page *clean*. The
  `partial` column is the fix — it is what caught the white-slab `.brand` on all four pages,
  independently, and `index.css`:144's `.summary-row` missing its `border-bottom`.
- **`input[type=text]` vs `input[type="text"]`** — theme.css writes attribute values unquoted,
  the legacy files quote them. Un-normalised, one rule reads as two: `blueprint` 21 → 20 and
  `bank` 2 → 1.

**D29 — quote FULL PATHS, never the basename.** Two different files are called `theme.css`:
`/static/theme.css` (the old stylesheet being removed) and
`/static/css/01-settings/theme.css` (the Tier 2 palette, which must load). The bare word
already cost one false alarm.

### What was produced · **DONE**

The table of all four pages with both checks side by side, a verdict each, and what did **not**
render, is **in the NEXT TASK block of `docs/ui/STATUS.md`** — that is where this board keeps
every measurement and where a reviewer can check it. Committed as `8adcf17` (qadam 2), on top
of `64484d9` (qadam 1). Nothing was migrated and no page's `<link>` was touched.

### What is already known about each page (detail in STATUS.md)

- **`blueprint`** — **21** orphan tokens, 19 needing a compat block (STATUS.md and D20 both
  said 17; that was an estimate, now measured). **This entry used to predict the rule half was
  *probably* clean, because its own file declares 10 `.btn` + 4 `.card` and it is the one page
  carrying its own `.pagehead` rules. That prediction was wrong** — measured, it is 20 orphan
  rules and they are the whole shell. `blueprint.css` declares no `.app`, `.nav`, `.top`,
  `.ch`, `.cb` or `.chip` rule at all (grep, not inference). Corrected here rather than left,
  per the rule UI-021 wrote about stale predictions. Its 19 tokens are still an exact subset of
  `taqseem`'s 23, so `docs/ui/parked-taqseem.css`'s compat block already covers them.
- **`bank`** — largest legacy file (366 lines, 62 raw hex), 5378 elements live, and **both
  halves measured clean**: 0 token exposure (declares its own 19) and 0 rule exposure (only 6
  of 118 rules reach it; the single orphan is `:focus-visible`, which `03-elements/forms.css`
  declares). A repetition of `slo-health`/`library`.
- **`index`** — SPA, 7 screens via `showScreen()`, 224 of the project's 466 inline `style=""`.
  Token half **0**, rule exposure **3**. **All seven screens were measured**, not the default
  one — the DOM grows 508 → 771 across them. **Do not start Sprint 5's inline burn-down here.**
- **`print`** — no `/static/theme.css` already (D9), only 2 `<link>`s, and **both halves 0** —
  its three matching rules are already inert because the file is not linked, so a migration
  cannot change them. Measured on a **real 25-question paper** (25 with images, 27 `<img>`,
  555 elements), never a blank page — but it is still the **Ctrl+P page**, the
  highest-consequence one in the epic. **One gap: no paper in this DB has Urdu question text**,
  so the Urdu half was not exercised; Urdu here can only come from the header and labels.

---

## Rules for this session (Irfan's, not negotiable)

1. **Migrate nothing. Change no file** except writing the results into `docs/ui/STATUS.md`.
2. **Stop before every step and ask for a one-word "go".** "What should I do next?" is not
   permission.
3. **Never push.** Irfan pushes from GitHub Desktop. Commit locally only, and only when asked.
4. **Measure, never assert.** The single most repeated failure on this epic is a number
   written down instead of measured — including backdrops for contrast ratios.
5. Do **not** re-attempt `landing` or `taqseem`. Both are HELD until Sprint 4.
