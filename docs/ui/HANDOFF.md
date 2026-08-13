# Handoff — 2026-08-13 (session end: 9 OF 9 PAGES LIVE — Sprint 4b complete)

Naye session mein yeh poori file paste kar dein. Yeh file har session ke aakhir mein
overwrite hoti hai — hamesha aakhri haalat rakhti hai.

---

PaperMaker — UI architecture sprint, session handoff

REPO: C:\PaperMaker\paper-maker-mvp   (sirf yeh path. E: drive ki purani copies mat chhuo)
BRANCH: feat/ui-architecture
Tree clean, dev server band, port 8000 free.

KAAM KARNE KA TAREEQA (yeh sab se ahem hai):
- Har qadam se pehle ruk kar mujh se ek-lafzi "go" lo. "Aage kya karna hai?" poochna ijazat
  nahi hai — qadam batao, phir ruko.
- Files kabhi PowerShell Set-Content/Out-File se mat likho, UTF-8 kharab hota hai. Edit tool
  use karo.
- Push main khud GitHub Desktop se karta hoon. Tum push mat karo, sirf `git ls-remote backup
  feat/ui-architecture` se confirm kar dena jab main kahoon.
- Koi cloud deploy nahi. `backup` remote sirf backup hai.

HAALAT: 9 ke 9 pages LIVE. Sprint 4b mukammal.
  live:   bank, blueprint, index, landing, library, print, slo, slo-health, taqseem
  held:   koi nahi

AGLA KAAM — SPRINT 6 (UI-060..064), "the drain". Yahan se CSS GHATNA shuru hoti hai.
  99-legacy/*  = 2,115 lines, nau files
  theme.css = 212 lines — AB ISAY KOI PAGE LINK NAHI KARTA, delete pehli baar unblocked
  app.css   = 57 lines  — NAU KE NAU pages abhi bhi link karte hain (@font-face + .icon
              sprite). Yeh UI-064 ke saath jaata hai, abhi nahi.
  Sprint 5 (466 inline styles) aur UI-042/UI-043 JAAN-BOOJH KAR chhore hain:
    koi page inka muntazir nahi, aur Sprint 5 ka bara hissa drain ke doran khud nikal aayega.
  Andaza: 6-12 sessions. Yeh andaza SAB SE KAMZOR hai — is qism ka ek bhi task abhi
  tak nahi hua.

⚠ EK KHULA DEFECT, PAANCH LIVE PAGES PAR:
.app-sidebar par `height: 100vh` hai aur `overflow` KOI NAHI. Content viewport se lamba ho
to wo scroll nahi hota, painted box se BAHAR chhalak jata hai. Irfan ne 2026-08-13 ko
browser mein pakra — index ka aakhri nav item "SLO Health" navy background se bahar tha.
index par page-scoped `overflow-y: auto` se theek kiya. library, bank, slo, slo-health,
taqseem par WOHI HOLE KHULA HAI (unki nav 209-294px hai, index ki 450px thi, is liye abhi
nahi phata). Jaan-boojh kar nahi chhua: paanch live pages apna gate maangte hain.
KOI PROBE ISAY NAHI DEKH SAKTA: probe ka viewport 900px hai (wahan overflow hota hi nahi)
aur `overflow` capture hi nahi hoti. Fix 0 deltas deta hai — matlab kuch bigra nahi, yeh
nahi ke kaam karta hai.
  blueprint : ✅ LIVE 2026-08-13 (UI-046 → UI-047b)
  index     : UI-047c — aur iske saamne KUCH NAHI hai

UI-043 AB CRITICAL PATH PAR NAHI HAI (naapa gaya 2026-08-12).
Board kehta tha ke dono pages UI-043 ke .chip aur .tag par ruki hain. Chaar rules daav par
hain — .chip (blueprint x1), .tag (index x2), .row (index x1), .summary-row:last-child
(index x1) — aur teen pehle se migrated pages par live hain. main.css:42 layer order mein
legacy sab se neeche hai, to layer(components) ka rule unhe dobara paint karta hai.
YEH SIRF PARHA NAHI, NAAPA GAYA: teenon rules arzi tor par layer(components) mein likhe,
css_type_probe same-browser control ke against chalaya, phir rules hata diye —
landing par 21 deltas, taqseem par 2 (gap 12px -> 10px).
.chip probe se naapa hi nahi ja sakta: taqseem par koi static .chip hai hi nahi, wo sirf
chipHtml() ke template string mein hai, to jab tak asal data render na ho chips kisi snapshot
mein nahi aate. Uska faisla dono declarations ke muqable se hua — 99-legacy/taqseem.css:72 ek
khara bordered block hai (code + strand + seq + select andar), theme.css:127 ek chapti pill.
Component wala rule pehle ko doosre mein gira dega.
Chaaron rules page-scoped hain aur UI-047b / UI-047c ke andar jaate hain — wahi jagah jahan
taqseem ka bara .card gaya. Poora saboot: docs/ui/NEXT-SESSION.md §📐

IS NAAP MEIN EK JHOOTA ALL-CLEAR AAYA THA — SABAQ YAAD RAKHNA.
Pehli run ne landing ke ilawa har jagah 0 diya, jo ".row mehfooz hai" parha gaya. Ghalat tha:
probe ki page list mein taqseem tha hi nahi, aur wohi akela live page hai jiska legacy .row
alag gap deta hai. slo/slo-health par 0 is liye aaya ke unki value pehle se wahi hai — yeh
ittefaq hai, collision ka na-hona nahi. JIS PAGE KO PROBE DEKH HI NAHI RAHA, USKA 0 SABOOT
NAHI HOTA. taqseem ab css_type_probe.mjs:33 ki list mein hai (der se — UI-047a ko usi din
add karna chahiye tha, jaisa us file ka apna comment kehta hai).

INDEX PAR JO PEHLE SE MALOOM HAI:
- Urdu toggle: 2 x <button class="urdu"> Nastaliq kho denge, kyunke forms.css:101 ka
  `button { font-family: inherit }` (layer elements) 99-legacy/index.css:34 ke `.urdu, .ur`
  (layer legacy) ko harata hai. IRFAN KA FAISLA (2026-08-13): **A — page-scoped, index ki apni
  entry file mein**. Sirf 2 elements; index:444 ka <input class="urdu"> mehfooz hai (inline
  style), aur bank/print mutasir nahi (unke class names hyphenated hain).
- Orphans: .tag x2, .row x1, .summary-row:last-child x1 — teenon page-scoped jaayenge, aur
  4 partial rules jinme .main ki teen properties hain.
- index SAB SE BARA aur SAB SE KHATRE WALA page hai: 7-screen SPA, 783 elements, 224 inline
  styles. blueprint ki tarah DO HISSON mein baanto — pehle entry file (unlinked, inert),
  phir <link> swap + markup.

BLUEPRINT SE DO TRAPS JO INDEX PAR DOBARA DEKHNE HAIN:
1. brand.js:22 `.brand .name` ko query karta hai — us class ko hatao to school ka naam
   khamoshi se set hona band. index bhi brand.js load karta hai.
2. 99-legacy/blueprint.css:28 ne `.main` par max-width rakhi thi — class hatate to content
   poori chaurai mein phail jata. index ki legacy file bhi aise rules rakh sakti hai.
DONO ko koi gate nahi pakarta: css_type_probe ki list mein index hai hi nahi. RE-CLASS SE
PEHLE JS aur LEGACY dono mein grep karo.

PEHLA QADAM HAMESHA ENUMERATION HOTA HAI, LIKHAI NAHI.
Ek hi din mein isi qadam ne do cheezein pakrin jo review nahi pakar saka: btn.css mein ghayab
`white-space` (13 mein se 12 port ho chuki thin), aur UI-043 ka critical path se hatna.
Tareeqa: `css_orphans.py <page> --rules --names` chala kar list nikalo ke page kya khota hai,
phir har line ko naye tree ke against khud check karo — coverage ke daawe par bharosa mat karo.
Ek probe run ka kharch hai.

TOOLS:
  scripts/css_orphans.py <page> --rules --names     page kya khota hai + har rule ka ghar
  scripts/css_page_rule_probe.mjs <url> [selector]  rule kis layer mein aaya + kitne match
  scripts/css_type_probe.mjs <label> <outdir>       live-page regression gate (5 pages)
  scripts/css_type_diff.mjs <before> <after>        deltas
  baqi probes: docs/ui/PROBES.md
Server: start-local.bat (uvicorn, port 8000). Probes headless Edge uthate hain — mehnga hai,
jahan static HTML se jawab mil sakta ho wahan grep behtar hai. JSON hamesha scratchpad mein
(har css_type_probe run ~12 MB), repo mein nahi. C: drive is session mein bhar gayi thi —
scratchpad ki purani JSON files kaam ke baad delete kar dena.

DO TRAPS JO IS SESSION MEIN LAGE:
1. `\b` wali grep `app-sidebar` aur `app-nav` par galat match deti hai (hyphen word boundary
   hai). Class token check karna ho to poora attribute match karo:
   class="([^"]* )?(app|top|nav)( [^"]*)?"
2. css_orphans ka "orphan" matlab sirf yeh hai ke page ki APNI legacy file usay redeclare
   nahi karti — naya tree usay cover karta hai ya nahi, wo tumhein khud check karna hai.

EK STALE NUMBER JO THEEK NAHI KIYA GAYA: PLAN.md:313 kehta hai docs/ui/ 2,655 lines hai
(asal ~3,835), aur main.css:117 kehta hai theme.css 6 pages par plain <link> hai (asal 2:
blueprint, index). Dono batae gaye the, chhue nahi gaye.

PEHLA KAAM: docs/ui/NEXT-SESSION.md ka "START HERE" block padho, phir UI-046 ka pehla qadam
propose karke mujh se "go" lo.
