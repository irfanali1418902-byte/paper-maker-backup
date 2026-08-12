# Handoff — 2026-08-12 (session end: UI-047a shipped, UI-043 struck)

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

HAALAT: 9 mein se 7 pages live.
  live:   bank, landing, library, print, slo, slo-health, taqseem
  baqi:   blueprint, index

AGLA KAAM — UI-046 (nav + shell). Yeh ab blueprint se pehle ka AKELA code hai.
  blueprint : UI-046 → UI-047b        (sirf yeh raasta)
  index     : sirf D22 ka faisla → UI-047c   (koi code aage nahi)

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

UI-046 SHURU KARNE SE PEHLE YEH JAAN LO (naapa gaya 2026-08-12):
blueprint par koi layer hai hi nahi — probe ne `layerStatements: []` diya, page sirf app.css +
theme.css + 99-legacy/blueprint.css load karta hai, main.css kabhi nahi. Yani UI-046 ke 12 ke
12 rules aaj inert honge. Unki tasdeeq UI-047b ke BAAD hi ho sakti hai. Likhna mehfooz hai,
magar "11 live + 1 known-dead" ko verified mat likhna jab tak dobara naap na lo.
Aur: .app/.top/.nav chhe live pages par 0 elements match karte hain, is liye css_type_probe ka
pass hona UI-046 ke liye koi saboot nahi — sirf no-regression check hai.

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
