# UI-ARCH — the measurement probes

Eight CDP drivers in `scripts/`, plus one plain parser (`css_breakpoints.mjs`, UI-064 — it
reads CSS text, drives no browser, and is listed below because both probes now import it). They are the reason the numbers on `STATUS.md` can be
re-checked instead of trusted, and they exist as repo files because **this epic has already
lost a set of measurement scripts once** — the first `print` session wrote them into a
session scratchpad and they were gone by the next one, with only the method surviving in
prose. These are the rebuilt versions plus everything written since. Do not leave a new one
in a scratchpad.

---

## What each one is for

| script | media | answers |
|---|---|---|
| `css_type_probe.mjs` | screen, **five widths** | The **live-page regression gate**. **⚠ UNTIL 2026-08-26 IT READ ONE WIDTH, 1280x900, AND SO DID EVERY OTHER PROBE HERE — of the fifteen screen `@media` queries in `static/css/`, exactly ONE was ever observed.** UI-064 gave it the five bands `1280 / 900 / 740 / 700 / 520` (one per band, derived by `css_breakpoints.mjs`) and added the fourteen properties those rules actually set, `flex-direction` and `position` among them. Non-reference bands suffix their keys `<path>@<width>`. Computed styles for every element on `slo`, `slo-health`, `library`, `taqseem` and `bank`, plus `landing` and the Urdu line boxes. This is what proves a type change moved nothing. `taqseem` joined 2026-08-12 — see the page-list rule below for what its absence cost. |
| `css_print_probe.mjs` | **print** | Print-media computed styles **and PDF page counts** for the three live pages and `print.html` on three real papers. The gate that caught D36's shared-tree blast radius. |
| `css_margin_probe.mjs` | **print** | `print.html` only: the margin chain (`html`/`body`/`.print-main`/`.sheet`), the three print knobs, `@page` as the engine sees it, and the PDF. Written for D35. |
| `css_margin_diff.mjs` | — | Diffs two `css_margin_probe` runs and **names every element whose box moved**. Written because "12 elements changed padding" is not an answer when the question is whether the printed margin moved. |
| `css_page_rule_probe.mjs` | **print** | Walks the CSSOM **including `@import`ed sheets** to find `@page` and report which layer it arrived in. **With an optional second argument (a selector substring) it also reports every `CSSStyleRule` carrying it — the layer it arrived in, and how many elements it matches.** That is the "is this new rule inert, or is it simply not there?" check UI-041's review ran by hand; UI-041b made it a flag. |
| `css_drain_probe.mjs` | screen | **Sprint 6's tool, and it answers the opposite question to `css_orphans.py`.** That one asked what a page LOSES when `static/theme.css` is unlinked; this asks, of each rule still sitting in `99-legacy/<page>.css`, **"if I delete it, does anything move?"** Deletes each rule from the CSSOM, re-snapshots, counts deltas, puts it back — one page load, no file ever edited. **A zero is a candidate, not a verdict**: `@media` blocks outside the viewport, JS-rendered content, `:hover`/`:focus`, and properties outside ITS OWN 40 all read 0 without being dead. Its header lists all four. **⚠ Two of those four are no longer shared limits, and that changes what a zero here is worth:** `css_type_probe` now reads five width bands and 58 properties, this probe still reads 1280x900 and 40. Its header's line "One size, 1280x900, same as css_type_probe" was corrected on 2026-08-26. **If a drain candidate sits inside an `@media` block, confirm it with `css_type_probe` at the relevant band before deleting it.** |

| `css_selector_probe.mjs` | screen | **What does this selector actually compute to, page by page?** Takes a selector, a property list and a page list. **`--add=<selector>:<class>` adds a class before reading and removes it after**, which is the only way to reach state that is `display: none` at rest — `.status-bar`'s `.ok`/`.err`/`.warn` are written by inline JS and `.modal-backdrop` needs `.open`, so `css_type_probe` returns 0 for both whether the CSS is right or wrong. Written 2026-08-15/16, when it found **six** families whose rule text was byte-identical across files and whose resolved values were not. Its header lists them. |

| `css_state_probe.mjs` | screen | **What does a HOVERED, FOCUSED, ACTIVE or DISABLED element paint?** Every other probe here reads the page **at rest**, so a state declaration contributes **zero deltas whether it is right or wrong**. Forces the state through CDP `CSS.forcePseudoState` — the flag the style engine itself reads, so the cascade resolves as it would under a real pointer, with no synthetic mouse events to race the pages' JS. `:disabled` is the exception and is applied as the **attribute**, then restored. Writes `css_type_probe`'s exact JSON shape, so **`css_type_diff.mjs` compares two runs unchanged**, `--names` included. Carries **`outline-*`, which `css_type_probe` does not have at all**. **Five states, and FOCUS IS TWO OF THEM:** `focus` forces `:focus` alone (pointer focus — this is the pass that sees `forms.css`:79 and every `input:focus` rule), `focus-visible` forces **both** `:focus` and `:focus-visible`, because a real tab-stop matches both and anything else models a state no user can reach. |

`css_rules_probe.mjs` (older, UI-032) is the DOM half of `css_orphans.py --rules` and is
unrelated to these.

**Rule 10, added 2026-08-25, and it is the only rule here that was proved by a control rather
than by a bug: A GATE THAT READS THE PAGE AT REST CANNOT SEE A STATE.** `css_state_probe.mjs`
exists because two tasks in two days were bitten. UI-061 deleted four `input:focus` rules and
could only argue they were dead from layer order plus 0 deltas at rest — had the argument been
wrong, the focus ring would have vanished and **no gate would have fired**; it was confirmed by
Irfan's eye. UI-062 then re-pointed `.btn-cancel:hover` onto a grey neither page used, and
pytest, ruff, the ratchet and all 34 measured deltas passed without noticing.

**The control, run 2026-08-25 on `bank`, mutating exactly that hover declaration:**

| probe | deltas |
|---|---|
| `css_type_probe.mjs` (at rest), all nine pages | **0** |
| `css_state_probe.mjs`, `bank` alone | **1** — `button.btn-cancel::hover  background-color` |

Both numbers came from the same mutation and the same browser, and review reproduced them
independently. **Run the state probe before and after any task that touches a `:hover`,
`:focus`, `:active` or `:disabled` rule** — the rest gate will pass regardless.

**Rule 12, and it is rule 10 on a second axis: A GATE THAT READS ONE WIDTH CANNOT SEE A
BREAKPOINT.** Every probe here ran at 1280x900, so fourteen of the tree's fifteen screen
`@media` queries were measured only where they do not apply — a rule inside
`@media (max-width: 720px)` could be deleted, recoloured or inverted for zero deltas.

**And half of it was not the width at all.** The property list was blind to what those rules
set: `flex-direction` appears **22 times** inside them and was not measured, likewise
`flex-wrap`, `position` and `grid-template-columns`. Adding viewports without adding the
properties would have produced a probe that visits the band and still sees nothing.

**The control, 2026-08-26**, mutating one declaration inside `slo`'s `@media (max-width: 720px)`:

| probe | control A (`display`) | control B (`flex-direction`) |
|---|---|---|
| `css_type_probe.mjs` as committed at HEAD | **0** | **0** |
| new probe restricted to `--viewports 1280` | **0** | — |
| new probe, five bands | **12** (only `@700`, `@520`) | **72** |

**The honest split, because it corrects the obvious guess:** of control B's 72 deltas only
**2** were on newly-added properties — the other 70 were `width`/`height` consequences the old
list already carried. So the properties are not what made these visible; **the width was.**
What the properties buy is a diff that NAMES the cause (`flex-direction: column -> row`)
instead of 70 unexplained box moves — and coverage of `z-index`, which moves no box at all.

**Rule 11, and it is the same lesson one level down: FORCING THE WRONG PSEUDO-CLASS LOOKS
EXACTLY LIKE A CLEAN RESULT.** The first version of `css_state_probe.mjs` forced
`focus-visible` alone. `:focus-visible` does not match a `:focus` rule, so every
`input:focus` in the repo — including `forms.css`:79, and the four UI-061 deleted — measured
**byte-identical to rest**, in the probe built to close exactly that hole. Nothing errored;
the records were all there; they were simply all the resting values. Review caught it by
running a direct CDP experiment, not by reading the output.

**What that experiment also settled, and it corrects a comment in the tree:** on a form field
both pseudo-classes match at once during real keyboard focus, and `input:focus` (0,1,1) beats
`:focus-visible` (0,1,0) in the same layer. So a focused input paints **no outline** — it
gets the teal border and the 3px glow from `forms.css`:79. `forms.css`:76's comment says the
`:focus-visible` rule wins "being later in the file"; it does not. The visible ring on an
input is the glow, and the `outline` treatment reaches buttons, links and anything with no
`:focus` rule of its own. See DEFERRED D47.

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

All of them need the app running first:

```
.venv/Scripts/python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Then, from anywhere:

```
node scripts/css_type_probe.mjs       <label> <outdir> [--viewports 1280,700]
node scripts/css_breakpoints.mjs      [width...]        # bands, and who observes them
node scripts/css_print_probe.mjs      <label> <outdir>
node scripts/css_margin_probe.mjs     <label> <outdir> <paperId...>
node scripts/css_margin_diff.mjs      <before.json> <after.json>
node scripts/css_page_rule_probe.mjs  <url> [selector-substring]
node scripts/css_drain_probe.mjs      <page> [--json <path>]
node scripts/css_state_probe.mjs      <label> <outdir> [--page <p>] [--viewports 1280,700]
node scripts/css_selector_probe.mjs   "<selector>" "<prop,prop>" [--add=<sel>:<class>] <page...>
```

`css_state_probe.mjs` writes the same JSON shape as `css_type_probe.mjs`, so the SAME diff
tool reads both — there is no state-specific diff to learn:

```
node scripts/css_type_diff.mjs <before>.json <after>.json --names
```

Its keys are `<path>::<state>` — or `<path>@<width>::<state>` when `--viewports` names more
than one band — and the `<path>` half is byte-identical to `css_type_probe`'s, so a path from
a state diff can be pasted into a rest diff and lands on the same element. **That invariant now
depends on both probes spelling the width the same way (`@<width>`, before the `::`), which is
the thing a future editor would break without noticing.**
Full run: **nine pages, five states, ~30 s, 13,100 records** (measured 2026-08-25, **at the
default single viewport** — the figure scales with the band count).
`--page bank` for one.

**This probe deliberately stays at 1280 while `css_type_probe` moved to five, and the reason is
measured: there are ZERO `:hover` / `:focus` / `:active` / `:disabled` rules inside any `@media`
block in `static/css/`** (parsed 2026-08-26). It prints its uncovered bands every run anyway, so
the day someone writes one, the default is visibly wrong rather than quietly wrong.

> **⚠ An earlier draft of this line said "~41 s, 8,112 records" and review measured `bank`
> ALONE at 445 s.** Both numbers were real: the first version awaited every
> `forcePseudoState` in turn — 1,533 elements × states × 2 serialised round-trips — and the
> cost is latency-bound, so it varies with machine load by an order of magnitude. The calls
> are independent, so they are now issued together and awaited once. The current figure is
> the pipelined one, with MORE states and MORE elements than the number it replaces.

Each writes `<outdir>/<label>.json` and prints a summary. **Use a scratchpad for `<outdir>`** —
the JSON and PDFs are large and are not repo artefacts; only the scripts belong here.

The usual shape of a task is: measure at HEAD → make the change → measure → diff → revert.

---

## What is hardcoded, and when it will bite

- **Edge's path** — `C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe`, now in
  seven of the eight. Change it if the dev PC moves.
- **`css_state_probe.mjs`'s interactive selector list and its four states** are hardcoded at
  the top of the file. Widen the selector list when a real rule falls outside it, not on
  principle — forcing `:hover` on all 5,379 of bank's elements produces a diff dominated by
  inherited colour, which is why it is scoped to what can actually take a state.
- **`http://127.0.0.1:8000/static`** as the base URL.
- **The viewport widths, and this is the one that already bit** — see UI-064. `css_type_probe`
  now carries a five-entry `VIEWPORTS` list *derived* from the tree's breakpoints, so it is
  hardcoded but **checked**: it prints any unobserved band every run, and `css_breakpoints.mjs`
  is what derives them. **`css_drain_probe`, `css_selector_probe` and `css_print_probe` are
  still single-width and are NOT checked** — a zero from any of those still means "at 1280".
  The reference width being the *unsuffixed* one is also hardcoded: change which width is the
  reference and every bare key changes meaning. `css_type_diff.mjs` warns when two runs
  disagree on their viewport lists; it cannot warn about anything older than that field.
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

1. **Two snapshots with no action between, and compare them.** *(UI-064: in `css_type_probe` the pair is now taken PER BAND, after the resize and its settle — there is an action between bands, none within a pair. Motion is switched off for the run, so the pair is comparing settled values, not tween frames.)* A data-driven page that jitters
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
