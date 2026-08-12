# Handoff — 2026-08-12 (session end after `UI-047a`)

Naye session mein yeh poori file paste kar dein. Yeh file har session ke aakhir mein
overwrite hoti hai — hamesha aakhri haalat rakhti hai.

---

PaperMaker — UI architecture sprint, session handoff

REPO: C:\PaperMaker\paper-maker-mvp   (sirf yeh path. E: drive ki purani copies mat chhuo)
BRANCH: feat/ui-architecture
HEAD: UI-047a ka commit — tree clean, dev server band, port 8000 free

KAAM KARNE KA TAREEQA (yeh sab se ahem hai):
- Har qadam se pehle ruk kar mujh se ek-lafzi "go" lo. "Aage kya karna hai?" poochna ijazat
  nahi hai — qadam batao, phir ruko.
- Files kabhi PowerShell Set-Content/Out-File se mat likho, UTF-8 kharab hota hai. Edit tool
  use karo.
- Push main khud GitHub Desktop se karta hoon. Tum push mat karo, sirf `git ls-remote backup
  feat/ui-architecture` se confirm kar dena jab main kahoon.
- Koi cloud deploy nahi (Railway/Northflank band hain). `backup` remote sirf backup hai.

HAALAT: 9 mein se 7 pages live.
  live:   bank, landing, library, print, slo, slo-health, taqseem
  baqi:   blueprint, index

AGLA KAAM — UI-043 (tables + domain).
Yeh dono bachi hui pages ka mushtarak blocker hai: blueprint ko uska .chip chahiye, index ko
uska .tag. In dono mein se koi bhi UI-043 ke bagair nahi khul sakti.
Tarteeb jo isse banti hai: UI-043 → UI-046 → UI-047b (blueprint khulti hai).
index uske baad bhi D22 par ruki rahegi, jise koi component unpark nahi kar sakta.

UI-043 SHURU KARTE WAQT PEHLA QADAM: ENUMERATION, likhai nahi.
UI-047a ne yehi kiya aur usne `btn.css` mein ek missing declaration pakri jo UI-041 ke CHAR
review rounds nahi pakar sake the — `white-space`, jiski 13 mein se 12 properties port ho
chuki thin aur 13vin bas ghayab thi. Tareeqa: `css_orphans.py <page> --rules --names` chala
kar list nikalo ke page kya khota hai, phir har line ko tree ke against check karo. Ek probe
run ka kharch hai.

UI-046 KE BARE MEIN EK NAAPI HUI BAAT (2026-08-12):
blueprint par koi layer hai hi nahi — probe ne `layerStatements: []` diya, page sirf app.css +
theme.css + 99-legacy/blueprint.css load karta hai, main.css kabhi nahi. Yani UI-046 ke 12 ke
12 rules aaj inert honge. Unki tasdeeq UI-047b ke BAAD hi ho sakti hai. Likhna mehfooz hai,
magar "11 live + 1 known-dead" ko verified mat likhna jab tak dobara naap na lo.
Aur: `.app`/`.top`/`.nav` chhe live pages par 0 elements match karte hain, is liye
css_type_probe ka pass hona UI-046 ke liye koi saboot nahi — sirf no-regression check hai.

TOOLS:
  scripts/css_orphans.py <page> --rules --names     page kya khota hai + har rule ka ghar
  scripts/css_page_rule_probe.mjs <url> [selector]  rule kis layer mein aaya + kitne match
  scripts/css_type_probe.mjs <label> <outdir>       live-page regression gate (5 pages)
  scripts/css_type_diff.mjs <before> <after>        deltas
  baqi probes: docs/ui/PROBES.md
Server: start-local.bat (uvicorn, port 8000). Probes headless Edge uthate hain — mehnga hai,
jahan static HTML se jawab mil sakta ho wahan grep behtar hai. JSON hamesha scratchpad mein,
repo mein nahi.

EK TRAP: `\b` wali grep `app-sidebar` aur `app-nav` par galat match deti hai (hyphen word
boundary hai). Class token check karna ho to poora attribute match karo:
class="([^"]* )?(app|top|nav)( [^"]*)?"

PEHLA KAAM: docs/ui/NEXT-SESSION.md ka "START HERE" block padho, phir UI-043 ki enumeration
ka qadam propose karke mujh se "go" lo.
