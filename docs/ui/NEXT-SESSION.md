# NEXT SESSION — start here

> Written at the end of the `taqseem`/UI-031c session (2026-08-03) so the next session needs
> no copy-paste handover. **Read `docs/ui/STATUS.md` first — it is the SOURCE OF TRUTH.**
> This file only says *what to do next and what not to do*; every number lives in STATUS.md.

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

## THIS SESSION — qadam 1 of UI-032 only. **MIGRATE NOTHING.**

UI-032 is the four pages still on their old `<link>`s: **`blueprint`, `bank`, `index`,
`print`** (three of nine pages are live on the new tree — `slo`, `slo-health`, `library`;
`landing` and `taqseem` are HELD).

**The task for this session is measurement, not migration.** Run **BOTH** checks over **all
four** pages in **one pass**, changing no file, so it is known up front which pages are
repetitions of `slo`/`slo-health`/`library` and which are decisions like `taqseem`.

### Check 1 — orphan TOKEN (two greps, no browser)

For each page's `static/css/99-legacy/<page>.css`:

1. collect the names it **declares** (`--name:`)
2. collect the names it **reads** (`var(--name)`)
3. **reads but never declares = the D20 exposure** — those go empty the moment
   `/static/theme.css` is unlinked, unless fallback-protected

Also diff the *declared* names against `01-settings/tokens.css` + `01-settings/theme.css`
together: a shared name means the token changes owner when the new tree arrives.

Known so far: `slo` 0 · `slo-health` 0 · `library` 0 · `taqseem` **26** · `blueprint` **17**
(per D20, none fallback-protected) · `bank`, `index`, `print` **never checked**.

### Check 2 — orphan RULE (needs the DOM; grep is NOT enough)

This is the half that held `taqseem`.

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

- **`blueprint`** — 17 orphan tokens; own file declares 10 `.btn` + 4 `.card` and is the one
  page carrying its own `.pagehead` rules, so the rule half is *probably* clean — **probably
  is not measured.**
- **`bank`** — largest legacy file (366 lines, 62 raw hex), **never checked for either.**
- **`index`** — SPA, 7 screens via `showScreen()`, 224 of the project's 466 inline `style=""`.
  **Do not start Sprint 5's inline burn-down here.**
- **`print`** — no `/static/theme.css` already (D9), only 2 `<link>`s, so small D20 exposure —
  but it is the **Ctrl+P page**, the highest-consequence one in the epic. Re-check on a real
  exam paper (Urdu, images, page breaks), never a blank page.

---

## Rules for this session (Irfan's, not negotiable)

1. **Migrate nothing. Change no file** except writing the results into `docs/ui/STATUS.md`.
2. **Stop before every step and ask for a one-word "go".** "What should I do next?" is not
   permission.
3. **Never push.** Irfan pushes from GitHub Desktop. Commit locally only, and only when asked.
4. **Measure, never assert.** The single most repeated failure on this epic is a number
   written down instead of measured — including backdrops for contrast ratios.
5. Do **not** re-attempt `landing` or `taqseem`. Both are HELD until Sprint 4.
