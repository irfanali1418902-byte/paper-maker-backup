# ADR-001 — CSS architecture for a no-build multi-page app

**Status:** Accepted · **Date:** 2026-07-28 · **Supersedes:** `static/theme.css` as source of truth
**Context epic:** `docs/ui/PLAN.md` (UI-ARCH)

---

## Context

9 static HTML pages served directly by FastAPI. ~90% of the styling lives in per-page
`<style>` blocks — 2133 lines / 966 rules — plus 466 inline `style=""` attributes. The shared
`theme.css` is 213 lines and is routinely overridden, because page `<style>` loads *after* the
shared `<link>`. `index.html` redefines `--line` and `--muted`, the same token names `theme.css`
declares.

Fixed constraints (not negotiable, they define the solution space):

- **No build step, no bundler, no npm.** The app is launched by non-technical school staff via
  `start.bat`. A stale build artifact is a mystery bug nobody on site can diagnose.
- **Fully offline.** No CDN. Fonts are self-hosted woff2.
- **Served over LAN** (`uvicorn --host 0.0.0.0`) to ~20 teachers on other PCs. RTT is ~1ms.
- **Unknown browser version** on school machines.

## Decision

**ITCSS layer order as the skeleton + BEM naming for components + a small hand-written
utility layer.** Three-tier design tokens (primitive → semantic → component) authored directly
as CSS custom properties. One `<link>` per page to `main.css`, which owns the `@import` order.
Migration by strangler fig via a temporary `99-legacy/` layer imported first.

Full tree, token example and naming rules: `docs/ui/PLAN.md` §2.

## Alternatives considered

| Option | Verdict |
|---|---|
| **Utility-first (Tailwind)** | **Disqualified.** v4 requires a CLI/Vite/PostCSS build. The Play CDN is a CDN (breaks offline) and Tailwind's own docs say it is "for development purposes only, not intended for production." |
| **CUBE CSS** | Good and explicitly tool-agnostic, but niche versus BEM. Its "Exception" (`data-state`) idea is borrowed; the whole system is not adopted. |
| **SMACSS** | Largely superseded by ITCSS for file order. Its `is-` state convention **is** adopted. |
| **OOCSS** | Superseded as a system; its principles are absorbed into everything above. |
| **BEM as a whole system** | The Yandex toolchain is legacy. The **naming convention** is current practice and is adopted. |
| **Keep `theme.css`, just enforce it harder** | Rejected. Enforcement by convention is exactly what already failed — 6 pages shadow its tokens today. |

**Why ITCSS wins here:** it is purely a source-order discipline. It needs no tooling at all,
which is the binding constraint. It is also effectively ratified by the platform — Miriam
Suzanne (a CSS spec editor) proposes a cascade-layer order explicitly credited to ITCSS.

**Precedent:** 37signals ships Fizzy, Campfire and Writebook on vanilla CSS — ~14k lines
across ~105 files, zero build. This is not a compromise architecture.

## Decision: `@import` inside `main.css`, not many `<link>` tags

The "`@import` is slow" advice is real and still current — Erwin Hofman's 16M-site analysis
(Dec 2024) measured a ~300ms start-render penalty, because imports are invisible to the
preload scanner and serialise round-trips. HTTP/2 multiplexing does not fix it (the requests
aren't discovered yet) and H2 push was removed from Chrome in 2022.

It does not bind here: RTT is LAN-local (~1ms) and the import depth is 2, so the real cost is
~2 round trips. In exchange we get one file that defines cascade order, and one line to change
across 9 heads.

**Revisit if** the app is ever served over a real network. Then switch to explicit `<link>`
tags per file, or concatenate at FastAPI startup — regenerated every launch, so it can never
go stale. **Do not** hand-run a concat script; that reintroduces the stale-artifact failure
this project explicitly rules out.

## Decision: no `@layer` — for now

Support is genuinely good: Baseline "widely available" since 2024-09-14 (Chrome/Edge 99,
Firefox 97, Safari 15.4 — all by March 2022), ~94% global on caniuse.

**The failure mode is why we still decline it.** `@layer` does not degrade — it hard-fails. An
unsupported browser treats it as an unknown at-rule and **discards the entire block**, so the
page renders completely unstyled. On an offline school PC of unknown vintage, that is a
catastrophic failure taken on a guess, to buy override convenience we do not currently need.

Import order alone gives the same cascade. The tree is identical either way, so this is a
one-line change in `main.css`, not an architecture fork. Tracked as `DEFERRED.md` D1: adopt
once someone reads `chrome://version` on a real machine (anything ≥ 99 passes).

## Decision: tokens authored as CSS custom properties, not DTCG JSON

The W3C Design Tokens Community Group format reached its first stable version (2025.10) on
2025-10-28 — but it is a **Community Group Report, not a W3C Standard**, and turning its JSON
into CSS requires a build tool (Style Dictionary) we deliberately do not have. We adopt its
**naming/structure model** (three tiers, per Nathan Curtis / EightShapes) and author the
custom properties directly.

Invariant: **components reference Tier 2 only. A raw hex outside `01-settings/tokens.css` is a
CI failure**, enforced by `tests/test_css_architecture.py`, not by review.

## Consequences

**Good.** One place to change a colour. Specificity stays flat, so no `!important` arms race.
The shell is defined once instead of 8 times. Progress is measurable (`99-legacy/` line count).
Architecture violations fail CI rather than depending on a reviewer noticing.

**Cost.** ~30 tasks across 7 sprints. A temporary `99-legacy/` layer exists mid-migration and
looks untidy by design — that is the mechanism, not a smell. Six extra HTTP requests per page,
irrelevant on LAN.

**Risk accepted.** Removing a page's `<style>` block can *reveal* shared rules it was
previously masking. Mitigated by making Sprint 1 a verbatim cut with zero visual change, so
any difference proves the cut was wrong and the task is reverted and redone.

## Sources

- Miriam Suzanne, "Cascade Layers Guide," CSS-Tricks, 2022-02-21 — hard-fail behaviour, ITCSS mapping, legacy-layer pattern — https://css-tricks.com/css-cascade-layers/
- caniuse, CSS Cascade Layers — ~93.9% global (StatCounter, June 2026), retrieved 2026-07-28 — https://caniuse.com/css-cascade-layers
- Web Platform Features Explorer — Cascade Layers Baseline Widely Available 2024-09-14 — https://web-platform-dx.github.io/web-features-explorer/features/cascade-layers/
- Erwin Hofman, "The curious (performance) case of CSS @import," Web Performance Calendar, 2024-12-24 — https://calendar.perfplanet.com/2024/the-curious-performance-case-of-css-import/
- Rob Zolkos, "Vanilla CSS is all you need," 2025-12-03 — 37signals, no build — https://www.zolkos.com/2025/12/03/vanilla-css-is-all-you-need
- Nathan Curtis, "Naming Tokens in Design Systems," EightShapes — three-tier naming — https://medium.com/eightshapes-llc/naming-tokens-in-design-systems-9e86c7444676
- Philip Walton, "Decoupling Your HTML, CSS, and JavaScript," 2013-08-18 — origin of the `js-` hook convention — https://philipwalton.com/articles/decoupling-html-css-and-javascript/
- W3C DTCG, "Design Tokens specification reaches first stable version," 2025-10-28 (Community Group Report, **not** a W3C Standard) — https://www.w3.org/community/design-tokens/2025/10/28/design-tokens-specification-reaches-first-stable-version/
- Andy Bell, CUBE CSS — https://cube.fyi/
- Tailwind CSS Play CDN docs — "development purposes only" — https://tailwindcss.com/docs/installation/play-cdn

**Stated uncertainty:** caniuse's 94% is StatCounter-weighted global traffic, a poor proxy for
one known school PC. The `chrome://version` check is the real test, not the percentage.
