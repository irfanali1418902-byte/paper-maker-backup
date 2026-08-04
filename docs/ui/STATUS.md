# UI-ARCH — Status Board

> **Fresh session: read THIS file first. Do not read PROGRESS.md (2000+ lines).**
> Full plan: `docs/ui/PLAN.md` · Rules: `CLAUDE.md` §11–12 · Parking lot: `docs/ui/DEFERRED.md`

**Branch:** `feat/ui-architecture` · **Baseline tag:** `ui-baseline`
**Last updated:** 2026-08-04 (UI-032's measurement — both checks, all four pages, nothing
migrated) — Sprint 3 2/3; **three pages are live on the new tree**, `landing` and `taqseem`
both held, and **`blueprint` now measures like a fourth held page**

---

## NEXT TASK → **UI-032** — migrate the complex pages: `blueprint`, `bank`, `index`, `print`

**Three of nine pages are live on the new tree, not seven.** `slo` (UI-031a), `slo-health` and
`library` (UI-031b) are migrated. `landing` and `taqseem` were each taken, measured and
**HELD on Irfan's call** — they are the only two waiting on Sprint 4, and their blocks are
below. **The other four have not been touched at all**: `blueprint`, `bank` and `index` still
carry three `<link>`s including `/static/theme.css`, and `print` still links its legacy file
directly. That is UI-032 (`PLAN.md`:190), it is still Sprint 3, and it is what comes next —
Sprint 4 does **not** start until it lands.

*(An earlier draft of this block said Sprint 3's migrations were "done as far as they can go"
and sent the next session to Sprint 4. That was wrong — it read the two HELD pages as the only
remainder and missed the four unmigrated ones. Corrected here rather than left, per the rule
UI-021 wrote about stale predictions.)*

**BOTH CHECKS HAVE NOW BEEN RUN ON ALL FOUR PAGES, and neither is prose any more — both are
`scripts/css_orphans.py`.** No file was migrated and no page's `<link>` was touched — the only
things this measurement wrote are the script, its browser driver, and this block. Re-run rather
than trusting the tables below; that is why it was written as a script and not as prose:

```
python scripts/css_orphans.py --names                       # tokens (check 1)
uvicorn app.main:app                                        # then, in another shell
python scripts/css_orphans.py --rules blueprint bank index print --paper-id <id> --names
```

`--rules` parses `static/theme.css`, runs every selector through `querySelectorAll` against
the live page in headless Edge (its own `--user-data-dir`, killed by the pid it spawned — the
UI-031a hazard), and subtracts what the page's own `99-legacy/<page>.css` redeclares. It
drives the browser through `scripts/css_rules_probe.mjs`.

### The result — four pages, both checks, one table

| page | theme? | tokens: supplied / compat | rules: match / redecl / partial / **orphan** | rule EXPOSURE | verdict |
|---|---|---:|---:|---:|---|
| `blueprint` | yes | 21 / 19 | 29 / 6 / 3 / **20** | **20** (19 + `:focus-visible`) | **DECISION** |
| `bank` | yes | 0 / 0 | 6 / 3 / 2 / **1** | **0** — the one orphan is `:focus-visible`, which `03-elements/forms.css` declares | repetition |
| `index` | yes | 0 / 0 | 11 / 2 / 4 / **5** | **3** — `input[type=number]` and `:focus-visible` are both in `forms.css` | repetition, with a 4-item list |
| `print` | **no** | 0 / 0 | 5 / 0 / 2 / **3** | **0** by D9 — the file is not linked, so all three already fail to apply today | safe by construction |

Measured at 1280×900 in **Edge 151** (this board said 150; the dev PC has moved). Every page
was probed **twice with no action in between and drift was 0 on all four**, and a second full
run from a fresh browser launch reproduced every number *and* every element count
(235 / 5378 / 508 / 555) — the determinism check UI-031b established, applied here to the
counts rather than to a diff. `static/theme.css` is **119 rule blocks**; the `:root` block is
excluded because everything in it is the token half's, leaving **118** probed.

**The unit is the rule block (`{}`), not the selector**, so these numbers are comparable with
`taqseem`'s hand measurement — `input[type=text], input[type=number], input[type=search],
select, textarea` is five selectors and one rule. **The method was validated against
`taqseem` before any new page was believed**: it reports 21 matched / 17 orphan where UI-031c
measured 20 / 16, and the whole of the difference is `:focus-visible`, a state-only rule with
no elements of its own that a `querySelectorAll` method can only report as universal and a
hand method never listed. Subtract it and the two agree exactly, including the redeclared
count. It is broken out as its own `state` column for that reason, and it applies identically
to all nine pages, so it is real but it is never a page's finding.

### `blueprint` — **this board's "probably clean" was wrong, and it is worse than `taqseem`**

**The prediction is corrected where it was made, not only here.** This block used to read: *its
own legacy file declares 10 `.btn` and 4 `.card` rules and it is the one page that already
carries `.pagehead` rules of its own, so the rule half is probably clean — probably is not
measured.* Measured: **20 orphan rules**, and they are the **entire application shell** —

`.app` (the grid itself: `grid-template-areas`, `grid-template-columns/rows`, `height:100vh`),
`.top` · `.top .crumbs` · `.top .crumbs b` · `.top .spacer` · `.top .avatar`,
`.nav` · `.nav .grp` · `.nav a` (×5) · `.nav a .icon` (×5) · `.nav a:hover` · `.nav a.active`,
`.brand .logo` · `.brand b` · `.brand small`, `.card > .ch` · `.card > .ch h3` · `.card > .cb`,
`.chip`, and `:focus-visible`.

Two more (`.app`, `.nav` inside `@media (max-width: 760px)`) are also redeclared nowhere; they
are reported separately because a page measured at one width cannot count them.
`blueprint.css` declares **no** `.app`, `.nav`, `.top`, `.ch`, `.cb` or `.chip` rule at all —
verified by grep, not inferred — its only mention of that shell is the dead
`@media` block D15 already records, which styles `.app-sidebar`/`.app-nav`, classes the markup
does not have. **Nothing in the new tree replaces them either**: `04-objects/shell.css` uses
`o-shell__*` names, which `blueprint.html`'s markup does not use, and none of the twenty
selectors above appears anywhere under `static/css/` outside `99-legacy/`.

**So `taqseem` lost its buttons and card chrome; `blueprint` would lose the grid that puts the
page together.** It is also the **first page exposed on both halves at once** — 21 orphan
tokens (19 needing a compat block) *and* 20 orphan rules. Both of its halves are already
solved on paper: `docs/ui/parked-taqseem.css`'s compatibility block covers its 19 tokens
(finding 4 of the token check), and the rule half needs Sprint 4's shell/nav components, which
is the same thing `taqseem` is waiting for. **Treat it as HELD-shaped work, not as a
migration**, and take it to Irfan before writing any entry file.

### `bank` — the largest legacy file is the cleanest page

366 lines, 5378 elements live, and only **6** of `static/theme.css`'s 118 rules reach it at
all. One is orphaned (`:focus-visible`) and `03-elements/forms.css` declares it, so **the rule
exposure is 0**. `bank.css`:80 declares `input[type="text"], input[type="number"], select,
textarea` itself. Both halves are clean; this is a repetition of `slo-health`/`library`.

Its two `partial` rules are the already-accepted deltas, below.

### `index` — repetition, with four named items

Three real orphan rules: **`.tag`** (×2), **`.row`** (×1), **`.summary-row:last-child`** (×1).
Each has a near-miss in `index.css` that does *not* cover it — `.brand .tag`:53 and
`.topbar .tag`:317 carry colour and size but not the chip's background, padding, radius or
family; `.topbar .row`:311 is more specific than theme's `.row` and already wins today. The
other two orphans (`input[type=number]`, `:focus-visible`) are in `forms.css`.

**All seven screens were measured**, not just the default one: `showScreen()` was driven
through `generate`, `mypapers`, `analytics`, `adaptive`, `results`, `settings`, `syllabus`, and
the counts are the union. The DOM grows **508 → 771** elements across them, so this matters.

### `print` — 0 by measurement, not by assumption

Three rules match its elements, and **all three are already inert**, because `print.html` does
not link `/static/theme.css` (D9 — the script measures the link rather than assuming it). A
migration cannot change them. Measured on a **real exam paper** (25 questions, 25 with images,
27 `<img>`, 555 elements), never a blank page. **One gap, stated rather than papered over:
none of the 21 papers in this DB has any Urdu question text**, so the Urdu half of that
instruction was not exercised — Urdu on this page can only come from the header and labels.

### `partial` — the column that caught what selector-equality gets wrong

A page redeclaring a *selector* does not mean it redeclares the *properties*. That direction of
error is the dangerous one, because it reports a page clean:

- **`.brand` is partial on all four pages** — theme.css:62 gives it `background`,
  `border-bottom`, `grid-area`, and the page's own rule does not. **This is the white slab**,
  removed on `slo`, `slo-health` and `library`, and the check found it independently rather
  than being told. Same for **`.brand small`** on `bank` and `print` (`text-transform`,
  `letter-spacing`, `opacity`) — the uppercase `slo-health` lost.
- **`index.css`:144 `.summary-row` has no `border-bottom`**, so the dashed rule between the
  rows goes with the link. A selector-only check calls that page clean.
- `blueprint` and `index` also lose `.main`'s `grid-area`, `overflow` and `padding`, and
  `blueprint` `.pagehead p`'s `margin-top`/`max-width`.

These are per-selector, so a property could still arrive from a *different* legacy selector
matching the same element. The check is deliberately conservative in that direction; the
migration task's before/after diff is what settles each one.

### Two bugs in the script, both of which moved real numbers

Recorded because both were found by cross-checking a result against the files, which is the
only reason the table above is not wrong:

1. **`input[type=text]` vs `input[type="text"]`.** `static/theme.css` writes the attribute
   value unquoted and both `forms.css` and the legacy files quote it. Normalised naively the
   same rule reads as two, and a page reports an orphan it does not have: **`blueprint` 21 → 20
   and `bank` 2 → 1** once attribute quotes were normalised away.
2. **No property-level check at all**, which produced the false *safe* described above. The
   `partial` column is the fix.

### What did NOT render, and why it does not move the numbers

`blueprint` was measured in its default empty state — no class/subject/exam chosen, `#secList`
holding one empty-state child and `#bpList` two — so its section builder never rendered. That
is **not** a lower bound on its theme.css exposure, and this was measured rather than assumed:
**`blueprint`'s JavaScript assigns no `static/theme.css` class at all.** 44 class tokens were
extracted from its script (the control that proves the extraction works), and the intersection
with theme.css's class names is empty; its one dynamically-built class resolves to
`bg-under`/`bg-over`/`''`. The same holds for `bank` (26 tokens) and `print` (42). `index` has
six — `card`, `bar`, `num`, `sub`, `ur`, `urdu` — of which `card` is already counted and the
rest are inert: `.stat .bar`/`.stat .num`/`.stat .sub` need a `.stat` ancestor and
`.langsw button.ur` a `.langsw`, and neither class exists on any of the four pages. All nine
dynamic class sites across the four pages were read individually; every value is a page-local
name (`q-bad`, `q-review`, `q-good`, `qt rtl`, `img-sm`, `type-badge`).

`bank`'s modals are in the DOM but closed (`[data-open="1"]` is 0), and `index` carries one
closed modal — `querySelectorAll` sees them either way.

**Worth knowing for Sprint 6:** `static/theme.css`'s whole component library matches **zero**
elements on all four pages — `.sec`, `.qrow`, `.pin`, `.switch`, `.segbtns`, `.bloom`, `.stat`,
`.badge`, `.tbl`, `.grid`, `.toolbar`, `.field`, `.panel-soft`, `.langsw` — including the block
commented "section builder (blueprint)". It was written for the mockup, not for the live pages.

### What is otherwise still true of each page

- **`blueprint`** — the first already-token-clean page (UI-015): its `:root` aliases onto
  `static/theme.css` tokens, which is exactly the D20 shape. Its own file declares 10 `.btn`
  and 4 `.card` rules, and it does carry its own `.pagehead` — none of which was enough, see
  above.
- **`bank`** — 366 lines, 62 raw hex.
- **`index`** — an SPA: 7 screens via `showScreen()`, sidebar with `onclick` rather than
  `href`, and 224 of the project's 466 inline `style=""` attrs. Sprint 5's burn-down is NOT to
  be started here; the inline values must come out byte-identical.
- **`print`** — only 2 `<link>`s, and it is the **Ctrl+P page**, the highest-consequence one
  in the epic. Whatever else is true, its output is re-checked on a real exam paper.

**`landing` is HELD, not pending — do not just migrate it.** It was built, measured and passed
its gates, then held on Irfan's call because it visibly degrades the app's front door: this
page's legacy `h1` is the largest in the project and the new tree's is smaller, so the hero
headline shrinks from two lines to one and `reset.css` zeroes the 12px gap beneath it, leaving
the title jammed against the paragraph. Its finished entry file is parked at
`docs/ui/parked-landing.css` with the full measurement and restore instructions in its header —
**read that before touching this page.** The real fix is a hero/display type step, which is
Sprint 4's typography work, so landing should resume *after* that lands, not before. **Note
that no Sprint 4 task currently owns it:** `PLAN.md`:195-198 gives UI-040..043 as card,
button, modal/field and tables/domain — a display type step is in none of them, so it needs
either an ID of its own or an explicit home inside one before landing can resume. It also
loses its `.icon` override (22px → 17px on 11 icons) the moment its file becomes layered,
because `app.css` is unlayered and beats it — the first time UI-031a's warning about that
actually fired.

**`taqseem` is HELD too, and the finding is bigger than the D20 it was carved out for.** It was
taken as a token problem — its legacy file reads `static/theme.css` tokens with no fallback —
and that half went exactly as planned: the real count is **26 read-but-never-declared** (this
board said 20; corrected by measurement), **3** of which (`--font-display`, `--font-body`,
`--font-data`) Tier 2 already declares under the deliberate collision, leaving **23** for a
compatibility block. All 23 map 1:1 onto existing Tier 2 roles with **no value change and no
literal**, declared names collide with `01-settings/` **zero** times, and the block was
verified in the browser: all 23 resolve, none empty. That file exists and works.

**It was held because the page also borrows RULES from `static/theme.css`, not just tokens —
and no grep over custom properties can see that.** Measured against the live DOM: **20**
`static/theme.css` rules match elements on this page and **16 of them are not redeclared
anywhere in `99-legacy/taqseem.css`** — `.btn`, `.btn.gold`, `.btn.ghost`, `.btn:hover`,
`.btn:disabled`, `.card`, `.card.has-ch`, `.card > .ch`, `.card > .ch h3`, `.card > .cb`,
`.pagehead`, `.pagehead h1`, `.pagehead p`, and two `input`/`:focus` rules. Dropping the link
therefore does not "remove theme.css bleed" here, it **removes the page's buttons and card
chrome**: measured after the swap, the three `.btn`s fell all the way back to UA default
(background `rgb(240,240,240)`, 2px border, padding 1px 6px, `display:block`, weight 400,
radius 0) and `.card`'s `box-shadow` went to `none`. The new tree has no replacement yet —
`.btn`/`.card` are Sprint 4 components and D22 parks the button reset until UI-041.

**This is a property of `taqseem` alone, and that is why three clean pages made it look
routine.** Counted per legacy file: `slo` declares 5 `.btn` and 3 `.card` rules of its own,
`slo-health` 2 and 3, `library` 13 and 3, `blueprint` 10 and 4 — **`taqseem` declares 0 and 0**
and leaned entirely on the shared stylesheet. The markup uses all of them (`btn gold` ×2,
`btn ghost`, `card has-ch`, `pagehead`).

**So the check this board prescribed was necessary but NOT sufficient, and that is the lesson
to carry to `blueprint` and every remaining page.** Two greps over `var()` and `--name:` decide
the *token* question only. The rule question is a different measurement and needs the DOM:
parse `static/theme.css`, run each selector through `querySelectorAll` on the live page, and
subtract the selectors the page's own legacy file redeclares. **Run both before deciding any
page.** That measurement is now `scripts/css_orphans.py --rules`, and it has been run on all
four remaining pages — see the NEXT TASK block above.

**This paragraph used to end: *"`blueprint` is the next page that will meet this (D20 lists it
at 17 orphan tokens) and its `.btn`/`.card` counts above say the rule half is probably clean
there — probably is not measured, so measure it."* It was measured, and the prediction was
wrong in both halves.** Its tokens are **21**, not 17, and its rule half is not clean but
**20 orphan rules — the whole application shell**, `.app` grid included. The `.btn`/`.card`
counts were a real signal about buttons and cards and said nothing about the shell, which is
the part `blueprint` borrows. `taqseem` 0/0 was the loudest case of a general fact, not the
only case. Detail and the full list are in the NEXT TASK block.

**The work already done is not wasted, and it is parked exactly like landing's:**
`docs/ui/parked-taqseem.css` carries the two `@import`s and the 23-token compatibility block,
ratchet-clean (no raw hex), with the restore instructions in its header — **read that header
before touching this page.** It sits in `docs/` for the same reason
`docs/ui/parked-landing.css` does: anything under `static/css/` counts toward
`shared_css_lines` even when no page links it, so leaving it in place would let the next
task's `--write` bury 61 unlinked lines inside its own number. `shared_css_lines` is therefore
back at **1616** and `BASELINE.json` was not re-pinned — nothing shipped. `taqseem.html` is
untouched at HEAD, still on its three `<link>`s.

**The shape, decided in UI-031a and not to be relitigated:** each page gets a two-line entry
file `static/css/pages/<page>.css` — `@import url("../main.css");` then
`@import url("../99-legacy/<page>.css") layer(legacy);` — and its `<link>` block becomes
`app.css` + that entry file. `main.css` no longer imports any legacy file. Copy
`pages/slo.css`, read its header first; it documents why each line is what it is.

**Do them one at a time, with a browser open, and measure per page before writing:**

- **Run the orphan-token check first — two greps — but know that it decides only HALF the
  page.** Collect the names the page's `99-legacy/<page>.css` *declares* and the names it
  *reads via `var()`*; the set it reads but does not declare is the D20 exposure. `slo` **0**,
  `slo-health` **0**, `library` **0**, `taqseem` **26** (this line said 20 until `taqseem` was
  measured). Also diff its declared names against `01-settings/tokens.css` +
  `01-settings/theme.css` together — a shared name means the token changes owner when the tree
  arrives. Zero collisions on all four pages checked so far.
- **Then run the orphan-RULE check, which is the half that held `taqseem`.** A page can borrow
  whole rules from `static/theme.css`, not just token values, and no grep over custom
  properties will show it. Parse `static/theme.css`, run every selector through
  `querySelectorAll` against the live page, and subtract the selectors the page's own legacy
  file redeclares — what is left disappears the moment the link goes. `taqseem`: **16**
  (`.btn*`, `.card*`, `.pagehead*`, two `input`/`:focus`), which is its whole button and card
  chrome. Cheap sanity check before the browser work: `.btn`/`.card` rule counts per legacy
  file — `slo` 5/3, `slo-health` 2/3, `library` 13/3, `blueprint` 10/4, **`taqseem` 0/0**.
- **Diff every page against BOTH mechanisms**, not just one — see `pages/slo.css`'s
  "WHAT ACTUALLY CHANGED" block. (1) `static/theme.css` bleed being removed, which is
  per-page and unpredictable: on `slo` it took a **white slab** out of the navy sidebar and
  un-flexed 115 badges; on `slo-health` the **same white slab** was sitting there too and is
  now gone, along with the uppercase and letter-spacing theme.css was putting on `.brand
  small`. Two for two: treat the slab as a `static/theme.css` fact, not a `slo` quirk. (2) The new tree beating `layer(legacy)` — D21, live: `reset.css`
  zeroes legacy class margins, `typography.css` grows `h1`/`h2`, `forms.css` re-fonts buttons.
- **Bare element selectors in `layer(elements)` reach further than the class rules suggest.**
  `slo-health` found two the review of `slo` did not name: `typography.css`'s `a { color:
  inherit }` beat legacy's `.app-nav a` colour, turning **all six** inactive nav links white
  (the active one already was), so active/inactive now differ only by background and left
  border; and `small { }` beat `.brand small`, taking the sidebar subtitle's size and colour.
  Check `a`, `small`, `th`, `td`, `h1`, `h2` against the page's own class rules on every page.
- **Prove the render is deterministic before you diff it.** Two identical before-snapshots,
  then compare. `slo-health` was 191 elements with **0** run-to-run drift; without that check a
  data-driven page's jitter reads as a CSS delta. And **align out the `<link>` you removed** —
  it is itself an element in `querySelectorAll("*")`, so the count legitimately drops by one.
- **Define the property set before quoting any aggregate**, or do not quote one (the rule
  `pages/slo.css` states, after two counts of the same migration disagreed). `slo-health`:
  **1463** element × property deltas over a set of 36 properties fixed in advance.
- **Measure the backdrop, never assume it** — the single most repeated failure on this epic
  (D26's first draft, and three more like it). On `slo-health` the subtitle's *before* backdrop
  was the white slab, not the navy sidebar, which flips the sign of the result: **2.20:1 →
  3.04:1, an improvement**, still under AA. Table `th` went the other way, **5.81:1 → 4.60:1**,
  which clears AA by 0.1 — worth knowing before someone "tidies" `--color-text-muted`.
- **A page renders less than you think.** `slo-health`'s measurement covers only what the
  current DB produced: four cards sat in empty states and the `.cov-*` blocks never rendered at
  all (they need a class + subject + exam chosen). Say which parts you did *not* measure in the
  handover, and put them in the click-list.
- **`landing.html` has no `theme.css` and no sidebar** (D9) — expect a different delta shape.
- **`library.css` carries `--text`, which is defined nowhere** (D14). Inert today; confirm it
  stays inert rather than assuming.
- **`app.css` stays linked** on every migrated page until Sprint 4 — it owns `.icon`.
- **Quote FULL PATHS in the handover click-list** (D29). Two files are named `theme.css` and
  the Network panel shows only the basename; the bare word cost a false alarm on UI-031a.

**Not carried over from UI-031a, deliberately:** `config/nav.json` was **not** rendered and
no `o-shell__*` class was added to the markup — the page's own legacy file still lays out and
paints its sidebar, so the shell object applies to nothing. Sprint 4's nav component is what
consumes both. Do the same here unless there is a reason not to; adding markup multiplies the
diff and the frozen-inventory risk across every page it touches. `slo-health` held to it: the
only bytes that moved were its `<link>` block, **−53**, and the frozen inventory (19), class
attributes (74) and all three `<script>` bodies came out identical.

**Still open from UI-030:** the `<760px` breakpoint is not in `shell.css` — it hides the nav
and the toggle that gives it back is a Sprint 4 component. Untested on a migrated page so far.

---

## Previous task → **UI-031a** — `slo.html` onto the new tree · **the first live page**

**`@layer` has now been parsed by a browser**, and the cascade this epic is built on resolved
on a real page for the first time. Verified in headless Edge 150 via CDP: the
`CSSLayerStatementRule` carries all seven names in order, every import lands in its declared
layer, and `99-legacy/slo.css` arrives in `layer(legacy)` rather than unlayered. Blocked item
1 (the school PC) is **still open** — this is the dev PC.

**D19 was resolved by changing the load mechanism, and the documented shape would have broken
the page.** Measured before writing: `main.css` imported all nine legacy files, they import
alphabetically, so `taqseem.css` is last and won **15 selectors** off `slo` — `:root`,
`.app-sidebar`, `.brand`, `.brand .name`, `.brand small`, `.app-nav`, `.app-nav a`,
`.app-nav a.active`, `.sidebar-foot`, `.row`, `body`, `html, body`, `a`, `*`. Every value it
brought reads a `static/theme.css` token that the same task unlinks, so "drop `theme.css`,
link `main.css`" would have shipped an **unpainted sidebar and no border colours**, through a
file belonging to a different page — **D20 arriving by the back door**, on the one page whose
own tokens are all local literals. So the legacy import moved out of `main.css` and into a
per-page entry file. `main.css` keeps the layer order and the shared tree and remains the
single source of the cascade (exactly one layer statement in the document).

**`CLAUDE.md` §11's link rule changed with it** — the `<link>` now goes to
`/static/css/pages/<page>.css`, not `main.css` directly. Recorded as unplanned in both the
rule and the file headers.

**Three visible changes nobody predicted, all `static/theme.css` bleed being removed**: the
`.brand` block had a **white slab** inside the navy sidebar (`theme.css`:62 paints it, because
there `.brand` is a cell in the `.app` topbar grid and this page has no `.app`); `.bloom` was
`display:flex` on 115 badges from a **bar-chart component** meant for another page; nav links
were the wrong grey. All three are fixes, and the first is why D26's first draft was wrong.

**Four rounds of review FAILED this, and the three real failures are one shape: a number
asserted instead of measured.** (1) D26 computed a contrast ratio against an *assumed* navy
backdrop — both colours were measured in the browser, the backdrop was not; the real figure is
**1.70:1 → 3.04:1, an improvement**, not the "6.59 → 3.04 regression" first written. (2) The
"what changed" block named only one mechanism, missing **D21 firing live** — `reset.css`
zeroing `.card .hint`'s 16px, `typography.css` taking `h1` to 24px, `forms.css` taking buttons
off Arial. (3) Four line numbers were inherited rather than checked: `forms.css:58` is the
input/select/textarea rule and **cannot match a button** (:101-102 does), `:102` is not the
border (:62 is), `reset.css`'s `margin:0` is at :91. **All three are recorded in the files as
failed drafts**, so the next session meets the trap, not just the answer. An aggregate
delta count was **removed rather than corrected**: two independent measurements disagreed
because they used different property sets, so the files now give affected *elements* per rule,
which is re-derivable from markup with a grep.

**A hex in a comment tripped the ratchet — and `--write` nearly laundered it.** Quoting two
border colours in prose took `unsanctioned_hex` **429 → 431**; because `css_baseline.py
--write` had already run, the raised number was pinned into `BASELINE.json` and `--check` then
reported OK against the laundered baseline. Fixed by removing the hex and
`git checkout docs/ui/BASELINE.json` before re-pinning. **Re-pin only after `--check` passes
against HEAD's baseline, never before.** The reviewer mutation-tested the guard afterwards
(hex restored → 429 → 431, exit 1).

**Irfan's browser check found a fourth false alarm, and was right to stop on it.** `theme.css`
appeared in the Network panel with initiator `main.css:87`. **Two different files carry that
basename**: `/static/theme.css` (13787 B, the old stylesheet, genuinely gone from this page)
and `/static/css/01-settings/theme.css` (8682 B, the Tier 2 palette, which must load). The
handover said "theme.css gone" instead of naming the path. **D29** records it; quote full
paths from here.

**Three visible changes ship with this page and are Irfan's accepted trade** — all with a
Sprint 4 home, none fixable inside a task scoped to one page's `<link>` block: **D26** the
sidebar subtitle at 3.04:1 (better than before, still under AA), **D27** `<a class="btn-ghost">`
losing its blue while `<button class="btn-ghost">` keeps it, **D28** cards visibly tighter —
headings ~20% bigger with the gap beneath them gone.

---

## Previous task → UI-030 — **`04-objects/shell.css` + nav config; still no page touched**

`.o-shell__*`, layout only, zero cosmetics, plus `config/nav.json` as data that nothing reads
yet. **Two reviews FAILED it**, the second on errors introduced by the first round of fixes
(see the task log). The finding worth carrying: **every one of the mockup's shell class names is
already taken**, and in two different ways — `.brand` (nine legacy files), `.main` (two) and
`.spacer` (one) sit in `layer(legacy)` and would be **silently overridden** by `layer(objects)`,
while `.app`/`.top`/`.nav` are in unlayered `static/theme.css` and *beat* the new layer instead.
Three and three. The `o-*` prefix (`PLAN.md`:125) is what makes the file safe, not tidiness —
and putting `.spacer` on the wrong side of that split is exactly what the second review caught.

**D21's height half is closed as unnecessary, not deferred again.** `html, body { height: 100% }`
was predicted to be UI-030's to land; it never landed, because `.o-shell` uses `height: 100vh`,
which needs no percentage chain from `body`. The design target carries both and only the second
is load-bearing. **`print.html` is therefore untouched** — the risk D21 existed to flag is not
taken at all.

**`--weight-medium` (500) did NOT land here either**, against the board's own prediction:
`04-objects` is layout-only and cannot consume a weight. It lands with `05-components/nav.css`
in Sprint 4. Both stale predictions were corrected where they were written, not just here.

**Sprint 3 (UI-031/032) is where the traps are: D19, D20 and now D21/D22 are one decision.**
`blueprint.html` and `taqseem.html` are the two pages that actually break (D20: 17 and 20
orphaned tokens, none fallback-protected). Add to that list, all landing in the same session:
base type goes **16px → 15px on nine pages** (`typography.css` `body`), `slo`/`slo-health`
tables take the design target's metrics (`tables.css`), and the button appearance reset is
still parked in **UI-041** (D22) so it does *not* land with them.

---

## The pre-Sprint-3 browser session — **done 2026-07-31**, with one item still open

Ran after UI-021, before any page's `<link>` changed — the point being that a revert was still
cheap. Two halves: Irfan in a real browser, and an agent over live HTTP against
`uvicorn app.main:app` on `127.0.0.1:8000`.

**Closed — Irfan, in the browser:**

- **`print.html` Ctrl+P: margin ~14mm, not 28mm.** Checked on a **real exam paper** (Pre Year 1
  Math), not a blank page — **Urdu, images and page breaks all correct**. This was the epic's
  highest-risk unknown and it is now closed for Sprint 1's extraction. *(This block warned that
  it was not closed for UI-030, "which lands `html, body { height: 100% }` on a page that has no
  such rule today". **UI-030 never landed that rule** — `.o-shell` uses `height: 100vh` instead,
  so print.html was not touched and D21's height half is closed as unnecessary.)*
- **All nine pages load styled** — `slo`, `slo-health`, `taqseem`, `landing`, `library`,
  `blueprint`, `bank`, `index`, `print`. No unstyled flash, no broken layout.

**Closed — over live HTTP:**

- Nine pages **200**, each with **0 `<style>` blocks** — Sprint 1 verified live, not just on disk.
- Every referenced stylesheet **200 / `text/css`**; no 404. `landing` and `print` carry 2 sheets
  (no `theme.css` — D9 live-confirmed), the other seven carry 3.
- **`main.css` is linked by zero of the nine** — "zero visual effect" is now a measurement.
- All 16 live `@import`s in `main.css` resolve **200** in their declared layer order.
- **All nine `woff2` return 200 through the `../../fonts/` relative path.** Better evidence than
  UI-021's disk check: `url()` actually resolved through the server. The one silent-404 risk the
  new tree introduced is closed.
- Dev PC: **Edge 150.0.4078.96, Chrome 150.0.7871.187** — both far past ADR-001's floor of 99.

**STILL OPEN, and do not let this board be read as saying otherwise:**

1. **The school PC's Edge version.** Irfan checks later. ADR-001 accepts `@layer`'s hard-fail
   risk *purely* on Edge auto-updating, and that is still untested on the machine that matters.
2. **No browser has ever parsed `main.css`.** "The pages didn't break" does **not** evidence
   `@layer` working, because no page loads `main.css` — that result is equally consistent with
   the `@layer` line never having been read. What actually retires the risk is the version
   numbers above (`@layer` shipped in 99; these are 150), plus the first page that links
   `main.css` in **UI-031**. Treat the cascade this epic is built on as *unobserved* until then:
   layer order beating specificity, `layer(elements)` overriding legacy classes, and D19/D20/D21
   all resolve for the first time on a real page in that task. **Open UI-031 with a browser.**

---

## Previous task → UI-021 — **done; Sprint 2 foundation complete**

**UI-021** (`docs/ui/PLAN.md` §Sprint-2): `02-generic` reset + fonts + `03-elements`
typography / forms / tables. Five new files, `main.css`'s five `@import`s uncommented in
place, **not one `.html` byte touched**. Same shape as UI-020, same zero visual effect.

**The one thing a fresh session must take from it: a "reset" in this tree is not neutral.**
`layer(generic)` and `layer(elements)` both **outrank `layer(legacy)`**, and layer order beats
selector specificity — so a bare element selector in the new tree overrides a *class* rule in
any of the 2115 legacy lines. That is what "legacy demoted" buys, and it is also what makes a
carelessly-ported reset destructive. UI-021 shipped a reset *smaller* than the design target's
for exactly this reason (**D21**), and parked the button appearance reset entirely (**D22**).
No ratchet metric sees this class of break — it counts lines and hex, not whether a list still
indents.

---

## Earlier → UI-020 — **done; the ratchet was ready for it**

**Sprint 1 is complete.** All nine pages load their CSS from `static/css/99-legacy/`.
`style_blocks` **0** · `css_lines_in_html` **0** · `hardcoded_hex` **0** ·
`legacy_css_lines` **2115** across nine files. Not one colour was deleted getting here —
`unsanctioned_hex` is still **429**, exactly where it started. The debt is fully
relocated and none of it is yet repaid. **That is the point.** Sprint 2 begins the
foundation the burn-down needs; the repayment itself is Sprints 5–6.

**UI-020a is done** (see the task log): the hex ratchet now distinguishes the sanctioned Tier 1
palette from everything else, which is what makes UI-020 writable at all. Do not relitigate it.

**UI-020** (`docs/ui/PLAN.md` §Sprint-2): `main.css` + import order + legacy demoted +
`01-settings` 3-tier tokens (Modern palette). Read PLAN.md and ADR-001 before planning —
this is the first task that *authors* CSS rather than moving it, so the rules that governed
Sprint 1 no longer all apply. Expect ADR-001's `@layer` decision (locked 2026-07-28) to
matter here for the first time.

**The contract changes shape at UI-020, and the metrics change with it.** Sprint 1's
invariant was "`total_css_lines` falls by exactly 2, nothing else moves." That is over.
UI-020 *adds* files under `static/css/`, so **`shared_css_lines` must rise** — it has been
flat at 269 through nine tasks and a rise was a FAIL every time. From here it is expected.
Re-read the ratchet's notes below before assuming a moving number is a defect, and set the
expected movement in the plan **before** writing, so the review agent has something to hold
you to.

**What UI-020 must get right, beyond the obvious:**

- **`unsanctioned_hex` must stay flat at 429.** Authoring `tokens.css` raises
  `total_hardcoded_hex` and `token_hex` together and leaves `unsanctioned_hex` alone — that
  is ratchet-neutral and correct. But **any raw hex in `01-settings/theme.css` (Tier 2) will
  fail**, because only `tokens.css` is exempt. Tier 2 reads `var(--tier-1)`, never a literal.
- **Author `tokens.css` one declaration per line.** `PLAN.md` §2's example is a single line,
  which satisfies `test_tokens_file_holds_only_token_hex` vacuously (D17).
- **`total_css_lines` and `legacy_css_lines` stay at 2115.** `01-settings/` is not
  `99-legacy/`; the new tree lands in `shared_css_lines`.
- **No page head is touched.** The single `<link>` to `main.css` is **Sprint 3** (§11 marks
  that rule end-state). UI-020 therefore has zero visual effect by construction.
- `git add static/css/` **explicitly** — new files there are not staged by adding modified
  files alone.
- After UI-020, `test_tokens_file_holds_only_token_hex` stops skipping: expect **906 passed,
  0 skipped**, not 905/1.

Still true, and still the thing that catches real mistakes: `unsanctioned_hex` may only
fall by genuine deletion, and no page may gain a `<style>` block.

---

## Progress

`99-legacy/` lines remaining is the real progress metric. **2133 → 0.**

| Sprint | Tasks | Done | State |
|---|---|---|---|
| 0 Guardrails | UI-000..003 | **4/4** | **done** |
| 1 Extraction | UI-010..018 | **9/9** | **done** |
| 2 Foundation | UI-020..021 | **2/2** | **done** |
| 3 Shell | UI-030..032 | **2/3** | in progress — **UI-032's MEASUREMENT is done (both checks, all four pages, 2026-08-04) but no page is migrated**; those four are still on their old `<link>`s. Verdicts: `bank` and `index` are repetitions, `print` is 0 by D9, and **`blueprint` measures like a fourth held page** — 21 orphan tokens *and* 20 orphan rules, the whole `.app`/`.top`/`.nav` shell, so it needs Irfan and Sprint 4's components, not an entry file. UI-031: `slo`, `slo-health`, `library` live; **`landing` HELD** (hero regression, resumes after Sprint 4 typography) and **`taqseem` HELD** as UI-031c (16 orphan RULES — its buttons and cards live only in `static/theme.css`; resumes after Sprint 4 components). Both measured, neither to be re-attempted before Sprint 4 |
| 4 Components | UI-040..043 | 0/4 | not started |
| 5 Inline burn-down | UI-050..052 | 0/3 | not started |
| 6 Legacy kill | UI-060..064 | 0/5 | not started |
| 7 Optional | UI-070 | 0/1 | not started |

### Task log

| ID | Task | Status | Commit | Note |
|---|---|---|---|---|
| UI-000 | Commit baseline, tag, branch | **done** | `addb2fb`, `985f47b` | tagged `ui-baseline`; tree had been dirty (theme.css Modern rewrite + 7 link lines + untracked mockups) |
| UI-001 | Planning docs + CLAUDE.md §11–12 | **done** | `6c381fa` | this document set |
| UI-002 | Ratchet test + BASELINE.json | **done** | `b215666` | 26 tests, 900 passed. 3 extra metrics added (see below). Reviewed twice; 2nd pass found the JS-class check is JS-side only → D11 |
| UI-003 | Remove dead `primary`/`navy` from brand config | **done** | `2eba2f8` | closes D6. Re-verified unused at implementation. Also fixed `api/brand.py` docstring; logo.svg's same hex → D13 |
| UI-010 | Extract `slo.html` CSS → `99-legacy/slo.css` | **done** | `cbd567a` | 91 lines moved verbatim, two reviewers byte-compared. Fixed 2 ratchet defects the first real extraction exposed: `hardcoded_hex` blind to `.css` files → added `total_hardcoded_hex`; a ratchet test anchored to `baseline` broke once a metric legitimately moved |
| UI-011 | Extract `slo-health.html` CSS → `99-legacy/slo-health.css` | **done** | `c05da55` | 111 lines moved verbatim; byte-compared against the original `<style>` inner, exact match at 5754 chars. Metrics landed exactly as predicted. Was built in a prior session but left **uncommitted** — caught at the start of UI-012, verified and committed then |
| UI-012 | Extract `taqseem.html` CSS → `99-legacy/taqseem.css` | **done** | `93f51b9` | 115 lines moved verbatim (6482 chars, exact match). Reviewer substituted the block back in at the `<link>` site and reconstructed `HEAD` byte-for-byte — proves both the verbatim cut and that nothing outside the block moved. Metrics landed exactly as predicted |
| UI-013 | Extract `landing.html` CSS → `99-legacy/landing.css` | **done** | `a9e876c` | 100 lines moved verbatim (3766 chars, exact match); `HEAD` reconstructed byte-for-byte. **This page had no `theme.css` link** — head one line shorter, so the `<link>` went to line 8; none was added, since adding one is a visual change. Metrics landed exactly as predicted |
| UI-013a | `CLAUDE.md` §11 — mark hard rules as end-state | **done** | `4a56b5b` | Docs only, no metric movement. §11's "one `<link>` per page" and "raw hex = CI failure" read as flat rules, but every Sprint 1 page necessarily breaks both in transit — a fresh session could "fix" it mid-sprint and revert a reviewed extraction. Adds an END-STATE preamble and marks the three affected rules with the sprint that retires each. Raised by UI-012's reviewer; committed separately so the extraction diff stayed reviewable |
| UI-014 | Extract `library.html` CSS → `99-legacy/library.css` | **done** | `19448a6` | 251 lines moved verbatim (11677 chars, exact match); `HEAD` reconstructed byte-for-byte at all **67668 bytes**. Largest extraction so far, 2.5× UI-013 — no re-indent or trailing-whitespace drift on any of the 251 lines. The ~39k script body byte-identical (39296 both sides). Found and deferred **D14** (`.pg-btn` reads `var(--text)`, which is defined nowhere) rather than fixing it. Metrics landed exactly as predicted |
| UI-015 | Extract `blueprint.html` CSS → `99-legacy/blueprint.css` | **done** | `5c7f752` | 277 lines moved verbatim (13378 chars, exact match); `HEAD` reconstructed byte-for-byte at all **66883 bytes**, the 46511-byte `<script>` body byte-identical. **First already-token-clean page** — its `:root` aliases onto `theme.css` tokens, so the whole block carried exactly one raw hex (`#fff` in `.btn-primary`), left untouched. `hardcoded_hex` therefore moved only 211 → 210, as predicted. Found and deferred **D15** (a `@media (max-width:760px)` block styling `.app-sidebar`/`.app-nav`/`.sidebar-foot`/`.bp-main`, none of which exist anywhere) rather than fixing it. Metrics landed exactly as predicted |
| UI-016 | Extract `bank.html` CSS → `99-legacy/bank.css` | **done** | `fcdfda1` | 366 lines moved verbatim (18015 chars, sha256 identical both sides); `HEAD` reconstructed byte-for-byte at all **94162 bytes**, the ~1830-line `<script>` body proven untouched. **Largest extraction of the sprint**, ~1.5× UI-014 — reviewer classified drift per line across all 366 and found none, with the indent-depth histogram (`{2: 214, 4: 124}`, 338 indented lines) identical on both sides. All **62 raw hex moved unconverted** in the same order (`var(` flat at 90), the inverse of UI-015's token-clean page. Reviewer additionally served the app and confirmed `/static/css/99-legacy/bank.css` returns **200, text/css, 18015 bytes** — the first live 404-check of the sprint. Frozen inventory 152 → 152. Metrics landed exactly as predicted |

| UI-017a | Ratchet — frozen inventory counted CSS attribute selectors as markup | **done** | `6c2829c` | Guardrail fix, no metric movement. `FROZEN_ATTR_RE` ran over the raw page source including `<style>` blocks, so a quoted attribute *selector* (`.modal-overlay[data-open="1"]`) was indistinguishable from a real markup attribute — extracting the block read as vanished handlers and failed two tests on a correct task. index.html had six (`[data-active="1"]` ×5, `[data-open="1"]`). Now scans markup only, via the `STYLE_ELEMENT_RE` that already existed. Effect surgical: index.html 269 → 263, other eight pages byte-identical, no ratcheted metric moved. Reviewer **mutation-tested** it rather than accepting the argument — five renames (`id`, `onclick`, `data-nav`, `data-lang-opt`, a dropped `data-active`) are all still caught — and found the decisive fact: `data-open="1"` never appears in index.html markup at all, JS sets it at runtime and the markup's `data-open="0"` survives in the inventory. Split from UI-017 so a self-referential guardrail change got reviewed on its own, per UI-013a precedent |
| UI-017 | Extract `index.html` CSS → `99-legacy/index.css` | **done** | `36f3c61` | 337 lines moved verbatim (17681 chars, exact match); `HEAD` reconstructed byte-for-byte at all **130737 bytes**, with all 3 `<script>` blocks (1712 lines) identical. Zero drift on any of 337 lines. All **61 raw hex** moved unconverted (`var(` flat at 87). **Scope trap held**: this page holds 224 of the project's 466 inline `style=""` attrs and 57 of the 76 inline hex — the full inline value sequence is byte-identical, so Sprint 5's work was not started early. The block's `@font-face` uses only `local()` and the block has **0 `url()`**, so relocating the CSS could not break a relative path — worth checking on every future move, since `url()` resolves against the stylesheet, not the document. Exposed the ratchet defect fixed in UI-017a. Reviewer served the app: `/` returns 200 with 0 `<style>` blocks and all three stylesheets 200. Metrics landed exactly as predicted |
| UI-018a | Ratchet test — re-anchor the cwd-independence canary | **done** | `549d0e3` | Test only, no metric movement. `test_measurement_is_cwd_independent` guards CLAUDE.md §12.9: a cwd-relative glob finds no pages from `C:\Users\MCS` and reports a triumphant zero for every metric. Its "we found pages" canary was `style_blocks > 0` — which Sprint 1 drives to 0 by design, so at UI-018 it fired on success. Re-anchored to `per_page` non-empty **and** the same page set. Reviewer mutation-tested it: with `page_paths()` swapped for a cwd-relative glob the new canary still catches it, and a second mutation (4 of 9 pages found) is caught only by the set-equality half — so that half is load-bearing, not decoration. It also established there is **no surviving metric** fit for the job: the six per-page metrics are all driven to 0 by the plan, and the five tree-level ones read `.css` directly so they stay non-zero with zero pages found — blind to the trap entirely. Page count is the only correct anchor. Same class as the defect UI-010 fixed |
| UI-018 | Extract `print.html` CSS → `99-legacy/print.css` | **done** | `6075ed0` | **Last extraction of Sprint 1.** 467 lines moved verbatim (20209 chars, sha256 identical both sides); `HEAD` reconstructed byte-for-byte at all **66389 bytes**, the 35711-byte script body identical. Zero drift on any of 467 lines (indent histogram identical). All **87 raw hex** — every one left in the project — moved unconverted, taking `hardcoded_hex` to **0**. **This head has no `theme.css`** (D9), so the `<link>` went to line 8 and none was added; the page carries exactly 2 stylesheets. Print-critical rules verified intact: 1 `@page { size: A4; margin: 0 }`, 2 `@media print`, and the three JS-driven knobs (`--page-margin: 14mm`, `--q-font: 14px`, `--q-gap: 14px`) still defined with their defaults. Reviewer reasoned the cascade explicitly: `setProperty` on `documentElement.style` writes the style attribute, which outranks author *normal* rules regardless of whether they came from a `<style>` or a `<link>` — the move is cascade-neutral. **Corrects a wrong number this board carried**: the UI-017 handoff said "3 `@page` / 3 `@media print`" from a raw grep that counted prose mentions inside CSS comments. Comments stripped, it is **1 and 2**, confirmed by two independent counts. `PLAN.md`'s "5 `@media print`" is wrong too → **D16**, not edited in passing (§12 rule 11). Metrics landed exactly as predicted |
| UI-020a | Ratchet — sanction Tier 1 token hex, ratchet `unsanctioned_hex` | **done** | `4273da6` | Guardrail fix, no CSS authored. **UI-020 was literally unwritable before this.** `total_hardcoded_hex` was ratcheted and summed hex across *every* `.css` under `static/` (`rglob`), but Tier 1 tokens are raw hex by definition, so authoring `01-settings/tokens.css` at all pushed 429 → ~451 and failed `test_metric_never_increases`. Meanwhile ADR-001:98–99 and §11 both define the invariant as "a raw hex outside `01-settings/tokens.css` is a CI failure" — the end state has hex *inside* that file, so this board's own target of 0 was unreachable by construction. Adds `token_hex` (that one file) + `unsanctioned_hex` (everything else, **ratcheted**); `total_hardcoded_hex` keeps its exact definition and goes informational, so every number in this log stays comparable. `RATCHETED_METRICS` is 8 both sides — one swapped, none dropped (reviewer AST-parsed both revisions). **First review FAILED it, and was right**: the new exemption-scope test asserted against `current` rather than the re-measurement, so it held only while `tokens.css` was absent and would have failed the suite deterministically on the very next task — the UI-018a defect class exactly. Reproduced at `assert 431 == (429 - 3)` before fixing, then re-verified invariant with a real `tokens.css` at **1, 5, 22 and 40 hex**: `unsanctioned_hex` pinned at **429** every time, and `total_hardcoded_hex` hit exactly **451** at 22, matching the projection. Second reviewer mutation-tested the exemption four ways (3 of 4 broadenings caught → D18) and proved hex outside `tokens.css` still trips the ratchet as the *only* failure, isolated so line counts stayed flat. Two limits recorded rather than oversold: the tokens-file guard is line-based (**D17** — PLAN.md's own tokens example is a single line, so UI-020 must author one declaration per line or the guard is vacuous) and the scope test cannot catch a `TOKENS_PATH.parent` broadening (**D18**) |
| UI-020 | `main.css` + import order + legacy demoted + `01-settings` 3-tier tokens | **done** | `01a27f6` | **First task in the epic that AUTHORS CSS rather than moving it.** Three new files, 310 insertions, **not one `.html` byte touched** — `main.css` is linked nowhere (verified over HTTP on all nine pages), so this task has zero visual effect by construction and needed no browser check. `main.css` = `@layer legacy, settings, generic, elements, objects, components, utilities` + 11 `@import`s, and **12 code lines total**; the nine `99-legacy/*` come first into the lowest layer, which is what "legacy demoted" means. They are `@import`ed rather than `<link>`ed because **a plain `<link>` is unlayered and unlayered normal declarations outrank every `@layer`** — linking would invert the cascade this file exists to establish. `tokens.css` = 19 Tier 1 primitives, one declaration per line (D17 — PLAN.md's own example is a single line and would satisfy the guard vacuously); `01-settings/theme.css` = 31 Tier 2 roles, **every one a `var()`, zero raw hex**. Reviewers verified 0 dangling refs and **0 unconsumed primitives** — 5 were deleted (`--font-urdu`, `--radius-1`, `--space-1/-4/-7`) to keep that invariant exact, so the space/radius scales have deliberate documented gaps. Palette is 1:1 with `static/theme.css`'s 19 distinct values, nothing invented. **`unsanctioned_hex` flat at 429** — the ratchet UI-020a built did its job on the first try: a hex quoted in a *Tier 2 comment* took it 429 → 430 and was caught before commit. **First review FAILED it** on three false claims in the comments (§12.12): "linked by 8 pages" (it is **7** — D9), "names do NOT collide" (**three do**: `--font-display`/`--font-body`/`--font-data`, and they must NOT be renamed because `blueprint.css`/`taqseem.css` read them), and D19 missing the token half → **D20**. All three measured and fixed, then re-reviewed PASS |
| UI-030 | `04-objects/shell.css` + `config/nav.json` | **done** | `704a76a` | **First Sprint 3 task, and still no page touched** — `main.css` is linked by none of the nine (verified live), so this is the last task that is safe by construction. `shell.css` = 6 rules, 23 declarations, `.o-shell__*`, **layout only**: not one background, border, colour, font or shadow, and zero raw hex. **The naming is the finding.** `PLAN.md`:125 gives `o-*` to layout objects, and taking the prefix is what makes the file safe rather than tidy: measured per name, **every one of the mockup's shell class names is already taken, in two different ways.** `.brand` (all nine legacy files), `.main` (blueprint + index) and `.spacer` (blueprint) are in `layer(legacy)`, so a rule of that name here would silently override nine pages at once — D21 at nine-page scale. `.app`, `.top` and `.nav` are in `static/theme.css` and no legacy file, which is the opposite case: unlayered, so they *beat* `layer(objects)` and then vanish when a page drops the link. `o-shell__*` appears nowhere in the project. **D21's height half is CLOSED as unnecessary, not deferred again**: `html, body { height: 100% }` never landed, because `.o-shell` uses `height: 100vh`, which resolves against the viewport and needs no percentage chain from `body` — the design target carries both (`mockup:16` and `:58`) and only the second is load-bearing, so **`print.html`'s Ctrl+P risk is not taken at all**. `--weight-medium` (500) did not land either, against this board's own prediction: a layout-only file cannot consume a weight, so it goes with `05-components/nav.css`. **Both stale predictions were corrected where they were written** (`tokens.css`, `reset.css`), per the rule UI-021 wrote after making the same mistake. `config/nav.json` = 4 groups / 11 items, **measured, not invented**: all 11 icon ids verified in `icons.svg` (an exact set match), all 7 urls 200, all 5 screen values real `showScreen` targets, groups and order 1:1 with the mockup, labels from the live pages. Found **D24** (`nav.mypapers` referenced by markup but in neither i18n table; `syllabus` is an orphaned screen) and **D25** (four nav destinations have no address at all, which is half of why the nav drifted into three versions). One layout omission is stated in the file that omits it: the `<760px` collapse hides the nav, and the control that gives it back is a Sprint 4 component. **TWO reviews FAILED this, and both were right.** The first caught three claims asserted instead of counted: "the mockup's nav is 12 items" (it is **11**, contradicted by the same paragraph two lines up), D25's "missing *exactly* the items that cannot be linked" (false — the 5-item pages also drop `/slo.html` and `/taqseem.html`, which have URLs, so that half **is** arbitrary drift), and `main.css` calling all four names a legacy collision. The second review then caught **two new false claims introduced by those very fixes**: the corrected `main.css` split put `.spacer` in the theme.css-only bucket when `blueprint.css:243` styles it — contradicting this task's own `shell.css`:21 — and the new `<760px` note said "six of the nine legacy files" when it is **five files, six blocks** (`index.css` has two), the same read-the-adjacent-number error as "12 items". Both fixed and re-verified independently. The reviewer also proved the two prose-only edits changed no CSS: `tokens.css` and `reset.css` are byte-identical to `HEAD` with comments stripped |
| UI-031a | Migrate `slo.html` onto the new tree via `static/css/pages/slo.css` | **done** | `f2493a0` | **The first page in the epic whose stylesheet is the new tree, and the first time any browser has parsed `@layer`.** Three files: `pages/slo.css` (new, two `@import`s and no rules of its own), `main.css` (the nine legacy `@import`s removed), `slo.html` (three `<link>`s → two: `app.css` + the entry file; **not one other byte** — 22/22 frozen attrs, 48/48 class attrs, `<script>` bodies identical, −53 bytes exactly the link swap). **D19 resolved by moving the legacy import out of `main.css`**, because the documented shape was measured to break the page: nine files import alphabetically, `taqseem.css` is last and won **15 selectors** off `slo` including `:root`, `.app-sidebar` and `.app-nav a`, and every value it brought reads a `static/theme.css` token the task unlinks — an unpainted sidebar via a file belonging to another page (**D20 by the back door**, on the one page whose own 17 tokens are all local literals). `main.css` keeps the layer order and stays the single source of the cascade; `CLAUDE.md` §11's link rule changed with it. **Verified in headless Edge 150 over CDP**, not by reasoning: layer statement with all seven names in order, every import in its declared layer, `99-legacy/slo.css` in `layer(legacy)`, sidebar `rgb(22,41,74)`, `static/theme.css`'s tokens all `<EMPTY>`, icons 17px, and the other eight pages byte-identical. **Four review rounds FAILED it and all three real failures were the same shape — a number asserted rather than measured**: D26's contrast computed against an assumed backdrop (real figure **1.70:1 → 3.04:1, an improvement**, not a regression); the change taxonomy naming only theme.css bleed and missing **D21 firing live**; and four inherited line numbers (`forms.css:58` is the input/select rule and cannot match a button). All three are recorded in the files as failed drafts. An aggregate delta count was **removed rather than corrected** — two measurements disagreed on property set, so the files give affected *elements* per rule, re-derivable with a grep. **A hex quoted in a comment took `unsanctioned_hex` 429 → 431 and `--write` pinned it** before `--check` ran; fixed with `git checkout` on the baseline, then re-pinned — **re-pin only after `--check` passes against HEAD**. Ships with three visible changes, all Sprint 4's to fix: **D26** subtitle at 3.04:1, **D27** ghost `<a>` vs `<button>` in two colours, **D28** cards tighter. Also found **D29**: two files are named `theme.css` and the Network panel shows only the basename — it caused a false alarm at Irfan's browser check, which he stopped on rather than assuming |
| UI-031b | Migrate `slo-health.html` onto the new tree via `pages/slo-health.css` | **done** | `8e9b839` | **Second live page, and the first repetition of UI-031a's mechanism — it needed no new decision, which was the thing being tested.** Three files: `pages/slo-health.css` (new, 49 lines, two `@import`s and no rules of its own), `slo-health.html` (three `<link>`s → two: `app.css` + the entry file), `BASELINE.json` (re-pinned). **−53 bytes, all of it the link block**; frozen inventory 19/19, class attrs 74/74, all three `<script>` bodies identical. **D20 does not hit this page, measured not assumed**: the legacy file declares 17 custom properties and reads 15, and the read-but-not-declared set is **empty**, so unlinking `/static/theme.css` orphans nothing; zero of its names collide with `01-settings/tokens.css` + `01-settings/theme.css`. Two are declared and never read (`--ok-bg`, `--primary-hover`) — pre-existing, left alone. **Cascade re-verified on this page in headless Edge 150 over CDP**, by recursing the CSSOM rather than reading the top level: the layer statement carries all seven names in order from `main.css`, all ten `@import`s sit in their declared layer, `99-legacy/slo-health.css` is in `layer(legacy)`, and every stylesheet plus four `woff2` returned 200. **The white slab is not a `slo` quirk — it is a `static/theme.css` fact.** The same `.brand` white background sat inside this page's navy sidebar too, and is gone; screenshots before/after. Also from theme.css: the subtitle's uppercase and letter-spacing. **Two `layer(elements)` element selectors reached past class rules and neither was named in UI-031a's review**: `a { color: inherit }` took all six inactive nav links from the legacy grey to white, so active/inactive now differ only by background and left border; and `small { }` took the sidebar subtitle's size and colour off `.brand small`. **Contrast measured against real backdrops, both directions**: subtitle **2.20:1 → 3.04:1** (an improvement, because the *before* backdrop was the white slab and not the navy — the same trap D26's first draft fell into), still under AA and still D26's to fix; `th` **5.81:1 → 4.60:1**, a fall that clears AA by 0.1. Tables took the design target's metrics (`tables.css` `th`/`td` padding to 24px horizontal, `vertical-align` top → middle on 38 cells, and `tr:last-child td` dropping the rule under the final row on 10 cells — deliberate, `tables.css`:63-66). Cards tighter again: D28, unchanged. **1463 element × property deltas over a property set of 36 fixed before measuring**, on a render first proven deterministic (two before-snapshots, 191 elements, 0 drift). **Stated limit: four cards were in empty states and the `.cov-*` blocks never rendered**, so that part of the page is unmeasured. **Process gaps, recorded rather than papered over: the independent review agent (§12 step 5) did not run on this task, and Irfan committed it himself** — so this row is the implementer's evidence only, not a reviewed result. The commit message says "theme.css link → main.css import"; the link actually goes to the per-page entry file, which is the whole of D19 — message only, code is correct |
| UI-031b | Migrate `library.html` onto the new tree via `pages/library.css` · `landing` HELD | **done** | `5291bdc` | **Third live page, and the biggest legacy file migrated so far.** `library.html`'s three `<link>`s → two (`app.css` + the entry file), **−53 bytes, all of it the link block**; frozen inventory 93/93, class attrs 94/94, **inline `style=""` 48/48**, all three `<script>` bodies identical. **Measurements, short form:** 2811 element × property deltas over a property set of 35 fixed before measuring, across 659 aligned elements; the page's one big visible change is its **44 `<label>`s** taking `03-elements/forms.css`'s bare `label` rule — 42 change size, 12 go weight 500→600, 2 change colour only — at **15.59:1/16.00:1 → 4.76:1, which still clears AA** (4.5 for normal text at these sizes; a review round called this a failure and was wrong, adjudicated by a later round). **D14 confirmed inert, measured not assumed**: `--text:` is declared nowhere in the project, so `/static/theme.css` never supplied it either — 5 of the 6 `.pg-btn` change colour by ordinary inheritance and the 6th is `.pg-btn.active`, which takes white by class and never reaches the invalid `var()`. D20 does not hit the page. The `static/theme.css` white slab in the sidebar is gone for the **third time in three pages** — treat it as a `theme.css` fact, not a per-page quirk. **EXPECTED ON THE BROWSER CHECK, so nothing here is a surprise: D21/D27/D28 — cards visibly tighter (`reset.css` zeroes legacy class margins), nav links all white (`typography.css`'s `a { color: inherit }` beats `.app-nav a`, so active/inactive now differ only by background and left border), and buttons re-fonted by `forms.css`.** **FOUR review rounds: three FAILED, and not one of them touched the CSS** — every finding was a measurement written into the entry file's comment that could not be re-derived from a stylesheet (a wrong page-count noun, an unreproducible aggregate, a miscounted property set, a wrong line citation, "six `.pg-btn`" when it was five, a font-size pair copied from a reviewer, and a settle-render claim taken from a review agent **without re-measuring it — it did not reproduce**). Irfan's call ended it: **strip the numbers from the comment entirely** and keep them here, where the board keeps every other task's and where a reviewer can check them. The entry file went 141 → 39 lines and passed on the next round. Two process facts worth carrying: writing a colour literal into that comment took `unsanctioned_hex` **429 → 430** and the ratchet caught it pre-review (third time in this epic); and a claim from a review agent is not evidence — verify it like any other number |
| UI-031c | `taqseem` onto the new tree — **ATTEMPTED, MEASURED, HELD** | **held** | `2085867` | **Not a migration: a measurement that changed the decision.** The D20 half worked. The orphan-token check gave **26** read-but-never-declared (the board said 20), of which Tier 2 already declares **3** under the deliberate `--font-*` collision, so the entry file carries a **23-token compatibility block** in `@layer legacy` — every one mapping 1:1 onto an existing Tier 2 role, **no value change, no literal, `unsanctioned_hex` flat at 429**, zero declared-name collisions with `01-settings/`. Verified live: all 23 resolve non-empty after the swap, `--color-canvas`/`--color-surface`/`--color-text`/`--color-border`/`--color-action` go `<EMPTY>` → real values, and the three font names resolve from Tier 2 exactly as its header predicts. **What stopped it is the half no grep can see: 20 `static/theme.css` rules match this page's elements and 16 are redeclared nowhere in its own legacy file** — the entire `.btn`/`.card`/`.pagehead` set plus two `input`/`:focus` rules. Swapped and measured: the 3 buttons fell to **UA default** (`rgb(240,240,240)`, 2px border, 1px 6px padding, `display:block`, weight 400, radius 0) and `.card`'s shadow went to `none`. **`taqseem` is the only page this hits** — own-file `.btn`/`.card` rule counts are `slo` 5/3, `slo-health` 2/3, `library` 13/3, `blueprint` 10/4, **`taqseem` 0/0** — which is precisely why three clean pages made it look routine. Measurement quality, for the record: render proven deterministic first (**70 elements, two before-snapshots, 0 drift**), **306 element × property deltas over a property set of 35 fixed before measuring**, across **67 aligned elements** (70 → 69 is the removed `<link>`, itself an element). The swap itself was clean and is the shape the eventual task will take: **−53 bytes, all of it the link block**, frozen attrs 15/15, class attrs 44/44, inline `style=""` 4/4, all three `<script>` bodies identical. **Then reverted on Irfan's call** — `taqseem.html` is at HEAD and the entry file was parked at **`docs/ui/parked-taqseem.css`**, following the `landing` precedent exactly: under `static/css/` its 61 lines counted toward `shared_css_lines` with no page loading them, and `docs/` is outside the metric, so **`shared_css_lines` is back at 1616 and `BASELINE.json` was not re-pinned**. One process note: an invariant check first reported the `<script>` bodies as differing; that was `git show` being decoded with the locale codec against a UTF-8 file (em-dash in the title, Urdu in the scripts), not a real change — `git diff` said 1 insertion / 2 deletions throughout. Decode explicitly before comparing bytes. **Not reviewed by an independent agent** — it never reached that gate, because the task was withdrawn rather than finished |
| UI-021 | `02-generic` reset + fonts · `03-elements` typography / forms / tables | **done** | `8ecb3cc` | **Sprint 2 complete.** Five new files (449 lines), `main.css`'s five `@import`s uncommented **in place** — the order is the cascade — and **not one `.html` byte touched**, so zero visual effect again by construction. `shared_css_lines` 573 → **1178**, the only metric that moved; `unsanctioned_hex` **flat at 429** and the new tree carries **zero raw hex**. Tier 1 gained 15 primitives (7 type steps, 2 weights, 2 leadings, `--font-serif`, `--font-nastaliq`) and Tier 2 13 roles, verified **0 dangling refs and 0 unconsumed primitives** — UI-020's invariant held exactly. **It predicted it would add space steps and did NOT**: control padding (9px 11px) and cell padding (10px/11px) are optical one-offs, left literal, and the one structural value needed was already `--space-inset`; the stale prediction was corrected in `tokens.css` rather than left to mislead. All nine `woff2` resolved on disk against `../../fonts/` — `url()` resolves against the *stylesheet*, the first such path in the tree. **The finding that outlives the task is D21: a reset in this tree is not neutral.** `layer(generic)`/`layer(elements)` outrank `layer(legacy)`, so a bare element selector beats a legacy *class* rule; the design target's `* { padding: 0 }` would have flattened `index.css:267`'s RTL list indentation, so the universal padding kill was **not** ported, the margin reset is targeted at block text elements, and `img` gets `max-width` without the usual `display:block` (it would break the inline `.icon` sprite). Each omission is stated in the file that omits it. **D22** parks the button appearance reset for UI-041 — `border:none; background:none; color:inherit` from `layer(elements)` would flatten `.btn-primary`/`.btn-ghost` across eight legacy files. **The first review FAILED it and was right**: the file shipped `font: inherit`, which is not a synonym for `font-family: inherit` — the shorthand also resets size, weight, style, variant, stretch and line-height, dragging every legacy button to 15px/400 and stripping the 600/700 weights they set by class. Fixed to the longhand, then re-reviewed PASS. Review also corrected three counts that were guessed rather than measured (`html, body {height:100%}` is 7 of 9 files, **not 8 — `print.css` is the second exception and it is the Ctrl+P page**; "exactly two pseudo-element rules" was a wrong generalisation from a `::before`-only grep; a Tier 2 comment's "20 unconsumed roles" mixed two different sets). **D23** records that `--font-mono`/`--font-data` name "IBM Plex Mono", which **no `@font-face` declares and no woff2 in the repo provides** — pre-existing since before this epic, always falling through to `ui-monospace`; the fix is a font-asset decision for Irfan, not CSS |
---

## Live metrics — these may only go DOWN

Verified at `ui-baseline`, real app pages only (`mockup-modern.html` is a reference, not a page):

**Enforced since UI-002.** `python scripts/css_baseline.py --check` fails on any increase,
and `tests/test_css_architecture.py` fails the suite. Numbers below are no longer maintained
by hand — run the script.

| metric | key | `ui-baseline` | now (UI-031b, `library`) | target |
|---|---|---:|---:|---:|
| `<style>` blocks in HTML | `style_blocks` | 9 | **0** ✅ | 0 |
| CSS lines in HTML | `css_lines_in_html` | 2133 | **0** ✅ | 0 |
| page CSS + `99-legacy/` | `total_css_lines` | 2133 | **2115** | 0 |
| inline `style=""` attrs | `inline_style_attrs` | 466 | 466 | ~171 (one-offs only) |
| ⤷ excluding `display:` toggles | `inline_style_non_display` | 385 | 385 | ~171 — **this is the one to drive down** |
| hardcoded hex in `<style>` | `hardcoded_hex` | 324 | **0** ✅ | 0 — *but see below, this one lies* |
| hardcoded hex in `style=""` | `hardcoded_hex_inline` | 76 | 76 | 0 |
| **hex outside `tokens.css`** | `unsanctioned_hex` | 429 | **429** | 0 — **the honest one** |
| `99-legacy/` lines | `legacy_css_lines` | 0 | **2115** | *informational* — peaks ~2133 after Sprint 1 |
| hex in every `.css` | `stylesheet_hex` | 29 | **372** | *informational* |
| hex in `01-settings/tokens.css` | `token_hex` | 0 | **19** | *informational* — the sanctioned palette |
| hex anywhere | `total_hardcoded_hex` | 429 | **448** | *informational* since UI-020a |
| `app.css` + `theme.css` + new tree | `shared_css_lines` | 269 | **1616** | *informational* — grows through Sprints 2–4 |

**Five are deliberately NOT ratcheted** (`legacy_css_lines`, `stylesheet_hex`, `token_hex`,
`total_hardcoded_hex`, `shared_css_lines`). `99-legacy/` climbs to ~2133 during Sprint 1 and
the new tree grows in Sprint 2, so a downward ratchet on any of them would fail its own
migration.

**`unsanctioned_hex` is the ratcheted hex metric, not `total_hardcoded_hex`** — changed in
UI-020a. This table used to give `total_hardcoded_hex` a target of **0** and call it "the
honest one". That target was never reachable: ADR-001 and `CLAUDE.md` §11 both state the
invariant as *"a raw hex outside `01-settings/tokens.css` is a CI failure"*, so the end state
has hex **inside** that one file, legitimately — Tier 1 primitives are raw values by
definition. Ratcheting a metric that counted them made UI-020 literally unwritable: authoring
the palette at all pushed the number up and failed the suite. So `token_hex` counts that one
file, `unsanctioned_hex` is everything else and is the ratcheted one, and it **baselines at
429** — the same figure `total_hardcoded_hex` carried through all nine Sprint 1 tasks, because
`tokens.css` did not exist yet. It is a continuation, not a reset. `total_hardcoded_hex` keeps
its exact definition and is still reported every run, so every number in the task log below
stays comparable.

**The new hiding place, stated plainly.** Hex laundered *into* `tokens.css` leaves
`unsanctioned_hex` while nothing was repaid. *Authoring* new primitives is ratchet-neutral
(`total_hardcoded_hex` and `token_hex` rise together, `unsanctioned_hex` flat) — that is the
point of the exemption. *Relocating* existing hex into `tokens.css` drops `unsanctioned_hex`
with nothing deleted from the tree, and that is arithmetically identical to the legitimate
Sprint 5–6 burn-down, so no automated check can separate them. `test_tokens_file_holds_only_token_hex`
narrows it — every hex in that file must sit on a custom-property declaration — but the check
is **line-based**, so a one-line or minified rule defeats it (D17), and it cannot judge whether
a primitive is needed. Like `shared_css_lines`, this one is on the reviewer: **watch `token_hex`
move; a large jump wants a reason.**

**`hardcoded_hex` falling is NOT progress during Sprint 1.** It counts only `<style>` blocks
in HTML, so extraction moves hex out of it and into `stylesheet_hex` untouched — UI-010..016
took it 324 → 298 → 273 → 268 → 254 → 211 → 210 → 148 → 87 → **0** without removing one colour. It reaches 0 when the last page is
extracted, with
all 324 still in `99-legacy/`. **`unsanctioned_hex` is the number that has to reach 0**;
it is flat at 429 through extraction and only moves when a hex is genuinely deleted.

**`total_css_lines` drops exactly 2 per page extracted, not 0.** `css_lines_in_html` counts
the `<style>` and `</style>` lines; a `.css` file has neither. Expect **2133 → 2115** across
Sprint 1. A drop larger than 2 on an extraction task means CSS was deleted rather than moved.

**Watch `shared_css_lines` when reviewing.** `total_css_lines` covers page CSS + `99-legacy/`
only, so moving a page's `<style>` block into `app.css` instead of `99-legacy/` passes the
ratchet with three metrics falling and nothing removed. A page shrinking while
`shared_css_lines` jumps by the same amount is debt relocated, not repaid — no automated
check can tell the difference, so that one is on the reviewer.

**Green baseline at `ui-baseline`:** `pytest -q` = 874 passed · `ruff check .` clean.
**Green at UI-002:** `pytest -q` = 900 passed (874 + 26) · `ruff check .` clean ·
`css_baseline.py --check` exit 0.
**Green at UI-011:** `pytest -q` = **902 passed** · `ruff check .` clean ·
`css_baseline.py --check` exit 0.
**Green at UI-012:** `pytest -q` = **902 passed** · `ruff check .` clean ·
`css_baseline.py --check` exit 0. Gates run twice — by the implementing session and
independently by the review agent.
**Green at UI-013:** `pytest -q` = **902 passed** · `ruff check .` clean ·
`css_baseline.py --check` exit 0. Both runs independent (implementer + review agent).
Note `ruff` is not on PATH in this environment — use `python -m ruff check .`.
**Green at UI-014:** `pytest -q` = **902 passed** · `python -m ruff check .` clean ·
`css_baseline.py --check` exit 0. Both runs independent.
**Green at UI-015:** `pytest -q` = **902 passed** · `python -m ruff check .` clean ·
`css_baseline.py --check` exit 0. Both runs independent (implementer + review agent).
**Green at UI-016:** `pytest -q` = **902 passed** · `python -m ruff check .` clean ·
`css_baseline.py --check` exit 0. Both runs independent; the reviewer also served the app
and confirmed the new stylesheet returns 200, not 404.
**Green at UI-017a / UI-017:** `pytest -q` = **902 passed** · `python -m ruff check .` clean ·
`css_baseline.py --check` exit 0, both gates run at each of the two commits. UI-017a was
built and verified on a clean `HEAD` (extraction stashed) so its own commit is green in
isolation, not only in combination.
**Green at UI-018a / UI-018:** `pytest -q` = **902 passed** · `python -m ruff check .` clean ·
`css_baseline.py --check` exit 0. Same clean-`HEAD` treatment for UI-018a. Reviewer served the
app: `/print.html` 200 with 0 `<style>` blocks, 2 stylesheets, no `theme.css`, and
`print.css` 200 at 20209 bytes.
**Green at UI-020a:** `pytest -q` = **905 passed, 1 skipped** · `python -m ruff check .` clean ·
`black --check` clean on both changed files · `css_baseline.py --check` exit 0. Gates run three
times: implementer, plus two independent review agents (the first FAILED the task). The single
skip is `test_tokens_file_holds_only_token_hex`, vacuous only until `tokens.css` exists — it
un-skips in UI-020. Project-wide `black --check .` reports ~95 unformatted files, but that is
**pre-existing at clean `HEAD`** (verified by stashing: identical count), not introduced here.
**Green at UI-020:** `pytest -q` = **906 passed, 0 skipped** · `python -m ruff check .` clean ·
`css_baseline.py --check` exit 0. The skip is gone because `test_tokens_file_holds_only_token_hex`
un-skips once `tokens.css` exists — expect 906/0 from here, not 905/1. Gates run three times
(implementer + two independent review agents; the first FAILED the task). **Not verified: `@layer`
parsing in a real browser** — the Chrome extension was not connected for the implementer or either
reviewer, and all three said so rather than claiming it. No risk today (`main.css` is linked
nowhere); close it in the pre-Sprint-3 browser session.
**Green at UI-021:** `pytest -q` = **906 passed, 0 skipped** · `python -m ruff check .` clean ·
`css_baseline.py --check` exit 0, with `shared_css_lines` re-pinned to **1178** in-task. Gates
run three times (implementer + two independent review agents; the first FAILED the task on
`font: inherit`). **`@layer` is still unparsed by any browser** — the Chrome extension was
connected for none of the five agents across UI-020 and UI-021, all five said so rather than
claiming it, and the browser session did not close it either: no page loads `main.css`, so
there was nothing to parse. Retired instead by version (Edge/Chrome 150 vs ADR-001's floor of
99) and finally by UI-031. See the browser-session block above.
**Green at UI-030:** `pytest -q` = **906 passed, 0 skipped** · `python -m ruff check .` clean ·
`css_baseline.py --check` exit 0 · `unsanctioned_hex` flat at **429** · `shared_css_lines`
1178 → **1351**, re-pinned in-task. One full-suite run reported `test_upload_replaces_previous_data`
failing on `sqlite3.OperationalError: disk I/O error`; re-run in isolation it passes 15/15, and
the final full run is clean — a flake, recorded rather than quietly dropped. Gates run five
times (implementer three, review agent twice
— it **FAILED the task twice**, and both times the second round of numbers was checkable in one
grep). No `.html` modified, so the frozen inventory diff is empty by construction. Still no
browser: `@layer` remains unparsed by anything, harmless here because no page links `main.css`,
and the `height:100vh` / independent-scroll reasoning is specification-level, not observed.
**UI-031 is the first task that can see any of it.**
**Green at UI-031a:** `pytest -q` = **906 passed, 0 skipped** · `python -m ruff check .` clean ·
`css_baseline.py --check` exit 0 · **all eight ratcheted metrics flat**, `unsanctioned_hex`
**429** · `shared_css_lines` 1351 → **1527**, the only mover, re-pinned in-task. Gates run
**nine times** (implementer four, review agent five — it **FAILED the task four times**).
**`@layer` is no longer unverified**: parsed in headless Edge 150 through CDP, layer statement
and per-file layer assignment both read off the live document. The Chrome extension was not
connected — Edge headless plus Node's built-in `WebSocket` over CDP was used instead, and
screenshots came from `msedge --headless=new --screenshot`. The school PC remains unchecked
(blocked item 1). **Two process hazards recorded rather than dropped:** the review agent ran
`Get-Process msedge | Stop-Process -Force`, which kills *every* Edge on the machine including
Irfan's — scope cleanup to your own `--user-data-dir` or PIDs. And `C:` reached **226 MB free**
during this task, causing a real `OSError: [Errno 28] No space left on device` mid-`pytest`;
**UI-030's recorded `sqlite3.OperationalError: disk I/O error` "flake" was almost certainly
this, not a flake.** Freeing headless-browser profiles recovered ~2.3 GB.
**Green at UI-031b:** `pytest -q` = **906 passed, 0 skipped** · `python -m ruff check .` clean ·
`css_baseline.py --check` exit 0 · **all eight ratcheted metrics flat**, `unsanctioned_hex`
**429** · `shared_css_lines` 1527 → **1576** (the 49-line entry file), the only mover, re-pinned
in-task and **only after `--check` passed against HEAD's baseline** — the ordering UI-031a had
to learn the hard way; the re-pin diff touches that one key and nothing else. All nine pages
still return 200, with `slo` and `slo-health` now on two `<link>`s. **Gates run once, by the
implementer only — the independent review agent did NOT run on this task**, so unlike every
task above it these numbers have not been reproduced by a second party. Headless Edge 150 was
driven through CDP on its own `--user-data-dir`, and the processes were checked as gone by
matching that directory rather than by killing every `msedge` on the machine (the UI-031a
hazard). Disk stayed at ~11 GB free, so UI-031a's `Errno 28` conditions did not recur.
**Green at UI-031b (`library`):** `pytest -q` = **906 passed, 0 skipped** · `python -m ruff
check .` clean · `css_baseline.py --check` exit 0 · **all eight ratcheted metrics flat**,
`unsanctioned_hex` **429** · `shared_css_lines` 1576 → **1616** (the 40-line entry file), the
only mover, re-pinned in-task after `--check` passed against HEAD's baseline. Gates run
**eight times** — implementer four, review agent four, and **the review agent FAILED this task
three times**. It also mutation-tested the hex ratchet (a colour literal in the comment →
429 → 430, exit 1, then restored byte-identical). `landing` is not in these numbers: it was
built and green, then held, and its entry file was moved to `docs/ui/parked-landing.css` so
that 55 lines of CSS no page loads could not be absorbed into this task's re-pin.
**Green after `taqseem` was held and reverted:** `pytest -q` = **906 passed, 0 skipped** ·
`python -m ruff check .` clean · `css_baseline.py --check` exit 0 · **all eight ratcheted
metrics flat**, `unsanctioned_hex` **429**, `shared_css_lines` **flat at 1616** — the entry
file is parked in `docs/`, which the metric does not count, so nothing unlinked is hiding in
it. **BASELINE.json was deliberately NOT re-pinned**: nothing shipped, and pinning lines of
CSS that no page loads is exactly the laundering this board warns about. `taqseem.html` is byte-identical to HEAD. Headless Edge 150 was driven on
its own `--user-data-dir` (the UI-031a hazard), and the dev server was a local
`uvicorn app.main:app` on `127.0.0.1:8000`.
**Re-pin `BASELINE.json` (`css_baseline.py --write`) as part of every extraction task** —
UI-010..012 did, UI-013 missed it and had to fix it in the close commit; UI-014 and UI-015
did it in-task. Skipping it leaves the next task comparing against numbers two tasks stale.

---

## Decisions locked (do not relitigate)

| Decision | Choice | When |
|---|---|---|
| Palette | **Modern** — indigo `#4f46e5` + teal `#0ea5a4` | 2026-07-28 |
| Design target | `static/mockup-modern.html` | 2026-07-28 |
| Shell fidelity | **Full mockup shell** — `.app` grid + topbar + grouped nav | 2026-07-28 |
| Architecture | ITCSS order + BEM naming + small utility layer | ADR-001 |
| Load mechanism | one `<link>` → `main.css`, `@import` inside | ADR-001 |
| `@layer` | **adopted** — floor is Edge/Chrome 99 (Mar 2022), Edge auto-updates | 2026-07-28 |
| Review gate | every task passes an **independent review agent** before Irfan sees it | 2026-07-28 |
| Dirty tree | committed as-is, tagged `ui-baseline` | 2026-07-28 |
| Branching | one epic branch, one commit per task | 2026-07-28 |
| Push | **never by Claude** — Irfan, via GitHub Desktop | standing |

---

## Blocked / needs Irfan

| # | Item | Needed for |
|---|---|---|
| 1 | **School PC's Edge version** (`edge://version`, needs ≥ 99). Dev PC is 150, but ADR-001 accepts `@layer`'s hard-fail risk purely on Edge auto-updating and the school machines have never been checked. Irfan said 2026-07-31 he would do it later | **UI-031** — the first task that puts `main.css` on a page. Not blocking UI-030, which touches no page |
| 2 | **`--font-mono` names "IBM Plex Mono" and no such font exists in the repo** (D23). Either commit the two woff2 (~80KB, licence-checked) or drop the family and let `ui-monospace` be the declared intent. Font-asset call, not CSS | a small asset task, or **UI-064** with D13. Nothing is blocked meanwhile — it has silently fallen back since before this epic |

---

## How to start a session

1. Read this file. Take **only** the task named under NEXT TASK.
2. Read `CLAUDE.md` §11–12 (rules) and the one page/file that task owns. Nothing else.
3. State a 2-line plan. Wait for go-ahead.
4. Implement — anchored `Edit`s only, inside the declared scope.
5. Self-check all gates, then **spawn the independent review agent**. It can FAIL you;
   on FAIL, fix and re-review. Never hand over a failed or unreviewed task.
6. On PASS, hand to Irfan with a **specific click-list** for his browser check.
7. Only after Irfan says OK: update this file (task log, metrics, NEXT TASK), then commit.
   Never push.
8. Emit a copy-pasteable prompt for the next task's fresh session.
