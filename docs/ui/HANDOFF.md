# Handoff — 2026-08-20 (`legacy_css_lines` 1,874 · `unsanctioned_hex` 354 · gate is 9 pages now)

> # ⛔ YE FILE BASI HAI — 2026-08-31 ko naapa gaya. `docs/ui/STATUS.md` parho.
>
> Do daawe jo ab ghalat hain:
>
> 1. **"CSS EPIC ROKA HUA HAI" — nahi hai.** Wo 20 Agast ka faisla tha; epic **24–29
>    Agast ko dobara khula aur chala** (UI-063 se UI-072 tak, items 1–7 mukammal). Ye
>    banner nau din tak jhoota khara raha — wohi bimari jis ka hisaab `docs/ROADMAP.md`
>    §E rakhta hai.
> 2. **Har adad purana hai.** `legacy_css_lines` 1,874 nahi, **1729**; `unsanctioned_hex`
>    354 nahi, **308**; gate 9 pages nahi, **10** (D56 ne `plan` shamil kiya), aur ab teen
>    gates hain — `css_type_probe`, `css_state_probe`, `css_inject_probe`.
>
> **Jo is file mein aaj bhi durust hai wo "KAISE" wale hisse hain** — teen qaide, gates
> ka andhapan, do traps, tools ki list. Wohi `MEASURED.md` ka usool hai: *jo kehta hai
> kya DONE ya NEXT hai us par yaqeen na karo; jo kehta hai cheez KAISE kaam karti hai wo
> abhi bhi durust hai.*

Naye session mein yeh poori file paste kar dein. Yeh file har session ke aakhir mein
**dobara likhi jaati hai** — purani cheezein jorhi nahi jaatin, hamesha sirf aakhri haalat.

---

PaperMaker — UI architecture sprint, session handoff

REPO: C:\PaperMaker\paper-maker-mvp   (sirf yeh path. E: drive ki purani copies mat chhuo)
BRANCH: feat/ui-architecture
Tree clean. **`backup` ke barabar — kuch push baqi nahi.**

## KAAM KARNE KA TAREEQA

- Har qadam se pehle ruk kar mujh se ek-lafzi "go" lo. "Aage kya karna hai?" ijazat nahi hai.
- Files kabhi PowerShell Set-Content/Out-File se mat likho, UTF-8 kharab hota hai.
- Push main khud GitHub Desktop se karta hoon. Tum push mat karo.
- **Measurement stylesheet ke comment mein mat likho** — numbers PROGRESS.md par, file mein
  sirf wo jis se agla banda ghalti karne se ruke. Teen review rounds isi par fail ho chuke
  hain, aur **20 Agast ko chauthi dafa hua**: comments itne lambe likhe ke `legacy_css_lines`
  1,865 se 1,885 chala gaya. Chhoti kar ke 1,869 par laaya. Comment bhi lines ginti hai.

## 🛑 SAB SE AHEM — DRAIN ZERO TAK NAHI JATA

**Irfan ka faisla, 19 Agast, `ROADMAP.md` mein darj hai.** `UI-060..063` kehta hai "drain to
zero" — **wo mansookh hai.** `scripts/css_duplication_audit.py` se dobara nikala ja sakta hai
(neeche ke aankray 20 Agast ke hain):

```
99-legacy ka 66% (1,055 lines)  page-only hai — koi component mumkin hi nahi.
                                Usay drain karne ka matlab sirf 99-legacy/<page>.css se
                                pages/<page>.css mein shift. Dono pehle se ek-page-ek-file
                                hain. Na duplication ghatti hai, na CSS. SKIPPED.
             8% (121 lines)     agree  — component, koi faisla nahi
            27% (431 lines)     disagree — pehle faisla, phir component. YAHIN QEEMAT HAI.
```

~~**Target: `legacy_css_lines` ~1,200–1,400 aur ek mutabiq app. Sifar NAHI.**~~
**⚠ 2026-08-31 — Irfan ne range khatam kar ke ek adad tay kiya: `legacy_css_lines` ~1400.**
**⚠⚠ SUPERSEDED 2026-09-04 — us par nazar-e-sani hui aur naya target `~1500` hai**
(`DECISIONS-FOR-IRFAN.md` §7). `~1400` scope ke andar reh kar hasil hi nahi ho sakta tha;
wajah aur poora hisaab `STATUS.md` §4 mein.
`docs/ui/STATUS.md` §5 dekho. Range ka neecha sira (1,200) riyazi taur par pohanch se
bahar tha — scope mein sirf 308 lines hain. Baqi jumla qaim: **sifar NAHI**, aur agar
koi session 99-legacy ko khali karne baithe to wo mansookh kaam kar raha hai.

## HAALAT

9 ke 9 pages LIVE. `legacy_css_lines` **2,115 (baseline) → 1,874**, `unsanctioned_hex` 429 → **354**.

**Saat components live:** `nav.css`, `status.css`, `field.css`, `modal.css`, `btn.css`,
`card.css`, `urdu.css`.

**`.sidenav__panel` paanch pages par:** `bank`, `library`, `slo`, `slo-health`, `index`.
Baqi teen — `taqseem`, `print`, `landing` — nahi (aur `blueprint` apne `.o-shell` par hai).

**Safed-links wala bug ab WAQAI band hai.** 19 Agast ka log kehta tha "nau ke nau par band" —
wo ghalat tha, `print` par 20 Agast tak khula raha. Ab band hai, aur naapa hua hai.

**Hover pehli dafa naapa gaya (20 Agast).** Saat pages bilkul yaksan: rest `rgb(198,210,232)`,
hover `rgb(255,255,255)` on `rgba(255,255,255,.07)`. `print` ka hover background `.08` hai —
jaan boojh kar chhora, mehsoos nahi hota.

## ⚠ TEEN QAIDE JO IS EPIC NE MEHNGE DAAM SEEKHE

**1. Rule ka text ek jaisa hona qeemat ka ek jaisa hona NAHI hai.** Migrate shuda entry files
kuch legacy token naamon ko naye tree ke roles par map karte hain aur kuch ko legacy literal
par chhorte hain. 15–16 Agast ko yeh **chhe** dafa nikla: do status palettes, do checkbox rang,
**do primary blues**, `--radius-btn` 10px vs 8px, `--bg` ke do grey, checkbox 16 vs 15px.
`.btn-ghost` to **paanch pages par chaar shaklein** tha.

**2. `layer(legacy)` mein mara hua declaration component mein jaate hi ZINDA ho jata hai** —
layer order **specificity, aur MEDIA QUERY, dono se pehle** tay hota hai. `.filter-bar` ke do
declarations aise zinda hue aur **75 deltas** de gaye.
**20 Agast ko yeh do dafa aur laga, dono nayi shakl mein:**
- `index` ka `@media (max-width:760px) { .app-sidebar { display:none } }` layer(legacy) mein
  tha. `.sidenav__panel { display:flex }` layer(components) mein. Class lagate hi mobile par
  poora sidebar wapas aa jata — topbar aur bottom tab bar ke oopar. Media query
  `pages/index.css` mein le jaa kar bacha.
- `print` ka fix khud is qaide mein phansne wala tha: base rule layer(components) mein daali
  to wo legacy ki `:hover` ko haraane lagi. **Fix ke saath uska `:hover` bhi likhna para.**

**3. Uthane se PEHLE har page par naapo, aur uthane ke BAAD dobara naapo.**
`scripts/css_selector_probe.mjs` isi liye hai.

## ⚠ GATE ANDHE HAIN — 0 ko coverage mat samjho

`css_type_probe` **ab 9 pages** chalata hai (`print` 20 Agast ko shaamil hua). Phir bhi in mein
se kisi ko nahi dekhta:

| cheez | kaise naapo |
|---|---|
| **KOI BHI VIEWPORT 1280×900 ke ilawa** — dono probes hardcoded hain | scratchpad ka `viewport_probe.mjs` (`Emulation.setDeviceMetricsOverride`) |
| **`:hover`, aur har pseudo-state** | scratchpad ka `hover_probe.mjs` (`CSS.forcePseudoState`) |
| `.status-bar` ki `.ok`/`.err`/`.warn` (inline JS lagata hai) | `--add=".status-bar:ok"` |
| `.modal-*` (sab `display:none` at rest) | `--add=".modal-backdrop:open"` |
| **`[dir="rtl"]` ka poora block** — nav rail, table alignment, legend dot | `--attr="html:dir=rtl"` |
| `blueprint` ka `.type-checks` (JS template string, `blueprint.html`:642) | markup inject karo |
| `.app-sidebar` ka `overflow` | captured property hi nahi |
| **`print` ka paper body** — gate mein sirf shell hai, `?paper_id=` ke baghair | `css_print_probe`, ya `--query=` ke saath alag run |
| `taqseem` ka board bina class+subject | `--warm=` se `Pre Year 1` / `Mathematics` chuno |

⚠ **GATE "element daala gaya" aur "element ka style badla" mein FARQ NAHI KAR SAKTA.** Wo
element ko DOM path se pehchanta hai (`DIV[3]`, `DIV[4]`…). Panel ke beech mein ek row daalne
par 20 Agast ko `print` par **22 deltas** aaye aur ek bhi asli nahi tha — sab neeche khisak gaye
the. Jab bhi markup mein kuch INSERT karo, deltas ko selector se dobara naapo
(`css_selector_probe.mjs`), path se nahi.

**19 Agast ko RTL ne kaat liya, 20 Agast ko viewport aur hover ne.** Teeno dafa suite khamosh
rahi. Jo bhi `@media`, `:hover`, `[dir="rtl"]`, `.lang-ur`, ya nav ke border ko chhuye — us ka
apna probe chalao, gate ka 0 kaafi nahi.

⚠ **Do throwaway probes scratchpad mein hain, repo mein NAHI.** `viewport_probe.mjs` aur
`hover_probe.mjs`. Dono `css_selector_probe.mjs` ke CDP dhaanche par bane hain. Agar aage kaam
paren to unhein `css_selector_probe.mjs` mein `--width=` aur `--pseudo=` flags ki soorat mein
shaamil karna behtar hoga — abhi tak nahi kiya.
⚠ `viewport_probe.mjs` mein ek race hai: `DevToolsActivePort` foran parhta hai aur kabhi-kabhi
`EBUSY` deta hai. Dobara chala do, ya retry daal do.

## AGLA QADAM — do saaf raaste

**RAASTA A — sasta `agree` (121 lines, koi faisla nahi).**
`field/filter` 43 (5 pages) · `modal` 26 (2) · `shell/nav` 23 (7) · `shortfall` 12 (2) ·
`page-head` 8 (4) · baqi 9.
**⚠ `.page-head` ko `.pagehead` par re-class MAT karo** jab tak markup na badle: component
`display:flex` hai aur mockup us ke andar ek wrapper `<div>` rakhta hai; chaaron `.page-head`
pages ka markup wrapper ke baghair hai. Bina us ke chaar headers toot jayenge.

**RAASTA B — `disagree` ka baqi (431 lines, har ek faisla).**
`other` 138 (zyada tar `:root`/`body`) · `shell/nav` 76 · `field/filter` 68 · `modal` 58 ·
`card` 28 · `brand` 24 · `btn-*` 22 · `chip/pill/row` 9 · `shortfall` 8.
Sab se saaf tukra: **`taqseem` ka panel/brand/foot** — `index` ki tarah, magar `taqseem` mein
paanch chhoti qeematein alag hain (panel padding 16 vs 18, brand padding, name line-height
1.1 vs 1.15, foot padding aur rang). Har ek par faisla chahiye, sab chhote.
`print` aur `landing` us ke baad — `print` ka brand aur foot dono alag shakl ke hain.

## ⚠ KHULE KAAM

- **`.btn-primary` ka box-shadow purane blue ka hai** aur ab fill se bemel hai. Apna faisla mangta hai.
- **`print` ke nav links par 3px ka rail nahi hai** — wo `.sidenav__link` par nahi hain
  (`slo` `border-left-width: 3px`, `print` 0px). Poora sidebar badalna parega, aur `print`
  wahi safha hai jahan teacher ka asal kaam hai. 20 Agast ko jaan boojh kar chhora.
- **Sprint 5 chhua tak nahi** — 466 inline `style=""`, 224 akele `index.html` par.
- **Drain ki mari hui rules KHATAM ho chuki hain** — 845 ka survey, ~47 waqai dead, sab ja
  chuki. Ab jo bhi `99-legacy` mein hai wo zinda hai, ya kisi state mein zinda hai.
- **STALE:** `main.css`:117 kehta hai `theme.css` 6 pages par link hai — wo file mojood hi
  nahi. (`PLAN.md`:317 ka lines wala daawa 20 Agast ko theek kar diya: `docs/ui/` **3,004**
  lines, naya CSS **3,495**.)

## TOOLS

```
scripts/css_selector_probe.mjs "<sel>" "<props>" [--add=<sel>:<class>]
                                                 [--attr=<sel>:<name>=<value>] page...
scripts/css_duplication_audit.py                  page-only / agree / disagree ka split
scripts/css_drain_probe.mjs <page> [--query=] [--warm="<js>"] [--wait=ms]
scripts/css_type_probe.mjs <label> <outdir>       regression gate — AB 9 PAGES
scripts/css_type_diff.mjs <before> <after>        deltas  (--names, --page)
scripts/css_page_rule_probe.mjs <url> [selector]  rule kis layer mein aaya + kitne match
scripts/css_baseline.py                           ratchet — unsanctioned_hex
baqi: docs/ui/PROBES.md
```

Server: `.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000`

Gate chalane ka tareeqa jo har dafa kaam aaya:
`git stash push -u` → probe `before` → `git stash pop` → probe `after` → `css_type_diff`.
⚠ Agar probe script khud badla ho to sirf CSS stash karo (`git stash push <file>`), warna
`before` aur `after` alag page list par chalenge.

⚠ `css_type_diff.mjs` ko **file** chahiye: `<outdir>\<label>.json`.
⚠ JSON hamesha scratchpad mein (~13 MB per run), repo mein nahi — kaam ke baad delete karo.

## DO TRAPS JO ABHI BHI LAGTE HAIN

1. **Raw hex COMMENT ke andar bhi `unsanctioned_hex` mein ginta hai** — **baarah** dafa fail ho
   chuka. `rgb()` mein likho.
2. `\b` wali grep hyphenated names par ghalat match deti hai. 16 Agast ko `sh` ke 68 "hits"
   aaye, sab `should` jaise lafzon ke andar. Token match karo: `(?<![\w-])x(?![\w-])`.

## 🛑 CSS EPIC ROKA HUA HAI — Irfan ka faisla, 20 Agast

**Yeh file CSS epic ki hai, aur wo abhi agla kaam NAHI hai.** 20 Agast ko, `index` aur `print`
ke baad, Irfan ne CSS rok kar features par jane ka faisla kiya. Usi din pehla feature bhi
ship hua — print ka "sawal ka range" (`97a3450`).

**Wajah:** target `legacy_css_lines` ~1,200–1,400 hai, abhi 1,874 — yani 5–8 session aur, aur
un mein teacher ko koi naya kaam ka feature nahi milta. Jo ho chuka wo apni jagah mukammal hai,
adhoora nahi chhoota.

**Product roadmap `docs/ROADMAP.md` mein hai. Agli cheez: school PC / Docker.**
(Us file mein "page range" ka zikr nahi tha — wo Irfan ki apni tarteeb se aaya, aur uska matlab
"safha" nahi "sawal" nikla. Feature ka naam poochh kar tay hua tha, farz kar ke nahi.)

**Neeche "AGLA QADAM" ka A/B tab ke liye hai jab CSS dobara khule.** Us waqt bhi: faisla Irfan
se lo, tajweez de kar aage mat barho.

## PEHLA KAAM

Agar CSS dobara khule: `docs/ui/ROADMAP.md` ka §"THE DRAIN DOES NOT GO TO ZERO" parho, phir
upar "AGLA QADAM" ka A/B faisla Irfan se lo.

**Enumeration pehle, likhai baad mein — aur board ke daawe par bharosa mat karo, chahe wo kal
ka ho.** Is epic mein board ke chhe daawe naapne par ghalat nikle: `.page-head` ka "sasta win",
`.type-checks` ka "kaunsa blue" wala faisla (jo mojood hi nahi tha), modal ke "18 agree rules"
(chhe nikle), drain ke "391 dead rules" (~47 nikle), **`index` ka "0 deltas, seedha adopt"**
(mobile toot raha tha), aur **"safed-links bug nau ke nau par band"** (`print` par khula tha).

Jo `docs/ui/MEASURED.md` mein hai wo alag hai — wo naapi hui cheezein hain, board ke daawe
nahi. Us file ka apna qaida: **jo kehta hai kya DONE ya NEXT hai, us par yaqeen na karo; jo
kehta hai cheez KAISE kaam karti hai, wo abhi bhi durust hai.**
