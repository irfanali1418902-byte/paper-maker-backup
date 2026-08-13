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
| today — `99-legacy/*.css`, still imported by every migrated page | **2,115** |
| today — the new tree (`01-settings` … `pages/`) | 2,401 |
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

### Marhala D — Sprint 6, the actual cleanup · **6–12 sessions**

Taken **before** B and C, deliberately — see "What is being skipped" below.

| # | task | est. |
|---|---|---:|
| 5 | UI-060..063 — drain `99-legacy/*` to zero, page by page. **STARTED 2026-08-13.** `css_drain_probe.mjs` written; **all nine files measured**; `slo.css` drained of its 10 dead rules — `legacy_css_lines` **2,115 → 2,105**, the first time that number has moved in this epic. See the survey below | 5–10 |
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

**⚠ THREE NAVIES EXIST AND NONE HAS BEEN CHOSEN.**

| shade | where |
|---|---|
| `#16294A` | the six pages whose legacy files declare their own `--navy` |
| `#0e1729` (`--slate-950`, behind `--color-sidebar-bg`) | `blueprint` and `taqseem` |
| `#132244` | `mockup-modern.html`:28, a non-Modern theme |

`blueprint` and `taqseem` now match each other, not the six. **Closing this moves a live
page's colour**, so it is left open on purpose and belongs to the shell work below.

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
the four pages that already agree (50 rules out, ~13 in), then take the other five one at a
time as decisions** — each one being "accept the shared values, or keep this page's variant".

`shell.css` already exists from UI-030, but it is the NEW `.o-shell*` shell and only
`blueprint` uses it. The eight other pages still run the old navy one.

**What this does to the 5–10 estimate:** it stays, but the upper end is likelier. The cheap
quarter is now measured and could be cleared quickly; the 454 is not measured by anything,
because no page has been taken through it.

### What is being skipped, and it is a choice not an oversight

- **Marhala B** — `UI-042` (modal/field), `UI-043` (status-bar + 7 domain families), 3–4
  sessions. **No held page waits on either**, and `UI-043` was measured off the critical path
  on 2026-08-12 (`NEXT-SESSION.md` §📐).
- **Marhala C** — Sprint 5, the 466 inline `style=""`, 3–5 sessions. Much of it is expected to
  fall out of Sprint 6 anyway, when the legacy files those styles compete with are drained.

Both stay in `PLAN.md`. Neither is cancelled. They are simply not in front of anything.

### Marhala E — optional
`UI-070` — dedupe the sidebar markup's 8 copies. 1 session.

---

## Total

```
A + D  (the plan)          10–19 sessions   ≈ 2–4 weeks
+ C                         3–5
+ B                         3–4
────────────────────────────────────────────
everything                 16–28 sessions   ≈ 3–6 weeks
```

At 1 session/day, 5 days/week.

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
