# Handoff — 2026-08-14 (four pages on `.sidenav` · `legacy_css_lines` 2,105 → 2,075)

Naye session mein yeh poori file paste kar dein. Yeh file har session ke aakhir mein
**dobara likhi jaati hai** — purani cheezein jorhi nahi jaatin, hamesha sirf aakhri haalat.

---

PaperMaker — UI architecture sprint, session handoff

REPO: C:\PaperMaker\paper-maker-mvp   (sirf yeh path. E: drive ki purani copies mat chhuo)
BRANCH: feat/ui-architecture
Tree clean, dev server band, port 8000 free. **Push abhi baqi hai — 4 commits `backup` se aage.**

## KAAM KARNE KA TAREEQA — yeh sab se ahem hai

- Har qadam se pehle ruk kar mujh se ek-lafzi "go" lo. "Aage kya karna hai?" poochna ijazat
  nahi hai — qadam batao, phir ruko.
- Files kabhi PowerShell Set-Content/Out-File se mat likho, UTF-8 kharab hota hai. Edit ya
  Write tool use karo.
- Push main khud GitHub Desktop se karta hoon. Tum push mat karo — sirf
  `git ls-remote backup feat/ui-architecture` se confirm karo jab main kahoon.
- Koi cloud deploy nahi. `backup` remote sirf backup hai.

## HAALAT

9 ke 9 pages LIVE. Sprint 0-4b mukammal. `static/theme.css` aur DOCX/PDF export DELETE ho chuke.

**Sprint 6 chal raha hai, aur ab is ka nateeja number par nazar aata hai:**

```
legacy_css_lines   2,115 (baseline)  →  2,105 (13 Aug)  →  2,075 (14 Aug)
unsanctioned_hex     429             →                     385
shared_css_lines   2,526             →                   3,064
```

**Chaar pages ab `.sidenav` component par hain** — `bank`, `library`, `slo-health`, `slo` —
aur unki 12 legacy rules nikal chuki hain. `blueprint` pehle se us par tha. Baqi chaar
(`taqseem`, `index`, `print`, `landing`) nahi.

## 14 AGAST KA KAAM — chaar commits, tarteeb ahem hai

  ✅ `778f65a` — `nav.css` ko chaar pages ki values par laya gaya.
     Component `--text-body` (15px), `--radius-control` (11px), 11px gap par tha;
     chaar legacy files 14px / 8px / 10px kehti hain. Component ko UN par laya gaya,
     ulta nahi — taake chaar live pages na hilein. Qeemat: `blueprint` par 104 deltas
     (type, corners, active ka weight 600→500, rail box-shadow se border par).
     Irfan ne browser mein dekh kar manzoor kiya.
     ⚠ 14px aur 8px LITERAL hain, token nahi — `--text-body` 15px hai, `--radius-control`
       11px, aur `--font-size-4` par `--text-heading-3` ka qabza hai. Teen naye naam
       banane ka matlab teen aise roles jinka ek-ek consumer ho: `tokens.css`:145 khud
       kehti hai ke file isi tarah sarhti hai. `nav.css` ke 34px avatar ka wohi usool.

  ✅ `8cbc38f` — `bank` re-classed. **0 deltas ki tawaqqo thi, 57 aaye.**
  ✅ `b75346a` — `library` 57, `slo-health` 85, `slo` 85.
  ✅ `b70cf99` — 12 rules delete: `.app-nav a`, `:hover`, `.active` × 4 files.
     **30 lines, 0 deltas har page par.**

## ⚠ EK PURANA BUG JO NIKLA — AUR WO ABHI DO PAGES PAR ZINDA HAI

`03-elements/typography.css`:50 par `a { color: inherit }` hai, `layer(elements)` mein.
Layer order specificity se PEHLE tay hota hai, is liye wo `layer(legacy)` ke
`.app-nav a { color: #C6D2E8 }` ko harata hai — selector ka wazan chahe kuch bhi ho. Link
`.app-sidebar { color: #fff }` se **safed** inherit kar leta hai.

Nateeja: **jo bhi page migrate hua, uske nav links safed ho gaye** — current aur baqi, dono.
Farq sirf background tint aur rail se rehta hai.

Yeh `pages/bank.css`:124 par ek line mein likha hua tha — *"Nav links go white and the canvas
changes tint"* — 10 Agast se, "expected consequence" ke tor par. **Kisi ne faisla nahi kiya tha.**
Irfan ne 14 Agast ko kiya: legacy rang qubool. `.sidenav__link` `layer(components)` mein hai,
elements se upar, is liye re-class karne se rang wapas aa gaya.

**`taqseem` aur `index` par ab bhi safed hai.** App mein do shaklein hain — aarzi, jaan-boojh kar,
bilkul waise jaise navy ka masla settle hone se pehle tha.

## AGLA QADAM — do saaf raaste, dono jayaz

**RAASTA A — `taqseem` aur `index` ko bhi `.sidenav` par lao.**
Faida: safed-links wali do-shakli khatam. Magar yeh chaar wale gutt jitna saaf NAHI hai:

  · `taqseem` ka `.app-nav a` **alag hai** — `border-radius: var(--radius-sm)` (8px nahi),
    aur uska `.active` `background: rgba(255,255,255,.10)` + `font-weight: 600` hai
    (chaaron ka `.09` aur koi weight nahi). Yani **do asal faisle**: radius kis ka, aur
    active bold ho ya nahi.
  · `index` ka aur bhi alag hai — `.app-nav a[data-active="1"]` (class nahi, attribute;
    `nav.css` mein us ke liye selector PEHLE SE mojood hai), plus `index.css`:63 ka
    `.app-nav a svg { width: 19px }` aur `.brand .tag`.
    ⚠ Wo 19px wala rule **shayad pehle se mara hua hai**: `static/app.css`:57 bare `.icon`
      ko 17px par set karta hai aur wo **unlayered** hai, yani har `@layer` ko harata hai
      (`main.css`:73-74). Yeh PARHA gaya hai, NAAPA nahi — `index` ko chhoone se pehle
      `css_page_rule_probe.mjs` se tasdeeq karo.
    `index` sab se bara page hai (783 elements, 224 inline styles).

**RAASTA B — chaar pages ke baqi 6 shell rules ka ghar banao.**
Har page par abhi bhi: `.app-sidebar`, `.app-nav` (sirf padding baqi), `.brand`, `.brand .name`,
`.brand small`, `.sidebar-foot` — **24 rules, chaar pages par**. Inme se **kisi ka koi component
nahi hai**, aur yeh ROADMAP ka "454 load-bearing" wala asal kaam hai.
  · `.app-sidebar` ka box `.o-shell` grid mein hai — magar in chaar par topbar hai hi nahi,
    to poora grid apnana bara kaam hai (aur wohi `overflow` defect bhi theek kar dega, neeche).
  · `.brand` ko component dena **mana hai** — wo nau ke nau pages par live hai (`UI-047b` ne
    yehi tay kiya tha aur usay page-scope kiya tha).
  · `.sidebar-foot` ka koi component nahi, aur `blueprint` par yeh element hai hi nahi.

Mera mashwara: **B se pehle A**, kyunke A do-shakli khatam karta hai aur uske faisle chhote hain.
Magar yeh Irfan ka faisla hai.

## ⚠ EK KHULA DEFECT — PAANCH LIVE PAGES PAR (aaj kuch nahi hua)

`.app-sidebar` par `height: 100vh` hai aur `overflow` KOI NAHI. Content viewport se lamba ho
to scroll nahi hota — painted box se BAHAR chhalak jata hai. Irfan ne 13 Agast ko browser
mein pakra: `index` ka aakhri nav item navy background se bahar tha; wahan page-scoped
`overflow-y: auto` se theek kiya. **`library`, `bank`, `slo`, `slo-health`, `taqseem` par
wohi hole khula hai** — unki nav 209-294px hai, `index` ki 450px thi, is liye abhi nahi phata.

KOI PROBE ISAY NAHI DEKH SAKTA — probe ka viewport 900px hai aur `overflow` captured property
hi nahi. Fix 0 deltas dega; iska matlab "kuch bigra nahi", yeh nahi ke "kaam karta hai".

Note: `04-objects/shell.css` ka `.o-shell__nav` mein `overflow: auto` **pehle se hai**. Jo bhi
qadam in pages ko us grid par laye ga, wo yeh defect saath hi band kar de ga.

## ⚠ EK CHEEZ JO NAAPI NAHI GAYI — HOVER

`b70cf99` ne `.app-nav a:hover` delete ki. **Probe hover karta hi nahi**, is liye uska 0 kuch
sabit nahi karta. Jo kiya gaya wo value-ba-value padhai hai:
`--color-sidebar-hover` → `--overlay-white-07` → `rgba(255,255,255,0.07)` aur
`--color-sidebar-fg-on` → `--white` → `#ffffff` — bilkul wahi jo purani rule likhti thi.
`.active` wala hissa NAAPA GAYA hai (wo halat-e-sukoon mein hai).
**Agle session mein kisi live page par ek nav link par mouse le jao aur dekh lo.** 10 second.

## PEHLA QADAM HAMESHA ENUMERATION HOTA HAI, LIKHAI NAHI

Is usool ne aaj phir kaam kiya, aur is baar usne KHUD BOARD ko pakra.

**HANDOFF (13 Agast) kehta tha: "chaar pages ka re-class = 36 rules bahar, rang bilkul nahi
badlega." Dono aadhe ghalat thay:**

- 36 sahi tha — nau shell rules waqai chaaron files mein harf-ba-harf ek jaise hain.
  **Magar `.sidenav` un nau mein se sirf TEEN ka ghar hai.** Baqi chhe ka koi component nahi.
  Asal nateeja: **12 rules**, 36 nahi.
- "rang nahi badlega" bhi ghalat tha — magar ULTI taraf se. Rang badla, aur behtar hui:
  safed se `#C6D2E8`, kyunke ek purana bug theek ho gaya (upar dekho).

Tareeqa jisne yeh pakra: `.sidenav*` ki har declaration ko chaar legacy files ki har
declaration ke saamne rakh kar padhna — token resolve kar ke, `--text-body` = 15px tak.
Ek bhi probe run se pehle. **Board ke daawe par bharosa mat karo, chahe wo kal ka ho.**

Aur ek qaida jo mehnga sabit hua: **probe batata hai ke kya kho raha hai — yeh nahi ke kya
rakhna chahiye.**

## TOOLS

  scripts/css_orphans.py <page> --rules --names     page kya khota hai + har rule ka ghar
  scripts/css_page_rule_probe.mjs <url> [selector]  rule kis layer mein aaya + kitne match
  scripts/css_type_probe.mjs <label> <outdir>       regression gate — 8 PAGES
  scripts/css_type_diff.mjs <before> <after>        deltas  (`--names`, `--page` bhi hai)
  scripts/css_drain_probe.mjs <page>                rule hataney se kya hilta hai
  baqi probes: docs/ui/PROBES.md

Server: start-local.bat (uvicorn, port 8000). Agar wo na chale to seedha:
`.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000`

⚠ `css_type_diff.mjs` ko **file** chahiye, directory nahi: `<outdir>\<label>.json`.
⚠ Uski `--names` list **60 par cap** hai. Poori ginti chahiye to JSON khud parh lo.
⚠ Probes headless Edge uthate hain — mehnga hai; jahan static HTML se jawab mil sakta ho wahan
grep behtar hai. JSON hamesha scratchpad mein (har run ~15 MB), repo mein nahi — kaam ke baad
delete kar dena. C: drive ek baar poori bhar chuki hai.

⚠ JO PAGE MIGRATE HO RAHA HO, USAY css_type_probe KI LIST MEIN PEHLE DAALO. `taqseem` par yeh
der se hua aur usne ek JHOOTA ALL-CLEAR paida kiya. JIS PAGE KO PROBE DEKH NAHI RAHA, USKA 0
SABOOT NAHI. (Aaj chaaron pehle se list mein thay.)

## TEEN TRAPS JO LAG CHUKE HAIN

1. `\b` wali grep hyphenated names par galat match deti hai (`app-sidebar`, `urdu-toggle-row`).
   Class token check karna ho to poora attribute match karo:
   `class="([^"]* )?(app|top|nav)( [^"]*)?"`
2. `css_orphans` ka "orphan" sirf itna matlab rakhta hai ke page ki APNI legacy file usay
   redeclare nahi karti. Naya tree usay cover karta hai ya nahi — wo tumhein khud dekhna hai.
3. Raw hex COMMENT ke andar bhi `unsanctioned_hex` mein ginta hai. Yeh check is epic mein
   DAS baar fail ho chuka hai, har baar comment ke zariye.

## DOOSRA KHULA KAAM — dead-code audit, adhoora

API layer ho chuka (13 Agast): 80 routes, 74 zinda. `export.docx` + `export.pdf` DELETE.
⬜ `/api/syllabus-topics` ka koi caller nahi — faisla nahi hua.
⬜ `blueprint-presets/{id}` aur `library/question-types` sirf tests se bulaye jaate hain.
⬜ JS / CSS / services wala audit shuru bhi nahi hua.

⚠ FastAPI routes ginte waqt: is version mein `app.routes` included routers ko
`_IncludedRouter` objects mein rakhta hai jinpar `.path` hai hi nahi. `_IncludedRouter` ginlo
(abhi 14) ya `app.openapi()["paths"]` parho.

## STALE NUMBERS — batae gaye, theek nahi kiye

- `PLAN.md`:313 kehta hai `docs/ui/` 2,655 lines hai. Asal ~4,000+.
- `main.css`:117 kehta hai `theme.css` 6 pages par plain `<link>` hai. Wo file **mojood hi nahi**.
- `docs/ui/NEXT-SESSION.md` **poori purani hai** — 12 Agast ki, "7 of 9 live" aur "UI-046 is the
  next task" kehti hai. Uske upar ab ek warning banner laga diya gaya hai. Usme sirf
  mechanism/traps wale hisse qaabil-e-etemaad hain, haalat wale nahi.

## PEHLA KAAM

`docs/ui/ROADMAP.md` parho (order + estimates + khule items), phir upar "AGLA QADAM" ka
A/B faisla mujh se lo. Enumeration pehle, likhai baad mein.
