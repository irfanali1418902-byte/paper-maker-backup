# NEXT SESSION — start here

> Written at the end of the `taqseem`/UI-031c session (2026-08-03) so the next session needs
> no copy-paste handover. **Read `docs/ui/STATUS.md` first — it is the SOURCE OF TRUTH.**
> This file only says *what to do next and what not to do*; every number lives in STATUS.md.
>
> **Updated 2026-08-05 — `index` is HELD too, and `print` is the only page left.** `bank` and
> `index` were each taken, migrated, measured in a browser and **reverted**; both entry files
> are parked. `blueprint` was held on the checks alone. **Nothing is migrated on the new tree
> beyond the original three.** Every number is in STATUS.md's NEXT TASK block and its UI-032
> rows. What remains is **one** migration: `print`.

**Branch:** `feat/ui-architecture` · **Working dir:** `C:\PaperMaker\paper-maker-mvp`

---

## THE NEXT SESSION'S TASK

**Migrate `print` — with a browser open, and stop for a "go" before each step.** Five of nine
pages are HELD and three are live; `print` is the one that is left.

### Read this before you start, because it has now happened four times

**Passing both orphan checks is necessary and NOT sufficient.** `taqseem` passed the token
check and was held on rules. `blueprint` failed both halves at once. **`bank` passed BOTH with
zero exposure and was still held** — on Urdu line-height. **`index` passed both and was held
too** — on Urdu *font-family* and on `.main` losing its padding. Do not read "0 / 0" as "safe";
read it as "nothing is *unsupplied*", which is a smaller claim than it looks.

**And do not assume the previous page's failure is the failure to look for.** `index` was
approached as "is this bank's line-height problem again?", and the answer was no — its Urdu
elements all carry a `line-height`. The property that actually broke was `font-family`, from a
different rule in the same file, and only a full before/after diff over a wide property set
surfaced it. **Read the whole diff, not the rows you expected to find.**

### The HELD pages you must not touch

**`blueprint`** (held 2026-08-04) — 20 orphan rules that are the entire application shell
(`.app` grid, `.top`, `.nav`, `.brand .logo/b/small`, `.card > .ch/.cb`, `.chip`) *plus* 21
orphan tokens, *plus* — found later, D32 — **nine more theme.css-only tokens read from inline
`style=""` with no fallback**, which the stylesheet-only check could never see. `taqseem` lost
its buttons; `blueprint` would lose the grid. Sprint 4's shell/nav work. **Nothing is parked
for it** — the decision came before any entry file was written — and `blueprint.html` is
untouched at HEAD.

**`bank`** (held 2026-08-04) — both checks clean, held on Urdu. `99-legacy/bank.css`:229
`.q-text .qt.rtl` sets Nastaliq and a size but **no `line-height`**, so
`03-elements/typography.css`:41's `body { line-height: var(--leading-body) }` in
`layer(elements)` takes it: **38px → 21.75px** on the 24 Urdu-only questions. Nothing clips
(no `overflow` anywhere on that row), so the failure mode is overlap. Its finished entry file
is parked at **`docs/ui/parked-bank.css`** — read its header before ever touching this page —
and `bank.html` is back on its three `<link>`s at HEAD.

**`index`** (held 2026-08-05) — both checks clean on their own halves (token 0, rule 3), held on
two things neither measures. **The Urdu language toggle loses Nastaliq**: `03-elements/forms.css`
:101 `button { font-family: inherit }` is in `layer(elements)` and `99-legacy/index.css`:34
`.urdu, .ur` is in `layer(legacy)`, so the bare element rule wins and `index.html`:21's اردو
button renders in the body's Latin sans — D22's button reset, landing on the control a teacher
uses to switch the app to Urdu. **And `.main` loses `overflow: auto` and its
`var(--pad) 28px 44px` padding** (`static/theme.css`:89; `index.css`:73 sets only flex
properties): the content area measured 28px left, 32px up, 56px wider on every screen. Its
finished entry file is parked at **`docs/ui/parked-index.css`** — read its header before ever
touching this page — and `index.html` is back on its three `<link>`s at HEAD.

Five pages are held in total (`landing`, `taqseem`, `blueprint`, `bank`, `index`) and **none of
them is a pending migration.**

**Two things `index` learned that outlive it**, both in STATUS.md's UI-032 row:

- **One of that page's 224 inline `style=""` attrs is load-bearing.** `index.html`:443's Urdu
  school-name field keeps Nastaliq *only* because the family is inline, which outranks every
  layer. D32's sweep was right that the inline `var()` reads are clean — that is a different
  question from whether an inline attribute is holding something up. **Sprint 5 must move that
  family into CSS before it burns the attributes down.**
- **If you reuse the contrast method from D31: it does NOT composite translucent layers.** The
  ancestor walk stops at the first background with alpha > 0. That was exact on `bank` (both
  backdrops opaque) and will be wrong anywhere a translucent surface sits between the text and
  its paint. Composite before quoting a ratio.

### `print` — the only one left, and the one to take the most care over

0 by D9 (it never linked `/static/theme.css`, so its three matching rules are already inert),
but it is the **Ctrl+P page**, the highest-consequence one in the epic. Check its output on a
real exam paper, never a blank one. Known gap: **no paper in this DB has Urdu question text**,
so the Urdu half cannot be exercised here — which is exactly why `bank` was the first page to
surface the Nastaliq problem.

**Two specific things to check on this page, because they are what held the last two:** whether
any `<button>` on it carries a font it needs (`forms.css`:101 takes those, and this page's Urdu
comes from the header and labels rather than question text), and whether anything relies on a
`static/theme.css` layout property the page's own file does not restate. Neither orphan check
reports either one.

Rules 1–5 at the bottom of this file still apply, **except** that rule 1's "migrate nothing"
was scoped to the measurement task and is now spent for `print`. It still holds for
`blueprint`, `bank`, `index`, `landing` and `taqseem`.

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
5. Do **not** re-attempt `landing`, `taqseem`, `blueprint`, `bank` or `index`. All five are
   HELD until Sprint 4.
