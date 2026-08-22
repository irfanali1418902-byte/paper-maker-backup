> # ⛔ ARCHIVE — YE SPEC MAT CHALAO (2026-08-22)
>
> **Classic navy/gold** palette par likhi hui hai, jo **Modern** se supersede ho
> chuki. Header khud kehta hai *"`static/theme.css` already exists from Round 1"* —
> wo file ab **mojood nahi** (UI-064 mein delete).
>
> `blueprint.html` us ke baad migrate ho chuka: `UI-047b`, 2026-08-13, aur ab wo
> ITCSS tree (`static/css/pages/blueprint.css`) par live hai.
>
> **Aaj ki asal jagah:** `docs/ui/STATUS.md` (haalat), `docs/ui/PLAN.md` (plan).
> Ye file sirf tareekh ke liye rakhi hai.

# PaperMaker — Blueprint Visual Redesign Spec (Round 2)

**For:** Claude Code CLI
**File:** `static/blueprint.html` (+ `static/theme.css` already exists from Round 1)
**Kyun:** Round 1 mein sirf **recolor** hua (hex → token). Look wahi raha. Ab **layout/components ko mockup (`papermaker-mockup.html`, Classic style) jaisa** banana hai — asli visual farq. Structure/JS/logic phir bhi untouched.

---

## 0. Golden rule (Round 1 ki galti dohrani nahi)

Round 1 sirf color tha. **Ab shakl badalni hai** — cards, spacing, headers, chips, badges, tables ki *appearance*. Lekin:

- **Koi `id`, `onclick`, `name`, `data-*` attribute NAHI badlega.** Sirf class add/CSS.
- **Koi JS function, `_apply_pinned`, coverage query, draft-exclusion, taqseem validation NAHI chhera jayega.**
- **Koi naya route ya DB column NAHI.**
- Markup **re-order/re-nest sirf tab** jab visual ke liye zaroori ho, aur us waqt bhi saare `id`/`onclick` element pe waise ke waise rahenge (element move ho sakta hai, uska handler nahi).
- Har element jo JS `getElementById`/`querySelector` se pakadta hai — uska `id`/selector byte-identical rahe.

**Pehle karo:** `grep -n "getElementById\|querySelector\|onclick=\|id=" static/blueprint.html` — ek list banao kis-kis element ko JS chhoo raha hai. Un elements ke `id`/handler ko lock treat karo.

---

## 1. Mockup se kya adopt karna hai (Classic style, visual language)

Reference: `papermaker-mockup.html` ka `data-style="classic"` block. Yeh visual "signature" laani hai:

### 1.1 Cards — sabse bada farq
Mockup mein har box ek `.card` hai jiska **alag header** hai:
```
.card {
  background: var(--panel); border: 1px solid var(--line);
  border-radius: var(--radius);           /* 10px */
  box-shadow: var(--shadow);              /* soft, do-layer */
}
.card > .ch {   /* card header: title + right-side meta */
  display:flex; align-items:center; gap:10px;
  padding:14px 20px; border-bottom:1px solid var(--line);
}
.card > .ch h3 { font-family:var(--font-display); font-size:14px; font-weight:700; }
.card > .cb { padding:20px; }   /* card body */
```
> Abhi blueprint mein "Paper ki details", "Preset se shuru karo" waghera plain sections hain bina card-header ke. Inko `.card > .ch (title) + .cb (body)` structure do. Title text jaisa hai waisa rahe (translate mat karo).

### 1.2 Section cards (`.sec-card`) — naya look
Mockup `.sec` style:
```
.sec { border:1px solid var(--line); border-radius:var(--radius-sm); overflow:hidden; }
.sec .sh {  /* section header strip */
  display:flex; align-items:center; gap:10px;
  padding:11px 14px; background:var(--panel-2);
}
.sec .sh b { font-family:var(--font-display); font-size:14px; }
.sec .body { padding:8px 14px; }
```
Section header mein Bloom chip + marks/type chip right-aligned (`.chip`, `.chip.gold`). Question rows `.qrow` (flex, dashed divider between).

### 1.3 Pin buttons — mockup `.pin` look
Abhi pin ek inline-styled `<button>` hai ("daalo"/"✓ pinned"). Visual ko mockup jaisa karo:
```
.pin { width:26px;height:26px;border-radius:6px;display:grid;place-items:center;
       border:1px solid var(--line); color:var(--muted); background:var(--panel); }
.pin.on { background:var(--accent-soft); border-color:var(--accent); color:var(--accent); }
```
> **BUT** — pin button ka `onclick="togglePin(...)"`, uska `id`/selector, aur `_pinned` logic bilkul haath mat lagao. Sirf uski CSS class/appearance. Agar text "daalo/pinned" JS se set hota hai to text rehne do; sirf button ka box-style token-based karo. Behavior byte-identical.

### 1.4 Chips, tags, badges
- SLO code → `.tag` (mono, `--accent-soft` bg, `--brand` text).
- Filter/meta labels → `.chip` / `.chip.gold`.
- Coverage status → `.badge.g / .y / .r` (dot + %). Traffic-light rule same: green≥100 / yellow 60-99 / red<60; Unassigned=null.

### 1.5 Buttons hierarchy
Ek hi hierarchy: primary `.btn` (navy), gold action `.btn.gold`, secondary `.btn.ghost`. Mockup jaisa padding/radius. Existing button text + onclick untouched.

### 1.6 Inputs / selects
Mockup mein cleaner: `min-height` consistent, `--line` border, focus ring `--accent`/`--brand`. Labels chhote, `--muted`, 600 weight.

### 1.7 Page header
Mockup `.pagehead`: bada display-serif `<h1>` + `--muted` subtitle ek line. Blueprint ka "Blueprint Builder" + subtitle isi treatment mein.

### 1.8 Spacing / rhythm
Mockup zyada saans-leta hai: card gap `18px`, card body pad `20px`. Blueprint abhi thoda tight/flat hai — yeh breathing-room laao. (Compact nahi — Classic.)

---

## 2. Kya NAHI karna (guardrails)

- Kisi `id` ka naam nahi badlega. (JS toot jayega.)
- Kisi `onclick`/handler ka reference nahi badlega.
- `_pinned`, `togglePin`, `checkExamCoverage`, `showSloQuestions`, `onGradeChange`, `renderSecCard`, draft-exclusion, taqseem validation — logic byte-identical.
- Koi route/endpoint/DB column nahi.
- Fonts offline (koi CDN). Colors sirf `theme.css` tokens (koi naya hardcoded hex; contrast `#fff` allowed jaisa Round 1).
- `papermaker-mockup.html` ko copy-paste NAHI — usse *visual language* lo, apne markup pe map karo.

---

## 3. Kaam ka order (chhote steps, har ke baad ruko)

Bade file (1530 lines) mein ek saath sab mat karo. Is order mein, **har step ke baad ruk kar mujhe dikhao**:

1. **CSS-only foundation** — blueprint ke `<style>` mein `.card/.ch/.cb`, `.sec/.sh/.body`, `.qrow`, `.pin`, `.pagehead`, chip/tag/badge, button, input styles ko mockup-Classic values pe le aao (theme.css tokens use karke). Abhi markup ko haath mat lagao — sirf CSS ready karo. → dikhao.
2. **Page header + top card** — "Blueprint Builder" header ko `.pagehead`; "Paper ki details" ko `.card > .ch + .cb`. → incognito screenshot / mujhe dikhao.
3. **Preset + filter cards** — inko bhi card-header structure. → dikhao.
4. **Section cards + question rows + pin** — `.sec/.sh/.body/.qrow/.pin` visual. Pin ka onclick/logic untouched. → dikhao (yeh sabse nazuk — pin test karo).
5. **Coverage box + bloom suggestion + shortfall** — badge/chip/panel-soft look. Logic untouched. → dikhao.

Har step ke baad: `grep` se confirm koi `id`/`onclick` nahi badla (`git diff` mein sirf class/CSS lines), `node --check` inline JS, `pytest`, `ruff`. Commit har approved step ke baad (ya sab ke aakhir mein) — **push NAHI** (Irfan GitHub Desktop se).

---

## 4. Definition of done (per step)

- [ ] Visual mockup-Classic jaisa (card headers, spacing, chips, section cards, pins) — sirf recolor nahi, **shakl badli**.
- [ ] `git diff` mein koi `id=`/`onclick=`/handler-name change NAHI (sirf class + CSS + wrapper markup).
- [ ] JS `getElementById`/`querySelector` targets sab intact.
- [ ] Pin toggle, coverage box, bloom suggestion, paper-generate — sab chalte hain (incognito test).
- [ ] Draft questions paper mein nahi.
- [ ] `pytest` + `ruff` + `node --check` pass.
- [ ] Commit + Summary bhara. Push NAHI.

---

## 5. CLI ko dene ka prompt (copy-paste)

```
Read REDESIGN_SPEC_blueprint.md fully. papermaker-mockup.html sirf visual reference (copy-paste NAHI).

Round 1 mein sirf recolor hua — ab layout/components ko mockup Classic jaisa karna hai (asli visual farq).

Section 3 order follow karo. Step 1 se shuru: sirf CSS foundation (.card/.ch/.cb, .sec, .qrow, .pin, .pagehead, chip/tag/badge, button, input) mockup-Classic values pe — abhi markup mat chhedo.

Non-negotiable:
- Koi id/onclick/handler-name/data-attr NAHI badlega. JS logic (_apply_pinned, togglePin, checkExamCoverage, showSloQuestions, draft-exclusion, taqseem validation) byte-identical.
- Koi naya route/DB column NAHI. Colors sirf theme.css tokens. Fonts offline.
- Pehle grep se JS-touched elements (getElementById/querySelector/onclick) ki list banao — un ke id/handler lock.
- Har step ke baad ruko, git diff + grep dikhao (sirf class/CSS lines), pytest+ruff+node --check pass karo. Commit karo par PUSH mat karo.
- Har step se pehle 2-line plan do; approve ke baad likho.
```
