# UI-ARCH — the measurement probes

Seven CDP drivers in `scripts/`. They are the reason the numbers on `STATUS.md` can be
re-checked instead of trusted, and they exist as repo files because **this epic has already
lost a set of measurement scripts once** — the first `print` session wrote them into a
session scratchpad and they were gone by the next one, with only the method surviving in
prose. These are the rebuilt versions plus everything written since. Do not leave a new one
in a scratchpad.

---

## What each one is for

| script | media | answers |
|---|---|---|
| `css_type_probe.mjs` | screen | The **live-page regression gate**. Computed styles for every element on `slo`, `slo-health`, `library`, `taqseem` and `bank`, plus `landing` and the Urdu line boxes. This is what proves a type change moved nothing. `taqseem` joined 2026-08-12 — see the page-list rule below for what its absence cost. |
| `css_print_probe.mjs` | **print** | Print-media computed styles **and PDF page counts** for the three live pages and `print.html` on three real papers. The gate that caught D36's shared-tree blast radius. |
| `css_margin_probe.mjs` | **print** | `print.html` only: the margin chain (`html`/`body`/`.print-main`/`.sheet`), the three print knobs, `@page` as the engine sees it, and the PDF. Written for D35. |
| `css_margin_diff.mjs` | — | Diffs two `css_margin_probe` runs and **names every element whose box moved**. Written because "12 elements changed padding" is not an answer when the question is whether the printed margin moved. |
| `css_page_rule_probe.mjs` | **print** | Walks the CSSOM **including `@import`ed sheets** to find `@page` and report which layer it arrived in. **With an optional second argument (a selector substring) it also reports every `CSSStyleRule` carrying it — the layer it arrived in, and how many elements it matches.** That is the "is this new rule inert, or is it simply not there?" check UI-041's review ran by hand; UI-041b made it a flag. |
| `css_drain_probe.mjs` | screen | **Sprint 6's tool, and it answers the opposite question to `css_orphans.py`.** That one asked what a page LOSES when `static/theme.css` is unlinked; this asks, of each rule still sitting in `99-legacy/<page>.css`, **"if I delete it, does anything move?"** Deletes each rule from the CSSOM, re-snapshots, counts deltas, puts it back — one page load, no file ever edited. **A zero is a candidate, not a verdict**: `@media` blocks outside the viewport, JS-rendered content, `:hover`/`:focus`, and properties outside the 44 all read 0 without being dead. Its header lists all four. |

| `css_selector_probe.mjs` | screen | **What does this selector actually compute to, page by page?** Takes a selector, a property list and a page list. **`--add=<selector>:<class>` adds a class before reading and removes it after**, which is the only way to reach state that is `display: none` at rest — `.status-bar`'s `.ok`/`.err`/`.warn` are written by inline JS and `.modal-backdrop` needs `.open`, so `css_type_probe` returns 0 for both whether the CSS is right or wrong. Written 2026-08-15/16, when it found **six** families whose rule text was byte-identical across files and whose resolved values were not. Its header lists them. |

`css_rules_probe.mjs` (older, UI-032) is the DOM half of `css_orphans.py --rules` and is
unrelated to these.

**Rule 9, added 2026-08-16 and it earned its place twice in one sitting: identical rule text is
not identical output, and a dead declaration is not a safe one.** The migrated entry files
remap some legacy token names onto the new tree's roles and leave others on the legacy
literals, so the same rule paints differently depending on the page — and a declaration that
loses to `layer(elements)` from inside `layer(legacy)` comes back to life the moment it is
copied into `layer(components)`, because layer order is decided before specificity. Measure the
computed value on each page before extracting a rule, and measure again after. `.filter-bar`'s
resurrection cost 75 deltas before it was caught.

**`css_orphans.py`'s main job is over.** It measured pages against `static/theme.css`, and that
file was deleted on 2026-08-13. It still runs — it degrades with a warning rather than crashing
— but every column now reads zero, correctly, because no page can be exposed to a file that
does not exist.

---

## Running them

All six need the app running first:

```
.venv/Scripts/python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Then, from anywhere:

```
node scripts/css_type_probe.mjs       <label> <outdir>
node scripts/css_print_probe.mjs      <label> <outdir>
node scripts/css_margin_probe.mjs     <label> <outdir> <paperId...>
node scripts/css_margin_diff.mjs      <before.json> <after.json>
node scripts/css_page_rule_probe.mjs  <url> [selector-substring]
node scripts/css_drain_probe.mjs      <page> [--json <path>]
```

Each writes `<outdir>/<label>.json` and prints a summary. **Use a scratchpad for `<outdir>`** —
the JSON and PDFs are large and are not repo artefacts; only the scripts belong here.

The usual shape of a task is: measure at HEAD → make the change → measure → diff → revert.

---

## What is hardcoded, and when it will bite

- **Edge's path** — `C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe` in five of
  the six. Change it if the dev PC moves.
- **`http://127.0.0.1:8000/static`** as the base URL.
- **Three paper UUIDs** in `css_print_probe.mjs`, and they are **database-specific**:

  | paper | at HEAD |
  |---|---|
  | `0d04c750-…` 20Q, 0 images | **2 pages** — the one that crosses a boundary (D36) |
  | `a5015cda-…` 20Q, 19 images | 6 pages |
  | `9ade2655-…` 25Q, 25 images | 7 pages |

  **On a different database these IDs do not exist and the probe renders a blank page.** The
  parameter is `paper_id` and the IDs are UUIDs — `?id=` silently renders nothing, which cost
  this epic time twice.

- **The page list** in `css_type_probe.mjs` and `css_print_probe.mjs` is the live pages plus the
  subject. **Add a page to that list when it migrates** — otherwise the gate silently stops
  covering it.

  **This rule was broken once, on 2026-08-12.** `UI-047a` migrated `taqseem` and did not add it,
  and the omission was invisible for exactly as long as nothing asked a question about that page.
  When one did — was `.row` safe to ship as a component? — the probe returned **0 deltas and the
  0 was believed**, because a page returning nothing and a page not being measured look identical
  in the output. Adding `taqseem` turned that 0 into 2 deltas and reversed the answer.
  **A page missing from this list does not fail loudly; it agrees with you.** That is why the rule
  is here rather than in a task's checklist.

---

## The rules these encode — do not remove them from a rewrite

Each of these exists because getting it wrong produced a wrong number on this board at least
once:

1. **Two snapshots with no action between, and compare them.** A data-driven page that jitters
   run-to-run reads as a CSS delta otherwise. Every probe reports `drift`; a non-zero drift
   means no delta below it can be believed.
2. **Await `document.fonts.ready` before believing any webfont line box.** `.school-ur` was
   first measured at 22px because it was read in the same tick the text was injected, before
   the `font-display: swap` font arrived. The real number was 47px.
3. **Fix the property set before measuring**, in the file, not in the analysis. Two counts of
   the same migration once disagreed because the set was chosen afterwards.
4. **Measure print in print media.** Screen media does not apply `99-legacy/print.css`:215 or
   :375, so a screen measurement describes a page nobody prints.
5. **Count PDF pages by producing the PDF**, never by dividing a document height by 1123.
6. **Recurse into `CSSImportRule.styleSheet`**, not just `rule.cssRules`. A walker that misses
   this reports `@page` as absent on a migrated page — which happened, and was caught before it
   became a finding.
7. **Give Edge its own `--user-data-dir` and kill it by the pid you spawned.** A review agent
   once ran `Get-Process msedge | Stop-Process -Force` and would have taken Irfan's own browser
   with it.
8. **`Page.printToPDF` is not proof of a physical print.** It is the right tool for measuring
   CSS. Before anything ships on `print.html`, a real print preview is still required.
