# PaperMaker — UI Design Implementation Handoff

**For:** Claude Code CLI (implementer)
**From:** Design review (mockup: `papermaker-mockup.html`)
**Rule:** Yeh spec follow karo. Mockup sirf *visual reference* hai — usko copy-paste mat karo. Existing pages ko incrementally update karo.

---

## 0. Sabse pehle — decide & confirm (Irfan bharega)

CLI implementation shuru karne se pehle yeh 3 cheezein fix hain:

| Decision | Choice | Note |
|---|---|---|
| **Base style** | `Classic` / `Modern` / `Compact` | Mockup mein teen the. Ek chuno. Default recommendation: **Classic** (already navy/gold brand ke qareeb). |
| **Pehli screen** | e.g. `blueprint.html` | Scratch se nahi — jo file already exist karti hai use pe polish. |
| **Scope is round** | Sirf CSS/layout, ya nayi feature bhi? | Is handoff ka default: **sirf visual/CSS refactor, koi naya route/column nahi.** |

> Agar naya route/column chahiye → alag Hissa banao, is handoff mein mat mila.

---

## 1. Golden rules (workflow — inko todna mana hai)

1. **Ek function ek jagah** — style tokens repeat mat karo, `brand.json` / central CSS se aayenge.
2. **Fix se pehle instrumentation** — pehle dekho current page mein kya hai (grep), phir badlo.
3. **Merge/push sirf GitHub Desktop se** — CLI kabhi `git push` na kare. Summary box khali na ho.
4. **`backup.bat` chalao** kisi bhi DB write se pehle. (Is round mein DB write nahi hona chahiye.)
5. **Server hard-restart** har naye route/column ke baad (`--reload` middleware ke liye reliable nahi). Is round mein sirf static/HTML/CSS change hai to reload theek — par confirm.
6. **Testing hamesha incognito** browser mein.
7. **Disk-verify har step:** `grep` / `diff` + `node --check` (agar JS) + `pytest` + `ruff`.
8. **Dry-run pehle**, `--apply` baad mein (jaha applicable).

---

## 2. Design tokens (central — `config/brand.json` + CSS)

Mockup ke teen styles mein se **jo choose kiya** uske tokens `brand.json` ya ek central `static/theme.css` mein daalo. Har page apne andar rang hardcode NA kare.

### Classic (recommended base)
```
--brand:      #132244   /* navy   */
--brand-2:    #1e3563
--accent:     #c8952b   /* gold   */
--accent-soft:#f6ecd4
--fg:         #1a2233
--muted:      #5c6a83
--line:       #dbe2ee
--panel:      #ffffff
--app-bg:     #eef1f6
--radius:     10px
font-display: "Source Serif 4"
font-body:    "IBM Plex Sans"
font-data:    "IBM Plex Mono"
```

### Traffic-light (coverage — sab pages same)
```
green  #2f9e58  bg #e5f5ec   (>= 100%)
yellow #c99400  bg #fbf1d4   (60-99%)
red    #cf4436  bg #fbe6e3   (< 60%)
```
> Rule: Unassigned = **null**, `0` nahi. Badge text "Unassigned" red style mein.

**Fonts offline hi rahenge** (IBM Plex Sans, Noto Nastaliq Urdu, Source Serif 4) — CDN mat lagao, app localhost/offline hai.

---

## 3. Reusable components (ek dafa banao, sab pages use karein)

Inko ek shared partial / CSS class set mein rakho (`static/theme.css` + optional `static/components.js`):

| Component | Class | Notes |
|---|---|---|
| Card | `.card > .ch (header) > .cb (body)` | border + soft shadow |
| Stat tile | `.card.stat` | lab / num / sub / progress bar |
| Traffic badge | `.badge.g / .y / .r` | dot + % |
| SLO tag | `.tag` | mono font, `M-1.04` style |
| Chip | `.chip`, `.chip.gold` | filters, meta |
| Button | `.btn`, `.btn.gold`, `.btn.ghost` | one hierarchy everywhere |
| Toggle switch | `.switch` (+`.on`) | Bloom default, drafts |
| Soft panel | `.panel-soft` | shortfall "tajweez — hukm nahi" |
| Table | `th`/`td` base | zebra hover, uppercase header |

> **Ek function ek jagah:** har page apna alag button CSS na likhe. Sab `theme.css` se.

---

## 4. Screen-by-screen delta (existing file → target)

Har screen ke liye: **pehle grep karo current file, phir sirf delta lagao.** Neeche har screen ka target behaviour + kis cheez ko chhedna nahi.

### 4.1 `blueprint.html`  (recommend: pehli screen)
- Section cards: har section header mein Bloom chip + marks + type chip.
- **Pin button per question** — mockup mein `.pin.on` = us section mein pinned.
  - Backend already: `BlueprintSection.include_question_ids`, `_apply_pinned`.
  - **Note (existing bug, is round mein NAHI):** `_pinned` reset gap — deferred. Chhedna mat.
- Right column: Paper summary (chips: sections / marks / pinned) + Bloom bars.
- Shortfall diagnostic panel = `.panel-soft`, read-only, `_diagnose_shortfall` ka output. Footer line: *"Tajweez — hukm nahi."*
- **Mat chhedo:** paper generation logic, draft-exclusion, `_apply_pinned` service.

### 4.2 `bank.html`
- Toolbar: search + SLO filter + Bloom filter + difficulty + "Show drafts" toggle.
- Draft rows dimmed + `Draft` chip. Draft kabhi paper mein na aaye (existing rule — verify only).
- Bulk checkbox → SLO-tag action (existing export-fill-upload workflow se link).

### 4.3 `taqseem.html`
- Dropdown-based (drag-drop NAHI — existing decision).
- Columns: Seq / SLO / Description / Page / Assigned-exam dropdown.
- Sequence page_number se derive (existing). Move range-validation preserve karo.

### 4.4 Coverage (`/api/coverage`, `/api/coverage-summary`)
- 3 summary tiles (green/yellow/red counts) + detail table with badges.
- Exam dropdown; cross-exam strict `WHERE p.exam_no = ?` (existing — mat badlo).
- "Show" button per SLO → `GET /api/slo/{slo_id}/questions` (Hissa 4-B, already hai).

### 4.5 Bloom Guidance (suggestion feature — active)
- Class-group tabs: Pre-Primary / Primary / Middle / Matric.
- Suggested distribution bars (existing numbers):
  - Pre-Primary: Remember 70 / Understand 30
  - Primary: 30 / 35 / 25 / 10
  - Middle: 20 / 30 / 30 / 20
  - Matric: 15 / 25 / 30 / 20 / 10
- **"Apply suggestion as default" toggle** — teacher marzi. Override sliders.
- **Strict enforcement OFF.** Sirf soft warning agar paper mix se door. (ahista ahista later.)

### 4.6 Print Settings (`class_print_settings`)
- Per-class: font size / question gap / margin — sliders + **live preview** `.sheet`.
- CSS variable approach valid (browser `Ctrl+P`, DOCX nahi).
- **Margin `.sheet` padding se** — `@page` CSS variable support nahi karta. (existing lesson.)

### 4.7 Dashboard (naya optional)
- Sirf tab banao agar Irfan chahe. Stat tiles + coverage-by-subject table + recent papers.
- Koi naya data source nahi — existing `/api/coverage-summary` + papers se.

---

## 5. Implementation order (recommended)

1. `static/theme.css` — tokens + components (ek dafa). `brand.json` se `--brand`/`--accent` pull.
2. Ek pilot page (jo Irfan chunega, e.g. `blueprint.html`) — theme.css include, markup ko component classes pe map.
3. Incognito test → screenshot Irfan ko.
4. Approve hone par baaki pages ek-ek (bank → coverage → taqseem → bloom → print).
5. Har page ke baad: `node --check` (agar JS), `pytest`, `ruff`, disk-verify grep/diff.
6. CLI **commit tak** ruke; **push Irfan GitHub Desktop se** karega.

---

## 6. Definition of done (per page)

- [ ] Sirf `theme.css` tokens use hue — koi hardcoded hex nahi.
- [ ] Fonts offline (koi CDN link nahi).
- [ ] Traffic-light: green≥100 / yellow 60-99 / red<60; Unassigned=null.
- [ ] Draft questions paper mein nahi (verify).
- [ ] Koi naya route/column NAHI (agar tha to alag Hissa).
- [ ] `pytest` + `ruff` pass.
- [ ] Incognito mein test + screenshot.
- [ ] Commit message + Summary box bhara. Push = GitHub Desktop (CLI nahi).

---

## 7. CLI ko exact prompt (copy-paste)

> Neeche wala message CLI ko do (style/page fill kar ke):

```
Read IMPLEMENTATION_HANDOFF.md fully before writing code.

Task: Section 5 order follow karo. Base style = <CLASSIC/MODERN/COMPACT>.
Pehli screen = <blueprint.html>.

Rules (non-negotiable):
- Pehle current file grep/dekho, phir delta lagao. Scratch rewrite mana.
- Sab colors/fonts theme.css tokens se; koi hardcoded hex nahi; fonts offline.
- Koi naya route/column NAHI is round mein. Sirf HTML/CSS/JS visual refactor.
- _apply_pinned, coverage query, draft-exclusion, taqseem validation ko mat chhedo.
- Har step disk-verify: grep/diff + node --check + pytest + ruff.
- Commit karo par PUSH mat karo (main GitHub Desktop se karunga).
- Kaam se pehle mujhe 3-line plan do, approve ke baad likho.
```
