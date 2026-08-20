# Handoff — 2026-08-20 (`legacy_css_lines` 2,075 → 1,865 · the drain's scope is now decided)

Naye session mein yeh poori file paste kar dein. Yeh file har session ke aakhir mein
**dobara likhi jaati hai** — purani cheezein jorhi nahi jaatin, hamesha sirf aakhri haalat.

---

PaperMaker — UI architecture sprint, session handoff

REPO: C:\PaperMaker\paper-maker-mvp   (sirf yeh path. E: drive ki purani copies mat chhuo)
BRANCH: feat/ui-architecture
Tree clean. **`backup` se 9 commits aage — push baqi hai.**

## KAAM KARNE KA TAREEQA

- Har qadam se pehle ruk kar mujh se ek-lafzi "go" lo. "Aage kya karna hai?" ijazat nahi hai.
- Files kabhi PowerShell Set-Content/Out-File se mat likho, UTF-8 kharab hota hai.
- Push main khud GitHub Desktop se karta hoon. Tum push mat karo.
- **Measurement stylesheet ke comment mein mat likho** — numbers PROGRESS.md par, file mein
  sirf wo jis se agla banda ghalti karne se ruke. Teen review rounds isi par fail ho chuke hain.

## 🛑 SAB SE AHEM — DRAIN ZERO TAK NAHI JATA

**Irfan ka faisla, 19 Agast, `ROADMAP.md` mein darj hai.** `UI-060..063` kehta hai "drain to
zero" — **wo mansookh hai.** `scripts/css_duplication_audit.py` se dobara nikala ja sakta hai:

```
99-legacy ka ~65%  page-only hai — koi component mumkin hi nahi.
                   Usay drain karne ka matlab sirf 99-legacy/<page>.css se
                   pages/<page>.css mein shift. Dono pehle se ek-page-ek-file
                   hain. Na duplication ghatti hai, na CSS. SKIPPED.
        ~7%        agree  — component, koi faisla nahi
        ~27%       disagree — pehle faisla, phir component. YAHIN QEEMAT HAI.
```

**Target: `legacy_css_lines` ~1,200–1,400 aur ek mutabiq app. Sifar NAHI.**
Agar koi session 99-legacy ko khali karne baithe to wo mansookh kaam kar raha hai.

## HAALAT

9 ke 9 pages LIVE. `legacy_css_lines` **2,115 (baseline) → 1,865**, `unsanctioned_hex` 429 → **357**.

**Aath components live:** `nav.css` (`.sidenav`, `.sidenav__panel/__brand/__brand-name/
__brand-sub/__foot`), `status.css`, `field.css` (`.field-row` + `.filter-bar` + `.type-checks`),
`modal.css` (chrome), aur `btn.css` mein `.btn-primary` + `.btn-ghost`.

**Nau ke nau pages ka sidebar ab ek shakl par hai.** Safed-links wala bug — jo 14 Agast ko
mila tha — **band ho chuka hai**, aakhri do pages (`taqseem`, `index`) 19 Agast ko.

## ⚠ TEEN QAIDE JO IS EPIC NE MEHNGE DAAM SEEKHE

**1. Rule ka text ek jaisa hona qeemat ka ek jaisa hona NAHI hai.** Migrate shuda entry files
kuch legacy token naamon ko naye tree ke roles par map karte hain aur kuch ko legacy literal
par chhorte hain. 15–16 Agast ko yeh **chhe** dafa nikla: do status palettes, do checkbox rang,
**do primary blues**, `--radius-btn` 10px vs 8px, `--bg` ke do grey, checkbox 16 vs 15px.
`.btn-ghost` to **paanch pages par chaar shaklein** tha.

**2. `layer(legacy)` mein mara hua declaration component mein jaate hi ZINDA ho jata hai** —
layer order specificity se pehle tay hota hai. `.filter-bar` ke do declarations aise zinda hue
aur **75 deltas** de gaye. Mare hue mile: `.type-checks label` ke teen, `.modal-header h3` ka
16px, `.page-head h1` ka 22px, `.brand small` ke do, `.btn-primary:disabled` ka cursor.

**3. Uthane se PEHLE har page par naapo, aur uthane ke BAAD dobara naapo.**
`scripts/css_selector_probe.mjs` isi liye hai.

## ⚠ GATE ANDHE HAIN — 0 ko coverage mat samjho

`css_type_probe` in mein se kisi ko nahi dekhta:

| cheez | kaise naapo |
|---|---|
| `.status-bar` ki `.ok`/`.err`/`.warn` (inline JS lagata hai) | `--add=".status-bar:ok"` |
| `.modal-*` (sab `display:none` at rest) | `--add=".modal-backdrop:open"` |
| **`[dir="rtl"]` ka poora block** — nav rail, table alignment, legend dot | `--attr="html:dir=rtl"` |
| `blueprint` ka `.type-checks` (JS template string, `blueprint.html`:642) | markup inject karo |
| `.app-sidebar` ka `overflow` | captured property hi nahi |
| `print` ka kuch bhi bina `?paper_id=` | `--query="?paper_id=9ade2655-21e6-449d-943a-ae875542012e"` |
| `taqseem` ka board bina class+subject | `--warm=` se `Pre Year 1` / `Mathematics` chuno |

**19 Agast ko RTL ne kaat liya:** `.sidenav__link` apnane se `index` ki Urdu rail toot gayi
(dono taraf 3px), aur **suite mein kuch bhi us par khamosh raha**. Fix `pages/index.css` mein
hai. Jo bhi `[dir="rtl"]`, `.lang-ur`, ya nav ke border ko chhuye — `--attr` se dono simtein
naapo.

## AGLA QADAM — do saaf raaste

**RAASTA A — sasta `agree` (~121 lines, koi faisla nahi).**
`field/filter` 43 · `modal` 26 · `shell/nav` 23 · `shortfall-panel` 12 · `page-head` 8 ·
baqi 8. **⚠ `.page-head` ko `.pagehead` par re-class MAT karo** jab tak markup na badle:
component `display:flex` hai aur mockup us ke andar ek wrapper `<div>` rakhta hai; chaaron
`.page-head` pages ka markup wrapper ke baghair hai. Bina us ke chaar headers toot jayenge.

**RAASTA B — `disagree` ka baqi (~439 lines, har ek faisla).**
`other` 138 (zyada tar `:root`/`body`) · `shell/nav` 83 · `field/filter` 68 · `modal` 58 ·
`card` 28 · `brand` 25 · `btn-*` 22.
Sab se saaf tukra: **`taqseem`, `index`, `print`, `landing` ka panel/brand/foot** — chaar pages
jo abhi `.sidenav__panel` par nahi hain, har ek ki apni qeematein (naapi hui, PROGRESS.md
19 Agast).

## ⚠ KHULE KAAM

- **Hover kabhi naapa nahi gaya** (`b70cf99` ne `.app-nav a:hover` delete ki thi). Kisi live
  page par ek nav link par mouse le jao — 10 second.
- **`.btn-primary` ka box-shadow purane blue ka hai** aur ab fill se bemel hai. Apna faisla mangta hai.
- **Sprint 5 chhua tak nahi** — 466 inline `style=""`, 224 akele `index.html` par.
- **Drain ki mari hui rules KHATAM ho chuki hain** — 845 ka survey, ~47 waqai dead, sab ja
  chuki. Ab jo bhi `99-legacy` mein hai wo zinda hai, ya kisi state mein zinda hai.
- ~~`docs/ui/NEXT-SESSION.md` delete~~ — **HO GAYA 20 Agast.** Seedha delete nahi ho sakta tha:
  **gyarah jagah us ka hawala saboot ke taur par tha** (`PLAN.md` ×3, `STATUS.md` ×3,
  `DEFERRED.md` ×2, `ROADMAP.md`, `PROGRESS.md`, aur `scripts/css_margin_probe.mjs` ×2). Jo
  zinda tha — §📐, print ke F1/F2/F3, margin harness, test-data UUIDs, `pre-commit` warning —
  wo `docs/ui/MEASURED.md` mein hai, aur gyaraho hawale us par mor diye gaye.
- **STALE:** `PLAN.md`:313 kehta hai `docs/ui/` 2,655 lines hai. `main.css`:117 kehta hai
  `theme.css` 6 pages par link hai — wo file mojood hi nahi.

## TOOLS

```
scripts/css_selector_probe.mjs "<sel>" "<props>" [--add=<sel>:<class>]
                                                 [--attr=<sel>:<name>=<value>] page...
scripts/css_duplication_audit.py                  page-only / agree / disagree ka split
scripts/css_drain_probe.mjs <page> [--query=] [--warm="<js>"] [--wait=ms]
scripts/css_type_probe.mjs <label> <outdir>       regression gate — 8 PAGES
scripts/css_type_diff.mjs <before> <after>        deltas  (--names, --page)
scripts/css_page_rule_probe.mjs <url> [selector]  rule kis layer mein aaya + kitne match
baqi: docs/ui/PROBES.md
```

Server: `.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000`

Gate chalane ka tareeqa jo har dafa kaam aaya:
`git stash push -u` → probe `before` → `git stash pop` → probe `after` → `css_type_diff`.

⚠ `css_type_diff.mjs` ko **file** chahiye: `<outdir>\<label>.json`.
⚠ JSON hamesha scratchpad mein (~13 MB per run), repo mein nahi — kaam ke baad delete karo.

## DO TRAPS JO ABHI BHI LAGTE HAIN

1. **Raw hex COMMENT ke andar bhi `unsanctioned_hex` mein ginta hai** — **baarah** dafa fail ho
   chuka, 16 Agast ko do dafa main ne kiya. `rgb()` mein likho.
2. `\b` wali grep hyphenated names par ghalat match deti hai. 16 Agast ko `sh` ke 68 "hits"
   aaye, sab `should` jaise lafzon ke andar. Token match karo: `(?<![\w-])x(?![\w-])`.

## PEHLA KAAM

`docs/ui/ROADMAP.md` ka §"THE DRAIN DOES NOT GO TO ZERO" parho, phir upar "AGLA QADAM" ka
A/B faisla Irfan se lo. **Enumeration pehle, likhai baad mein — aur board ke daawe par bharosa
mat karo, chahe wo kal ka ho.** Is hafte board ke chaar daawe naapne par ghalat nikle:
`.page-head` ka "sasta win", `.type-checks` ka "kaunsa blue" wala faisla (jo mojood hi nahi
tha), modal ke "18 agree rules" (chhe nikle), aur drain ke "391 dead rules" (~47 nikle).
