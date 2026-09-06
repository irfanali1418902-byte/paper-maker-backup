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
| `css_drain_probe.mjs` | screen | **Sprint 6's tool, and it answers the opposite question to `css_orphans.py`** (deleted 2026-09-02, D59). That one asked what a page LOSES when `static/theme.css` is unlinked; this asks, of each rule still sitting in `99-legacy/<page>.css`, **"if I delete it, does anything move?"** Deletes each rule from the CSSOM, re-snapshots, counts deltas, puts it back — one page load, no file ever edited. **A zero is a candidate, not a verdict**: `@media` blocks outside the viewport, JS-rendered content, `:hover`/`:focus`, and properties outside ITS OWN 40 all read 0 without being dead. Its header lists all four. **⚠ Two of those four are no longer shared limits, and that changes what a zero here is worth:** `css_type_probe` now reads five width bands and 58 properties, this probe still reads 1280x900 and 40. Its header's line "One size, 1280x900, same as css_type_probe" was corrected on 2026-08-26. **If a drain candidate sits inside an `@media` block, confirm it with `css_type_probe` at the relevant band before deleting it.** |

| `css_selector_probe.mjs` | screen | **What does this selector actually compute to, page by page?** Takes a selector, a property list and a page list. **`--add=<selector>:<class>` adds a class before reading and removes it after**, which is the only way to reach state that is `display: none` at rest — `.status-bar`'s `.ok`/`.err`/`.warn` are written by inline JS and `.modal-backdrop` needs `.open`, so `css_type_probe` returns 0 for both whether the CSS is right or wrong. Written 2026-08-15/16, when it found **six** families whose rule text was byte-identical across files and whose resolved values were not. Its header lists them. |
| `css_contrast_probe.mjs` | screen | **Which text fails WCAG AA, on the background that is actually PAINTED?** Walks every element with its own text, reads `color`/`font-size`/`font-weight`, walks ancestors collecting backgrounds until an opaque one, composites them back-to-front with the accumulated `opacity`, and computes the WCAG 2.1 ratio against the right threshold (3.0 for large text, 4.5 otherwise). **It never reads a token file**, and that is the whole point: D26's first draft failed review for measuring both colours in the browser and then computing against an ASSUMED backdrop, and D41 records the mirror image — `.pagehead p` against white is 4.76 and PASSES, against the measured canvas it is 4.48 and FAILS. Written 2026-09-06 for UI-092, when D26/D31/D41 all asked for the same computation and nobody had one. ⚠ **Read it per element, never by the `TOTAL` line** — `bank` renders one text element per question row and its count moved 3168 → 85 between two runs minutes apart. ⚠ A ratio of exactly **1.00** is the signature of a backdrop bug in the probe, not a real failure. |

| `css_state_probe.mjs` | screen | **What does a HOVERED, FOCUSED, ACTIVE or DISABLED element paint?** Every other probe here reads the page **at rest**, so a state declaration contributes **zero deltas whether it is right or wrong**. Forces the state through CDP `CSS.forcePseudoState` — the flag the style engine itself reads, so the cascade resolves as it would under a real pointer, with no synthetic mouse events to race the pages' JS. `:disabled` is the exception and is applied as the **attribute**, then restored. Writes `css_type_probe`'s exact JSON shape, so **`css_type_diff.mjs` compares two runs unchanged**, `--names` included. Carries **`outline-*`, which `css_type_probe` does not have at all**. **Five states, and FOCUS IS TWO OF THEM:** `focus` forces `:focus` alone (pointer focus — this is the pass that sees `forms.css`:79 and every `input:focus` rule), `focus-visible` forces **both** `:focus` and `:focus-visible`, because a real tab-stop matches both and anything else models a state no user can reach. |

`css_rules_probe.mjs` (older, UI-032) was the DOM half of `css_orphans.py --rules`. **Both
files were deleted on 2026-09-02 — see below and `DEFERRED.md` D59.**

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

**Rule 13, added 2026-09-01: the human half of the check is a probe too, and it kept
slipping because nothing carried it.** The eight-item browser check sat ⬜ for three
sessions, not because it was hard but because every session handed it on as prose.
`static/dev/ui-check.html` now measures the four that CAN be measured — it opens each page in
an **iframe on the same origin**, so it reads their DOM and computed styles with no
extension, no headless runner and no new dependency, in whatever browser the teacher
already uses. The other four (slo import counters, taqseem chips, blueprint shortfall
text, print + Ctrl+P) exist only after a click; the page marks them **AANKH**, never
THEEK, which is rule 10's lesson applied to a human gate.

⚠ **Its first run produced a FALSE FAIL, and the check was wrong, not the app.** It asked
for `select[disabled], button:disabled, input:disabled` and took the FIRST match — a
`<select>`, cursor `default`. But `03-elements/forms.css:211` is `button:disabled` ONLY,
and that file's own comment says so. **A selector list that is wider than the rule under
test will accuse the app of the test's own sloppiness.** Name the exact selector the rule
names, and print the neighbouring value separately if it is interesting.

**`css_orphans.py` and `css_rules_probe.mjs` were DELETED on 2026-09-02 (D59 closed).** They
measured pages against `static/theme.css`, and that file was deleted on 2026-08-13.

**D59's own reason for keeping the file was measured and found false.** That row said
*"Deleting it is tempting and wrong: its `--rules` mode does a job nothing else does."*
Run on 2026-09-02, `--rules` reported `static/theme.css: 0 rules probed (0 selectors)` and
**zero in every column on all nine pages** — it reads the deleted file too. Both halves were
dead, not one. The table half printed the same nine rows of zeros with a warning at the top.

**Why deleted rather than left to degrade:** a tool that prints a confident, well-formatted
table of zeros is worse than an absent one. D59 itself had to warn *"do not quote its
table before then"* — a warning that only works on someone who reads `DEFERRED.md` first.
The measurement lives in git history and in this paragraph.

**Nothing replaced them, because the question is closed, not moved.** They asked *"what does
a page LOSE when `static/theme.css` is unlinked?"*; that file no longer exists and no page
links it. The nearest live question — *"does any `var()` fail to resolve?"* — was settled by
**UI-072 (D14)**: zero unresolved `var()` on any page. Sprint 6's drain question is
`css_drain_probe.mjs`, which is the opposite question and is unaffected.

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
node scripts/css_inject_probe.mjs     <label> <outdir>          # JS-built families — rule 10
node scripts/css_contrast_probe.mjs   [page...] [--json <path>] [--all]   # WCAG AA
```

The browser check is not a script — it is a page. With the app running, open:

```
http://127.0.0.1:8000/static/dev/ui-check.html      # four measured, four marked AANKH — rule 13
```

`css_state_probe.mjs` and `css_inject_probe.mjs` both write the same JSON shape as
`css_type_probe.mjs`, so the SAME diff tool reads all three — there is no per-probe diff to
learn:

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
9. **When ONE declaration of a rule moves and another does not, suspect the cascade before
   the probe.** *(D49, settled 2026-08-28. The row is in `DEFERRED.md`'s Resolved section and
   it asked for this note "beside rules 10 and 11" — there are eight, so it is here.)*

   `slo.css`'s `.btn:disabled { opacity: .5; cursor: not-allowed }` was mutated as a control
   and the probe reported **0 deltas on `cursor`** while `opacity` read `0.5` correctly — the
   same rule, the same element, the same moment. That looks exactly like a blind reader, and
   the row was filed for two days saying it might be one. **It was not.** A four-button
   control page, all disabled, differing only in which layer carries the `:disabled` rule:

   ```
   :disabled rule in layer(legacy)      -> cursor: pointer        (loses)
   :disabled rule in layer(elements)    -> cursor: not-allowed
   :disabled rule in layer(components)  -> cursor: not-allowed
   :disabled rule unlayered             -> cursor: not-allowed
   opacity: .5 in ALL FOUR              -> 0.5
   ```

   CDP reads `cursor` on a disabled control perfectly. What differs is the COMPETITION:
   nothing else in the app declares `opacity` on a button, so that declaration wins even from
   the weakest layer, while `cursor` is contested by `03-elements/forms.css`'s bare
   `button { cursor: pointer }` in `layer(elements)` — which beats `layer(legacy)` whatever
   the specificity. **The probe was right and the CSS was dead.**

   The general form, and it is D51 wearing a disguise: *"the declaration did not move"* and
   *"the probe cannot see it"* are different claims, and the cheap way to tell them apart is
   a second declaration in the same rule. If one moved, the reader works.
10. **A family built in JS is measured by INJECTING it, not by hoping.** *(UI-071,
    2026-08-29. Tool: `scripts/css_inject_probe.mjs`.)*

    Both snapshot probes walk `document.querySelectorAll('*')`, so anything the page builds
    later is simply not there. Measured at rest on every page, **zero elements**:

    ```
    .shortfall-panel   blueprint, print     blueprint.html:1280, print.html:993
    .pill              index, slo           index.html:2190, slo.html:180
    .chips             slo-health, taqseem  slo-health.html:181, taqseem.html:150
    ```

    That is 26 of item 7's 31 lines, and both gates report **0 deltas on all of it whether
    the CSS is right or wrong** — D45's shape, and D12 has recorded the general hole since
    2026-07-28. `status.css`'s header had already been telling sessions to "verify colour by
    injecting the class"; each one did it by hand and threw it away.

    The probe injects each family's own builder markup into the REAL container the builder
    writes into, so inherited context is real — blueprint's panel genuinely sits inside
    `.status-bar.warn`, which is why its `background: var(--surface)` reads as a white panel
    on a tinted bar. Output is `css_type_probe`'s shape on purpose, so `css_type_diff` reads
    it unchanged.

    ⚠ **THE FIXTURES ARE COPIES AND THEY ROT.** Every entry cites the builder line it came
    from. If the builder's markup changes and the fixture does not, the probe measures a
    shape the app no longer renders and returns a confident zero — worse than no probe.
    Re-read the cited lines before trusting a run. And a fixture that cannot find its
    container reports it rather than silently measuring nothing: that is how `print`'s
    `.section-block` was caught being JS-built too.

    ⚠ **A RENAME MAKES ITS OWN ENTRY'S BEFORE/AFTER MEANINGLESS.** The element identity
    changed on purpose, so read absolute values for that entry instead of the diff.

    ⚠ **TWO FIXTURES OF THE SAME SHAPE USED TO EAT EACH OTHER — fixed 2026-09-03, and the
    only reason it was caught is that `injected` and `elems` disagreed.** Item 8's fixtures
    put an identical `.strip-empty` into two different bank containers (`#addTopicImgRow`,
    `#efTopicImgRow`). Both are the first child of their host, so `path()` produced the same
    key for both, the snapshot object is a plain object, and **the second silently
    overwrote the first**: the run printed `injected 3, elems 2` and was otherwise clean.
    Keys now begin with the container selector the fixture was injected into. **Read the
    `injected` and `elems` columns against each other** — a fixture that vanishes this way
    does not report an error, and a gate that measures two things where you wrote three is
    rule 10's own disease one level down.

11. **A fixture is not a gate until a control has broken it.** *(2026-09-03, item 8.)*

    The five new fixtures all resolved and printed plausible values on the first clean run —
    which proves only that they found *something*. The proof they measure the right thing is
    the control: `99-legacy/blueprint.css`'s `.list-empty` padding was changed `30px` →
    `40px 20px`, and the diff returned **exactly 4 deltas on exactly that element and 0
    everywhere else**, then **0 again after the revert**. Do this before trusting any new
    fixture. It costs two probe runs and it is the difference between a gate and a decoration
    — D45 was written because a probe that could not see a change passed happily.

    Values the fixtures pulled on the first run, which are also item 8's own disagreements:

    ```
    bank      .strip-empty  color rgb(138,147,164)   pad 4px 0
    print     .strip-empty  color rgb(153,153,153)   pad 4px 0     <- hardcoded #999
    bank      .list-empty   color rgb(138,147,164)   pad 40px 20px
    blueprint .list-empty   color rgb(100,116,139)   pad 30px      <- BOTH differ
    ```

12. **`css_selector_probe` sirf PEHLA element parhta hai — jab kai elements hon to wo
    jhoot nahi bolta, magar poora sach bhi nahi batata.** *(2026-09-04, UI-081.)*

    Us ka core `getComputedStyle(els[0])` hai (`:118`), aur output ka `n=` batata hai ke
    kitne mile — magar qadrein sirf pehle ki hain. `label` par is ne chaar pages par
    `margin-top: 0px` dikhaya, jis se seedha natija nikalta tha ke legacy ka
    `label { margin-top: 14px }` **murda hai** aur us ko chhorna mehfooz hai. **Wo ghalat
    hota.** Pehla `label` hamesha `label:first-of-type` hai, aur usi page ka apna
    `label:first-of-type { margin-top: 0 }` us par lagta hai. `label:not(:first-of-type)`
    se naapne par chaaron pages par **14px** nikla — rule poori tarah zinda.

    **Qaida: agar `n` ek se zyada ho aur elements mein farq mumkin ho (`:first-of-type`,
    `:last-child`, koi state class), to ek aur selector likh kar dobara naapo.** `n=459`
    dekh kar ek qadr par bharosa karna wahi ghalti hai jise rule 10 doosri shakl mein
    mana karta hai.
