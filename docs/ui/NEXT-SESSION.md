# NEXT SESSION — start here

> Written at the end of the `taqseem`/UI-031c session (2026-08-03) so the next session needs
> no copy-paste handover. **Read `docs/ui/STATUS.md` first — it is the SOURCE OF TRUTH.**
> This file only says *what to do next and what not to do*; every number lives in STATUS.md.
>
> **Updated 2026-08-04 — qadam 1 (the TOKEN half) is DONE.** Its results are below and the
> check is now a script. What remains of UI-032's measurement is the RULE half.

**Branch:** `feat/ui-architecture` · **Working dir:** `C:\PaperMaker\paper-maker-mvp`

---

## What happened last session

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

## UI-032 — the four pages still on their old `<link>`s. **MIGRATE NOTHING.**

**`blueprint`, `bank`, `index`, `print`** (three of nine pages are live on the new tree —
`slo`, `slo-health`, `library`; `landing` and `taqseem` are HELD).

**The task is measurement, not migration.** Both checks over all four pages, changing no
file, so it is known up front which pages are repetitions of `slo`/`slo-health`/`library`
and which are decisions like `taqseem`.

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

### Check 2 — orphan RULE · **STILL TO DO. This is the half that decides UI-032.**

**A clean token result is half a page's answer, not a page's answer** — `taqseem` passed
check 1 and still could not ship. Do not read the three zeros above as three safe pages
until this check has run on them.

Worth adding to `css_orphans.py` as a `--rules` mode rather than doing it by hand, so the
result is re-runnable like check 1.

1. parse `static/theme.css` (the **old** stylesheet, full path — see the D29 warning below)
2. run **every** selector through `querySelectorAll` against the **live** page
3. subtract the selectors the page's own `99-legacy/<page>.css` redeclares
4. **what is left disappears the moment the `<link>` goes**

Cheap sanity signal before the browser work — own-file `.btn`/`.card` rule counts:
`slo` 5/3 · `slo-health` 2/3 · `library` 13/3 · `blueprint` 10/4 · **`taqseem` 0/0**.

Serve the app for this: `uvicorn app.main:app` on `127.0.0.1:8000`.

**D29 — quote FULL PATHS, never the basename.** Two different files are called `theme.css`:
`/static/theme.css` (the old stylesheet being removed) and
`/static/css/01-settings/theme.css` (the Tier 2 palette, which must load). The bare word
already cost one false alarm.

### What to produce

**A table of all four pages, both checks side by side**, and the verdict per page:
*repetition* (safe, same shape as `slo-health`/`library`) or *decision* (needs Irfan, like
`taqseem`). Say explicitly which parts of a page did **not** render and so were not measured.

**Results go into the NEXT TASK block of `docs/ui/STATUS.md`** — that is where this board
keeps every other measurement, and where a reviewer can check it.

### What is already known about each page (detail in STATUS.md)

- **`blueprint`** — **21** orphan tokens, 19 needing a compat block (STATUS.md and D20 both
  say 17; that was an estimate, now measured). Its own file declares 10 `.btn` + 4 `.card`
  and it is the one page carrying its own `.pagehead` rules, so the rule half is *probably*
  clean — **probably is not measured.**
- **`bank`** — largest legacy file (366 lines, 62 raw hex). Token half now checked: **0
  exposure**, it declares its own 19. Rule half **never checked**.
- **`index`** — SPA, 7 screens via `showScreen()`, 224 of the project's 466 inline `style=""`.
  Token half **0**. The rule check must reach all seven screens, not just the default one —
  `querySelectorAll` only sees what is in the DOM. **Do not start Sprint 5's inline burn-down
  here.**
- **`print`** — no `/static/theme.css` already (D9), only 2 `<link>`s, and token exposure
  measured at **0** — but it is the **Ctrl+P page**, the highest-consequence one in the epic.
  Re-check on a real exam paper (Urdu, images, page breaks), never a blank page.

---

## Rules for this session (Irfan's, not negotiable)

1. **Migrate nothing. Change no file** except writing the results into `docs/ui/STATUS.md`.
2. **Stop before every step and ask for a one-word "go".** "What should I do next?" is not
   permission.
3. **Never push.** Irfan pushes from GitHub Desktop. Commit locally only, and only when asked.
4. **Measure, never assert.** The single most repeated failure on this epic is a number
   written down instead of measured — including backdrops for contrast ratios.
5. Do **not** re-attempt `landing` or `taqseem`. Both are HELD until Sprint 4.
