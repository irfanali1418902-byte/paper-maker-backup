# Handoff — 2026-08-16 (`legacy_css_lines` 2,075 → 2,008 · six components live)

Naye session mein yeh poori file paste kar dein. Yeh file har session ke aakhir mein
**dobara likhi jaati hai** — purani cheezein jorhi nahi jaatin, hamesha sirf aakhri haalat.

---

PaperMaker — UI architecture sprint, session handoff

REPO: C:\PaperMaker\paper-maker-mvp   (sirf yeh path. E: drive ki purani copies mat chhuo)
BRANCH: feat/ui-architecture
Tree clean. **`backup` se 6 commits aage — push baqi hai.**

## KAAM KARNE KA TAREEQA — yeh sab se ahem hai

- Har qadam se pehle ruk kar mujh se ek-lafzi "go" lo. "Aage kya karna hai?" poochna ijazat
  nahi hai — qadam batao, phir ruko.
- Files kabhi PowerShell Set-Content/Out-File se mat likho, UTF-8 kharab hota hai. Edit ya
  Write tool use karo.
- Push main khud GitHub Desktop se karta hoon. Tum push mat karo.
- Koi cloud deploy nahi. `backup` remote sirf backup hai.
- **Measurement stylesheet ke comment mein mat likho.** `pages/bank.css` ka apna qaida:
  numbers board par rehte hain (PROGRESS.md), file mein sirf wo jis se agla banda ghalti
  karne se ruke. Teen review rounds isi par fail ho chuke hain — aur 16 Agast ko main ne
  yehi ghalti teen naye files mein ki aur `8ca7ed8` mein wapas li.

## HAALAT

9 ke 9 pages LIVE. Sprint 6 (drain) chal raha hai.

```
legacy_css_lines   2,115 (baseline) → 2,075 (14 Ag) → 2,008 (16 Ag)
unsanctioned_hex     429            →   385         →   382
```

**Chhe components ab live hain:** `nav.css` (`.sidenav`, 4 pages), aur 16 Agast ke paanch —
`status.css`, `field.css` (`.field-row` + `.filter-bar` + `.type-checks`), `modal.css` (chrome),
aur `btn.css` mein `.btn-primary`.

## 15–16 AGAST KA KAAM — aath commits

```
f957a0e  sidebar scroll — 5 pages ka khula defect band
9c99160  blueprint + taqseem: subtitle title ke neeche wapas
60fa37e  .status-bar component — 12 rules, do palettes ek, AA pass
5e3120a  .field-row + .filter-bar — 19 rules, 0 deltas
70e55da  .type-checks — 4 rules, 0 deltas
fa68cd7  modal chrome — 6 rules, 0 deltas
8ca7ed8  teen component files se measurements nikal kar board par
2a18b1a  .btn-primary — 9 rules, indigo par unify (dekhne wali tabdeeli)
```

## ⚠ SAB SE AHEM SABAQ — CHHE DAFA PAKRA GAYA

**Rule ka text do files mein harf-ba-harf ek hona yeh sabit nahi karta ke wo ek jaisa paint
karta hai.** Migrate shuda entry files kuch legacy token naamon ko naye tree ke roles par map
karte hain aur kuch ko legacy literal par chhor dete hain. Nateeja: ek hi rule page ke hisab se
alag rang deta hai. 15–16 Agast ko yeh **chhe** dafa nikla:

| | |
|---|---|
| `.status-bar` | bank/library purana muted, blueprint naya bright — **do live palettes** |
| `.type-checks` checkbox | bank `rgb(46,90,172)` 16px, blueprint `rgb(79,70,229)` 15px |
| `.btn-primary` | **do live primary blues** — ab indigo par unify |
| `--radius-btn` | bank **10px**, print **8px** |
| `--bg` | bank aur print ke do alag grey |
| `.btn-ghost` | **paanch pages, chaar shaklein** |

**Aur us ka doosra rukh, jo utna hi mehnga hai: `layer(legacy)` mein mara hua declaration
component mein jaate hi ZINDA ho jata hai** — kyunke layer order specificity se pehle tay hota
hai. `.filter-bar` ke do declarations aise hi zinda hue aur **75 deltas** de gaye, pakre gaye,
hataye gaye. Yeh bhi mare hue mile: `.type-checks label` ke teen, `.modal-header h3` ka 16px,
`.page-head h1` ka 22px, `.btn-primary:disabled` ka cursor.

**Qaida: rule uthane se pehle har page par naapo ke wo compute kya hota hai — aur uthane ke
baad dobara naapo.** `scripts/css_selector_probe.mjs` isi liye likha gaya.

## AGLA QADAM — teen raaste, dono baqi faisle maangte hain

**RAASTA A — `.btn-ghost`.** 5 pages (`bank`, `blueprint`, `library`, `slo`, `slo-health`),
**chaar alag shaklein** — background, border, radius, padding, font-size aur height, sab par
ikhtilaf. Yeh **chaar faisle** hain, refactor nahi.

**RAASTA B — shell.** `.app-sidebar`, `.app-nav` (sirf padding baqi), `.brand` ×3,
`.sidebar-foot` — **24 rules, chaar pages.** ROADMAP is ko "454 load-bearing" ka asal kaam
kehta hai.
  · `.app-sidebar` ka box `.o-shell` grid mein hai, magar in chaar par topbar hai hi nahi.
  · **`.brand` ko component dena mana hai** — nau ke nau pages par live hai (UI-047b).
  · `.sidebar-foot` ka koi component nahi.

**RAASTA C — baqi 58% ka faisla.** 16 Agast ke audit se: `99-legacy` ke **682 distinct
selectors mein se 581 sirf EK file mein hain**. Line ke hisab se **58% page-only hai — us ka
koi component ban hi nahi sakta**, wo sirf `pages/*.css` mein shift hoga. Yani baqi drain ka
zyada tar hissa **muntaqili hai, dedup nahi**. Kya usay zero tak le jana hai, ya "kaafi hai" par
rokna hai — **yeh Irfan ka faisla hai aur abhi nahi hua.**

## ⚠ KHULE DEFECTS AUR NA-NAAPI CHEEZEIN

- **Hover kabhi naapa nahi gaya.** `b70cf99` ne `.app-nav a:hover` delete ki thi; probe hover
  karta hi nahi. Kisi live page par ek nav link par mouse le jao — 10 second.
- **`.btn-primary` ka box-shadow purane blue ka hai** aur ab har page par fill se thora
  bemel hai (blueprint par migration se hi tha). Jaan-boojh kar chhora — apna faisla mangta hai.
- **`.page-head` → `.pagehead` NAHI ho sakta jaise likha tha.** Component `display:flex` hai
  aur mockup us ke andar ek wrapper `<div>` rakhta hai; chaaron `.page-head` pages ka markup
  wrapper ke baghair hai. Pehle markup badlo, warna chaar pages ka header toot jayega.
- **Sprint 5 chhua tak nahi** — 466 inline `style=""`, un mein 224 akele `index.html` par.
- **`library.html`:186 par inline style** control ka padding tay karta hai, koi rule nahi.

## ⚠ JO GATE ANDHE HAIN — 0 ko coverage mat samjho

`css_type_probe` in mein se kisi ko dekh hi nahi sakta:
- `.status-bar` ki `.ok`/`.err`/`.warn` — inline JS lagata hai (`el.className = 'status-bar ' + type`)
- `.modal-*` — sab `display:none` at rest, `.open` chahiye
- **`blueprint` ka `.type-checks`** — JS template string mein banta hai (`blueprint.html`:642),
  fresh load par mojood hi nahi. Ek probe run mein mila, agli mein nahi.
- `.app-sidebar` ka `overflow` — captured property hi nahi

In sab ke liye `css_selector_probe.mjs --add=` ya markup injection use karo.

## TOOLS

```
scripts/css_selector_probe.mjs "<sel>" "<props>" [--add=<sel>:<class>] page...
                                                  ek selector, har page par computed value
scripts/css_type_probe.mjs <label> <outdir>       regression gate — 8 PAGES
scripts/css_type_diff.mjs <before> <after>        deltas  (--names, --page)
scripts/css_page_rule_probe.mjs <url> [selector]  rule kis layer mein aaya + kitne match
scripts/css_drain_probe.mjs <page>                rule hataney se kya hilta hai
scripts/css_orphans.py <page> --rules --names     (ab zyada kaam ka nahi — theme.css delete ho chuki)
baqi: docs/ui/PROBES.md
```

Server: `.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000`

Gate chalane ka tareeqa jo is session mein har dafa kaam aaya:
`git stash push -u` → probe `before` → `git stash pop` → probe `after` → `css_type_diff`.

⚠ `css_type_diff.mjs` ko **file** chahiye, directory nahi: `<outdir>\<label>.json`.
⚠ JSON hamesha scratchpad mein (har run ~13 MB), repo mein nahi — kaam ke baad delete karo.
⚠ Probes headless Edge uthate hain — mehnga hai; jahan grep se jawab mile wahan grep karo.

## TEEN TRAPS JO LAG CHUKE HAIN

1. **Raw hex COMMENT ke andar bhi `unsanctioned_hex` mein ginta hai.** Yeh check is epic mein
   **baarah** dafa fail ho chuka hai — 16 Agast ko do dafa main ne kiya. `rgb()` mein likho.
2. `\b` wali grep hyphenated names par ghalat match deti hai (`app-sidebar`).
3. `css_orphans` ka "orphan" sirf itna matlab rakhta hai ke page ki APNI legacy file usay
   redeclare nahi karti — naya tree usay cover karta hai ya nahi, wo tumhein dekhna hai.

## DOOSRA KHULA KAAM

- **Dead-code audit** — API layer ho chuka (13 Agast, `export.docx`/`export.pdf` delete).
  ⬜ `/api/syllabus-topics` ka koi caller nahi, faisla nahi hua. ⬜ JS/CSS/services audit
  shuru bhi nahi hua.
- **Docs ka bojh.** `docs/ui/` **3,494 lines** hai. `NEXT-SESSION.md` akela **798 lines** hai
  aur uske apne banner mein likha hai ke wo purani aur gumraah-kun hai — usay **delete hona
  chahiye**, banner nahi lagna chahiye tha. Irfan ne 15 Agast ko yeh step manzoor kiya tha aur
  wo abhi baqi hai.
- **STALE:** `PLAN.md`:313 kehta hai `docs/ui/` 2,655 lines hai (asal 3,494)।
  `main.css`:117 kehta hai `theme.css` 6 pages par link hai — wo file **mojood hi nahi**.

## PEHLA KAAM

`docs/ui/ROADMAP.md` parho, phir upar "AGLA QADAM" ka A/B/C faisla Irfan se lo.
**Enumeration pehle, likhai baad mein — aur board ke daawe par bharosa mat karo, chahe wo kal
ka ho.** 16 Agast ko board ke teen daawe naapne par ghalat nikle: `.page-head` ka "sasta win",
`.type-checks` ka "kaunsa blue" wala faisla (jo mojood hi nahi tha), aur modal ke "18 agree
rules" (chhe nikle).
