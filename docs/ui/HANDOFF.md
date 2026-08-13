# Handoff — 2026-08-13 (session end: 9 OF 9 LIVE · theme.css DELETED · export DELETED)

Naye session mein yeh poori file paste kar dein. Yeh file har session ke aakhir mein
**dobara likhi jaati hai** — purani cheezein jorhi nahi jaatin, hamesha sirf aakhri haalat.

---

PaperMaker — UI architecture sprint, session handoff

REPO: C:\PaperMaker\paper-maker-mvp   (sirf yeh path. E: drive ki purani copies mat chhuo)
BRANCH: feat/ui-architecture
Tree clean, sab kuch push ho chuka, dev server band, port 8000 free.

## KAAM KARNE KA TAREEQA — yeh sab se ahem hai

- Har qadam se pehle ruk kar mujh se ek-lafzi "go" lo. "Aage kya karna hai?" poochna ijazat
  nahi hai — qadam batao, phir ruko.
- Files kabhi PowerShell Set-Content/Out-File se mat likho, UTF-8 kharab hota hai. Edit ya
  Write tool use karo.
- Push main khud GitHub Desktop se karta hoon. Tum push mat karo — sirf
  `git ls-remote backup feat/ui-architecture` se confirm karo jab main kahoon.
- Koi cloud deploy nahi. `backup` remote sirf backup hai.

## HAALAT

9 ke 9 pages LIVE — bank, blueprint, index, landing, library, print, slo, slo-health, taqseem.
Sprint 0-4b mukammal. `static/theme.css` DELETE ho chuki (UI-064 part 1, 212 lines).
DOCX/PDF export bhi DELETE ho chuka (630 lines) — epic se bahar, dead-code audit se.

## AGLA KAAM — Sprint 6 ka asal hissa: UI-060..063, "the drain"

  ✅ AALA BAN CHUKA HAI: scripts/css_drain_probe.mjs
     Chalao:  node scripts/css_drain_probe.mjs <page>
     Har legacy rule ko hata kar page naapta hai, phir wapas daal deta hai.
     0 deltas = wo rule mara hua hai. Koi file kabhi edit nahi hoti.
     ⚠ 0 CANDIDATE hai, FAISLA nahi — @media, JS-rendered content,
       :hover/:focus, aur 44 se bahar ki properties sab 0 dete hain bagair
       maray huay. Chaaron caveats us file ke header mein likhe hain.

  ✅ slo.css DRAIN HO CHUKI (pehla page): 45 rules -> 35, 91 lines -> 81.
     legacy_css_lines 2,115 -> 2,105 — YEH ADAD IS EPIC MEIN PEHLI BAAR HILA.
     Uske 19 zeros mein se sirf 10 nikale; 9 blind spot thay (4 x :hover/:disabled,
     4 x .pill* jo sirf JS templates mein hain, 1 x @media).
     ⚠ Uske 26 ZINDA rules ab bhi wahin hain — unhe ghar nahi mila.

  ✅ NAU KE NAU FILES KA SURVEY HO CHUKA (2026-08-13):
       845 rules kul  ·  391 zero-delta  ·  454 zinda
     Poori table: docs/ui/ROADMAP.md ka "drain survey" section.

  ⚠ 391 KO "DELETE HO SAKTE HAIN" MAT PARHNA. slo akela page hai jo poora dekha
     gaya, aur uske aadhe zeros blind spot nikle. Asal delete-able hissa ~845 ka
     CHAUTHAI hai. Aur 454 zinda rules HI ASAL KAAM hain — un mein se ek ka bhi
     ghar nahi bana. Ek mara hua rule hatana minute ka kaam hai; ek zinda rule ko
     ghar dena har baar EK FAISLA hai (naya component / page ki apni file / value
     badalne ki ijazat).

  AGLA QADAM (do mein se ek, Irfan se poochho):
    (a) baqi files ka AASAN hissa nikalo — har file ke zeros ko caveats se chhaan
        kar delete karo. Tez, kam khatre wala, ~200 rules.
    (b) slo.css ko POORA khatam karo — uske 26 zinda rules ko ghar do. Mushkil,
        magar isse pata chalega ke ek file poori karne mein kitna waqt lagta hai,
        jo abhi bilkul na-maloom hai.

## ⚠ EK KHULA DEFECT — PAANCH LIVE PAGES PAR

`.app-sidebar` par `height: 100vh` hai aur `overflow` KOI NAHI. Content viewport se lamba ho
to scroll nahi hota — painted box se BAHAR chhalak jata hai. Irfan ne 2026-08-13 ko browser
mein pakra: index ka aakhri nav item "SLO Health" navy background se bahar tha. index par
page-scoped `overflow-y: auto` se theek kiya. **library, bank, slo, slo-health, taqseem par
wohi hole khula hai** — unki nav 209-294px hai, index ki 450px thi, is liye abhi nahi phata.
Jaan-boojh kar nahi chhua: paanch live pages apna gate maangte hain.

KOI PROBE ISAY NAHI DEKH SAKTA — probe ka viewport 900px hai (wahan overflow hota hi nahi)
aur `overflow` captured property hi nahi. Fix 0 deltas deta hai; iska matlab "kuch bigra
nahi", yeh nahi ke "kaam karta hai".

## DOOSRA KHULA KAAM — dead-code audit, adhoora

API layer ho chuka (2026-08-13) aur us par amal bhi hua: 80 routes, 74 zinda.
✅ `export.docx` + `export.pdf` DELETE ho chuke (e2bdcc4) — 630 lines unke tests samet,
   plus `python-docx` aur LibreOffice subprocess ka taqaza. Irfan ka faisla, aur UI-ARCH
   epic se BAHAR (wo epic sirf ek backend change ki ijazat deti thi, UI-003).
⬜ ABHI KHULA: `/api/syllabus-topics` ka koi caller nahi — na frontend, na test. Faisla
   nahi hua.
⬜ `blueprint-presets/{id}` aur `library/question-types` sirf tests se bulaye jaate hain —
   asal routes, magar koi frontend raasta nahi. Faisla nahi hua.
⬜ JS / CSS / services wala audit shuru bhi nahi hua.

⚠ FastAPI routes ginte waqt: is version mein `app.routes` included routers ko
`_IncludedRouter` objects mein rakhta hai jinpar `.path` hai hi nahi. `.path` par filter
karoge to sirf 4 docs endpoints aur 2 mounts milenge aur lagega ke sab kuch toot gaya.
`_IncludedRouter` ginlo (abhi 14) ya `app.openapi()["paths"]` parho.

## PEHLA QADAM HAMESHA ENUMERATION HOTA HAI, LIKHAI NAHI

Is usool ne do din mein char cheezein pakrin jo review nahi pakar saka:
- `btn.css` mein `white-space` ghayab thi (13 mein se 12 properties port ho chuki thin) —
  UI-041 ke CHAR review rounds nahi pakar sake.
- UI-043 critical path par tha hi nahi — teenon selectors live pages par collide karte hain.
- D22 `index` ko rok hi nahi raha tha — wo tasheeh 9 din se board par un-parhi pari thi.
- `taqseem` ka safed brand slab — chaar pages ki policy ke khilaf, aur wo maine hi daala tha.

Tareeqa: `css_orphans.py <page> --rules --names` chala kar list nikalo ke page kya khota hai,
phir HAR line ko naye tree ke against KHUD check karo. Coverage ke daawe par bharosa mat karo.
Ek probe run ka kharch hai.

Aur ek qaida jo mehnga sabit hua: **probe batata hai ke kya kho raha hai — yeh nahi ke kya
rakhna chahiye.** `.brand` ka slab probe ne "lost" dikhaya tha; chaar pages pehle hi tay kar
chuke thay ke usay JAANA chahiye, aur wo faisla ek sibling entry file (pages/bank.css:110)
mein likha tha jo kholi hi nahi gayi thi.

## TOOLS

  scripts/css_orphans.py <page> --rules --names     page kya khota hai + har rule ka ghar
  scripts/css_page_rule_probe.mjs <url> [selector]  rule kis layer mein aaya + kitne match
  scripts/css_type_probe.mjs <label> <outdir>       regression gate — AB 8 PAGES
  scripts/css_type_diff.mjs <before> <after>        deltas
  baqi probes: docs/ui/PROBES.md

Server: start-local.bat (uvicorn, port 8000). Probes headless Edge uthate hain — mehnga hai;
jahan static HTML se jawab mil sakta ho wahan grep behtar hai. JSON hamesha scratchpad mein
(har css_type_probe run ~15 MB), repo mein nahi — kaam ke baad delete kar dena. C: drive is
session mein ek baar poori bhar gayi thi aur ek write fail hui.

⚠ JO PAGE MIGRATE HO RAHA HO, USAY css_type_probe KI LIST MEIN PEHLE DAALO. taqseem par yeh
der se hua aur usne ek JHOOTA ALL-CLEAR paida kiya: probe ne ".row mehfooz hai" kaha kyunke
wo taqseem ko dekh hi nahi raha tha. JIS PAGE KO PROBE DEKH NAHI RAHA, USKA 0 SABOOT NAHI.

## TEEN TRAPS JO LAG CHUKE HAIN

1. `\b` wali grep hyphenated names par galat match deti hai (`app-sidebar`, `urdu-toggle-row`).
   Class token check karna ho to poora attribute match karo:
   `class="([^"]* )?(app|top|nav)( [^"]*)?"`
2. `css_orphans` ka "orphan" sirf itna matlab rakhta hai ke page ki APNI legacy file usay
   redeclare nahi karti. Naya tree usay cover karta hai ya nahi — wo tumhein khud dekhna hai.
3. Raw hex COMMENT ke andar bhi `unsanctioned_hex` mein ginta hai. Yeh check is epic mein
   DAS baar fail ho chuka hai, har baar comment ke zariye — do baar isi session mein.

## STALE NUMBERS — batae gaye, theek nahi kiye

- `PLAN.md`:313 kehta hai `docs/ui/` 2,655 lines hai. Asal ~4,073.
- `main.css`:117 kehta hai `theme.css` 6 pages par plain `<link>` hai. Wo file ab **mojood hi
  nahi**, to poora comment purana ho chuka hai.

## PEHLA KAAM

`docs/ui/ROADMAP.md` padho (order + estimates + khule items), phir `docs/ui/NEXT-SESSION.md`
ka "START HERE" block. Uske baad Sprint 6 ka pehla qadam propose karke mujh se "go" lo.
