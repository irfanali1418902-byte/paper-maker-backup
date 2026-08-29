# UI-ARCH — what is left, in order, with estimates

**Written 2026-08-13**, from the board and from `git log`, at Irfan's request after a full
audit. `PLAN.md` holds the sprint definitions and does not change; this file holds the **order
they will actually be done in** and **what that is expected to cost**. When the two disagree
about sequencing, this file is the newer decision.

---

## Where the epic actually stands

**9 of 9 pages are live** as of 2026-08-13. **Marhala A is complete** — it was estimated at 4–7
sessions and took about two.

**And the duplication this epic exists to remove is still entirely present.** That is not a
failure, it is the middle of a strangler fig — but it should not be misread:

| | lines |
|---|---:|
| baseline, 2026-07-28 — nine `<style>` blocks | 2,133 |
| ~~2026-08-13 — `99-legacy/*.css`~~ | ~~2,115~~ |
| **2026-08-14 — `99-legacy/*.css`, still imported by every migrated page** | **2,075** |
| today — the new tree (`01-settings` … `pages/`) | 3,064 |
| ~~today — `theme.css`~~ | ~~212~~ **DELETED 2026-08-13** |
| today — `app.css`, **still linked by all nine** (`@font-face` + the `.icon` sprite) | 57 |

**CSS has roughly doubled and nothing has been deleted yet.** The old tree comes out in
Sprint 6, which has not started. **"9 of 9 live" is the halfway marker, not the finish** — and
**`theme.css` is now deleted** — 212 lines, 0 deltas, the first commit in this epic that only
removes. `app.css` is a different matter: all nine pages still link it, and it goes with the
rest of `UI-064`. **`legacy_css_lines` has still not moved**, and that is the number that
matters.

---

## The order

### Marhala A — open the last two pages · **4–7 sessions**

| # | task | est. | why it is this size |
|---|---|---:|---|
| ~~1~~ ✅ | **UI-046** nav + shell | 1 | **DONE 2026-08-13.** The board's twelve rules were nine: `.app` and `.top .spacer` were already complete in `shell.css`, and `.nav a .icon` is dead |
| ~~2~~ ✅ | **UI-047b** `blueprint` | 1 | **DONE 2026-08-13, and it verified UI-046** — nine rules from `matches:0` to live. Two re-classes turned out to be additions: `.brand` (brand.js) and `.main` (legacy:28) |
| ~~3~~ | ~~**D22** — Irfan's decision~~ | — | **THIS ROW WAS WRONG AND SO WAS EVERY OTHER PLACE THAT SAID IT.** `DECISIONS-FOR-IRFAN.md`:67 corrected it on 2026-08-04: D22 is a technical constraint for Sprint 6, not a decision. The correction had not propagated, and this file repeated it on 2026-08-13 without checking |
| ~~4~~ ✅ | **UI-047c** `index` | 1 | **DONE 2026-08-13. 9 of 9.** Feared as the riskiest item and was the SMALLEST migration in the epic: no compat block (index declares all 27 tokens it reads), no re-classing (its shell is its own `.app-sidebar`), no UI-046. 2,476 deltas on the page, every one accounted for. **Irfan found the one real bug in the browser** — the sidebar could not scroll |

**Marhala A is COMPLETE — 9 of 9 pages live, 2026-08-13.** Estimated at 4–7 sessions and took
about two, because `index` — carried here as the riskiest item in the epic — turned out to be
the smallest migration in it.

### 🛑 THE DRAIN DOES NOT GO TO ZERO — Irfan's decision, 2026-08-19

**This overrides `UI-060..063`'s stated goal ("drain `99-legacy/<page>.css` to zero") and it is
recorded here because a session that reads the old wording will do three to five sessions of
work that was deliberately cut.** Same shape as the navy sidebar decision of 2026-08-13.

Measured 2026-08-19, at `legacy_css_lines` **1,949** — of its 1,594 rule-block lines:

| | lines | | verdict |
|---|---:|---|---|
| **page-only** — appears in one file, no component is possible | **999** | 63% | **SKIPPED** |
| **shared but drifted** — `.btn-ghost`, shell, `.brand`, modal, card | **495** | 31% | **do it** |
| **shared and identical** — cheap dedup | **100** | 6% | **do it** |

**Why the 999 are skipped, and it is not fatigue.** Draining them means moving each rule from
`99-legacy/<page>.css` into `pages/<page>.css`. **Both are already one file per page.** Merging
two per-page files into one per-page file removes no duplication, no CSS and no lookup step —
`legacy_css_lines` would fall to ~0 while the stylesheet count and the line count stayed where
they are. The metric would move and nothing else would.

**Where the value actually is: the 495.** Those are the rules where the app is visibly
inconsistent with itself — `.btn-ghost` renders **four different ways across five pages**, the
shell has drifted, `.brand` has drifted. Fixing them is user-visible and is the thing this epic
was started for.

**So the target is `legacy_css_lines` ≈ 1,200–1,400 and a visually coherent app, not 0.**
Estimated 5–8 sessions. Anything below that number is the 999, and the 999 are not the work.

**Re-derive the split with `scripts/css_duplication_audit.py`** — it is a repo file so this
decision does not rest on a number nobody can check. **The three figures move as work lands**
and will not reproduce 999 / 100 / 495 exactly: every rule that becomes a component leaves the
`agree` or `disagree` bucket. What must stay true for the decision to hold is the *shape* —
roughly two thirds page-only. Read the script's header before quoting it: it compares
declaration TEXT, and text that matches can still paint differently.

### Marhala D — Sprint 6, the actual cleanup · **6–12 sessions**

Taken **before** B and C, deliberately — see "What is being skipped" below.

| # | task | est. |
|---|---|---:|
| 5 | UI-060..063 — drain `99-legacy/*`. **STARTED 2026-08-13.** `css_drain_probe.mjs` written; all nine files measured; `slo.css` drained of its 10 dead rules — **2,115 → 2,105**, the first time that number moved. **2026-08-14: four pages onto `.sidenav`, 12 load-bearing rules rehomed and deleted — 2,105 → 2,075.** That is the first time rules that were *alive that morning* came out. See the survey and the correction below | 5–10 |
| 6 | ~~UI-064 — delete `theme.css`~~ ✅ **part 1 done 2026-08-13**, out of order and deliberately: `UI-047c` made the file unreachable that morning, so it became Marhala D's cheapest step. `app.css` + final sweep remain | 1 |

**CSS only goes down here.** Everything before this adds.

#### The drain survey — all nine files, measured 2026-08-13

| file | rules | 0-delta | load-bearing |
|---|---:|---:|---:|
| `landing` | 31 | 7 | 24 |
| `slo` | 45 | 19 | 26 |
| `taqseem` | 51 | 31 | 20 |
| `slo-health` | 57 | 33 | 24 |
| `library` | 93 | 28 | 65 |
| `blueprint` | 102 | 56 | 46 |
| `index` | 154 | 85 | 69 |
| `bank` | 154 | 53 | 101 |
| `print` | 158 | 79 | 79 |
| **total** | **845** | **391** | **454** |

**Read the middle column carefully — 391 is not the number of deletable rules.**
`slo` is the only file taken all the way through: of its **19** zeros, **10** were genuinely
dead and **9** were the probe's own blind spots — four `:hover`/`:disabled`, four `.pill*`
that exist only inside JS template strings, one `@media` outside the viewport. If that
roughly halves everywhere, the genuinely deletable share is **~200 of 845, about a quarter**.

**And the 454 are the work.** Deleting a dead rule is minutes; giving a load-bearing one a
home is a decision each time — a new component, the page's own entry file, or an accepted
change in value. **That half has not been done once.** `slo` still has all 26 of its
load-bearing rules.

#### The sidebar stays navy — Irfan's decision, 2026-08-13

Recorded here because it **overrides the design target**, and a roadmap that did not say so
would leave the next session reading `PLAN.md` §2 and `shell.css` for an intent that is no
longer the plan.

`mockup-modern.html`:38 makes Modern's default sidebar **white**. `04-objects/shell.css` and
`05-components/nav.css` were built to it, and `UI-047b` put `blueprint` on them — at which
point `blueprint` rendered `rgb(255,255,255)` while the other eight pages rendered navy. One
app, two looks, live. Asked to choose, Irfan chose **navy**, and `nav.css` was recoloured the
same day: 92 deltas on `blueprint`, **0 on the other seven**.

**✅ AND THE NAVY IS SETTLED — 2026-08-13, on the majority.** This block used to say three
navies existed and none had been chosen. They did, and one was: `--color-sidebar-bg` now reads
`--navy-900` (`#16294A`), the shade the six legacy files already carried, and `--slate-950` was
deleted from `tokens.css` having no other consumer. `blueprint` and `taqseem` moved 2 deltas;
the other seven were already there. `#132244` was `mockup-modern.html`:28's non-Modern theme and
was never in the running.

#### And the drain should go BY THING, not BY PAGE — measured 2026-08-13

`UI-060..063` is written as "per page: drain `99-legacy/<page>.css` to zero". Taking `slo`
that far first is what showed why that ordering is wrong. Of its 26 load-bearing rules, **9
are the navy sidebar shell** — and those same rules are in seven other files:

| selector | rules across all files | how many DIFFERENT versions |
|---|---:|---:|
| `.app-nav` (+ `a`, `a:hover`, `a.active`) | 36 | 3–4 |
| `.brand` (+ `.name`, `small`) | 30 | 6 |
| `.app-sidebar` | 16 | 5 |
| `.sidebar-foot` | 15 | 5 |
| `.page-head` (+ `h1`, `p`) | 11 | — |
| **total** | **~108** | |

**~108 of the 454 load-bearing rules are one shell, written eight or nine times.** This is
`PLAN.md` §1's opening complaint — *".app-sidebar 8 copies, .app-nav a 7 copies, .brand 9
copies"* — still true, and now measured at the rule level rather than the selector level.

**AND THE DUPLICATION HAS DRIFTED, WHICH IS THE PART THAT DECIDES THE TASK.** These are not
eight identical copies. Each selector has 3–6 genuinely different versions. But there is one
clean group: **`bank`, `library`, `slo-health` and `slo` are byte-identical across all five
selectors** — **50 rules between them**. `taqseem` joins them for `.app-nav` only;
`blueprint`, `index`, `print` and `landing` each drifted their own way.

So the shape of the work is not nine page-drains. It is: **extract the shell once, adopt it on
the four pages that already agree, then take the other five one at a time as decisions** — each
one being "accept the shared values, or keep this page's variant".

> **⚠ "50 rules out, ~13 in" WAS WRONG, AND IT WAS RUN ON 2026-08-14. It came out at 12.**
> The 50 counted the rules that AGREE across the four files. It did not check whether anything
> in the new tree could receive them, and `.sidenav` is a home for only **three of the nine**
> shell selectors — `.app-nav a`, `:hover`, `.active`. The other six have none:
> `.app-sidebar`'s box lives inside `.o-shell`, a whole-page grid these four have no topbar
> for; `.brand` ×3 was **deliberately denied a component** in `UI-047b` because it is live on
> all nine pages; `.sidebar-foot` has no component and `blueprint` has no such element; and
> `.app-nav`'s own `padding: 0 10px` survives even after `.sidenav` took its column and gap.
> **12 rules out, 30 lines, `legacy_css_lines` 2,105 → 2,075.** The remaining **24** — six
> rules × four pages — are still there and are the real shape of the 454.
>
> **The lesson is the method, not the number.** Counting which rules agree with each other is
> not the same question as counting which rules have somewhere to go. The second question is
> the one the drain is made of, and it is answered by reading the component against the legacy
> declaration by declaration, tokens resolved — not by a probe.

`shell.css` already exists from UI-030, but it is the NEW `.o-shell*` shell and only
`blueprint` uses it. The eight other pages still run the old navy one.

**What this does to the 5–10 estimate:** it stays, but the upper end is likelier. The cheap
quarter is now measured and could be cleared quickly; the 454 is not measured by anything,
because no page has been taken through it.

### What is being skipped, and it is a choice not an oversight

- **Marhala B** — `UI-042` (modal/field), `UI-043` (status-bar + 7 domain families), 3–4
  sessions. **No held page waits on either**, and `UI-043` was measured off the critical path
  on 2026-08-12 (`MEASURED.md` §📐).
- **Marhala C** — Sprint 5, the 466 inline `style=""`, 3–5 sessions. Much of it is expected to
  fall out of Sprint 6 anyway, when the legacy files those styles compete with are drained.

Both stay in `PLAN.md`. Neither is cancelled. They are simply not in front of anything.

### Marhala E — optional
`UI-070` — dedupe the sidebar markup's 8 copies. 1 session.

---

## ⛳ THE FINISHING PLAN — 2026-08-25, measured, in order

**Read this before anything else in this file.** Everything above it is the plan as it was
understood on 2026-08-13; this is what is actually left, re-measured today with
`scripts/css_duplication_audit.py` and `scripts/css_baseline.py`.

**Where we stand:** `legacy_css_lines` **1,842**. Target **~1,350**. Available work is
**490 lines** — 68 `agree` + 422 `disagree` — and 1,055 page-only lines are skipped on
purpose (2026-08-19). 1,842 − 490 = **1,352**, so the target and the work agree.

### The rule that makes this finishable

**One family per session. Every session is: measure → one decision if needed → edit → both
probes → review → Irfan's browser → commit.** Two families in one session is what makes a
diff unreviewable; that is not caution, it is the reason UI-061 and UI-062 both landed clean.

### The order, and why it is this order

| # | task | lines | decision needed | why here |
|--:|---|--:|---|---|
| ~~**1**~~ ⚠ | ~~**The button task** — D44 + D46 + D47(b)~~ **SHIPPED 2026-08-26 as UI-063, TWO THIRDS.** D44 ✅ (one radius, `--radius-control`) and D46 ✅ (`.5` + `not-allowed` everywhere) are closed. **D47 was never touched** — `forms.css` is not in the diff, so this row's own scope is unmet and the ring-vs-glow decision is still open. Three more things this row did not anticipate: the change is only true for filled **light-surface** buttons (**D48** on-dark, **D50** two navy segmented controls); the `cursor` third of the decision **produced zero deltas and no gate can see it** (**D49**); and the lines figure below was wrong — real effect **−1** legacy line, not 22, because it was first measured against a stale `BASELINE.json`. Detail: `PROGRESS.md` 2026-08-26 | ~~22 + 2~~ **−1** | **Three, all Irfan's:** one radius for every filled legacy button (`.btn-primary` is 10px, `.btn-save` now 11px); hover direction (some darken, some lighten); disabled opacity (.4/.5/.55/.6 across nine files) | **FIRST, and nothing else may go before it.** Every remaining family contains buttons, so each one taken first would add another radius to reconcile later. UI-062 already created that debt once |
| ~~**2**~~ ✅ | ~~**The viewport pass** — a tooling task, not a drain~~ **DONE 2026-08-27 as UI-064.** `css_type_probe` now reads five width bands (1280/900/740/700/520, one per band, derived by the new `scripts/css_breakpoints.mjs`) and **fourteen more properties** — the row below said "add a second viewport" and that alone would NOT have worked, because `flex-direction` (x22 inside media blocks), `flex-wrap`, `position` and `grid-template-columns` were not measured at all. Proved by control: mutating one declaration inside `slo`'s `@media (max-width:720px)` gives **0 deltas at HEAD** and **12** now. `css_state_probe` deliberately stays at one width — **zero state rules exist inside any `@media` block**, measured. No page CSS changed, ratchet unmoved. Detail: `PROGRESS.md` 2026-08-27 | 0 | none | **`shell/nav`'s 23 agree lines are 6 `@media (max-width: 720/760px)` rules and NO PROBE CAN SEE THEM** — every probe runs at 1280×900. This is D45's shape exactly: a gate that cannot measure the thing will pass regardless. Add a second viewport to `css_type_probe`/`css_state_probe` before touching any `@media` rule |
| ~~**3**~~ ✅ | ~~`shell/nav` — agree **and** disagree together~~ **DONE 2026-08-27 as UI-065.** `taqseem` and `print` moved onto the `sidenav` component (Irfan: one shell); `blueprint`'s three sidebar rules deleted as dead (**no `.app-sidebar` element exists on that page**); 14 legacy `@media` collapse rules deleted after the component took them. **The row's premise was wrong: there are NOT three navies** — all seven sidebar pages paint `rgb(22,41,74)`; three *spellings*, one colour, no decision needed. **And the task found a two-week-old bug:** `nav.css` had no `@media` rule and `legacy` is the weakest layer, so the narrow-screen collapse was broken on all five component pages. Fixed at root. `legacy_css_lines` 1841 → **1806**. Detail: `PROGRESS.md` 2026-08-27 | ~~23 + 76~~ **−35** | **One:** the shell has drifted into 3–6 versions per selector, and **there are three navies** (see line 375). Pick one shell, one navy | Biggest single family (99 lines, 8 files) and the most visible. Needs #2 done first |
| **4** | `field/filter` disagree | 59 | One: which control sizing wins | Its `agree` half shipped as UI-061, so the ground is known |
| **5** | `modal` disagree | 58 | One: the app has **three modal systems** (`modal.css`:  header). Decide whether they unify or stay three | Its `agree` half shipped as UI-062 |
| **6** | `card` + `brand` | 28 + 24 + 3 | One each | Small, independent, no ordering constraint |
| **7** | `chip/pill/row` + `page-head` + `shortfall` | 9 + 2 + 12 + 6 | One each, all small | The tail. Can be one session if the decisions are quick |
| **8** | `other` — 15 rules, 9 files | 138 | **Unknown — this is the honest gap.** Nobody has read these 15 rules; "other" is what the family regexes did not match | **Survey it before scheduling it.** It is the single biggest number on this table and the least understood. One session to read and split it into real families, THEN plan |
| **9** | `UI-064` — delete `app.css`, move mockups, final sweep | — | none | Last. 57 lines still linked by all nine pages for `@font-face` + the `.icon` sprite |

---

## 📋 THE PLAN FROM HERE — settled 2026-08-27, after items 1–3 shipped

**Measured 2026-08-27:** `legacy_css_lines` **1,806** · `unsanctioned_hex` **347** · target
**~1,350** · available work **461** lines (71 `agree` + 390 `disagree`). 1,806 − 461 = 1,345,
so the target and the work still agree.

> ### ⚠ RE-MEASURED 2026-08-28 AFTER ITEM 6 — AND THAT LAST SENTENCE NO LONGER HOLDS
>
> `legacy_css_lines` **1,759** · `unsanctioned_hex` **334** · available work **351**
> (69 `agree` + 282 `disagree`) · page-only **1,047** (75%, skipped by design).
>
> ```
> 1,759 − 351 = 1,408          target ~1,350          shortfall: 58 lines
> ```
>
> **The two numbers count different things, and that is the whole explanation.** Available
> work is measured on RULE-BLOCK lines — `css_duplication_audit.py` totals 1,398 of them.
> `legacy_css_lines` counts EVERY line. The 361-line difference is `:root` blocks, `@media`
> wrappers, comments and blank lines, and **the drain does not target any of it**. So as
> rules leave, that remainder sits still and the projected floor drifts UP, not down. It
> was 1,345 on 2026-08-27 and it is 1,408 today; it will keep rising.
>
> **This is a decision, not a defect, and it is Irfan's:** either the target becomes ~1,408
> and "done" means the last shared rule, or some of the 1,047 page-only lines come into
> scope — which is a different project, since page-only was excluded on purpose on
> 2026-08-19. **Do not quietly re-derive the target to make a session's numbers look good.**
>
> Method and the rule-by-rule evidence: `PROGRESS.md` 2026-08-28 (the audit entry).

### Two tracks, and they do not block each other

**TRACK 1 — the drain. One family per session, in this order.**

| # | session | lines | decisions needed from Irfan |
|--:|---|--:|---|
| ~~4~~ ✅ | ~~`field/filter` disagree~~ **DONE 2026-08-27 as UI-066.** Sizing: **44px / 6px**, the majority's (Irfan). **The row's question was a third of it:** of the 59 lines, seven properties per rule were already DEAD against `forms.css` by layer order; only `width`/`min-height`/`margin-top` were live. Two holes the probe found — `index` has **11 inputs with no `type` attribute**, which `forms.css`'s attribute-based selector never matched, and file inputs are outside that set by contract; deleting the legacy rules without covering both drops them to UA defaults. **And the three live properties could NOT move up a layer** — that broke six pages, four outside this family, because every compact override in the app is itself in `layer(legacy)` (**D51**). **Review then found a fifth thing:** `index`'s `input[type="color"]` was left unstyled. *(This row first said "no gate could have seen it — 0 deltas, closed panel". Corrected 2026-08-28: the probe read **30** deltas on it; the printed diff is capped at 60 per page and the reading was taken from the truncated list. D53.)* `legacy_css_lines` 1806 → **1799**, hex 347 → **338**. Detail: `PROGRESS.md` 2026-08-27 | ~~59~~ **−7** | done |
| ~~5~~ ✅ | ~~`modal` disagree~~ **DONE 2026-08-28 as UI-067.** Irfan: **keep the three systems, unify the values** — renaming classes means markup + JS on five pages and removes no CSS. ⚠ **This row's "58 lines, 5 files" was an undercount:** counted in the markup there are **eight** modals and **four** wrapper names, and the eighth (`print`'s `.lib-picker-overlay` library picker) was in no audit bucket at all because it is page-only. Six radii became one — and that one needed no decision, because `theme.css`:183's `--radius-container` already said "cards, panels, **modals**" and no modal had ever consumed it. Two new tokens: `--color-scrim`, `--shadow-modal`. 220 type / 30 state deltas, every one intended; `slo`, `slo-health`, `blueprint`, `landing` **0**. `legacy_css_lines` 1799 → **1798** — the value here was never in lines. Detail: `PROGRESS.md` 2026-08-28 | ~~58~~ **−1** | done |
| ~~6~~ ✅ | ~~`card` + `brand`~~ **DONE 2026-08-28 as UI-068/069, one commit.** Three decisions, not two: card values (new tree's — `--radius-container` / `--shadow-card` / `--space-gap`), the sidebar subtitle colour, and taqseem's brand. ⚠ **Both halves of this row's arithmetic were wrong, in opposite directions.** `card` said "6 files" and was **eight** — `pages/taqseem.css` and `pages/plan.css` each shipped a page-scoped bare `.card` with a header explaining why `card.css` could not, and the audit reads `99-legacy/` only, so it never saw them. `brand` counted **too much**: `landing`'s `.brand` is a hero block in a gradient header, not a sidebar brand, and it was removed from the family rather than unified. **Two pre-existing bugs fell out:** `print`'s brand had been sitting at `padding: 0` against the navy edge since UI-065 (the only one of seven), and the sidebar subtitle was rendering slate-500 on navy at ~3.1:1 on six pages — beaten not by legacy but by `03-elements/typography.css:88`'s bare `small { color }` in layer(elements). D51 fired three more times and every lift was verified by the absence of a single `padding` delta. `legacy_css_lines` 1799→**1759**, hex 338→**334**. Five new rows: D54–D58. Detail: `PROGRESS.md` 2026-08-28 | ~~52~~ **−39** | done |
| 7 | `btn` + `chip/pill/row` + `shortfall` + `page-head`. ⚠ **The 39 was disagree-only; re-measured 2026-08-28 the four families are 61** — btn 24, shortfall 20, chip/pill/row 11, page-head 6. **D49 IS NOW SETTLED (2026-08-28, UI-069a) AND IT HANDED THIS ROW A DECISION IT DID NOT HAVE.** The probe was never blind: `03-elements/forms.css`:155's bare `button { cursor: pointer }` sits in `layer(elements)` and beats `layer(legacy)` whatever the specificity, so **all six `cursor: not-allowed` declarations in `99-legacy/` are inert and always have been** — blueprint:48, index:96, library:185, print:74, print:83, slo:31. UI-063 chose `not-allowed` for every disabled button on 2026-08-26 and **that choice has never rendered on any page.** So this row is not "drain six dead lines"; it is **"does Irfan still want the choice, and if so it has to be re-shipped above `layer(legacy)`"** — and lifting it is D51 territory, the move that broke six pages in UI-066. Proof and method: `PROGRESS.md` 2026-08-28, rule in `PROBES.md` 9. (2) **`05-components/card.css`'s closing line says `.btn` is NOT safe**: `slo.html` has two live `class="btn"` buttons, so a bare `.btn` in layer(components) takes them — the same move item 6 made for `.card`, which only worked because every legacy `.card` modifier was enumerated first. **D47 is also still open and was supposed to close at item 1.** **⚠ SPLIT INTO TWO SESSIONS, 2026-08-28** — four families and five decisions in one diff breaks this file's own reviewability rule. **First half SHIPPED as UI-070**: the disabled cursor (now live for the first time, 1050 state deltas), `.btn-danger`/`.btn-edit` on bank's values, and `.page-head` → `.pagehead` on the last three pages. `legacy_css_lines` 1759 → **1757**, hex 334 → **333**. Two census corrections came out of it and both were the session's own errors: the btn size decision was first put to Irfan on a **markup** count of 1-per-page when the probe says **459/24** (they are JS-rendered — D12), and the `.pagehead` adoption first broke the layout because the four pages already on it wrap `h1`+`p` in a `<div>` — **a warning that was already written in their markup and was not read.** **Second half REMAINS**: `shortfall` (20) + `chip/pill/row` (11), both design forks, both already decided by Irfan — see STATUS.md. Detail: `PROGRESS.md` 2026-08-28 | ~~39~~ 61 → **31 left** | ~~4–5~~ **2 decided + 3 small** |
| 8 | `other` — **SURVEY ONLY, no code**. ⚠ **Add `body` to this survey (38 lines, 6 files).** It is filed under `shell/nav` by the audit's family regex and is therefore inside a row marked ✅, so no session is scheduled to touch it — see the remnants block below | 134 (+38) | **unknown, and that is the point** |
| 9 | delete `app.css`, move mockups, final sweep. **Do D56 first** — `plan.html` is in no probe's page list, and this row touches every page | — | none |
| — | the `agree` bucket | ~~71~~ **69** | none — it falls out of the sessions above |

### ⚠ A ✅ MEANS "THE DECISION WAS TAKEN", NOT "THE LINES ARE GONE" — measured 2026-08-28

Nothing above says this, and it is 44% of the remaining work. Of the 351 available lines,
**156 sit in families this table already ticks:**

| family | item | ticked | `agree` | `disagree` | still there |
|---|--:|---|--:|--:|--:|
| `shell/nav` | 3 | ✅ | 12 | 45 | **57** |
| `modal` | 5 | ✅ | 11 | 43 | **54** |
| `field/filter` | 4 | ✅ | 22 | 13 | **35** |
| `card` | 6 | ✅ | 2 | 4 | **6** |
| `brand` | 6 | ✅ | 0 | 4 | **4** |
| | | | | | **156** |

Each session left its remnant on purpose and said so in `PROGRESS.md` — item 6, for
instance, deliberately left `.card-title` (4 lines, three values) and `print`'s 18px brand
(2 lines) because neither was among the decisions Irfan was asked. **The problem is not the
leaving, it is that the board shows a tick and the remnant is invisible from here.** A
session planning from this table alone will believe items 3–6 are worth 0 lines.

**AND THE FAMILY LABELS THEMSELVES CAN BE WRONG.** Rule-by-rule dump, 2026-08-28:

```
shell/nav  DISAGREE  38L   body       bank,library,print,slo,slo-health,taqseem
modal      DISAGREE   2L   #status    index,print
```

`body` is not a nav. At 38 lines across six files it is **the largest single `disagree`
item in the repo after `other`**, and because the regex files it under a ✅ family, no row
schedules it. `#status` is not a modal. **This is the census lesson one level up: item 5
found the bucket counted too few, item 6 found `card` too few and `brand` too many, and now
the labels are wrong too. Read the rules, not the family name.**

**Item 8 is the honest gap and it gets its own rule: its first session writes no CSS.**
134 lines, 15 rules, 9 files, and **nobody has read them** — "other" only means the family
regexes did not match. Survey, split into real families, THEN schedule. Do not attach it to
a drain session.

**TRACK 2 — not sessions, Irfan's own work.**

* **Bank seeding** — 108 topics left (PY3 44 + PY2 64), ~20–26 AI calls/day = **5–6 days**.
  It is quota-bound, not time-bound, so run it FIRST each morning, then do everything else.
  Command and the four forbidden syllabi: §B row R1 above.
* **R7 plans for PY1 and PY2** — still empty. PY3's filled sheet is now in the repo
  (`namoona_plan_pre_year_3.xlsx`) so the shape is known.
* **Merge `master`** — the whole month sits on `feat/ui-architecture`, which is 158 commits
  ahead and no longer only UI work. **After item 9** is the natural point.

### Deferred rows, and when each one is actually due

| row | due |
|---|---|
| **D49** — no gate can see `cursor` | **before any decision that involves a cursor.** Either the probe is blind or every `cursor: not-allowed` in the repo is dead CSS; a small CDP experiment settles it |
| **D47(a)** — `forms.css`:76's comment contradicts the cascade | **safe and small** — do it in whatever session next opens `forms.css` |
| **D47(b)** — field focus: ring or glow | **Irfan's design decision.** The instrument is ready (`outline-*` is in the state probe) |
| **D48**, **D50** | parked; both need palette decisions and neither blocks anything |

### The estimate, on three sessions of real data

UI-063 **−1** line (a decision, not a drain) · UI-064 **0** (a tool) · UI-065 **−35**.
Plus the two before: UI-061 −9, UI-062 −22.

```
items 4–7, 9   one family per session, one decision each      6–9 sessions
item 8         survey (1) + whatever it turns out to be       3–5 sessions
──────────────────────────────────────────────────────────────────────────
the drain, from here                                          9–14 sessions
```

**The 10–17 estimate written on 2026-08-25 is holding.** Three sessions have run and removed
36 lines between them — but two of those three were not drains, and that is the point the
old rate-based estimate kept missing: **the cost of a session is the DECISION, not the lines.**

### One rule this week added, and it should survive the epic

**Do not write long comments into `99-legacy/*.css`.** `legacy_css_lines` counts every line,
comments included. UI-065's first draft deleted 24 lines of rules, wrote 44 lines of comment,
and made the number go **UP** — 1,841 → 1,861 — while genuinely doing the work. Reasoning
belongs in `PROGRESS.md`; the legacy file gets a pointer.

---

### The estimate as it stood on 2026-08-25 (superseded by the block above, kept for the argument)

**The old figure on this page said the drain was 5–8 sessions. Two sessions have now actually
run and they are the only real data:** UI-061 took `legacy` 1,873 → 1,864 and UI-062 1,864 →
1,842. **Nine and twenty-two lines.** At that rate 490 lines is far more than 8 sessions.

But rate-per-line is the wrong model and it is worth saying why: **the cost of a session is
the DECISION, not the lines.** UI-062 removed 22 lines and spent its time on one radius
question; item 3 removes 99 and asks one shell question. So:

```
items 1–7, 9   one family per session, one decision each     8–12 sessions
item 8         survey (1) + whatever it turns out to be      2–5 sessions
──────────────────────────────────────────────────────────────────────────
the drain, honestly                                         10–17 sessions
```

At 1 session/day, 5 days/week: **~2–3.5 weeks of working days.** The 2026-08-13 estimate of
5–8 was written before any Sprint 6 task had ever run.

### What is NOT on this list, deliberately

* **Sprint 5 (466 inline `style=""`)** and **Marhala B** (`UI-042`, `UI-043`) — nothing waits
  on them and much of Sprint 5 is expected to fall out of the drain. Unchanged decision.
* **`docs/ui/DEFERRED.md` has 44 open rows.** Most are notes, not tasks. Only D44/D46/D47 are
  scheduled above; the rest stay parked until something needs them.
* **The non-CSS work**, which is Irfan's and not a session: **R1 bank seeding** (~128 topics,
  ~6 days of a 10-minute daily command) and **R7 adoption** (`topic_week_plan` has 4 rows;
  one Excel plan needs filling). Neither blocks the epic and the epic does not block them.

### Two rules that came out of this week and should survive it

1. **A gate that cannot measure the thing will pass regardless.** D45 proved it for states,
   item 2 is the same problem for viewports. Before a task, ask what its change would look
   like to the probes — if the answer is "nothing", build the probe first.
2. **Close the row the day the work lands.** This file, `PLAN.md` and `docs/ROADMAP.md` all
   carried false rows for weeks or months. Every one cost a later session real time.

## What the estimate rests on, and where it is weak

**The basis is measured, not guessed.** 2026-08-05 → 08-12, once the work was components and
migrations rather than mechanical extraction: UI-041, UI-045, UI-040, UI-041b, UI-047d,
UI-047e, UI-047f, UI-047a — **8 tasks in 8 days, ~1 task per session.**

1. **A's estimate is strong; D's is weak.** Four migrations are done and their cost is known.
   **No task of Sprint 6's kind has ever been run here.** Draining legacy means every rule
   finds a new home or is proven dead, on pages whose content is substantially JS-rendered.
   The 5–10 could be 4. It could be 14.
2. ~~**D22 is not on the clock.**~~ **Struck 2026-08-13 — the premise was false.** `index` was
   never blocked on D22; that attribution was corrected on 2026-08-04 and the correction sat
   unread in `DECISIONS-FOR-IRFAN.md` while six other places kept repeating it, this file
   included. **Check the decisions file before recording something as a blocker.**
3. **One session is not one hour, and a revert is not a failure.** 2026-08-12 shipped
   `taqseem`, found a missing declaration in `btn.css`, struck `UI-043`, and caught a false
   all-clear from its own probe — 7 commits. `taqseem` itself was migrated and reverted once
   before it shipped, deliberately.

---

## Open items that are not sprint tasks

These are real and are tracked nowhere else. They are not in the estimate above.

| item | state |
|---|---|
| **`.app-sidebar` cannot scroll — OPEN on five pages** | `height: 100vh` with no `overflow`, on all six pages using the legacy shell. Content taller than the viewport spills out of the painted box instead of scrolling. **Found by Irfan in the browser on 2026-08-13** — `index`'s last nav item hung outside the navy background — and fixed page-scoped there only. `library`, `bank`, `slo`, `slo-health`, `taqseem` still have it; their navs are 209–294px against `index`'s 450px, so nothing has spilled yet. **No probe can see this**: at the probe's 900px viewport nothing overflows, and `overflow` is not a captured property |
| **`taqseem` browser check** | **done 2026-08-13, and the half that mattered is confirmed.** Chips render as standing blocks and a chip's select moves the SLO — the two things no probe can see. **Modal open/cancel and card/brand header were not checked** and are recorded as such. Use `Pre Year 1` + `Mathematics`; it is the only class/subject with a plan |
| **`STATUS.md` task-log gap** | the log table stops at `UI-041b`. **Six shipped tasks have no row**: UI-044a, UI-044b, UI-047d, UI-047e, UI-047f, UI-047a |
| **Dead-code audit — API layer** | done 2026-08-13, **and acted on.** 80 routes, 74 live. **`export.docx` + `export.pdf` DELETED** (`e2bdcc4`) — 630 lines including their tests, plus `python-docx` and a LibreOffice subprocess dependency; Irfan's call, and outside the UI-ARCH epic. **STILL OPEN: `/api/syllabus-topics` has no caller anywhere** and has not been decided. `blueprint-presets/{id}` and `library/question-types` are called by tests only — real routes with no frontend path, also undecided |
| **Dead-code audit — JS / CSS / services** | not started |
| **Two stale numbers, flagged not fixed** | `PLAN.md`:313 says `docs/ui/` is 2,655 lines (it is ~3,900). `main.css`:117 says `theme.css` is linked on 6 pages (it is 2) |
