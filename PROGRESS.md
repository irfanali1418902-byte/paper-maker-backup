# PaperMaker — Fix / Feature Log

## 2026-08-20 — `index` joins `.sidenav__panel`, and layer order nearly took the mobile view

**`legacy_css_lines` 1,865 → 1,869**, `unsanctioned_hex` 357 → **356**. Eight rule lines out of
`99-legacy/index.css`, twelve comment lines in, so the informational line count went **up by
four** — recorded rather than dressed up. The dedup is real: ten `.app-sidebar` declarations
now come from `05-components/nav.css` instead of being index's own.

**7 element × property deltas, all on one `<div>`, none of them painting.** 0 on the other
seven pages, drift 0, ratchet clean.

### The board said this page was the cheap one. It was not.

The handoff called `index` "panel aur name bilkul yaksan — seedha adopt, 0 deltas." The eleven
panel declarations **are** identical, including the two that go through tokens — `--navy` and
`--color-sidebar-bg` are both the same navy, `#fff` and `--color-sidebar-fg-on` both the same
white. Adopting anyway would have broken the page below 760px.

`99-legacy/index.css` hid the sidebar in a `@media (max-width: 760px)` block, where `index`
swaps to a topbar plus a bottom tab bar. `.sidenav__panel` declares `display: flex` in
`layer(components)`, and `main.css:42` orders `legacy` before `components`. **Layer order is
resolved before specificity and before media queries**, so the component wins at every width
and the full navy rail returns on top of the mobile chrome. This is rule 2 of the epic's three,
for the fourth time.

**`index` is the only page this catches.** The other five reshape `.app-sidebar` into a
horizontal strip at that breakpoint instead of hiding it, so the four pages already on this
component never met it.

The media query moved up into `pages/index.css`, which imports `main.css` first and then opens
its own `@layer components` block — at an equal `0,1,0` it is simply later in the same layer.
Same move as the RTL rail on 2026-08-19, for the same reason.

**No probe in this repo could see it.** `css_type_probe.mjs` and `css_selector_probe.mjs` are
both fixed at 1280×900. Measured with a throwaway viewport override: `display` computes `none`
at 720px before **and** after, box 0×0 both times. RTL was re-checked too — LTR left 3px /
right 0, RTL left 0 / right 3px, unchanged.

### What was left behind, deliberately

| | verdict |
|---|---|
| `.app-sidebar` → `.sidenav__panel` | adopted, 11/11 declarations identical |
| `.brand .name` → `.sidenav__brand-name` | adopted, `700` = `--font-weight-heading`, 15.5px/1.15 already the component's |
| `.sidebar-foot` → `.sidenav__foot` | adopted; the 7 deltas are here |
| `.brand` → `.sidenav__brand` | **skipped** — index's brand is a flex row round a 40px logo; the component is padding only, and adding the flex to it would put text and `<small>` side by side on the four pages already on it |
| `.brand .tag` → `.sidenav__brand-sub` | **skipped** — `nav.css` calls `10.5px` and the pale blue dead, which is true of the `<small>` on four pages but not of index's `<div class="tag">`, where both are live at `0,2,0` |

**The 7 deltas are on `<div.sidebar-foot>` and every one is invisible.** `font-size`,
`line-height` and `color` are inherited values that `.box` — index's foot text is wrapped, the
other four pages' is not — re-declares on itself and therefore wins as a direct declaration.
The other four are `border-*-color` following `color`, on a div measured at `border-style: none`
and 0px on all four sides. `.box` itself measured byte-identical before and after, and the
foot's box stayed 248×84.

## 2026-08-19 — `taqseem` and `index` join `.sidenav`, and the white-links bug is finally gone

**`legacy_css_lines` 1,880 → 1,865**, `unsanctioned_hex` 364 → **357**. Six rules out; 17 nav
links re-classed. **567 deltas on `taqseem` (159) and `index` (408), 0 on the other six.**

**The bug that was raised on 2026-08-14 and stayed open is closed.** `03-elements/typography.css`'s
`a { color: inherit }` sits in `layer(elements)` and beat the legacy nav colour, so every
migrated page's nav links turned white and inherited from the sidebar. Four pages were fixed by
adopting `.sidenav`; `taqseem` and `index` kept the defect for five days. Measured before:
white on both. After: `rgb(198,210,232)` on all three, identical to `slo`.

`index`'s nav also changed shape, which Irfan approved knowing it: its links were full-bleed
rows (`padding: 12px 22px`, no radius) and are now the group's inset pills (`10px 12px`,
radius 8px, 3px rail).

### The part no gate could have caught

**Adopting `.sidenav__link` broke the Urdu rail on `index`, and nothing in the suite would have
reported it.** The component sets `border-left: 3px` in `layer(components)`; the two
`[dir="rtl"]` rules that flip the rail to the trailing edge were in `layer(legacy)` and lost.
**Measured: both borders came out at 3px** — the rail on the wrong side and on both sides at
once. The rules moved to `pages/index.css`, and both directions were then verified: LTR
left 3px / right 0, RTL left 0 / right 3px with the rail at `rgb(91,141,239)`.

**`css_selector_probe.mjs` gained `--attr=<selector>:<name>=<value>` to see it at all.** No probe
in this repo has ever set `dir="rtl"`, so the entire RTL block — nav rail, table alignment, the
legend dot — has been unmeasured for the whole epic. It is measurable now.

## 2026-08-19 — the sidebar shell becomes a component on four pages, at zero deltas

**`legacy_css_lines` 1,916 → 1,880**, `unsanctioned_hex` 375 → **364**. Twenty rules — five
selectors × `bank`, `library`, `slo`, `slo-health` — into `05-components/nav.css` as
`.sidenav__panel`, `.sidenav__brand`, `.sidenav__brand-name`, `.sidenav__brand-sub` and
`.sidenav__foot`. **0 element × property deltas on all eight pages**, drift 0, ruff clean.

Zero deltas despite twenty rules moving *and* four HTML files changing, because the values were
measured identical on all four pages before anything was written — `.app-sidebar`, `.brand`,
`.brand .name`, `.brand small` and `.sidebar-foot`, every declaration.

**The `.brand` ban was about the NAME, not the element, and that distinction is what made this
possible.** `UI-047b` recorded that `.brand` may not have a component because it is live on all
nine pages — true of a rule *named* `.brand` in `layer(components)`, which would repaint all
nine the moment they link `main.css`. A differently-named rule that markup opts into reaches
only the pages that ask, which is exactly what `.sidenav` did on 2026-08-14. The ban stands as
written; it just never covered this route.

**Two declarations were left behind because they were already dead.** `.brand small` also
declared `font-size: 10.5px` and `color: #9DB0D0`; the subtitle measures **11.5px in slate** on
all four pages. Carrying them up a layer would have resurrected them — the `.filter-bar` mistake
of 2026-08-15, now caught before it shipped rather than after.

**One token was promoted, on the same basis as the four before it.** `--navy-400` /
`--color-sidebar-fg-muted` is the sidebar footer's own colour; `theme.css`:120 already records
that the sidebar foregrounds are "the legacy sidebar's own values, promoted rather than
invented". This is the fifth. Ratchet stays flat: `token_hex` +1, `total_hardcoded_hex` +1.

**`.app-nav`'s `padding: 0 10px` was NOT taken.** Putting it on `.sidenav` reaches `blueprint`
too, which runs the `.o-shell` grid — a different question, deliberately not answered here.

## 2026-08-19 — the drain's scope is decided, and `.btn-ghost` stops being two buttons

**Two things, and the first governs everything after it.**

### The drain does not go to zero — Irfan's decision

Recorded in `ROADMAP.md`, not only here, because `UI-060..063` says "drain to zero" and a
session reading that would do 3–5 sessions of work that was deliberately cut. Measured at
`legacy_css_lines` 1,949, of 1,594 rule-block lines:

| | lines | | |
|---|---:|---|---|
| page-only, no component possible | **999** | 63% | **skipped** |
| shared but drifted | **495** | 31% | do it |
| shared and identical | **100** | 6% | do it |

Draining the 999 means moving rules from `99-legacy/<page>.css` to `pages/<page>.css`, and
**both are already one file per page** — it removes no duplication, no CSS and no lookup step.
`legacy_css_lines` would reach ~0 while the line count stayed put. **Target is ~1,200–1,400 and
a coherent app, not 0.**

### `.btn-ghost` — one class, two buttons, five pages

**`legacy_css_lines` 1,949 → 1,916**, `unsanctioned_hex` 381 → **375**. Ten rules out; the
legacy name is joined to every `.btn--ghost` selector in `btn.css` rather than given its own
rule, so the two cannot drift again.

It rendered **two ways**: an outline button on `bank`, `blueprint` and `library` (white fill,
grey border, dark text) and a **tinted** one on `slo` and `slo-health` (light-blue fill, blue
text). Irfan chose the outline — the variant the component already defines, the same argument
that settled `.btn-primary`.

**369 element × property deltas on five pages, 0 on the other three.** All of them on
`.btn-ghost`, its SVG children, or the `.filter-bar` siblings that re-laid out when the button
went 40px → 36px. `slo` also gained `cursor: pointer`, which its rule never had.

**And `btn.css`'s header had been false for three days.** It still opened "PREPARED, NOT LIVE.
Nothing on any page carries these classes yet" — untrue since `.btn-primary` landed on
2026-08-16. Corrected where it was written.

## 2026-08-16 — the drain probe learns to warm the page, and 38 rules are saved from deletion

**No CSS changed and `legacy_css_lines` did not move.** This step removed nothing, and the
reason it was worth doing is that it stopped 38 rules from being removed wrongly.

`css_drain_probe.mjs` gains `--query=`, `--warm=` and `--wait=`. Without them it loads the bare
page, and most of these pages render their real content from JS after an API call — so it was
measuring a DOM no user ever sees.

| page | cold | warmed | rules that were NOT dead |
|---|---:|---:|---:|
| `print` — `?paper_id=9ade2655…` | 78 dead | **58** | **19** |
| `taqseem` — Pre Year 1 / Mathematics selected | 27 dead | **8** | **19** |

**Both would have read as deletable and both are load-bearing.** `print` renders nothing at all
without a paper id; `taqseem` shows an empty board until a class and subject with a plan are
chosen, and `Pre Year 1` / `Mathematics` is the only pair that has one.

**A longer wait alone changes nothing** — `bank`, `library` and `blueprint` return identical
counts at 1,200ms and 3,500ms, and a spot check confirms their main content is already
rendered (459, 24 and 1 elements). What those three still report as dead belongs to *other*
states — modals, bulk-import results, empty states — each of which needs its own warm-up.

**And after warming, `print` and `taqseem` have ZERO unreachable rules left.** Every remaining
zero is a class something in the page can build. **The drain's supply of dead rules is
exhausted**: across all nine files, ~47 were genuinely dead and all of them are already gone.
Everything still in `99-legacy/*.css` is either live, or live in a state no probe has entered.

The warm-up prints its own element delta and says so when it added nothing, because a warm-up
that silently failed produces exactly the same zeros as no warm-up at all.

## 2026-08-16 — the `js-only` bucket, resolved without a browser: 9 of 216 can never match

**`legacy_css_lines` 1,962 → 1,949**, 0 deltas on all eight pages, ratchet OK, ruff clean.

**The 204 `js-only` candidates were not 204 dead rules. Nine of them are.** A `js-only` zero
means only that the class was absent from the DOM when the probe ran. The decisive test needs
no browser: `99-legacy/<page>.css` is imported by **exactly one page**, so if a class token
appears nowhere in that page's HTML — not in markup, not in a template string, not in a
`classList` call — nothing can ever put it in the DOM.

**207 of 216 are reachable.** Something in the page can build them, so they must be verified by
injecting markup, not by deleting on a zero. **The drain's supply of dead rules is now
essentially exhausted**: 845 rules surveyed, ~47 genuinely dead across all nine files.

**A naive substring grep disagreed with the token match on three of the nine, and the token
match was right every time.** `sh` had 68 "hits" in `blueprint.html` — all inside words like
`should`; there is no class named `sh`. `code` had 4 in `slo-health.html` — all inside
`slo-codes`, `slo_code` and `cov-code`. `spacer` had 1 — inside `o-shell__spacer`. This is the
hyphen/substring trap already on the project's list, and it would have kept three deletable
rules alive rather than killing a live one, which is the safe direction to be wrong in.

**What went:** `.opt-radio-label` (`bank`), `.pagehead .spacer` / `.sec .sh` / `.sec .sh b` /
`.qrow` / `.qrow .qtxt` (`blueprint`), `.bloom-bar` (`index`), `td.code` / `.tag.err`
(`slo-health`).

**And 12 lines of my own noise went with them.** Both drain passes wrote a per-file
`/* dead rules dropped: … */` marker listing what had been removed — a changelog inside a
stylesheet, which is the same mistake `8ca7ed8` had just corrected at a larger scale. The first
pass's nine deletions netted **one** line because of it. Git history and this file already
record what was dropped.

## 2026-08-16 — the drain runs on all eight files: 38 dead rules out, and `legacy_css_lines` goes under 2,000

**2,008 → 1,962**, 46 lines. **0 element × property deltas on all eight pages**, drift 0,
ratchet OK, ruff clean. `css_drain_probe.mjs` had only ever been taken all the way through on
`slo`; this runs it on the other eight and acts on the result.

**The survey's "391 dead rules" is not 391. Measured end to end, it is about 67, and the
deletable-with-confidence set is 38.** The probe reported **339 zero-delta candidates** across
the eight pages. Bucketing each one against why a zero can be a lie:

| bucket | n | why the zero means nothing |
|---|---:|---|
| `js-only` | 204 | the class exists only inside a `<script>` template string |
| `state` | 78 | `:hover` / `:focus`, and `[open]` / `[dir="rtl"]` / `[data-open]` |
| `at-rule` | 15 | `@page`, `@font-face`, `:root` |
| **genuinely dead** | **42** | present in static markup, no state, no media |

**`@page` was in the candidate list and deleting it would have broken every printed paper.**
The drain probe runs in screen media, where `@page` does nothing, so it reads 0. `print.css`:1-2
records that this page's margin has been broken before. Attribute state was the same trap:
`[open]` is a `<details>` the probe never opens and `[dir="rtl"]` is the Urdu toggle switched on
— both read 0 at rest, neither is dead.

**Two of the filters were wrong on the first pass and were caught by measurement, not review.**
Reading `class="…"` out of the raw HTML counted template strings as static markup, which marked
`blueprint`'s `.topic-check-row` deletable — a rule measured live earlier the same day. Stripping
`<script>` blocks first moved 199 candidates down to 55. The `absent` bucket then failed too:
`.qrow` had 8 hits and `td.code` 4, so every `absent` row was dropped from the delete set rather
than trusted.

**What went, and it is mostly the new tree already doing the job:** `*`, `a`, `body`,
`html, body` on most pages (reset.css and typography.css), `select` / `table` / `th` on
`slo-health` (forms.css, tables.css), `.page-head h1` on three pages (typography's `h1` beats it),
`.pagehead` ×3 on `blueprint` (card.css owns them since UI-040), and `.icon` on `landing` plus
`.app-nav a svg` on `index` — **both of which the previous handoff had flagged as "probably
already dead, not measured". They are, and now it is measured.**

## 2026-08-16 — `.btn-primary` unifies on the locked indigo; the app had two primary blues

**`legacy_css_lines` 2,032 → 2,008**, `unsanctioned_hex` 385 → **382**. Nine rules out of
`bank`, `blueprint` and `library`, into `05-components/btn.css` beside the `.btn--*` set.

**The three files declared this rule byte-identically and rendered two different blues.**
`bank` and `library` painted `rgb(46,90,172)`; `blueprint` painted `rgb(79,70,229)`, because
`pages/blueprint.css`:82 maps `--brand` onto `--color-action` while the other two kept the
legacy literal. `tokens.css`:10 records the palette as **locked 2026-07-28 — Modern, indigo
action**, so blueprint was the one that was right and the other two had simply never been
remapped.

**Irfan asked for the better option rather than the safer one, and the deciding argument was
not the palette lock.** `btn.css` already ships `.btn--primary` reading `--color-action`.
Building `.btn-primary` at the old blue would have put **two primary blues inside one component
layer** — the exact defect this drain keeps uncovering — and would have forced re-pointing
`--color-action` itself later, which reaches blueprint's `--brand` and the focus ring. On
indigo, a future re-class to `class="btn btn--primary"` is a no-op.

**9 background changes, all intended** — 3 on `bank`, 6 on `library`, 0 on `blueprint`.

**Two unintended deltas, kept deliberately.** `cursor: pointer → not-allowed` on the two
disabled upload buttons and their SVG children: the legacy `.btn-primary:disabled` declared
`not-allowed` and it was **dead in `layer(legacy)`**, losing to a `button { cursor: pointer }`
higher up. In `layer(components)` it applies. Unlike `.filter-bar`'s resurrection this one is
correct behaviour and matches the `.btn--primary:disabled` already in `btn.css`, so it stays.

**`--radius-control` was nearly a silent regression.** The token is 11px; all three pages
measure 10px. The component keeps the literal.

**`.btn-ghost` was NOT taken.** Five pages, four different looks — `bank`, `blueprint`,
`library`, `slo` and `slo-health` disagree on background, border, radius, padding, font-size
and height. That is four decisions, not a refactor.

## 2026-08-16 — modal chrome: six rules out of eighteen, and the other twelve are named

**`legacy_css_lines` 2,036 → 2,032.** Three selectors × two files —
`.modal-backdrop.open`, `.modal-header`, `.modal-footer` — into
`05-components/modal.css`. **0 element × property deltas on all eight pages**, drift 0,
`unsanctioned_hex` back to 385, ruff clean.

**This app has THREE modal systems, not one**, and that is the first thing the enumeration
returned:

| | pages | classes |
|---|---|---|
| 1 | `bank`, `print` | `.modal-backdrop` `.modal-header` `.modal-footer` `.btn-cancel` `.btn-save` |
| 2 | `index`, `library` | `.modal-overlay` `.modal-head` `.modal-title` `.modal-foot`/`.modal-body` |
| 3 | `taqseem` | `.modal h3` `.modal-actions` |

`.modal` itself names four different boxes and `.modal-close` four different buttons. Only
system 1's shared chrome was taken.

**The audit said eighteen rules agreed across `bank` and `print`. Six were takeable.**

- **`.btn-cancel` / `.btn-save` and their three states — left, and NOT only because of the
  values.** They look identical and are not: `--radius-btn` is **10px on bank, 8px on print**,
  and the two `--bg` greys differ, so the shared `border-radius` and the cancel hover resolve
  differently. They are also **buttons**, and `.btn-primary` (3 files), `.btn-ghost` (5),
  `.btn-danger` / `.btn-edit` (2) are duplicated too. They belong in one button task beside
  `05-components/btn.css`, where the radius is decided once instead of three times.
- **`.modal-header h3` — left, because two of its three declarations are already dead.**
  `margin: 0` is done by `02-generic/reset.css` in `layer(generic)`; `font-size: 16px` loses to
  `03-elements/typography.css`'s `h3` in `layer(elements)` — **measured 14px on both pages, not
  16**. Copying it up would have resurrected the 16px. What survives is one colour, and the
  navy heading has no Tier 2 role; inventing one with a single consumer is what
  `tokens.css`:145 warns against.
- `.modal-backdrop` itself differs — `bank` pads 16px, `print` pads 0.

**Everything here is `display: none` at rest, so `css_type_probe` cannot see any of it.**
Verified by adding `.open` to the backdrop and reading the chrome on both pages before and
after: byte-identical. The gate's 0 only says the rest of the app did not move.

**`unsanctioned_hex` went 385 → 387 again, from two hex in a comment.** Twelfth time in this
epic. Fixed the same way, with `rgb()`.

## 2026-08-16 — `.type-checks` joins `field.css`, and the decision it was scheduled on turned out not to exist

**`legacy_css_lines` 2,042 → 2,036.** Four rules — the container and its label, from
`99-legacy/bank.css` and `blueprint.css`. **0 element × property deltas on all eight pages**,
drift 0, `unsanctioned_hex` flat at 385, ruff clean.

**The task was opened to settle a decision, and enumeration dissolved it.** The board entry said
`.type-checks`' checkbox is `rgb(46,90,172)` at 16px on `bank` and `rgb(79,70,229)` at 15px on
`blueprint`, so componentising it required choosing a blue. Irfan chose bank's. **That choice
does not apply**, because `blueprint`'s `.type-checks input[type="checkbox"]` is **dead**:
`blueprint.css`:109's `.topic-check-row input[type="checkbox"]` has equal specificity, sits
later in the same file, and wins. The colour never came from the rule being discussed.

**And componentising it anyway would have made the page worse, not better.**
`.topic-check-row` renders at two sites on `blueprint` — inside `.type-checks`
(`blueprint.html`:581) and in the topics list (`:607`). A `.type-checks` rule in
`layer(components)` beats `.topic-check-row` **only inside `.type-checks`**, so the page would
have ended up with 16px blue boxes next to 15px indigo ones. The checkbox rule was left in both
legacy files. Unifying the two checkbox styles is a real task; it is not this one.

**Three more declarations were dropped for the reason `.filter-bar` taught yesterday.**
`.type-checks label`'s `font-size: 13.5px`, `font-weight: 500` and `color: var(--ink)` all lose
to `03-elements/forms.css`'s bare `label` in `layer(elements)` — measured 12px / 600 /
`rgb(71,85,105)` on both pages. Copying them into `layer(components)` would have resurrected
them. The component carries only the five that are actually alive.

**`blueprint`'s `.type-checks` is JS-rendered and the gate cannot see it.** It is built inside
the section template at `blueprint.html`:642, so it does not exist on a fresh load — one probe
run found it and the next did not, which is what exposed this. It was verified instead by
**injecting the exact markup `renderSection()` produces** and reading the computed values
before and after: byte-identical, including both checkbox sites. **A 0 from `css_type_probe` is
not coverage of this element.**

## 2026-08-15 — `.field-row` + `.filter-bar` become a component, at zero deltas

**`legacy_css_lines` 2,054 → 2,042.** Nineteen rules out of `99-legacy`'s `bank`, `blueprint`,
`index` and `library`; `05-components/field.css` replaces them, the name `main.css` had held
commented-out since UI-042 was scoped. **0 element × property deltas on all eight pages,
drift 0.** `unsanctioned_hex` flat at 385 — the file declares no colour at all.

The net line count is 12 rather than 19 because each deletion left a one-line signpost naming
the component that took it, the same as the `.status-bar` commit.

**It did NOT come out at zero on the first run — it came out at 75, and the reason is worth
more than the rules.** Two of the legacy declarations had been **dead since the migration**:
`.filter-bar label { font-size: 11.5px }` and `.filter-bar select { padding: 8px 11px }` sit in
`layer(legacy)` and lose to `03-elements/forms.css` in `layer(elements)`, because layer order is
decided before specificity. Those labels have rendered at 12px, and those selects at 9px 11px,
for as long as the pages have been migrated. **Copying the declarations into a component file
moved them up to `layer(components)` and brought them back to life** — 11 labels shrank and 9
selects lost a pixel of padding.

Irfan's call: **match what is live.** Both declarations are dropped from the component, which
now carries only `margin-top: 0` on the label and `min-height: 38px` on the control — the one
thing the filter bar genuinely adds over the default. Re-measured at 0.

**A third value was never a rule at all.** `.filter-bar input` measured `padding: 8px 11px`
where `select` measured `9px`, which looked like a cascade puzzle. It is an **inline style** on
`library.html`:186, and inline beats every layer. That input was never reading the rule.

**Measured identical before anything was written**, which is why the `.field-row` half was
uneventful: `flex`/`gap 14px` and `flex: 1 1 0%` on all four pages, `.filter-bar` and its `> div`
identical on both. `index` alone stacks at `gap: 14px` below 760px against the other three at
`10px`; the component took the majority and index's own value moved to `pages/index.css`.

**`.type-checks` was in the original scope and was left out.** Its rule text is byte-identical
in `bank` and `blueprint`, and its checkbox is `rgb(46,90,172)` at 16px on one and
`rgb(79,70,229)` at 15px on the other — `blueprint` maps the legacy token names onto the new
tree's roles in its entry file. That is a decision about which blue, not a refactor.

## 2026-08-15 — `.status-bar` becomes a component, and it turns out the app had two status palettes

**`legacy_css_lines` 2,075 → 2,054.** Twelve rules, 21 lines, out of `99-legacy/bank.css`,
`blueprint.css` and `library.css`; `05-components/status.css` replaces them.
`unsanctioned_hex` flat at 385, ruff clean, and **0 element × property deltas on all eight
pages, drift 0**.

**The rule text agreed across all three files. The resolved colour did not.** That is the
finding, and it is why the "byte-identical, therefore free" reading of the duplication survey
is not safe. Measured by injecting the state class and reading the computed pair:

| | before | after |
|---|---|---|
| `bank`, `library` — ok | `rgb(46,125,91)` on `rgb(230,244,236)` | `rgb(22,101,52)` on `rgb(230,244,236)` |
| `blueprint` — ok | `rgb(22,163,74)` on `rgb(220,252,231)` | `rgb(22,101,52)` on `rgb(230,244,236)` |

`blueprint` was on the traffic-light palette because `pages/blueprint.css`:99-104 maps its
legacy `--green`/`--green-bg` onto `--color-success`/`-soft`; `bank` and `library` carry the
raw legacy hex. **Two palettes, live, on three pages** — the same shape as the navy vs white
sidebar settled on 2026-08-13, and nothing on the board recorded it.

**Both palettes failed AA, and the new one failed harder.** At 13.5px/500 the pairs measured
3.00 / 3.95 / 2.86 (traffic-light) and 4.41 / 4.64 / 3.37 (legacy) against a 4.5:1 requirement.
Irfan chose to keep the legacy tint and darken the ink: **6.29 / 4.64 / 6.12, all passing.**
`err` was left exactly as it was, because it already passed.

**Geometry did not move at all** — `10px 14px`, `9px`, 13.5px/500, `margin-top: 14px`,
identical on all three pages before and after. Four of those stay literal in the component:
9px has no radius token, 10px/14px are not on the space scale, and 500 has no weight
primitive. Same call `nav.css` made for its 14px and 8px.

**Two gates are blind here and the numbers should be read accordingly.** `.status-bar` is
`display: none` at rest and `.ok`/`.err`/`.warn` are set by inline JS
(`el.className = 'status-bar ' + type`, eight sites), so `css_type_probe` returns 0 whether
this file is right or wrong, and a drain probe would report all nine state rules as dead.
The colour claim above comes from a probe that injects the class; the 0 only says the rest of
the app did not move.

**And `unsanctioned_hex` went 385 → 389 on the first run, from six raw hex inside a comment.**
Trap #3, for the eleventh time in this epic. Fixed by writing the comparison as `rgb()`.

## 2026-08-15 — `blueprint` and `taqseem` had their subtitle beside the title, not under it

A wrapper `<div>` around `h1` + `p` in both pages' `.pagehead`. **2 element × property
deltas in the whole app**, both intended: the `.pagehead` box grows 26.4 → 49.0px on
`blueprint` and 42.1 → 68.5px on `taqseem`. The other six pages measured **0, drift 0**.

**It was found by enumerating a different task.** The plan was to re-class the four
`.page-head` pages onto `card.css`'s `.pagehead` component and delete 11 legacy rules.
Reading the component against the markup first — before writing anything — showed why that
would have broken them: `.pagehead` is `display: flex`, and the mockup
(`mockup-modern.html`:279) puts an inner `<div>` inside it. `blueprint` and `taqseem` were
migrated to the class **without that div**, so their `h1` and `p` became flex items and sat
side by side. The four `.page-head` pages were unaffected only because their class is still
`display: block`. A re-class would have given all four the same defect.

**And one number the board carried was wrong.** The re-class was costed as "h1 22px → 24px on
four pages". Measured: **all four are already 24px.** `03-elements/typography.css` sets bare
`h1` at 24px in `layer(elements)`, which beats `layer(legacy)`'s `.page-head h1 { 22px }` —
that legacy declaration is already dead. The real cost of a re-class is layout, plus the `p`
colour (`rgb(91,102,120)` → `rgb(100,116,139)`) and a new `max-width: 620px`.

`.page-head` → `.pagehead` is **not done** and is no longer the cheap win it was scheduled as.

## 2026-08-15 — the sidebar can scroll on all nine pages; the two-day-old hole is closed

`.app-sidebar { overflow-y: auto }` added to `pages/bank.css`, `library.css`, `slo.css`,
`slo-health.css` and `taqseem.css` — one declaration each, in `layer(components)`. The legacy
shell sets `height: 100vh` with no `overflow`, so a nav taller than the viewport spilled out of
the painted navy box instead of scrolling. **Found by Irfan in the browser on 2026-08-13** on
`index`, fixed page-scoped there the same day, and recorded as still open on five pages rather
than fixed by a drive-by. This closes it.

**The enumeration moved the scope from six pages to five, both ways.** `blueprint` was on the
board's list and does not have the defect — its only `.app-sidebar` rule is inside
`@media (max-width: 760px)`, and at desktop it runs the new `.o-shell` grid, which already sets
`overflow: auto`. `print` was not on the list and was already fixed: `99-legacy/print.css`:45
carries `overflow-y: auto` with its own comment.

**There is no shared home for this and that is by design, not an oversight.**
`04-objects/shell.css`'s header forbids a `.app-sidebar` rule outright — a rule under that name
in `layer(objects)` would take over the brand/shell block on all nine pages the moment they
link `main.css` (the D21 failure mode). So it is five page-scoped copies, and they go away when
these pages move onto `.o-shell`.

**No probe can verify this and the gate was not run for it.** `css_type_probe`'s viewport is
900px and `overflow` is not a captured property, so it returns 0 either way. Ratchet OK
(`shared_css_lines` 3,064 → 3,117, `unsanctioned_hex` flat at 385), ruff clean.
**Verified by Irfan in the browser instead** — incognito, zoomed to ~200% so the 209–294px navs
exceed the viewport, on the pages themselves.

## 2026-08-14 — the drain: 12 dead rules leave four legacy files, and `legacy_css_lines` moves for the second time in this epic

**`legacy_css_lines` 2,105 → 2,075. Thirty lines, 0 deltas on all eight pages.** This is the
payoff for everything above it today — three commits that only added, followed by the one that
takes away.

**What was deleted:** `.app-nav a`, `.app-nav a:hover` and `.app-nav a.active` from
`99-legacy/bank.css`, `library.css`, `slo-health.css` and `slo.css`. **Twelve rules, thirty
lines** — the blocks are 8 lines in `bank`/`library` and 7 in `slo`/`slo-health`, which is why
the estimate of "~24" written an hour earlier was wrong: it counted rules and the file counts
lines.

**`.app-nav` itself STAYS on all four**, and that is not an oversight. It carries
`display: flex`, `flex-direction: column`, `gap: 2px` and `padding: 0 10px`, and **no component
covers the last of those** — `.sidenav` took the column and the gap in `778f65a`, deliberately,
but the 10px side padding has no home. The `@media (max-width: 760px)` `.app-nav` rules stay too,
for the reason `shell.css` gives: that breakpoint hides the nav and the control that brings it
back does not exist yet.

**0 element × property deltas on all eight pages, drift 0** — `slo`, `slo-health`, `library`,
`taqseem`, `blueprint`, `bank`, `landing`, `index`. `unsanctioned_hex` 401 → 385: sixteen raw hex
went with the rules, four per file.

**The `:hover` half is NOT probe-verified, and that is stated rather than glossed.** The probe
hovers nothing, so `.app-nav a:hover`'s deletion returns 0 whether or not the component replaces
it. What was done instead is a value-for-value read: `--color-sidebar-hover` resolves through
`--overlay-white-07` to `rgba(255,255,255,0.07)` and `--color-sidebar-fg-on` through `--white` to
`#ffffff`, which is exactly what the deleted rule declared. The `.active` half **is** measured,
because the current item is in that state at rest. **A hover check belongs to a person with a
mouse.**

**What this does to the epic's own number.** The first move was `slo`'s ten dead rules on
2026-08-13 (2,115 → 2,105). This is the second, and it is a different kind: those ten were dead
already, while these twelve were **load-bearing until this morning** and were made dead on
purpose. That is the 454, not the 391 — the first of the load-bearing rules in this epic to be
given a home and then removed.

## 2026-08-14 — `library`, `slo-health` and `slo` adopt `.sidenav`; all four pages of the clean group are on the component

**Same edit three times, measured one page at a time: `library` 57, `slo-health` 85, `slo` 85.**
Every delta is one of the two changes already decided on `bank` — the nav links returning from
white to `rgb(198,210,232)`, and the `<nav>` gaining `--color-sidebar-bg`, navy painted on navy.
**No new kind of delta appeared on any of the three, and no geometry moved at all** — not a
font-size, radius, gap, border-width or height. That is the proof that `778f65a` seated the
component exactly on the legacy values; if it had not, these three runs are where it would have
shown.

**The counts scale with link count and nothing else.** `library` has 5 nav links, `slo` and
`slo-health` have 7. Four inactive links × 14 (`color` plus three `currentColor` borders on the
`<a>`, and `color` plus four on each of its `svg` and `use`) + 1 for the `<nav>` = 57; six
inactive × 14 + 1 = 85. The current page's link measured 0 deltas on all three.

**`taqseem`, `blueprint`, `bank`, `landing` and `index` all measured 0**, drift 0 on all eight.
Ratchet OK, ruff clean, suite 890.

**Where this leaves the four.** `bank`, `library`, `slo-health` and `slo` now carry both
`.app-nav` and `.sidenav` on the `<nav>`, and both `active` and `sidenav__link--active` on the
current link. **Nothing has been deleted from `99-legacy/*.css` yet and `legacy_css_lines` has
not moved** — the three dead rules per page (`.app-nav a`, `:hover`, `.active`, 12 in total) come
out as their own step, so a re-class and a deletion are never in the same commit.

**`taqseem` and `index` still render white nav links**, because nothing has reached them. Two
looks in one app again, deliberately and temporarily — the same shape as the navy split before it
was settled.

## 2026-08-14 — `bank` adopts `.sidenav`, and it turns out six live pages have had white nav links since they migrated

**The re-class was predicted at 0 deltas and measured 57. The prediction was wrong in the
useful direction: 56 of the 57 are an existing defect being undone.**

**`bank.html` only.** `<nav class="app-nav">` → `<nav class="app-nav sidenav">`, and the five
`<a>` get `sidenav__link` (the current one also `sidenav__link--active`, keeping its legacy
`active`). `.app-sidebar`, `.brand` and `.sidebar-foot` are untouched — no component can carry
them. **Nothing is deleted from `99-legacy/bank.css` yet**; proving the re-class is quiet comes
first, and it did not come back quiet.

**What moved: four nav links from `rgb(255,255,255)` to `rgb(198,210,232)`** — plus their `svg`
and `use` children inheriting it, and the border colours that resolve to `currentColor`. One more
delta is the `<nav>` gaining `--color-sidebar-bg`, navy painted on navy, invisible. The current
page's link measured **0 deltas**: it was white before and stays white.

**The cause, measured rather than reasoned.** `03-elements/typography.css`:50 declares
`a { color: inherit }` in `layer(elements)`. Layer order is decided before specificity, so it
beats `99-legacy/*.css`'s `.app-nav a { color: #C6D2E8 }` in `layer(legacy)` no matter what the
selectors weigh, and the link inherits `.app-sidebar`'s white. `.sidenav__link` sits in
`layer(components)`, above `elements`, which is why re-classing restores the legacy intent.

**This is live on six pages right now, not one.** Read out of the before-snapshot: `slo`,
`slo-health`, `library`, `taqseem`, `bank` and `index` render **every** nav link white, current
and not. `blueprint` is the only page showing the intended split, because it is the only one
already on `.sidenav`. So on those six the current page is distinguished by its background tint
and rail alone, and the colour that was supposed to carry it has been absent since each page
migrated.

**It was recorded and never decided.** `pages/bank.css`:124 says it in one line — *"Nav links go
white and the canvas changes tint, both from the new tree"* — filed as an expected consequence of
`UI-047e` on 2026-08-10. **Irfan decided it today: accept the legacy colour.** The remaining three
re-classes carry the same change, and `taqseem` and `index` keep white until something reaches
them.

**Gates:** 0 deltas on the other seven pages, drift 0 on all eight, ratchet OK, ruff clean, suite
890. Irfan compared `bank` against `blueprint` in the browser.

## 2026-08-14 — `nav.css` moves to the four pages' values, so the re-class can be free

**Nothing shipped to a teacher today. One component file changed, and `blueprint` moved 104
element × property deltas to make four other pages able to adopt it at zero.**

**The board's plan for this step was wrong, and the enumeration is what said so.** `HANDOFF.md`
described re-classing `bank`, `library`, `slo` and `slo-health` onto `.sidenav` as "36 rules out,
colour unchanged". The 36 is right — the nine desktop shell rules really are byte-identical
across those four files, re-verified line by line — but **`.sidenav` is a home for only three of
those nine**. `.app-nav a`, `:hover` and `.active` have component equivalents. `.app-sidebar`'s
own box, `.app-nav`'s column, `.brand` ×3 and `.sidebar-foot` have none: the first lives inside
`.o-shell`, which is a whole-page grid these four have no topbar for, and `.brand` was
deliberately denied a component in `UI-047b` because it is live on all nine pages. **So the step
yields 12 rules, not 36.**

**And the three that do have a home were not free either.** `.sidenav__link` read `--text-body`
(15px), `--radius-control` (11px) and an 11px gap, against the legacy 14px / 8px / 10px, and it
carried no `border-left` at all. Re-classing at those values would have moved type and corners on
four pages a teacher uses daily. **Irfan's call: bring the component to their values instead**,
so `blueprint` — one page, already in the probe's list — absorbs the whole change.

**What changed in `05-components/nav.css`:** `.sidenav__link` gap 11 → 10px, `font-size`
`--text-body` → 14px, `border-radius` `--radius-control` → 8px, a `3px solid transparent`
`border-left` added, `margin-bottom` removed. `.sidenav` gains `display:flex` + `flex-direction`
+ `gap: 2px` — the 2px moves from the item to the container because the four pages already stack
their links with `.app-nav { gap: 2px }` in `layer(legacy)`, and an item margin would have made
the spacing 4px on every one of them. `.sidenav__link--active` drops `font-weight` (only
`taqseem` bolds the current item, and it is in the other group) and its rail moves from an inset
`box-shadow` to `border-left-color` — **a shadow cannot reserve space, and the transparent border
is what stops the current page's label from shifting.**

**14px and 8px are literals, deliberately.** Neither has a Tier 2 role and neither gets one:
`--text-body` is 15px, `--radius-control` is 11px, and `--font-size-4` is already spoken for by
`--text-heading-3`. Giving these roles means three new names with one consumer each — the way
`tokens.css`:145 says that file rots. Same policy as the 34px avatar in the same file and
`shell.css`'s 248px sidebar.

**Measured: 0 deltas on seven pages, 104 on `blueprint`, drift 0 everywhere.** All 104 are
accounted for — 30 font-size/line-height across 5 links and their `svg`/`use`, 20 radius corners,
15 `border-left`, 12 gap, 12 `min-height`/`min-width` `0px` → `auto` (the flex-item default, no
visual effect), 5 `margin-bottom`, 5 `height`, 3 `font-weight`, 1 `display`, 1 `box-shadow`. The
active item was checked on its own: the rail is the same `rgb(91,141,239)` at the same 3px on the
same edge, and background and text colour did not move at all.

**Irfan opened `blueprint` and `bank` side by side and the two sidebars now look the same** —
which is the whole point of the step and the one thing no probe could report. Ratchet OK, ruff
clean, suite 890.

**Nothing is re-classed yet.** That is the next step, one page at a time, and it should now
measure zero.

## 2026-08-13 — Sprint 6 starts: the first legacy lines come out, and all nine files are surveyed

**`legacy_css_lines` 2,115 → 2,105.** `PLAN.md` §3 says *"Progress is literally measurable as
lines remaining in `99-legacy/`"*, and that number had not moved once in the life of this epic
until now. Everything before today added; `theme.css`'s deletion removed a shared file but left
legacy untouched. These are the first lines of the actual debt to go.

**A tool had to exist first.** The migrations asked *"what does this page lose when
`static/theme.css` is unlinked?"* — `css_orphans.py` answered that by diffing against
`theme.css`, which was deleted the same morning. The drain asks the opposite: *"this legacy rule
is still here — if I delete it, does anything move?"* Nothing measured that.
`scripts/css_drain_probe.mjs` does: it deletes each rule from the CSSOM, re-snapshots, counts
deltas, and puts it back. One page load, and **no file is ever edited**, so an interrupted run
cannot leave a half-drained stylesheet on disk.

**`slo.css`: 45 rules → 35, 91 lines → 81.** Ten went. Each was checked against the tree rather
than trusted to the probe's zero — `*` and `a` by hand, because `box-sizing` and
`text-decoration` are not among the 44 properties the probe measures. Three of the ten
(`.status-error`, `.status-updated`, `.status-added`) turned out to be dead in a stronger
sense: they appear nowhere in the repo outside `slo.css` itself. 0 deltas on all eight probed
pages, ratchet 32, suite 890, and Irfan checked the page.

**Nine of its nineteen zeros were NOT deleted, and that is the important half.** Four are
`:hover`/`:disabled` and match nothing at rest; four are `.pill` variants that exist only inside
JS template strings at `slo.html`:170 and :228; one is an `@media` block outside the probe's
viewport. Deleting on the first number would have repeated the taqseem-chips mistake exactly.

**Then all nine files were surveyed: 845 rules, 391 at zero deltas, 454 load-bearing.** The
survey table is in `docs/ui/ROADMAP.md`. Two files could not be measured at first — `landing`
and `bank` — because both contain rules with a `transition`, and the probe's restore check was
snapshotting mid-animation. The guard was right to refuse; the fix freezes transitions before
the baseline, which is safe because `transition-*` is not among the measured properties, and
was verified by re-running `taqseem` to the same numbers.

**What the survey actually says about the remaining work.** 391 is not the deletable count —
`slo` is the only file taken through, and half its zeros were blind spots, so the genuinely
deletable share is nearer **a quarter of 845**. The **454 load-bearing rules are the real
job**, and none of them has been rehomed yet: even `slo` still has all 26 of its. Deleting a
dead rule takes minutes; giving a live one a home is a decision every time.

## 2026-08-13 — the DOCX/PDF export is deleted: 630 lines nothing called, and a LibreOffice dependency

**Not part of the UI-ARCH epic.** That epic sanctioned exactly one backend change (UI-003);
this comes out of the dead-code audit and is committed on its own for that reason.

**Removed:** `app/api/export.py` (49 lines), `app/services/export_service.py` (362),
`tests/test_export_service.py` (210), `python-docx` from `requirements.txt`, the
`PdfConversionFailed` exception, and the router's import and registration in `app/main.py`.

**Why, and "unused" is the weaker half of it.** `/api/paper/{id}/export.docx` and `.pdf` had
no caller anywhere — not in any page, not in `apiClient.js`, not in a test. The stronger half
is that the PDF path **shells out to LibreOffice** (`soffice`) as a subprocess: a feature
needing third-party software installed on the school PC, that nothing invoked, and that would
have failed the moment anyone did invoke it on a machine without it. The code was also
untouched since the initial commit of 2026-07-06 — one commit in the whole life of the repo.

**And the cost is real, not zero.** This was the app's only DOCX export, so a teacher wanting
an editable paper file no longer has a path to one. It was working, tested code — 16 tests
passed — not rot. What makes it a removal rather than a loss is the standing position that
printing is the browser's Ctrl+P via `print.html`; DOCX was never in the workflow.

**Verified:** app imports, suite **890 passed** (906 minus the 16 that tested the deleted
service), 69 API paths remain, and the only `export` among them is `/api/questions/slo-export`
— the SLO spreadsheet, unrelated.

**A note for whoever checks this next.** The first verification reported "0 API routes" and
looked like the deletion had unregistered everything. It had not. In this FastAPI version
`app.routes` holds included routers as `_IncludedRouter` objects with no `.path`, so filtering
on `.path` finds only the four docs endpoints and the two mounts. Count the `_IncludedRouter`
entries (14 now, 15 before) or read `app.openapi()["paths"]`.

**Still open from the same audit:** `/api/syllabus-topics` has no caller anywhere and has not
been decided. `blueprint-presets/{id}` and `library/question-types` are called by tests only.

---

## 2026-08-13 — static/theme.css is deleted. The file this epic was written about is gone

**Sprint 6, UI-ARCH epic — `UI-064` part 1.** Full board: `docs/ui/STATUS.md`.

`PLAN.md` §1 opens with: *"The app has a design system (`theme.css`, 213 lines) that ~90% of
the styling bypasses."* That file is now removed. **212 lines deleted, 0 element × property
deltas on all nine pages, ratchet 32 passed, suite 906 passed** — deleting it changed nothing,
because the seven migrations had already made it unreachable. `UI-047c` unlinked the last page
holding it earlier the same day.

**`unsanctioned_hex` went 429 → 400.** That is the first ratcheted metric in this epic to fall
through deletion rather than through care; the 29 were theme.css's own.

**Checked before deleting, not after.** No page links it, verified across all nine plus the
mockup. No test opens it — the two hits in `test_css_architecture.py` are prose.
`css_baseline.py` names it only in comments. `css_orphans.py` **does** read it, at :89 as
`OLD_THEME`, and already handles absence at :807 with a warning rather than a crash; confirmed
by running it afterwards, where `index` reports `theme? no` and every column zero, which is
correct rather than broken.

**And this is the easy half, which the numbers should not be allowed to hide.**
`legacy_css_lines` is **2,115 and did not move**. `shared_css_lines` is 2,963 — down 212 from
3,175, but still **437 above** the 2,526 pinned at baseline, because the new tree was built
alongside the old one rather than in place of it. `static/app.css` is untouched and still
linked by all nine pages. **The real work of Sprint 6 is the nine `99-legacy` files and none of
it has started.** This deletion was cheap precisely because the migrations had already done the
expensive part.

---

## 2026-08-13 — index is live. **9 of 9 pages.** Sprint 4b is complete

**Sprint 4b, UI-ARCH epic.** Full board: `docs/ui/STATUS.md`. Sprint 3 closed incomplete at
3 of 9; seven migrations opened the other six, four of them in two days.

**The page everyone feared was the smallest migration in the epic.** `index` is the largest
page in the app — 508 elements at rest, a 7-screen SPA, 224 inline `style` attributes — and
it needed **no compat block, no re-classing and no UI-046**. It declares all 27 tokens it
reads, so nothing had to be re-supplied; its shell is its own `.shell`/`.app-sidebar`/
`.app-nav` rather than `theme.css`'s grid, so no class attribute changed at all; and the 224
inline styles were never at risk, because inline beats every layer. Part 2 was a `<link>` swap
and nothing else. The very thing `PLAN.md` §1 opens with as a defect — *"index.html redefines
`--line` and `--muted`"* — is what made it cheap.

**2,476 deltas on the page, and each was read rather than waved through.** The palette takes
over (index's `--ink` → `--color-text`, 256 elements plus their border colours), the type scale
lands (16→15px on 171, 15→13.5px on 58), the body leading lands where legacy left it `normal`
(185 at 21.75px), D31's label role arrives on 44 — the same change `bank` and `library` already
took — em gaps shrink with their font-size, and form controls take `forms.css`'s optical
padding. Nothing unaccounted for, nothing pointing at something lost. The five page-scoped
rules were verified element by element: `.main` keeps its padding, `.summary-row` keeps its
dashed rule at index's own `--line`, `.tag` keeps its pill, and **all four `.urdu` elements keep
Nastaliq — including the two toggle buttons that were the whole of decision A.**

**And the one real defect was found by eye, not by any gate.** Irfan opened the page and the
last nav item, SLO Health, hung outside the navy sidebar. `.app-sidebar` is `height: 100vh`
with **no `overflow` property**, so content taller than the viewport spills out of the painted
box instead of scrolling. Both other shells in this repo handle it — `theme.css`'s `.nav` and
`shell.css`'s `.o-shell__nav` both set `overflow: auto` — and the legacy `.app-sidebar` never
did, on any of the six pages that use it.

**index's line-height was not the defect and the fix does not touch it.** All six migrated
pages compute the nav at 21.75px; index's is simply the tallest at 450px against 294 and 209,
because it lists every screen. Special-casing its leading would have fixed the symptom by
making one page disagree with five. The fragility also pre-dates the migration — the sidebar's
children totalled 680.4px before and 700.7px after, so the new leading added 20.3px and crossed
the threshold on Irfan's screen.

**No probe could have caught it, and the record says so.** At the probe's 900px viewport
nothing overflows, `overflow` is not a captured property, and the fix therefore measures as 0
deltas — which means it disturbs nothing, not that it works. **The same hole is still open on
`library`, `bank`, `slo`, `slo-health` and `taqseem`** and is deliberately left open: they are
live, their navs are short enough that nothing has spilled, and five live pages want their own
gate run rather than a drive-by.

**Where the epic now stands.** Every page is on the new tree and **`static/theme.css` — the
212-line file this epic exists to replace — is now linked by no page at all**, so deleting it
is unblocked for the first time. `static/app.css` is not in the same position: all nine pages
still link its 57 lines for the `@font-face` block and the `.icon` sprite rule, and it goes
with `UI-064`. But `99-legacy/*` is still **2,115 lines** against a 2,133-line baseline,
and the new tree sits on top of it rather than in place of it. **CSS has roughly doubled and
nothing has been deleted yet.** That reverses in Sprint 6, which has not started.

---

## 2026-08-13 — blueprint is live, UI-046 is finally verified, and index turns out to be blocked on nothing

**Sprint 4b, UI-ARCH epic.** Full board: `docs/ui/STATUS.md`. **8 of 9 pages are now live**;
only `index` remains.

**UI-046 — nav + shell, and the board's twelve rules were nine.** `05-components/nav.css`,
nine rules in `layer(components)`. Three of the twelve were not written and none was skipped:
`.app` and `.top .spacer` are already complete in `04-objects/shell.css` as `.o-shell` and
`.o-shell__spacer`, so repeating them would duplicate the layout this epic exists to remove;
and `.nav a .icon` is dead, because `static/app.css`:57 sets a bare `.icon` unlayered and an
unlayered rule beats every `@layer` regardless of specificity. The enumeration also turned up a
name the board never recorded — `theme.css`:84 spells it `.nav a .ic, .nav a .icon`, so there
are two dead names, not one. `.top` and `.nav` shrank to two declarations each, because
`shell.css` owns their layout and only the surface and the edge were left.

**The names are new — `.appbar` and `.sidenav` — and that was chosen against measurement.**
`.top` and `.nav` were measured free on all seven live pages, so adopting them would have been
safe; the reason not to is that they are exactly the kind of generic name whose nine
independent copies caused this epic. `.app-nav` is live on seven pages and `.topbar` on
`index`, so both were excluded; `.sidenav` and `.appbar` return zero in every page and every
stylesheet here.

**UI-047b — blueprint is LIVE, and it is what verified UI-046.** UI-046 shipped prepared and
*unverifiable*: its rules stood at `matches:0` because blueprint loaded no layered stylesheet
at all. This migration gave them markup, and all nine went live — `.sidenav__link` at 5,
`.appbar` and the rest at 1. Split into two commits at Irfan's request: the entry file first,
deliberately unlinked and measurably inert, then the `<link>` swap and the re-classing.

**Two of the ten re-classes turned out to be additions, and both were caught before the edit
rather than after.** `.brand` is kept alongside `.o-shell__brand` because `brand.js`:22 queries
`.brand .name` and sets the school name from it. `.main` is kept alongside `.o-shell__main`
because `99-legacy/blueprint.css`:28 sets `max-width: 1080px` on it. Dropping either class
would have been an invisible regression — blueprint is not in `css_type_probe`'s page list, so
no gate would have caught the school name silently not being set, or the content running the
full width of the viewport.

**And `index` was never blocked on D22.** Six places on the board said it was.
`DECISIONS-FOR-IRFAN.md`:67 corrected that on **2026-08-04** — D22 is a technical constraint
whose fix can only land in the commit that re-classes markup, which is Sprint 6, not a decision
anyone was waiting on — and the correction never propagated. Two of the six stale copies were
written by this session, into `ROADMAP.md` and `HANDOFF.md`, from the stale rows rather than
from the decisions file. All six are corrected here.

**The real blocker was smaller and is now answered.** `index`'s two اردو toggle buttons lose
Nastaliq after migration, because `03-elements/forms.css`:101's `button { font-family: inherit }`
sits in `layer(elements)` and outranks `99-legacy/index.css`:34's `.urdu, .ur` in
`layer(legacy)`. Measured scope: **exactly 2 elements.** The `.urdu` input at `index.html`:444
is safe behind an inline style, and `bank`/`print` are unaffected — their `urdu-toggle-row`,
`qtext-ur` and `urdu-input` are different class names. Irfan answered **A**: a page-scoped rule
in `index`'s own entry file, the same pattern `taqseem`'s bare `.card` and `blueprint`'s
`.brand` and `.chip` already use. **`index` now waits on nothing.**

**Gates across both tasks:** 0 element × property deltas on all six probed live pages, drift 0,
ratchet 32 passed, suite 906 passed. On blueprint: `theme?` **no**, EXPOSURE **20 → 0**,
elements 235 → 234 which is the removed `<link>`.

**Not fixed, and said out loud rather than buried under "page is live":** blueprint's
narrow-viewport shell. `theme.css` carries two `@media (max-width: 760px)` rules for `.app` and
`.nav` that nothing redeclares. `shell.css` declined that breakpoint deliberately — hiding the
nav without the control that brings it back is half a mechanism, and that control is a
component nobody has built. D21 flags the same viewport. It was broken before this and is
broken after it.

**The ratchet earned its keep again.** `nav.css` failed it on the first run,
`unsanctioned_hex` 429 → 430, because the file's own comment quoted a raw hex while explaining
that raw hex cannot be quoted. Seventh time that check has fired on this epic; seventh time
through a comment.

---

## 2026-08-12 — UI-043 came off the critical path, and no CSS was written to do it

**Sprint 4b, UI-ARCH epic.** Docs only. Full board: `docs/ui/STATUS.md`, evidence block in
`docs/ui/NEXT-SESSION.md` §📐.

**What the board said.** Both remaining pages — `blueprint` and `index` — were held on
`UI-043`, a component task, for its `.chip` and its `.tag`. The order was `UI-043` → `UI-046`
→ `UI-047b`.

**What the enumeration measured.** Four rules are actually at stake: `.chip` (blueprint ×1),
`.tag` (index ×2), `.row` (index ×1), `.summary-row:last-child` (index ×1). Three of them are
already live on migrated pages. `main.css`:42 orders the layers with `legacy` lowest, so a
`layer(components)` rule should beat the legacy file painting those elements — the same call
`card.css` made for the bare `.card` and `btn.css` for the bare `.btn`. **But those two had safe
descendants to ship and these three do not**: they are flat single rules with nothing underneath
them, so a component file has nothing it can carry.

**That reading was then tested rather than trusted**, because a cascade argument is exactly the
kind of thing this epic keeps getting wrong. The three rules were written into
`layer(components)` at `theme.css`'s own values, `css_type_probe` was run against a same-browser
control, and the rules were reverted. **`landing` moved 21 element × property deltas and
`taqseem` moved 2** (`gap` 12px → 10px). The mechanism is measured, not inferred.

**The first run gave a false all-clear, and that is the part worth keeping.** It reported 0
deltas everywhere but `landing`, which read as "`.row` is safe" — and that was written down and
told to Irfan before it was checked. It was wrong. The probe's page list did not include
`taqseem`, the one live page whose legacy `.row` sets a different `gap`; `slo` and `slo-health`
returned 0 because their value already agrees, which is agreement and not absence of collision.
**A 0 from a probe that is not looking at the page is not a 0.** `taqseem` was added to
`css_type_probe.mjs` — late, since `UI-047a` migrated it that same day and should have added it
then, exactly as that file's own comment requires.

**`.chip` cannot be probe-measured at all.** `taqseem` has no static `.chip`; the class exists
only inside `chipHtml()`'s template string, so the chips are absent from every snapshot until
real data renders them. An earlier count of "`.chip` ×1" was counting that template string as
markup. What can be compared is the two declarations, and they are not variants of one
component — `99-legacy/taqseem.css`:72 is a standing bordered block holding a code, a strand, a
sequence and a `<select>`; `theme.css`:127 is a flat pill. A component `.chip` would collapse
the first into the second.

**`.tag` is the same failure three times over**: the brand tagline on `index` (×2, both
`data-i18n="brand.tag"`), the hero tagline on `landing` (which `brand.js`:27 queries as
`.brand .tag:not([data-i18n])`), and a JS-rendered SLO code badge on `slo-health`.

**Consequence.** All four rules are page-scoped and belong to the two migrations, `UI-047b` and
`UI-047c` — exactly where `taqseem`'s bare `.card` went the same day. **`UI-043` is off the
critical path**: `blueprint` now needs only `UI-046` plus its migration, and `index` needs only
a decision on **D22**, with no code in front of it at all. UI-043's remaining scope is real but
nothing waits on it — tables were already shipped by `03-elements/tables.css`, and the domain
families are duplication work for Sprint 5/6.

**The method is the transferable part.** This is the second finding in one day from the same
step: list what a page loses when `theme.css` goes, then check each line against the tree
instead of trusting the coverage claim. The first was a missing `white-space` in `btn.css`.
Neither was found by review; both were found by one probe run and a grep.

**And the correction is the second transferable part.** The claim in this entry was written
once from a cascade reading, presented as settled, and then asked for by Irfan as a measurement
before it could be committed. Measuring it confirmed the conclusion and broke one of the three
arguments under it. The conclusion survived; the reasoning did not, and a board carrying the
original wording would have taught the next session a false rule about `.row`.

---

## 2026-08-12 — UI-047a: taqseem migrated, and its enumeration found a hole in a finished component

**Sprint 4b, UI-ARCH epic.** Full board: `docs/ui/STATUS.md`. **7 of 9 pages are now live**
on the new tree; `blueprint` and `index` remain.

**What shipped.** `taqseem.html`'s three `<link>`s became two — `app.css` plus the entry file
`static/css/pages/taqseem.css`, unparked from `docs/ui/` where it had waited since 2026-08-03
for the components it borrows. Three buttons re-classed (`btn gold` ×2 → `.btn--accent`,
`btn ghost` → `.btn--ghost`). The entry file gained a page-scoped bare `.card` and the two
`.brand` partials the legacy file does not fully redeclare. This is the first migration that
had to change markup rather than only swap a link.

**The finding, and it is why the first step was an enumeration and not the `<link>`.** The
board said `taqseem` loses 17 rules when `theme.css` goes, that existing components cover
them, and that exactly one exception was known — the bare `.card`, which `card.css` omits
deliberately because `.card` is on 13 live elements elsewhere. The instruction was to confirm
there was no *second* exception before touching anything. There was. `theme.css`'s bare `.btn`
carries thirteen declarations; twelve had been ported into `.btn--*`, and the thirteenth,
`white-space: nowrap`, existed **nowhere** in the layered tree — not ported, not decided
against, simply absent. UI-041 shipped after four review rounds and none of them saw it.
Listing what one page loses and checking each line against the tree did, in one probe run.
Fixed at its own address in `btn.css` (`2f2368e`), not page-scoped, because it is a property
of the button rather than of this page.

**Gates.** 0 element × property deltas on all five pages `css_type_probe` covers, drift 0.
On `taqseem`: `theme?` no, EXPOSURE 17 → 0. Element count 70 → 69, which is the removed
`<link>` and not a lost node. `.btn--*` went live on real markup for the first time — the
rules probe reports 3 / 2 / 2 / 1 in `layer(components)` against UI-041b's `matches=0`.

**And the page was opened before it was committed.** The same migration was performed on
2026-08-11, passed every gate above, and was reverted deliberately — chips and the `.move-sel`
selects are JS-rendered, appear in no snapshot, and no computed-style probe can see whether the
page still works. **Checked by Irfan on 2026-08-13, item by item.** Confirmed: **chips render as
standing blocks** rather than collapsing to pills, so the legacy `.chip` still wins; and
**changing a chip's select moves the SLO**, so `moveSlo` fires. Those two are precisely what the
board said needed eyes. **Not checked: the confirm modal's open/cancel, and the card border and
brand header** — recorded as unchecked rather than assumed. Only `Pre Year 1` / `Mathematics`
can be used for this check; it is the one class/subject carrying a plan, and every other
combination renders an empty board that reads as breakage and is not.
Two changes are deliberate and were flagged in advance so they would not read as regressions —
the buttons are taller (44px touch target) and the accent fill is darker, because white on the
old fill measured 3.03:1 and failed WCAG on this page.

---

## 2026-08-01 — UI-031a: slo.html is the first page on the new CSS tree (@layer live)

**Sprint 3, UI-ARCH epic.** Full board: `docs/ui/STATUS.md`. This is the first page in the
epic whose stylesheet is the new ITCSS tree, and the first time any browser has parsed the
`@layer` statement the whole architecture rests on.

**What shipped.** `slo.html`'s three `<link>`s became two: `app.css` (it still owns the
`.icon` sprite until Sprint 4) plus a new entry file `static/css/pages/slo.css`, which is two
`@import`s and no rules of its own — `../main.css`, then `../99-legacy/slo.css layer(legacy)`.
`main.css` lost the nine legacy `@import`s it used to carry. Not one other byte of the page
moved: frozen inventory 22/22, class attributes 48/48, `<script>` bodies identical, −53 bytes
which is exactly the link swap.

**Why the documented shape was abandoned.** ADR-001 says the `<link>` goes straight to
`main.css`, which imported all nine `99-legacy/*` files. Measured before writing: they import
alphabetically, so `taqseem.css` is last and won **15 selectors** off this page — `:root`,
`.app-sidebar`, `.brand`, `.app-nav a`, `.sidebar-foot`, `.row` and more — and every value it
brought reads a `static/theme.css` token that the same task unlinks. The by-the-book migration
would have shipped an unpainted sidebar and no border colours, through a file belonging to a
different page. That is D19 and D20 arriving together, on the one page whose own 17 tokens are
all local literals. The legacy import therefore moved out of `main.css` into a per-page entry
file; `main.css` keeps the layer order and remains the single source of the cascade. Rule
changed in `CLAUDE.md` §11 and recorded as unplanned.

**Verified in a real browser, not by reasoning.** The Chrome extension was not connected, so
headless Edge 150 was driven over CDP with Node's built-in WebSocket. Read off the live
document: the layer statement with all seven names in order, every `@import` in its declared
layer, `99-legacy/slo.css` in `layer(legacy)` rather than unlayered, sidebar `rgb(22,41,74)`,
`static/theme.css`'s tokens all empty, icons 17px, and the other eight pages untouched.

**Four review rounds failed it, and the three real failures were one shape: a number asserted
instead of measured.** A contrast ratio computed against an assumed backdrop (the real figure
was 1.70:1 → 3.04:1, an *improvement*, because the old sidebar had a white slab in it); a
"what changed" list naming only one of two mechanisms and missing D21 firing live; and four
line numbers inherited rather than checked. All three now sit in the files as recorded failed
drafts, so the next session meets the trap and not just the answer. One aggregate count was
deleted rather than fixed — two measurements disagreed on which properties to count, so the
files give affected elements per rule, which anyone can re-derive with a grep.

**Two things worth remembering beyond this task.** Quoting two hex values in a *comment* took
`unsanctioned_hex` 429 → 431, and because `css_baseline.py --write` had already run, the
raised number was pinned into `BASELINE.json` and `--check` then passed against the laundered
baseline — re-pin only *after* `--check` passes against HEAD. And `C:` hit 226 MB free during
this task, producing a real `No space left on device` mid-pytest; UI-030's recorded sqlite
"disk I/O error flake" was almost certainly the same thing.

**Ships with three visible changes, all accepted and all homed in Sprint 4:** the sidebar
subtitle at 3.04:1 (better than before, still under WCAG AA) — D26; `<a class="btn-ghost">`
losing its blue while `<button class="btn-ghost">` keeps it — D27; and cards visibly tighter,
headings ~20% bigger with the gap beneath them gone — D28. A fourth item, D29, records that
two different files are named `theme.css` and the browser's Network panel shows only the
basename — it caused a false alarm at the browser check.

Gates: `pytest -q` 906 passed · `ruff` clean · ratchet OK, eight ratcheted metrics flat,
`unsanctioned_hex` 429 · `shared_css_lines` 1351 → 1527, the only mover.


## 2026-07-26 — Concurrency fix: SQLite WAL + busy_timeout (20-teacher concurrent write)

MASLA: 20 teachers ek server se (LAN) ek saath likhte — default DELETE-journal +
busy_timeout=0 par write-conflict FORAN "database is locked" (500) deta tha. Data SAFE
tha (SQLite ACID — failed write cleanly rollback, koi corruption NAHI; DB local disk par,
clients HTTP se — network-FS nahi), par teacher ko error dikhta aur dobara try karna padta.
Fix chhota + in-place, koi re-architecture nahi.

- STEP 1: `get_connection()` (app/core/database.py) —
  `sqlite3.connect(DB_PATH, timeout=30)` + `PRAGMA journal_mode=WAL` +
  `busy_timeout=5000` + `synchronous=NORMAL`.
    * WAL — concurrent reads smooth (reader/writer ek doosre ko block nahi karte); ek
      writer serialized. WAL local disk par safe (network-FS par NAHI — yahan clients
      HTTP se aate, DB file local hai). WAL DB header par persistent (ek dafa stick).
    * timeout=30 / busy_timeout=5000 — locked par foran fail nahi, thodi der wait
      (short writes ab ek doosre ka intezaar kar lete, error nahi).
    * synchronous=NORMAL — WAL ke saath durable + tez.
- STEP 4: .gitignore — `*.db-wal` + `*.db-shm` add. (`*.db.*` dot-pattern hyphen-siblings
  ko match nahi karta tha — WAL sidecar files kabhi git par na jayein.)
- Regression: sirf get_connection() ke ANDAR PRAGMAs — koi endpoint/repository/connection-
  per-op logic chhua NAHI (open→execute→commit→close waise ka waisa).

Deployment context: `start.bat` → `uvicorn --host 0.0.0.0 --port 8000` (single worker);
teachers LAN par doosre PCs se EK server machine se connect karte, DB usi ki local disk par.
Sync `def` endpoints threadpool mein → concurrent threads, har ek apna connection — yahi
contention point tha.

Tasdeeq: PRAGMAs present; live raw-open `PRAGMA journal_mode` = **wal** (persistent, bina
PRAGMA set kiye — hatmi saboot), busy_timeout=5000, synchronous=NORMAL; `-wal/-shm` ab
gitignored; pytest -q = 874 passed; ruff clean. Browser test (Irfan): server restart ke
baad WAL ON confirm, do-tab se ek saath paper banaya — dono success, koi "database is
locked" error nahi. Note: `-wal/-shm` sidecar sirf live connection ke doraan disk par
(connection-per-op → idle par SQLite checkpoint kar ke hata deta — WAL-off ki nishani nahi).
Server restart chahiye tha (naya get_connection) — ho chuka. Postgres tab jab writes bahut
heavy hon (database.py comment migration path likhta) — abhi WAL+timeout kaafi.

## 2026-07-26 — Landing / teacher-welcome page (static/landing.html)

App ke andar chhota teacher-welcome page — 3 hisse: Hero, 7 quick-action cards
(existing pages tak), aur intro cards. Modern lekin saaf, teacher-focused (public
marketing NAHI). Frontend-only, responsive.

- STEP 1: `<head>` dhaancha index.html jaisa (consistency) — `app.css` link + inline
  `:root` vars (wahi palette: primary/navy/tint/ink/muted/border/surface/bg/radius/shadow)
  + body font 'IBM Plex Sans' + end mein `<script src="/static/js/brand.js">`. `<body
  data-page="Welcome">` (brand.js title + .brand name/tag set karta). Nastaliq @font-face
  skip (page English/Roman-Urdu, koi Nastaliq text nahi).
- STEP 2 (Hero): navy gradient band; `.brand .logo` (/static/brand/logo.svg) + name/tag
  (brand.js bharega) + welcome line (offline exam paper generator, AII Mingora).
- STEP 3 (Quick actions): 7 hover-lift cards, icons `icons.svg` se — Generator (/),
  Blueprint (/blueprint.html), Question Bank (/bank.html), Image Library (/library.html),
  Learning Outcomes (/slo.html), Exam Taqseem (/taqseem.html), SLO Health (/slo-health.html).
  Icon pattern `<svg class="icon"><use href="/static/icons.svg#i-…"></use></svg>`.
- STEP 4 (Intro cards): 4 chhote cards (Paper banao / Blueprint templates / SLO coverage /
  Image library), 1-line each — intro, marketing nahi.
- STEP 5: responsive (grid auto-fill/auto-fit wrap + mobile media query). Koi external
  CDN/font/script nahi (offline) — sirf app.css vars + icons.svg + brand.js REUSE, koi
  naya brand code nahi.

Placement: `/landing.html` — ZERO backend/main.py change (StaticFiles `/` mount ise serve
karta). `/` waise ka waisa hai (= index.html Generator); landing usay replace nahi karta.
Palette: navy + primary-blue on-brand — brand.json mein gold color nahi, is liye invent NAHI
kiya (agar gold accent chahiye to pehle brand system mein add ho, tab landing use kare).

Tasdeeq: git diff sirf naya static/landing.html (koi backend/dusra page change nahi);
7 quick-action cards + 7 sahi hrefs, 11 icon `<use>` refs (7+4), brand.js + data-page,
div balance 38/38; ruff clean; pytest -q = 874 passed. Browser test (Irfan): Hero+brand
(name/tag/logo) sahi ✓, 7 links sahi pages ✓ (Blueprint confirm), mobile cards wrap ✓,
navy+blue on-brand ✓. Frontend-only — koi restart nahi.

## 2026-07-26 — Hissa 5-B: question-type ↔ Bloom hint (section-level, soft)

Section card mein Bloom Level chunne par uske paas chhoti soft hint — us bloom ke munasib
question-types (misal "Apply ke liye aksar behtar: Short-answer · Fill-blank"). Tajweez,
hukm nahi; override khula. Frontend-only, koi backend/DB/5-A change nahi.

- STEP 1: `QTYPE_HINT` const (frontend, script scope) — UPPERCASE bloom key → labels array.
  Values SIRF section-card ke 4 selectable types (MCQ / Fill-blank / True/False /
  Short-answer). `essay` bloom_service/ai_service mein hai par section-card checkbox mein
  selectable NAHI, is liye hint se chhoda (warna teacher aisi type ki tajweez dekhta jo
  select hi nahi kar sakta). Keys UPPERCASE = dropdown value se seedha match (koi casing-
  bridge nahi, 5-A wala lowercase masla yahan nahi). Purely presentational — koi backend
  consumer nahi, is liye frontend const (5-A ke ulat jahan bloom_standards 3 services
  consume karte the).
- STEP 4: `qtypeHintHtml(bloomVal)` DRY helper — UPPERCASE bloom → hint HTML (ya khali
  agar Any/null/unknown). renderSecCard (initial render) + onBloomFilter (update) dono
  reuse karte — ek jagah.
- STEP 2: `#qtypeHint_${i}` read-only div, renderSecCard mein Bloom `<select>` ke baad
  (isi wrapping div). Initial content `qtypeHintHtml(sec.bloom_filter)`. escHtml-safe.
- STEP 3 (STALE-TRAP FIX): `onBloomFilter` pehle sirf state set karta tha (card re-render
  nahi) — to static hint bloom badalne par stale reh jata. Ab handler hint element ka
  `innerHTML` seedhe update karta (`getElementById('qtypeHint_'+idx)`). Poora
  `renderSections()` NAHI — focus/scroll safe + sasta.
- STEP 5: regression-safe — bloom_filter khali/'Any'/null → helper `''` return → hint
  hidden (invisible). Question Types checkboxes / onTypeChange / Bloom filter ki asal
  functionality chhui NAHI (sirf ek read-only div + handler mein ek update-line). 5-A box
  (#bloomSuggestionBox) + backend untouched.

5-A se alag: 5-A paper-level Bloom DISTRIBUTION (class-tier %, grade dropdown ke paas),
5-B section-level QTYPE hint (Bloom filter ke paas). Alag DOM, scope, trigger — koi takrav nahi.

Tasdeeq: grep QTYPE_HINT=2 (def+use), qtypeHintHtml=3 (def + renderSecCard + onBloomFilter),
qtypeHint_=2 (element+handler); inline JS node --check "JS SYNTAX OK"; pytest -q = 874 passed;
ruff clean. Browser test (Irfan): Remember/Apply/Analyze → sahi hint ✓, Any → gayab ✓, fauran
badalta bina blink/scroll-jump ✓. Naya backend test nahi (behaviour puri tarah frontend/DOM;
koi contract nahi badla). Frontend-only — hard refresh kaafi, restart nahi.

## 2026-07-26 — Hissa 4-E: pin reset-gap fix (deferred 4-D bug)

4-D mein pins ephemeral kehlaate the lekin makePaper ke baad `_pinned` clear nahi hota
tha — purane pins agle paper mein reh jaate ("yeh question kahan se aaya?" confusion).
4-E: pins teen jagah clear, ek DRY helper se. Frontend-only, koi backend/DB/schema change nahi.

- STEP 1: `clearPins()` helper — `_pinned = new Map(); updatePinnedBadge();`. Khali Map ->
  khali Map, to koi pin na ho to no-op (regression-safe).
- STEP 2: makePaper SUCCESS par reset — dono success branches (shortfall `if` + ok `else`)
  ke BAAD, renderBloomGuidance/print-open se pehle. `clearPins()` + `checkExamCoverage()`
  (open SLO panels ka stale "✓ pinned" button reset). SUCCESS-ONLY: 404 / `!res.ok` guards
  pehle return kar chuke, `catch` network-error, aur `finally` (sirf btn re-enable) — in par
  reset NAHI, pins intact (warna fail par teacher ko dobara pin karna padta).
- STEP 3+4: `onSubjectChange` + `onGradeChange` mein bhi `clearPins()`. Yeh sirf tidy nahi —
  CORRECTNESS fix: pins `qid` hain jo ek subject/grade ke question-set se bandhe. Subject/
  grade badle to purane qids be-maani; aur 4-C backend pinned ids ko filters ke BAHAR bhi
  force-include karta — doosre subject ka valid qid naye paper mein force-inject ho kar
  ghalat-subject question la sakta tha. checkExamCoverage() dono handlers mein already hai
  (L501/L541), to SLO panels bhi refresh ho jaate.
- STEP 5: pin-attach logic (makePaper L1156-1164) chhua NAHI — sirf success ke baad clear add.

Tasdeeq: grep clearPins=4 (1 def + 3 call: onSubjectChange/onGradeChange/makePaper-success);
inline JS node --check "JS SYNTAX OK"; pytest -q = 874 passed; ruff clean. Browser test (Irfan):
success→clear ✓, subject/grade change→clear ✓, fail→intact ✓. Naya backend test nahi (behaviour
puri tarah frontend/DOM; pin-attach backend contract pehle se 7 tests se covered). Frontend-only —
hard refresh kaafi, restart nahi. 4-D ka reset-gap ab band.

## 2026-07-26 — Hissa 5-A: Bloom distribution tajweez — investigation + guard test

Maqsad tha blueprint page par class-tier ki soft Bloom distribution tajweez (Pre-Primary
70/30 … Matric 15/25/30/20/10, read-only, "mashwara hukm nahi"). INSPECT mein pata chala
feature **pehle se end-to-end maujood** hai: `app/core/bloom_standards.py` (_GROUPS) →
`GET /api/bloom-suggestion/{class_name}` (app/api/bloom_suggestions.py) → blueprint.html
`onGradeChange` fetch + `#bloomSuggestionBox` render. Yaani naya kaam sirf tasdeeq +
tahaffuz ka tha.

- STEP 1 (rejected): frontend-only mirror try kiya — `BLOOM_STD` JS const (UPPERCASE keys,
  casing bridge) + `bloomSuggestion()`/`renderBloomSuggestion()` helpers, API call ki jagah.
  Faisla: REVERT. Wajah — `bloom_standards.py` waise bhi 3 jagah consume hota
  (bloom-suggestion route + blueprint_bloom_guidance_service + slo_shortfall_service), to
  Python copy khatam nahi ho sakti; mirror teesri copy = net duplication + drift-risk.
  Localhost par round-trip ka faida ~sifar (onGradeChange mein pehle hi /api/topics fetch).
  "Ek source of truth" (backend) saaf jeeta. blueprint.html byte-identical wapas (git diff khali).
- STEP 2 (kept): tests/test_bloom_standards.py — 6 tests jo canonical %ages pin karte:
  Pre-Primary 70/30, Primary 30/35/25/10, Middle 20/30/30/20, Matric 15/25/30/20/10;
  normalize variants (grade 1 / Grade  1 / GRADE-1 / grade_1 → Primary); unknown/khali → None.
  Yeh guidance + shortfall services ki bunyaad bhi pin karta (woh bhi inhi standards par tikke).

Tasdeeq: blueprint.html unchanged (diff khali, API path bahal, /api/bloom-suggestion=1);
inline JS node --check OK; pytest test_bloom_standards.py = 6 passed; full suite 874 passed;
ruff clean. Net change is branch par: sirf naya guard-test (frontend/backend code chhua nahi).
Note: Bloom naming casing — questions.bloom_level UPPERCASE, slo.bloom_level lowercase;
standard keys lowercase (services `.upper()` se bridge karte).

## 2026-07-26 — Hissa 4-D: multi-section pin targeting

4-C ka pin ab per-section — teacher batata hai konsa pinned question KIS section mein
jaye (pehle sab pehli section par jaate the). `_pinned` ab `Set<qid>` ki jagah
`Map<qid, sectionIndex>`. Backend pehle se per-section `include_question_ids` guarantee
karta tha (4-C contract), sirf frontend value-group kar ke bhejta.

- STEP 1: blueprint.html — `_pinned = new Map()` (qid -> 0-based sectionIndex, ephemeral).
  showSloQuestions har question par section `<select>` (A/B/C… = index) deta; pinned ho
  to us ki section pre-select. togglePin saath wale select ki value uthata; setPinSection
  already-pinned ki section re-assign. Badge ab per-section breakdown (📌 3 pinned A:2 B:1).
- STEP 2: makePaper — `_pinned.entries()` ko section index se group, har section apne ids
  `include_question_ids` mein; koi pin na ho to body bilkul waisa (regression-safe).
- STEP 3: removeSection — pin re-map: hataayi section (idx) ke pins DROP, us se upar wale
  (secIdx > idx) ek khisak (secIdx-1). Warna pin ghalat section par point karta.
- STEP 4 (BUG fix): browser test se "pinned question galat section" pakra. Instrumentation
  pehle ([PIN-DBG] console.log removeSection+makePaper) — console trace + 2 PDF se saabit
  ke pin LOGIC sahi hai; asli masla sirf COSMETIC label-drift tha: default headings
  ("Section A/B/C") remove ke baad re-number nahi hote the, jabke select/badge index-based
  letter dikhate. `renumberDefaultHeadings()` — conditional: sirf `/^Section [A-Z]$/`
  (default) headings ko index se align; teacher ki custom heading ("Objective Questions")
  MAT chhue. removeSection (re-map ke baad) + addSection dono par chalta — "ek source of
  truth" (badge/select/heading sab index se derive). Phir instrumentation revert.
- STEP 5: tests/test_blueprint_hissa4c_pin.py — +2 (total 7): two-sections-distinct-pins,
  pin-only-in-its-section (backend per-section contract jis par frontend bharosa karta).

Tasdeeq: grep [PIN-DBG]=0 (reverted); renumberDefaultHeadings 1 def + 2 call; inline JS
node --check "JS SYNTAX OK"; pytest test_blueprint_hissa4c_pin.py = 7 passed; ruff clean.
Frontend-only change (backend/schema untouched) — hard refresh kaafi, restart nahi.
Deferred: pin reset-gap (blueprint reset/switch par pins clear nahi hote) — Hissa 4-E candidate.

## 2026-07-25 — Hissa 4-C: "daalo" — must-include pinned questions (Option A)

Teacher "questions dikhao" (4-B) list se question pin karta; backend usay blueprint
section mein GUARANTEE karta. "Tajweez, hukm nahi" — app khud add nahi, teacher pin
karta. Faisla: pinned COUNT KE ANDAR (pinned pehle, filter baqi jagah); pinned > count
to count barh jaata.

- STEP 1: schema `BlueprintSection.include_question_ids: List[str] = []` (requests.py).
  Khali = purana rawaiyya (backward-compat).
- STEP 2: `blueprint_paper_service._apply_pinned(picked, ids, wanted)` — pinned pehle
  (dedup, order-preserve), filler baqi; effective count = max(wanted, #valid-pins);
  non-existent id skip (find_by_id None); double-count guard. Loop mein filter ke baad
  call; pins ki soorat mein shortfall-note final got par recompute. Koi valid pin na
  ho to picked/wanted bilkul waise (regression-safe).
- STEP 3: blueprint.html — `_pinned = new Set()` (ephemeral, paper-level); 4-B list ke
  har question par "daalo"/✓pinned toggle (togglePin); action-bar mein "N pinned" badge
  (updatePinnedBadge); makePaper body mein pins PEHLI section par attach (saveBlueprint
  ko nahi chhua — template mein pins save nahi). escAttr/escHtml-safe.
- STEP 4: tests/test_blueprint_hissa4c_pin.py — 5 pass: guaranteed-first-within-count,
  dedup, over-count-expands, nonexistent-skip, no-pins-unchanged.

Tasdeeq: schema default []/list accept; service AST+import OK; blueprint inline JS
node --check OK (_pinned=8, togglePin=2, pinnedBadge=2, include_question_ids=1);
pytest -k "blueprint or coverage or paper" = 260 passed; ruff clean. Naya schema
field + service => server hard-restart chahiye.

## 2026-07-25 — Hissa 4-B: "questions dikhao" — missing SLO ke tagged questions (Option A)

4-A warning box extend: har missing SLO ke saath "questions dikhao" link; click par
us SLO se tagged questions (published + draft dono) inline expand — READ-ONLY, teacher
khud upar section mein daalta (app add nahi karti). Zero DB/schema change — sirf ek
naya read route jo maujooda question_slo link table parhta.

- STEP 1: `question_slo_repository.list_questions_for_slo(slo_id)` — ek JOIN (q.* JOIN
  question_slo WHERE slo_id), koi status filter nahi (sab), created_at se sorted. N+1 nahi.
- STEP 2: `question_service.list_questions_for_slo(slo_id)` — pass-through wrapper.
- STEP 3: `GET /api/slo/{slo_id}/questions` (app/api/slo.py) — READ-ONLY, minimal fields
  {id, question_en, status, bloom_level} (poora row nahi). SLO wajood check nahi (khali
  list valid). slo router pehle se registered.
- STEP 4: blueprint.html — remaining SLO `<li>` mein "questions dikhao" link (slo_id via
  escAttr) + hidden `<div>`; `showSloQuestions(sloId, linkEl)` GET fetch, question_en +
  status badge render, toggle band. escHtml-safe, koi add/checkbox nahi.
- STEP 5: tests/test_slo_questions_api.py — 2 pass: published+draft dono tagged aayein
  (untagged bahar, minimal shape); unknown slo => 200 + khali list.

Tasdeeq: repo/service/route AST OK + route router par registered; blueprint inline JS
node --check OK (showSloQuestions grep=2); pytest 2 passed. Naya route => server
hard-restart chahiye.

## 2026-07-25 — Hissa 4-A: Blueprint exam-coverage warning (frontend-only)

blueprint.html mein exam (bpExamNo) chunte hi taqseem-coverage ka READ-ONLY warning —
kaun se planned SLO abhi shamil nahi. Koi backend/DB/route change nahi; GET /api/coverage
ka maujooda `remaining` list reuse (per-SLO uncovered). Server restart nahi, hard refresh.

- STEP 1: bpExamNo ke neeche `<div id="bpCoverageWarn">` (hint div ke baad, container
  332 ke andar) + select par `onchange="checkExamCoverage()"`.
- STEP 2: `checkExamCoverage()` — guards (Unassigned""/subject/grade khaali => hide),
  GET /api/coverage (slo-health.html:398 pattern), render: remaining=0 & total_slos>0
  green tick; remaining>0 amber "⚠️ N planned SLO abhi shamil nahi" + list (slo_text
  readable, SLO-code bracket mein, pehle 8 + "… aur M zyada"); total_slos=0 => hide.
  esc via escHtml. Read-only — koi button/action nahi.
- STEP 3: triggers — bpExamNo onchange + onSubjectChange()/onGradeChange() ke andar
  checkExamCoverage() call (subject/grade badle to warning refresh).

Tasdeeq: grep -c bpCoverageWarn=2, checkExamCoverage=4; onchange @334, calls @499/@539;
inline JS node --check OK.

## 2026-07-25 — Coverage Marhala 6b (UI) + 7 (nav icon) — feature mukammal

ECONNRESET mein jo 6 markers 0 nikle the (cov-badge/loadCoverage/paperExamNo/bpExamNo/
covResult + backend exam_no) — sab wapas, har file apne commit mein (ECONNRESET-safe).
Faisla: Unassigned = null (0 nahi) teeno paper-dropdown par. N-source har jagah
school_settings.exam_count (drift nahi). Traffic-light server coverage_percent reuse.

- 6b-1 (a5329c4) index.html `paperExamNo`: paper-build dropdown (Unassigned""→null +
  1..N). buildExamNoOptions loadSchoolSettings se (fail 8). buildPaper body exam_no.
- 6b-2 (3ce0a6c) blueprint.html `bpExamNo`: dropdown; N ek reuse GET /api/school-
  settings (page-load init); makePaper body exam_no. Inline-handler trap-zone chhua nahi.
- 6b-3 (444c560) slo-health.html `covResult` card: class+subject+exam -> GET /api/coverage;
  covered SLO ke saamne paper naam (paper_ids->paper_titles drill-down), remaining ke
  saamne "(kisi paper mein nahi)". esc() escaped, addEventListener saaf.
- 6b-4 (68c34cb) taqseem.html `loadCoverage`+`cov-badge`: har exam column header par
  "covered/planned" + traffic-light (>=100 green, >=60 yellow, <60 red, unassigned/
  planned0/null grey). Ek GET /api/coverage-summary, data-exam se match, idempotent inject.
- 7 (59a7fb2) icons.svg `i-taqseem` symbol (3-column exam-bucket shape) + 4 pages
  (index/slo-health/slo/taqseem) nav i-blueprint->i-taqseem. Blueprint nav har page
  i-blueprint par barqarar.

Tasdeeq: har file grep -c <marker> + node --check (inline JS) + per-file commit.
icons.svg XML well-formed. Full regression (test_ai_service ke ilawa) = 842 passed,
working tree clean.

## 2026-07-25 — Coverage Marhala 6a: blueprint exam_no threading (silent gap fix)

Gap: generate/bank/adaptive paper paths exam_no ko papers.exam_no tak thread karte
the, magar BLUEPRINT path nahi — UI dropdown se exam_no aata bhi to silently gir jaata
(blueprint paper hamesha exam_no=NULL). Marhala 3 threading ne ye path chhod diya tha.
UI (6b) se pehle band karna zaroori warna bpExamNo dropdown bekaar.

Teen keyword-arg edits (positional trap se bacha — pichla dead-code sabaq):
- `app/schemas/requests.py` BlueprintPaperRequest: `exam_no: Optional[int] =
  Field(default=None, ge=0)` (baaki 3 paper schemas jaisa).
- `app/api/papers.py` blueprint-paper route: `assemble_blueprint_paper(..., exam_no=
  req.exam_no)` (keyword).
- `app/services/blueprint_paper_service.py`: signature mein `exam_no: Optional[int] =
  None` param, aur `papers_repository.insert(..., exam_no=exam_no)` (keyword).

Test (`tests/test_coverage_api.py` — TestClient, full chain): `test_blueprint_paper_
persists_exam_no` — question seed -> POST /api/blueprint-paper {sections_input, subject,
exam_no:3} -> paper_id read -> assert paper["exam_no"] == 3 (NULL nahi). Exactly wo
silent gap band karta hai.

Tasdeeq: pytest tests/test_coverage_api.py -v => 4 passed. grep -c exam_no: requests.py
6, papers.py 1, blueprint_paper_service.py 2. Regression (blueprint hissa1-3 + shortfall
+ bloom + coverage + paper_service) => 180 passed. git diff --stat: 4 files, +60/-1.

Agla: Marhala 6b — UI (taqseem badges, index paperExamNo, blueprint bpExamNo, slo-health
coverage card).

## 2026-07-25 — Coverage Marhala 5: tests (service + api)

`tests/test_coverage_service.py` (6) + `tests/test_coverage_api.py` (3) — conftest
`test_db` fixture (tmp SQLite + init_db), data seedha repos se seed. Helpers _q/_slo/
_link/_paper(exam_no=)/_plan(overwrite_assignments). API: TestClient(app) module-level,
koi auth header nahi (key unset => unprotected, sibling jaisa).

Service tests:
- ⭐ test_covered_in_wrong_exam_stays_missing (STRICT cross-exam): s1 exam 2 mein
  planned, exam 3 ke paper ne cover kiya => exam 2 remaining mein, summary exam 2 & 3
  dono covered=0. Covered-in-wrong-exam kisi ko credit nahi (leak-guard lock).
- test_planned_but_missing: planned SLO, koi paper nahi => remaining.
- test_null_exam_paper_excluded: exam_no=NULL paper coverage se bahar (detail + summary).
- test_slo_two_papers_same_exam: paper_map mein dono paper_ids, covered_slos double-count
  nahi (SET membership).
- test_summary_includes_unassigned: exam_no=0 bucket shamil.
- test_class_normalized_match: paper class 'pre year 1' vs SLO 'Pre Year 1' match.

API tests: test_coverage_summary_200 (shape: class/subject/exam_count/exams + row keys),
test_blank_class_400, test_exam_no_out_of_range_400.

Tasdeeq: `pytest tests/test_coverage_service.py tests/test_coverage_api.py -v` => 9 passed.
Poora suite (test_ai_service network-call ke ilawa) regression check.

Agla: Marhala 6 — UI (taqseem.html badges, index/blueprint exam dropdown, slo-health card).

## 2026-07-25 — Coverage Marhala 4: routes (GET /api/coverage + /api/coverage-summary)

Nayi file `app/api/coverage.py` — HTTP layer (taqseem.py/papers.py jaisa: `APIRouter()`
koi prefix nahi, full path per route, GET query params, `.strip()` khali-check → 400,
service call `try/except` → 500).
- `GET /api/coverage?class_name&subject&exam_no` — ek exam ka mukammal coverage.
  exam_no LAAZMI (koi default nahi; UI hamesha bhejta, missing par FastAPI 422 —
  intended). Range 0..N validate (N = `coverage_service._exam_count()`, reuse — koi
  naya public wrapper nahi banaya). Out-of-range → 400.
- `GET /api/coverage-summary?class_name&subject` — saare exams 1..N + Unassigned(0)
  ek-nazar. N + bucketing service khud handle karti.
- `main.py`: import block mein `coverage` (alphabetical, brand ke baad), aur
  `taqseem.router` ke baad `include_router(coverage.router, dependencies=_api_auth)` —
  siblings jaisa protected (key unset local par unprotected, magar consistency).

Tasdeeq (hard-restart, --reload par bharosa nahi; fresh uvicorn PID par curl):
- `coverage-summary` → 200, Exam 3 planned=6 covered=1 pct=17.
- `coverage?exam_no=1` → 200, total_slos=5, remaining asal SLO data.
- khali class_name → 400; missing exam_no → 422; exam_no=99 → 400 "0..8".
git diff --stat: main.py +2; coverage.py naya. grep -c coverage.router (main.py)=1.

Agla: Marhala 5 — Tests (cross-exam coverage test sab se ahem).

## 2026-07-25 — Coverage Marhala 2-3 refinement: paper drill-down (slo_id→paper_ids)

Marhala 2-3 commit (464f975) ke baad refine kiya — mudda: coverage sirf "ye SLO covered
hai/nahi" (boolean) batati thi, "KIN papers ne cover kiya" nahi. slo-health drill-down ke
liye ye chahiye.

- `papers_repository.covered_slo_pairs()` — pehle `set` of slo_id lautata tha; ab
  `list[dict]` of DISTINCT `(slo_id, paper_id)` jodi. Ek hi query se caller membership-set
  BHI banata hai aur `{slo_id: [paper_ids]}` map BHI (do query se bacha).
- `coverage_service._assemble_coverage()` — param `papers: list` → `paper_map: dict`; har
  covered SLO ke brief mein ab `paper_ids: [...]` chip jaata. Purana top-level `"papers"`
  field hataya (ab paper_titles alag).
- `exam_coverage()` — pairs se covered_ids + paper_map banata; `list_by_exam` se alag
  `paper_titles {id: title}` map (UI paper_id ki jagah naam dikhaye).

Tasdeeq (LIVE DB, class='Pre Year 1'/Mathematics): `coverage_service` import OK;
`coverage_summary` → 8 exams + Unassigned (Exam 3 mein 1 covered); `exam_coverage(1)` →
total_slos=5, covered_slos=0, paper_titles=2, keys mein `covered/remaining/strands/
paper_titles`. git diff --stat: papers_repository +15, coverage_service +35.

Agla: Marhala 4 — Routes (GET /api/coverage + /api/coverage-summary, main.py register).

## 2026-07-24 — Coverage Marhala 3: coverage_service + exam_no threading

`app/services/coverage_service.py` (naya):
- `_assemble_coverage(planned, covered_ids, papers)` — PURE core, koi DB query nahi.
  Coverage math (covered/remaining/percent/strands) + papers attach. total=0 → pct
  None. Hissa 4 (Blueprint tajweez) isay draft question_ids ke covered_ids se reuse
  karega — is liye DB-free rakha (warna Hissa 4 mein refactor).
- `exam_coverage(class, subject, exam_no)` — DB se planned (list_planned) + covered_ids
  (covered_slo_pairs, subject/class-filtered) + papers (list_by_exam) → core ko feed.
- `coverage_summary(class, subject)` — exams 1..N + Unassigned(0). covered_pairs_all_
  exams() EK query → exam_no par bucket (N calls se bachne ko). Unassigned: planned
  count dikhta, covered HAMESHA 0. Bucketing taqseem rule (NULL/0/>N → Unassigned).
- `_exam_count()` — N = school_settings.exam_count (taqseem_service jaisa rule).

`app/services/paper_service.py`:
- `_persist_paper(...)` mein `exam_no` param + `insert(exam_no=...)`.
- CHAARON callers (balanced/adaptive/bank/ratio) ko KEYWORD args mein badla +
  `exam_no=req.exam_no`. (Positional se exam_no galat param mein jaata — is liye
  keyword lazmi.)

`app/schemas/requests.py`:
- `exam_no: Optional[int] = Field(default=None, ge=0)` teeno paper-requests mein
  (Generate/Adaptive/Bank). None = Unassigned. UI (Marhala 6) bhejega.

Design note: "paper_map" ko `papers` (list_by_exam rows) banaya — core mein display-
only passthrough, Hissa 4 draft mein [] chalega. Cross-exam correctness coverage_
summary ke bucketing mein (Marhala 5 test isi ko pakdega).

Tasdeeq (live + pure): core 2/3=67%, empty→None. exam_coverage(PY1,Math,1)=5 planned/
0 covered/2 papers (covered SLO doosre exams ke plan mein — asli cross-exam data).
coverage_summary: exam_count=8, exam3 planned6/covered1, Unassigned planned1/covered0.
Chaaron _persist_paper callers keyword (grep). Saari files ast.parse OK. git diff
--stat + grep -c 'def <fn>' = sab disk par.

Agla: Marhala 4 — routes (GET /api/coverage + /api/coverage-summary, main.py register).

## 2026-07-24 — Coverage Marhala 2: repos (exam-wise coverage data layer)

`app/repositories/papers_repository.py`:
- `insert(...)` mein `exam_no: Optional[int] = None` param + INSERT column add. Purane
  callers exam_no na bhejein to None (Unassigned) — backward-compatible.
- `list_by_exam(exam_no, subject, class_name)` — ek exam ke papers (list-view fields).
- `covered_slo_pairs(exam_no, subject, class_name) -> set` — us exam ke papers ke
  sawalon se cover hue distinct slo_id. SQL: `json_each(p.question_ids)` se JSON
  expand → `question_slo` JOIN. Membership-test ke liye set.
- `covered_pairs_all_exams(subject, class_name) -> [{exam_no, slo_id}]` — har
  (exam, slo) coverage-jodi, tagged papers (exam_no IS NOT NULL). Cross-exam data.

BUG-FIX (isi marhale mein pakda): teeno functions mein subject+class filter add.
Pehle sirf `WHERE exam_no = ?` tha → doosre subject/class ke same-exam_no papers
leak ho jaate (Pre Year 1 Math ka coverage nikaalte waqt Class 8 Urdu ke papers
bhi gin liye jaate). Ab `LOWER(TRIM(subject/class_name)) = LOWER(TRIM(?))` normalized
match (papers.class_name free-text, slo_coverage_service jaisa). class_name NULL wale
papers khud bahar. Tasdeeq: ghalat subject/class → 0, ganda-casing ('MATHEMATICS' +
'  pre year 1 ') → sahi 8.

`app/repositories/slo_exam_plan_repository.py`:
- `list_planned(class, subject, exam_no)` — us exam ka 'universe': planned SLO poore
  fields samet (slo JOIN slo_exam_plan, INNER). Ordering list_resolved jaisa.

Design: "pair" = (exam_no, slo_id). Single-exam function sirf slo_id set deta hai
(exam fix), all-exams (exam_no, slo_id) jodi.

Tasdeeq (live DB, read-only): sab import/callable. json_each chali —
covered_pairs_all_exams()=8 jodi, covered_slo_pairs(1)=set of 4, list_by_exam(1)=2
papers, list_planned('Pre Year 1','Mathematics',2)=8 SLO. git diff --stat +
grep -c 'def <fn>' = har function disk par (=1).

Agla: Marhala 3 — coverage_service.py (_assemble_coverage core + exam_coverage +
coverage_summary; exam_no threading through _persist_paper, saare callers keyword args).

## 2026-07-24 — Coverage Marhala 1-fix: papers.exam_no schema migration

Pas-manzar: Marhala 2-7 (Coverage feature) ka session ECONNRESET se toota tha; audit
mein nikla source files (coverage_service.py, coverage.py, UI, tests) gum, sirf `.pyc`
bache the. Live DB ke `papers` table mein `exam_no` column pehle se maujood tha (kisi
gum-shuda migration ne banaya), magar `database.py` mein iska koi zikr nahi tha → fresh
DB par column banta hi nahi (orphan column).

Kiya:
- Stale `.pyc` delete: `app/api/__pycache__/coverage*.pyc`,
  `app/services/__pycache__/coverage_service*.pyc` (confusion se bachne ko).
- `app/core/database.py` — papers-migration block (line ~108, `sections_meta` ke baad)
  mein idempotent add: `if "exam_no" not in papers_cols: ALTER TABLE papers ADD COLUMN
  exam_no INTEGER`. Usi `papers_cols` PRAGMA-check pattern par → live DB par dobara add
  nahi hota.

Tasdeeq: `init_db()` do baar chala (live DB) → `exam_no` count = 1, koi error nahi.
Fresh temp DB par `init_db()` → `exam_no` present = True.

Agla: Marhala 2 (repos) — papers_repository (insert exam_no, covered_slo_pairs,
covered_pairs_all_exams, list_by_exam) + slo_exam_plan_repository.list_planned.

## 2026-07-24 — Taqseem Hissa 2 / Tukda 4: taqseem.html page + nav

Maqsad: taqseem ka UI. Tukda 3 (move) browser-confirmed (move 200, range 400, restore).

Naya page `static/taqseem.html` (StaticFiles se serve — koi naya backend route nahi):
- Upar: class + subject dropdown (`/api/slo/facets` se — GET /api/taqseem dono laazmi
  maangta hai), `N = k exams` badge (`plan.exam_count`), "Sequence se auto-generate"
  button, status line.
- Board: N columns (Exam 1..N) + alag **Unassigned** column (dashed). Har chip:
  `slo_code` + strand pill + `seq k` (NULL → "seq —" warn-rang). Chip par
  **"move to exam" dropdown** (Unassigned + Exam 1..N; current selected) — drag-drop
  NAHI (tay-shuda).
- Move: `change` par `POST /api/taqseem/move {slo_id, exam_no}` (position nahi bhejte →
  None; **siblings shift nahi hote**, position sirf ishara). Har move ke baad plan reload
  (source-of-truth server).
- Auto-generate: custom confirm modal (native `confirm()` nahi) — count dikhata hai
  kitne SLO abhi exams mein rakhe hain (yehi tarteeb overwrite hogi). Confirm ke baad
  `POST /api/taqseem/generate`; result mein backend ka theek `assigned/unassigned/
  overwritten` status line par.
- Nav "Exam Taqseem" (i-blueprint icon) **Learning Outcomes ke baad** — jin 3 pages ke
  nav mein SLO link tha (`index.html`, `slo.html`, `slo-health.html`) unmein add.

**Dead-code trap se bacha (Jul 24 ka sabaq):** har function ek hi jagah define, ek hi
call — koi `_orig… = fn; fn = wrapper` reassignment nahi. Move dropdown **event
delegation** par (`board` ka `change`), koi inline `onclick`/`JSON.stringify`-in-markup
nahi (frontend onclick-markup trap se door).

Verify (read-only): taqseem.html tag-balanced + inline JS `node --check` OK; teenon
nav-edited pages tag-balanced, har ek mein 1 taqseem link. **Khud test nahi kiya** — user
browser se. Server fresh `--reload` zaroori (Tukda 2/3 routes + naya page).

## 2026-07-24 — Taqseem Hissa 2 / Tukda 3: POST /api/taqseem/move (per-move)

Maqsad: ek SLO ka assignment badalne ka route (drag/drop ke liye). Tukda 2 (generate)
browser-confirmed — plan sahi bana (exam 1: seq 1-7, exam 2: seq 8-14, split 7/7/6×6).
Sirf route; page Tukda 4 mein.

Body: `{slo_id, exam_no, position?}`. Usool:
- `exam_no 0` = Unassigned (valid). Range `0 <= exam_no <= N` (N global). Bahar → **400**.
- `slo_id` DB mein na ho → **404**. `position` optional (None = get_plan sequence par
  fall back). Sirf isi SLO ki row upsert — siblings ki positions nahi chhedi jaatin
  (re-pack Tukda 4 ka kaam).

Changes:
- `app/repositories/slo_repository.py` — naya `find_by_id()` (existence check;
  questions_repository jaisa).
- `app/services/taqseem_service.py` — naya `move_slo()` + `SloNotFoundError`. Range
  check pehle (ValueError), phir existence (SloNotFoundError), phir `overwrite_assignments`
  se ek-row upsert (Tukda 2 ka bulk-upsert dobara istemaal).
- `app/schemas/requests.py` — `TaqseemMoveRequest {slo_id, exam_no, position?}`.
- `app/api/taqseem.py` — `POST /api/taqseem/move`; SloNotFoundError→404, ValueError→400,
  baaqi→500.
- `tests/test_taqseem_move.py` — 10 test: move to exam, exam_no 0, position optional,
  >N & negative reject, missing slo, route 200/400/404.

Verify: move+generate suites **16 passed**. **Move khud NAHI chalaya** — user browser se.
Server fresh `--reload` zaroori (naya route) — warna 404/stale (aaj chauthi dafa stale-server).

## 2026-07-24 — Taqseem Hissa 2 / Tukda 2: POST /api/taqseem/generate (auto-split)

Maqsad: ek (class, subject) ke SLO ko **sequence** ke hisaab se N exams mein khud-ba-khud
baant do (Tukda 1 = read-only GET pehle browser-confirmed ho chuka).

Split usool:
- `sequence` NULL wale SLO **kisi exam mein NAHI** jaate — `exam_no 0` (Unassigned)
  rehte hain (in ki asal teaching-tarteeb maloom nahi). Chahe pehle manually assign
  the, regenerate unhe 0 par le aata hai.
- baaqi SLO **sequence ASC** par (tie → slo_code, deterministic): `total` = un ki
  ginti, `base = total//N`, `rem = total%N`. Pehle `rem` exams ko `base+1`, baaqi ko
  `base`. (misal total=50, N=8 → do exam 7, chhe exam 6.)
- Poora regenerate: har SLO ka row upsert. `overwritten` = kitne SLO ka pehle se plan
  row tha (frontend confirm/summary ke liye) — pehli dafa 0, dobara sab.

Changes:
- `app/repositories/slo_exam_plan_repository.py` — naya `overwrite_assignments()`:
  `executemany` + `ON CONFLICT(slo_id) DO UPDATE` (class_print_settings jaisa pattern),
  ek transaction/commit. Sirf likhna — split logic service mein.
- `app/services/taqseem_service.py` — naya `generate_plan()`: `list_resolved()` se
  rows, `_exam_count()` se N, split compute, exam_no 0 for NULL-seq, counts wapas.
- `app/schemas/requests.py` — `TaqseemGenerateRequest {class_name, subject}` (N global,
  body mein nahi).
- `app/api/taqseem.py` — `POST /api/taqseem/generate`; blank class/subject → 400
  (GET /api/taqseem jaisa), DB error → 500.
- `tests/test_taqseem_generate.py` — 7 test: even/uneven split, NULL-seq unassigned,
  sequence-not-slo_code ordering, overwritten count, N>total, blank-class 400.

Verify: naye 7 test pass; related suites (api_routes + slo_repo + class_print) **93
passed**, koi regression nahi. **Generate khud NAHI chalaya** — user browser se karega
(fresh `--reload` server zaroori, warna naya module load na ho — dekho Jul 24 stale-server sabaq).

Symptom: Class Size save (DB=30, GET confirm) magar F5 ke baad field 25 dikhata. Do cache
theories (server no-store, phir client no-store — neeche wali entries) **galat** thi;
data kabhi clobber nahi hua. Asal wajah frontend mein thi:

`static/index.html` mein `loadSchoolSettings` DO baar mojood tha —
- L1302 original `async function loadSchoolSettings()` (sirf identity fields set karta,
  classSize NAHI), aur L1340 par **call**.
- L2595-2596 par baad mein `_origLoadSchoolSettings = loadSchoolSettings; loadSchoolSettings
  = async function(){…}` — wrapper jo classSize/minAnalysisPct/weakTopicThreshold populate
  karta tha.
- Magar ekloti call (L1340) reassignment se PEHLE chalti thi → hamesha **original** chalta,
  **wrapper kabhi call nahi hota** (dead code). Natija: classSize field kabhi server se load
  hi nahi hota → har F5 par HTML default `value="25"`. (Instrumentation ne sabit kiya:
  console mein sirf ORIGINAL log aaya, WRAPPER ka kabhi nahi.)

Fix: wrapper + reassignment poora delete; classSize/minAnalysisPct/weakTopicThreshold
populate ab **isi** original `loadSchoolSettings` ke andar (logo ke baad). Ab ek hi
function, ek hi call. Saari [PM-DEBUG] instrumentation (frontend 4 + backend 2) nikaal di.

Verify (read-only, koi POST nahi — user khud browser se test karega): served index.html
mein PM-DEBUG=0, wrapper=0, `loadSchoolSettings`=2 (1 def+1 call), classSize-in-load=1.
index.html tag-balanced; backend import OK; server clean restart. Data salaamat (logo
97491, class_size 30).

Alag masla (isi din): meri adhoori curl POST ne school_settings wipe kar diya tha
(address/logo/email/principal) — logo backup se surgical single-column UPDATE se restore
(baaqi untouched); backup `paper_maker_backup_before_logo_restore_20260724_084757.db`.
Sabaq: `/api/school-settings` merge-less POST (sirf kuch fields) baaqi ko pydantic-defaults
par reset kar deta — test/verify ke liye kabhi partial POST na karo.

Note: neeche ki do "Cache-Control / stale-UI" entries asal bug ka hal nahi thi, magar woh
headers (api no-store, HTML/JS/CSS no-cache, client cache:'no-store') sahih hygiene hain —
rakhe gaye.

## 2026-07-24 — Stale-UI fix ka round 2: client cache:'no-store' + JS/CSS no-cache

Pichhla fix (server no-store/no-cache) kaafi na tha — bug baqi raha. Do asal wajah:
1. **fetch() purani cached entry reuse karta tha.** Server ab no-store deta hai, magar us
   se PEHLE (jab koi Cache-Control nahi tha) browser ne `/api/school-settings` cache kar
   liya tha; `fetch()` default mode us stored entry ko bina revalidate reuse karta hai.
   Natija: merge se pehle wala GET **stale** → `saveSchoolSettings` purani `class_size`
   dobara POST → clobber. (DB mein 30 sirf isliye ke aakhri save Class Settings ka tha —
   user ne theek pakda.)
   Fix (`static/apiClient.js`, single choke-point): `_rawFetch` par default
   `cache:'no-store'` (`Object.assign({cache:'no-store'}, opts, {headers})`, opts override
   kar sakta hai). loadSchoolSettings + dono merge GET + print.html ka GET + har API call
   ek saath cache-proof.
2. **apiClient.js khud stale ho sakti thi.** Woh alag JS file hai; pichhla middleware sirf
   `text/html` par no-cache lagata tha, is liye external JS par koi Cache-Control nahi →
   naya no-store code hi load na hota.
   Fix (`app/main.py`): no-cache branch ab HTML + JS + CSS teenon par (`_NO_CACHE_TYPES =
   text/html, javascript, text/css`; content-type match). Immutable webp/fonts pehle
   branch mein mehfooz.

Verify (curl matrix): `/api/*` no-store; `/`, `index.html`, `print.html`, `apiClient.js`,
`app.css` no-cache; library webp abhi bhi immutable. Served apiClient.js mein naya code
mojood. Clean restart (--reload par bharosa nahi). Tests: api_routes **58 passed**.
Ahem: user ko ek dafa **Ctrl+F5** karna hoga taake purani cached apiClient.js/index.html
nikal jaye; uske baad no-cache khud maintain karega.

## 2026-07-24 — Cache-Control: /api no-store + HTML no-cache (stale-UI fix)

Symptom: Class Size 25→30 Save (✅), phir identity "Settings save karen", F5 → Class Size
wapas 25. **Data theek tha** — `GET /api/school-settings` DB mein 30 deta tha; UI purana
cached GET response padh raha tha. Root cause: StaticFiles/API responses par koi
`Cache-Control` header nahi tha (sirf ETag/Last-Modified) → browser heuristic caching se
normal F5 par purana `index.html`/JS aur purana API JSON serve kar deta (stale merge-code
bhi = "merge kaam nahi kiya" jaisa lagta, halaanki code theek tha).

Fix (`app/main.py`, mojooda immutable-assets middleware extend kiya, rename
`_cache_control_headers`, priority order):
1. `/library/*.webp` + `/static/fonts/*.woff2` → `public, max-age=31536000, immutable`
   (pehle se, **untouched** — jaan-boojh kar; filename UUID/font kabhi nahi badalta).
2. `/api/*` → `no-store` (API kabhi cache na ho).
3. HTML documents (content-type `text/html`) → `no-cache` (har load revalidate; stale JS band).

Verify: curl headers — `/api/school-settings` no-store, `/` + `/static/index.html` +
`/print.html` no-cache, library webp abhi bhi immutable (na toota). Server clean restart
(--reload ne main.py change flaky uthhaya tha — fresh start se yaqeeni). Tests:
api_routes + settings **62 passed**. Browser re-test (Class 25→30 → Save Class → identity
Save → F5 → 30 rehna) hard-refresh ke baad user karega.

## 2026-07-24 — School Settings: identity (phone/email/principal) + academic session

Maqsad: School Settings page ko extend karna — A) identity (phone, email, principal),
B) academic session (start month, exams N). Naya page/table NAHI: `school_settings`
singleton (id=1) aur mojooda `settings` screen pehle se the, sirf extend kiya.

Backend:
- `app/core/database.py` — 5 idempotent `ALTER TABLE ADD COLUMN` (wahi migration
  pattern): `phone TEXT ''`, `email TEXT ''`, `principal_name TEXT ''`,
  `session_start_month INTEGER 3` (March), `exam_count INTEGER 8`. ADD…DEFAULT purani
  row (id=1) ko backfill kar deta hai.
- `app/schemas/requests.py` — `SchoolSettings` model mein yehi 5 fields defaults ke sath.
- `settings_repository.upsert()` + `settings_service.save_settings()` — pass-through
  (INSERT + ON CONFLICT UPDATE dono). Routes (`GET/POST /api/school-settings`) schema-
  driven the, isliye naye nahi banaye — fields khud flow karte hain.

Frontend (`static/index.html` settings screen):
- Card A (identity) mein Phone / Email / Principal name (principal par "record only —
  print par nahi" note). Card B (Academic Session) naya: Session start month (dropdown,
  default March) + Number of exams N (default 8).
- `saveSchoolSettings()`: (1) `school_name` REQUIRED — khali par block + focus, save nahi.
  (2) ab **merge-safe** — pehle GET kar ke `Object.assign(existing, {...})`, taake identity
  save `class_size`/`print_*` ko model-defaults par clobber na kare (ye pehle latent bug
  tha; Class Settings save already merge karta tha). `loadSchoolSettings()` naye fields
  populate karta hai.

print.html letterhead: address ke neeche `.contact` line — phone · email (jo mojood ho).
principal print par NAHI (record-only, user ka faisla). exam_count → taqseem N wiring
JAAN-BOOJH kar chhoda (Hissa 2 mein).

Verify: migration real DB par chali (5 column + defaults backfill confirmed). API round-
trip (POST→GET) sab naye fields persist. Merge-safety: class_size=30 set ho kar bacha
raha. Poora suite **833 passed**. index+print.html tag-balanced (headless parse). Server
fresh restart (migration ke liye), DB wapas Test-School defaults par saaf chhoda.
Browser click-verify baqi (extension off) — hard-refresh ke baad.

## 2026-07-24 — Ops: sequence import "Updated:50" magar seq NULL — stale server

Alaamat: teacher ne sequence-wali Excel import ki, "Updated: 50, Errors: 0" mila,
magar `/api/slo` aur DB dono mein saari 50 `sequence` NULL. DB file ka mtime import
ke baad bhi purana (Jul 23 21:21) — yani us DB par aaj koi write hi nahi hua.

Diagnosis:
- Do uvicorn processes chal rahe the (PID 21160, 38148), dono ka `cwd` repo, `DB_PATH`
  unset → **dono ek hi** `paper_maker.db` par. Sirf 38148 :8000 par bind tha.
- Dono **Jul 23 18:34** ke — yani `sequence` ka code (jo isi 23 ko baad mein aaya) is
  running process mein load hi nahi tha. uvicorn `--reload` ke baghair chala tha, is liye
  purana `slo_import_service` module memory mein reh gaya (slo_text/bloom/strand update
  karta tha, sequence nahi → "Updated:50" sach tha magar seq NULL).
- Disk code sahi sabit hua: DB ki temp copy par poora import path chalaya → `updated:1,
  errors:0`, DB ne `sequence=99` wapas diya.

Hal: dono purane process band → fresh `uvicorn --reload` (PID naya). Teacher ne dobara
import kiya → (1) `POST /api/slo/import 200` access-log mein, (2) DB mtime badla
(Jul 24 06:38), (3) seq non-null **50/50**. Phir taqseem N=8 sahi chala (4 mixed,
4 single-strand; ab strand-boundary par mix, alphabetical artifact nahi).

Sabaq: `sequence`/naye feature ke baad server hamesha restart (ya `--reload` ke saath
chalao); warna "Updated" report sach hote hue bhi naye columns skip ho sakte hain.

## 2026-07-23 — SLO: `sequence` column (asal kitab ki tarteeb)

Maqsad: taqseem (exam distribution) `slo_code` se sort karta tha, magar slo_code
**strand-grouped** hai (C→D→N→S→W), teaching tarteeb nahi. Nateeja: Number strand
akela 25/50 SLO hone se **4 exam sirf Number** ke ban rahe the. Asli tarteeb sirf
teacher jaanta hai — is liye teacher ke bharne ke liye alag `sequence` column.

Changes:
- `app/core/database.py` — `init_db()` mein idempotent migration: `slo` table mein
  `ALTER TABLE ADD COLUMN sequence INTEGER` (nullable). Purani 50 rows NULL rehti hain.
- `app/repositories/slo_repository.py` — `insert()` mein `sequence` column+value.
  `update_by_code()` generic tha (koi change nahi) — re-import par sequence refresh.
- `app/services/slo_import_service.py` — `sequence` optional column parho: khali→NULL,
  poora number→int (Excel "3.0" bhi qubool), **number na ho ("abc"/"2.5")→row error**
  (chupke null nahi). Add + update dono paths mein sequence.
- `static/slo_import_template.xlsx` — purana (ignored) `book_pages` column hataya,
  `sequence` add. Sample rows teaching-order (W,N,C,S = seq 1,2,3,4) dikhate hain.
- `static/slo.html` — list mein pehla **"Seq"** column (NULL → "—" muted, taake teacher
  dekh sake kaunse khali). Import hint text update (book_pages hata, sequence likha).
- `scripts?/taqseem.py` (scratchpad standalone) — sort ab `sequence` se, NULL par
  slo_code fallback (aakhir mein); report top par kitne NULL saaf batata hai. N configurable.

Verify: migration real DB par chala (sequence column + 50 NULL confirmed). Import
end-to-end test (valid/float/empty/invalid/re-import) sahi. Naye 5 sequence tests +
poora SLO suite: **104 passed**. Koi DB data change nahi (sirf nullable column add).

Agla step (manual): teacher/user Excel mein sequence bhar kar re-import karega →
50 rows update; phir taqseem asal teaching order se banega.

## 2026-07-23 — UI: pdfSubject free-text → datalist (KAAM 3)

Scan ke baad KAAM 3 mein asal mein sirf **ek** field bacha tha (alag phase nahi, chhota
add-on): `pdfSubject` (index.html Syllabus Upload). `exSubject`/`fSubject` KAAM 2 mein ho
gaye; generator ka `subject` (index.html:429) cascade se auto-bharta hai — chhoda.

Fix (`static/index.html`):
- `pdfSubject` → `<datalist>` (pdfGrade jaisa hi). CREATION field hai (naya subject ka
  syllabus yahin add hota hai), is liye strict dropdown nahi — maujooda subjects suggest,
  naya likhna bhi allowed.
- `loadSyllabusGrades()` mein `fillDatalist()` helper — ab pdfGrade + pdfSubject dono
  `_allGrades` se bharte hain.

Verify: index.html tag-balanced (headless parse); wiring (list=+datalist+fillDatalist)
match. Backend change nahi (frontend-only). Browser click verify baqi — extension off.

## 2026-07-23 — UI: class fields free-text → dropdown (KAAM 2)

Maqsad: free-text class/subject se data bikhar jata tha — 'Pre year 1' vs stored
'PRE YEAR 1'. Aaj isi wajah se SLO list KHALI dikhi thi. Root cause: SLO list filter
(`slo_repository.list_by_filters`) **EXACT** match karta hai (`class = ?`), zara sa
farq = 0 rows.

Ahem: SLO ka class/subject syllabus ke `grade` se **alag vocabulary** hai (SLO Excel ke
apne `class,subject` columns). Is liye dropdown syllabus-grades se NAHI — SLO table ke
asal distinct values se banaya.

Backend:
- `slo_repository.list_distinct_facets()` — DISTINCT class + subject (non-empty, sorted).
- `GET /api/slo/facets` → `{classes, subjects}` (sibling `list_slos` jaisa unwrapped read).

Frontend (`static/slo.html`):
- `fClass`, `fSubject`, `exSubject` free-text input → `<select>`. `exGrade` (pehle se
  select) ab syllabus-grades ke bajaye facets.classes se bharta hai — export bhi SLO data
  se match kare.
- `loadExportGrades()` (syllabus-grades) → `loadFacets()` + `fillFacetSelect()` (facets).
  Chaaron dropdown ek hi `/api/slo/facets` call se.

Frontend (`static/index.html` — Syllabus upload):
- `pdfGrade` ye CREATION field hai (naya class ka syllabus yahin add hota hai) — strict
  dropdown naye class ko block kar deta. Is liye `<datalist>` (input + maujooda grades
  suggest, naya likhna bhi allowed). `_allGrades` se populate (already loaded).
- `pdfSubject` + baaqi subject fields = KAAM 3 (alag phase).
- Cosmetic label fields (`bpClass` bank.html, `bpClassName` blueprint.html) — chhode,
  ye paper par chhapne wale roster naam hain, data se link nahi.

Verify: `/api/slo/facets` → `{"classes":["Pre Year 1"],"subjects":["Mathematics"]}`;
`/api/slo?class_name=Pre Year 1&subject=Mathematics` → rows aate hain (exact match ab
dropdown se guaranteed). Teenon pages HTML tag-balanced (headless parse). 828/828 tests pass.
Browser click verify NAHI ho saka — Chrome extension connected nahi tha.

## 2026-07-23 — UI: bank.html "Naya question add karo" form collapsible (KAAM 1)

Maqsad: teacher zyadatar Excel se questions add karta hai — manual add form roz nazar
aane ki zaroorat nahi, sirf jagah gherta tha. Ab `print.html` ke Print Settings jaisa
`<details>` pattern, default **BAND**.

Fix (`static/bank.html`):
- "Naya question add karo" card (`<div class="card">`) → `<details class="card add-q-collapse"
  id="addQCard">` + `<summary class="add-q-summary">` (arrow + title + hint). Andar ka
  poora content ek `<div class="add-q-body">` mein wrap. Koi ID/JS/handler nahi badla —
  form waisa hi kaam karta hai, sirf collapse hua.
- CSS: summary marker hidden, `[open]` par arrow rotate + border-bottom, body padding.

## 2026-07-23 — Data cleanup: dummy/trial data DB se hataya

Maqsad: trial data saaf, sirf asal seed rakhna. ("class" = syllabus_topics.grade via
syllabus_topic_id; questions table mein direct class column nahi.)

RAKHA: Pre Year 1 Mathematics 329 questions, saare 50 SLOs, 329 question_slo links
(sab Pre Year 1 ke), Image Library (99) — poori, syllabus_topics, blueprints (2),
usage_log (99).

DELETE (single transaction, guards ke sath): ALL papers (72), class null/empty
Mathematics questions (60) + Pre Year 2 (40) + Pre Year 3 (20) = 120 questions +
unke question_slo links (0 the). Orphan trial results bhi (user ne "sab delete"
chuna): result_uploads (14) + student_question_results (840).

Nateeja: questions 449→329, papers 72→0, results 0, SLO 50 (unchanged), question_slo
329 (unchanged), image_library 99 (unchanged). Verify: live API 329; 0 non-Pre-Year-1
baaqi; 0 dangling question_slo (dono taraf). Backup (user ke apne backup ke ilawa,
sqlite .backup se consistent): `paper_maker_backup_before_dummy_cleanup_20260723_172026.db`.

## 2026-07-23 — Fix: bank.html Edit button dead (onclick markup toota)

Symptom: Question Bank mein **Edit** dabane se kuch nahi hota (Delete theek — confirm
+ orphan warning). Script parse ho rahi thi (Delete chalta tha), masla generated
markup mein tha.

Wajah: `renderQRow` mein Edit button ka onclick
`openEditModal(${escAttr(JSON.stringify(q))})` tha. `JSON.stringify` **double quotes**
deta hai (`{"id":...}`) aur `escAttr` sirf single quote escape karta hai — double-quoted
`onclick="..."` attribute pehle hi `"` par **toot jata** tha → handler `openEditModal({`
ban jata (invalid JS) → click par kuch nahi. (Delete safe tha kyunki UUID mein quote
nahi.) `node --check` isse nahi pakadta — bug JS syntax mein nahi, HTML markup mein tha.

Fix (`static/bank.html`):
- Edit onclick ab Delete jaisa: `openEditModal('${escAttr(q.id)}')` (id string).
- `openEditModal(q)` ab string aane par `_allQuestions` se lookup karta hai (JSON.parse
  path hata — UUID JSON nahi).

Verify: node --check clean; VM mein real HTML id-set + missing-id→null getElementById ke
sath `openEditModal('<id>')` sab 5 types (mcq/tf/fill/short-answer + Urdu `"quotes"&<b>`
wala) par bina throw OK; koi missing element id nahi. Static file live — sirf hard-refresh.

## 2026-07-23 — Marhala 2B: Blueprint Bloom shortfall (soft guidance)

Maqsad: Blueprint se paper banate waqt paper ka ASAL Bloom mix class-standard se
compare → kisi Bloom level par **10% se ZYADA** farq ho to teacher ko soft guidance
+ 2 option (Ignore / Questions badlo). App khud kuch adjust NAHI karta.

**Ahem faisle:**
- Bloom source = **question ka apna `bloom_level`** (Question Bank wala), SLO ka NAHI
  (SLO-based per-paper wala purana `slo_shortfall_service` alag hai — chheda nahi).
- `bloom_level` khali/na-maloom questions **alag gine** (`no_bloom`); percentages
  sirf `with_bloom` par (warna numbers jhoot bolenge).
- Threshold strictly > 10 (epsilon se float-noise ignore) — **theek 10% par warning NAHI**.
- Class→tier: `bloom_standards.get_bloom_suggestion` (reliable source = syllabus
  `grade`, na ho to free-text `class_name`).
- Option 2 = **pointer-only** (user faisla): under-represented Bloom ke liye bank-count
  + `/bank.html?subject&bloom` filtered link; koi inline replace nahi.

**Backend:**
- `app/services/blueprint_bloom_guidance_service.py` (naya) — `compute_bloom_guidance(
  questions, class_tier, subject)`. subject=None → bank-count skip (pure/testable).
  Graceful: class na ho / tier na mile / `with_bloom==0` → `available False` + message.
- `app/services/blueprint_paper_service.py` — `assemble_blueprint_paper` mein
  `class_tier` param + return mein `bloom_guidance`.
- `app/schemas/requests.py` — `BlueprintPaperRequest.grade` (tier ke liye).
- `app/api/papers.py` — `class_tier = resolved_grade or class_name` resolve + pass.
- `tests/test_blueprint_bloom_guidance.py` (naya, 16 tests) — mix/empty-alag,
  case-insensitive, per-tier shortfall, boundary theek-10%, all-empty graceful,
  bank-pointer (seeded), 2× `/api/blueprint-paper` integration.

**Frontend:**
- `static/blueprint.html` — makePaper `grade` bhejta hai; `#bloomGuidance` panel
  (`renderBloomGuidance`) sirf `available && has_shortfall` par; no_bloom note,
  per-Bloom rows, "Ignore karo" (hide) + "Questions badlo" (bank pointers reveal).
- `static/bank.html` — `applyUrlListFilters()`: `?subject&bloom` se list pre-filter.

**Verify:** `pytest tests/test_blueprint_bloom_guidance.py` 16 green; blueprint+api
regression suites 157 green. **Browser test baaqi — server RESTART ke baad** (naya
`grade` field + guidance panel).

## 2026-07-23 — Marhala 4B: live print controls (sidebar stepper + POST save)

Maqsad: teacher print.html sidebar mein 3 knobs hilaye → preview foran badle
(setVar, koi fetch) → "Is class ke liye mehfooz karein" par DB likhe (auto-save
nahi) → Reset global default par (visual-only, DB untouched).

**Backend (POST):**
- `app/schemas/requests.py` — naya `ClassPrintSettingsSave` (class_name + font_size
  11–20 / q_gap 6–30 / page_margin 10–25, `Field(ge/le)` → out-of-range 422).
- `app/services/class_print_settings_service.py` — naya `save_print_settings()`:
  normalize_class, blank class → ValueError (route 400), warna repo.upsert (4A wala).
- `app/api/school_settings.py` — naya `POST /api/print-settings` (StatusResponse;
  ValueError→400, baaqi→500). GET/repo 4A se.
- `tests/test_class_print_settings.py` — POST: roundtrip, normalization, upsert
  overwrite, blank→400, out-of-bounds→422 (6 params, value persist bhi nahi hoti),
  boundary font accept. Total file ab 28 tests.

**Frontend (print.html):**
- `.options` font-size → `calc(var(--q-font) - 1px)` — **user faisla:** options bhi
  scale hon (font bara = bachcha jawab bhi padh sake). `.marks`/`.sec-title` waise.
  Default 14 par 13px = pehle jaisa.
- Sidebar mein `<details class="print-settings no-print">` — 3 stepper controls
  (+/− buttons, min/max par disabled), Save + Reset, status + hint line. Collapsible
  ([[project-papermaker-kaam-b-collapse-manual-add]] pattern). `.app-sidebar` par
  `overflow-y:auto` (khulne par clip na ho).
- JS: `PRINT_BOUNDS` (UI limits = schema mirror), `_printState`/`_printGlobalDefaults`/
  `_currentClassName`. `stepPrint` → clamp + setVar foran. `applyPrintSettings` (4A)
  extend: resolved values se controls init + Save UI configure (class na ho to Save
  disabled). `resetPrintSettings` → global default (visual). `savePrintSettings` →
  POST, inline feedback (koi alert nahi). `_printGlobalDefaults` loadPaper mein
  school-settings ke print_* se.

**Control type:** stepper +/− (non-tech teachers ke liye — sirf valid steps, bade
tap-target). **Feedback:** inline status line (✓ mehfooz / err), koi browser-dialog nahi.

**Verify:** POST tests + `pytest` (poora suite) 812 green; `ruff` clean; inline
JS `node --check` OK. **Browser test — server RESTART ke baad** (naya POST route).

**Browser test follow-up (2026-07-23):**
- Layout bug: sidebar flex-column mein `.print-settings` (details) shrink ho raha tha
  → summary+ps-body side-by-side, buttons wrap. Fix: `.print-settings { width:100%;
  box-sizing:border-box }` + `summary { display:block }`. (CSS-only.)
- POST 405: code theek — current app ke openapi mein `['get','post']` dono, TestClient
  POST=200. 405 = live server abhi **purana 4A code** (sirf GET) chala raha tha (GET+405
  combo = stale process ki nishaani). Hal: sahi process kill karke restart. Code bug nahi.

## 2026-07-23 — Marhala 4A · Commit 3: print.html CSS vars + JS apply (+ tests)

Maqsad: backend ke resolved print settings ko print.html par CSS vars se apply.

- `static/print.html` — (1) `:root` mein `--q-font: 14px`, `--q-gap: 14px`
  (`--page-margin` Commit 1 se). (2) `.question` gap → `var(--q-gap)`; `.qhead`
  + `.qtext-en` → `var(--q-font)`; `.qnum` → `calc(var(--q-font) + 1px)`;
  `.qtext-ur` → `calc(var(--q-font) + 2px)` (Urdu +2, qnum +1 nisbat barqarar).
  (3) naya `applyPrintSettings(className)` — `GET /api/print-settings?class_name=`
  fetch, `setVar` se font(px)/gap(px)/margin(mm) apply; fetch/JSON error par
  silent (defaults CSS mein pehle se). `loadPaper` mein `paper.class_name` ke
  saath await.
- `tests/test_class_print_settings.py` (naya, 16 tests) — migration columns
  DEFAULT 14, resolution (fresh default, global fallback, blank/None class,
  class-row override, normalization "Class 5"/"class 5"/" CLASS 5 ", other class
  → global, upsert replace), aur endpoint (global/override/no-param).

**Defaults par diff-zero:** `--q-font 14 / --q-gap 14 / --page-margin 14mm` =
purani hardcoded values → koi class-override na ho to output bilkul waisa.

**Verify:** `pytest` = **800 passed** (poora suite). Browser test baaqi (server
restart ke baad — neeche).

## 2026-07-23 — Marhala 4A · Commit 2: per-class print settings backend + chain

Maqsad: 3 print knobs (font_size, q_gap, page_margin) per-class store + resolve.
Row-level fallback: class ki row ho to woh, warna school_settings ke global
defaults. UI 4B mein; yeh sirf backend + endpoint.

- `app/core/database.py` — (1) school_settings migration mein 3 naye global-default
  columns `print_font_size/print_q_gap/print_page_margin` (DEFAULT 14 = maujooda
  print.html values, purana output na badle). (2) naya `class_print_settings` table
  (`class_key` PK = normalize_class(class_name); font_size/q_gap/page_margin NOT NULL).
- `app/schemas/requests.py` — `SchoolSettings` mein 3 fields (default 14).
- `app/repositories/settings_repository.py` — `upsert` mein 3 columns (accent jaisa).
- `app/services/settings_service.py` — `save_settings` 3 fields pass karta hai.
- **naya** `app/repositories/class_print_settings_repository.py` — get(class_key)/upsert.
- **naya** `app/services/class_print_settings_service.py` — `get_print_settings(class_name)`:
  normalize_class → class row → warna global. Row-level fallback.
- `app/schemas/responses.py` — naya `PrintSettingsResolved` (font_size/q_gap/page_margin).
- `app/api/school_settings.py` — naya `GET /api/print-settings?class_name=` (auth same router).

**Verify:** temp-DB smoke (real DB safe) — fresh default 14/14/14, global override,
class-row wins + normalization ("class 5"=="Class 5"==" CLASS 5 "), aur other/empty/None
class → global fallback. `pytest tests/test_settings_repository.py tests/test_api_routes.py`
= 62 passed. Client-side (print.html JS apply) = Commit 3.

**Baaqi:** naye service/endpoint ke liye dedicated test abhi nahi likha (existing pass;
smoke se cover) — chaho to Commit 3 se pehle add kar dun.

## 2026-07-23 — Marhala 4A · Commit 1: print margin bug (28mm → 14mm)

Maqsad (per-class print settings feature ka Commit 1 — sirf bug fix, aage nahi barha).
Bug: `print.html` mein `@page { margin: 14mm }` **+** `.sheet { padding: 14mm }`, aur
`@media print` mein `.sheet` padding reset nahi hota tha → chhapte waqt asal margin
14+14 = **28mm** ban raha tha.

**Faisla (plan §0 — single source):** `@page` margin `0`, saara page-margin `.sheet`
padding se, `var(--page-margin)` (default `14mm`). Isse bug bhi theek aur aage
`page_margin` setting ke liye mechanism bhi tayyar (throwaway `padding:0` nahi likha).

- `static/print.html` — 3 edits: (1) `@page` margin `14mm→0` (2) `:root` mein
  `--page-margin: 14mm` (3) `.sheet` padding `14mm → var(--page-margin)`.
- `@media print` block chhua nahi — padding ab var se aata hai (14mm), single source.

**Asar:** har paper ka print margin 28→14mm (yeh deliberate correction, user ne manzoor
kiya). Font/spacing waghera bilkul waise hi — koi aur farq nahi. Sirf CSS, koi
backend/JS nahi. User browser test karega.

**Note (4B ke liye):** `export_service.py` (DOCX/python-docx + PDF/LibreOffice) apna
**alag** layout render karta hai — Word default ~1inch margin, yeh CSS use hi nahi karta.
4A/print.html ke settings export par apply NAHI honge. Teacher kis raaste se print karta
hai (browser vs export) — 4B se pehle confirm karna.


## 2026-07-21 — feature/print-shortfall (print.html panel + sections_meta persistence)

Maqsad: print.html blueprint jaisa shortfall payghaam dikhaye (reason + read-only
options), do jagah alag wording ka khatra khatam. Masla (pichle session ka STOP):
`shortfall_details` (reason/options) DB mein **mehfooz nahi hoti** — assembly ke waqt
banti hai phir discard. Sirf `sections_meta` bachti hai (heading/question_ids/marks/
shortfall-int). Isliye backend change laazmi tha.

**Faisla (Option 1):** reason/options ko **`sections_meta` ke andar** hi rakho (alag
column/migration nahi). Short section par hi keys aati hain; poore section par bilkul nahi.

- `app/services/blueprint_paper_service.py` — short section ki meta mein `shortfall_reason`
  + `shortfall_options` embed (`diag` se). Full section = keys hi nahi.
- `static/print.html` — naya `sectionShortfallHtml(sec, gotCount)`: `shortfall_reason` ho
  to panel (heading + wajah + read-only options), warna **purana numeric note**
  (`{wanted} maange, {n} mile`). Options **clickable nahi**. Naya `.shortfall-panel`
  CSS (`display:block` — `.no-print` ke inline-flex ko override).
- `tests/test_blueprint_shortfall_reason.py` — `TestSectionsMetaPersistence` (short →
  reason+options meta mein; full → keys absent).

**SHART (poori hui):** purane papers ke `sections_meta` mein reason/options nahi →
**numeric-note fallback** chalta hai (bilkul pehle jaisa). `.no-print` usool bar-qarar —
dono branch screen-only, kaghaz par kuch nahi.

**Real-DB check:** 79 papers, 0 JSON parse-fail, 0 shape-issue → koi page nahi tootta.
27 legacy short-sections (shortfall>0, no reason) → numeric note. 0 sections mein abhi
reason (kuch regenerate nahi hua).

**Verify:** **784 tests pass, ruff clean.** (Uncommitted working-tree changes — commit
Irfan ke kehne par.) Browser render (panel + Ctrl+P par note gayab) baqi — Irfan ka test.

## 2026-07-21 — feature/design-base (Brand config + local fonts + icon sprite)

Sirf **tanzeem** ka kaam — **koi visual badlaav NAHI**, pages bilkul pehle jaise. Teen
QADAM, teen alag commits. Maqsad: branding ek jagah se, app fully offline (fonts local),
aur nav icons ek sprite se.

**QADAM 1 — Brand config:**
- `config/brand.json` (Parcha / "Parcha Paper Maker" / "Exam paper generator" / colours).
- `app/services/brand_service.py` — **startup par ek dafa** parhta hai (module-load), file
  missing/kharab ho to **crash NAHI** — safe defaults + `uvicorn.error` warning. `get_brand()`.
- `GET /api/brand` (`app/api/brand.py`, `BrandResponse` schema). **Jaan-boojh kar auth ke
  bahar (public)** — cosmetic shell hai (koi secret/DB/AI-cost nahi) aur har page load par
  chahiye; auth ke peeche hota to key set hone se pehle har page par key-gate khul jata.
- `static/js/brand.js` — `/api/brand` se `document.title` (`<page> — full_name`) + sidebar
  `.brand .name` set. Defaults baked (config jaise) → fetch fail par bhi sahi text, **koi FOUC nahi**.
- Sab 7 pages: `<body data-page="...">`, hardcoded **"AII Smart Paper Maker" → "Parcha Paper
  Maker"**, brand.js include. (`.brand .name` par **full_name** dikhta hai — pehle jaisa full
  naam.)
- `index.html`: `.sidebar` → **`.app-sidebar`**, `.nav-link` → **`.app-nav a`** (baqi 6 pages
  jaise). Safe kyunke active-state JS `[data-nav]`/`data-active` par chalta hai, class par nahi.

**QADAM 2 — Fonts local (offline):**
- 9 woff2 `static/fonts/` mein: **IBM Plex Sans** 400/500/600/700, **Noto Nastaliq Urdu**
  400/600, **Source Serif 4** 400/600/700 (fontsource CDN = official fonts, per-weight).
- `static/app.css` `@font-face` (sab `font-display: swap`).
- Sab pages se Google Fonts ke **3 links** (2 preconnect + css) hataye → `<link rel="stylesheet"
  href="/static/app.css">`.
- Cache middleware: `/static/fonts/*.woff2` par **1-saal immutable**; `app.css`/`icons.svg`
  par jaan-boojh kar **koi long cache nahi** (StaticFiles ka default ETag/304).
- `.urdu/.ur` stack (sirf index mein defined) pehle se **Jameel-first** — koi tabdeeli nahi.

**QADAM 3 — Icon sprite:**
- `static/icons.svg` — **10 unique `<symbol>`** (i-generator/library/bank/blueprint/outcomes/
  slo-health/adaptive/analytics/mypapers/settings), sab `viewBox 0 0 24 24`, stroke 1.8, round.
- `.icon { 17px }` app.css mein; **index apne `.app-nav a svg` se 19px** rakhta hai (index ke
  icons pehle 19px the — chhote na hon, no-visual-change).
- 6 sidebar pages ke inline nav SVG → `<svg class="icon"><use href="/static/icons.svg#i-..."></use></svg>`.
- `static/brand/logo.svg` (mojooda navy+blue document mark, standalone — abhi koi consumer nahi).
- `print.html` **chhua nahi** (text-only nav, koi icon nahi — scope ke mutabiq).

**FAISLE / spec se hatt kar (jaan-boojh kar):**
- **Source Serif 4 bundle kiya** — font-list mein nahi tha, magar index ke paper-preview mein
  use hota hai (`Georgia` fallback). No-visual-change + offline honor karne ke liye zaroori,
  warna offline preview Georgia par gir jata.
- **`/static` mount naya add** kiya (`app/main.py`) — spec ke saare asset paths `/static/...`
  maangte the, app pehle sirf `/` par mount tha. Legacy `/apiClient.js` waise hi chalta hai.
- Fontsource ka **"latin" subset** — extended-Latin/doosre scripts system font par fall back
  (UI text ke liye kaafi).
- **`/api/brand` public** rakha (upar wajah).

**BAQI (follow-up, is scope se bahar):** `index.html` ke tip-text mein 3 jagah **"AII"** copy
bacha hai ("AII suggests", "AII PDF/images parse karke…") — sidebar brand naam nahi, body copy
hai; 1d ne sirf "AII Smart/… Paper Maker" naam kaha tha.

**Files:** naye — `config/brand.json`, `app/api/brand.py`, `app/services/brand_service.py`,
`static/js/brand.js`, `static/app.css`, `static/icons.svg`, `static/brand/logo.svg`,
`static/fonts/*.woff2` (9). Chhue — `app/main.py`, `app/schemas/responses.py`, sab 7 static HTML.

**Verify:** **772 tests pass, ruff clean.** Server smoke (curl): saare 7 pages + app.css +
icons.svg + logo.svg + brand.js + `/api/brand` + 9 fonts → **200**; fonts par 1yr immutable,
css/svg par sirf ETag. **Browser render (icons `<use>`, font visual, Urdu RTL, print preview,
OFFLINE) baqi — Irfan ka incognito test** (Claude-in-Chrome extension is env mein connect nahi tha).

## 2026-07-19 — feat/slo-health (SLO Health page — Marhala 2 Hissa C)

Ek page jo DONO taraf ka gap dikhata hai: (a) SLO jinke paas koi (published) question
nahi, (b) (published) questions jinke paas koi SLO tag nahi. Plus per class/subject
health line aur "SLO import baqi". `GET /api/slo-health` (coverage/shortfall ke parallel,
magar paper-scoped nahi — poore data par). Live compute (JOIN), snapshot NAHI.

**Sab se ahem:** page GENERAL hai — SAARI classes/subjects/strands ke liye. Koi class/
subject/strand HARDCODE nahi (abhi sirf Pre Year 1 Math ka SLO data hai, magar Grade
4/5/6 Math, Grade 7 Science, Grade 8 Geography syllabus mein maujood — aate hi khud aayenge).

**Faisle amal mein:**
- **Covered = SLO ke paas >=1 linked PUBLISHED question.** draft/archived shumar NAHI —
  page par saaf note (`draft_note`).
- **Questions par class column NAHI** (koi migration nahi kiya). grade `syllabus_topic`
  se LEFT JOIN; jis question ka topic-link nahi uska grade na-maloom -> **"(class na-maloom)"**
  bucket (Part 3 aur health line mein).
- **`normalize_class`** naya (`app/core/text_norm.py`) — `normalize_subject` jaisa alias-dict
  (abhi khali, structure mojood). Case/alias normalize har jagah: class, subject, bloom.
- **Bloom NULL SLO -> "(bloom na-maloom)"** bucket (silently REMEMBER nahi maante).
- **import_pending** = `syllabus_repository.list_distinct_subject_grade()` ke woh combos
  jinka SLO group nahi.
- **Filter** (class+subject) DB se distinct — dropdown response ke `classes`/`subjects`
  se populate (hardcode nahi); filter server-side, magar dropdown lists hamesha POORE.

**Naye REPO functions (coverage/shortfall ke shared functions NAHI chhede):**
- `slo_repository.list_all()`
- `question_slo_repository.slo_ids_with_published_questions()` (JOIN questions status='published')
- `questions_repository.list_published_with_grade_and_tag()` (LEFT JOIN syllabus_topics for grade,
  EXISTS+JOIN slo for is_tagged — orphan link ko tagged nahi ginta, covered jaisa).

**MULTI-TENANT (abhi implement NAHI — sirf jagah):** teeno naye repo functions mein optional
`school_id` param add kiya jo abhi use nahi hota — aage 100+ schools par `WHERE school_id = ?`
yahin lagega bina signature tode. Service/route abhi ise pass nahi karte.

**Files:** `app/services/slo_health_service.py` (naya) · `app/api/slo.py` (route) ·
`static/slo-health.html` (naya page) · nav link **6 pages** (index, slo, bank, blueprint,
library, print — user ne "5" kaha tha; print.html ka nav bhi maujood tha to consistency ke
liye woh bhi). NOTE: bank/blueprint/library/print ke nav mein "Learning Outcomes" (slo.html)
link pehle se nahi tha — sirf SLO Health add kiya (scope).

**Tests:** `test_slo_health_service.py` (11) + `test_slo_health_api.py` (2) = 13 naye —
seed-based, koi hardcoded DB count nahi (apne seeded id/norm-keys par assert). draft-covered,
class-na-maloom, bloom-null, import-pending, filter, multi-class general — sab covered.

**Baqi:** browser test + merge teacher karega. Pre-generate/blueprint integration alag scope.

**FUTURE (idea — implement nahi):** Blueprint shortfall warning behtar karna. Abhi sirf
"Section A: 20 maange, 8 mile" dikhata hai. Behtar yeh ho ke **wajah** bhi bataye (kaunsi
shart tang hai) aur **teen option** de — bilkul Hissa B ke Bloom shortfall ki tarah:
(a) jo mil raha usi se banao, (b) filan shart hata do -> itne milenge, (c) naye questions
likho. App khud chup-chaap adjust NA kare.

---

## 2026-07-19 — feature/slo-phase-2b-shortfall (Bloom shortfall — Marhala 2 Hissa B)

Paper ka asal Bloom distribution vs class standard (Pre-Primary 70/30) — per-Bloom
**kami (shortfall)**. `GET /api/paper/{id}/bloom-shortfall` (coverage endpoint ke parallel).
**App khud kuch adjust NAHI karta** — sirf report; teacher UI par 3 option chunta hai.

**Faisla (darj):** Bloom source = **SLO ka `bloom_level`**, question ka nahi. Wajah: SLO book
se soch kar bana (PY1 Math 31 remember/19 understand = 70/30 fit); question ka bloom auto-derive
+ mashkook ("Trace the number 3" par APPLY; 197 mein 80 APPLY = 41%, standard se door).

- **`slo_shortfall_service.py`** (naya): SLO bloom se actual, `bloom_standards.get_bloom_suggestion`
  se target %, **largest-remainder (Hamilton)** se target counts (sum = N). Per-Bloom
  `{needed, actual, short}` + total_short. Live compute (JOIN), snapshot nahi.
- **`question_slo_repository.list_slo_blooms_for_questions`** (naya) — question→SLO.bloom rows.
  Coverage ka shared `list_links_for_questions` **NAHI chheda** (uski query na toote).
- **`app/api/papers.py`** — naya route; **`static/index.html`** — Bloom Shortfall panel (SLO Coverage
  ke neeche): per-Bloom bar + kami + **3 option** (jo mil raha usi se / doosre Bloom se / naye sawal).

**Ahem faisle amal mein:**
- **Multi-SLO** question → uske SLOs mein sabse **UNCHA (highest)** Bloom; UI par `ℹ️ N multi-SLO` nishaan.
- **Denominator N** = classifiable questions (SLO-tagged AND bloom maloom).
- **CASE-normalize** (`_norm` = LOWER+TRIM) har bloom par — `REMEMBER`(q) / `remember`(slo) /
  `remember`(standard) sab ek jagah; warna ginti zero. (Source SLO hai, magar defensive.)
- **untagged** (koi SLO link nahi) aur **bloom-unknown** (SLO tagged par bloom NULL) — **DO alag ginti**,
  distribution se bahar (subject badalne par masla tagging ka hai ya SLO-data ka — farq zaroori).
- Koi classifiable question na ho → panel ZERO nahi, **graceful message** (coverage `_no_universe` jaisa).

**Tests:** `test_slo_shortfall_service.py` (11) + `test_slo_shortfall_api.py` (2) = 13 naye —
seed-based, koi hardcoded bank-count nahi. ruff clean; full suite **759 pass** (746 → 759).
Browser test + merge teacher karega.

**Baqi:** Hissa C (SLO Health page) pending. Pre-generate shortfall (bank-availability) alag scope —
abhi nahi (post-hoc pehle). Data gaps qaim: Pre-writing/C-05/C-06/Colour-Circle-11-24 (pichhli entry dekho).

---

## 2026-07-19 — Pre Year 1 Math SLO tagging (DATA kaam, app code nahi)

197 Pre Year 1 Mathematics questions ko SLO se tag kiya — coverage report ko zinda
karne ke liye (pehle sirf 8 tagged the). Yeh mostly DATA kaam hai; app code touch
nahi hua, do standalone one-shot scripts `scripts/` mein (branch `chore/slo-prefill-script`).

**1. `scripts/prefill_slo_pre_year1_math.py`** (one-shot, read-only — DB mein kuch NAHI likhta):
Question text ke template se slo_code khud derive karta hai (manual picker nahi):
- Number: `Trace the number N` → N-03/N-11/N-16 · `Count..write`/`How many`/`There are`/Urdu
  count+write → N-04/N-12/N-17 · `Colour` → N-06 · `Circle all` → N-07 — **range** 1-10/11-20/21-24
  se sahi code. Colour/Circle sirf 1-10 (11-24 ka SLO nahi → khali).
- Shape: `Trace the <shape>` text se · `Name this shape` MCQ ka **correct_answer_en** (answer-key)
  se — S-01..S-04 (flat) / D-01..D-06 (solid).
- Comparison: topic `Concept of "a" and "b"` se C-01..C-04.
- Koi rule match na ho → khali (andaaza nahi).
Output DO sheets ek Excel mein: **UPLOAD 161** (auto-filled) · **MANUAL 36** (28 khali +
8 review). import `pd.read_excel(sheet_name=0)` = pehli sheet (UPLOAD) parhta hai (script verify karta).
`.xlsx` gitignored (`scripts/*.xlsx`).

**2. Teacher ne UPLOAD sheet import ki** (`/api/slo/assign-import`): **Updated 161, Errors 0**.
Tagging 8 → **169 questions**.

**3. 8 stray test-tags theek kiye** (bina delete ke): 8 `How many..are there?` MCQ par pichhle
browser-test ka kachra tha (number question par D-01/C-01/S-01/W-01/N-01). Kyunki assign-import
**replace-set** hai, `fix_8_stray_tags.xlsx` (8 rows, sab sahi **N-04**, range 1-10) upload se
purana ghalat link khud replace ho gaya — alag delete ki zaroorat nahi. **Updated 8**.

**4. `scripts/clean_stray_slo_links.py`** — dry-run cleanup helper (default sirf dikhata, delete
`--delete` par). Is dafa **istemal NAHI hua** (replace-set behtar tha), aainda ke liye rakha.
Iske dry-run ne ek bara khatra pakRa: table 8 nahi 169 links par tha (teacher upload ho chuki thi),
to "saare PY1 links" wala pehla broad target 161 sahi tags mita deta — target ko precise
(`How many` + non-count code) kiya, tab 8 dikhe.

**TASDEEQ:** coverage report ab **zinda** — bare paper par **13/50 (26%)**, aur **Pre-writing 0/3**
(pehle jhoota `1/3` dikh raha tha, kyunki number-8 question par ghalti se W-01 laga tha).

**DATA GAP (report ne khud pakRa — aainda tagging/question-banane ke liye darj):**
- **Pre-writing** ke teeno SLO (W-01/02/03) — bank mein ek bhi question nahi.
- **Comparison C-05** (which has more/less) aur **C-06** (equal groups) — koi question nahi.
- **Colour/Circle numbers 11-24** — in skills ka koi SLO define nahi (28 questions MANUAL sheet
  mein khali chhoRe — inhe kabhi tag nahi kar sakte jab tak SLO na banein ya questions na haten).

**Baqi:** Hissa B (shortfall 70/30) + Hissa C (SLO Health page) abhi bhi pending. `feature/slo-export-class-filter`
(export grade/subject filter, 746 tests) bhi merge ke intezaar mein — alag branch.

---

## 2026-07-19 — feature/slo-export-class-filter (SLO export grade/subject filter)

SLO bulk-assign export (`GET /api/questions/slo-export`) ab optional `?grade=&subject=`
leta hai — kyunki export saare 317 Mathematics questions deta tha (Pre Year 1 ke ~197
nahi), teacher ko tagging ke liye chhaant-na parta. **Backward compatible:** koi param na
ho to purana sab-questions behaviour + `slo_assign_export.xlsx`.

- **Naya `app/core/text_norm.py`** — `normalize_subject()`: alias **dict** (`math/maths →
  mathematics`), hardcoded if-else NAHI (nayi alias add karna aasaan). Compare-time only, data untouched.
- **`questions_repository.list_for_slo_export(grade, subject)`** (naya) — grade par
  `syllabus_topics` JOIN (case/whitespace-insensitive); **`syllabus_topic_id` NULL wale grade
  filter par khud EXCLUDE** (expected, INNER JOIN). subject dono-taraf `normalize_subject` se
  Python-side filter — DB mein `Math`/`Mathematics` dono ho to bhi sahi.
- **`question_slo_import_service`** — `build_export_xlsx(grade, subject)` (return **bytes hi**,
  purane 2 export tests untouched) + naya `export_filename()` → dynamic naam
  `slo_assign_export_Pre_Year_1_Mathematics.xlsx`. Columns waise hi 5 — koi naya nahi.
- **`app/api/slo.py`** — route par optional query params + dynamic `Content-Disposition`.
- **`static/slo.html`** — export par grade **`<select>`** (`/api/syllabus-grades` distinct se
  populate — **hardcode NAHI**, nayi class add hote hi aa jaye) + subject input + button URL builder.

**NOTE (code change NAHI kiya, sirf darj):** coverage universe (`slo_coverage_service`) abhi
`normalize_subject` use nahi karta — `papers.subject` vs `slo.subject` par `LOWER(TRIM)` (alias
nahi). Aaj teeno 'Mathematics' hain to theek; Math/Mathematics mismatch aaya to universe khali
(covered SLO phir bhi dikhte, remaining/% None — crash nahi). [[project-papermaker-roadmap]] Hissa B se pehle chhota fit ho sakta.

**Tests:** `tests/test_slo_export_filter.py` (8) — **seed-based, koi hardcoded 317/197 nahi**
(apne `q1..q5`/`t_py1,t_py2` ke id-sets se assert). ruff clean; full suite **746 pass** (738 → 746).
Browser test + merge/push teacher karega (GitHub Desktop).

---

## 2026-07-18 — fix/paper-class-and-delete-warning (2 zinda bugs)

SLO Marhala 2 Hissa A ke dauran nikle do data-masle ki tashkhees se: `class_name`
None (47/63 papers) aur orphaned papers (40/63). Do fixes (merge `4fb1409`):

**Fix 1 — Generator class_name capture** (`static/index.html buildPaper`): ab
`class_name: val('gradeSelect') || null` body mein jaata hai. Backend
(`GeneratePaperRequest.class_name` + `_persist_paper`) pehle se ready tha — masla
sirf frontend line ka tha (isi liye har Generator paper class None banta,
coverage universe kabhi nahi banta). Zero backend change. **Regression-guard**:
`test_generator_class_name.py` `index.html` ke buildPaper mein `class_name`+`gradeSelect`
ki maujoodgi check karta — line dobara gayab hui to test fail.
(Blueprint/bank-paper pehle se class bhejte the — free-text `bpClassName`/`bpClass`.)

**Fix 2 — question delete se pehle paper warning**: `papers.question_ids` JSON blob
hai (koi FK/cascade nahi), is liye sawal delete karna papers ko chup-chaap orphan
kar deta tha. Ab delete se pehle warning kaun se papers tootenge:
`papers_repository.find_papers_containing` (quoted-id `LIKE '%"uuid"%'`, substring-safe),
`paper_service.papers_using_question` (count+titles, untitled→'(Untitled)'),
`GET /api/bank/questions/{id}/paper-usage`, `bank.html deleteQuestion` (3-4 naam +
"aur N mazeed"). **Sirf warning** — koi block/cascade/snapshot nahi (jaan-boojh kar simple).

**Haath NAHI lagaya (data, code nahi):** 40 orphaned papers (deleted sawal wapas nahi
aate — murda), 47 None-class papers (coverage graceful handle karta, andaaze se backfill
galat hota). **Deferred tajweez:** Blueprint/bank-paper ka free-text class box →
dropdown+custom fallback (isi se Jasmine/NUrsery/play aaye) — alag chhota kaam, baad me.

**Tests:** `test_generator_class_name.py` (2) + `test_paper_delete_warning.py` (6) =
8 naye. ruff clean; full suite **738 pass** (730 → 738). Browser test (teacher) green:
Generator par Pre Year 1 chuna → paper class set + poora coverage; delete par paper-naam warning.

---

## 2026-07-18 — SLO Marhala 2 Hissa A (paper coverage + Excel tagging)

Do stacked branches, tarteeb se master mein merge (`--no-ff`):
`feature/slo-phase-2a-coverage` (9d8a9d1) → `feature/slo-phase-2a-excel-tagging` (f7876c3).

**Coverage** (`slo_coverage_service.py`, `GET /api/paper/{id}/slo-coverage`):
Paper ke sawalon se covered vs class/subject ke reh gaye SLO + strand breakdown +
untagged-question ginti. **Live compute (JOIN), stored snapshot NAHI** — link/SLO
baad me badle to report khud sahi rahe. class match **normalized** (`LOWER(TRIM)`)
kyunki `papers.class_name` free-text/gandi hai; universe na mile (class None ya us
class/subject ki koi SLO nahi) to **graceful covered-only + saaf message**, koi crash nahi.
`coverage_percent` = covered∩universe / total. Repo: `list_links_for_questions` (batch
JOIN), `list_by_class_subject_normalized`. UI: `index.html` paper preview ke neeche
SLO Coverage section (progress bar + strand table + reh-gaye list + untagged note).

**Excel tagging** (KAAM A — user manual picker use nahi karta, sab Excel/Blueprint se):
- **Naye questions**: bulk upload Excel mein optional `slo_code` column (comma-separated
  = kai SLO). Ghalat code → skip + warning, question phir bhi import (topic-behavior jaisa).
  Insert ke baad link (image-attach pattern par). `bulk_upload_template.xlsx` + bank.html hint update.
- **Purane 200+ questions**: `GET /api/questions/slo-export` (Excel: `question_id` +
  current `slo_code`) → teacher `slo_code` bhare/edit kare → `POST /api/slo/assign-import`.
  **question_id se match** (text se nahi), **replace-set** (idempotent, khali=clear).
  `question_id` protection: import par saaf error (khali/unknown id) + Excel cell-comment
  warning — real sheet-lock NAHI (over-engineer). Shared `resolve_slo_codes` (case/space-insensitive).
  `question_slo_import_service.py` naya; `slo.html` par bulk-assign card.

**Duplicate trap (confirmed + tested):** bulk question import upsert NAHI karta — har row
naya uuid. Same sheet dobara upload = QUESTION duplicate. Isi liye purane questions ke liye
slo-export/assign-import (id se) — question sheet re-upload NAHI. SLO links khud replace-set
(multiply nahi hote). `test_bulk_import_slo.py::test_reupload_duplicates_the_question` documents.

**Data findings (live test):** saare Pre Year 1 Math papers ORPHANED (question_ids ab
questions table me nahi — sawal delete ho chuke, coverage 0 dikhega); real-question papers ka
`class_name = None` (poora universe view sirf class-set paper par). Ye data-hygiene, code bug nahi.

**Tests:** `test_slo_coverage_{service,api}.py` (13) + `test_bulk_import_slo.py` (6) +
`test_question_slo_import.py` (11) = 30 naye. ruff clean; full suite **730 pass** (700 → 730).
Browser test (teacher) green: bulk-assign 8 tags, purana paper covered-only + graceful,
naya Pre Year 1 paper POORA view (0/50, 5 strands sahi, reh-gaye 50), 'play' class graceful.
`sample_slo_assign.xlsx` (gitignored) test ke liye.

**Baqi:** Hissa B (shortfall) + Hissa C (SLO Health page) abhi NAHI. Aur [[project-papermaker-kaam-b-collapse-manual-add]] (bank.html manual form collapse) pending.

---

## 2026-07-18 — feature/slo-phase-1 (SLO Marhala 1 — question↔SLO link)

**Scope:** Har question ko ek ya kai SLO se jorna (Marhala 2 paper-coverage report ki buniyaad).
Bulk-assign Excel is marhale me NAHI (pehle manual UI se validate) — baad me
`question_slo_import_service` + `POST /api/slo/bulk-assign` me fit hoga.

**DB** (`app/core/database.py`): naya **`question_slo` link table** (column NAHI) —
`question_id`, `slo_id`, `created_at`, composite PK `(question_id, slo_id)`. Wajah: (1) ek sawal =
kai SLO, (2) `questions` table bilkul untouched → 200+ purane questions bina migration ke chalte
rahein, (3) gemini (protected) question bhi tag ho bina uske row ko chhue. `slo_id` (PK) se link
(slo_code se nahi) — re-import par id stable; report ke liye slo_code/slo_text JOIN se. FK enforce
nahi (baaqi schema jaisa) — coverage report defensive INNER JOIN. Index: `idx_question_slo_slo`
(reverse lookup "is SLO ke saare questions" — Marhala 2). Migration = sirf CREATE TABLE/INDEX
(idempotent, server restart chahiye).

**Repo** (`app/repositories/question_slo_repository.py`, naya): `replace_for_question` (replace-set,
duplicate INSERT OR IGNORE), `list_slo_ids_for_question`, `list_slos_for_question` (JOIN, orphan
link INNER JOIN se khud drop), `list_question_ids_for_slo` (reverse), `existing_slo_ids` (link se
pehle validate — orphan se bachao).

**Service** (`app/services/question_service.py`): `set_slos_for_question` (sirf maujood slo_ids
likhta — orphan filter), `get_slos_for_question`; manual create/update me `slo_ids` diya ho to link
write (replace-set).

**API** (`app/api/questions.py`): `GET /api/questions/{id}/slo` + `PUT .../slo` (replace-set, khali
list = clear; **har source** par — link table protected row ko nahi chhoota); `slo_ids` optional on
manual create (`POST /api/bank/questions`) + update (`PATCH /api/bank/questions/{id}`).
Schemas: `ManualQuestionRequest`/`Update` me `slo_ids`, naya `SetQuestionSloRequest`; update ke
"kam az kam ek field" validator me `slo_ids` shaamil.

**UI** (`static/bank.html`): Add + Edit modal me **SLO picker** (checkbox list + search).
Filter subject+class par — **gate:** subject/class/topic teeno maloom hon tabhi bharta, warna
"pehle topic chuno" hint (teacher ko 50 SLO me se dhoondna na pare). Add: subject/grade/topic
badalne par reset. Edit: subject se filter, linked SLO pre-checked, un-check kar ke clear.
(Edit modal sirf manual questions ke liye khulta; gemini tagging PUT endpoint se — UI me abhi surface nahi.)

**Tests:** `tests/test_question_slo_repository.py` (7) + `tests/test_question_slo_api.py` (11) =
18 naye. ruff clean; full suite **700 pass** (682 → 700). Live server smoke: PUT link → GET →
empty-PUT clear sab OK (dev DB cleanup). Browser test (teacher): gate/add/edit/clear/purane-questions —
sab green, tabhi merge (`--no-ff`, commit `26fb90c` → merge `fca1fbf`).

---

## 2026-07-18 — feature/slo-phase-0 (SLO Marhala 0 — table + Excel import)

**Scope:** SIRF `slo` table + Excel bulk import. Question↔SLO link (Marhala 1) aur
paper coverage (Marhala 2) is marhale me NAHI. Data target: Pre Year 1 Math (~50 SLO).

**DB** (`app/core/database.py`): `init_db()` me naya `slo` table (CREATE TABLE IF NOT EXISTS,
existing data safe) — `id` TEXT uuid PK, `class`, `subject`, `slo_code` (UNIQUE), `slo_text`,
`bloom_level` (nullable), `strand`, `created_at`. `strand` ALAG column (slo_code parse nahi karte —
Marhala 2 strand-wise coverage seedha column par bane). Index: `idx_slo_class_subject`.

**Bloom auto-suggest** (`app/core/bloom_standards.py`): naya `suggest_bloom_from_text()` —
slo_text ke pehle content-verb se level (`_VERB_BLOOM` map: count/identify/recognize→remember,
describe→understand, solve→apply, compare→analyze...). Fillers (students/will/be/able/to) skip.
Verb match na ho → **None** (default "remember" NAHI, taake galat label na lage). Sirf tajweez —
import me teacher ki di hui value overwrite nahi hoti; khali ho tabhi auto-fill.

**Import service** (`app/services/slo_import_service.py`, `library_meta_import_service` pattern par):
pandas `read_excel(dtype=str)`, columns lowercase-normalize. Required: class/subject/slo_code/slo_text;
optional: bloom_level/strand; `book_pages` + koi bhi extra column IGNORE (error nahi).
Duplicate `slo_code` par **UPDATE** (draft dobara import: slo_text/bloom_level/strand refresh,
`created_at` untouched), naya par ADD. Ek row fail se baaki nahi rukti. Summary:
`{added, updated, errors, results:[{row, slo_code, status, reason?}]}`.

**Repo/API/UI:** `app/repositories/slo_repository.py` (insert/find_by_code/update_by_code/list_by_filters);
`app/api/slo.py` — `GET /api/slo` (class/subject/strand filter), `GET /api/slo/template`,
`POST /api/slo/import`; `app/main.py` me router register (auth ke peeche). `static/slo.html` (import +
summary + filterable list), `static/slo_import_template.xlsx` (header + 4 sample rows), index.html nav link.

**Strand codes (is book se, 50 SLO):** W=Pre-writing(3), N=Number(25), C=Comparison(6),
D=Solid Shape(8), S=Flat Shape(8). Pattern/Measurement/Data is book me NAHI.

**Tests:** `tests/test_slo_import.py` (10) + `tests/test_slo_api.py` (6) = 16 naye. ruff clean;
full suite **682 pass** (666 → 682). Smoke test (real boot): template/import/re-import/list/slo.html
sab OK; bloom verify (compare→analyze, count/recognize→remember, trace→None); demo rows real DB se saaf.

---

## 2026-07-18 — feature/db-index-caching (HISSA 4 DB index + HISSA 5 caching)

**HISSA 4 — image_library filter indexes** (`app/core/database.py`, commit `59517e0`):
- `init_db()` me 3 `CREATE INDEX IF NOT EXISTS`: `syllabus_topic_id` (list filter +
  topic_ids_with_images/topic_image_counts + find_by_name_and_topic — 4 code paths), `subject`, `grade`.
- Migration = sirf CREATE INDEX (existing data safe, idempotent, sirf server restart chahiye — koi schema change nahi).
- Query plan pehle `SCAN image_library` → ab `SEARCH ... USING INDEX`. init_db 2x chala, error nahi.
- **Scope se bahar (index nahi lagta):** search `q` (`name/keywords LIKE '%..%'` leading wildcard) aur
  `category` (`LOWER(category)=?`) — FTS/expression index chahiye, HISSA me nahi.
- **Reality:** abhi sirf 106 rows — koi query slow nahi thi; ye future-proofing hai (library barhne par).

**HISSA 5 — caching headers** (`app/main.py`):
- Nayi `@app.middleware("http")` — sirf `/library/*.webp` (full + thumbs) par
  `Cache-Control: public, max-age=31536000, immutable` (1 saal). HTML/JS ko haath nahi (StaticFiles default ETag/304).
- **Cache-busting zaroorat NAHI** — code-verified: `image_id=uuid.uuid4()` har upload, koi route
  existing `{uuid}.webp` overwrite nahi karta (replace = delete + naya upload = naya UUID = nayi URL).
  Filename hi content-address hai. Future guardrail: agar kabhi in-place replace feature bane to
  naya UUID/`?v=` rakhna warna immutable stale dega.
- Verified (TestClient): webp → immutable header; library.html/index.html → koi long-cache nahi.

**Tests:** ruff clean; full suite **666 pass**. Do alag commits (H4 db, H5 main).

---

## 2026-07-18 — feature/bulk-convert (HISSA 3 — 99 purani PNG → smart WebP)

**Kya kiya:** `image_library` ki 99 purani rows (`file_path .png`, `compression=None`, static/library/)
ko smart WebP me convert kiya — `process_and_save()` (same uuid) se full webp + 300px thumb, phir DB update.
Data migration hai (koi naya code nahi; detection HISSA-2/saturation-gate wahi).

**Irreversible-safety (convert se PEHLE):**
- DB backup: `paper_maker_backup_bulkconvert_20260718_*.db`
- 99 original PNG backup: `backups/library_png_20260718/` (static ke bahar) — `.gitignore` me `backups/` add
- Convert ke baad browser me crisp confirm (horse_bw, candy_bw, trace, sharpener_bw, walnut_bw lossless;
  basket_c colour saaf) — TAB original .png delete.

**Per row:** `file_path` → `library/{uuid}.webp`, `thumb_path` → `library/thumbs/{uuid}.webp`,
`compression` → lossless/lossy. Per-row try/except + commit (resumable; ek run timeout hua, doosre ne baaki 21 pura kiya).

**Natija:** 99/99 convert, 0 fail. **lossless 76, lossy 23** (saare lossy = `_c` colour photos).
Size: PNG 52.93 MB → WebP full **21.05 MB (−60.2%)** (+thumbs 25.97 MB, −50.9%).
Lossy 23: 25.19→2.19 MB (−91.3%); lossless 76: 27.74→18.86 MB (−32%, phir bhi crisp).
Integrity: 99 webp + 99 thumb + DB sab OK.

**Note:** images aur `paper_maker.db` gitignored hain (version control me nahi) — commit sirf PROGRESS + .gitignore.
Backups (DB + 99 PNG folder) local safe rakhe. Cloud deploy-remote par push NAHI (sirf backup remote).

---

## 2026-07-18 — smart-compression: unit tests + backup push

**Unit tests — `tests/test_smart_compression.py` (16 naye, pure functions, koi DB/client nahi):**
numpy se controlled images bana kar exact boundaries test kiye —
- `_buckets_to_cover`: 1 flat colour → 1 bucket; 60/40 → 2; photo-noise → >40;
  **boundary 47 colours → 40 buckets** (lossless side) vs **48 → 41** (lossy side); khaali → 1.
- `_is_low_saturation`: pure grayscale → True; saturated red → False;
  **boundary 13% sat (<0.14) → True** vs **15% (>0.14) → False**; khaali → True.
- `_choose_compression` **3-stage order**: force_lossless jeetta hai; high-detail B/W
  (64 near-gray, buckets 55>40 par low-sat) → saturation gate lossless deta hai (bucket rule se pehle);
  saturated colour noise → lossy; flat colour graphic (chand buckets) → lossless.

**Run:** ruff clean (import-order auto-fix); **poora suite 666 pass** (pehle 650 → +16).

**Git:** commits `bef8ead` (feat: buckets + saturation gate) → merge `6e39909` → `1483f37` (tests).
**Push:** `backup` remote (paper-maker-backup.git) par push kiya — yeh **backup repo hai, deploy-remote NAHI**
(Railway/Northflank yahan configured hi nahi). Isliye "master push se deploy todta hai" wala rule nahi toota.
`master -> master` synced (ahead 0).

---

## 2026-07-18 — feature/smart-lossy-webp: saturation gate (detailed B/W line-art false-lossy fix)

**Asli _bw test se pakda:** library me 65 named images hain (`_bw` = line-art, `_c` = colour) —
UUID naam se store, DB `image_library.name` → `file_path` mapping se mile (original `.png`, compression=None).
Naye buckets-metric par 40 me se 38 `_bw` lossless, par **2 false-lossy**: `sharpener_bw` (51 buckets,
21 shaded sharpeners) aur `walnut_bw` (55 buckets, dense stippling) — ground truth Read se dekha, dono
sach me B/W line-art hain jo lossy me smear ho jate.

**Root cause:** detailed B/W line-art (grey shading/stippling) bucket-count me simple colour photos se
**OVERLAP** karta hai (sharpener 51, walnut 55 vs cat_c 56, banana_c 46, panda_c 41). Buckets *akele*
in dono ko alag nahi kar sakte — koi N kaam nahi karega (wahi 8/16 wali limitation, dusre end par).

**Discriminator = saturation.** B/W drawing chahe kitni detailed ho, saturation ~0; colour photo ki high.
Real library par mapa: `_bw` sat-frac (S>40 wale pixels ka hissa) ≤0.122, `_c` ≥0.104.

**Fix — `app/services/image_processing_service.py`, `_choose_compression` me saturation gate:**
1. `force_lossless` (mode 1/P/transparency) → lossless  [waise hi]
2. **NAYA** `_is_low_saturation()` — sat-frac < `_SAT_LOSSLESS_MAX=0.14` → lossless (har B/W drawing, detailed bhi)
3. warna colour: `_buckets_to_cover <= _MAX_BUCKETS_LOSSLESS(40)` → lossless, warna → lossy
- Constants: `_SAT_PIXEL_MIN=40` (HSV S se upar = meaningful rang), `_SAT_LOSSLESS_MAX=0.14`.

**Validated (real library, ground truth):** 40/40 `_bw` → lossless ✓; 22/24 `_c` → lossy ✓;
sirf `cat_c`+`football_c` (muted colour) over-lossless — storage cost only, quality nahi (safety bias).
ruff clean; 85 library/image tests pass. Merged to master (LOCAL only, cloud push NAHI).

---

## 2026-07-18 — feature/smart-lossy-webp: detection metric fix (top-8 coverage → buckets-to-85)

**Masla (code review se):** purana `_is_line_art` **fixed top-8 buckets ka coverage ≥0.85** dekhta tha.
Ye multi-colour flat art par galat tha — 10-15 flat rang wali (bacchon wali crisp) illustration ka
top-8 coverage <0.85 aa jaata → galti se **lossy** (quality loss us cheez par jise crisp chahiye).
`_TOP_BUCKETS` ko 8→16 karna wahi bug ka bada version tha (16-colour art phir lossy). Magic number kaam nahi karta.

**Naya metric — "85% coverage tak kitne buckets chahiye?"** (`_buckets_to_cover`):
- Buckets ghatte order me jodo jab tak cumulative coverage ≥0.85 na ho; kitne lage = signal.
- Flat art (chand flat rang) → **kam buckets**; photo (gradients phaile) → **bohot buckets**.
- `_is_line_art = _buckets_to_cover(img) <= _MAX_BUCKETS_LOSSLESS (40)`.
- `_QUANT_SHIFT=3`, `_COVERAGE_TARGET=0.85` waise hi. `force_lossless`/`_choose_compression` unchanged.

**N=40 kaise choose kiya — real uploads par mapa (synthetic NAHI):**
- `static/uploads/` ke 1206 asli teacher images ka sample: do alag populations —
  line-art/flat **≤29 buckets** par rukta, photo **≥41** se shuru; **30–40 bilkul khaali (gap)**.
- 6 library photos ka floor bhi 46 tha — match. N=40 valley me baitha, isliye magic number nahi (±5 safe).
- Ground truth khud dekha (Read se): `099cdf59`(1b, safed worksheet+trace+text) → lossless ✓;
  `1b2feffd`(41b, 6 shaded tables+bold "SIX") → lossy ✓ (bold text q85 me bachta, tables photographic);
  `861d9631`(379b, 23 baskets photo) → lossy ✓. Delicate line-art hamesha safed pages par (kam buckets) → lossless.

**Verified:** updated service function real images par expected split; ruff clean; 85 library/image tests pass. Cloud push NAHI.

---

## 2026-07-17 — feature/smart-lossy-webp (Smart Lossy/Lossless WebP)

**Kya bana (sirf naye uploads):** har image ka type detect karke best compression —
line drawing/trace/outline → LOSSLESS (bacchon ke liye crisp), photo → LOSSY q85 (zyada saving).
Ambiguous → hamesha lossless (safety bias).

**Detection tareeqa — "dominant colour coverage" (raw unique-count se robust):**
- Raw unique-colour count ka masla: anti-aliasing se ek simple trace bhi hazaaron edge-shades de deta
  hai → galti se photo detect. Isliye coverage use kiya.
- `app/services/image_processing_service.py`:
  - `_is_line_art(full)`: RGB → numpy, colours quantize (`>>3` = 32 levels/channel, AA noise merge),
    `np.bincount` se top-8 buckets ka pixel coverage; **coverage ≥ 0.85 → lossless**, warna lossy.
  - `_has_graphic_signals(img)`: hard signals jo seedha lossless karte hain (coverage skip):
    mode "1" (bilevel), mode "P" (palette ≤256), ya real transparency. Grayscale "L" ko force NAHI
    (B/W photo ho sakta hai) — coverage decide karta hai. Signal P→RGBA convert se PEHLE capture.
  - `_choose_compression()` → `"lossless"`/`"lossy"`; full + thumb **dono same mode** use karte hain.
  - Tunables: `_LOSSY_QUALITY=85`, `_QUANT_SHIFT=3`, `_TOP_BUCKETS=8`, `_COVERAGE_LOSSLESS_THRESHOLD=0.85`.
  - Return dict mein ab `compression` bhi.
- `app/core/database.py` — `image_library.compression TEXT` (CREATE + safe ALTER; purani rows NULL)
- `app/schemas/responses.py` — `LibraryImage.compression`
- `app/repositories/library_repository.py` — `insert()` mein `compression` column
- `app/api/library.py` — single + bulk row mein `compression` add
- `requirements.txt` — `numpy` explicitly add (ab seedha import; pehle sirf pandas ke through transitive)

**Verified (manual smoke):**
- Line art (grid + circle) → `lossless`, full 6.7 KB (crisp) ✓
- Photo (random noise, worst-case) → `lossy`, full 467 KB ✓

**Baaki:** pytest + ruff (baad mein), naye detection tests likhna. Cloud push NAHI.

---

## 2026-07-17 — feature/webp-thumbnails (HISSA 2 — WebP + Thumbnails)

**Kya bana (sirf naye uploads — purani JPG/PNG untouched, woh HISSA 3 Bulk Convert mein):**
- `app/services/image_processing_service.py` (naya) — `process_and_save(contents, image_id)`:
  Pillow se open, EXIF orientation fix, palette→RGBA; **2 LOSSLESS WebP** banata hai —
  Full (max 1200px, upscale nahi) → `static/library/{uuid}.webp`,
  Thumb (max 300px) → `static/library/thumbs/{uuid}.webp` (dono `lossless=True, method=6` — trace/outline crisp)
  Corrupt/na-khulne wali image → `ValueError`
- `app/api/library.py` — single upload (`POST /api/library`) + bulk upload (`POST /api/library/bulk`)
  ab `dest.write_bytes()` ki jagah service call karte hain; row mein `thumb_path` add;
  process fail → single 400, bulk us file ko skip (baaki chalti rahein)
- `app/api/library.py` — DELETE route ab thumb file bhi hataata hai (orphan fix)
- `app/repositories/library_repository.py` — `insert()` mein `thumb_path` column
- `app/core/database.py` — `image_library.thumb_path TEXT` (CREATE TABLE + safe ALTER migration; purani rows NULL)
- `app/schemas/responses.py` — `LibraryImage.thumb_path: Optional[str] = None`
- `static/library.html` — grid `renderCard()` ab `thumb_path || file_path` (purani images full par fall back)

**Verified (server restart + manual smoke test):**
- 1600×1000 PNG → full 1200×750, thumb 300×188, dono `WEBP` ✓
- 500px image upscale nahi hui (500×500 raha) ✓
- delete → full + thumb dono disk se hatt gaye (koi orphan nahi) ✓
- DB migration clean, `thumb_path` column present, `thumbs/` dir auto-create ✓

**Test fixture fix (same branch):** upload route ab image ko genuinely decode karta hai (Pillow),
isliye purane test files ka minimal 1×1 PNG/JPG (jo truncated/broken tha — `load()` par "broken data stream")
fail karne laga. `test_library_api.py` mein `_img_bytes()` helper (Pillow se valid bytes) + baaki 5 library
test files mein PNG ki IDAT line valid bytes se replace. Upload tests ab `.webp` ext, `thumb_path`, aur
thumbnail file existence check karte hain; bulk test `*.webp` count karta hai; delete test thumb removal verify.
- Service refactor: `process_and_save(contents, id, library_dir)` — dir ab param hai (tests `_LIBRARY_DIR`
  monkeypatch karte hain, isliye service ko route se dir milna chahiye, apna hardcoded nahi).

**Tests:** 650 pass, ruff clean. Cloud push NAHI.

**Fix (same branch) — upload size limit 2 MB → 10 MB + pixel guard:**
- **Masla:** 2 MB byte-check upload ke baad par conversion se PEHLE tha. WebP+1200px cap se stored
  size waise hi chhoti hoti hai, lekin bade high-res PNG (4–8 MB) convert hone se pehle hi reject ho jaate the.
- **Faisla (Option A):** 2 MB ko *storage guard* ki jagah *input/decode guard* maana. `_MAX_BYTES` 2 → 10 MB
  (single + bulk dono routes), byte-check ab bhi conversion se pehle (sasta rejection).
- `app/api/library.py` — `_MAX_BYTES = 10 MB`; error messages ("2 MB" → "10 MB") single + bulk.
- `app/services/image_processing_service.py` — **pixel guard** `_MAX_PIXELS = 50 MP`: chhoti file bade
  dimensions (decompression bomb) ko bhaari decode se PEHLE (header ki `img.size` se) reject karta hai.
- `static/library.html` — 2 labels ("max 2 MB" → "max 10 MB") + client-side pre-check `2*1024*1024` → `10*...`.
- `tests/test_library_api.py` — oversized tests (single + bulk) ab `10 MB + 1` use karte hain
  (warna 2 MB payload naye limit ke neeche aa ke corrupt-path test karta, size-path nahi).
- **Verified (manual):** 7.34 MB real PNG → 200 + 1200×1200 WebP ✓; 64 MP pixel-bomb (0.19 MB file) → 400 guard ✓
- pytest + ruff: baad mein (user browser test kar raha hai).

---

## 2026-07-16 — feature/fix-warning-null (in progress)

**Bug:** `adaptive_results_service.py` mein `upload_results()` warning calculation fail hoti thi jab `school_settings` table mein `class_size`/`min_analysis_percent` columns `NULL` hote hain (SQLite `ALTER TABLE ADD COLUMN` existing rows ko NULL rakhta hai). `settings.get("class_size", 25)` ka default sirf missing key par kaam karta hai — NULL value par `None` return hota tha, phir `math.ceil(None × pct / 100)` crash.

**Fix (`adaptive_results_service.py` lines 64–78):**
- `settings.get("class_size") or 25` — `or` None aur 0 dono handle karta hai
- `settings.get("min_analysis_percent") or 60` — same
- Poora warning block `try/except Exception: pass` mein — warning crash hone par upload fail nahi hoga

## 2026-07-16 — feature/remove-dashboard → master (dashboard.html delete)

**Kya kiya:**
- `static/dashboard.html` delete kiya — legacy page tha, Results screen hatayi thi to orphan ho gaya tha;
  Analytics screen (index.html) same kaam karta hai aur zyada features bhi hain
- `static/index.html` — saare references clean kiye:
  - `#dashboardBtn` button Results screen se hata diya
  - `mpDashboard()` aur `openDashboard()` functions delete
  - 3 jagah `dashboardBtn.style.display` lines delete (loadPaper, generateQuestions, buildAdaptivePaper)
  - CSV upload ke baad auto-open dashboard line delete
  - My Papers table mein "Dashboard" button delete
  - `btn.dashboard` i18n keys (EN + UR) delete
- Analytics screen aur Adaptive Analysis untouched

---

## 2026-07-16 — feature/category-dropdown → master (Image Library category dropdown)

**Kya kiya:**
- `static/library.html` — Category field 2 jagah text box se dropdown bana:
  - **Bulk Tag modal**: `bmCategory` input → select (12 options) + hidden `bmCategoryNew` text box
  - **Edit modal**: `editCategory` input → select + hidden `editCategoryNew` text box
- `_buildCategorySelect()` helper: dono selects consistently populate karta hai;
  existing value auto-pre-select; unknown DB value → "Naya likhein" select + text box mein value
- `onBmCategoryChange()` / `onEditCategoryChange()`: "Naya likhein" chunne par text box dikhao
- `saveBulkMeta()` + `saveEdit()`: `__new__` sentinel resolve karke actual category string bhejte hain
- 12 categories (DB se): animal, concept, flower, food, fruit, furniture, number, object, shape, sports, vegetable, vehicle

---

## 2026-07-16 — feature/bloom-suggestions → master (Bloom Taxonomy class-wise suggestions)

**Kya kiya:**
- `app/core/bloom_standards.py` (naya) — 4 class groups (Pre-Primary/Primary/Middle/Matric) with
  Bloom % distributions; `get_bloom_suggestion()` with flexible matching: case-insensitive,
  spaces/dashes normalize, `Grade X` aur `Class X` dono variants support
- `app/api/bloom_suggestions.py` (naya) — `GET /api/bloom-suggestion/{class_name}`;
  match nahi → 404
- `app/main.py` — bloom_suggestions router registered
- `static/blueprint.html` — Grade dropdown ke neeche neela info box (`#bloomSuggestionBox`);
  `onGradeChange()` mein suggestion fetch + display; sirf mashwara, koi auto-fill/enforcement nahi

**Bug fix (same branch):** DB mein grades `Grade 4`/`Grade 6` etc hain, `Class X` nahi —
`bloom_standards.py` mein `Grade X` variants add kiye taake matching kaam kare.

**Distributions:**
- Pre-Primary: Remember 70%, Understand 30%
- Primary: Remember 30%, Understand 35%, Apply 25%, Analyze 10%
- Middle: Remember 20%, Understand 30%, Apply 30%, Analyze 20%
- Matric: Remember 15%, Understand 25%, Apply 30%, Analyze 20%, Evaluate 10%

---

## 2026-07-16 — feature/adaptive-skip-upload → master (Adaptive: skip upload if results exist)

**Kya kiya:**
- `app/api/adaptive_results.py` — naya route `GET /api/adaptive/has-results/{paper_id}`:
  paper nahi → 404; uploads nahi → `{has_results: false, student_count: 0}`;
  upload mila → unique roll_no count → `{has_results: true, student_count: N}`
- `static/index.html` — Step 1 mein `div#adHasResultsBox` add kiya (green info box, default hidden)
- `static/index.html` — `onAdaptivePaperSelect()` async ho gayi: paper select hote hi
  has-results check karta hai; results hain → box dikhao + "Upload Results" button chhupao;
  2 buttons: "Analysis dekho →" (Step 3) aur "Naya Result Upload karo" (Step 2)
- Existing upload/analysis/generate logic unchanged

**Verified:** `GET /api/adaptive/has-results/628ccbea-...` → `{has_results: true, student_count: 25}` ✓

---

## 2026-07-16 — feature/analytics-improve → master (Analytics screen improvements)

**Kya kiya:**
- `static/index.html` — Paper ID text box hata ke dropdown lagaya (GET /api/papers se load hota hai); paper select hote hi auto analytics load; "Analytics dekhen" button backup ke liye rakha
- `static/index.html` — "Kaisa tha?" column add kiya per-question table mein — Roman Urdu difficulty explanation: >80% "Asaan tha — X% ne sahi kiya", 40–80% "Theek tha", <40% "Mushkil tha — sirf X% ne sahi kiya"
- `static/index.html` — Row background color ab Difficulty Index (P-value) se: Green (40–80%), Yellow (80–90% ya 30–40%), Red (>90% ya <30%); D-index column aur Quality badge unchanged
- `static/index.html` — `initAnalyticsScreen()` naya function: showScreen('analytics') hook se call hota hai, `currentPaperId` auto pre-select karta hai
- Legend text update: difficulty range explain karti hai (P-value based)

**Tests:** sirf frontend — koi backend change nahi, pytest pending

---

## 2026-07-15 — feature/language-filter HISSA 2+3 (commit de7b95b)

**Kya kiya:**
- `app/services/blueprint_paper_service.py` — `language_filter` har section se read karke `_fetch_simple` + `_fetch_with_distribution` ko pass. Shortfall notes mein `(English only)`/`(Urdu only)` label.
- `app/services/paper_service.py` — `_pick_questions()` ko `language_filter` param mila; `assemble_balanced_paper` aur `_assemble_by_ratio` `req.language_filter` pass karte hain (adaptive paper mein nahi — `AdaptivePaperRequest` mein field nahi).
- `static/blueprint.html` — FILTERS row mein Language dropdown (Sab / English only / Urdu only); `onLangFilter()` handler; `addSection`/`loadPreset`/`loadBlueprintToUI` mein `language_filter: null` default.
- `static/index.html` — Generate paper form mein Language filter dropdown; `buildPaper()` POST body mein `language_filter: langVal || null`.

**Tests:** 635 pass (pehle wali 3 adaptive failures fix ho gayi — `AdaptivePaperRequest` mein field nahi thi).

---

## 2026-07-15 — feature/language-filter HISSA 1 (commit 6fcc19f)

**Kya kiya:**
- `app/repositories/questions_repository.py` — `_apply_language_filter()` helper; `find_for_blueprint_section`, `find_least_used`, `find_for_bank_paper` mein `language_filter` param.
- `app/schemas/requests.py` — `GeneratePaperRequest` mein `language_filter: Optional[Literal["en","ur"]] = None`.
- `tests/test_language_filter.py` — 11 nayi tests (repository + schema validation).

---

## 2026-07-15 — fix/bad-file-crash → master (Bulk upload crash guard)

**Kya fix kiya:**
- `app/services/bulk_import_service.py` — 0-bytes upfront check; corrupt file pe user-friendly message (raw Python exception expose nahi hota); header-only xlsx pe explicit error; DB insert per-row try/except
- `app/api/questions.py` — `file.file.read()` try/except mein wrap kiya (pehle unguarded 500 tha)
- `tests/test_bulk_import.py` — 5 nayi `TestBadFileCrash` tests: jpg ext, 0 bytes, corrupt message quality, header-only, server survives 3 bad uploads
- `start.bat` — naya launcher: `.env` load, venv check, browser auto-open 2s baad

**Tests:** 624 pass, ruff clean

---

## 2026-07-15 — fix/edit-modal-save → master (print.html answer_lines save bug)

**Root cause:** `saveQuestion()` mein `question_ur`, `correct_answer_en`, `correct_answer_ur` hamesha payload mein jaate the (empty string `""`). `_not_blank` Pydantic validator 422 raise karta tha → answer_lines kabhi DB tak nahi pahunchti thi.

**Kya fix kiya:**
- `static/print.html` — `saveQuestion()`: optional text fields sirf tab payload mein jayen agar non-empty (empty string → omit)
- `static/print.html` — `ef_answer_lines` dropdown options fix: `0, 2, 3, 4, 6, 8` (bank.html se match; pehle `5, 10` the jo invalid hain)
- `tests/test_print_edit_modal.py` — 8 naye tests: valid values, zero, bilingual, empty-string-422, DB persistence

**Tests:** 619 pass, ruff clean

---

## 2026-07-15 — feature/bulk-answer-lines → master (Bulk Excel mein answer_lines column)

**Kya bana:**
- `app/services/bulk_import_service.py` — `answer_lines` column parse karo (valid: `0,2,3,4,6,8`; invalid/blank = NULL + warning)
- `app/repositories/questions_repository.py` — `insert()` mein `answer_lines` column add
- `static/bulk_upload_template.xlsx` — `answer_lines` column (22nd, green/optional) add kiya
- `tests/test_bulk_import.py` — 11 naye tests (valid values, zero, blank, invalid, non-numeric, backward compat, parametrize)

**Tests:** 590 pass, ruff clean

---

## 2026-07-15 — Pre Year 1 questions delete (197 sawal)

- Backup: `paper_maker_backup_pyr1_20260715_104351.db`
- DELETE: 197 Pre Year 1 sawal (syllabus_topics JOIN, grade='Pre Year 1')
- Baad mein Pre Year 1 count = 0 ✓, baaki classes (70 sawal) safe

---

## 2026-07-14 — Image Library — Excel se Meta Import (feature/image-meta-import → master)

**Kya bana:**

- **`app/services/library_meta_import_service.py`** (naya) — Core service:
  - `import_meta_from_excel(file_bytes)`: pandas se Excel parse, har row par `image_name` se DB match
  - Topic resolution: `subject + class` hint ke saath priority — subject+grade > subject-only > global first
  - Partial update: khali cell = us field ko chhua nahi (purana data rahe)
  - Return: `{updated, skipped, results: [{row, image_name, status, reason?, warnings?}]}`

- **`app/api/library.py`** — 2 naye routes:
  - `POST /api/library/excel-meta-import` — Excel upload, service call, JSON summary
  - `GET /api/library/excel-meta-import/template` — template .xlsx download

- **`static/library_meta_import_template.xlsx`** (naya) — 7-column template (image_name zaroori, baaki optional), colored headers, 2 example rows

- **`static/library.html`** — Bulk Upload card ke baad naya card:
  - Template download button, xlsx file input, Import button
  - `importMetaExcel()` JS: POST → results render (row number + status + warnings) → grid reload
  - Same `.bulk-results` CSS — Bulk Upload se consistent UI

**Tests:** 17 naye tests (11 service + 6 API) — 579 total pass, ruff clean

**Excel columns:**
`image_name` (zaroori) | `topic` | `subject` | `class` | `keywords` | `category` | `question_types`

---

## 2026-07-11 — Image System HISSA C — In-form image selection UI (feature/image-system)

**Kya bana (frontend only — koi backend change nahi):**

- **`static/print.html`** — Edit modal mein topic thumbnail strip:
  - Modal khulte hi `loadTopicStrip(topicId, qid)` call hoti hai
  - `/api/library?syllabus_topic_id=...` se images fetch, strip mein dikhayi
  - Thumbnail click → `applyLibraryImageInModal()` → image-from-library API → modal ka preview update
  - Topic na ho ya images na hon → strip hidden (no clutter)
  - "Choose Image" file upload button barabar maujood hai (dono options)

- **`static/bank.html`** — Add form + Edit modal mein thumbnail grid:
  - Add form: topic select `onchange="onAddTopicChange()"` → library images strip
  - Thumbnail click → highlight (selected), dobara click → deselect
  - Question save hone ke baad agar image select thi → image-from-library API call
  - Edit modal: `openEditModal()` mein `_loadEditStrip(topicId, qid)` call
  - Edit thumbnail click → seedha attach + list refresh + modal close

**Test run:** 482 passed (no backend change) — ruff clean

**Browser test checklist (khud check karo):**
1. print.html: paper mein ✏️ button → modal khule → agar topic hai to library strip dikhe
2. Strip mein thumbnail click → modal preview update ho, file upload button abhi bhi kaam kare
3. Topic nahi ya library mein images nahi → strip bilkul nahi dikhi
4. bank.html: nayi question form → subject → class → topic chunein → library strip dikhe
5. Thumbnail click → highlighted ho (blue border), dobara click → deselect
6. "Save" karo → question save + image attach ho (list mein image_path set ho)
7. Edit button → modal khule → strip dikhe → click karo → modal band, list refresh ho
8. Purani "Choose Image" file upload dono jagah abhi bhi kaam kare (backward compat)

---

## 2026-07-11 — Image System HISSA B — Excel image column (feature/image-system)

**Kya bana:**

- **`app/services/bulk_import_service.py`** — `image` column support:
  - `_find_library_image(name, topic_id)` helper: topic-scoped match pehle (`find_by_name_and_topic`), phir global (`find_by_name`), narm (case-insensitive, trim)
  - `_validate_row()` — `_image_name` internal field pass-through
  - `import_from_bytes()` — post-insert: library se file `static/uploads/` mein copy, `image_path` set; naam na mile → warning (skip nahi)
  - `image` column absent (purani files) → `""` → koi action nahi (backward compat)
- **`static/bulk_upload_template.xlsx`** — `image` column (13th) add kiya
- **`tests/test_bulk_import_image.py`** — 7 nayi tests

**Test run:** 482 passed, 0 failed — ruff clean

**Browser test (khud check karo):**
1. Purana template (.xlsx bina image column) import karo → bilkul theek chale
2. Naye template mein image naam likho (library mein pehle upload karo) → question mein image dikhe
3. Galat naam likhain → question import ho, warning mein naam aaye
4. Case mismatch test: "OrangeS5" library mein, "oranges5" Excel mein → match ho

---

## 2026-07-11 — Image System HISSA A — Bulk Image Upload (feature/image-system)

**Kya bana:**

- **`app/core/database.py`** — `image_library` table mein `name_normalized TEXT` column add kiya (CREATE TABLE + safe ALTER TABLE migration existing DBs ke liye + back-fill UPDATE)
- **`app/repositories/library_repository.py`** — `insert()` updated: `name_normalized = name.strip().lower()` field include hoti hai. Teen nayi helpers: `name_exists(name)` (duplicate check), `find_by_name(name)`, `find_by_name_and_topic(name, topic_id)` (HISSA B ke liye)
- **`app/api/library.py`** — `POST /api/library/bulk` nayi route: `List[UploadFile]`, per-file MIME + size + duplicate check, skip karo invalid/duplicate, result list wapas karo
- **`static/library.html`** — "Ek saath kai images upload" card: multi-file input, subject/grade/topic cascade (alag single-upload se), per-file result list (ok/skip/err styled), library grid auto-refresh on success
- **`tests/test_library_api.py`** — 8 nayi bulk tests: all_added, duplicate_skip, wrong_mime_skip, oversized_skip, name_normalized_stored, topic_tagged, per_file_result_list, case_insensitive_duplicate

**Test run:** 475 passed, 0 failed — ruff clean

**Browser test (khud check karo):**
1. Library page → "Ek saath kai images" card dikhe
2. Subject → Grade → Topic cascade kaam kare
3. Multiple PNG/JPG files select → Upload → result list (ok/skip) dikhe
4. Duplicate naam dobara upload karo → skip + reason dikhe
5. GIF file try karo → skip (JPG/PNG only)
6. Grid refresh ho nayi images ke saath

---

## 2026-07-11 — Blueprint HISSA 4 — blueprint.html frontend (feature/blueprint)

**Kya bana:**

- **`static/blueprint.html`** — nayi file, poora Blueprint Builder UI:
  - Paper metadata: blueprint name, subject+grade cascade, paper title, class name
  - Preset loader: `/api/blueprint-presets` se presets — "Load sections" button
  - Dynamic section cards: heading, topic multi-select (syllabus se checkboxes), question types (MCQ/Fill/T-F/Short), count, marks_each, source filter
  - Live total marks bar (count × marks_each, real-time update)
  - "Save Blueprint" → `POST /api/blueprints` — DB mein save
  - "Paper Banao" → `POST /api/blueprint-paper` → `print.html?paper_id=...` mein redirect
  - Shortfall warnings: agar section mein maange zyada mile kam — yellow list dikhti hai
  - Saved Blueprints list: Load / Paper Banao / Delete per blueprint
- **Sidebars updated** — Blueprint link add kiya: `bank.html`, `library.html`, `print.html`, `index.html`
- **Branch:** feature/blueprint (commit a16a9fc)

**Test checklist (browser mein khud check karo):**
1. `/blueprint.html` open ho — sidebar aur page dono sahi dikhein
2. Subject → Grade change kare → topics load hon section cards mein
3. Preset load kare → sections replace hon
4. Section add/remove karo — marks bar update ho
5. Save Blueprint → success message aur list mein nayi entry dikhe
6. Paper Banao → print.html khole, paper render ho
7. Shortfall warning: aisa subject/topics chunein jahan kam questions hain
8. Saved list mein "Load" → form mein load ho; "Paper Banao" → direct paper
9. "Delete" → blueprint list se hata de

---

## 2026-07-11 — Blueprint HISSA 3 — print.html blueprint rendering (feature/blueprint)

**Kya bana:**

- **`app/schemas/responses.py`** — `Paper` model mein `sections_meta: Optional[str] = None` add kiya
  - Pehle FastAPI response_model strip kar deta tha — ab `GET /api/paper/{id}` mein sections_meta aata hai
- **`static/print.html` (HTML)** — `sectionA` + `sectionB` divs hata ke `sectionsContainer` bana
- **`static/print.html` (CSS)** — `.shortfall-note` style add kiya (yellow warning box, screen only)
- **`static/print.html` (JS)** — `loadPaper()` mein sections_meta branch:
  - `sections_meta` non-null → blueprint rendering: qMap build, har section ka `section-block` dynamically inject
  - `sections_meta` null → `_renderLegacySections()` call (A/B objective/subjective — bilkul unchanged)
  - Shortfall notes `.no-print .shortfall-note` — screen par dikhein, print mein nahi
  - `_renderLegacySections()` new helper: container mein sectionA/sectionB divs create karke purana `renderSection()` call karta hai
- **Tests:** 58 blueprint tests pass, ruff clean
- **Branch:** feature/blueprint (commit 3a76257) — merge pending

---

## 2026-07-11 — feature/bulk-import merged to master (HISSA 4 — Bulk Upload)

**Kya bana:**

- **Backend — `app/services/bulk_import_service.py`**
  - pandas se `.xlsx`/`.csv` parse (openpyxl engine)
  - Per-row validation: type check (mcq/fill/tf/short), blank question, MCQ options, correct letter/tf value
  - Topic matching: case-insensitive + strip → subject+grade → subject-only → global; match na mile to `topic_id=NULL` + fuzzy suggestion (difflib)
  - `source='manual'` insert — HISSA 1 ki `questions_repository.insert()` reuse
  - Return: `{added, skipped, errors: ["row N: wajah"], warnings: ["row N: note"]}`
  - Marks: blank/zero/invalid → silent default 1
  - `is_urdu=yes` → `question_ur` mein, warna `question_en`

- **API — `app/api/questions.py`**
  - `POST /api/questions/bulk-import` route (.xlsx/.xls/.csv accept, ext check at route level)

- **Frontend — `static/bank.html`**
  - "Bulk Upload — Excel se questions import karo" card (bank-paper card ke baad)
  - Drag-and-drop zone + file chooser (.xlsx/.csv, max 5 MB client-side check)
  - Upload button (disabled jab tak file na chune), Clear button
  - Result box: green (sab add), orange (kuch skip), red (sab skip) — har skip row ka number + wajah, warnings alag list
  - Question list auto-refresh after successful import
  - "Template download karo" button → `/bulk_upload_template.xlsx`

- **Template — `static/bulk_upload_template.xlsx`**
  - 4 sample rows (mcq/tf/fill/short), green styling
  - `Instructions` sheet mein puri guide

- **Tests — `tests/test_bulk_import.py`** — 39 tests
  - Happy path (xlsx + csv, sab 4 types), DB mein actually insert check
  - MCQ correct letter → option text resolve
  - is_urdu, marks defaults (blank/zero/string)
  - Per-row validation errors (blank question, invalid type, MCQ options, wrong correct)
  - Mixed valid+invalid — ek buri row se baaki nahi rukein
  - Topic matching (unknown → warning + import, blank → no warning)
  - File format errors (PDF reject, corrupt xlsx, missing column, empty file)

- **Merge:** `feature/bulk-import → master`, clean (koi conflict nahi)
- **Total: 409 tests pass, ruff clean**

## 2026-07-11 — feature/question-bank merged to master (HISSA 1–3 + bank.html)

**Kya bana:**

- **HISSA 1 — Manual Question CRUD** (`source=manual`)
  - `app/core/database.py` — `source TEXT DEFAULT 'gemini'` column migration; existing rows safe
  - `app/repositories/questions_repository.py` — `insert()` mein `source` field; `list_by_filters()` mein `source` filter support
  - `app/schemas/requests.py` — `CreateManualQuestionRequest` + `UpdateQuestionRequest` mein `source` field
  - `app/api/questions.py` — `POST /api/questions/manual` route (manual question create, no Gemini)
  - `tests/test_bank.py` — 231 tests (CRUD, source filter, edge cases)

- **HISSA 2 — bank.html (Manage Page)**
  - `static/bank.html` — nayi page: question list (filter: subject/class/topic/source), add/edit/delete modal, inline form validation
  - `static/index.html` — "Question Bank" nav link added (sidebar)
  - `static/library.html` — "Question Bank" nav link added (sidebar)

- **HISSA 3 — bank-paper route (bina Gemini API)**
  - `app/services/question_service.py` — `get_questions_for_bank_paper()` — DB se manual questions fetch, subject/source filter
  - `app/services/paper_service.py` — `create_bank_paper()` — paper object banao from bank questions (no API call)
  - `app/api/papers.py` — `POST /api/bank-paper` route registered
  - `tests/test_hissa3.py` — 284 tests (bank-paper route, source filter, question types)

- **bank.html UI — "Bank se Paper Banao" section**
  - `static/bank.html` — subject/class/topic select + "Paper Banao" button → `/api/bank-paper` call → `print.html` redirect

- **Ruff fix:** `tests/test_hissa3.py` — 2 unused variables (`g_id`, `qid`) removed (F841)

- **Total: 370 tests pass, ruff clean**

## 2026-07-10 — feature/image-library Hissa 4 (Auto-Suggest)

- `app/repositories/library_repository.py` — `topic_image_counts(ids)` added (returns {topic_id: count})
- `app/api/library.py` — `topics-with-images` response changed: `{"topics": {"id": count}}` (breaking change, test updated)
- `app/schemas/requests.py` — `CopyFromLibraryRequest` added (image_id + image_size validator)
- `app/api/questions.py` — `_LIBRARY_DIR` constant + `POST /api/questions/{id}/image-from-library` route (copy file from library to uploads, update DB)
- `static/print.html` — auto-suggest badges (📚 N image(s) — Dekho/Nahi), library picker modal (grid thumbnails, size selector), localStorage dismiss per paper, batch API call on paper load
- `tests/test_library_api.py` — topics-with-images tests updated for new shape + `test_topics_with_images_returns_counts` added
- `tests/test_copy_from_library.py` — 7 nayi tests (PNG/JPG copy, default size, replace old upload, 404s)
- **Total: 335 tests pass, ruff clean**

## 2026-07-10 — feature/image-library Hissa 2 (Library Manager page)

- `static/library.html` — nayi page: upload form (cascade Subject→Class→Topic dropdown), client-side file pre-check (type + size), image grid (filter: subject/grade/naam), delete with confirm
- `static/index.html` — "Image Library" nav link added (sidebar)
- `static/print.html` — "Image Library" nav link added (sidebar)
- **Total: 327 tests pass, ruff clean**

## 2026-07-10 — feature/image-library Hissa 1 (DB + API + backup)

- `app/core/database.py` — `image_library` table added in `init_db()`
- `static/library/` — folder created, gitignored
- `app/repositories/library_repository.py` — insert, find_by_id, list_by_filters, delete, topic_ids_with_images
- `app/schemas/responses.py` — `LibraryImage` model added
- `app/api/library.py` — POST /api/library, GET /api/library (filters), DELETE /api/library/{id}, GET /api/library/topics-with-images
- `app/main.py` — library router imported and included
- `backup.bat` — [3/3]→[4/4], library-backups step added
- `tests/test_library_api.py` — 12 nayi tests (upload PNG/JPG, wrong MIME 400, oversized 400, blank name 400, list+filter, delete, topics-with-images)
- **Total: 327 tests pass, ruff clean**

## 2026-07-10 — feature/image-size (Hissa 3)

- `app/core/database.py` — `image_size TEXT` nullable migration
- `app/schemas/responses.py` — `image_size: Optional[str]` in `Question`
- `app/schemas/requests.py` — `image_size` in `UpdateQuestionRequest` + validator (small/medium/large only)
- `app/repositories/questions_repository.py` — `image_size` in `insert()`
- `static/print.html` — CSS size classes (img-sm/md/lg), modal dropdown (sirf image wale questions par), renderQuestion() size class
- `tests/test_image_size.py` — 9 nayi tests (valid sizes, invalid reject 422, null field)
- **Total: 315 tests pass, ruff clean**

## 2026-07-10 — feature/question-image Hissa 1 (Backend)

**Kya kiya:**
- `app/core/database.py` — `questions` table mein `image_path TEXT` column migration added (nullable, existing rows safe)
- `app/repositories/questions_repository.py` — `insert()` mein `image_path` column add; `update()` already generic fields le leta hai
- `app/schemas/responses.py` — `Question` model mein `image_path: Optional[str] = None` add
- `app/api/questions.py` — 2 nayi routes:
  - `POST /api/questions/{id}/image` — JPG/PNG upload, max 2MB, content-type se ext decide, purani image (kisi bhi ext) pehle delete
  - `DELETE /api/questions/{id}/image` — DB NULL + file delete
- `static/uploads/` folder create (images yahan store hongi)
- `.gitignore` — `static/uploads/` add (GitHub par na jaaye)

**Tests (Hissa 1b):** `tests/test_question_image_api.py` — 9 nayi tests:
- PNG/JPG successful upload (200, file on disk, DB path set)
- Oversized (>2MB) → 400, koi file nahi likhi
- Wrong MIME (text/plain, image/gif, application/pdf) → 400
- Unknown question_id → 404
- Delete: file disk se hata, DB NULL
- Replace PNG→JPG: purana .png orphan nahi raha
- **Bug fix:** DELETE route mein `_UPLOADS_DIR / Path(...).name` use kiya (pehle `.parent` galat path de raha tha)
- **Total:** 306 tests pass, ruff clean.

**Hissa 2 (Frontend) — 2026-07-10:**
- `static/print.html` — edit modal mein image section add (file input, thumbnail preview, remove button, warning)
- `renderQuestion()` mein `imageHtml` — `max-height: 180px` screen, `160px` print
- `onImageFileChange()` — client-side pre-check (type + size), instant local preview, auto-upload
- `uploadQuestionImage()` — FormData POST, server response se `_paperQuestions` + re-render
- `deleteQuestionImage()` — DELETE, in-memory update + re-render, UI reset
- `printWithImagesLoaded()` — `Promise.all(imgs.map(img => img.decode()))` phir `window.print()`
- Print button ab `printWithImagesLoaded()` call karta hai
