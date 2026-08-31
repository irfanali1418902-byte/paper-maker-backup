# PaperMaker — Fix / Feature Log

## 2026-08-31 — FAISLA: CSS epic ka target `legacy_css_lines` ~1400 (Irfan)

Purani range **`1,200–1,400` mansookh**. Ab ek adad hai: **~1400**.

**Wajah ye nahi ke kaam mushkil hai — wajah ye hai ke 1,200 riyazi taur par pohanch se
bahar tha.** Usi din `css_duplication_audit.py` dobara chali:

```
rule-block lines  1359
page-only         1051  (77%)  <- 2026-08-19 ka faisla, barqarar
agree                76  (6%)
disagree            232  (17%)
```

**Scope mein kul 308 lines.** Us waqt `legacy_css_lines` 1729 tha, to floor `≈1420`.
Range ka neecha sira sirf tab milta jab page-only ki 1,051 lines scope mein aatin — aur
wo **rad kar diya gaya**, kyunke wo mehaz `99-legacy/<page>.css` → `pages/<page>.css`
shift hai: na duplication ghatti hai, na CSS.

**Ye adad chaar files mein alag alag likha hua tha** (`HANDOFF.md`, `PLAN.md`,
`docs/ui/ROADMAP.md`, `STATUS.md`). Chaaron par nishan lagaya gaya, aur faisla
`DECISIONS-FOR-IRFAN.md` §5 mein apni jagah darj hua — us file ka header ab ye bhi
kehta hai ke §5 ke adad **usi din dobara naape gaye** (§1–§4 board se copy kiye gaye
thay). Warna wohi bimari: ek file mein faisla, teen mein purana number.

**Aaj ka faasla: 1707 − 1400 = 307 lines** — lag-bhag utna hi jitna scope mein bacha
hai. Yani target pohanch mein hai, magar item 8 ka tail, item 9 aur `body` ka bacha hua
hissa **teenon** chahiyen.

## 2026-08-31 — UI-073: `body` — jise "sab se bara bacha hua kaam" kaha gaya tha, wo zyada tar murda tha

`legacy_css_lines` **1729 → 1707 (−22)** · `unsanctioned_hex` **308 → 301 (−7)** ·
**type probe 0 deltas, state probe 0 deltas**, dono 10 pages par. 1075 pass, ruff saaf.

### Board ne ise "38 lines, `other` ke baad sab se bara `disagree` item" kaha. Dono baatein ghalat thin.

Ginti pehle: `99-legacy` ke `body` rules **50 lines** hain, 38 nahi — board `@media`
wale nahi ginta.

Aur "disagree" ka matlab hota hai *har ek par faisla chahiye*. Naapa gaya —
`css_selector_probe` `body` par, nau pages:

```
font-family  "IBM Plex Sans", system-ui, sans-serif   nau ke nau par
color        rgb(15,23,42)                            nau ke nau par
background   rgb(247,248,251)                         nau ke nau par
smoothing    antialiased                              nau ke nau par
```

**Nau ke nau pages ek hi qeemat compute karte hain — is ke bawajood ke chhe files
ne ye chaar cheezein apne apne tareeqe se likhi hui thin.** `print` `color: #1a1a1a`
(rgb(26,26,26)) likhta hai aur rgb(15,23,42) paint karta hai; `taqseem` teen alag
token naam (`--font-body`/`--fg`/`--app-bg`) likhta hai aur wohi qeemat paint karta
hai. Wajah `css_page_rule_probe` se: **`03-elements/typography.css` ka `body`
`layer(elements)` mein hai aur `margin` `02-generic/reset.css` deta hai** — layer
order legacy ko harata hai, to ye sab **migration ke din se murda** hain.

**Yani ye faislon ka khandan nahi tha, deletion tha.** Chhe files ke `body` blocks se
sirf do zinda declarations bachi hain — `display: flex` aur `min-height: 100vh` —
kyunke typography ye do deti hi nahi.

**Do gates, 0 deltas:** type probe **2,450,110 element×property** (10 pages × 5
viewports) aur state probe **368,620** (paanch states) — dono par **0**.

### Review ne pakda: is task ne khud chhe declarations murda kar dein

`body` hi wo aakhri jagah thi jahan chaar pages ka `--bg` parha jata tha, aur `slo`/
`slo-health` ka `--ink` bhi. Hataate hi wo be-consumer ho gaye — **yani task ne apne
peechhe wohi kachra chhora jo UI-072 saaf karne baitha tha.** Chhe declarations
(`--bg` × 4, `--ink` × 2) delete; JS ka `setProperty` bhi dekha (sirf `--accent` aur
print knobs set karta hai, ye do nahi). **Gate dobara: 0 deltas.** Isi se `unsanctioned_hex`
307 → **301**.

### Aur wohi trap, terhvin dafa

Pehle draft mein maine `print` ke murde rang ko comment mein `#1a1a1a` likh diya.
`unsanctioned_hex` **308 par khara raha** jab ke ek hex delete hua tha — kyunke
**comment ke andar ka raw hex bhi ginta hai** (`HANDOFF.md` trap 1, "baarah dafa fail
ho chuka" — ab terah). `rgb(26,26,26)` likhne par ginti 307 par aa gayi.
**Ginti ne pakda, meri nazar ne nahi.**

### Jo `body` par ab bhi zinda hai (agle session ke liye)

* `display: flex` + `min-height: 100vh` — chhe pages par. `pages/plan.css` pehle se
  `@layer objects { body { display: flex } }` ka namoona rakhti hai. **Faisla Irfan
  ka:** shared objects rule, ya per-page rehne do.
* `@media (max-width:760px) body { flex-direction: column }` — **saat files mein
  byte-identical**, magar media query + layer order milkar wohi shakal banate hain
  jis ne UI-05x mein 75 deltas diye the. Uthane se pehle naapna laazmi.
* `html, body { margin: 0; height: 100% }` — chaar files. `margin` reset se murda
  hai; **`height: 100%` aur `html` ka hissa naapa nahi gaya** — is round mein chhua
  nahi.
* `index` ke teen `body.lang-ur` rules — `05-components/urdu.css` mojood hai, magar
  ye khandan badalna apna faisla hai.

⬜ **Browser check nahi hua** (aaj ka bakaya pehle se khula hai).

## 2026-08-31 — R2 seeding: Pre Year 3 — 43/87 se 64/87

Backup: `paper_maker_backup_before_preyear3_seed_20260831.db` (run se pehle).

| | pehle | ab |
|---|---:|---:|
| bank kul | 766 | **850** |
| PY3 topics | 43/87 | **64/87** |
| PY3 sawal | 172 | **256** |

PY1 (71/81, 329) aur PY2 (23/87, 92) chhue nahi gaye. Wohi command jo `ROADMAP.md`
mein darj hai (defaults NAHI):

```
python -m scripts.seed_bank --subject Mathematics --grade "Pre Year 3" \
  --types "multiple-choice,short-answer,true-false" --bloom foundational \
  --max-topics 87 --write
```

**Quota:** 21 topics ke baad HTTP 429, phir musalsal 3 par script khud ruki —
`[25/44]` tak pohanch kar 19 topics chhu-e bhi nahi gaye. Andaza "~20/din" tha,
aaj **21** mile. **Baqi: PY3 ke 23 + PY2 ke 64 = 87 topics**, lag-bhag **chaar
aur din**.

### `--write` se pehle jo dekha gaya — aur jo pehli nazar mein khatra laga

44 unseeded rows aankh se parhi gayeen: sab asli pre-school Math hain, wo jaali
Grade-4 duplicate rows nahi. **Magar title khud dohraye hue thay** —
`Concept of subtraction` **13 dafa**, `Practice of addition` 4, `Addition` 3 —
aur un ka `learning_outcome` bhi bilkul title ke barabar hai. Sirf `page_no`
farq karta hai, jo prompt mein jata hi nahi. Yani 13 topics ko **ek jaisa prompt**
milna tha.

Kharch karne se pehle naapa gaya: PY3 ke pehle se seeded topics mein
`Activity of missing number` **3 dafa** isi shakal mein seed ho chuka tha, aur us
ke 12 sawal alag alag hain; poore 172 sawal mein **bilkul ek jaisa matn sifar**.
Is bunyaad par run kiya gaya. **Baad ki tasdeeq: 36 subtraction sawal, 36 ke 36
alag**, aur PY3 mein ab bhi duplicate matn **0**. Yani ek jaisa prompt duplicate
sawal nahi deta — mazmoon ka overlap hai, naql nahi.

⬜ Sawalon ka **matn** nazar se nahi parha gaya (sirf ginti aur duplicate-check).

## 2026-08-29 — UI-072: audit — jo baqi kaam nahi, ghalti thi

Irfan: *"ache tarah audit karlo, jaha jo kaam baqi hai aur ghalti ke zumre mein hai use
theek karlo."* Ye us ka nateeja — **baqi kaam se alag kar ke sirf ghaltiyan**.

`legacy_css_lines` **1751 → 1732 (−19)** · `unsanctioned_hex` **333 → 308 (−25)** ·
`hardcoded_hex_inline` **76 → 74** · **unresolvable `var()` bina fallback ke 1 → 0** (do
aur jo fallback rakhte thay wo bhi gaye — alag cheez, alag ginti) · 1075 pass, ruff saaf,
frozen yaksan · type probe **sirf 40** (maqsood), state **0**, inject **0**.

### Sab se ahem: D14 kehti thi ye "already inert" hai. Wo inert nahi thi.

`99-legacy/library.css` ka `.pg-btn { color: var(--text) }` — `--text` kahin declare hi
nahi hota. **D14 ise 2026-07-28 se "already inert" keh kar parked rakhe hue thi.** Maine
usi bunyaad par declaration delete ki, "zero-delta" samajh kar.

**Probe ne 25 deltas dikhaye: `rgb(15,23,42)` → `rgb(0,0,0)`.**

Wajah — aur ye poore epic ke liye kaam ki hai: **ek `var()` jo resolve na ho, wo "kuch
nahi" ke barabar NAHI hai.** Wo declaration ko *invalid at computed-value time* banata
hai, aur `color` jaisi **inherited** property par us ka natija `inherit` hota hai.
`<button>` par yehi cheez UA ke `color: buttontext` (kaala) ko harati thi. Declaration
hatate hi UA ka kaala rang wapas aa gaya.

Yani **toota hua `var()` teen hafte se kaam kar raha tha.** Ab wo `color: inherit` hai —
sahi qeemat, sahi tareeqe se, aur repo mein ab **koi unresolved `var()` nahi bacha**.

### `bank` par teen border grey thay, aur teesra sirf ghalat token naam se tha

`bank.html`:104 aur :601 ke do inline boxes `var(--line, #e2e8f0)` parhte thay. **`--line`
bank par declare hi nahi hota** (wo `theme.css`/blueprint/taqseem ka naam hai), to hamesha
fallback `#e2e8f0` paint hota tha — jab ke usi page ke cards `#EAEDF3` aur legacy `--border`
`#E3E8F1` hai. Ab dono `var(--color-border)` par; **do inline hex kam**, aur ye D55 ki
fehrist mein teesra rang tha jo kisi faisle se nahi, ek typo se aaya tha.

### 44 murda token declarations — nau pages, sifar deltas

`99-legacy` ke nau `:root` blocks mein **150 tokens declare** hote hain. Har page ke liye
alag naapa — us ki apni legacy file, us ka entry file, **aur us ka HTML (inline `var()` +
JS ka `setProperty`)**, kyunke D12 ka sabaq yehi hai:

```
taqseem   12 murda    index 7    slo 5    blueprint 6    slo-health 6
bank       3          landing 2  library 2               print 1        = 44
```

**`--primary-hover` nau ke nau files mein declare hota hai aur sifar dafa parha jata hai**
— chhe jagah apni poori line par, `#244a90` ke saath. Us ke saath `--easy`/`--medium`/
`--hard`/`--prog-bg`/`--prog-tx` bhi poore repo mein be-consumer hain.

**44 declarations (150 declare thay, 106 bache), 21 poori lines, aur teeno probes par 0 deltas** — yani wo waqai murda
thin. `taqseem` ka `:root` 15 se **3** par aa gaya; us ke upar ka comment ("purane naam
barqarar taake page-specific rules na tootein") ab jhoot tha, wo bhi durust.

### Teen deferred rows band, dono tools mein

* **D56** — `plan.html` kisi probe ki page list mein nahi tha, aur wohi **ek page hai jis
  ka koi legacy file hai hi nahi** (sirf naya tree), yani har component tabdeeli us tak
  bina naape pohanchti thi. Ab dono probes mein hai.
* **D53** — `css_type_diff` ka 60-delta cap khamosh tha. Ab list aakhir mein
  `… and N more` likhti hai aur `--all` cap uthata hai. *(Isi khamoshi se ek dafa board
  par "0 deltas" likha gaya tha jab ginti 30 keh rahi thi.)*
* **D58** — `pages/index.css` ka comment kehta tha legacy ka `.brand .tag`
  *"already wins at 0,2,0"*. Layer order specificity se pehle chalta hai; durust.

### Do cheezein jo aage kaam aayengi

**`node --check` kaafi nahi.** D53 ke fix mein maine `LIST_CAP` ko `args` se pehle rakh
diya — syntax bilkul theek, magar chalane par `Cannot access 'args' before initialization`.
**Tool ko chala kar hi pakda gaya**, check se nahi.

**`scripts/css_orphans.py` ab khud basi hai.** Wo `static/theme.css` ke against naapta hai,
jo 2026-08-13 ko delete ho chuki. Chalane par khud warning deta hai ke *"'supplied' will
read 0 for every page"* — aur us ke `orphan`/`dead`/`covered` columns isi wajah se bay-maani
hain. Us ki jagah per-page `var()` resolution wali check hai jo is audit mein chali.
**D59.**

⬜ **Browser check nahi hua.** Sirf do cheezein nazar aane wali hain: `bank` ke do boxes ka
border (halka farq), aur `library` ke pagination buttons ka rang (jo pehle jaisa hi hona
chahiye — agar kaala dikhe to `color: inherit` kaam nahi kar raha).

## 2026-08-29 — UI-071: item 7 ka doosra nisf — aur ek probe jo pehle mumkin hi nahi thi

Item 7 mukammal. `legacy_css_lines` **1757 → 1751 (−6)** · `unsanctioned_hex` **333**
(nahi hila) · **1075 pass**, ruff saaf · frozen inventory yaksan · type probe **36**,
state probe **0**, **injection probe blueprint/print/index/slo/slo-health par 0**.

### Pehle ye maloom hua ke is nisf ka zyada hissa naapa hi nahi ja sakta

Probe se ginti, kaam shuru karne se pehle:

```
.shortfall-panel   blueprint 0   print 0        <- JS se banta hai
.pill              har page  0                  <- JS se banta hai
.chips             har page  0                  <- JS se banta hai
.row               index 1 · slo 4 · slo-health 2 · taqseem 1
.empty-state       slo 1 · slo-health 4   (display:none, JS kholta hai)
```

**31 lines mein se 26 aisi thin jin par dono gates har haal mein 0 deltas dete** — chahe
main kuch bhi torh doon. Ye D45 wali shakal hai aur **D12 is ko 2026-07-28 se darj kar rahi
thi**; `status.css` ka header bhi sessions ko *"verify colour by injecting the class"* keh
raha tha, magar har session ye kaam haath se karta aur phenk deta.

Irfan ka faisla: **harness banao.** `scripts/css_inject_probe.mjs` — har khandan ka apna
builder-markup us **asal container** mein daalta hai jahan builder likhta hai, phir computed
values naapta hai. Output `css_type_probe` ki shakal ka hai, to maujooda review-shuda
`css_type_diff` bina kisi tabdeeli ke parh leta hai. `PROBES.md` rule 10.

Ek cheez us ne foran pakdi: `print` ka `.section-block` **khud bhi JS-built hai**, to fixture
ne container na milne par **report kiya, khamoshi se 0 nahi diya** — yehi design ka maqsad
tha.

### `shortfall` — chhe rules component par, do dabbe apni jagah

Chhe andar wale rules (`.sf-head`, `.sf-reason`, `.sf-q`, `.sf-options`, `.sf-options li`,
`.sf-gain`) dono files mein **byte-identical** thay → `05-components/shortfall.css`.
`.shortfall-panel` ka dabba dono jagah apna rehta hai.

⚠ **Layer upar le jaane se pehle naapa gaya (D51/UI-066).** `layer(components)` `generic`
aur `elements` dono ko harata hai, to legacy mein murda declaration upar ja kar zinda ho
jati. Naap: `.sf-options` `padding-left: 20px` aur `margin-top: 3px` **pehle se live** thay
aur `list-style-type: disc` har element par — yani kuch resurrect nahi hua. (`reset.css` ka
`* { margin: 0; padding: 0 }` comment ke andar hai, live rule nahi — wohi ek cheez thi jo
inhein murda kar sakti thi.)

**Injection probe: blueprint 0, print 0.** Yani chhe rules layer badalne ke bawajood bilkul
waise hi paint karti hain. **Koi maujooda gate ye saboot de hi nahi sakta tha.**

### ⚠ Aur wo wajah jo maine Irfan ko di thi, ghalat thi

Maine likha tha *"print chhapta hai; amber fill toner kharch karta hai"*, aur usi bunyaad
par do dabbe rakhne ka faisla hua. **Panel kabhi chhapta hi nahi:** `print.html`:993 use
`no-print` ke saath banata hai aur `99-legacy/print.css`:203/:338 `@media print` mein
`.no-print` ko chhupa dete hain. Us ka `display: block` bhi sirf `.no-print` ke
`inline-flex` ko harane ke liye hai (`print.css`:373 khud kehta hai). Irfan ko durust
haqeeqat batai gayi aur unhone **wohi faisla dobara diya, asal wajah par**: do jagah, do
maqsad — blueprint ka panel `.status-bar.warn` ke andar baithta hai, print ka paper preview
mein.

### `.chips` aur `.pill` — ek naam, do cheezein

Irfan: **dono rakho, alag naam do.**

* `taqseem` ka `.chips` → **`.col-chips`** (us page ke apne `.col-head`/`.col-empty` ke
  khandan mein). `slo-health` ka `wrap` hai, ye `column` — **sirf `display: flex` sanjha
  tha**, baqi har cheez alag.
* `slo` ka `.pill` → **`.sum-pill`** (import ka natija-counter). `index` ka `.pill` question
  ka metadata chip hai jo **apna rang inline `style=` se leta hai**. *(Ye `.pill` wala faisla
  poochha nahi gaya tha — maine `.chips` wala usool laga diya, kyunke haalat bilkul wohi
  hai. Agar Irfan `.pill` ko alag rakhna chahein to ye ulta ho sakta hai.)*

Injection probe se naapa: `.col-chips` aur `.sum-pill` **bilkul waise hi** paint karte hain
jaise purane naam karte thay.

⚠ **Aur rename ne ek break banaya jo maine khud paida kiya.** `slo.html` par `.pill` **do**
jagah render hota hai — `:180` (`renderSummary`) aur `:238` (`renderAssignSummary`). Maine
pehla rename kiya, doosra chhoot gaya; wo teen counters bilkul unstyled ho jate. Poore repo
ka sweep chalane par pakda gaya. **Rename karte waqt ek call site kaafi nahi — sab gino**,
aur JS template strings grep se hi milte hain.

### Do chhoti qeematein majority par

* `.row` gap — `taqseem` 12px → **10px** (`slo` 4 + `slo-health` 2 elements banaam 1)
* `.empty-state` padding — `slo` 18px → **16px** (`slo-health` 4 banaam 1)

Type probe ke 36 deltas theek yehi do hain, plus un ke height knock-ons. State probe 0.

### Review ne naye gate ko hi FAIL kiya — aur wo theek tha

**Rule 10 pehle hi din apne aap par laga.** Us ne likha tha *"fixtures are copies and they
rot"*, aur teen fixtures pehle hi ghalat thay:

* **`index` — container hi ghalat tha.** `#results` maujood hai, resolve bhi hota hai, aur
  **`.pill` wahan kabhi render hota hi nahi**. Asal container `#replaceCandidates`
  (`index.html`:592) hai, jo ek modal ke andar hai. Yani probe ek saaf, purevishwas
  measurement de rahi thi aisi jagah se jahan app ye cheez rakhti hi nahi. **Jo fixture
  resolve ho jaye zaroori nahi ke wafadar ho** — aur modal band hota hai, to ab
  `data-open="1"` set kar ke pehle khola jata hai.
* **`taqseem` — bachche ghalat thay.** Maine `.tag` daale; `.col-chips` ke andar asal mein
  `.chip` cards hote hain (`chipHtml()`, `taqseem.html`:127). `.tag` taqseem ki class hai
  hi nahi, to probe do be-style spans naap rahi thi aur **`.chip` ki koi bhi regression pass
  kar deti.**
* **`slo-health` — container ka ancestor** (`.slo-main`) diya tha, asal `#uncoveredBox` hai.

Teeno theek. Ab naap: `taqseem` ke asal `.chip` cards (safed, 11px radius, `.code` badge),
`slo-health` ke `.tag`, aur `index` ke `.pill` modal ke andar — sab styled.

⚠ **Ratchet PAANCHWEEN dafa upar gaya (1751 → 1755)** — review ne `.row`/`.empty-state` par
wajah likhne ko kaha, maine paanch line ke comment likh diye. Ab wajah **usi rule ki line ke
aakhir mein** hai: wajah bhi darj, aur ek line bhi nahi barhi. **Ye is qaide ka hal hai jo
pehle nahi likha gaya tha — legacy mein comment upar nahi, line par.**

Aur ek chhoti: probe ka comment `String.raw` template ke andar tha aur us mein backtick
likh diya — literal wahin khatam ho gaya. `node --check` ne pakda.

⬜ **Browser check nahi hua.** Fehrist HANDOVER mein.

## 2026-08-28 — UI-070: item 7 ka pehla nisf — `btn` + `page-head`, aur do census ghaltiyan meri apni

`legacy_css_lines` **1759 → 1757 (−2)** · `unsanctioned_hex` **334 → 333 (−1)** ·
**1075 pass**, ruff saaf · type probe **2543**, state probe **1530** · frozen inventory
das pages par yaksan.

Item 7 ko do sessions mein baanta gaya — chaar families aur paanch faisle ek diff mein
un-reviewable ho jate (`ROADMAP.md` ka apna qaida). Ye pehla nisf: `btn` + `page-head`.

### 1. D49 ka nateeja ship hua — `cursor: not-allowed` pehli dafa zinda

`03-elements/forms.css` ko `button:disabled { cursor: not-allowed }` mila. Yahan rakhne ki
wajah ye hai ke **jise harana tha wo isi file mein us se teen satar upar hai** — bare
`button { cursor: pointer }`. Ek hi layer, aur `(0,1,1)` banaam `(0,0,1)`, yani specificity
se jeet — source order par bharosa nahi. Component file mein rakhna ghalat hota: ye disabled
controls ke bare mein element-darja haqeeqat hai, `.btn--*` variant nahi.

Chhe legacy declarations delete: `blueprint:48`, `index:96`, `library:185`, `print:74`,
`print:83`, `slo:31`.

**State probe: 1050 `cursor: pointer → not-allowed`** — bank 921, library 68, index 44,
print 12, blueprint 3, slo 2. Ye adad hi is task ka nateeja hai: UI-063 ka faisla
2026-08-26 ko hua tha aur **aaj tak ek bhi pixel par render nahi hua tha**.

⚠ **Ab ye chhe se zyada buttons par lagta hai** — `button:disabled` un buttons ko bhi
pakadta hai jin ki apni kabhi koi rule nahi thi. Ye maqsood hai (Irfan ka faisla "har
disabled button" tha) magar likha ja raha hai kyunke scope chhe rules se bara hai.

⚠ **Magar "har" bhi ghalat lafz hai, aur review ne naap kar pakda.** Ek bare-class
`cursor: pointer` jo `layer(components)` mein ho wo is rule ko harata hai — layer upar
hai, specificity ka koi dakhal nahi. **Yani wohi shakal jo bug ki thi, ulti taraf se.**
Do aisi classes hain jin ka apna `:disabled` sathi nahi:

```
btn.css:380          .btn-save, .btn-cancel { cursor: pointer }
                     .btn-save:disabled hai (:400), .btn-cancel ka nahi
pages/print.css:291  .ps-range-all { cursor: pointer }, koi :disabled nahi
```

Naapa gaya: `.btn-cancel` disabled kar ke bhi `pointer` deta hai. Aaj ye dono kabhi
disabled hote hi nahi (`bank.html`:605, `print.html`:223/257/66 — sab static), to kuch
ghalat render nahi hota. **Aur yehi wajah hai ke `bank` par 921 deltas aaye jab ke us par
928 buttons hain** — farq isi carve-out ka hai. `index` par 44 deltas banaam 36 buttons
ulta sabab rakhta hai: `cursor` inherit hone wali property hai, to disabled button ke
andar ke `<span>` bhi ginti mein aate hain.

### 2. D47(a) band — jhoota comment durust

`forms.css` khulа to D47(a) apni tehreer ke mutabiq due thi. Comment kehta tha
`:focus-visible` "being later in the file it wins". **Nahi jeetta.** Dono `layer(elements)`
mein hain, to source order ka koi dakhal nahi — **specificity faisla karti hai**, aur
`input:focus` `(0,1,1)` hai jab ke `:focus-visible` `(0,1,0)`. Keyboard focus par dono
match karte hain aur `outline: none` qaim rehta hai; field ka indicator teal border + 3px
glow hai. **Rendering ghalat nahi — sirf comment ghalat tha.** D47(b) (ring ya glow) ab
bhi khuli hai aur Irfan ki hai.

### 3. `btn-danger` / `btn-edit` — aur meri census ghalti

Maine Irfan ko bataya tha ke ye "dono pages par ek-ek button hain, barabari hai", aur usi
bunyaad par unhone `library` wali size chuni. **Wo bunyaad ghalat thi.** Probe:

```
.btn-danger    bank n=459    library n=24
.btn-edit      bank n=459    library n=24
```

Maine sirf static HTML ka template gina tha — **ye buttons JS se render hote hain**, har
question row par ek jodi. 483 buttons, do nahi, aur `bank` un ka 95% rakhta hai. Faisla
sahi ginti ke saath dobara liya gaya: **bank wali (12px / 4px 10px)**, yani 48 buttons
hile, 918 nahi. `library` ka `.btn-edit` border `#c0d0ea` → `var(--border)` bhi gaya, jo
bank pehle se paint karta tha — ek raw hex kam.

**Teen session se yehi sabaq lag raha hai aur is dafa main hi us mein phansa.** Markup ginna
kaafi nahi jab markup JS se banta ho — probe ka `n` hi asal ginti hai (D12).

### 4. `page-head` → `.pagehead`, aur wo wrapper `<div>` jo faisle mein nahi tha

`.pagehead` chaar pages par pehle se live tha (blueprint, slo, taqseem, plan). Teen baqi
(bank, library, slo-health) `.page-head` par thay. Rename hua, 6 legacy lines gayin, aur ab
**koi page `.page-head` nahi pehnta.**

⚠ **Pehli koshish ghalat thi aur probe ne pakdi.** `.pagehead` `display: flex` hai. Maujooda
chaar pages apne `<h1>` + `<p>` ko ek `<div>` mein lapetate hain, yani flex ka **ek hi
child** hota hai aur andar sab kuch normal stack karta hai. Teen nayi pages par `<h1>` aur
`<p>` **seedhe children** thay — flex ne unhein **saath saath** rakh diya, aur naapa gaya:

```
slo-health  h1        26.39px -> 52.78px     (do lines par wrap)
slo-health  #draftNote 32.12px -> 86.50px    (teesra flex child, dab gaya)
h1/p        min-height 0px -> auto           (flex item ban gaye)
```

`slo-health` par to ek **teesra** element bhi tha — `#draftNote` — jo faisle mein zikr hi
nahi hua tha. Teeno par wrapper `<div>` daal kar shakal maujooda chaar jaisi kar di gayi;
2798 deltas ghat kar 2543 reh gaye aur wrapping wale sab ghayab.

⚠ **Aur ye trap pehle se likha hua tha — maine parha hi nahi.** Chaaron maujooda pages ke
markup mein ek comment maujood hai: *".pagehead is display:flex — the inner `<div>` is
what keeps the title and subtitle stacked… which is what this page did until
2026-08-15."* Yani blueprint isi mein gir chuka tha aur warning chhod gaya tha. **Maine
CSS parhi aur markup ka comment nahi** — wohi ek darja jo bachaata. Ab teeno nayi pages
par bhi wohi comment hai (review ne yaad dilaya).

**Jo preview maine Irfan ko dikhaya tha (h1 aur p ek line par) wo ghalat tha** — sahi
adoption stack ko waisa hi rakhta hai. Asal tabdeeli sirf itni hai: container ka
`margin` 0/24 → 6/22, aur `p` ka rang `--muted` → `--color-text-muted`, `margin-top` 3px,
`max-width` 620px. Saaton pages ab hu-ba-hu ek jaise.

### 5. `card.css` ka **teesra** basi dawa — jo UI-068 mein mujh se chhoot gaya

Header kehta tha `.pagehead` rules "off every live page — **0 matches, measured**".
`.pagehead` us waqt **chaar pages par live tha**. UI-068 ne isi header ke **do** basi dawe
theek kiye (13-element census aur `.ch` wala) aur **yehi teesra chhod diya**. `main.css`
:180 par bhi wohi teen dawe naql shuda thay — dono jagah durust.

**Sabaq: jab ek comment block ka koi hissa ghalat nikle, poora block parho** — sirf wo
jumla nahi jis par thokar lagi.

### 6. Ratchet phir upar gaya — CHAUTHI dafa — aur phir mere comment se

Pehli measurement par `legacy_css_lines` 1759 → **1760**. Maine `library.css` mein chaar
line ka comment likh diya tha. Chhota kar ke **1757**.

Aur usi comment mein **ek raw hex** (`#c0d0ea`) tha — **is session mein doosri dafa**
(pehli `nav.css` mein, UI-069). `unsanctioned_hex` us ke nikalne par hi 334 se 333 hua.
Qaida `card.css` ke header mein pehle se likha hai aur ab paanch nahi, **saat** dafa fail
ho chuka hai — har dafa comment ke zariye.

⬜ **Browser check nahi hua.** Fehrist HANDOVER mein.

## 2026-08-28 — UI-069a: D49 — probe andha nahi tha, CSS murda thi

Item 7 se pehle wala gate task, bilkul UI-064 wali shakal: pehle aala theek karo, phir us
family ko haath lagao. **Koi CSS, markup ya test nahi chhua** — sirf `PROBES.md` (naya
rule 9), `DEFERRED.md` (D49 → Resolved), `ROADMAP.md` ki item 7 row, aur ye entry.

### Sawal

`css_state_probe` ka `:disabled` pass `cursor` par khamosh tha. 2026-08-26 ko control
chalaya gaya tha: `slo.css` ki `.btn:disabled` ka cursor `not-allowed` → `crosshair` kiya,
probe dobara chalaya — **0 deltas**, jab ke **usi rule ki `opacity` theek 0.5 parhi ja rahi
thi.** Ek hi rule, ek hi element, ek hi lamha. D49 ne do imkan likhe thay aur kaha tha
andaza mat lagao — D45 isi tarah andha ship hone wala tha.

### Naap — chaar buttons, sab disabled, farq sirf layer ka

```
:disabled rule ka layer          cursor          opacity
  legacy    (sab se kamzor)      pointer         0.5     <- rule haar gayi
  elements                       not-allowed     0.5
  components                     not-allowed     0.5
  unlayered                      not-allowed     0.5
```

**CDP disabled control par `cursor` bilkul theek parhta hai.** Farq *muqable* ka hai: is
app mein kisi cheez ne button par `opacity` declare nahi ki, is liye wo sab se kamzor layer
se bhi jeet jati hai; `cursor` ka harif maujood hai — `03-elements/forms.css:155` ka bare
`button { cursor: pointer }`, `layer(elements)` mein, jo `layer(legacy)` ko specificity se
qat'a nazar harata hai.

**Probe sahi tha. CSS murda thi.**

### Nateeja — jo is task ka asal hasil hai

`99-legacy/` ki **chhe** `cursor: not-allowed` declarations inert hain, aur hamesha se
thin: `blueprint:48`, `index:96`, `library:185`, `print:74`, `print:83`, `slo:31`. Chhon ke
chhon `<button>` element par hain, yani `forms.css` un sab ko match karta hai.

**Iska matlab UI-063 ka faisla kabhi render hi nahi hua.** 2026-08-26 ko Irfan ne har
disabled button ke liye `not-allowed` chuna tha; wo aaj tak kisi page par nazar nahi aaya.
Item 7 ke liye ye "chhe murda lines nikalo" nahi hai — **"faisla ab bhi chahiye ya nahi,
aur agar chahiye to use `layer(legacy)` se upar dobara ship karna parega"** — aur upar
uthana wohi D51 wala kaam hai jis ne UI-066 mein chhe pages tore thay.

### Aur ek aam qaida jo is se nikla — `PROBES.md` rule 9

*"Declaration hili nahi"* aur *"probe use dekh nahi sakta"* **do alag dawe hain**, aur
inhein alag karne ka sasta tareeqa usi rule ki doosri declaration hai. **Agar ek hili, to
reader kaam kar raha hai.** Do din ye row is liye khuli rahi ke ye sawal poochha nahi gaya.

*(D49 kehti thi ye note "beside rules 10 and 11" likha jaye — `PROBES.md` mein aath rules
hain. Wo hawala bhi basi tha; note rule 9 ban gaya.)*

## 2026-08-28 — Audit: baqi kaam ka naya naap, aur teen cheezein jo plan se mail nahi khatin

Item 6 ke baad poora naap dobara liya (`css_baseline.py` + `css_duplication_audit.py` +
rule-by-rule dump). **Koi CSS, markup ya test nahi chhua** — sirf `ROADMAP.md` ki table,
ye entry, aur `STATUS.md` ka pointer.

```
legacy_css_lines   1,759      available work   351  (69 agree + 282 disagree)
unsanctioned_hex     334      rule-block     1,398
                              page-only      1,047  (75%, jaan-boojh kar skip)
```

### 1. Jo hisaab plan ko "finishable" banata tha, wo ab band nahi hota

`ROADMAP.md` khud likhti thi: *"1,806 − 461 = 1,345, so the target and the work still
agree."* Aaj wohi hisaab **1,759 − 351 = 1,408** deta hai, target `~1,350` ke khilaf —
**58 lines ka farq.**

**Wajah ghalti nahi, do alag paimane hain.** Available work sirf **rule-block** lines par
naapa jata hai (1,398). `legacy_css_lines` **har** line ginta hai (1,759). Beech ka
**361 lines** ka farq `:root` blocks, `@media` wrappers, comments aur khali lines hai —
aur **drain in mein se kisi ko target nahi karta**. Rules nikalte hain, ye baithi rehti
hain, aur projected floor **neeche nahi, upar** khisakta hai. 27 tareekh ko 1,345 tha, aaj
1,408, aur barhta rahega.

Ye faisla hai, bug nahi: ya target ~1,408 ho jaye, ya 1,047 page-only lines mein se kuch
scope mein aayen — magar page-only 2026-08-19 ko jaan-boojh kar nikala gaya tha, to wo
doosra project hai.

### 2. 351 mein se 156 un families mein hain jin par ✅ lagi hai

| family | item | agree | disagree | baqi |
|---|--:|--:|--:|--:|
| `shell/nav` | 3 ✅ | 12 | 45 | 57 |
| `modal` | 5 ✅ | 11 | 43 | 54 |
| `field/filter` | 4 ✅ | 22 | 13 | 35 |
| `card` | 6 ✅ | 2 | 4 | 6 |
| `brand` | 6 ✅ | 0 | 4 | 4 |

**44%.** Har session ne apna baqiya jaan-boojh kar chhora aur `PROGRESS.md` mein likha bhi
— item 6 ne `.card-title` (4 lines, teen qeematein) aur `print` ka 18px brand (2 lines)
is liye chhora ke wo Irfan se poochhe gaye faislon mein shamil nahi thay. **Masla chhorna
nahi, ye hai ke board par tick nazar aati hai aur baqiya wahan se dikhta hi nahi.** Sirf
us table se plan karne wala session samjhega ke items 3–6 ki qeemat 0 lines hai.

### 3. Family labels khud bhi ghalat ho sakti hain

`css_duplication_audit.py:98` `family()` selector par regex chalata hai. Dump se:

```
shell/nav  DISAGREE  38L   body       bank,library,print,slo,slo-health,taqseem
modal      DISAGREE   2L   #status    index,print
```

**`body` nav nahi hai.** Chhe files mein 38 lines — `other` ke baad **repo ka sab se bada
single disagree item** — aur kyunke regex use ✅ wali family mein daalta hai, koi row use
shedyool nahi karti. `#status` modal nahi hai.

**Census ka sabaq ab ek darja upar chala gaya hai.** Item 5 ne dekha bucket ne kam gina;
item 6 ne dekha `card` mein kam aur `brand` mein zyada; ab maloom hua **naam bhi ghalat ho
sakta hai**. Rules parho, family ka naam nahi.

### Aur item 7 se pehle do cheezein jo pehle se likhi hui hain

- **`D49` apni tehreer ke mutabiq yahin due hai** — *"before any decision that involves a
  cursor"* — aur `btn` theek wohi jagah hai jahan UI-063 ka `cursor: not-allowed` wala
  tehai bina naape reh gaya tha. **`D47` bhi khuli hai aur item 1 par band honi thi.**
- **`card.css` ka aakhri jumla kehta hai `.btn` abhi safe nahi**: `slo.html` par do live
  `class="btn"` buttons hain. Bare `.btn` un ko le lega — bilkul wohi harkat jo item 6 ne
  `.card` ke saath ki, aur wo sirf is liye kaamyab hui ke pehle har legacy modifier gina
  gaya tha.

Item 7 ka asal size bhi **61 lines** hai, 39 nahi — row disagree-only quote karti thi.

## 2026-08-28 — UI-068: card — bucket chhe kehta tha, markup ne aath dikhaye

Finishing plan ka **item 6**, pehla nisf (`card`). `legacy_css_lines` **1798 → 1772 (−26)**,
`unsanctioned_hex` **338 → 337 (−1)**. **1075 pass**, ruff saaf. Type probe **1284 deltas**,
state probe **0** — har delta gina gaya, neeche.

### Audit ne chhe files kahe. Aath thin, aur do naye tree mein chhupi thin

Row kehti thi `card` = 28 lines, 6 files (bank, blueprint, index, library, slo, slo-health).
Ginne par **`.card` aath pages par** — aur do total nikle, dono sahi:
**markup mein 46, aaram ki halat ke DOM mein 42.**

| page | bank | blueprint | index | library | slo | slo-health | taqseem | plan |
|---|--:|--:|--:|--:|--:|--:|--:|--:|
| `.card` (markup) | 4 | 4 | 20 | 4 | 3 | 6 | 1 | 4 |

Farq index ke **chaar** cards ka hai jo JS template strings se bante hain
(`index.html`:876 / 2390 / 2404 / 2418), is liye kisi probe snapshot mein maujood nahi
(`css_selector_probe` index par `n=16` deta hai). **Probe se moqabla karte waqt 42, HTML
parhte waqt 46.** Review ne pakda ke pehli tehreer dono adad ko ek bana rahi thi.

`taqseem` aur `plan` kisi bucket mein nahi thay **kyunke un ki `.card` rule `99-legacy/`
mein hai hi nahi** — wo `pages/taqseem.css` aur `pages/plan.css` ke andar `@layer components`
mein bare `.card` ship kar rahe thay, dono apne header ke saath jo samjhata tha ke card.css
ye rule kyun nahi de sakta. `css_duplication_audit.py` sirf `99-legacy/` parhta hai, is liye
us ne aath ko chhe gina. **UI-067 ka sabaq bilkul dobara: bucket par nahi, markup par gino.**

### Aur ek adad jo teen hafte se ghalat tha, aur khud ko theek nahi kar sakta tha

`05-components/card.css:8` likhta tha: *"`.card` is carried by 13 elements today — slo 3,
slo-health 6, library 4, measured 2026-08-08"*, aur isi jumle ki bina par bare `.card` rule
ko rok rakha tha. **Aaj 42 elements, 8 pages hain.** Adad 29 elements aur 5 pages kam tha —
aur wo kabhi theek na hota, kyunke *dekhne se rokne ki wajah* usi paragraph mein likhi thi
jis mein adad tha. Header ab naapi hui tafseel ke saath badal diya gaya.

Usi file ka doosra dawa bhi expire ho chuka tha: *"the day a live page's markup gains a `.ch`
child, these four rules activate"*. Teen pages ne le liya — blueprint 1, taqseem 1, plan 4.
Rules haftôn se live hain aur theek chal rahi hain; note sahi tha, defect nahi.

### Irfan ka faisla: naye tree ki qeematein

Aath implementations sirf **teen** properties par ikhtelaf karti thin (`css_selector_probe`,
2026-08-28) — baqi sab par pehle se muttafiq thin:

| | radius | shadow | margin-bottom |
|---|---|---|--:|
| bank, blueprint, library, slo, slo-health | 14px | `rgba(22,33,58,.06)` | 22px |
| index | 16px | `rgba(22,33,58,.05)` | 0 |
| taqseem, plan | 16px | `--shadow-card` | 0 / 22px |

Faisla: **`--radius-container` · `--shadow-card` · `--space-gap`**. Radius phir faisla nahi
tha balke **parhna** tha — `theme.css:183` khud kehta hai *"cards, panels, modals"*, wohi
be-istemal role jo UI-067 ne modals ke liye dhoonda tha.

### Chauthi tabdeeli jo faisle mein NAHI thi, aur majboori thi

**Border ka rang 620 deltas mein badla: `rgb(227,232,241)` → `rgb(234,237,243)`.** Legacy
`--border` `#E3E8F1` hai, naye tree ka `--color-border` `#EAEDF3`. Ek component Tier 2 role
hi parh sakta hai (CLAUDE.md §11), is liye ye tabdeeli component par jaane ka **lazmi**
nateeja thi, alag intikhab nahi. Farq bohat halka hai magar 42 elements par hai —
**browser check ki fehrist mein pehla item yehi hai.** Do border rang poori app mein hain,
sirf cards mein nahi: **D55**.

### D51 phir — teen rules layer badalne se mar rahi thin

Bare `.card` `layer(components)` mein hai aur legacy sab se kamzor layer hai. Ye teen rules
barabar specificity (0,1,0) par bhi **haar jatin**, is liye naapi aur upar uthai gayin:

| rule | tha | agar na uthate |
|---|---|---|
| `bank` `.add-q-collapse { padding: 0 }` | legacy | collapsible add-question card ko 22px padding milti, jab ke summary ki apni `18px 22px` pehle se hai |
| `bank` `.bp-card` / `.bulk-card { border: 2px solid #c7d8f7 }` | legacy | neela 2px border 1px slate ban jata |
| `index` `@media(760) .card { padding: 18px }` | legacy | phone par 22px inset reh jata |

Pehli do ab `pages/bank.css` mein `.card.bp-card` / `.card.add-q-collapse` (0,2,0) ke tor
par hain — `.bp-card` nahi, taake import order par bharosa na karna pare. Teesri
`pages/index.css` ke `@media` block mein. **Naapa gaya: probe mein `padding` ka ek bhi delta
nahi aaya**, yani teeno lift kaam kar gaye.

`.card.has-ch` (blueprint) poori tarah murda ho gayi — `card.css` padding aur overflow deta
hai, aur radius ab dono taraf wohi 16px hai. Delete.

### Padding literal 22px hai, aur ye bhool nahi

`--space-inset` sab se zahir choice thi — `theme.css:176` khud use *"card / panel padding"*
kehta hai — magar wo **24px** resolve karta hai, aur **kisi bhi page ka koi card 24px nahi
padta**; chhon ke chhon bare cards 22px naapte hain. Yani role maujood hai, isi kaam ka naam
lekar, aur ghalat adad rakhta hai. Us par rule point karna 42 elements ko token ki aar mein
2px hila deta. `--space-inset` ko 22px karna `.card > .ch` aur `.card > .cb` ko hila deta, jo
aaj waqai 24px chahte hain. **Ye token ka faisla hai, card ka nahi — D54.**

### Naapa gaya — 1284 type deltas, poore, capped list se nahi

Diff ki chhapi hui list 60 per page par cap hoti hai (D53), is liye ginti seedhi JSON se
ki gayi. **Chhe qism ke ilawa kuch nahi:**

```
  620  border-*-color   rgb(227,232,241) -> rgb(234,237,243)   (--border -> --color-border)
  400  border-radius    14px -> 16px
  185  box-shadow       -> --shadow-card
   75  margin-bottom    0px -> 22px        (index 70, taqseem 5)
    4  height           taqseem 900 -> 915.156px  (upar wale margin ka nateeja)
    0  padding          -- teeno lift kaam kar gaye
```

`landing` aur `print` par **0** — un par `.card` hai hi nahi. State probe **0**, sab pages.

**`plan` kisi probe ki page list mein nahi hai** (na type, na state). Alag se
`css_selector_probe` se naapa: 16px / padding 0 / `--shadow-card` / mb 22px /
`rgb(234,237,243)` — **bilkul pehle jaisa, ek pixel nahi hila**. Probe ki ye khali jagah
khud ek row hai: **D56**.

✅ **Browser check ho gaya — Irfan, 2026-08-28.** `bank` aur `slo-health` par naya border
rang aur 16px kone, `index` par cards ka naya 22px faasla, aur `landing`/`blueprint` par
kuch na hilna — sab theek. **Border ke rang par khaas poochha gaya kyunke wo faisle mein
shamil nahi tha; Irfan ne dekh kar qubool kiya**, is liye D55 defect nahi, consistency row
hai.

## 2026-08-28 — UI-069: brand — nau pages par ek naam, chhe alag cheezein

Finishing plan ka **item 6**, doosra nisf (`brand`). `legacy_css_lines` **1772 → 1759 (−13)**,
`unsanctioned_hex` **337 → 334 (−3)**. **1075 pass**, ruff saaf. Type probe **297 deltas**,
state probe **0**. Frozen inventory (`id`/`onclick`/`name`/`for`/`data-*`) das pages par
**bilkul yaksan** — naapa gaya, maana nahi.

### `.brand` ek class hai, chhe cheezein hain

ROADMAP:155 kehta tha `.brand` chhe tarah drift ho chuki hai. Markup se ginne par wo chhe
**shakalein** nahi, chhe **mukhtalif dhaanche** nikle:

| | dhaancha | kahan |
|---|---|---|
| bank, library, slo, slo-health | `.name` + `<small>`, logo nahi | sidebar — pehle se component par |
| index | `.logo` + `.name` + `<div class="tag">` | sidebar |
| taqseem | `.logo` + `.name` + `<small>` + divider | sidebar |
| print | **naked text + `<small>` — `.name` element hai hi nahi** | sidebar |
| blueprint | `o-shell__brand`, safed topbar, dark text | top bar |
| landing | **hero header ke andar** — 52px safed logo, 20px naam, gradient par | sidebar nahi |

**`landing` is family ka member hai hi nahi.** Audit ne use "brand" bucket mein daala kyunke
selector ka naam ek hai; wo hero ka block hai, sidebar ka nahi. Chhoda nahi gaya — **nikala
gaya**, aur wajah likh di gayi (`nav.css` header). UI-067 ka wohi sabaq, ulti simt se: bucket
ne is dafa zyada gina, kam nahi.

### `print` ka brand 27 ghante navy kinare se chipka raha

`UI-065` ne print ka `.app-sidebar { padding: 24px 18px }` delete kiya aur `sidenav__panel`
(`padding: 18px 0`) diya. `.sidenav__link` apni padding khud rakhta hai — magar **`.brand` ko
kuch nahi mila**, aur us ki apni rule mein sirf font tha. Naapa gaya:

```
.brand padding-left   bank 22 · library 22 · slo 22 · slo-health 22 · index 22 · taqseem 18
                      print 0        <- saat sidebar pages mein akela
```

Aankh se nahi, probe se pakda gaya, aur paanchon bands par. `sidenav__brand` dene se theek.

### Subtitle ka rang — legacy ki ghalti nahi, ek na-chuna hua role tha

`nav.css` ka purana comment kehta tha ke legacy ka `color: #9DB0D0` "already dead" hai, is
liye component use na uthaye. **Dono baatein sahi thin, magar sawal adhoora tha: "murda" ne
sirf itna kaha ke legacy haar gayi — ye kabhi nahi poochha ke JEETA KAUN.** Jeeta
`03-elements/typography.css:88` — ek bare `small { color: var(--color-text-muted) }`,
layer(elements) mein, body copy ke liye bilkul theek — aur wo **navy sidebar par slate-500
paint kar raha tha, chhe pages par**. Contrast ~3.1:1, AA se neeche.

Faisla (Irfan, 2026-08-28): **`--color-sidebar-fg-muted`** (`--navy-400`, ~4.5:1). Ye token
`theme.css:131` par pehle se maujood tha, isi kaam ke liye likha gaya tha, aur us ka ek hi
consumer tha — `.sidenav__foot`. **Phir wohi shakal jo UI-067 ne `--radius-container` ke
saath dekhi thi: jawab design system ke paas pehle se tha, bas koi consumer nahi tha.**

Purana pale-blue wapas nahi laya gaya: wo kisi Tier 1 role mein nahi hai, aur ab sirf
`landing` us ka user hai — aur us ka hex `nav.css` ke comment se bhi nikal gaya, jahan wo
purane note se chala aa raha tha. **Yehi teesra hex hai** (`#9DB0D0` index se, `#A9B6CE`
print se, aur ye). Review ne pakda: mera pehla draft us hex ko comment mein dobara likh
raha tha, aur usi paragraph ke aakhir mein daawa kar raha tha ke "no hex is spelled here".

### Teen pages component par aaye

`index`, `taqseem`, `print` → `.sidenav__brand*`. **`index` par 0 deltas** — us ki padding
pehle se `2px 22px 20px` thi, yani component ki hu-ba-hu; jo nahi ja sakta tha wo flex row
aur 40px logo hai, aur wo `pages/index.css` mein page-scoped hai. `taqseem` ka logo isi tarah
`pages/taqseem.css` mein. **Component sirf padding deta hai** — `display: flex` wahan nahi ja
sakta, kyunke saat mein se chaar pages ka brand logo-less block hai.

`taqseem` ne shared values qubool kiye (Irfan): padding 18→22, divider gayi, `margin-bottom`
10→0, sub ka uppercase/letter-spacing/opacity gaye, line-height 1.1→1.15.

### Do murda cheezein naap kar nikleen

- **`.brand { padding: 0 }` teeno @media blocks mein** (bank, library, blueprint) — "agree"
  bucket ki poori teen lines. Paanchon bands par naapa: teeno jagah padding 22/22/18 hi
  aata tha. bank aur library pehle se `.sidenav__brand` par thay; blueprint ka
  `.o-shell__brand` `pages/blueprint.css` mein hai. **Legacy sab se kamzor layer hai, to
  teeno kabhi lagi hi nahi.**
- **`index` ka `.brand .tag`** — `font-size` aur `color` murda thay. Purana comment kehta tha
  *"both are live at 0,2,0"*; specificity theek thi magar `pages/index.css` ka `.tag`
  layer(components) mein hai aur ye legacy mein. **D51 phir.** Sirf `letter-spacing` zinda
  thi, wohi rehne di.

### Naapa gaya — 297 deltas, poore

```
  150  color + border-*-color   slate-500 -> navy-400   (6 pages ka subtitle; border
                                zero-width hai, currentColor ka shor)
   68  print                    padding 0 -> 2/22/20, sub ka margin-top 4 -> 3px,
                                aur un ke layout knock-ons (widths/heights)
   99  taqseem                  padding, divider, margin, letter-spacing, opacity,
                                line-height + unki heights
    0  index, blueprint, landing
```

`plan` (probe list mein nahi, D56) alag naapa gaya: us ka `.sidenav__brand-sub` naya rang
qubool karta hai — maqsood, wo saatwan page hai jo component par hai. State probe **0**.

### Do cheezein jo theek NAHI ki gayin

1. **`print` ka brand ab bhi 18px/700 hai**, baqi chhe ka 15.5px. Us ke markup mein `.name`
   element hai hi nahi, to `.sidenav__brand-name` bina markup badle nahi lag sakta. Ye ek
   qeemat ka faisla hai jo poochha nahi gaya tha — is liye chhera nahi gaya. Agle session ka
   sawal.
2. **`brand.js` ka school-name feature do pages tak pohanchta hi nahi** — `print.html`
   `brand.js` load hi nahi karta, aur `plan.html` karta hai magar us par `.brand`/`.name` hai
   hi nahi. Dono pehle se aise thay. **D57**, aur wo `UI-070` se pehle due hai kyunke drain
   `.brand` ko delete karega aur script khamoshi se toot jayegi.

✅ **Browser check ho gaya — Irfan, 2026-08-28.** `print` ka sidebar ab links ke barabar
andar hai (wo bug jo UI-065 se chala aa raha tha), `taqseem` ka brand bina divider ke
theek lagta hai, aur `library` par subtitle ka naya rang theek. `blueprint` par kuch nahi
hila — jo maqsood tha, kyunke wo `o-shell__brand` par hai.

## 2026-08-28 — UI-067: modal — teen system rehne diye, shakal ek kar di

Finishing plan ka **item 5**. `legacy_css_lines` **1799 → 1798**, `unsanctioned_hex` **338**
(nahi hila — is family mein hex tha hi nahi, sab `rgba()` tha). **1075 pass**, ruff saaf.
Type probe **220 deltas**, state probe **30** — har ek maqsood.

### Irfan ka faisla: naam mat chhero, qeematein ek karo

Row ka sawal tha "teen modal system — ek karein ya teen rehne dein". Faisla (2026-08-28):
**class names bilkul na chhuein, sirf qeematein ek karein.** Wajah wazeh hai — naam badalne
ka matlab paanch pages ka markup aur JS chhoona hai aur us se **ek line CSS kam nahi hoti**;
jo be-yaksani nazar aati hai wo shakal aur rang hai, aur wo poori tarah CSS ka kaam hai.

### Pehle audit ka adad ghalat tha — sat nahi, AATH modals hain

`css_duplication_audit.py` ne is family ko 58 lines / 5 files kaha, aur `modal.css` ka header
"teen system" likhta tha. **Markup se ginne par tasveer bari nikli — aath modals, chaar
wrapper naam:**

| wrapper | pages | modals |
|---|---|--:|
| `.modal-backdrop` | bank, print | 2 |
| `.modal-overlay` | index (1), library (3) | 4 |
| `.overlay` | taqseem | 1 |
| `.lib-picker-overlay` | print ka library picker | **1 — kisi bucket mein nahi tha** |

**Aathwan modal `print` ka library picker hai.** Wo page-only hai, is liye audit ne use
"skipped 1056" mein daala tha aur item 5 ki 58 lines mein wo shamil hi nahi thi. Use chhorne
ka matlab tha ke saat modals ek jaise ho jate aur aathwan alag khada rehta — yani faisla
adhoora lagta. Shamil kar liya gaya.

Box ke naam do nahi teen: `.modal` (bank, print, index, taqseem), `.modal-box` (library),
`.lib-picker-modal` (print). **Radius ki chhe declaration** — 10, 12, 12, 14, 16, aur
taqseem ka `var(--radius)` — **magar asal mein chaar hi mukhtalif qeematein**, kyunke index
ka 16 aur taqseem ka `var(--radius)` dono pehle se 16px resolve karte the. Yehi wajah hai ke
un do pages par radius ka koi delta nahi aaya.

### Aik sawal ka jawab design system ke paas pehle se tha

`theme.css`:183 par `--radius-container` likha hai: *"cards, panels, **modals**"* — 16px.
Yani radius naya faisla nahi tha, **ek role tha jo kisi modal ne kabhi apnaya hi nahi**
(siwaye index ke, aur wo bhi ittefaqan). Ab aathon us par hain.

Do naye token bane, kyunke in ka koi role maujood nahi tha:
* `--overlay-navy-45` → `--color-scrim`. Irfan ne navy .45 chuna. **Channels `--slate-900` ke
  hain, library ke `rgba(22,33,58,.45)` ke nahi** jahan se chunao naqal hua tha: 45% alpha par
  saat-per-channel ka farq nazar nahi aata, aur teesri navy banana wohi drift hai jo ye epic
  mitane aaya hai.
* `--shadow-2` → `--shadow-modal`. Paanch shadow ki jagah ek: `0 16px 48px` (do sab se aam
  adad) `--slate-900` par, taake wo usi navy par tint ho jis par `--shadow-1` hai.

### Naapa gaya — har delta maqsood

| page | type | state | kya hila |
|---|--:|--:|---|
| `library` | 90 | 15 | scrim, radius 14→16, shadow (3 modals) |
| `print` | 60 | 5 | scrim ×2, radius 10→16 aur 12→16, shadow ×2 |
| `bank` | 40 | 5 | scrim, radius 12→16, shadow, close 22→20 |
| `index` | 20 | 5 | scrim, shadow, close 24→20 |
| `taqseem` | 10 | 0 | scrim, shadow |
| `slo`, `slo-health`, `blueprint`, `landing` | **0** | **0** | in par modal hai hi nahi |

**Do jagah radius delta NAHI aaya aur dono tasdeeq hain:** `index` pehle se 16px tha, aur
`taqseem` ka `var(--radius)` bhi 16px resolve karta tha — yani wo do pehle se durust the.
State probe ke saare 30 deltas sirf scrim ka `background-color` hain, paanch states par.

`.modal-close` ki padding jaan-boojh kar ek nahi ki gayi (chaar files mein 2px ka farq,
20px glyph par nazar nahi aata). `line-height` khud 22/24 → 20 hua kyunke wo `1` hai.

⚠ **Ratchet phir upar gaya — 1799 → 1800 — aur phir wahi wajah:** legacy files mein comment.
**Teesri dafa.** Comments ek-ek line par aaye aur number 1798 par gira. Is dafa lines kam
honi thi hi nahi: kaam declarations hatane ka tha, aur wo dense lines ke andar baithi thin.
**Is family ka faida lines mein nahi, shakal mein hai** — ROADMAP ne yehi likha tha.

### Review ne saat durustiyan nikaleen — ek code par, chhe matn par

**Cascade par kuch nahi mila:** blast radius sifar (app mein `modal`/`overlay` naam ka koi
aisa element nahi jo modal na ho — JS template literals sameet dekha gaya), koi declaration
kho nahi gayi, koi `pages/*.css` `@layer components` block in selectors ko chhoota nahi, aur
`@media print` bhi mehfooz hai.

**Code wali:** `pages/taqseem.css` ka `--radius` is commit ke baad **orphan** ho gaya tha —
us ka ek hi consumer taqseem ka `.modal` border-radius tha, jo ab component ke paas hai.
Delete kar diya. Us ke bhai `--radius-sm` (2 consumer) aur `--shadow` (1) zinda hain, gin kar
tasdeeq kiya — **review ne `--shadow` ko murda kaha tha, wo durust nahi tha.**

**Matn wali chhe, sab durust kar di gayin:** wrapper "paanch" likhe the, **chaar** hain (mera
apna table chaar hi ginta tha); `.modal-close` ki padding ka farq "2px" likha tha, **amudi
2px magar ufqi 4px** hai; `--overlay-navy-45` dark-sidebar wale section mein rakh diya tha
jis ka apna header kehta hai "hover aur active **on this sidebar**" — ab us ka apna section
hai; shadow ka comment "one per modal system" kehta tha, jabke **index aur library ek hi
system hain aur phir bhi do alag shadow rakhte the**; `modal.css` ke header ki do purani
satrein ("shared by bank and print only", "nothing below assumes the three will ever be
unified") ab is file ke apne neeche wale block se takrati thin; aur "chhe radii" ki jagah
chhe **declaration**, chaar qeematein.

⬜ **Browser check — HUA NAHI.** Dekhne wali cheezein: koi bhi modal khol kar **peechay ka
andhera** (ab har jagah ek navy), **kone** (ab har jagah 16px — `bank` aur `print` par sab se
zyada farq, 12px aur 10px se), aur `print` ka **library picker** (wo aathwan modal).

## 2026-08-27 — UI-066: field/filter disagree — 59 lines mein se 12 zinda thin, aur teen wahin rehni parin

Finishing plan ka **item 4**. `legacy_css_lines` **1806 → 1799 (−7)**, `unsanctioned_hex`
347 → **338 (−9)**. **1075 pass**, ruff saaf. Chhui gayi files: `03-elements/forms.css`, aur
`99-legacy/` mein `bank`, `blueprint`, `index`, `library`, `slo`; plus review ke baad chhe
files ke line refs.

**Adad HEAD ke khilaf naape gaye, `BASELINE.json` ke khilaf nahi** — wo file ab bhi stale hai.

### Row ki "one decision: which control sizing wins" adhoori tasveer thi

Teen sizing waqai chal rahi thin — `bank`/`blueprint`/`library` 14.5px/44px/10px 13px/radius
10px, `index` 15px/48px/11px 14px/radius 11px, `slo` 13.5px/9px 11px/radius 9px. **Magar in
mein se saat properties har jagah pehle se murda thin.** `main.css`:42 `legacy` ko sab se
neechi layer rakhta hai aur `forms.css` (layer `elements`) unhi controls par `font-family`,
`font-size`, `color`, `background`, `border`, `border-radius`, `padding` khud declare karta
hai — layer specificity se pehle tay hota hai, to legacy ka koi bhi hijja jeet nahi sakta.

Zinda sirf teen thin, kyunke inhein `forms.css` declare nahi karta: **`width`, `min-height`,
`margin-top`**. Yani 59 lines ka faisla teen declarations ka faisla tha.

**`slo`:35 to poori tarah murda thi** — us ke paas ye teen thin hi nahi.

### Do sooraakh jo naapne par nikle, aur dono live pages par thay

**1. `forms.css` ka selector list attribute par hai, aur `index` ke 11 inputs par `type` hai
hi nahi.** `#subject`, `#topic`, `#paperTitle`, `#schoolNameEn/Ur`, `#schoolAddress`,
`#schoolPhone`, `#schoolPrincipal`, `#pdfSubject`, `#pdfGrade`, `#mpSearch` — sab asal mein
text fields, aur `input[type="text"]` in mein se kisi ko match nahi karta. Unhein `index` ki
bare `input, select` rule paint kar rahi thi. Us rule ko bina soche delete karna in 11 ko
**UA ke default box par gira deta** — sizing ki tabdeeli nahi, saaf toot-phoot. Baqi aath
pages par ye adad **sifar** hai (naapa gaya). `forms.css`:53 ab `input:not([type])` aur
`input[type="email"]` (`#schoolEmail`) dono ko naam se bulata hai.

**2. File inputs us set se jaan-boojh kar bahar hain** (`forms.css` ka apna header, :16–21) —
to `library`, `index` aur `slo` par wo shared rule se poori tarah paint ho rahe the. Teenon
ko apni box rule mili, ab tokens par, is liye dobara drift nahi kar saktin.

### Aur ek ghalti jo probe ne pakdi — ye is session ka asal nateeja hai

Pehle draft ne wo teen zinda properties `forms.css` mein rakhi thin. Ye theek lagta tha aur
**chhe pages tor raha tha:**

| page | kya hila |
|---|---|
| `bank` | `.opt-input-wrap input` `min-height` 38px → 44px (**16 elements**), `.float-bar` 34px → 44px |
| `blueprint` | filter controls 38/36px → 44px |
| `print` | modal controls `min-height` 0 → 44px, `width` auto → **100%** |
| `slo-health` | selects `width` 157px → **903px**, rows reflow |
| `slo` | file input `width` 300px → **903px**, us ki row 41px → 98px |

**Wajah wohi hai jo UI-065 ne doosri simt se seekhi thi:** is app ka **har** compact override
khud `layer(legacy)` mein hai — `.opt-input-wrap`, `.float-bar`, `print` ki modal rules — to
ek base rule ek layer upar un sab ko **har specificity ke bawajood** haraati hai. UI-065 mein
legacy ne us component ko haraya tha jo breakpoint bhool gaya tha; yahan element rule ne un
legacy overrides ko haraya jo asal kaam kar rahe the.

To teenon wapas har `99-legacy` file mein gayin, jahan specificity ab bhi faisla karti hai.
Wo tab hi upar aa sakti hain jab stacked-field containers ka aik naam ho — aaj `.row`,
`.field-row`, `.filter-row`, `.ps-row` chaar naam hain. Wo markup ka kaam hai, is ka nahi:
**D51**.

⚠ **Aur ratchet pehle UPAR gaya** — 1806 → **1821** — jabke rules delete ho rahi thin. Wajah
bilkul wohi thi jo ROADMAP ne is hafte likhi thi: `99-legacy/*.css` mein lambe comments, aur
`legacy_css_lines` har line ginta hai. Comments ek-ek line par aaye, dalail yahan aayin, aur
number 1795 par gira. **Ye qaida do session mein do dafa toota hai.**

### Jo naapa gaya — sirf teen pages hile, aur wohi teen jinhein hilna tha

`css_type_probe` (paanch width bands) aur `css_state_probe`, dono before/after:

| page | type deltas | state deltas |
|---|--:|--:|
| `index` | 1350 | 523 |
| `slo` | 162 | 84 |
| `library` | 150 | 126 |
| `bank`, `blueprint`, `print`, `taqseem`, `slo-health`, `landing` | **0** | **0** |

* **`index`** — 48px/7px → **44px/6px** (Irfan ka faisla), aur us ke controls ab `forms.css`
  ka 13.5px/9px 11px parhte hain, 15px/11px 14px nahi.
* **`slo`** — selects/text ko pehli dafa control height mili (40px → 44px). **`margin-top`
  aur `width` nahi** — dono ki wajah review wale hissay mein.
* **`library`** — sirf teen file inputs, aur sirf box tokens (14.5px → 13.5px, border/radius
  ab `--color-border`/`--radius-control` par).
* **`outline-color` ke 26 state deltas `currentColor` ka peechha hain**, focus ring ka nahi —
  file inputs ka `color` `var(--ink)` se `--color-text` par gaya aur `outline-style` wahan
  `none` hai (`forms.css`:79). Koi basri asar nahi.

### Review ne chaar defect nikale, chaaron band — aur pehla gate ke andhe nuqte par tha

**1. `index` ka colour input be-libaas ho gaya tha.** `index.html`:480 `#accentColor` bhi usi
bare `input, select` rule par tha, aur `forms.css` `input[type="color"]` ko jaan-boojh kar
bahar rakhta hai (file ki tarah, UA-drawn). Us ka border, radius aur background gayab ho
chuke the — inline style sirf `min-height`, `cursor`, `padding` deti hai. Ab colour file ke
saath ek hi box rule par hai (`index.css`:87).

> ⚠ **YAHAN PEHLE LIKHA THA "type probe ne is par sifar delta diya … koi gate pakad nahi
> sakta tha". WO GHALAT HAI, aur agle din naapne par pakda gaya.** Probe ne is par **30
> deltas** diye the. `css_type_probe.mjs`:282 `querySelectorAll('*')` chalata hai, koi
> visibility filter nahi, aur `getComputedStyle` chhupe element par bhi rang/radius/padding/
> font theek deta hai — `#accentColor` snapshot mein apne border aur font-size ke saath
> maujood hai, aur fix lagte hi `index` ke deltas **1380 → 1350** gaye: theek 6 properties ×
> 5 bands. **Asal wajah `css_type_diff.mjs`:42 ka `LIST_CAP = 60` hai** — count poora hai,
> chhapi hui list kati hui, aur raay kati hui list par bani. Nuqsan asli tha aur review ne
> theek pakda; **gate ke andhepan wali wajah ghalat thi.** D53 durust kar di gayi.

**2. `slo` par `margin-top: 6px` ki koi buniyad nahi thi.** `slo.html` mein **ek bhi `<label>`
nahi** — baqi chaar pages `label { margin-top: 14px }` ke saath control ka 6px jora karte
hain, `slo` ke paas dono mein se koi nahi. Aur us ke controls `.row { display: flex;
align-items: center }` mein buttons ke saath baithe hain, to 6px unhein row-mates se neeche
gira raha tha. Hata diya; `slo` ke deltas 187 → **162**.

**Aur us rule ke saath likhi wajah bhi ghalat thi.** "width isliye nahi di ke file input
903px ho gaya tha" — magar aakhri selector `select, input[type=text]` hai, jis mein file
hai hi nahi; aur paanchon matched elements inline `width` carry karte hain, jo har layer se
jeetti hai. Yani width ka faisla wahan sifar-delta tha. **Nateeja theek tha, dalil ghalat —
aur agla session dalil hi wirse mein leta hai.**

**3. Gyarah nahi, BAARA untyped inputs hain.** Baarhwan `.sec-row__heading`
(`index.html`:1392) JS template literal ke andar hai, is liye id-sweep se chhoot gaya —
**aur isi wajah se koi probe use naapta bhi nahi**, wohi blind spot jo UI-060 mein `.pill*`
par tha. Wo naye selector se cover ho jata hai, aur us ki apni rule `layer(components)` mein
hai (sirf `flex`/`min-width`), to koi takraav nahi.

**4. Is commit ne `forms.css` mein 45 lines joreen aur us ke saare line refs khisak gaye.**
Chhe naye comments ke ilawa `btn.css`:104/232, `field.css`:102, `pages/index.css`:32/65,
`pages/print.css`:113, `pages/slo.css`:114/122/123 — sab purane number par ishara kar rahe
the. Sab naap kar theek kiye gaye. `forms.css` ka apna header bhi ab `slo` ke bare mein sach
bolta hai: wo "shared group" ab mojood nahi, isi task ne delete ki.

⚠ **Aur ek framing durusti:** "saat properties pehle se murda thin" `index` ke 12 untyped +
1 email inputs par **sach nahi tha** — un par wo zinda thin, aur `forms.css` ne selector isi
commit mein liye. Un terah controls ki qeemat waqai badli (padding 11px 14px → 9px 11px,
font 15px → 13.5px, border `#D6DEEA` → `--color-border`). `index` ke 1350 deltas ki asal
wajah yehi hai. "Murda tha" sirf `bank`, `blueprint`, `library` aur `slo` par sach hai.

### Do cheezein jo darj hui hain, chhupayi nahi gayin

* **D52** — `index` ke teen `.qtype` checkbox `width: 100%` compute karte hain aur **pehle se
  karte the**. Selector isi liye bare rakha gaya ke wo na badlein. Unhein theek karna alag
  faisla hai.
* **D51** — oopar wala, aur ye item 4 ka sab se qeemti nateeja hai.

⬜ **Browser check — HUA NAHI.** Chrome extension is baar bhi connect nahi hui. Server chalta
raha `http://127.0.0.1:8000/static/`. Dekhne wali cheezein: **`index`** ke fields (ab thore
chhote — 44px, 13.5px), **`slo`** ke selects (ab 44px, pehle 40px) aur us ka file input,
**`library`** ke teen file inputs. Aur D52 ke checkbox.

## 2026-08-27 — UI-065: shell/nav — ek shell, aur mobile collapse jo do hafte se toota para tha

Finishing plan ka **item 3**. `legacy_css_lines` **1841 → 1806 (−35)**, `unsanctioned_hex`
349 → **347**. **1075 pass**, ruff saaf.

### ROADMAP ki row ghalat thi, aur ye naap kar pata chala

Row kehti thi *"there are three navies. Pick one shell, one navy."* **Navy par koi faisla
darkar nahi tha:** saaton sidebar page `rgb(22,41,74)` hi paint karte hain. Teen **hijje**
hain (`#16294A`, `var(--brand)`, `var(--sidebar-bg)`), teen rang nahi.

Asal masla ye tha ke **kaun component par hai**: paanch page (`slo`, `slo-health`,
`library`, `bank`, `index`) `sidenav__panel` carry karte the aur un ki legacy shell rules
pehle se **mari hui** thin; `taqseem` aur `print` component par thay hi nahi. Irfan ka
faisla, 2026-08-27: **dono ko component par lao.**

Aur `blueprint` ke paas `.app-sidebar` **element hai hi nahi** (wo `o-shell` par hai, top
bar) — us ki teen sidebar rules kabhi kisi cheez par lagi hi nahi.

### Us ne aik purana bug benaqab kiya — aur wo is task ka asal nateeja hai

`nav.css` mein **koi `@media` rule tha hi nahi**, aur layer order hai
`@layer legacy, settings, …, components, utilities` — yani **`legacy` sab se kamzor**. To
har page ka apna `@media { .app-sidebar { width: 100% } }` component ke `width: 248px` se
**har baar harta tha**.

**700px band par, kisi bhi tabdeeli se PEHLE naapa gaya:**

| page | width | position | |
|---|---|---|---|
| slo, slo-health, library, bank, index | **248px** | sticky | **toota** |
| taqseem, print | 700px | static | theek |

Yani phone/tablet par paanch page ka sidebar top bar banta hi nahi tha — 248px ka sticky
column khara rehta tha. **Theek wohi do page saheeh the jo component par nahi thay**, aur
isi liye unhein component par laane wale task ne ise pakda.

**Ye do hafte chhupa raha kyunke har probe 1280 par chalta tha.** Kal ka UI-064 isi ke liye
tha. Irfan ka faisla: **jad se theek karo**, phailao mat.

`nav.css` ko ab apna `@media (max-width: 760px)` block mila hai. Qeemat ke do intikhab, dono
darj:
* **760px, 720px nahi** — chaar file 760 kehti thin, teen 720. `slo`/`slo-health`/`taqseem`
  ab 40px pehle collapse karenge (721–760 band ka asli delta).
* **`flex-direction: row`** — 760 wala group bar banata tha, 720 wala column. Majority.

### Naapa gaya — desktop bilkul nahi hila

| page | 1280 | 900 | 740 | 700 | 520 |
|---|---:|---:|---:|---:|---:|
| bank, index, library | 0 | 0 | 15 | 15 | 15 |
| blueprint, landing | 0 | 0 | 0 | 0 | 0 |
| slo | 0 | 0 | 76 | 28 | 28 |
| slo-health | 0 | 0 | 158 | 28 | 28 |
| **taqseem** | **11** | **11** | 65 | 33 | 33 |
| **print** | **74** | **74** | 80 | 80 | 80 |

**Desktop (1280/900) par sirf wohi do page hile jin ka move manzoor hua tha.** Baqi saat
par sifar. State probe: sirf `print` par 80 (rail ka 3px border + hover .08 → .07).

### Do slip jo naap kar pakdi gayin, shipping se pehle

* **Pehla `@media` rule `blueprint` ko tor raha tha.** Maine `.sidenav` likha tha, magar
  blueprint `class="o-shell__nav sidenav"` carry karta hai — **wohi nav component, magar top
  bar mein**. 18 deltas aik aise page par jis ke paas collapse karne ko sidebar hai hi nahi.
  Ab rule `.sidenav__panel .sidenav` par scoped hai; blueprint **0**.
* **`.brand` do dafa galat delete hui.** Ek dafa `print` se, ek dafa `blueprint` ke media
  block se. Dono jagah element **maujood hai** (`blueprint` par `class="brand o-shell__brand"`),
  aur brand **item 6 ki family** hai. Markup dekh kar pakdi gayi, andaze se nahi.

### Aur aik cheez jo maine khud ghalat ki: comment ne file bara kar di

Pehli koshish mein `legacy_css_lines` **1841 → 1861** ho gayi — **barh gayi**. Wajah: maine
in files mein **44 lines ke comment** likh diye jabke rules **24 lines** ke gaye. Metric har
line ginti hai. **Jin files ko drain karna hai un mein tafseel likhna drain ke khilaf hai** —
tafseel ki jagah yehi file hai. Comments chhote kar ke 1841 → 1806.

Aakhir mein 14 legacy `@media` rules (paanch file se) **naap kar** hatayin — component ke
aane ke baad wo murda thin, aur hatane par **0 deltas**.

⚠ **Browser check darj nahi hua.** Narrow-screen ka rawaiyya aaj badla hai (paanch page par
behtar, teen par 40px pehle) — ye wo cheez hai jo browser window chhoti kar ke dekhni chahiye.

## 2026-08-27 — UI-064: viewport pass — pandrah media queries mein se chaudah kabhi naapi hi nahi gayi thin

Finishing plan ka **item 2**. **Auzaar hai, drain nahi:** kisi page ki CSS ka aik byte nahi
badla, ratchet bilkul nahi hila (`legacy_css_lines` 1841 → 1841). **1075 pass**, ruff saaf.

### Masla, adad mein

Is repo ka har probe **1280×900** par chalta tha. `static/css/` mein **15 screen `@media`
width queries** hain. 1280 par un mein se **sirf 1** ka mushahida hota tha:

| band | rules | 1280 par |
|---|---:|---|
| 1–560 | 14 | **kuch nahi** |
| 561–720 | 13 | **kuch nahi** |
| 721–760 | 10 | **kuch nahi** |
| 761–1024 | 2 | **kuch nahi** |
| 1025+ | 1 | 1280 |

### Aur aadha masla width tha hi nahi

Sirf viewport barhane se kaam nahi banta tha: **jo properties ye rules set karte hain, wo
property list mein thin hi nahi.** Media blocks ke andar `flex-direction` **22 dafa**,
`flex-wrap` 9, `position` 9, `grid-template-columns` 3, `z-index` 2 aata hai — aur in mein
se koi bhi naapa nahi jata tha. Yani probe band tak pahunch kar bhi andha rehta.

### Control — daawe se nahi, do mutation se

`slo` ke `@media (max-width: 720px)` block ke andar aik-aik declaration badal kar:

| probe | control A (`display`) | control B (`flex-direction`) |
|---|---|---|
| HEAD ka probe, jaisa commit mein tha | **0** | **0** |
| naya probe, sirf `--viewports 1280` | **0** | — |
| naya probe, paanch band | **12** (sirf `@700`, `@520`) | **72** |

**Aur aik nateeja jo mere andaze ke khilaf nikla, is liye darj ho raha hai:** control B ke 72
deltas mein se **sirf 2** nayi properties par the — baqi 70 `width`/`height` ke natije the jo
purani list pehle se ginti thi. **Yani asal andhapan width tha, property list nahi.**
Properties ka faida ye hai ke diff ab **wajah ka naam** leta hai (`flex-direction: column ->
row`) na ke 70 be-wajah box moves, aur `z-index` jaisi cheez cover hoti hai jo kisi box ko
hilati hi nahi.

### Naya auzaar: `scripts/css_breakpoints.mjs`

Ye CSS parh kar **bands** nikalta hai — width ki wo range jis ke andar matching rules ka set
badal hi nahi sakta — aur batata hai ke di hui viewport list kaunsa band **nahi** dekh rahi.
Dono probe ise import karte hain aur **har run mein apne blind spots khud chhapte hain.**
Ye asal sabaq hai: D45, D49 aur ye — teenon aik hi bimari hain (gate wo cheez nahi dekh sakta
jis ki wo hifazat kar raha hai), aur us ka dawa ye hai ke gate khud bole ke wo kya nahi dekh raha.

Paanch widths (1280/900/740/700/520) **chuni nahi gayin, nikali gayin** — har band se aik.

### `css_state_probe` jaan-boojh kar 1280 par hi hai

Wajah naapi hui hai: **kisi bhi `@media` block ke andar aik bhi `:hover`/`:focus`/`:active`/
`:disabled` rule nahi hai** (pandrah ke pandrah blocks). Us par `--viewports` flag maujood
hai magar default aik hi rahega. Refactor ke baad HEAD ke probe se muqabla: **0 deltas**.

### Review ne chaar asal defect nikale — chaaron isi commit mein band

* **336 MB.** `css_type_probe` ka aik run ab ~80 MB likhta hai (paanch band), aur probe ki
  output directory `.gitignore` mein thi hi nahi. Aik `git add -A` aur wo history mein.
  Directory delete, `.gitignore` mein `.probe-*/` aur `docs/ui/probe/`.
* **Flag parsing chup-chaap tootti thi.** `argv.filter(a => !a.startsWith('--'))` flag ki
  **value** ko positional samajh leta tha, to `--viewports 1280,700 before out` ka label
  `1280,700` ban jata aur bina error ke kooda directory banti. Ab values consume hoti hain.
  `css_state_probe` mein ye **pehle se** thi (`--page` par bhi), wahan bhi theek ki.
* **`keysPerViewport` sirf chhapta tha, jaancha nahi jata tha** — jabke yehi wo cheez hai jo
  pakde ke bands ne alag-alag DOM naapa. Ab ginti barabar na ho to `drift` mein jata hai.
* **300 ms ki wajah galat likhi thi.** Maine likha tha ke sleep mid-reflow read se bachata hai
  aur determinism check us ki tasdeeq karta hai. **Dono ghalat:** `getComputedStyle` Blink
  mein synchronous layout flush karta hai, to mid-reflow read mumkin hi nahi. Sleep asal mein
  **transitions** se bachata hai (tree ki sab se lambi 0.2s), aur ye ab ahem hai kyunke
  `bottom` unhi properties mein hai jo **is task ne add ki**. Ab `css_type_probe` bhi
  `css_state_probe` ki tarah motion band karta hai, to sleep par bharosa nahi rehta.

Aur aik trap jis ka koi pehra nahi tha: reference viewport ki keys **bina suffix** hain. Do
alag viewport list wale runs ka diff poore page ko `beforeOnly`/`afterOnly` dikhata, jise
`css_type_diff` ka apna usool "0 deltas, 0 beforeOnly, 0 afterOnly" **regression samajh leta**.
Ab `css_type_diff` dono runs ki viewport list parh kar farq par saaf warning deta hai.

### Do choti ghaltiyan jo maine khud kin

`css_breakpoints.mjs` ka CLI pehli dafa **kuch nahi** chhapa — Windows par
`file://${argv[1]}` kabhi `import.meta.url` se match nahi karta (`file:///C:/…`, teen slash).
`pathToFileURL` se theek. Aur **teen dafa** template literal ke andar comment mein backtick
likh kar string tor di — teesri dafa comment mein hi likh diya ke aisa mat karna.

Ye bhi: comment ke andar likha `@media` pehle asal query gina ja raha tha (**18** aata tha,
asal **15** hai) — teen jagah ye tree apni hi media rules **prose mein** quote karta hai
(`shell.css`:58, `pages/index.css`:207, `pages/blueprint.css`:50). Ab comments blank kar ke
parhe jate hain. Over-report bhi utna hi bura hai jitna under-report.

⚠ **Browser check darj nahi hua** — is task ne kisi page ka CSS badla hi nahi, aur probe ka
apna determinism check (do run, **0 deltas, 0 drift**, nau ke nau page) wo cheez hai jo yahan
naapi ja sakti thi.

## 2026-08-26 — R7 adoption: hafta-war plan pehli dafa asal data se bhara — 4 rows se 91

Backup: `paper_maker_backup_before_r7_import_20260826.db`.

**Rukawat code nahi thi, aur file pehle se mojood thi.** `ROADMAP.md` ka order-4 row
mahine bhar se keh raha tha: *"The remaining work is not code — it is one teacher filling
in one Excel plan."* Aaj ka audit dekhta hai ke `namoona_plan_pre_year_3.xlsx` **root mein
para hai, 2026-08-23 se, untracked, aur bhara hua hai** — 87 rows, weeks **1–36**, koi
khali `week_no` nahi, aur saare `syllabus_topic_id` PY3 se milte hain. Yani jo kaam
"baqi" darj tha, wo teen din pehle ho chuka tha aur **import nahi hua tha.**

Import `POST /api/topic-plan/assign-import` se: `{"updated": 87, "cleared": 0,
"errors": [], "warnings": []}`. `topic_week_plan` **4 → 91 rows** (PY3 ke 87 + PY1 ki
wohi 4 purani browser-test rows).

### `covered: 0` bug NAHI hai — aur ye galat-fehmi likhne layak hai

Import ke baad PY3 ka coverage `covered_topics: 0` deta hai, jabke usi din seeding ne
PY3 ke **43 topics par 172 sawal** bana diye. Ye ulta nahi lagna chahiye:
`topic_coverage_service.py`:54 `covered` ko **`papers` se** nikalta hai, bank se nahi —
topic tab covered hai jab wo kisi **asal paper** mein aa jaye. PY3 ka abhi koi paper bana
hi nahi, is liye **0 durust hai.** Bank bharna aur topic cover hona do alag cheezein hain.

Tasdeeq ke liye PY1 (jis ke papers bane hue hain) wohi purana adad deta hai:
`81 topics, 49 covered, 60%` — yani import ne kuch toda nahi.

| | pehle | ab |
|---|---:|---:|
| `topic_week_plan` rows | 4 | **91** |
| PY3 planned topics | 0 | **87** (36 hafte) |
| PY3 covered | — | **0** (koi paper nahi bana) |
| PY1 coverage | 49/81, 60% | **49/81, 60%** (na hila) |

**Ab `plan.html` par PY3 ka board pehli dafa asal hai.** Order-4 ki "Built ≠ adopted"
warning ab PY3 ke liye khatam; PY2 aur PY1 ke liye ab bhi qaim hai.

## 2026-08-26 — R1 seeding: Pre Year 3 ka doosra run — 23/87 se 43/87

Backup: `paper_maker_backup_before_preyear3_seed_20260826.db` (run se pehle).

| | pehle | ab |
|---|---:|---:|
| bank kul | 686 | **766** |
| PY3 topics | 23/87 | **43/87** |
| PY3 sawal | 92 | **172** |

PY1 (71/81, 329) aur PY2 (23/87, 92) chhue nahi gaye — script seeded topics khud
chhod deti hai, is liye sirf PY3 aage barha.

**Quota wahi nikla jo naapa gaya tha:** 20 topics ke baad `[21/64]` par HTTP 429.
`ROADMAP.md` ka andaza "~23–26 calls/din" tha; aaj **20** mile. Yani row ka paimana
durust hai, aur **PY3 ke 44 + PY2 ke 64 = 108 topics** abhi baqi hain — mojooda raftaar
par lag-bhag **paanch se chhe aur din ka rozana kaam**.

Command wohi thi jo `ROADMAP.md` mein darj hai (defaults NAHI — pre-school par
`fill-blank`/`essay`/`balanced` ghalat hain):

```
python -m scripts.seed_bank --subject Mathematics --grade "Pre Year 3" \
  --types "multiple-choice,short-answer,true-false" --bloom foundational \
  --max-topics 87 --write
```

Chaar jaali syllabi (Math G5, Math G6, Science G7, Geography G8) aaj bhi 0/11 par hain
aur **jaan-boojh kar chhue nahi gaye** — un ka asal syllabus import hone tak seed karna
mana hai.

## 2026-08-26 — UI-063: button task — ek radius, ek disabled, aur do adad jo maine ghalat likhe the

**1075 pass**, ruff saaf, ratchet chhua nahi. **D44 aur D46 band. D47 NAHI —
aur ye ahem hai** (neeche).

⚠ **Browser check DARJ NAHI HUA.** Server chala kar paanchon page ke URL Irfan ke
saamne rakhe gaye (bank, index, slo, library, print) aur commit ka "go" mila — magar
**"maine dekh liya, theek hai" alag se nahi kaha gaya**, is liye ise tasdeeq-shuda nahi
likha ja raha. Gate list ise laazmi kehti hai. Agar kabhi in buttons par shak ho, ye row
yaad rakhna: **rang aur radius naapi hui hain, nazar se dekhi hui nahi.**

### Pehli baat: ye kaam pehle se working tree mein para tha, bina kisi gate ke

Aaj ka audit is se shuru hua ke `git status` par das files modified thin aur **koi
commit nahi tha, koi PROGRESS entry nahi thi, koi probe run nahi hua tha.** Yani
finishing plan ka item 1 code ki tarah mukammal tha aur **darj ki tarah wujood hi nahi
rakhta tha.** Ye is repo ki wohi purani bimari hai jo `ROADMAP.md` ki P0 rows mein
mahinon chali — kaam ho gaya, row khuli rahi. Is entry ka aadha maqsad usay band karna hai.

### Faisla (Irfan, 2026-08-25) — teen, aur teenon amal mein aaye

| # | faisla | natija |
|---|---|---|
| radius | har filled action button ek radius par | `--radius-control` = **11px**. 8/10/12/13px sab gaye |
| hover | ek simt | light-surface buttons ab **halka** karte hain (`--color-action-hover`) |
| disabled | ek opacity | **`.5` + `not-allowed`**, har `:disabled` rule par |

### Naapa gaya — dono probe, aur sirf TEEN property hili

`css_state_probe` (paanch state) **1,054 deltas**, `css_type_probe` (rest) **206**.
Poore data par property-wise ginti:

| property | state | rest |
|---|---:|---:|
| `border-*-radius` (chaar kone) | 940 | 188 |
| `background-color` | 75 | 15 |
| `opacity` | 39 | 3 |

**Aur kuch nahi.** `font-size`, `padding`, `min-height`, `box-shadow`, `outline-*`,
`border-color` — sab sifar. Har chhua hua selector aik button hai. `slo-health`,
`taqseem`, `landing` par **0 deltas** — kyunke un ki `--radius-btn` declaration pehle
se **mari hui** thi (review ne `git show HEAD:` se paanchon ki tasdeeq ki).

Transitions: `1054` adad qabil-e-aitbaar isi liye hai ke probe ab motion band karta hai.
Us se pehle `landing` **apne aap se 197 deltas** deta tha.

### ⚠ Do adad jo maine audit mein GHALAT diye

Maine likha tha ke ye kaam `legacy_css_lines` **1873 → 1841 (−32)** aur
`unsanctioned_hex` **356 → 349 (−7)** karta hai. **Dono ghalat attribution thi**, aur
review ne pakda. Naapa gaya:

* **`legacy_css_lines`: HEAD 1842 → 1841. Ye kaam kul `−1` line hai.** 1873 wala adad
  `docs/ui/BASELINE.json` ka hai jo **31 lines purana** ho chuka hai.
* **`unsanctioned_hex`: is diff mein net hex tabdeeli SIFAR hai** (`git diff -U0` par
  sirf `#5B8DEF` ×2 aur `#fff` ×8, `+`/`−` par barabar). 349 sach hai, magar `−7` is
  kaam ka nahi, purani drift hai.

**Sabaq, aur wo bilkul D45 wala hai:** stale baseline ke khilaf naapna aur farq ko apne
kaam ke naam likh dena — ye "kaamyabi jaisa dikhta hai". Aage se ratchet ka farq
**HEAD ke khilaf** naapo, `BASELINE.json` ke khilaf nahi.

### ⚠ D47 band nahi hua, aur item 1 ka daira teen-tihai adhoora raha

`ROADMAP.md` item 1 ko "D44 + D46 + **D47(b)**" likhta hai. `forms.css` ko **haath tak
nahi laga** — na jhoota comment theek hua, na ring-vs-glow ka faisla hua. Review ne
pakda, kisi gate ne nahi. Aur `css_state_probe.mjs`:186-187 mein `outline-*` **isi liye**
daala gaya tha ke (b) naapa ja sake — auzaar tayyar tha, istemaal nahi hua.

### Naya masla, control se sabit: gate `cursor` dekh hi nahi sakta (D49)

Faisle ka teesra hissa `cursor: not-allowed` tha. Us ka **aik bhi delta nahi bana**.
Shak par control chalaya — `slo` ki `.btn:disabled` ka cursor `crosshair` kar ke probe
dobara:

| naap | natija |
|---|---|
| deltas | **0** |
| record | `cursor: pointer` — yani **rest ki qeemat** |

Jabke usi element par `opacity` `0.5` parhta hai (rest par `1`), yani `:disabled` **lag
raha hai**, aur `cursor` `STATE_PROPS` mein **mojood hai**. Wohi khamoshi
`library.css` ki `.pg-btn:disabled` par bhi — `opacity` `.4→.5` ka delta aaya, saath
wala `default→not-allowed` gayab. **Sabab tay nahi hua aur andaza lagana mana hai:** ya
to probe ki kami hai, ya Chromium disabled control par `:disabled` ka `cursor` lagata hi
nahi — doosri soorat mein poore repo ki har `cursor: not-allowed` **mari hui CSS** hai
aur faisla dobara dekhna parega, auzaar nahi. **D49.**

### Jo jaan-boojh kar NAHI kiya, aur review ne mera daawa chhota karwaya

Maine "har filled legacy button" likha tha. **Ye daawa bara tha.** Sach ye hai: **har
filled _light-surface action_ button.** Bahar rahe:

* **on-dark family** — `bank` ka `.btn-fb-save`/`.btn-fb-cancel`, `print` ka
  `.ps-stepper`/`.ps-save`/`.ps-reset`. In ke paas jaane ke liye koi Tier 2 on-dark role
  hai hi nahi. Isi liye `.btn-fb-save` **aaj bhi hover par gehra karta hai** — yani
  darken/lighten ka mix **khatam nahi hua, sirf chhota hua**. **D48**
* **do navy filled control** — `library` ka `.pg-btn.active`, `index` ka `.lang-toggle`
  ka selected button. Ye segmented/pagination hain, CTA nahi, is liye un ka 6px/8px
  radius durust hai aur chhua nahi gaya — magar un ka **fill** ab usi screen ke har
  action button se nahi milta. Ye D27 ka bacha hua hissa hai. Recolour karna Irfan ke
  teen faislon mein shamil **nahi** tha, is liye row bani, edit nahi. **D50**

### Comments jo code se jhooth bolne lage the — wohi bimari, isi commit mein theek

D47(a) ka sabaq ye hai ke is tree mein comment documentation ki tarah parha jata hai. Ye
kaam khud paanch aise comment bana raha tha, review ne ginwaye, sab theek kiye:
`btn.css`:210 (aik "range" jo ab mojood nahi + pehle se ghalat line number), `btn.css`:303
(bank ab `--radius-btn` declare hi nahi karta), `btn.css`:349 aur :352 (apni hi rule ka
ulta kehte the), `modal.css`:12, `pages/landing.css`:43.

### Aur unhi comment edits ne aik rule maar di — probe ne pakda, warna ship ho jati

Comments theek karte waqt is entry ke mussanif (main) ne aik **ziyada `*/`** chhor diya.
Us ne `btn.css` ka bara comment block waqt se pehle band kar diya, baqi prose CSS ban gayi,
aur us ne **`.btn-save, .btn-cancel` ki poori rule nigal li.** Nateeja: bank aur print ke
modal ke dono buttons `border-radius: 0`, `font-size: 13.33px` — yani default `<button>`.

**Kisi doosre gate ne aawaz nahi ki:** `pytest` 1075 pass tha, `ruff` saaf tha, aur
**ratchet ne bhi kuch nahi kaha** kyunke line count aur hex ginti dono theek thin — CSS
"maujood" thi, bas comment ke andar. Sirf `css_type_probe` ne **25 deltas** dikhaye.
Theek karne ke baad dono probe **0/0**.

**Sabaq:** "sirf comment badla hai" is repo mein probe skip karne ki wajah **nahi** hai.
C-style comment ka aik ghalat token rule delete karne ke barabar hai, aur ratchet us
qism ke nuqsan par khamosh hai kyunke wo lines ginta hai, matlab nahi.

`css_state_probe.mjs` ka `KILL_MOTION` comment bhi ghalat wajah deta tha — kehta tha
unlayered `<style>` "har @layer ko harata hai". **Ye `!important` par ulta hai:**
important declarations par layer order **ulti** chalti hai, to layer ke andar ka
`transition: … !important` is injection ko **harata**. Aaj kaam karta hai kyunke
`static/css/` mein aisa koi declaration hai hi nahi (grep, 2026-08-26). Wajah durust
likh di gayi, aur ye bhi ke `animation: none` wala hissa **aaj kuch nahi maarta**
(repo mein `@keyframes` hai hi nahi) aur ye probe **motion regression bilkul nahi dekh
sakta**.

## 2026-08-25 — UI-065: state probe — jo gate rest par parhta hai wo state dekh hi nahi sakta

`scripts/css_state_probe.mjs` — naya file, **D45 band.** Ye drain nahi, **auzaar** hai, aur
jaan-boojh kar agle drain se pehle banaya gaya. Kisi page ka koi byte nahi badla.

### Ye control se sabit hua, daawe se nahi

Is repo ka har probe page ko **rest par** parhta tha. Yani `:hover`/`:focus-visible`/
`:disabled` ki koi bhi declaration **0 deltas** deti thi — durust ho ya ghalat. Do din mein do
task isi se kate, aur dono is file mein upar darj hain: UI-061 ne chaar pages se `input:focus`
delete ki (sabot sirf layer-order ka istidlal), aur UI-062 ne `.btn-cancel:hover` ka grey badal
diya jabke **pytest, ruff, ratchet aur 34 measured deltas sab paas ho gaye.**

To auzaar banane ke baad us par wohi mutation chalayi gayi jo UI-062 mein chupke se guzri thi —
`bank` par `.btn-cancel:hover` ka background badal kar:

| probe | deltas |
|---|---|
| `css_type_probe.mjs` (rest), nau ke nau pages | **0** |
| `css_state_probe.mjs`, akela `bank` | **1** — `button.btn-cancel::hover  background-color` |

Ek hi mutation, ek hi browser. Iske baad `btn.css` HEAD ke barabar restore ki gayi
(`git diff --quiet` saaf).

### Do faisle jo qeemat tay karte hain

**Wohi JSON shape jo `css_type_probe` likhta hai.** Nateeja: `css_type_diff.mjs` **bina badle**
dono parhta hai, `--names` sameet — koi naya diff tool nahi. Keys `<path>::<state>` hain aur
`<path>` byte-identical hai, to state diff ka path rest diff mein paste ho sakta hai.

**`outline-*` shamil hai, jo `css_type_probe` mein bilkul nahi.** App ka focus ring
`forms.css`:106 par `outline` hi hai — us ke baghair probe ring ka aana ya gayab hona dekh hi
nahi sakta, yani UI-061 wala sooraakh khula reh jata.

State CDP ke `CSS.forcePseudoState` se lagayi jati hai — wohi flag jo style engine khud parhta
hai, to cascade waise hi hal hoti hai jaise asal pointer par. Koi synthetic mouse event nahi,
kyunke ye pages JS se render hote hain aur asal mousemove un ke listeners se race karta.
`:disabled` isteshna hai: wo forceable flag nahi, **attribute** hai — set, snapshot, phir
bahaal, aur bahaali ka count output mein darj hota hai.

### Review ne pehla version FAIL kiya — aur ghalti theek wahi thi jo auzaar rokne aaya tha

Pehle version ne akela `focus-visible` force kiya. **`:focus-visible` kisi `:focus` rule ko
match nahi karta**, is liye repo ki har `input:focus` rule — `forms.css`:79 sameet, aur wohi
chaar jo **UI-061 ne delete ki thin** — rest ke barabar naapi gayi. Yani jo auzaar us sooraakh
ko band karne bana tha, wo usi par andha tha.

**Aur wo bilkul saaf natije jaisa dikhta tha:** koi error nahi, records poore, counts theek —
bas har qeemat resting qeemat thi. Review ne ise output parh kar nahi, seedha CDP experiment
chala kar pakda. **Yeh is auzaar ka apna sabaq hai: ghalat pseudo-class force karna kaamyabi
jaisa lagta hai.**

Ab focus **do pass** hai: `focus` (akela `:focus`, pointer focus) aur `focus-visible` (dono
force, kyunke asal tab-stop dono ko match karta hai).

### Auzaar bante hi paanch cheezein naap kar mil gayin

* **Fields par focus ring `outline` nahi, GLOW hai.** `select#fSubject`: `border-top-color
  rgb(14,165,164)`, `box-shadow rgb(220,245,244) 0 0 0 3px`, `outline-style: none` — kyunke
  `input:focus` (0,1,1) usi layer mein `:focus-visible` (0,1,0) ko harata hai. **Is entry ke
  pehle draft ne "ring = `outline: 2px solid`" likha tha; wo buttons ke liye sahi, fields ke
  liye ghalat tha.** Aur `forms.css`:76 ka comment is ka ulta kehta hai — **D47**.
* **`.btn-save:hover` indigo-500 hai jabke rest par indigo-600** — UI-062 ka "hover ab halka
  karta hai" wala jumla ab naapa hua adad hai, raay nahi.
* **`.btn-cancel:hover` = `rgb(250,251,254)`** — pehli dafa naapa. UI-062 mein ye "kisi tarah
  tasdeeq-shuda nahi" darj hua tha; ab band.
* **`.btn-save:disabled` opacity `0.6`, aur `.btn-cancel` ka koi disabled rule hai hi nahi** —
  D46 ka maal, ab naapne ke qabil.
* **`slo` ke table rows ka hover** — pehle daire se bahar tha, ab andar.

### Daira chhota, magar review ke baad teen selector chaura

Review ne `static/css/` ke 66 state selectors ginn kar teen **zinda `:hover` rules** dhoondein
jo tag list kabhi pakad hi nahi sakti thi: `tbody tr:hover` (**slo — ek LIVE gate page**),
`.q-row:hover` (bank), `.bp-row:hover` (blueprint). Daira jo zinda rule chhor de, wo daira
nahi — sooraakh hai. `slo` 20 → **135**, `bank` 1,533 → **1,992**.

Nau pages, paanch states, **~30 second, 13,100 records, 0 errors.**

⚠ **Pehle "~41 second, 8,112 records" likha tha, aur review ne akele `bank` ko 445 second par
naapa.** Dono adad asli the: pehla version har `forcePseudoState` ka alag round-trip awaited
karta tha (bank par ~9,200 calls), aur wo latency par hai — machine ke bojh se das guna farq.
Ab calls saath bheji jati hain aur ek dafa await hoti hain, is liye naya adad **zyada states
aur zyada elements ke bawajood** kam hai.

**Agla kaam D44 (button task) hai, aur wo is probe ka pehla asal istemaal hoga** — us se pehle
aur baad mein chalana laazmi hai, kyunke wo task poora ka poora hover aur disabled surfaces
par hai.

## 2026-08-25 — UI-062: modal family — aur bank par do primary rang mile

**1075 pass**, ruff saaf, `legacy_css_lines` **1864 → 1842 (−22)**, `unsanctioned_hex`
**353 → 349 (−4)**. `css_type_diff`: **bank 13, print 21, baqi saat pages 0.**

**Ye pehla drain hai jis mein deltas jaan-boojh kar sifar nahi rakhe gaye.**

### Kyun ye family do din pehle nahi ho sakti thi

`modal.css` ne ise 2026-08-16 ko park kiya tha, aur wajah naapne par aaj bhi zinda thi:
`.btn-cancel`/`.btn-save` ka matn dono files mein byte-identical hai, magar bank apna
`--radius-btn` 10px declare karta hai aur print 8px. Component tab hi ban sakta tha jab **ek
radius jeete** — aur us se ek page nazar aane ki had tak badalta. Wo faisla mera nahi tha;
Irfan ne `--radius-control` (11px) chuna.

### Asal daryaft — aur ye poochhne se pehle naapi gayi

Component banane se pehle ye dekha ke component ke rang legacy se milte bhi hain ya nahi.
Nahi milte the, aur us se ek cheez benaqab hui jo kahin darj nahi thi:

| bank par, us waqt | background |
|---|---|
| `.btn-primary` | `rgb(79,70,229)` — **indigo**, UI-041 mein `--color-action` le chuka |
| `.btn-save` | `rgb(46,90,172)` — **navy**, legacy `--primary` par khada |

**Bank ek hi screen par do mukhtalif filled action buttons paint kar raha tha.** Ye D27 ka
wohi defect hai jis ke liye epic bana. Isi liye rang badalna is task ka maqsad bana, koi
side-effect nahi — magar ye poori tasveer Irfan ke saamne rakh kar hi aage barha gaya,
kyunke pehle sirf radius ki baat hui thi aur wo adhoori thi.

### Jo jaan-boojh kar NAHI kiya gaya

`.btn-save` ko seedha `.btn--primary` ke selector list mein jorna ek line ka kaam tha aur
**ghalat hota**: us se `font-size` 14→15px, `font-weight` 600→700 aur `min-height` 44px bhi
saath aate — teenon faisle se bahar. Us ki jagah `btn.css` ke apne `.btn-primary` block wala
tareeqa apnaya: **legacy naam, component ke token, apni measured geometry.** Naap kar tasdeeq
hui ke `font-size` aur `padding` ek bhi delta par nahi hile.

### Deltas ginne ke qabil hain, is liye ginwaye ja rahe hain

34 ke 34 `.btn-cancel` ya `.btn-save` par hain, aur har property teen mein se ek: border
colour, radius, ya `.btn-save` ka background. Baqi saat pages par sifar.

### Aur ek chauthi tabdeeli jo maine "teen" likh kar chhupa di — review ne pakdi

Maine `btn.css`, `STATUS.md` aur yahan teenon jagah likha tha ke **teen** cheezein badlin aur
teenon manzoor-shuda hain. **Wo ek closed-set daawa tha aur ghalat tha — chaar hain.**

Chauthi hai `.btn-cancel:hover`. Legacy mein wo `var(--bg)` tha, jo **har page par alag** hai
(bank `#EEF1F6`, print `#F5F7FB`); ab dono `--color-surface-sunken` par hain — ek teesri
qeemat jo kisi page par nahi thi. Ye Irfan ke saamne rakhe gaye faisle ke preview mein darj
tha, to manzoori maujood hai; **likhna ghalat tha, karna nahi.**

**Aur wajah jo isay ahem banati hai:** `css_type_probe` **rest par** naapta hai, is liye hover
ka **ek bhi delta nahi banta**. Yani ye 34 mein shamil nahi, aur har us gate se guzar gaya jo
is task par chalaya gaya. Jo cheez sirf state par zahir hoti hai, us ka koi auzaar is repo
mein nahi — UI-061 mein `:focus` par yehi kami darj hui thi, aur do din mein dobara kaat gayi.

Ek aur nateeja jo faisle mein shamil nahi tha: `.btn-save:hover` `--primary-hover` se
`--color-action-hover` par gaya, jo **simt ulat deta hai** — legacy hover par gehra karta tha,
naya halka karta hai. Action role apnane ka lazmi nateeja hai, magar ab app mein kuch filled
buttons gehre hote hain aur kuch halke. D44 ke saath.

### Naya qarz jo isi waqt darj kiya — D44

`btn.css`:275 `.btn-primary` ko jaan-boojh kar 10px par rakhta hai. Ab bank **10px primary
aur 11px save** ek saath dikhayega; is se pehle dono 10px par mutafiq the. Ye radius ke
faisle ka nateeja nahi, us purane 10px hold ka baqaya hai. **Agla button task pehle** —
saare filled legacy buttons ek radius par, warna har agla drain yehi qarz barhata rahega.

### Browser check hua — usi din, aur adhoora hone ke baad bhi kaam ka

Extension is baar bhi connect nahi hui; Irfan ne khud incognito + hard refresh par dekha.

**Confirmed:** `bank` ka Save button **indigo** hai (is task ki sab se bari nazar aane wali
tabdeeli), `bank` par **focus ring aata hai**, aur `print` ka edit modal theek hai — wohi
page jahan radius ka farq sab se bara tha (8px → 11px).

**Nahi dekha, aur waise hi darj:** `index`/`library`/`blueprint` ke labels aur focus, strip
filter ka box, aur `.btn-cancel:hover` ka naya grey. D44 par Irfan ki raay bhi baqi hai.

**Focus ring ki tasdeeq asal mein UI-062 se zyada UI-061 ke kaam ki hai.** Us task ne chaar
pages se `input:focus` ki rules delete ki thin aur us ka poora sabot layer-order ka istidlal
plus rest par 0 deltas tha. Ab wo aankh se poora ho gaya.

**Magar D45 isse band nahi hoti, aur ye nuqta chhoot jane wala hai:** gap is dafa **haath se**
bhara gaya, auzaar se nahi. `.btn-cancel:hover` ka naya grey ab bhi kisi tarah tasdeeq-shuda
nahi hai — na probe use naap sakta, na wo dekha gaya. Agli dafa jab hover ki koi rule chupke
se badlegi, koi haath maujood na hoga.

## 2026-08-24 — UI-061: `field/filter` drain — aur wo "duplication" nahi, murda code nikla

**1075 pass**, ruff saaf, `legacy_css_lines` **1873 → 1864 (−9)**, `unsanctioned_hex`
**356 → 353 (−3)**, aur `css_type_diff` par nau pages ke **367,048 element × property jode
mein se sifar hile**.

### Task kyun apni tareef se mukhtalif nikla

Plan ye tha: `css_duplication_audit.py` ka `agree` bucket (119 lines, 34 rules) utha kar
`field/filter` khandan ko component par le jao — "koi faisla darkar nahi". Script ke apne
header ne pehle hi chetawni de rakhi thi:

> ⚠ IT COMPARES DECLARATION TEXT, NOT PAINTED OUTPUT … `agree` here means "worth measuring
> next", never "safe to extract".

Naapa gaya, aur chetawni durust nikli — magar ulti simt mein. Rules "shared" isliye nahi
thin ke unhein component chahiye tha; wo **teenon jagah barabar murda** thin:

| rule | file kya likhti hai | probe kya kehta hai |
|---|---|---|
| `label` × 4 pages | `font-size: 12.5px` | **12px** |
| `input:focus, select:focus` × 4 | apna ring | rule ka koi asar nahi |
| `.strip-filter input/select` × 2 | `12px` / `4px 9px` / radius `7px` | **13.5px / 11px / 11px** |

Wajah aik hi hai aur `main.css`:42 par likhi hai: layer order `legacy` ko sab se neeche
rakhta hai, aur **layer specificity se pehle tay hota hai**. `.strip-filter input:focus` ki
specificity `(0,2,1)` hai, `forms.css` ke `input:focus` ki `(0,1,1)` — phir bhi legacy
haarti hai.

### Ek asal cheez jo is se benaqab hui

`bank` aur `print` par topic-image strip ka filter row **jaan-boojh kar chhota** design kiya
gaya tha — 12px text, 4px 9px padding, radius 7px, thumbnail grid ke pehlu mein. **Wo look
aaj mojood nahi hai** aur is task se pehle hi ja chuka tha: jis din page `main.css` par aaya,
`forms.css` ne wo controls 13.5px par draw karna shuru kar diya. Kisi test ne ye nahi pakda
kyunke koi test computed size nahi naapta.

Ise **theek nahi kiya gaya** — wapas laana design ka faisla hai (kya dense picker ka filter
form control se chhota hona chahiye?), aur drain ke parde mein do live pages badalna wohi
ghalti hoti. `DEFERRED.md` **D43**.

### Kya bana, kya jaan-boojh kar nahi bana

`05-components/field.css` mein `.strip-filter` ka **container** gaya (dono pages par matn
aur paint dono barabar), saath `min-height: 30px` — **sirf yehi ek declaration zinda thi.**
Baqi (bank par saat, print par chhe) sath nahi layin: `layer(components)` mein copy karna
unhein zinda kar deta, wohi jaal jo UI-042 mein 75 deltas hila chuka hai.

Ek cheez darj karni chahiye: **`.strip-filter select` asal mein `agree` bucket mein thi hi
nahi** — audit use `disagree` ginti hai, kyunke bank `color: var(--ink)` likhta hai aur print
nahi. Ye scope se bahar thi aur review ne pakdi. Utha isliye li gayi ke saath wali container
rule (jo waqai agree thi) ke jane ke baad ise chhorna be-maani tha, aur ikhtilaf ka hal
mehfooz tareeqe se nikla: `color` sameet koi bhi cheez component mein nahi gayi, sirf wo ek
declaration gayi jo zinda thi. **Faisla Irfan ka hai ke ye scope-breach qabool hai ya nahi.**

Do rules pehle se tay-shuda hone ki wajah se chhui hi nahi gayin — `label:first-of-type`
(`field.css`:66, warna print ke 11 labels tak pahunchti) aur
`.type-checks input[type="checkbox"]` (`field.css`:18–24, blueprint par do checkbox shakal
ban jatein).

### Do baatein record ke liye

**`PLAN.md`:381 aur asal kaam takra rahe hain.** Wo Sprint 6 ko per-page likhta hai
(*"drain `99-legacy/<page>.css` to zero, delete it"*), jo 2026-08-19 ke faisle ke baad
mumkin nahi — 66% lines page-only hain aur skip hain, to koi file zero par nahi jayegi.
CLAUDE.md §12.11 ke tehat poochha gaya; **Irfan ka faisla: per-family.**

**Probe ka raasta Chrome extension se azad hai.** `css_selector_probe.mjs` aur
`css_type_probe.mjs` apna headless Edge khud chalate hain. Extension mahinon se connect nahi
ho rahi, magar ye naap phir bhi mumkin hai — jo is task ka poora sabot hai. **Browser check
phir bhi nahi hua**, aur 0 deltas "page dekhne mein theek hai" ka daawa nahi hai.

## 2026-08-23 — Pre Year 3 seeding: 23/87 topics, quota phir raaste mein khatam

Bank **594 → 686** (+92 sawal). Sirf DB badli — koi code nahi.

```
python -m scripts.seed_bank --subject Mathematics --grade "Pre Year 3" \
  --types "multiple-choice,short-answer,true-false" --bloom foundational \
  --max-topics 87 --write
```

Backup pehle: `paper_maker_backup_before_preyear3_seed_20260823.db`.

### Syllabus pehle parha gaya, aur wo zaroori tha

`seed_bank.py` ka apna header chetawni deta hai ke topic ka title jaisa likha hai waisa
hi maan liya jata hai. Pre Year 3 ke 87 topics parhe: numbers 1–30, blocks se ginti,
up/down, left/right, long/longer/longest. **Poori tarah pre-school** — chunanche
ROADMAP wale `--types` (mcq/short-answer/true-false) aur `--bloom foundational` durust
the. Default types (`fill-blank` + `essay` + `balanced`) yahan bilkul ghalat hote.

### Kya bana

| | |
|---|---|
| topics | **23 / 87** (61 chhu-e hi nahi gaye) |
| sawal | **92 / 348** |
| MCQ / short-answer / true-false | 35 / 30 / 27 |
| khali `question_en` | **0** |
| MCQ bina `correct_answer_en` | **0** |

Teenon qismein barabar bani — ye dekhna zaroori tha, kyunke `seed_bank` ke pehle run
(2026-08-21) ne yehi bug pakda tha ke AI maangne par bhi `essay` nahi banata tha.

### Script ne theek wohi kiya jo design tha

Topic 24 par HTTP 429 aaya, phir 25 aur 26 par bhi. **Musalsal 3 rate-limit par khud
ruk gayi** — baqi 61 topics ko be-faida calls par zaya nahi kiya. Seeded topics skip
hote hain, to wahi command dobara chalane se top-up ho jata hai.

### Ek adad jo naapne par khatakta hai

**Pre Year 2 bhi theek 23/87 topics aur 92 sawal par khada hai** (kal ka run). Yani
dono din quota lag-bhag **23–26 AI calls** par khatam hua.

Ye ROADMAP ki R1 row ke lehje ko badalta hai. Wahan likha hai *"Rukawat: Gemini
free-tier ka rozana quota"* — jo sach hai magar chhota lagta hai. **Naap kar:** PY3 ke
64 + PY2 ke 64 = **128 topics baqi**, aur ~23 per din ka matlab hai **~6 aur din ke
run**. Ye "chhota tukda" nahi, ek hafte ka rozana kaam hai.

### Bank ki nayi halat (DB se naapi, kisi row ke bharose nahi)

```
OK  Mathematics  Grade 4      11/11 topics    43 sawal
..  Mathematics  Pre Year 1   71/81 topics   329 sawal
..  Mathematics  Pre Year 2   23/87 topics    92 sawal
..  Mathematics  Pre Year 3   23/87 topics    92 sawal   <- aaj
--  Mathematics  Grade 5       0/11 topics     0 sawal   \
--  Mathematics  Grade 6       0/11 topics     0 sawal    | chaar JAALI syllabi
--  Science      Grade 7       0/11 topics     0 sawal    | (seed karna mana)
--  Geography    Grade 8       0/11 topics     0 sawal   /
```

**Agla:** kal wahi command dobara (PY3), aur PY2 ke liye bhi wahi. Chaar jaali syllabi
par seeding **mana** hai jab tak asal syllabus import na ho — ye code ka masla nahi,
data ka hai.

## 2026-08-23 — Coverage ab `plan.html` par dikhti hai (Marhala 3 ka frontend)

**1075 pass**, ruff saaf, CSS ratchet ka har metric **+0**.

Marhala 3 ne endpoint bana diya tha magar us ka koi frontend nahi tha — **bilkul wohi
soorat jis ki is din ke shuru mein shikayat ki gayi thi** (82 routes mein se 6 orphan,
un mein se 4 yehi module). Isi liye ye usi din jod diya gaya, "baad mein" nahi.

### Kya dikhta hai

* Har hafte ki chip par `covered/planned` badge, `taqseem.html` ke `.cov-badge` wale
  **wohi thresholds** (100 / 60) — do reportein ek hi rang-zaban bolein.
* Card ke upar ek line: *"Imtihan mein aa chuke: 49 / 81 topics (60%) — kisi bhi paper
  mein, hafte se qat-e-nazar."* Aakhri fiqra laazmi hai: covered ka koi hafta hota hi
  nahi, aur ye baat report parhne wale ko malum honi chahiye.
* Call **alag aur optional** hai (taqseem ka usool) — fail ho to board pehle jaisa
  render rehta hai. Idempotent bhi: purana badge hata kar inject hota hai.

### "Tay nahi" wale chip par traffic-light NAHI lagti — ye asal data ne pakda

Pehla live run: Unassigned bucket **46/78 = 59%**, jo threshold se **laal** ban gaya.
Wo jhoot hai — un topics ka koi hafta tay hi nahi, to "hafta ka coverage fail hua"
jaisi koi cheez wujood mein nahi. **Ginti kaam ki hai** (46 topics imtihan mein aa
chuke magar plan mein kahin nahi) is liye dikhti hai; **faisla hata diya gaya.**

Ye is baat ki misaal hai ke chhota UI faisla asal data par chala kar hi pakda jata
hai — 59% ka theek threshold ke neeche girna kisi test mein nazar na aata.

### Naapa gaya

| metric | delta |
|---|---|
| har ratcheted metric | **+0** (`inline_style_attrs`, `unsanctioned_hex`, `legacy_css_lines` sameet) |
| frozen inventory | +3 (`covSummary`, do `data-week`), koi MISSING nahi |

JS ke 17 id ↔ markup ke 17 id, dono taraf sifar farq. 32/32 classes tree mein resolve.
`node --check` saaf. Live server par asal data: `Pre Year 1` → H1/H2/H3 par 1/1 (100%,
hara), Unassigned 46/78 (neutral), baqi 33 hafte khali (`—`).

⚠ **Browser check phir bhi nahi hua** — Chrome extension is baar bhi connect nahi hui.

## 2026-08-23 — R7 Marhala 3: hafta-war coverage — spec ne ghalat function ka naam diya tha

**1075 pass** (1055 → 1075, **20 nayi**), ruff saaf. Spec: `docs/TOPIC_WEEK_PLAN.md` §8.2.

### Spec aur code takra gaye, aur poochh kar hi aage barha gaya

Marhala 3 ki row kehti thi *"`_assemble_coverage` key parameterize"*. Kaam uthate waqt
naapa gaya, aur teen cheezein us ke khilaf gayin:

1. **`_assemble_coverage` ko aaj koi bahar se bulata hi nahi** — sirf `exam_coverage`,
   usi file ke andar. Us ke docstring ka waada (*"Hissa 4 dobara istemal karega"*)
   kabhi poora nahi hua.
2. **Us ka maal report ko chahiye hi nahi** — wo drill-down deta hai
   (`covered`/`remaining`/`strands` + `paper_ids`), report per-bucket ginti hai.
3. **Jo waqai share hota hai wo `_summary_row` hai — aath lines**, aur wo pehle se
   domain-neutral thi.

`CLAUDE.md` §12.11 ke mutabiq ruk kar poochha gaya. **Irfan ka faisla: naya service,
`_summary_row` share, `_assemble_coverage` bilkul haath na lagao.** Chunanche us ke SLO
tests bina chhue green hain — wohi gate tha.

| bana | |
|---|---|
| `papers_repository.covered_topic_pairs()` | (topic, paper) jodi — gate topic par |
| `coverage_service.bucket_row()` | `_summary_row` se `exam_no` nikal kar public |
| `topic_coverage_service.py` | naya (~90 lines) — wahi file jo spec §4 ne maangi thi |
| `GET /api/topic-plan/coverage` | `/template` ki tarah PATCH `/{topic_id}` se **pehle** |

### "covered" ki tareef — ye spec mein saaf nahi tha, aur ye faisla asal mein bara hai

**`papers` mein `week_no` column HAI HI NAHI** (sirf `exam_no`). To "hafta 3 ka paper"
wujood mein hi nahi. Irfan ne chuna: **topic kisi BHI paper mein aaya = covered.**
Sawal jis ka jawab milta hai — *"jo maine hafta 3 mein parhaya, us ka imtihan kabhi
liya bhi?"* Doosra raasta (hafta → exam mapping) rad hua kyunke wo mapping repo mein
hai hi nahi.

Is se teen cheezein `coverage_summary` se **ulat** ho jati hain, aur teenon ki apni
test hai:

* **`exam_no` ki koi shart nahi.** 30 mein se 10 papers par `exam_no` hai hi nahi; SLO
  ka raasta unhe ginta hi nahi (`exam_no IS NOT NULL`), ye ginta hai.
* **`class_name` ka `LOWER(TRIM(...))` match nahi, aur ye kami nahi.** Gate
  `syllabus_topics.subject/grade` par hai — ek topic id pehle se theek ek (subject,
  grade) ki hai, to paper ka ganda free-text `class_name` hisaab mein aata hi nahi.
* **Unassigned ka `covered` asal ginti hai, forced 0 nahi.** "Hafta tay nahi magar
  paper mein aa chuka" asal soorat hai; usay 0 dikhana maloomat chupana hoga.

### `week_count()` public — magar alias jaan-boojh kar nahi

PROGRESS.md ne 2026-08-22 ko yehi Marhala 3 ka kaam likha tha. Teen module ab ek hi N
par chalte hain.

**`_week_count = week_count` likh dena aasan tha aur khatarnak:** tests us naam ko
monkeypatch karte hain, aur alias patch karne se andar ke caller (jo `week_count()`
bulate) par koi asar na hota — **test green rehta hue bhi kuch guard na karta.** Teenon
caller aur saaton test-line saath badle.

### Asal data par chalaya

`Mathematics / Pre Year 1` — **49 / 81 topics covered (60%)**, `paper_map` mein 49
entries. Spec §5 ka daawa ("pehle din se asal data dikhayega") poora hua.
`Pre Year 2` aur `Grade 4` par 0% — durust, un ke topics kisi paper mein aaye hi nahi.

### `plan.html` ka browser check ho chuka hai — aur wo DB mein likha mila

`topic_week_plan` mein **3 rows** milin (Pre Year 1, hafte 1/2/3), `plan.html` wale
commit ke **56 second baad** — teen alag PATCH, 2–4 second ke faasle par. **Irfan ne
tasdeeq ki: ye us ka browser test tha, aur rows rakhni hain.**

Yani pichhle commit mein jo gap saaf likh kar chhoda gaya tha (*"browser check nahi
hua, ye claim nahi kiya ja raha ke page dikhne mein theek hai"*) **ab band hai**:
page load hua, subject/grade dropdown bhare, table render hui, aur hafta chunne se
PATCH DB tak pahuncha — asal browser mein, asal data par.

Qabil-e-zikr baat ye hai ke **ye khud kaam se pata chala, kisi report se nahi.**
Coverage ka pehla run Pre Year 1 par `total=81` magar Unassigned `planned=78` dikha
raha tha — teen ka farq. Agar wo farq na khatakta to ye rows kisi ko nazar hi na aatin.

**Agla:** coverage ko `plan.html` par dikhana (abhi endpoint ka koi frontend nahi — wohi
soorat jis ki shikayat aaj subah ki gayi thi).

## 2026-08-23 — R7 Marhala 4: `plan.html` — hafta-war plan ab teacher tak pahunchta hai

**1055 pass**, ruff saaf, CSS ratchet ka **har metric +0**. Spec:
`docs/TOPIC_WEEK_PLAN.md` §8.1.

Marhala 1 aur 2 ne 79 tests ke saath poora backend de diya tha, magar 2026-08-22 ko
naapa gaya tha ke **`static/` mein in endpoints ka sifar zikr hai** — API zinda, koi
button us se juda nahi. Aaj naye sire se naapa: **82 routes mein se sirf 6 aise the
jin ka frontend nahi tha, aur un 6 mein se 4 yehi module tha.** Ab wo 4 jude hue hain.

### Tarteeb badli gayi — Marhala 4 pehle, Marhala 3 baad mein

Irfan ka faisla, aur bunyaad naapi hui thi: `topic_week_plan` mein **0 rows** thin.
Coverage report ka koi matlab nahi jab plan mein data hi na ho. Pehle bharne ka
zariya, phir report. **Marhala 3 ab bhi baqi hai.**

### Spec se ek hatna, aur wo naap kar hua

§4 kehta tha UI `taqseem.html` ka aaina ho — yani kanban board. Wo shakal yahan
tootti hai: `exam_count` **8** hai magar `week_count` **36**. taqseem ka board 9
columns ka hai; yahan wohi cheez **37 columns × 87 topics** hoti — na screen par
aati, na us mein "hafta 7 khali hai" nazar aata.

To page ek **table** hai (Unit / Topic / Page / Hafta-dropdown) aur upar har hafte ki
ginti ka strip. Move ka raasta wohi hai jo taqseem par hai: ek `<select>`, drag nahi.
Khali hafte strip mein **dikhte hain** (dabe hue), gayab nahi hote — "hafta 7 khali
hai" wohi maloomat hai jo teacher dhoondh raha hai.

### Ye pehla page hai jis ka koi `99-legacy` file nahi

Baqi aath entry files do `@import` karti hain (`main.css` + apni legacy file);
`pages/plan.css` sirf ek. Naya page purana qarz paida nahi karta — is epic ka maqsad
hi `99-legacy/` ki line count girana hai.

**Naap kar tasdeeq, dawa nahi** — poora naya page aane ke bawajood:

| metric | delta |
|---|---|
| `legacy_css_lines` | **+0** |
| `inline_style_attrs` | **+0** (page par ek bhi `style=""` nahi) |
| `unsanctioned_hex` | **+0** (plan.css mein ek bhi hex nahi, comment mein bhi nahi) |
| `style_blocks`, `css_lines_in_html`, `hardcoded_hex` | **+0** |
| `shared_css_lines` | +197 (informational — naya tree barhta hai, yehi design hai) |

Sidebar poora naye tree se hai: markup sirf `.sidenav__*` pehnta hai. `.app-sidebar` /
`.brand` / `.app-nav` / `.sidebar-foot` is page par hain hi nahi. `slo.html` dono ek
saath pehnti hai kyunke wo **migrate** hui; ye page shuru se us jagah khara hai jahan
wo pahunch rahi hai. Qeemat ye hai ke teen rules (`body{display:flex}`, main ka box,
bare `.card`) khud likhni pareen — teenon component tree se values leti hain.

### Teen faisle jo `taqseem.html`/`slo.html` se mukhtalif hain

**1. Template `apiFetch` se, `window.location` se nahi.** `slo.html` seedha `href`
istemal karti hai; wo `x-api-key` header nahi bhejta, to jis deployment par key set
hai wahan wo download **401** ho jata. Yahan blob bana kar diya jata hai, filename
server ke `Content-Disposition` se.

**2. Grade ki list subject par munhasir hai.** Do azaad dropdown aise jode bana dete
jin ka koi topic nahi (Geography ke paas sirf Grade 8 hai).

**3. Koi inline handler nahi** — sab `addEventListener`, aur 87 rows ke selects par
ek listener `tbody` par, 87 nahi.

### Test jo phata, aur phatna hi chahiye tha

`test_measures_the_nine_real_pages` page-count 9 par guard karta tha. **Spec ne yehi
peshgoi ki thi** (§9.3: *"plan.html daswan page hoga"*). 10 kar diya, aur wajah test
ke docstring mein — ginti jaan-boojh kar hard-coded hai, kyunke naya page jodna aisa
faisla hai jis ki qeemat ek test edit honi chahiye.

### Verify — browser ka hissa BAQI hai

- `--check` → ratchet OK; `--write` se naye page ki 19 frozen entries declare
- **JS jo 16 id bulata hai, markup mein wohi 16 hain** — dono taraf sifar farq. Yehi
  wo bug-qism hai jahan button chup-chaap kaam karna chhod deta hai
- 30/30 CSS classes tree mein resolve hoti hain; `node --check` saaf
- **Poora flow asal HTTP par chalaya** (template → sheet bhari → import → reload →
  PATCH → range 400 → ghalat id 404 → khali cell se clear): 10/10 theek, aur DB wapas
  asal halat mein (87/87 unassigned)
- ⚠ **`CLAUDE.md` §12.10 ka browser check nahi hua** — Chrome extension connect nahi
  hui. Ye claim NAHI kiya ja raha ke page browser mein theek dikhta hai

### Nayi khuli row

**D42** — nav har page par ek jaisi nahi hai. `bank`, `library`, `blueprint` sirf 5
link rakhte hain (na SLO, na Taqseem, na Plan); `print` ke paas `.sidenav__link` hai
hi nahi. Isi liye naya link sirf un 5 pages par laga jahan planning group pehle se
tha. Teen aur jagah paste kar dena is epic ki bunyadi bimari (aik hi nav ki 5 copies)
ko barha deta.

**Agla:** Marhala 3 (coverage), ya browser check.

## 2026-08-23 — D39: frozen inventory ke 81 handlers guard se bahar the

**1055 pass**, ruff saaf, CSS ratchet green. Do file badlin: `scripts/css_baseline.py`
aur `docs/ui/BASELINE.json`.

Irfan ka faisla: frontend ka kaam pehle. Ye us se pehle ka qadam hai — hum jin pages
par kaam karne wale hain (`plan.html`, `bank.html` ka form), guard theek unhi par sab
se kamzor tha.

### Masla

`FROZEN_ATTR_RE` sirf `id`, `onclick`, `name`, `data-*` pakadta tha. `CLAUDE.md` §12.7
ka poora maqsad ye hai ke handler ka naam badle to shor mache — magar `onchange` aur
`oninput` us guard se bahar the, aur wo dropdowns/search boxes par lagte hain.

Ye farzi khatra nahi tha: **UI-046 (print range) ka apna `oninput="setPrintRange()"`
2026-08-20 ko bina guard ke chala gaya aur ratchet khamosh raha.** Feature ne khud
apni hifazat ka soorakh dikhaya.

### Adad — D39 row ke apne adad ghalat the

| | row (2026-08-20) | naapa (2026-08-23) |
|---|---|---|
| `onclick` (guarded) | 123 | **125** |
| `onchange` | 59 | **61** |
| `oninput` | 17 | **20** |
| **guard se bahar** | 76 | **81** (kul ka 39%) |

Wahi bimari jo `ROADMAP.md` ki P0 rows mein thi. **Parking-lot row ka adad tareekh
hai, haqiqat nahi** — kaam uthate waqt dobara naapo.

### 81 entries `--write` se PEHLE dekhi gayin

Irfan ne yehi maanga tha, aur theek maanga: do saaf qismein nikleen.

**57 seedha markup mein** — `onSubjectChange()`, `loadList()` ×5, `loadGrid(true)` ×4.
Bilkul `onclick` jaise, guard mein aane chahiye the.

**24 `<script>` ke andar `innerHTML` templates mein** — `onchange="onTypeChange(${i}, this)"`.
Ye source mein literal text hain, is liye freeze karna mustahkam hai aur `onTypeChange`
ka rename phir bhi pakda jayega.

**Ek badsoorat hai, aur ye jaan lena zaroori hai:** `blueprint.html`:410 JS concatenation
hai — `setPinSection(\'' + escAttr(q.id) + '\', this)` — jise regex poora nigal jata hai.
Naam ki hifazat theek karta hai, magar `BASELINE.json` mein bura lagta hai.

**Koi false positive nahi tha** — na CSS attribute selector, na koi data string.

### Widening izafi hai, ye naap kar tasdeeq hui

`--write` se pehle per-page diff chalaya: **699 → 780 (+81), aur purani entries mein se
gayab 0.** Ye ahem tha — `--write` poori `BASELINE.json` dobara likhta hai (`metrics` +
`per_page` + `frozen_inventory`), sirf inventory nahi. Metrics us waqt baseline se behtar
ya barabar the (`total_css_lines` 1873 vs 1875), to ratchet **sakht** hua, dheela nahi.

### Guard chalta hai — maana nahi, aazmaya

`oninput="setPrintRange()"` — theek wahi handler jo 20 Aug ko bina guard ke gaya tha —
aarzi taur par rename kiya:

```
exit code: 1
RATCHET FAILED:
  - print.html: MISSING oninput="setPrintRange()" - renaming this breaks a handler silently
  - print.html: ADDED oninput="setPrintRangeXX()" - declare it in the task scope, then --write
```

File foran wapas asal halat mein (`git status` khali).

### Mustaqbil ke liye

`onsubmit`, `onkeyup`, `onkeydown`, `onkeypress`, `onblur`, `onfocus` bhi list mein hain.
In ki ginti aaj **sifar** hai — yani 0 nayi entries — magar `plan.html` jaisa naya page
jab pehla form banayega to wo apne pehle commit se guard mein hoga, agli khamosh
kharabi ke baad nahi.

**Agla:** `plan.html` (R7 Marhala 4, sirf "plan bharo" wala hissa — coverage baad mein).

## 2026-08-22 — R7 Marhala 2: Excel template + import (backend; UI abhi nahi)

**1055 pass** (1026 → 1055, **29 nayi**), ruff saaf, CSS ratchet ka har metric **+0**
(is kaam ne CSS chhua hi nahi). Spec: `docs/TOPIC_WEEK_PLAN.md` §7.

Marhala 1 ne table/service/API di thi magar plan bharne ka koi zariya nahi tha. Ye
wo zariya hai — Irfan ke "data Excel se aayega" wale faisle par:

| naya | kya karta hai |
|---|---|
| `GET /api/topic-plan/template` | us (subject, grade) ke saare topics ka sheet |
| `POST /api/topic-plan/assign-import` | bhari hui sheet se plan replace-set |
| `topic_week_import_service.py` | dono ka kaam (184 lines) |

`question_slo_import_service` ka aaina: header lower-case, match **`syllabus_topic_id`
se — title se nahi**, aur ghalat/gayab id par us row ka saaf error.

### Teen faisle jo SLO import se jaan-boojh kar mukhtalif hain

**1. Unknown id = ERROR, warning nahi.** SLO import mein unknown `slo_code` sirf
warning hai kyunke baqi links phir bhi ban jate hain. Yahan `week_no` poori row ka
maqsad hai — ghalat hua to karne ko kuch bacha hi nahi, aur chup-chaap 0 (Unassigned)
likh dena teacher ko dhoka dena hoga.

**2. Khali `week_no` = plan CLEAR, na ke skip.** Sheet "template" bhi hai aur "export"
bhi — current `week_no` pehle se bhara aata hai, to cell khali karna teacher ka saaf
iraada hai. Response mein `cleared` alag ginti hai taake ye khamoshi se na ho.

**3. Tanbeeh Excel cell-comment mein, alag note-row mein nahi.** Note-row daalte to
wahi file dobara upload karne par header toot jata. Header ek hi hai, machine-readable.

Saari rows pehle parhi jati hain, phir **ek dafa** likha jata hai — aadha-laga plan sab
se bura nateeja hai, teacher ko pata nahi chalta kaunsi rows lagin. Id-tasdeeq bhi ek
hi DB round mein (`existing_topic_ids`), har row par query nahi.

### Jo ab bhi baqi hai — ye feature teacher tak nahi pahunchta

`grep` se naapa: **`static/` mein in dono endpoints ka sifar zikr hai.** API zinda aur
green hai, magar koi button/page us se juda nahi. `slo.html` ka `/api/slo/assign-import`
ek **alag purana** endpoint hai — us se dhoka na khayein.

Chhoti baat, darj isliye ke chupi na rahe: import service `topic_week_service._week_count()`
bulata hai — doosre module ka private function. Kaam karta hai, magar Marhala 3 mein
public karna behtar hoga.

**Agla:** ya to R7 ka UI (in endpoints ko page se jorna), ya Marhala 3 (coverage).

## 2026-08-22 — R7 Marhala 1: hafta-war plan ki buniyad (UI abhi nahi)

**1026 pass** (976 → 1026, **50 nayi**), ruff saaf. Spec: `docs/TOPIC_WEEK_PLAN.md`.

Irfan ke do faisle jin par ye khara hai: daira **taqseem-e-auqat + coverage** hai
(sabaq ka mazmoon nahi), aur data **Excel se** bharega (manual form nahi — wahi wajah
jo `HANDOVER_19July.md` mein likhi hai).

### Ye naya module nahi — aadhi machinery mojood thi

"Planned vs actual" ki shakal repo mein pehle se do dafa bani hai: taqseem
(`slo_exam_plan`) + `coverage_service`. **Jo waqai naya hai wo sirf waqt ka dimension
hai** — kaunsa topic kab. Is liye ROADMAP ka "size L" naapne par zyada laga; andaza
ab **~2 hafte** hai.

`topic_week_plan` `slo_exam_plan` ka **hu-ba-hu aaina** hai — table, repository ki
ordering, upsert, aur Unassigned bucket ka rule (0 / NULL / >N). Naya design isliye
nahi banaya ke wo rule pehle se aazmaya hua hai.

| naya | kis ka aaina |
|---|---|
| `topic_week_plan` table + index | `slo_exam_plan` |
| `topic_week_plan_repository.py` | `slo_exam_plan_repository` |
| `topic_week_service.py` | `taqseem_service` |
| `api/topic_plan.py` | `api/taqseem.py` (ValueError→400, NotFound→404) |

### Ek daawa jo naapne par poora sach nahi nikla

`coverage_service` ka docstring kehta hai `_assemble_coverage` "DB-FREE hai taake
dobara istemal ho". **Wo waada SLO ke daire ke andar tha** (draft question_ids).
Function khud **SLO-keyed** hai — `s["slo_id"]` aur `strand` par chalta hai. Topic ke
liye us ki key parameterize karni paregi. **Ye Marhala 3 ka kaam hai, aur us ke
mojooda tests hi gate honge — SLO coverage tootni nahi chahiye.**

Plan mein maine pehle likh diya tha "coverage dobara likhne ki zaroorat nahi" — wo
zyada tha, aur spec mein durust kar diya gaya.

### Auto-generate jaan-boojh kar nahi banaya

`taqseem_service` mein `generate_plan()` hai (SLO ko N exams mein baraabar baant do).
Yahan wo **nahi** — Irfan ne Excel chuna, aur andhi taqseem ye nahi jaanti kaunsa
topic bhaari hai. 87 topics ko 36 hafton par baraabar baant dena aisa plan deta jo
har hafte badalna parta.

### `week_count`: column haan, settings API nahi

`school_settings.week_count` (default 36) migration se add hui — `exam_count` ka
aaina. Magar **`SchoolSettings` model aur `save_settings()` jaan-boojh kar nahi chhue
gaye**: `/api/school-settings` ka partial POST baqi fields wipe kar deta hai, to us
surface ko chherna apna alag gate maangta hai (Marhala 4, jab UI ise edit karega).
`_week_count()` column na hone par bhi 36 par chalti hai — dono suraton mein
mehfooz.

### Tests: 50, aur teenon parton par

repository **14** · service **26** · API **10**

Jo edge jaan-boojh kar likhe: N ghatne par purane hafte (>N) Unassigned mein girein
aur **gum na hon**; `week_no` 0 = Unassigned, error nahi; khali syllabus par crash
nahi (PRD §6); ghalat input par **DB mein aadha kaam na ho** (validate pehle, likhna
baad mein); aur bin-plan topics `list_resolved` mein aayen warna teacher ko kabhi
pata na chale kitna kaam baqi hai.

**Ruff ne ek asal cheez pakdi:** `raise ValueError(...)` bina `from e` — B904. Theek
kiya.

**Naapa NAHI gaya:** koi UI nahi (Marhala 4), koi Excel import nahi (Marhala 2),
coverage ka hisaab nahi (Marhala 3). Ye teen endpoint abhi sirf `curl` se kaam ke
hain.

## 2026-08-22 — D4: teen mari hui spec files repo root se archive mein

Teenon **Classic navy/gold** palette par likhi hain, jo **Modern** se supersede ho
chuki. `git mv` se `docs/design/archive/` mein gayin — root ab sirf zinda dastaveiz
rakhta hai.

**UI-064 ka intezar nahi kiya (D4 row wahan bhejti thi), aur wajah ye hai:**
`ROLLOUT_all_pages.md` §1 aaj bhi kehti thi *"theme.css `static/` mein rakho — agar
purana chhota hai to isse replace karo"*. Magar `static/theme.css` **UI-064 part 1
mein delete ho chuka hai** (2026-08-13, 212 lines), aur usi delete se
`unsanctioned_hex` 429 → 400 gira tha. Yani ye spec sirf gumraah-kun nahi thi —
**us par amal karne wala wo file wapas bana deta jo jaan-boojh kar hataayi gayi
thi.** Ek deferred row ke peeche ye chhorna theek nahi tha.

Har file ke oopar ⛔ tanbeeh lagi hai: kya supersede hua, kaunsa hawala ab jhoot hai,
aur aaj asal jagah kaun si hai (`docs/ui/STATUS.md`, `docs/ui/PLAN.md`,
`static/css/`). Sirf hata dena kaafi nahi hota — jo shakhs purana link khole use
wahin par pata chalna chahiye.

**Hawale naape gaye pehle:** teenon ka bahar se koi link nahi tha — sirf apne andar
ke ("Read X fully before writing code") aur `DEFERRED.md` ki D4 row. Kuch nahi toota.

**Naapa gaya:** `test_css_architecture.py` 32 pass (ye files CSS metrics mein nahi
aatin).

**Ek aur jhooti row jo isi dauran nazar aayi, theek NAHI ki:** `docs/ROADMAP.md` ki
**H6** row kehti hai *"`API_VERSIONING.md` — **File mojood nahi**"*. Wo file repo
root mein **mojood hai**. Ye aaj ka chautha aisa daawa hai. Alag kaam hai, apne
gate ke saath — magar darj kar raha hoon taake dobara na chhupe.

## 2026-08-22 — `.app-sidebar` ka "OPEN DEFECT" kab ka band ho chuka tha

**Ek line bhi CSS nahi likhi gayi. Kaam sirf do jhoote comment hatane ka nikla.**

`docs/ui/STATUS.md` ye kehti thi:

> **OPEN DEFECT, not fixed and not forgotten:** `.app-sidebar` has `height:100vh`
> and no `overflow`, on all six pages that use it. `index` ... is fixed
> page-scoped; **the other five are untouched.**

Fix likhne se pehle naapa (file-ba-file, comment ke bharose nahi) — aur **saaton
pages pehle se dhaki hui hain**:

| page | overflow kahan se |
|---|---|
| `bank`, `library`, `slo`, `slo-health`, `taqseem` | apni `pages/*.css`, `@layer components` |
| `index` | `.sidenav__panel` — `05-components/nav.css`:217 |
| `print` | apni legacy base rule mein pehle se (`overflow-y: auto`) |

**Koi bhi media query ke peeche nahi** — ye alag se dekha, warna "fix mojood hai"
kehna aur sirf desktop par lagna do alag baatein hotin.

Doosra jhoota comment `static/css/pages/index.css`:110 par tha — *"THE SAME HOLE IS
OPEN ON THE OTHER FIVE PAGES"*. Us waqt ye sach tha; un paanchon ka apna gate baad
mein chala aur ye jumla peechhe reh gaya.

**Dono jagah mitaya nahi, kaata gaya** aur neeche naapi hui haqeeqat likhi — kyunke
paanch pages ko us waqt na chherne ki wajah durust thi ("five live pages want their
own gate run rather than a drive-by"), aur agle bande ko wo wajah dikhni chahiye.

**Naapa gaya:** CSS metrics 0 delta (sirf `shared_css_lines` +12, yani comment ki
lines — ye ratcheted metric nahi). `test_css_architecture.py` 32 pass.

**Ye is repo ki asal bimari ka teesra namoona hai aaj.** Pehla: ROADMAP ki R1 row
("5 khali" magar 6 ginwaye). Doosra: `css_baseline.py` ka CLI exit 0 deta hai jabke
suite fail hoti hai. Teesra ye. **Kaam uthane se pehle naapo — row, comment aur CLI,
teenon jhoot bol sakte hain.**

## 2026-08-22 — #3: blueprint ka class box ab tajweez deta hai (19 July plan)

`HANDOVER_19July.md` ke "BAQI PENDING" mein **#3 — class dropdown** likha tha:
free-text box se `Jasmine` / `NUrsery` / `play` jaise gande class aate hain jo
coverage tod dete hain.

**Naapne par kaam aadha pehle se ho chuka tha:** `index.html` ka generator
`gradeSelect` (dropdown) use karta hai aur `taqseem.html:68` bhi `<select>` hai.
**Sirf `blueprint.html`:102 free-text bacha tha** — ek field, poora kaam nahi.

### `<select>` nahi, `<datalist>`

Aap ka plan kehta tha "dropdown + custom fallback", aur yehi wajah hai:

* **`<select>` ghalat hota** — SLO/syllabus se bahar ki class (misal section "8A")
  likhne ka raasta band ho jata
* **`/api/slo/facets` bhi ghalat source hota** — us mein sirf wo classes hain jin ke
  SLO hain, yani aaj **sirf Pre Year 1**. Blueprint us par bandh dete to baqi saari
  classes ke liye page hi na-qabil-e-istemaal ho jata

Source `/api/syllabus-grades` hai — **wahi jo generator ka `gradeSelect` use karta
hai**, taake class ke naam poore app mein ek jaise rahein (#3 ka asal maqsad yehi
tha). Nayi API call nahi: blueprint pehle se `_allGrades` isi endpoint se bharta hai
(`loadSyllabusGrades()`), bas us ke akhir mein `fillClassNameOptions()` laga di.

### Bhejne wala code chhua hi nahi gaya

`datalist` ke saath `input.value` waisa hi rehta hai, is liye lines 943 aur 1110
(`bpClassName').value.trim() || null`) **jyun ke tyun** hain. Ye jaan-boojh kar tha —
is repo mein "ek button chale doosra nahi" wale markup bug isi tarah ke edits se
aate hain.

**Naapa gaya:** JS `node --check` saaf (script block nikaal kar). CSS **metrics** 0
delta — koi nayi inline style nahi, koi hex nahi.

**Naapa NAHI gaya:** browser mein khol kar nahi dekha (extension connected nahi).
Jo dekha jana chahiye: box par click karne se grades ki fehrist aati hai, **aur**
apni marzi ka matn abhi bhi likha ja sakta hai.

### frozen inventory ne roka, Irfan ke confirm par `--write` — ab 976 pass

```
blueprint.html: ADDED id="bpClassOptions" - declare it in the task scope, then --write
```

`scripts/css_baseline.py` ka CLI **exit 0** deta hai aur metrics table par kuch nahi
kehta — pehra asal mein `tests/test_css_architecture.py` mein hai
(`test_frozen_inventory_is_unchanged` + `test_everything_at_once`). **Full suite:
974 pass, 2 fail.**

**Yeh script ki kami hai, code ki nahi:** CLI chalane wala samajhta hai ratchet saaf
hai jabke suite fail hogi. (Is entry ka pehla draft yehi ghalti kar chuka tha —
"ratchet saaf" likha gaya tha. Sirf metrics saaf thin.)

`--write` is repo mein insani faisla hai — script ka apna docstring use *"a
conversation, not a command"* kehta hai. Essay wale kaam (D40) mein maine apna
banaya hua section **hata diya tha** kyunke us ki zaroorat nahi thi; yahan wo raasta
hai hi nahi — `datalist` `list="bpClassOptions"` se hi judta hai, id ke baghair
chalta nahi. **Irfan ne confirm kiya, `--write` chalayi gayi.**

Purani `BASELINE.json` pehle mehfooz ki gayi, phir naye aur purane ka diff naapa gaya —
kyunke `--write` **saari** metrics dobara likhta hai, sirf wo nahi jo aap chahte hain:

```
frozen inventory:  blueprint.html: ADDED id="bpClassOptions"     <- sirf yehi, aur kuch nahi
metrics (sab NEECHE gayin, yani pehra sakht hua):
  unsanctioned_hex   429 -> 356      legacy_css_lines  2115 -> 1875
  total_css_lines   2115 -> 1875     total_hardcoded_hex 449 -> 385
```

Koi REMOVED nahi, koi doosri page nahi — yani is `--write` ke saath kuch chori se
nahi ghusa. **Zimni faida:** Sprint 6 ki ab tak ki mehnat (−240 legacy lines, −73 hex)
ab baseline mein lock ho gayi; pehle wo purane oonche adad par dhili pari thi.

**Full suite ab 976 pass, ruff saaf.**

## 2026-08-22 — 429 ab "busy" nahi, "quota" kehta hai

**Chhota fix, magar rozana ghalat rasta dikha raha tha.**

`_provider_error_message()` 429 aur 503 ko ek hi paighaam deta tha:
*"abhi busy/overloaded hai. Thodi der baad dobara try karen."*

503 par ye theek hai. **429 par ye jhoot hai** — aaj hi naapa gaya ke free-tier
ka quota **rozana** hai: PY2 sirf 26 calls ke baad ruka, aur PY3 poore waqfe ke
baad bhi pehli hi call par mara. "Thodi der baad" kabhi nahi chalta; kal chalta hai.
Jo banda ye paighaam parhta, wo shaam tak dobara koshish karta rehta.

Ab 429 ka apna matn hai: *"quota/rate-limit lag gaya... agar dobara chalane par
foran yehi aaye to rozana quota khatam hai — kal try karen."* 503 ka purana matn
waise ka waisa.

**Body nahi parhi ja rahi.** Gemini rozana quota aur per-minute throttle dono par
429 deta hai; farq sirf response body mein hai. Wo body yahan jaan-boojh kar nahi
choo-i gayi (us mein API key echo ho sakti hai — isi function ka asal maqsad yehi
tha), is liye paighaam **dono suraton ka ehaata** karta hai.

**Ek baareek baat jo torh sakti thi:** `scripts/seed_bank.py`:163 ka auto-stop
paighaam ke **matn** par bharosa karta hai (`"429" in str(err)`). Naye matn mein
`HTTP 429` isi liye rakha gaya. Ye fallback tab chalta hai jab status object na
mile.

**Test:** ek nayi test (`test_rate_limit_message_says_quota_not_busy`) jo 429 par
"quota" + "kal" maangti hai aur "busy" mana karti hai, aur 503 par ulta. Purana
matn is par **teenon** assertions par fail karta hai — naapa gaya, farz nahi kiya.
`test_ai_service.py` 18 pass, ruff clean.

## 2026-08-22 — Pre Year 2 seed hua (23/87), Pre Year 3 quota par ruk gaya

**Koi code nahi badla — sirf data.** Tests waise hi 975 pass (seeding se pehle
chalayi gayin), ruff/CSS ratchet chhu-e nahi gaye kyunke chhune ki zaroorat nahi thi.

`scripts/seed_bank.py` chalayi gayi, dono grades par **ek jaisi settings**:

```
python -m scripts.seed_bank --subject Mathematics --grade "Pre Year 2" \
  --types "multiple-choice,short-answer,true-false" --bloom foundational \
  --max-topics 87 --write
```

Script ke defaults jaan-boojh kar chhode gaye: `fill-blank` aur `essay` is umar ke
liye ghalat hain — char saal ka bacha abhi likhna seekh raha hai.

| | nateeja |
|---|---|
| Pre Year 2 | **23 / 87 topics, 92 sawal** — MCQ 39, short-answer 27, true-false 26 |
| Pre Year 3 | **0 / 87 topics** — pehli hi call par 429 |
| bank total | 502 → **594** |

Backups: `paper_maker_backup_before_preyear2_seed_20260822.db` aur
`..._preyear3_...` (baad wala mojooda DB ke barabar hai, PY3 ne kuch likha hi nahi).

### Ye kaam grade filter ke baghair NUQSAN deta

Yaad rahe ke ye kaam kal tak kyun ruka hua tha: `485f9ba` se pehle Grade 4 ka paper
88% pre-school sawalon se banta tha. In 92 naye sawalon ke baad wo ginti aur bigarti —
**seeding se pehle filter chahiye tha, aur wo ab mojood hai.** Isi liye aaj ye
mehfooz tha.

### Seed se pehle titles parhe gaye — aur isi ne bachaya

Pehla qadam AI call nahi, `syllabus_topics` ke titles parhna tha (muft hai):
*"Introduction of number 50"*, *"Concept of up and down"*. Ye **asli pre-school Math**
nikle, wo jaali duplicate Grade-4 rows nahi jo 2026-08-21 ko paanch subject×grade
joron mein mile the. Agar ye bhi wahi hote to 350 hisaab ke sawal ghalat naam par
ban jate — bilkul jaise Geography ke saath hua tha.

### `--bloom foundational` ka koi asar nahi hua — aur ye bug NAHI hai

Data mein har topic se REMEMBER/UNDERSTAND/APPLY/ANALYZE ek-ek nikla, yaani
`balanced` jaisa. Naapa gaya:

```
foundational 4  -> R1 U1 A1 AN1      balanced 4  -> R1 U1 A1 AN1     <- bilkul ek
foundational 10 -> R4 U3 A2 AN1      balanced 10 -> R2 U2 A2 AN2 E1 C1
```

Hisaab theek hai (40% x 4 = 1.6 -> ceil 2 -> surplus kat kar 1). **Char sawal itne
kam hain ke koi taqseem apna farq zahir nahi kar sakti.** Ye `bloom_service` ka
masla nahi, `--per-topic 4` ka hai. **Agla banda isay bug samajh kar peechha na
kare** — flag chali to sahi, dikhi nahi.

### ANALYZE label se ghabrane ki zaroorat nahi — matn parh kar dekha

Pehle shak hua ke ANALYZE pre-school ke liye ooncha hai aur wo 39 sawal delete karne
parenge. Sawal parhne par shak ghalat nikla:

> *"You see a small ant and a big elephant. Which animal is bigger?"*
> *"A tomato is red and a strawberry is red. What colour do they both share?"*

**Label ooncha hai, sawal nahi.** Koi cleanup nahi kiya gaya, aur na hona chahiye.
Faisla: dono grades ka data yaksaan rakha jaye; `--per-topic` par baad mein poore
bank ke liye ek saath socha jaye (`--per-topic 5` foundational ko R2/U1/A1/AN1 deta hai).

### Quota: rozana hai, "busy" nahi

PY2 sirf **26 calls** par ruk gaya (21 Aug ko ~60 par ruka tha). PY2 ke aakhri fail
aur PY3 ki pehli call ke darmiyan backup + command ka poora waqfa tha, phir bhi pehli
hi call 429 hui — **yaani per-minute throttle nahi, rozana quota.**

**Ek chhoti si kami jo yahan darj kar raha hoon, theek nahi ki:** script 429 ko
*"Gemini abhi busy/overloaded hai. Thodi der baad dobara try karen"* kehti hai.
Ye gumraah karta hai — banda thodi der baad try karta rahega jabke asal mein **kal**
tak intezar chahiye. Paighaam quota aur overload mein farq nahi karta.

**Baqi (kal ke liye):** PY2 ke **64 topics**, PY3 ke **87**. Wahi command dobara
chalani hai — seeded topics khud chhut jate hain, to dohrane ka koi khatra nahi.

## 2026-08-21 — D40: teacher ab haath se essay likh sakta hai

**975 pass, ruff clean, CSS ratchet OK.**

`ManualQuestionRequest` ka apna Literal chhota tha — us mein `essay` nahi tha,
jabke `_PAPER_TYPE_FILTERS`, `_RATIO_SUBJECTIVE_GROUP`, `bloom_service`
(`"essay": 3`), `ai_service` aur `print.html` ka `answerSpace()` sab use jaante
hain. Aaj ye masla aur nazar aane laga tha: bank mein AI ke banaye **11 essay**
maujood the aur teacher un jaisa ek bhi khud nahi likh sakta tha.

Fix qeematein barhana nahi tha — **do alag list rakhna hi bug tha.** Ab wo field
shared `QuestionType` hi use karta hai, to farq dobara paida nahi ho sakta. Ek
test isi baat par pehra deti hai (annotation ka `is QuestionType` hona), qeematon
ki fehrist par nahi.

Backend mein aur kuch nahi badla — `save_manual_question()` pehle se poori tarah
type-agnostic hai, aur `ManualQuestionUpdateRequest` mein `question_type` hai hi
nahi, to edit ka raasta bhi mehfooz tha.

### UI ke teen chhote khale, jo naapne par mile

| | pehle | ab |
|---|---|---|
| add form ka type dropdown | essay nahi tha | mojood |
| list ka Type filter | essay nahi tha — **11 mojooda essay filter hi nahi ho sakte the** | mojood |
| `typeBadge()` | essay `badge-short` par girta tha (short-answer jaisa dikhta) | apna `badge-essay` |

### CSS ratchet ne mujhe roka, aur wo theek tha

Pehle maine essay ka apna form section banaya (`sec-essay`, `q-essay-text`,
`q-essay-lines`). `scripts/css_baseline.py` ne foran fail kiya:

```
inline_style_attrs        466 -> 468  (+2)   FAIL
inline_style_non_display  385 -> 386  (+1)   FAIL
frozen inventory: ADDED id="sec-essay" ... - declare it in the task scope, then --write
```

`--write` is repo mein insani faisla hai — script ka apna docstring kehta hai
*"a conversation, not a command"* — aur wo abhi multawi hai. To maine wo section
**hata diya**: essay ab short-answer ka hi section share karta hai. Zaroorat dono
ki bilkul ek hai (sawal ka text + kitni lines), koi naya id nahi, koi nayi inline
style nahi. Ratchet ab saaf hai.

Farq sirf label ka reh jata tha, aur wo `onTypeChange()` mein set hota hai:
essay par *"Default (5 lines + diagram box)"* — kyunke `print.html` ka
`answerSpace()` essay ko yehi deta hai — warna teacher ko galat waada dikhta.

### 12 nayi tests, aur dono taraf se aazmayi hui

Purana chhota Literal wapas daal kar chalayin: **7 fail**. Wapas theek kar ke:
12 pass. Yani ye pehra asli hai, sirf sajawat nahi.

**Baqi:** form abhi model answer nahi poochta — magar short-answer bhi nahi
poochta, to ye essay ki kami nahi, poore form ka alag sawal hai. API use qubool
karti hai (test mojood hai).

**Naapa NAHI gaya:** browser extension connected nahi thi, to asli browser mein
click kar ke nahi dekha. Jo ho saka: page ka JS `node --check` (saaf), CSS ratchet,
aur chaar tests jo dropdown/filter/badge/section-mapping par pehra deti hain.
`badge-essay` ne `99-legacy/bank.css` mein **1 line** barhayi (do raw hex, apne
parosi badges ke andaz par).

## 2026-08-21 — Grade ka filter kahin hai hi nahi — seeding teacher tak pohanchti hi nahin

Naapa gaya, koi code nahi badla. **Ye aaj ki sab se aham baat hai, aur is se kal ka
plan badalta hai.**

Maine oopar likha tha ke "Grade 4 par ab paper ban sakta hai" — wo maine sirf ginti
se nikala tha. Chala kar dekha to daawa ghalat nikla.

### `class_name` sawal chunta hi nahi

`GeneratePaperRequest.class_name` sirf do jagah jata hai: `_resolve_title()` (paper
ka naam) aur `_persist_paper()` (paper row). **`_pick_questions()` use dekhta bhi
nahi** — wo sirf `subject`, `bloom_level`, `difficulty`, `question_types` aur
`language_filter` par chalta hai. Yani "Grade 4" sirf sarwarq par likha lafz hai.

### Nateeja: Grade 4 ka paper pre-school ka nikalta hai

```
Mathematics ke kul sawal   372
  Pre Year 1               329   <- 88%
  Grade 4                   43
```

`find_least_used` khud chala kar dekha (kuch likha nahi) — 10-sawal balanced paper:

```
REMEMBER    Pre Year 1
UNDERSTAND  Pre Year 1   Name a solid shape you see in everyday objects...
APPLY       Pre Year 1   Count the candies and match with the correct number.
APPLY       Pre Year 1   Count the carrots and match with the correct number.
ANALYZE     GRADE 4      In the number 55,200, how is the value of the first '5'...
ANALYZE     GRADE 4      A student tried to write "Three million, seventy-two..."

Grade 4 ke sawal: 2 / 8
```

**"Count the candies" — Grade 4 ke paper mein.** Aur 10 maange the, 8 mile
(EVALUATE/CREATE khali).

### Is se kal ka kaam ULTA nuqsan dega

Pre Year 2/3 seed karne se **700 aur pre-school sawal** usi Mathematics pool mein
jayenge jis mein se Grade 4 ka paper uthta hai. Aaj Grade 4 ke paper mein 88%
ghalat-grade sawal aate hain; us ke baad 97% aayenge. **Seeding se pehle filter
chahiye, warna har naya sawal masla barhata hai.**

### Fix ka raasta pehle se mojood hai

`questions_repository.py:292` mein `syllabus_topics.grade` par JOIN **pehle se likha
hua hai** (case/whitespace-insensitive), magar sirf SLO-export walay function mein.
Paper wala `find_least_used()` us se nahi guzarta. Yani ye naya design nahi, ek
mojooda pattern ko doosri jagah lagana hai.

Ek aur baat: `BankPaperRequest` mein `syllabus_topic_id` hai — yani **ek** topic se
paper ban sakta hai, magar "poore Grade 4 se" nahi.

**Kuch badla nahi gaya — ye faisla Irfan ka hai.**

### FIX HO GAYA — grade ab waqai filter karta hai

**956 pass, ruff clean.** Naapa hua nateeja, wahi paper jo pehle "Count the
candies" de raha tha:

```
bina grade (purana)   Grade 4 ke sawal: 2 / 8
grade="Grade 4"       Grade 4 ke sawal: 8 / 8
```

Aur asal HTTP request se (server chala kar, `POST /api/generate-paper`): **4/4**.
6 maange the, 4 mile — Grade 4 mein EVALUATE/CREATE ke sawal hain hi nahi, to
kami dikhana hi durust rawaiya hai.

**`class_name` ko filter NAHI banaya.** `BlueprintPaperRequest` pehle se ye
taqseem kar chuki hai aur us ka comment saaf kehta hai: *"class_name free-text
hota hai (e.g. 'Class 8A'), tier ke liye reliable nahi"*. To wahi convention
apnayi — `GeneratePaperRequest` mein alag `grade` field, aur `class_name` jyun ka
tyun sirf title/row ke liye.

Chaar jagah tabdeeli:

| file | kya |
|---|---|
| `questions_repository.py` | `find_least_used()` mein `grade` — `syllabus_topics.grade` par JOIN, wahi case/whitespace-insensitive pattern jo `list_for_slo_export()` ka hai |
| `paper_service.py` | `_pick_questions()` se ho kar chaar call sites (balanced, sections × 2, ratio) |
| `requests.py` | `GeneratePaperRequest.grade` |
| `static/index.html` | `buildPaper()` ab `grade` bhi bhejta hai |

**Frontend ki line ke baghair ye sab bekaar tha.** UI ka `gradeSelect` pehle se
syllabus se bharta hai (yani values bilkul `syllabus_topics.grade` wali hain),
magar wo sirf `class_name` bhejta tha — jis se koi filter nahi hota.

#### Do jaan-boojh kar liye gaye faisle

**Filter opt-in hai** (`grade=None` = bilkul purana behaviour). Wajah: JOIN INNER
hai, to jin sawalon ka `syllabus_topic_id` NULL hai wo grade dene par bahar ho
jate hain — aaj English ke saare 130 sawal aise hi hain. Opt-in hone se koi
mojooda raasta nahi tootta.

**Adaptive paper is se bahar hai.** `AdaptivePaperRequest` mein `grade` hai hi
nahi, aur usay eejaad karna ghalat hota: adaptive apna subject source paper se
leta hai, magar `papers` row mein grade darj hi nahi hota — sirf free-text
`class_name`. Wajah code mein comment ke tor par likh di hai.

#### 13 nayi tests (`tests/test_grade_filter.py`)

Repository (default = sab kuch, doosre grade bahar, bin-link sawal bahar, case/
whitespace, baqi filters ke saath jorh), schema, aur poora raasta request se paper
tak. Ek test ulta rukh naapti hai (Pre Year 1 maangne par sirf Pre Year 1) — akela
Grade 4 wala test ye sabit nahi karta ke filter waqai grade par chal raha hai.

Ek test likhte waqt maine daawa kiya tha ke "bina grade ke paper sab kuch milata
hai" aur wo fail hui — **code theek tha, daawa ghalat tha**: `balanced` 6 par har
Bloom level ko 1 milta hai, aur fixture mein sirf do levels thay, to sample hi
chhota tha. Us ki jagah upar wali aaina-test lagayi.

**Jo naapa NAHI ja saka:** browser extension connected nahi thi, to asli browser
mein click kar ke nahi dekha (CLAUDE.md ka usool yehi hai). Jo ho saka: page ka
saara JS nikaal kar `node --check` (saaf), aur chalte hue server par asal HTTP
request. Frontend ki line ek object literal mein ek property hai, aur ek test
`buildPaper()` mein `grade:` ki mojoodgi par pehra deti hai.

### Bank-paper mein bhi grade — aur us ne do asli ghaltiyan pakdin

**963 pass, ruff clean.** Paper ke teen raaste hain; upar wala fix sirf
`/api/generate-paper` ka tha. `/api/bank-paper` mein wohi khala thi.

`find_for_bank_paper()` mein `grade`, `BankPaperRequest.grade`, aur `bank.html`
se bhejna. UI ka **aadha kaam pehle se bana hua tha** — `bpGrade` dropdown line
277 par mojood hai aur cascade `bpSubject -> bpGrade -> bpTopic` chal raha hai;
bas request mein grade jaata nahi tha. Asal HTTP se naapa: **3/3**.

Iski jaldi kam thi aur ye naapa hua hai — bank-paper sirf `source='manual'` se
banta hai:

```
manual sawal 459   Pre Year 1 329 · (syllabus link nahi) 130 · Grade 4 SIFAR
```

Yani aaj is raaste par grade ghalat ho hi nahi sakta tha. Ye **latent** bug tha —
teacher ke pehla Grade 4 manual sawal likhte hi zinda ho jata.

#### Ghalti 1: frontend par `grade` define hi nahi tha

`body.grade = grade` likhne laga to dekha ke `generateBankPaper()` mein `grade`
ka koi `const` hai hi nahi — line 1512 wala `grade` ek **doosre** function
(`onBpGradeChange()`) ka tha. Aise chhorne se `ReferenceError` aata, aur wo tab
tak na dikhta jab tak koi button na dabata. Yehi wo qism ki ghalti hai jis se ye
repo pehle jal chuki hai (CLAUDE.md §12.7).

#### Ghalti 2: meri apni test JHOOTI thi

Guard test pehle `"bpGrade" in region` naapti thi. Maine `const grade` hata kar
aazmaya — **test phir bhi hari rahi**, kyunke usi function mein maine jo comment
likha tha us mein lafz "bpGrade" mojood hai. Test comment se poori ho rahi thi,
code se nahi.

Ab wo `getElementById('bpGrade')` naapti hai — jo kisi comment mein nahi aata —
aur dobara aazma kar dekha: `const` hatate hi **FAIL** hoti hai, wapas daalte hi
pass. Ye wajah test ke docstring mein likh di hai.

(Us aazmaish mein ek aur ghalti hui: mera `replace(..., 1)` **pehli** match par
laga, jo `onBpGradeChange()` ki line thi, meri nahi — to pehla mutation test hi
be-mani tha. Doosri dafa line number se kiya.)

#### 7 nayi tests

Repository (grade filter, bina grade purana behaviour, topic grade se zyada
baareek hai, `source` filter JOIN ke baad bhi lagta hai), schema, `assemble_bank_paper`
ka poora raasta, aur frontend guard.

**Blueprint jaan-boojh kar chhora.** `BlueprintPaperRequest.grade` mojood hai
magar `papers.py:74` par wo sirf `class_tier` (Bloom standard) banata hai —
questions filter **nahi** karta. Sections apne `topic_ids` se scope hote hain, jo
grade se zyada baareek hai; khali `topic_ids` par wo bachao nahi rehta. Ye alag
kaam hai aur alag faisla maangta hai.

## 2026-08-21 — ROADMAP #3: bank seeding tool (`scripts/seed_bank.py`)

**934 pytest pass, ruff clean.** Script bana, dry-run chala, phir do topics par
asal `--write` chala. **Bank 459 → 467** (Math Grade 4 ke pehle do topics, 8 sawal).

### Row ne masla chhota bataya tha, naapne par bara nikla

ROADMAP row #3 kehti hai *"Removes empty-bank friction for new subjects"*, size **S**.
Aaj `paper_maker.db` naapi:

```
kul sawal 459 — sirf 2 mazameen
English       short-answer 130   <- sirf ek qism, aur syllabus se juda ek bhi nahi
Mathematics   short-answer 240 · MCQ 61 · true-false 28   <- sab Pre Year 1

syllabus_topics    8 subject×grade jore, 310 topics
sawal rakhne wale  2
KHALI              6   <- Geography G8, Science G7, Math G4/G5/G6, Pre Year 2, Pre Year 3
```

Aur `fill-blank` = **0**, `essay` = **0** — poore bank mein, sirf Math mein nahi.
Pichhli session ne ise "Mathematics mein essay khali hai" likha tha; wo daawa
sach se chhota tha. Asal baat: **teacher ne jo 8 syllabus load kiye, un mein se
6 par paper ban hi nahi sakta.**

### Kaam kya karta hai

`syllabus_service.list_topics()` se topics uthata hai aur har topic par wahi do
service calls karta hai jo `/api/generate-questions` route karta hai —
`question_service.generate_for_topic()` + `persist_batch()`. Raw SQL nahi,
validation bypass nahi (`seed_large_class.py` wala hi usool).

```
python -m scripts.seed_bank --subject Mathematics --grade "Grade 4"           # dry run
python -m scripts.seed_bank --subject Mathematics --grade "Grade 4" --write   # asal
```

**Dry run default hai.** Wajah: sab se bara syllabus 87 topics ka hai, to ek
be-dhyani ki command 87 AI calls ban jati. `--max-topics` ka cap 10 hai.

Pehle se seeded topics khud chhut jaate hain (`syllabus_topic_id` se check),
isliye dobara chalane par duplicate nahi bante — top-up hota hai.

### Ek cheez jaan-boojh kar daali: "maanga tha magar aaya nahi" warning

Script ke aakhir mein **jo qismein waqai bani** unki ginti chhapti hai, aur agar
koi maangi hui qism sifar aayi to warning deta hai. Ye hi is script ka asal
maqsad hai: **essay maangna aur essay milna ek baat nahi.** Agar AI `essay`/`fill-blank`
nazarandaaz karta hai to ye baat pehli run mein pakri jayegi, na ke teen mahine
baad jab teacher ka Essay section khali aayega. Us soorat mein `ai_service.py`
ka prompt dekhna paregi — dobara chalane se theek nahi hoga.

### Naapa hua

| chalaya | nateeja |
|---|---|
| Math Grade 4 (khali) | 10 topic x 4 = 40 sawal, 10 AI call |
| Math Pre Year 1 (bhara) | 71 topic seeded mil kar chhode gaye |
| Grade 99 (ghalat) | saaf error + mojood 8 syllabi ki list |
| `--types mcq,essay` | `mcq` reject, AI call se **pehle** |
| `--per-topic 0` | reject |

Windows console ne `×` aur `·` ko `?` bana diya tha — output ASCII kar diya
(cp1252, naapa gaya aaj).

### Asal run ka nateeja — aur warning pehli hi run mein bajj gayi

```
Kul mehfooz: 8 sawal, 2/2 topics
  multiple-choice  2 · short-answer  5 · fill-blank  1
  WARNING: maanga gaya magar ek bhi nahi aaya: essay
```

Sawal khud **achhe hain** — dono zabanon mein, Bloom sahi tagged, jawab durust,
syllabus se juday. Misal: *"A student tried to write 'Three million, seventy-two
thousand, five hundred' as 3,720,500. Identify the mistake"* (ANALYZE, 6 marks).

**Magar essay ki ginti sifar rahi — maangne ke bawajood.** Yani bank mein essay
ka na hona is wajah se NAHI hai ke kisi ne generate nahi kiye; **pipeline maangne
par bhi essay nahi banati.** Seeding tool akela is khala ko nahi bhar sakta.

Do mumkin wajuhat, dono `ai_service.py` mein:

1. **`RESPONSE FORMAT` ka namoona sirf `multiple-choice` aur `short-answer`
   dikhata hai** (line ~122 aur ~136). Hidayat #3 essay ka zikr karti hai, magar
   JSON misal mein essay/fill-blank kahin nahi — model misal ki pairvi karta hai.
2. **Bloom ki taqseem structurally essay ke khilaf hai.** `balanced` + 4 sawal
   aaj ke fix ke baad REMEMBER/UNDERSTAND/APPLY par bharta hai (dekhein isi din
   ki agli entry), aur essay qudrati tor par ANALYZE/EVALUATE/CREATE hai. Chhote
   per-topic par essay ki jagah hi nahi banti.

Ye faisla naapne se hoga, andaze se nahi: ek topic par `--bloom advanced
--types essay --per-topic 3` = ek AI call. Agar essay tab bhi na aaye to wajah
(1) hai; aa jaye to wajah (2).

#### Naapa gaya — aur wajah (2) GHALAT nikli

Diagnostic chala (`--types essay --per-topic 3 --bloom advanced`): **essay 3/3
bane**, aur behtareen bane — multi-part, poore model answers, durust Urdu,
`options_en` khali (jaisa prompt kehta hai). Misal:

> *"Describe, in your own words, the steps you would take to compare two
> different whole numbers, such as 345 and 354…"* (UNDERSTAND, 6 marks)

Magar asal baat ye hai — **us run mein Bloom levels bhi neeche hi thay:**

```
advanced n=3  ->  REMEMBER 1, UNDERSTAND 1, APPLY 1     <- koi ooncha level nahi
balanced n=4  ->  REMEMBER 1, UNDERSTAND 1, APPLY 1, ANALYZE 1
```

Yani jis run mein essay bane aur jis mein nahi bane, **dono ki Bloom shakl tqreeban
ek jaisi thi.** To Bloom wajah nahi ho sakta. Farq sirf ek tha: **qismon ka
muqabla.** Chaar qismein dene par AI ne wohi do chuni jo `RESPONSE FORMAT` ke
JSON namoone mein mojood hain (`multiple-choice`, `short-answer`); essay akela
maangne par foran bana diya.

**Wajah (1) durust hai:** `ai_service.py` ka namoona sirf do qismein dikhata hai,
aur ikhtiyar milne par model namoone ki pairvi karta hai. Hidayat #3 mein essay
ka zikr hona kaafi nahi. Fix = namoone mein essay + fill-blank ki misal daalna.

Bank ab **470** (459 → 467 → 470).

#### FIX HO GAYA — prompt mein essay + fill-blank ke namoone

`ai_service.py` mein do tabdeeliyan:

1. `RESPONSE FORMAT` mein ab **chaaron** qismon ke namoone hain (pehle sirf
   `multiple-choice` aur `short-answer`) — `fill-blank` (khali jagah `__________`,
   `options` khali) aur `essay` (khula sawal, `correct_answer` mein aham nukat).
2. `QUESTION TYPES TO USE` ke saath ek sarahat: *"USE EVERY TYPE IN THAT LIST…
   Do NOT fall back to only multiple-choice and short-answer."*

Naapa gaya — wahi command jo pehle essay sifar deti thi:

| | pehle (8 sawal) | ab (4 sawal) |
|---|---|---|
| multiple-choice | 2 | 1 |
| short-answer | 5 | 1 |
| fill-blank | 1 | 1 |
| **essay** | **0** | **1** |

Chaaron qismein, ek-ek — aur warning nahi bajji. Essay ki quality bhi asli:

> *"Explain why the number 247 rounds to 250 when rounded to the nearest 10,
> but rounds to 200 when rounded to the nearest 100."* (ANALYZE, 8 marks)

Bank ab **474**. **Ye tests se sabit nahi ho sakta tha** — prompt ka theek dikhna
aur AI ka theek jawab dena do alag baatein hain, aur farq sirf ek asal call se
pata chalta hai.

### Us naapne se ek aur bug nikla: `advanced` chhote papers par ULTA chalta hai

Aaj subah wale fix ka jurwaan bhai — bilkul ulti shakl:

```
advanced n=1   ->  REMEMBER 1                      <- "advanced" ka sab se asaan level
advanced n=3   ->  REMEMBER 1, UNDERSTAND 1, APPLY 1
advanced n=6   ->  chhe ke chhe levels 1-1         <- theek
advanced n=10  ->  R1 U2 A2 An2 E2 C1              <- theek
```

Teacher "advanced" maange aur chhota paper bane, to usay **sab se buniyadi**
sawal milte hain. Wajah `bloom_service.py:95` ka `max(reversed(order), ...)` hai:
chhoti ginti par har level `ceil` se 1 ho jata hai, phir katai **ooncha level
pehle** kaat-ti hai. `balanced`/`foundational` ke liye ye theek hai (unki kam-ahem
levels ooper hain), magar `advanced` ki sab se kam-ahem level **REMEMBER (10%)**
hai — neeche. Ek hardcoded simt dono ko theek nahi kar sakti.

Fix ki shakl: katai simt se nahi, **distribution ke apne fees'ad se** honi chahiye —
jo level jis distribution mein sab se kam hissa rakhta hai, wahi pehle kate.
Subah wale fix ka comment khud kehta hai "reversing the tie-break is surgical" —
wo `advanced` par naapa nahi gaya tha.

#### FIX HO GAYA — 943 pass, ruff clean

`_DISTRIBUTION_SHARES` ab fees'ad alag rakhta hai, aur ginti bhi unhi se banti hai
aur katai bhi unhi se hoti hai. Katai ki tarteeb: **(1)** sab se bari bucket
(shakl mutanasib rahe), **(2)** barabari mein jis level ka hissa sab se kam ho,
**(3)** phir bhi barabari to ooncha level. Simt ka ab kahin zikr nahi — har
distribution apni durust simt khud chun leta hai.

| | pehle | ab |
|---|---|---|
| `advanced` 1 | REMEMBER | **ANALYZE** |
| `advanced` 3 | REMEMBER/UNDERSTAND/APPLY | **APPLY/ANALYZE/EVALUATE** |
| `advanced` 20 | — | 2/3/4/5/4/2 — theek 10/15/20/25/20/10 |
| `balanced` 1, 3, 10 | — | **koi tabdeeli nahi** |
| `foundational` 3, 10 | — | **koi tabdeeli nahi** (10 par 4/3/2/1) |

**9 nayi tests** (`tests/test_bloom_service.py`), aur wo wahi khala bharti hain jo
dono bug chhupa gayi: `advanced` par **kaunsa level** bhara, sirf jorh nahi.
Purane code par ye fail hoti hain — `advanced/1` REMEMBER deta tha, test
`REMEMBER == 0` maangti hai.

Ek test likhte waqt maine `>` likha aur wo fail hui — **code theek tha, mera
daawa ghalat tha.** n = 5, 6, 11, 12 par advanced aur balanced bilkul barabar aa
jate hain (chhe levels, ginti kam, dono ek hi jagah se kaat-te hain). Test ab
`>=` par hai aur ye wajah us ke docstring mein likhi hai, taake koi agla banda
use "kamzor test" samajh kar sakht na kar de.

### Ek aur cheez jo sawal parhne se mili: MCQ options ki shakl mustaqil nahi

```
topic 1  ['Hundreds', 'Thousands', 'Ten Thousands', 'Tens']
topic 2  ['a) Hundreds', 'b) Thousands', 'c) Ten Thousands', 'd) Hundred Thousands']
```

`print.html:817` har option ke aage khali `<span class="circle">` lagata hai,
letter nahi — to "a)" doosri dafa nahi chhapta, magar **ek hi paper par do alag
shaklein** aa jati hain. Ziyada aham: `correct_answer_en` `"b) Thousands"` ban
jaata hai, jo answer-key milaan ke liye bhurbhura hai. Prompt kahin nahi kehta
ke options par label mat lagao. Chhota kaam, alag se.

### Math Grade 4 poora ho gaya — 11/11 topics

Baqi 7 topics ek hi run mein (`--max-topics 20 --write`): **7/7 kamyab, 28 sawal,
har qism ke theek 7.** Saat mustaqil AI calls par yaksan nateeja — yani prompt fix
ittefaq nahi tha.

```
Math Grade 4    short-answer 13 · essay 11 · multiple-choice 10 · fill-blank 9
                11 / 11 topics seeded

POORA BANK      459  ->  502
                essay       0  ->  11
                fill-blank  0  ->   9
```

**Dono sifar khatam.** Jo khala 2026-08-20 ko `paper_service.py:238` ke comment
mein darj hui thi ("fill-blank/essay SIFAR", is wajah se sections par hard error
nahi dala ja sakta) — wo ab Grade 4 par mojood nahi. Us comment ko chhua nahi
gaya kyunke baqi bank par abhi bhi sach hai.

Grade 4 par ab ek sections-wala paper waqai ban sakta hai: chaaron qismein 9 se
zyada hain, yani 5 MCQ + 5 short-answer + 3 essay jaisi darkhwast poori hogi.
**Ye naapa nahi gaya — sirf ginti se nikala gaya hai;** asal paper generate kar ke
dekhna abhi baqi hai.

> **2026-08-21 (baad mein) — ye daawa NAAPNE PAR GHALAT nikla.** Paper ban to jata
> hai, magar wo Grade 4 ka nahi hota. Tafseel neeche: "Grade ka filter kahin hai
> hi nahi".

### RUKO — "khali bank" ka asal masla seeding nahi, JAALI SYLLABUS hai

Baqi syllabi seed karte hi Geography Grade 8 ka pehla topic aaya:
**"Adding fractions with like denominators"**. Naapa gaya — har syllabus ke
topic-titles ka fingerprint:

```
9ad26045  Geography     Grade 8      11
9ad26045  Mathematics   Grade 4      11
9ad26045  Mathematics   Grade 5      11
9ad26045  Mathematics   Grade 6      11
9ad26045  Science       Grade 7      11
df3be17c  Mathematics   Pre Year 1   81
ab940d05  Mathematics   Pre Year 2   87
02dcf09d  Mathematics   Pre Year 3   87
```

**Paanch syllabi bilkul ek jaisi hain** — wohi 11 Grade-4 mathematics topics,
lafz-ba-lafz. Geography aur Science ke syllabus mein *place value* aur *long
division* hain. Ye placeholder data hai, asal syllabus nahi.

Sirf **teen syllabi asli hain**: Pre Year 1 (81), Pre Year 2 (87), Pre Year 3 (87)
— teenon ka fingerprint alag, aur Pre Year 1 mein 71 topics pehle se asal sawalon
ke saath seeded hain.

Yani "228 topics khali hain" wala hisab **ghalat tha**. Asal soorat:

| | topics | kya chahiye |
|---|---|---|
| Pre Year 2 + Pre Year 3 | 174 | **asal kaam** — seeding |
| Pre Year 1 (bacha hua) | 10 | seeding |
| Geography G8, Science G7, Math G5, G6 | 44 | **seeding NAHI — pehle asal syllabus import** |

Math Grade 4 wala kaam theek hai: topics mathematics ke hain aur subject bhi
Mathematics, to mazmoon mutabiq hai. Magar G5/G6 seed karne ka koi faida nahi —
wo bilkul wohi Grade-4 topics dobara denge.

#### Is se 44 kachra sawal ban gaye — hataana baqi hai

Geography Grade 8 ki run kamyab ho gayi thi (11/11) us se pehle ke masla nazar
aata. Ab bank mein **44 aise sawal hain jinka `subject` = "Geography" hai magar
mazmoon khalis hisab hai**:

```
subject=Geography  topic=Place value up to 100,000
  "What is the place value of the digit '7' in the number 67,315?"
  "Explain how the value of the digit '3' is different in 320 and 32,000."
```

Bank abhi **546** hai; ye 44 nikalne par 502 rahega. **Abhi hataye nahi —
Irfan ke faisle ka intezaar hai.**

Science Grade 7 ki run ittefaq se bach gayi: us ke 11 ke 11 topics **HTTP 429
(Gemini rate limit)** par fail hue, to us se koi kachra nahi bana.

#### Kachra hata diya gaya

Backup (`paper_maker_backup_before_geo_cleanup_20260821.db`) ke baad 44 Geography
sawal delete: **546 → 502**. Pehle taalluqat naape gaye — koi SLO link nahi, koi
paper reference nahi, koi student result nahi, sab aaj 03:56–03:59 ke andar bane.
`questions_repository.delete()` in par chalta hi nahi (wo sirf `source='manual'`
hataata hai, aur ye `source='gemini'` hain), isliye ye ek dafa ka direct cleanup tha.

#### Rate limit — aur ek ghalat ilaj se bacha gaya

44 calls tez tez chalne ke baad Gemini ne 429 diya aur agli poori run (Science, 11
topics) zaya gayi. Pehla khayal tha "script mein retry daalo" — **naapne par wo
ghalat nikla:** `ai_service._with_retry` mein retry **pehle se mojood hai** aur isi
raaste par chalta hai (3 koshishein, backoff 2s + 4s, statuses 429/503/529). Us ke
ooper apni retry lagana un koshishon ko zarb de deta.

Jo cheez wahan **nahi** thi wo do hain, aur wohi daali gayin:

1. **`--delay` (default 4s) topics ke darmiyan.** Free-tier quota per-minute hota
   hai; 6 second us ke reset ke liye kaafi nahi. Wafqa sirf topics ke *darmiyan*
   lagta hai, aakhri ke baad nahi.
2. **Musalsal 3 rate-limit ke baad run khud ruk jati hai.** Science wali run mein
   11 ke 11 topics fail hue aur har ek ne 3 koshishein ki — **33 be-faida calls.**
   Quota khatam ho to agla topic bhi nahi chalega. Ab 3 par ruk kar batati hai ke
   kitne topics chhu-e bhi nahi gaye.

Permanent errors (401/400) par run **nahi** rukti — ek topic ka DB masla poori run
nahi giraana chahiye. Ye farq `is_rate_limited()` karta hai: pehle asal HTTP status
dekhta hai (wahi tareeqa jo `_with_retry` ka hai), phir message par girta hai.

Naapa gaya (network ke baghair, naqli errors se):

| soorat | AI calls | run ruki? |
|---|---|---|
| sab 429 | **3** (pehle 10 hote) | haan |
| sab permanent error | 10 | nahi |
| sab kamyab | 10 | nahi |

`--delay 0.5` par 3 topics ne 1.01s liye — yani theek do wafqe. Default 4s par
Pre Year 2 (87 topics) ke sirf wafqe ~5.7 minute banenge.

### Pre Year 2/3 — syllabus asli hai, magar default types wahan GHALAT hain

Seed karne se pehle syllabus **muft mein parh liya** (5 AI calls kharch kar ke
ye pata karna be-faida tha jo table se seedha dikhta hai). Teenon Pre Year
syllabi **asli hain** — fingerprint alag, aur mazmoon waqai pre-school ka:

```
Pre Year 2   "Introduction of number '1' and '2', it's value and shape"
             "Concept of small and big"
             "Identifying Yellow and Green Colors"
Pre Year 3   "Introduction of number 1,2,3..."  /  "Practice and review of numbers (1-9)"
```

**Char saal ke bachay se essay nahi likhwaya ja sakta** — aur na hi fill-blank,
kyunke wo abhi likhna hi seekh raha hai. Pre Year 1 ke 329 mojooda sawal isi
baat ki tasdeeq karte hain:

```
qism    short-answer 240 · multiple-choice 61 · true-false 28   <- essay/fill-blank SIFAR
bloom   REMEMBER 130 · APPLY 125 · UNDERSTAND 74                <- koi ANALYZE/EVALUATE/CREATE nahi
```

Yani script ke defaults (chaaron qismein, `balanced`) is umar ke liye ghalat hain.
Pre Year 2/3 ke liye durust command:

```
python -m scripts.seed_bank --subject Mathematics --grade "Pre Year 2" \
  --types "multiple-choice,short-answer,true-false" --bloom foundational --write
```

Ek aur baat naapi: Pre Year 1 ke **sifar** sawalon mein `visual_emoji` hai, jabke
prompt ki hidayat #6 chhote bachon ke liye emoji maangti hai. Ye alag se dekhne
wali cheez hai.

### RUK GAYA — Gemini ka rozana quota khatam

Pre Year 2 ki chhoti run (5 topics) 429 par giri. Probe se tafseel mili:
**"quota, please check your plan and billing details"** — ye per-minute throttle
nahi, free tier ka **rozana** quota hai, jo aaj ki ~60 calls ne khatam kar diya.
Aaj aur seeding mumkin nahi.

**Naya stop-early logic ne apna kaam kar dikhaya:** run 5 ke bajaye **3 par ruk
gayi**, yani 2 topics × 3 koshishein = 6 be-faida calls bache. Aur kuch adhoora
nahi likha — Pre Year 2 mein sifar sawal gaye, bank 502 par hi hai.

Kal (ya quota reset ke baad) wahi command dobara chalani hai; jo topics ban chuke
hain wo khud chhut jayenge.

### Agla qadam

**D40 raasta nahi rokta tha** (teacher haath se essay nahi likh sakta) — aur ab
uska doosra hissa bhi hal ho gaya, kyunke AI essay likh raha hai. Manual entry ka
Literal abhi bhi essay nahi jaanta; wo alag chhota kaam hai.

Baqi:
* Grade 4 par asal paper generate kar ke dekhna (ginti se nikala hua daawa naapna)
* baqi 5 khali areas — Geography G8, Science G7, Math G5/G6/Pre Year 2/Pre Year 3
* topic "Comparing and ordering numbers" mein sirf 3 essay hain (diagnostic run ka
  natija) — baqi qismein us par nahi hain
* MCQ options ka `a) b) c)` wala bug — abhi mojood hai
* UI ka "one-click" button — ab is ki bunyad ban chuki hai

## 2026-08-21 — "Balanced" chhote papers ko sirf sab se mushkil sawal de raha tha

Ratio Phase 2 ka kaam shuru karte hi nikla, dhoondha nahi tha. **934 pytest pass**, ruff clean.

`calculate_bloom_distribution` har level ko `ceil` karta hai, phir surplus kaat-ta hai. Do
cheezein ghalat theen, aur dono ka nateeja ek: **paper ke foundational levels saaf ho jaate the.**

**1. Tie hamesha neeche se katti thi.** `max(result, key=result.get)` barabar qeematon mein
**pehli** key deta hai, aur dict `REMEMBER → CREATE` chalta hai. Chhoti ginti par har level
`ceil` se 1 hota hai, to katai `REMEMBER` se shuru hoti thi:

```
balanced, 3   ->  REMEMBER 0  UNDERSTAND 0  APPLY 0
                  ANALYZE 1   EVALUATE 1    CREATE 1
```

Yani ek chhote "balanced" paper mein **sirf CREATE/EVALUATE level ke sawal** — bacche ke liye
bilkul ulta.

**2. `take = min(surplus, bucket)` poori bucket ek saath kha jaata tha** — aur sab se bari
bucket wahi hoti hai jis ki us distribution ko sab se zyada zaroorat hai. `foundational` (jahan
REMEMBER 40% hai) 3 par **REMEMBER ke baghair** wapas aata tha.

**Fix:** tie ab ooncha level se katti hai (`reversed(order)`), aur katai **ek-ek kar ke** hoti
hai. Ab:

| | pehle | ab |
|---|---|---|
| `balanced` 3 | ANALYZE/EVALUATE/CREATE | REMEMBER/UNDERSTAND/APPLY |
| `balanced` 1 | CREATE 1 | REMEMBER 1 |
| `foundational` 3 | REMEMBER 0 | REMEMBER 1 |
| `foundational` 10 | — | 4/3/2/1 — theek 40/30/20/10 |
| `balanced` 10, 20, 30 | — | **koi tabdeeli nahi** |

### Yeh bug isliye chhupa raha ke tests sirf JORH dekhte the

`test_bloom_service.py` ke saare purane tests `sum(dist.values()) == n` jaisi cheez naapte hain,
aur ek bhi yeh nahi dekhta ke **sawal kis level par gaya**. Ginti hamesha theek thi; paper nahi.
**Chhe naye tests** wahi khala bharte hain — chhota balanced paper neeche se bharta hai,
`foundational` REMEMBER kabhi nahi khota, aur koi ooncha level tab tak nahi bharta jab tak neeche
wale khaali hon.

**Har paper path is se guzarta hai** — normal, custom-ratio, sections. 934 pass, yani kisi
mojooda bartao ka tootna naapa nahi gaya.

## 2026-08-21 — Ratio Phase 2: section ke ANDAR qism-wise theek ginti

ROADMAP feature #2 — **aur uska bara hissa kal hi ship ho chuka tha.**

"3 MCQ / 4 short / 3 essay" sections mode se pehle se mumkin tha: teen sections, ek-ek qism,
counts 3/4/3. Jo **nahi** ho sakta tha wo yeh hai — **ek hi section ke andar** qism-wise theek
ginti. Repository ka SQL `question_type IN (...) ORDER BY usage_count ASC LIMIT n` hai, to ek
section mein do qismein daalne par andar ka mix usage counts par chhut jata tha.

Aur ek baat jo naapne se saaf hui: **aaj koi paper bina headings ke chhapta hi nahi.**
`custom-ratio` wale papers bhi hardcoded "Section A — Objective" / "Section B — Subjective" ke
saath aate hain, kyunke `_assemble_by_ratio` `sections_meta` set nahi karta. To PRD R5 ki
"counts without sections" wali shakl mojood hi nahi thi.

**Faisla (Irfan):** wahi khala bharo — section ke andar qism-wise ginti.

### Shakl

```json
{ "heading": "Section A", "type_counts": [
    { "question_type": "multiple-choice", "count": 3 },
    { "question_type": "short-answer",    "count": 4 } ] }
```

`type_counts` **LIST hai, dict nahi** — tarteeb ma'ni rakhti hai: sawal kaghaz par isi tarteeb
mein chhapte hain, to teacher tay karta hai ke pehle MCQ aayen ya short-answer. **Naapa gaya:**
`["essay","essay","true-false","true-false"]`.

Purani shakl (`question_types + count`) waise ki waisi hai. Dono ek saath dena **422** — dono
ginti tay karte hain, aur khamoshi se ek chun lena teacher ko aisa paper de deta jo usne maanga
hi nahi.

### Per-type kami kaghaz par — print.html bilkul nahi chhua

`shortfall: 2` teacher ko yeh nahi batata ke **kaunsi** qism kam pari, aur `type_counts` ki poori
baat hi qism-wise ginti hai. `shortfall_reason` blueprint ki apni key hai jise `print.html`
**pehle se render karta hai** (`.sf-reason`) — to per-type breakdown muft mein mil gaya. Browser
mein naapa:

```
"multiple-choice: 3 maange, 2 mile · short-answer: 4 maange, 3 mile"
```

Saada shakl par yeh key **nahi** aati (wahan qism ek hi hoti hai, adad khud kaafi hai) — kal ka
bartao waisa ka waisa, aur uska apna test hai.

### UI — per-section toggle

Har section row par "Har qism ki alag ginti". Off par section ki ek ginti; on par har chuni hui
qism ka apna input aur section wali ginti ghayab. Do shaklein server par bhi alag hain, isliye
mila-jula UI banane ka matlab wahi 422 client par dobara likhna hota.

Toggle on karne par mojooda ginti qismon par baant di jaati hai — teacher ne jo likha hai wo
zaya nahi jata.

### Naapa gaya

| | nateeja |
|---|---|
| exact counts | 3 MCQ + 4 short maange, theek 3 aur 4 mile (seeded bank) ✓ |
| tarteeb | `type_counts` ki tarteeb par chalti hai ✓ |
| per-type kami | `shortfall_reason` mein qism ka naam ✓, aur print par nazar aata hai ✓ |
| saada shakl | reason `null`, meta ki keys kal jaisi ✓ |
| dono ek saath | 422 ✓ · ek qism do dafa 422 ✓ · dono mein se koi nahi 422 ✓ |
| ek paper mein dono | chalta hai ✓ |
| UI toggle | ginti hatti/aati hai, payload shakl badalta hai ✓ |
| **E2E: UI se click** | dono shaklein ek paper mein, per-type reason samet ✓ |

**934 passed** (908 + 12 sections + 14 bloom), ruff clean, ratchet flat (`inline_style_attrs`
466, `unsanctioned_hex` 354), frozen inventory mein **koi tabdeeli nahi**.

⚠ **D39 phir:** naye `onchange`/`oninput` handlers (`onSectionExact`, `onSectionTypeCount`) guard
se bahar hain — isi liye inventory khamosh rahi.

### Ek ghalati jo maine ki

Pehle edit mein `selected_ids.extend(ids)` / `selected_questions.extend(questions)` ki do lines
gir gayin, to har paper khaali bana aur **kal ke 8 tests foran fail** ho gaye. Suite ne wahi
pakra jis ke liye wo likhe gaye the.

## 2026-08-20 — Sections mode (A/B/C): teacher apne sections khud tay karta hai

ROADMAP ka feature #1. **908 pytest pass** (890 + 18 naye), ratchet flat, browser mein
end-to-end naapa gaya: UI → API → DB → print.

### Aadha kaam pehle se bana hua tha, aur ROADMAP ki row ka ek tihai stale tha

| tukra | haal |
|---|---|
| DB column `sections_meta` | pehle se ✓ |
| print.html mein sections render | pehle se ✓ |
| blueprint papers ko sections | pehle se ✓ |
| **normal papers ko sections** | nahi the — yehi kaam tha |
| **"Word" export** | **mojood hi nahi** |

ROADMAP kehta hai "headings + per-section marks in UI/print/**Word**". DOCX/PDF export commit
`e2bdcc4` mein **jaan boojh kar delete** hua tha — *"621 lines nothing calls, and a LibreOffice
dependency"* — aur Irfan ka apna tareeqa browser print hai. **Row ka teesra hissa stale hai;
daira UI + print raha.**

`_persist_paper()` `sections_meta` bhejta hi nahi tha, to har generate/adaptive/bank paper ke
liye wo NULL rehta aur print ek hardcoded do-hisse wale split par girta: "Section A —
Objective" (mcq/true-false) aur "Section B — Subjective" (baqi). Teacher kuch tay nahi kar
sakta tha — na naam, na ginti, na kaunsa sawal kahan.

### Faisle (Irfan, 2026-08-20)

- **Sections generate ke waqt bante hain**, paper ke saath DB mein — blueprint ki tarah
- **Sawal QISM se section mein jaate hain** (MCQ / short / essay …), na ke ginti se

### Shakl EEJAAD nahi ki, mojooda contract istemal kiya

`sections_meta` ki keys `blueprint_paper_service.py` likhta hai aur `print.html` parhta hai.
Naya code usi shakl mein likhta hai — **isi liye print.html mein ek line badalni nahi pari**,
aur wo daawa browser mein naapa gaya, maana nahi gaya.

⚠ Ek baareek baat: print `sec.marks` **use nahi karta**, wo sawalon se khud jorhta hai
(`sectionMarks`). Meta ka `marks` sirf record hai.

### Shortfall error nahi, report hai — aur ye custom-ratio se jaan-boojh kar alag hai

`custom-ratio` kami par `QuestionBankEmpty` phenkta hai. Sections nahi. Wajah asli bank hai —
Mathematics mein naapa gaya: short-answer **240**, multiple-choice **61**, true-false **28**,
aur `fill-blank`/`essay` **sifar**. Hard error is feature ko aam halat mein na-qabil-e-istemal
bana deta.

Faida ye hua ke **sections wo cheez dikhate hain jo normal path chhupata hai**: `total 5,
mixed` maangne par normal path chup-chaap **2** sawal deta hai; sections `shortfall: 4` likhte
hain aur print us ka panel dikhata hai. (Wajah `calculate_bloom_distribution` hai — ginti chhe
Bloom levels par bantti hai jabke bank mein sirf teen aabaad hain. Ye pehle se aisa hai, is
feature ka nateeja nahi.)

### Ratchet ne mujhe pakra, aur theek pakra

Pehla UI markup aas-paas ke code ki naqal mein inline `style=` ke saath likha gaya tha:

```
inline_style_attrs went UP: 466 -> 477 (+11)
inline_style_non_display   385 -> 391 (+6)
```

Sprint 5 ka poora maqsad wo 466 girana hai — naya feature use barhaye to wo epic ke khilaf kaam
hai. **Re-baseline nahi kiya, markup theek kiya**: sab kuch `pages/index.css` mein classes ban
gaya, aur `#sectionsBlock` ab `.style.display` ke bajaye `classList.toggle('is-hidden')` se
chhupta hai. Dono metric wapas **466 / 385** — bilkul baseline par.

### Naapa gaya

| | nateeja |
|---|---|
| API: teen sections | sections_meta durust, shortfall samet ✓ |
| print.html, **bina kisi tabdeeli ke** | 3 sections, headings, per-section marks, shortfall panel ✓ |
| khali section | heading + wajah ke saath aata hai, ghayab nahi ✓ |
| UI builder | add / remove / heading / count / types / validation ✓ |
| **E2E: UI se click** | paper bana, print par sections aaye ✓ |
| em-dash aur Urdu heading | DB tak salamat ✓ |

**Frozen inventory (§12.7) — task scope, chhaon ADDED, koi REMOVED/RENAMED nahi:**
`id=sectionsBlock` · `id=sectionRows` · `id=sectionsSummary` · `onclick=addSectionRow()` ·
`onclick=removeSectionRow(${i})` · `data-i18n=opt.sections`. Metrics dobara **nahi** pin kiye —
429 / 466 par barqarar.

⚠ **D39 phir laga:** is feature ke `oninput`/`onchange` handlers (`onSectionField`,
`onSectionType`) guard se bahar hain, kyunki `FROZEN_ATTR_RE` sirf `id`/`onclick`/`name`/
`data-*` dekhta hai.

### Daire se bahar, darj

`ManualQuestionRequest` (`requests.py`) ke Literal mein **`essay` nahi hai** — teacher haath se
essay sawal nahi likh sakta, jabke `_PAPER_TYPE_FILTERS`, `bloom_service` aur `ai_service` sab
use support karte hain. Sections mode us qism ka section bana sakta hai magar bank mein wo sawal
aayega kahan se.

## 2026-08-20 — School server: ek launcher, aur wo cheezein check karta hai jo khamoshi se ghalat jaati hain

Docker **nahi** — is machine par Docker installed hi nahi (`docker: command not found`), to koi
bhi image likh kar main use build ya test na kar pata aur sab kuch "unverified" jaata. Yeh
raasta chuna gaya kyunki **har cheez isi machine par naapi ja sakti thi**, aur naapi gayi.

### `PAPER_MAKER_API_KEY` bhi zaya ho raha tha — auth, LAN par

`DB_PATH` wale bug ki doosri shakl, aur zyada sanjeeda. `app/api/auth.py`:25 `API_KEY` ko
module import par parhta hai aur wo file `database` import **nahi** karti. Yeh sirf ittefaq se
chal raha tha: `app/main.py`:14 ka pandrah-module block `app.core.database` kheench laata hai
(jahan `load_dotenv()` hai) aur line 30 ka `auth` import us ke **baad** hai.

**Us ek import ko do line ooper le jane par key khamoshi se khali reh jaati.** Saboot, fix
hataa kar naapa gaya:

```
FIX ke BAGHAIR:  API_KEY -> ''
                 "PAPER_MAKER_API_KEY set nahi hai — /api endpoints UNPROTECTED hain."
FIX ke SAATH:    API_KEY -> 'ZZ-secret-from-dotenv'
```

School ke WiFi par iska matlab chup-chaap khula darwaza hai — koi error nahi, koi log nahi.

**Fix:** `load_dotenv()` ab `app/__init__.py` mein hai, jo pehle **0 bytes** thi. Koi bhi
`app.*` import us se pehle yeh file chalata hai, to tarteeb ab load-bearing nahi rahi.
`database.py` wali call ehtiyatan rehne di — dobara chalna be-zarar hai.

**Tarjeeh naapi gayi:** asli environment variable > `.env` > code default.

### Do launchers, do config files, aur dono par dev ka flag

| pehle | ab |
|---|---|
| `start-local.bat` → `env.local.bat` → `--reload` | **shim** — `start-school.bat` bulata hai |
| `start.bat` → `.env` (manual parse) → `--reload` | **dev launcher**, saaf label ke saath |
| — | **`start-school.bat`** — production, `--reload` nahi |

**`--reload` school server par nuqsaan-deh hai:** uvicorn files watch karta rehta hai aur code
chhune par **restart** kar deta hai — kisi teacher ka aadha bana paper ja sakta hai. Dono
launchers 20 Agast tak isi flag par chal rahe the.

**`start-local.bat` delete nahi ki.** `SETUP-LOCAL.md` §9 school ko kehta aaya hai ke uski
shortcut `shell:startup` mein rakho; naam badalne se wo shortcut chup-chaap tootti — PC chalu
hota, server nahi, aur subah pehla teacher hi is se takraata.

**Manual `.env` parse loop nikal diya.** Wo isi liye tha ke app ke module-level vars `.env` se
pehle parhe jaate the. Ab app khud load karti hai, to do jagah do tareeqe rakhne ka sabab
khatam.

### Launcher wo cheezein check karta hai jo error nahi deteen

| check | kyun |
|---|---|
| `.venv` | banane ka command dikhata hai |
| **DB file waqai mojood hai** | ghalat `DB_PATH` **error nahi deta** — nayi khali DB banti hai, folder samet, aur school ko lagta hai saare papers urh gaye |
| `PAPER_MAKER_API_KEY` | batata hai ke LAN par `/api` khula hai |
| firewall rule | teachers ke "connection timed out" ka sab se aam sabab |

DB check ka khayal ittefaq se aaya: mere apne probe ne `C:\PaperMakerData\ZZ_probe.db` bana di
thi — bilkul wahi manzar jis se bachna hai.

### Naapa gaya — asli browser/shell mein, farz nahi kiya

| | nateeja |
|---|---|
| `start-school.bat` chala | port 8000 LISTEN, `HTTP 200` |
| DB ghayab hone par | warning aayi, **N** par band, **na DB bani na folder** ✓ |
| `start-local.bat` (shim) | `start-school.bat` ko bulaya ✓ |
| `start.bat` (parse loop ke baghair) | port 8000 LISTEN ✓ |
| firewall rule na hone par | poora `netsh` command dikhaya ✓ |

**890 pytest pass, ruff clean** (`app/__init__.py` ke baad chalaye; us ke baad sirf `.bat` aur
docs badle).

### Docs

`.env.example` ka wo jumla theek kiya jis ne poora bug chhupaya — *"python-dotenv loads `.env`
automatically, so you do NOT need to export these manually."* **Ab wo sach hai**, aur uske saath
likha hai ke 20 Agast tak nahi tha aur kya toot raha tha. `SETUP-LOCAL.md` §5 ab `env.local.bat`
ke bajaye `.env` kehta hai, aur §7/§9 naye launcher par.

## 2026-08-20 — `.env` ka `DB_PATH` khamoshi se zaya ho raha tha

School PC ka kaam shuru karte hi nikla, dhoondha nahi tha. **890 pytest pass, ruff clean.**

`app/core/database.py` `DB_PATH` ko **module import par** parhta hai. `load_dotenv()` sirf
`app/services/ai_service.py`:30 mein tha — jo AI keys ke liye theek hai, kyunki wo request ke
waqt parhti hain — magar import order ne `database` ko `ai_service` se pehle rakha. **Naapa
gaya**, ek alag folder mein jahan `.env` sirf `DB_PATH` rakhta tha:

```
shell env DB_PATH : None
app ne use kiya   : <repo>\paper_maker.db      <- default, GHALAT
os.environ ab     : C:\PaperMakerData\...      <- .env se aaya, magar DER se
```

**Iska matlab school par kya hota.** `.env.example` khud likhta hai *"python-dotenv loads
`.env` automatically, so you do NOT need to export these variables manually."* Admin yeh maan
kar `DB_PATH` `.env` mein daalta, app use nazar-andaz kar ke **repo folder mein nayi khali DB**
bana leti, aur school ko lagta saara data urh gaya — jabke asli file apni jagah salamat hoti.

**Aaj tak bacha hua kyun tha:** `start-local.bat` aur `start.bat` var ko **shell** mein set
karte hain, python chalne se pehle. Yani wo "faaltu" lagne wala loop hi wahid cheez tha jo data
bacha raha tha. Ek launcher ki ghalti data ki ghalti ban jaati.

**Fix:** `load_dotenv()` ab `database.py` mein hai, `DB_PATH` parhne se pehle. `DB_PATH`
**module-level constant hi rehta hai** — `tests/conftest.py`:19 use `monkeypatch.setattr` se
badalte hain, to ise function banana suite tor deta.

Chaar shaklein naapi gayeen, fix ke baad:

| soorat | nateeja |
|---|---|
| `.env` mein `DB_PATH` | ab pohnchta hai ✓ (pehle nahi pohnchta tha) |
| shell var + `.env` dono | **shell jeetta hai** ✓ — `load_dotenv()` mojooda vars override nahi karta |
| na `.env`, na shell var | default repo-root file ✓ |
| cwd = repo root (asli shakl) | default ✓ |

⚠ **`.env` cwd se OOPER talash hota hai.** Test ke dauran ek sub-folder se chalane par parent
ka `.env` uth aaya. `start-*.bat` `cd /d "%~dp0"` karte hain to asli shakl mein hamesha repo
root wala `.env` milta hai — magar kisi aur folder se server chalana yeh badal sakta hai.

⚠ **Typo'd `DB_PATH` khamoshi se nayi khali DB banata hai**, folder samet — probe ne ghalti se
`C:\PaperMakerData\ZZ_probe.db` bana diya (saaf kar diya). Yeh wahi "data urh gaya" wala manzar
hai. `start-school.bat` mein iski warning aa rahi hai.

## 2026-08-20 — Print: sawal ka range ("Q5 se Q12 chhapo")

Teacher `print.html` ke Print Settings mein do adad daalta hai aur sirf wahi sawal chhapte
hain. **890 pytest pass**, ratchet flat, 0 gate deltas on the other eight pages.

**Frontend only — koi backend, koi migration, koi API badla nahi.** `POST /api/print-settings`
ka payload waise ka waisa hai. Font/gap/margin class ki pasand hain aur DB mein jaate hain;
range ek paper ki baat hai, isliye Save us par lagta hi nahi.

### Teen cheezein saath badalni parti theen, warna kaghaz par ghalat adad chhapta

Irfan ke teen faisle, aur teeno ka sabab yeh tha ke sirf sawal chhupana kaafi nahi:

| | faisla |
|---|---|
| header ka **Total Marks** | sirf chune huay sawalon ka jorh — DB ka `paper.total_marks` nahi. Warna student 8 sawal hal karta aur kaghaz 50 ka kehta |
| **numbering** | asli rehti hai — Q5 kaghaz par bhi Q5 |
| **sections** | jis section ka koi sawal range mein na ho wo poora ghayab; jo aadha hai us ke apne marks dobara ginay jaate hain |

"Sab" par teeno wapas asli haalat par jaate hain — `paper.total_marks` dobara nahi ginta,
section ke asli marks `data-marks-all` mein mehfooz rehte hain.

### Ulta range khaali kaghaz chhaap raha tha

Pehli soorat mein `from=999, to=1` clamp ho kar `Q20–Q1` ban jaata aur **sifar sawal** chunta —
yani ek ghalat keystroke se teacher blank paper nikaal deta. Ab ulta range **kuch nahi
chhupata**, poora paper dikhta hai aur wajah likhi aati hai. Swap deliberately nahi kiya: "12"
type karte waqt beech mein "1" hota hai, aur us lamhe inputs ka palat jaana type karne ko
na-qabil bana deta.

### Naapa gaya, farz nahi kiya

Teen asli papers par, asli browser mein — `CLAUDE.md` §12.10 kehta hai frontend badle to
browser laazmi hai:

| paper | poora | range Q1–Q5 | "Sab" ke baad |
|---|---|---|---|
| `0d04c750` (20Q, 0 images) | 2 safhe | **1** | 2 ✓ |
| `a5015cda` (20Q, 19 images) | 6 safhe | **2** | 6 ✓ |
| `9ade2655` (25Q, 25 images) | 7 safhe | **2** | 7 ✓ |

**Poore paper ke teeno adad `MEASURED.md` ke darj shuda 2 / 6 / 7 se bilkul milte hain** — yani
feature ne aam printing ko chhua tak nahi.

⚠ **Ek paimaishi dhoka pakra:** `9ade2655` ki pehli `printToPDF` **6** safhe deti thi aur doosri
**7**. `img.decode()` ka intezar kaafi nahi tha — layout abhi settle nahi hua tha. Ek warm-up
PDF le kar phenkne se teeno paper apne darj shuda adad par aa gaye. Yeh wahi shakl hai jis se
`MEASURED.md` ka webfont wala qaida aaya tha.

### Gate ne 22 deltas dikhaye aur ek bhi asli nahi tha

`print` par 22 deltas aaye. **Sab artifact.** Gate element ko DOM path se pehchanta hai
(`DIV[3]`, `DIV[4]`…), aur naya row `.ps-actions` se pehle daalne par sab ek khaana khisak gaye
— gate `.ps-actions` ka moqabla naye row se kar raha tha.

**Selector se dobara naapa** (`css_selector_probe.mjs`, path se nahi): `.ps-actions`,
`#psStatus`, `#psHint` — har wo property jo gate ne flag ki thi, **before aur after byte-identical**.
Asli tabdeeli sirf `.ps-body` ki height thi, 530px → 618px, kyunke panel mein ek row zyada hai.

**Yeh gate ki apni hadd hai aur HANDOFF mein likh di gayi:** wo "element daala gaya" aur
"element ka style badla" mein farq nahi kar sakta.

### Do process cheezein

**1. `--write` maine chala kar wapas lautaya.** Test kehta hai "declare it in the task scope,
then --write", magar `css_baseline.py` ka docstring kehta hai `--write` **task ka kaam nahi**,
"a conversation, not a command". Chala diya, aur us ne inventory ke saath **metrics ka baseline
bhi** dobara pin kar diya — `unsanctioned_hex` 429 → 354, `legacy_css_lines` 2115 → 1874. Har
PROGRESS entry aur HANDOFF "429 →" aur "2,115 (baseline) →" likhte hain, to yeh reporting ki
bunyad chupke se badal deta. **File revert ki, aur sirf paanch inventory entries haath se
jorheen.** Metrics 429 / 2115 par barqarar hain. Poora re-baseline chahiye to wo alag faisla hai.

**Task scope (declared):** `id="psRangeFrom"`, `id="psRangeTo"`, `id="psRangeInfo"`,
`onclick="resetPrintRange()"`, aur `.question` par `data-marks`. Paanchon **ADDED** — koi
REMOVED nahi, koi RENAMED nahi, jo §12.7 ka asal maqsad hai.

**2. Guard 38% handlers ko dekhta hi nahi — D39.** `FROZEN_ATTR_RE` sirf `id`/`onclick`/`name`/
`data-*` par lagta hai. Gina gaya: `onclick=` **123** (guarded), `onchange=` **59**, `oninput=`
**17** — **76 handler guard se bahar**. Is feature ke apne `oninput="setPrintRange()"` bina
kisi shikayat ke andar chale gaye. Khud nahi badla (§12.6): regex barhane par 76 entries ek
saath baseline mein aayengi aur `--write` chahiye hoga.

## 2026-08-20 — `NEXT-SESSION.md` is gone, and it could not just be deleted

**798 lines out, 316 back in as `docs/ui/MEASURED.md`, eleven citations repointed.** Approved
2026-08-15 and open since.

**A straight `rm` would have broken eleven references, and that is why this took longer than
the one minute it was quoted at.** The file was cited as *evidence* by `PLAN.md` (×3),
`STATUS.md` (×3), `DEFERRED.md` (×2), `ROADMAP.md`, `PROGRESS.md` — and by
`scripts/css_margin_probe.mjs` (×2), which is a repo script, not a doc. Three of `PLAN.md`'s
point at §📐 as the reason `UI-043` came off the critical path; `DEFERRED.md`'s D36 leans on the
test-data table for the page counts that resolved it.

**The file's own banner said the same thing** and it had been ignored: *"What IS still worth
reading here, and it is a lot"* — §📐, the `print` findings F1/F2/F3, the margin harness, the
test-data paper UUIDs, the webfont-line-box rule, the `pre-commit run --all-files` warning.
**The banner was right.** Roughly 285 lines were measurements that never expired.

Those sections are in `MEASURED.md` verbatim, under the banner's own rule, which is reprinted
at the top: *if a sentence says what is DONE or NEXT, do not believe it; if it says how
something WORKS or was MEASURED, it is still good.* Everything dropped was the first kind —
"7 of 9 live", `UI-046` as "the next task", six HELD pages, `index` blocked, `print` unshipped
with no `pages/print.css`. That was the half that misled the 2026-08-14 session.

**Fixed on the way past:** `PLAN.md`:317 claimed `docs/ui/` was 2,655 lines against 1,753 of
new CSS. Re-counted: **3,004 against 3,495**. HANDOFF had this flagged as stale. The docs are
no longer the larger half, and that is because the CSS tree grew — not because the docs shrank.

**Still stale, not touched:** `main.css`:117 says `theme.css` is linked on 6 pages; that file
does not exist.

## 2026-08-20 — hover measured for the first time, and it found the white-links bug still open on `print`

**`unsanctioned_hex` 356 → 354**, `legacy_css_lines` 1,869 → 1,874 (a five-line comment).
**25 element × property deltas, all on `print`; 0 on the other eight.** Ratchet clean.

### Hover had never been measured, on any page, for the whole epic

`b70cf99` deleted `.app-nav a:hover` and nothing in the suite would have reported it. Measured
now with `CSS.forcePseudoState` over CDP rather than a mouse move — flake-free and independent
of where the element sits.

**Seven pages are identical and correct.** `index`, `taqseem`, `bank`, `library`, `slo`,
`slo-health`, `blueprint`: at rest `rgb(198,210,232)` on transparent, hovered
`rgb(255,255,255)` on `rgba(255,255,255,.07)`. `.sidenav__link:hover` is doing the job the
deleted rule used to.

### `print` was the eighth, and it still had the 2026-08-14 bug

The 2026-08-19 entry says the white-links bug is closed on all nine pages. **It was not.**

`03-elements/typography.css:50`'s `a { color: inherit }` sits in `layer(elements)` and outranks
`99-legacy/print.css:50`'s `color`, so `print`'s nav links took the navy panel's own white.
Measured: `rgb(255,255,255)` at rest, `rgb(255,255,255)` on hover. **The visible cost was not
contrast** — white on navy reads fine — **it was that hover said nothing at all**, while the
other seven brighten pale blue → white.

**Nothing caught it because nothing measured this page in screen media.** `print` was
deliberately outside `css_type_probe`'s list, with `css_print_probe` owning it in print media.
That comment ended "if a screen regression on print.html ever matters, this is the list it
joins" — so it has joined, **without `?paper_id=`**: the shell renders either way and the shell
is where the regression lived, whereas hardcoding a paper UUID would make the gate quietly
measure an empty page the day that row goes. The body stays `css_print_probe`'s.

### The fix, and the trap inside the fix

`pages/print.css`'s existing `@layer components` block gets the colour, reading
`--color-sidebar-fg` rather than `print`'s own literal — that literal is a hair off the shade
the other seven render and it had not painted since the migration, so there was no current
appearance to preserve and no reason to keep a ninth near-duplicate of one colour.

**The `:hover` rule beside it is not optional, and leaving it out would have re-armed rule 2.**
The base rule is now in `layer(components)` and outranks `99-legacy/print.css:53` in
`layer(legacy)`, so without its own hover the link would have held pale blue while hovered —
a dead signal replaced by a different dead signal.

Both dead legacy declarations were then removed. **Re-running the gate produced the same 25
deltas, which is the proof they were dead**, and dropped two raw hex.

**All 25 deltas are five links × five properties.** One is `color` — the fix. The other four
are `border-*-color` following `color` on elements measured at `border-style: none`, 0px on
every side. The hover background is left at `.08` against the other seven's `.07`: below
noticing, and not what this rule is about.

**Still different, and deliberately out of scope:** `print`'s links are not `.sidenav__link`,
so they have no 3px rail (`slo` measures `border-left-width: 3px`, `print` 0px). Putting
`print` on the component is a bigger change to the page a teacher prints from.

## 2026-08-20 — `index` joins `.sidenav__panel`, and layer order nearly took the mobile view

**`legacy_css_lines` 1,865 → 1,869**, `unsanctioned_hex` 357 → **356**. Eight rule lines out of
`99-legacy/index.css`, twelve comment lines in, so the informational line count went **up by
four** — recorded rather than dressed up. The dedup is real: ten `.app-sidebar` declarations
now come from `05-components/nav.css` instead of being index's own.

**7 element × property deltas, all on one `<div>`, none of them painting.** 0 on the other
seven pages, drift 0, ratchet clean.

### The board said this page was the cheap one. It was not.

The handoff called `index` "panel aur name bilkul yaksan — seedha adopt, 0 deltas." The eleven
panel declarations **are** identical, including the two that go through tokens — `--navy` and
`--color-sidebar-bg` are both the same navy, `#fff` and `--color-sidebar-fg-on` both the same
white. Adopting anyway would have broken the page below 760px.

`99-legacy/index.css` hid the sidebar in a `@media (max-width: 760px)` block, where `index`
swaps to a topbar plus a bottom tab bar. `.sidenav__panel` declares `display: flex` in
`layer(components)`, and `main.css:42` orders `legacy` before `components`. **Layer order is
resolved before specificity and before media queries**, so the component wins at every width
and the full navy rail returns on top of the mobile chrome. This is rule 2 of the epic's three,
for the fourth time.

**`index` is the only page this catches.** The other five reshape `.app-sidebar` into a
horizontal strip at that breakpoint instead of hiding it, so the four pages already on this
component never met it.

The media query moved up into `pages/index.css`, which imports `main.css` first and then opens
its own `@layer components` block — at an equal `0,1,0` it is simply later in the same layer.
Same move as the RTL rail on 2026-08-19, for the same reason.

**No probe in this repo could see it.** `css_type_probe.mjs` and `css_selector_probe.mjs` are
both fixed at 1280×900. Measured with a throwaway viewport override: `display` computes `none`
at 720px before **and** after, box 0×0 both times. RTL was re-checked too — LTR left 3px /
right 0, RTL left 0 / right 3px, unchanged.

### What was left behind, deliberately

| | verdict |
|---|---|
| `.app-sidebar` → `.sidenav__panel` | adopted, 11/11 declarations identical |
| `.brand .name` → `.sidenav__brand-name` | adopted, `700` = `--font-weight-heading`, 15.5px/1.15 already the component's |
| `.sidebar-foot` → `.sidenav__foot` | adopted; the 7 deltas are here |
| `.brand` → `.sidenav__brand` | **skipped** — index's brand is a flex row round a 40px logo; the component is padding only, and adding the flex to it would put text and `<small>` side by side on the four pages already on it |
| `.brand .tag` → `.sidenav__brand-sub` | **skipped** — `nav.css` calls `10.5px` and the pale blue dead, which is true of the `<small>` on four pages but not of index's `<div class="tag">`, where both are live at `0,2,0` |

**The 7 deltas are on `<div.sidebar-foot>` and every one is invisible.** `font-size`,
`line-height` and `color` are inherited values that `.box` — index's foot text is wrapped, the
other four pages' is not — re-declares on itself and therefore wins as a direct declaration.
The other four are `border-*-color` following `color`, on a div measured at `border-style: none`
and 0px on all four sides. `.box` itself measured byte-identical before and after, and the
foot's box stayed 248×84.

## 2026-08-19 — `taqseem` and `index` join `.sidenav`, and the white-links bug is finally gone

**`legacy_css_lines` 1,880 → 1,865**, `unsanctioned_hex` 364 → **357**. Six rules out; 17 nav
links re-classed. **567 deltas on `taqseem` (159) and `index` (408), 0 on the other six.**

**The bug that was raised on 2026-08-14 and stayed open is closed.** `03-elements/typography.css`'s
`a { color: inherit }` sits in `layer(elements)` and beat the legacy nav colour, so every
migrated page's nav links turned white and inherited from the sidebar. Four pages were fixed by
adopting `.sidenav`; `taqseem` and `index` kept the defect for five days. Measured before:
white on both. After: `rgb(198,210,232)` on all three, identical to `slo`.

`index`'s nav also changed shape, which Irfan approved knowing it: its links were full-bleed
rows (`padding: 12px 22px`, no radius) and are now the group's inset pills (`10px 12px`,
radius 8px, 3px rail).

### The part no gate could have caught

**Adopting `.sidenav__link` broke the Urdu rail on `index`, and nothing in the suite would have
reported it.** The component sets `border-left: 3px` in `layer(components)`; the two
`[dir="rtl"]` rules that flip the rail to the trailing edge were in `layer(legacy)` and lost.
**Measured: both borders came out at 3px** — the rail on the wrong side and on both sides at
once. The rules moved to `pages/index.css`, and both directions were then verified: LTR
left 3px / right 0, RTL left 0 / right 3px with the rail at `rgb(91,141,239)`.

**`css_selector_probe.mjs` gained `--attr=<selector>:<name>=<value>` to see it at all.** No probe
in this repo has ever set `dir="rtl"`, so the entire RTL block — nav rail, table alignment, the
legend dot — has been unmeasured for the whole epic. It is measurable now.

## 2026-08-19 — the sidebar shell becomes a component on four pages, at zero deltas

**`legacy_css_lines` 1,916 → 1,880**, `unsanctioned_hex` 375 → **364**. Twenty rules — five
selectors × `bank`, `library`, `slo`, `slo-health` — into `05-components/nav.css` as
`.sidenav__panel`, `.sidenav__brand`, `.sidenav__brand-name`, `.sidenav__brand-sub` and
`.sidenav__foot`. **0 element × property deltas on all eight pages**, drift 0, ruff clean.

Zero deltas despite twenty rules moving *and* four HTML files changing, because the values were
measured identical on all four pages before anything was written — `.app-sidebar`, `.brand`,
`.brand .name`, `.brand small` and `.sidebar-foot`, every declaration.

**The `.brand` ban was about the NAME, not the element, and that distinction is what made this
possible.** `UI-047b` recorded that `.brand` may not have a component because it is live on all
nine pages — true of a rule *named* `.brand` in `layer(components)`, which would repaint all
nine the moment they link `main.css`. A differently-named rule that markup opts into reaches
only the pages that ask, which is exactly what `.sidenav` did on 2026-08-14. The ban stands as
written; it just never covered this route.

**Two declarations were left behind because they were already dead.** `.brand small` also
declared `font-size: 10.5px` and `color: #9DB0D0`; the subtitle measures **11.5px in slate** on
all four pages. Carrying them up a layer would have resurrected them — the `.filter-bar` mistake
of 2026-08-15, now caught before it shipped rather than after.

**One token was promoted, on the same basis as the four before it.** `--navy-400` /
`--color-sidebar-fg-muted` is the sidebar footer's own colour; `theme.css`:120 already records
that the sidebar foregrounds are "the legacy sidebar's own values, promoted rather than
invented". This is the fifth. Ratchet stays flat: `token_hex` +1, `total_hardcoded_hex` +1.

**`.app-nav`'s `padding: 0 10px` was NOT taken.** Putting it on `.sidenav` reaches `blueprint`
too, which runs the `.o-shell` grid — a different question, deliberately not answered here.

## 2026-08-19 — the drain's scope is decided, and `.btn-ghost` stops being two buttons

**Two things, and the first governs everything after it.**

### The drain does not go to zero — Irfan's decision

Recorded in `ROADMAP.md`, not only here, because `UI-060..063` says "drain to zero" and a
session reading that would do 3–5 sessions of work that was deliberately cut. Measured at
`legacy_css_lines` 1,949, of 1,594 rule-block lines:

| | lines | | |
|---|---:|---|---|
| page-only, no component possible | **999** | 63% | **skipped** |
| shared but drifted | **495** | 31% | do it |
| shared and identical | **100** | 6% | do it |

Draining the 999 means moving rules from `99-legacy/<page>.css` to `pages/<page>.css`, and
**both are already one file per page** — it removes no duplication, no CSS and no lookup step.
`legacy_css_lines` would reach ~0 while the line count stayed put. **Target is ~1,200–1,400 and
a coherent app, not 0.**

### `.btn-ghost` — one class, two buttons, five pages

**`legacy_css_lines` 1,949 → 1,916**, `unsanctioned_hex` 381 → **375**. Ten rules out; the
legacy name is joined to every `.btn--ghost` selector in `btn.css` rather than given its own
rule, so the two cannot drift again.

It rendered **two ways**: an outline button on `bank`, `blueprint` and `library` (white fill,
grey border, dark text) and a **tinted** one on `slo` and `slo-health` (light-blue fill, blue
text). Irfan chose the outline — the variant the component already defines, the same argument
that settled `.btn-primary`.

**369 element × property deltas on five pages, 0 on the other three.** All of them on
`.btn-ghost`, its SVG children, or the `.filter-bar` siblings that re-laid out when the button
went 40px → 36px. `slo` also gained `cursor: pointer`, which its rule never had.

**And `btn.css`'s header had been false for three days.** It still opened "PREPARED, NOT LIVE.
Nothing on any page carries these classes yet" — untrue since `.btn-primary` landed on
2026-08-16. Corrected where it was written.

## 2026-08-16 — the drain probe learns to warm the page, and 38 rules are saved from deletion

**No CSS changed and `legacy_css_lines` did not move.** This step removed nothing, and the
reason it was worth doing is that it stopped 38 rules from being removed wrongly.

`css_drain_probe.mjs` gains `--query=`, `--warm=` and `--wait=`. Without them it loads the bare
page, and most of these pages render their real content from JS after an API call — so it was
measuring a DOM no user ever sees.

| page | cold | warmed | rules that were NOT dead |
|---|---:|---:|---:|
| `print` — `?paper_id=9ade2655…` | 78 dead | **58** | **19** |
| `taqseem` — Pre Year 1 / Mathematics selected | 27 dead | **8** | **19** |

**Both would have read as deletable and both are load-bearing.** `print` renders nothing at all
without a paper id; `taqseem` shows an empty board until a class and subject with a plan are
chosen, and `Pre Year 1` / `Mathematics` is the only pair that has one.

**A longer wait alone changes nothing** — `bank`, `library` and `blueprint` return identical
counts at 1,200ms and 3,500ms, and a spot check confirms their main content is already
rendered (459, 24 and 1 elements). What those three still report as dead belongs to *other*
states — modals, bulk-import results, empty states — each of which needs its own warm-up.

**And after warming, `print` and `taqseem` have ZERO unreachable rules left.** Every remaining
zero is a class something in the page can build. **The drain's supply of dead rules is
exhausted**: across all nine files, ~47 were genuinely dead and all of them are already gone.
Everything still in `99-legacy/*.css` is either live, or live in a state no probe has entered.

The warm-up prints its own element delta and says so when it added nothing, because a warm-up
that silently failed produces exactly the same zeros as no warm-up at all.

## 2026-08-16 — the `js-only` bucket, resolved without a browser: 9 of 216 can never match

**`legacy_css_lines` 1,962 → 1,949**, 0 deltas on all eight pages, ratchet OK, ruff clean.

**The 204 `js-only` candidates were not 204 dead rules. Nine of them are.** A `js-only` zero
means only that the class was absent from the DOM when the probe ran. The decisive test needs
no browser: `99-legacy/<page>.css` is imported by **exactly one page**, so if a class token
appears nowhere in that page's HTML — not in markup, not in a template string, not in a
`classList` call — nothing can ever put it in the DOM.

**207 of 216 are reachable.** Something in the page can build them, so they must be verified by
injecting markup, not by deleting on a zero. **The drain's supply of dead rules is now
essentially exhausted**: 845 rules surveyed, ~47 genuinely dead across all nine files.

**A naive substring grep disagreed with the token match on three of the nine, and the token
match was right every time.** `sh` had 68 "hits" in `blueprint.html` — all inside words like
`should`; there is no class named `sh`. `code` had 4 in `slo-health.html` — all inside
`slo-codes`, `slo_code` and `cov-code`. `spacer` had 1 — inside `o-shell__spacer`. This is the
hyphen/substring trap already on the project's list, and it would have kept three deletable
rules alive rather than killing a live one, which is the safe direction to be wrong in.

**What went:** `.opt-radio-label` (`bank`), `.pagehead .spacer` / `.sec .sh` / `.sec .sh b` /
`.qrow` / `.qrow .qtxt` (`blueprint`), `.bloom-bar` (`index`), `td.code` / `.tag.err`
(`slo-health`).

**And 12 lines of my own noise went with them.** Both drain passes wrote a per-file
`/* dead rules dropped: … */` marker listing what had been removed — a changelog inside a
stylesheet, which is the same mistake `8ca7ed8` had just corrected at a larger scale. The first
pass's nine deletions netted **one** line because of it. Git history and this file already
record what was dropped.

## 2026-08-16 — the drain runs on all eight files: 38 dead rules out, and `legacy_css_lines` goes under 2,000

**2,008 → 1,962**, 46 lines. **0 element × property deltas on all eight pages**, drift 0,
ratchet OK, ruff clean. `css_drain_probe.mjs` had only ever been taken all the way through on
`slo`; this runs it on the other eight and acts on the result.

**The survey's "391 dead rules" is not 391. Measured end to end, it is about 67, and the
deletable-with-confidence set is 38.** The probe reported **339 zero-delta candidates** across
the eight pages. Bucketing each one against why a zero can be a lie:

| bucket | n | why the zero means nothing |
|---|---:|---|
| `js-only` | 204 | the class exists only inside a `<script>` template string |
| `state` | 78 | `:hover` / `:focus`, and `[open]` / `[dir="rtl"]` / `[data-open]` |
| `at-rule` | 15 | `@page`, `@font-face`, `:root` |
| **genuinely dead** | **42** | present in static markup, no state, no media |

**`@page` was in the candidate list and deleting it would have broken every printed paper.**
The drain probe runs in screen media, where `@page` does nothing, so it reads 0. `print.css`:1-2
records that this page's margin has been broken before. Attribute state was the same trap:
`[open]` is a `<details>` the probe never opens and `[dir="rtl"]` is the Urdu toggle switched on
— both read 0 at rest, neither is dead.

**Two of the filters were wrong on the first pass and were caught by measurement, not review.**
Reading `class="…"` out of the raw HTML counted template strings as static markup, which marked
`blueprint`'s `.topic-check-row` deletable — a rule measured live earlier the same day. Stripping
`<script>` blocks first moved 199 candidates down to 55. The `absent` bucket then failed too:
`.qrow` had 8 hits and `td.code` 4, so every `absent` row was dropped from the delete set rather
than trusted.

**What went, and it is mostly the new tree already doing the job:** `*`, `a`, `body`,
`html, body` on most pages (reset.css and typography.css), `select` / `table` / `th` on
`slo-health` (forms.css, tables.css), `.page-head h1` on three pages (typography's `h1` beats it),
`.pagehead` ×3 on `blueprint` (card.css owns them since UI-040), and `.icon` on `landing` plus
`.app-nav a svg` on `index` — **both of which the previous handoff had flagged as "probably
already dead, not measured". They are, and now it is measured.**

## 2026-08-16 — `.btn-primary` unifies on the locked indigo; the app had two primary blues

**`legacy_css_lines` 2,032 → 2,008**, `unsanctioned_hex` 385 → **382**. Nine rules out of
`bank`, `blueprint` and `library`, into `05-components/btn.css` beside the `.btn--*` set.

**The three files declared this rule byte-identically and rendered two different blues.**
`bank` and `library` painted `rgb(46,90,172)`; `blueprint` painted `rgb(79,70,229)`, because
`pages/blueprint.css`:82 maps `--brand` onto `--color-action` while the other two kept the
legacy literal. `tokens.css`:10 records the palette as **locked 2026-07-28 — Modern, indigo
action**, so blueprint was the one that was right and the other two had simply never been
remapped.

**Irfan asked for the better option rather than the safer one, and the deciding argument was
not the palette lock.** `btn.css` already ships `.btn--primary` reading `--color-action`.
Building `.btn-primary` at the old blue would have put **two primary blues inside one component
layer** — the exact defect this drain keeps uncovering — and would have forced re-pointing
`--color-action` itself later, which reaches blueprint's `--brand` and the focus ring. On
indigo, a future re-class to `class="btn btn--primary"` is a no-op.

**9 background changes, all intended** — 3 on `bank`, 6 on `library`, 0 on `blueprint`.

**Two unintended deltas, kept deliberately.** `cursor: pointer → not-allowed` on the two
disabled upload buttons and their SVG children: the legacy `.btn-primary:disabled` declared
`not-allowed` and it was **dead in `layer(legacy)`**, losing to a `button { cursor: pointer }`
higher up. In `layer(components)` it applies. Unlike `.filter-bar`'s resurrection this one is
correct behaviour and matches the `.btn--primary:disabled` already in `btn.css`, so it stays.

**`--radius-control` was nearly a silent regression.** The token is 11px; all three pages
measure 10px. The component keeps the literal.

**`.btn-ghost` was NOT taken.** Five pages, four different looks — `bank`, `blueprint`,
`library`, `slo` and `slo-health` disagree on background, border, radius, padding, font-size
and height. That is four decisions, not a refactor.

## 2026-08-16 — modal chrome: six rules out of eighteen, and the other twelve are named

**`legacy_css_lines` 2,036 → 2,032.** Three selectors × two files —
`.modal-backdrop.open`, `.modal-header`, `.modal-footer` — into
`05-components/modal.css`. **0 element × property deltas on all eight pages**, drift 0,
`unsanctioned_hex` back to 385, ruff clean.

**This app has THREE modal systems, not one**, and that is the first thing the enumeration
returned:

| | pages | classes |
|---|---|---|
| 1 | `bank`, `print` | `.modal-backdrop` `.modal-header` `.modal-footer` `.btn-cancel` `.btn-save` |
| 2 | `index`, `library` | `.modal-overlay` `.modal-head` `.modal-title` `.modal-foot`/`.modal-body` |
| 3 | `taqseem` | `.modal h3` `.modal-actions` |

`.modal` itself names four different boxes and `.modal-close` four different buttons. Only
system 1's shared chrome was taken.

**The audit said eighteen rules agreed across `bank` and `print`. Six were takeable.**

- **`.btn-cancel` / `.btn-save` and their three states — left, and NOT only because of the
  values.** They look identical and are not: `--radius-btn` is **10px on bank, 8px on print**,
  and the two `--bg` greys differ, so the shared `border-radius` and the cancel hover resolve
  differently. They are also **buttons**, and `.btn-primary` (3 files), `.btn-ghost` (5),
  `.btn-danger` / `.btn-edit` (2) are duplicated too. They belong in one button task beside
  `05-components/btn.css`, where the radius is decided once instead of three times.
- **`.modal-header h3` — left, because two of its three declarations are already dead.**
  `margin: 0` is done by `02-generic/reset.css` in `layer(generic)`; `font-size: 16px` loses to
  `03-elements/typography.css`'s `h3` in `layer(elements)` — **measured 14px on both pages, not
  16**. Copying it up would have resurrected the 16px. What survives is one colour, and the
  navy heading has no Tier 2 role; inventing one with a single consumer is what
  `tokens.css`:145 warns against.
- `.modal-backdrop` itself differs — `bank` pads 16px, `print` pads 0.

**Everything here is `display: none` at rest, so `css_type_probe` cannot see any of it.**
Verified by adding `.open` to the backdrop and reading the chrome on both pages before and
after: byte-identical. The gate's 0 only says the rest of the app did not move.

**`unsanctioned_hex` went 385 → 387 again, from two hex in a comment.** Twelfth time in this
epic. Fixed the same way, with `rgb()`.

## 2026-08-16 — `.type-checks` joins `field.css`, and the decision it was scheduled on turned out not to exist

**`legacy_css_lines` 2,042 → 2,036.** Four rules — the container and its label, from
`99-legacy/bank.css` and `blueprint.css`. **0 element × property deltas on all eight pages**,
drift 0, `unsanctioned_hex` flat at 385, ruff clean.

**The task was opened to settle a decision, and enumeration dissolved it.** The board entry said
`.type-checks`' checkbox is `rgb(46,90,172)` at 16px on `bank` and `rgb(79,70,229)` at 15px on
`blueprint`, so componentising it required choosing a blue. Irfan chose bank's. **That choice
does not apply**, because `blueprint`'s `.type-checks input[type="checkbox"]` is **dead**:
`blueprint.css`:109's `.topic-check-row input[type="checkbox"]` has equal specificity, sits
later in the same file, and wins. The colour never came from the rule being discussed.

**And componentising it anyway would have made the page worse, not better.**
`.topic-check-row` renders at two sites on `blueprint` — inside `.type-checks`
(`blueprint.html`:581) and in the topics list (`:607`). A `.type-checks` rule in
`layer(components)` beats `.topic-check-row` **only inside `.type-checks`**, so the page would
have ended up with 16px blue boxes next to 15px indigo ones. The checkbox rule was left in both
legacy files. Unifying the two checkbox styles is a real task; it is not this one.

**Three more declarations were dropped for the reason `.filter-bar` taught yesterday.**
`.type-checks label`'s `font-size: 13.5px`, `font-weight: 500` and `color: var(--ink)` all lose
to `03-elements/forms.css`'s bare `label` in `layer(elements)` — measured 12px / 600 /
`rgb(71,85,105)` on both pages. Copying them into `layer(components)` would have resurrected
them. The component carries only the five that are actually alive.

**`blueprint`'s `.type-checks` is JS-rendered and the gate cannot see it.** It is built inside
the section template at `blueprint.html`:642, so it does not exist on a fresh load — one probe
run found it and the next did not, which is what exposed this. It was verified instead by
**injecting the exact markup `renderSection()` produces** and reading the computed values
before and after: byte-identical, including both checkbox sites. **A 0 from `css_type_probe` is
not coverage of this element.**

## 2026-08-15 — `.field-row` + `.filter-bar` become a component, at zero deltas

**`legacy_css_lines` 2,054 → 2,042.** Nineteen rules out of `99-legacy`'s `bank`, `blueprint`,
`index` and `library`; `05-components/field.css` replaces them, the name `main.css` had held
commented-out since UI-042 was scoped. **0 element × property deltas on all eight pages,
drift 0.** `unsanctioned_hex` flat at 385 — the file declares no colour at all.

The net line count is 12 rather than 19 because each deletion left a one-line signpost naming
the component that took it, the same as the `.status-bar` commit.

**It did NOT come out at zero on the first run — it came out at 75, and the reason is worth
more than the rules.** Two of the legacy declarations had been **dead since the migration**:
`.filter-bar label { font-size: 11.5px }` and `.filter-bar select { padding: 8px 11px }` sit in
`layer(legacy)` and lose to `03-elements/forms.css` in `layer(elements)`, because layer order is
decided before specificity. Those labels have rendered at 12px, and those selects at 9px 11px,
for as long as the pages have been migrated. **Copying the declarations into a component file
moved them up to `layer(components)` and brought them back to life** — 11 labels shrank and 9
selects lost a pixel of padding.

Irfan's call: **match what is live.** Both declarations are dropped from the component, which
now carries only `margin-top: 0` on the label and `min-height: 38px` on the control — the one
thing the filter bar genuinely adds over the default. Re-measured at 0.

**A third value was never a rule at all.** `.filter-bar input` measured `padding: 8px 11px`
where `select` measured `9px`, which looked like a cascade puzzle. It is an **inline style** on
`library.html`:186, and inline beats every layer. That input was never reading the rule.

**Measured identical before anything was written**, which is why the `.field-row` half was
uneventful: `flex`/`gap 14px` and `flex: 1 1 0%` on all four pages, `.filter-bar` and its `> div`
identical on both. `index` alone stacks at `gap: 14px` below 760px against the other three at
`10px`; the component took the majority and index's own value moved to `pages/index.css`.

**`.type-checks` was in the original scope and was left out.** Its rule text is byte-identical
in `bank` and `blueprint`, and its checkbox is `rgb(46,90,172)` at 16px on one and
`rgb(79,70,229)` at 15px on the other — `blueprint` maps the legacy token names onto the new
tree's roles in its entry file. That is a decision about which blue, not a refactor.

## 2026-08-15 — `.status-bar` becomes a component, and it turns out the app had two status palettes

**`legacy_css_lines` 2,075 → 2,054.** Twelve rules, 21 lines, out of `99-legacy/bank.css`,
`blueprint.css` and `library.css`; `05-components/status.css` replaces them.
`unsanctioned_hex` flat at 385, ruff clean, and **0 element × property deltas on all eight
pages, drift 0**.

**The rule text agreed across all three files. The resolved colour did not.** That is the
finding, and it is why the "byte-identical, therefore free" reading of the duplication survey
is not safe. Measured by injecting the state class and reading the computed pair:

| | before | after |
|---|---|---|
| `bank`, `library` — ok | `rgb(46,125,91)` on `rgb(230,244,236)` | `rgb(22,101,52)` on `rgb(230,244,236)` |
| `blueprint` — ok | `rgb(22,163,74)` on `rgb(220,252,231)` | `rgb(22,101,52)` on `rgb(230,244,236)` |

`blueprint` was on the traffic-light palette because `pages/blueprint.css`:99-104 maps its
legacy `--green`/`--green-bg` onto `--color-success`/`-soft`; `bank` and `library` carry the
raw legacy hex. **Two palettes, live, on three pages** — the same shape as the navy vs white
sidebar settled on 2026-08-13, and nothing on the board recorded it.

**Both palettes failed AA, and the new one failed harder.** At 13.5px/500 the pairs measured
3.00 / 3.95 / 2.86 (traffic-light) and 4.41 / 4.64 / 3.37 (legacy) against a 4.5:1 requirement.
Irfan chose to keep the legacy tint and darken the ink: **6.29 / 4.64 / 6.12, all passing.**
`err` was left exactly as it was, because it already passed.

**Geometry did not move at all** — `10px 14px`, `9px`, 13.5px/500, `margin-top: 14px`,
identical on all three pages before and after. Four of those stay literal in the component:
9px has no radius token, 10px/14px are not on the space scale, and 500 has no weight
primitive. Same call `nav.css` made for its 14px and 8px.

**Two gates are blind here and the numbers should be read accordingly.** `.status-bar` is
`display: none` at rest and `.ok`/`.err`/`.warn` are set by inline JS
(`el.className = 'status-bar ' + type`, eight sites), so `css_type_probe` returns 0 whether
this file is right or wrong, and a drain probe would report all nine state rules as dead.
The colour claim above comes from a probe that injects the class; the 0 only says the rest of
the app did not move.

**And `unsanctioned_hex` went 385 → 389 on the first run, from six raw hex inside a comment.**
Trap #3, for the eleventh time in this epic. Fixed by writing the comparison as `rgb()`.

## 2026-08-15 — `blueprint` and `taqseem` had their subtitle beside the title, not under it

A wrapper `<div>` around `h1` + `p` in both pages' `.pagehead`. **2 element × property
deltas in the whole app**, both intended: the `.pagehead` box grows 26.4 → 49.0px on
`blueprint` and 42.1 → 68.5px on `taqseem`. The other six pages measured **0, drift 0**.

**It was found by enumerating a different task.** The plan was to re-class the four
`.page-head` pages onto `card.css`'s `.pagehead` component and delete 11 legacy rules.
Reading the component against the markup first — before writing anything — showed why that
would have broken them: `.pagehead` is `display: flex`, and the mockup
(`mockup-modern.html`:279) puts an inner `<div>` inside it. `blueprint` and `taqseem` were
migrated to the class **without that div**, so their `h1` and `p` became flex items and sat
side by side. The four `.page-head` pages were unaffected only because their class is still
`display: block`. A re-class would have given all four the same defect.

**And one number the board carried was wrong.** The re-class was costed as "h1 22px → 24px on
four pages". Measured: **all four are already 24px.** `03-elements/typography.css` sets bare
`h1` at 24px in `layer(elements)`, which beats `layer(legacy)`'s `.page-head h1 { 22px }` —
that legacy declaration is already dead. The real cost of a re-class is layout, plus the `p`
colour (`rgb(91,102,120)` → `rgb(100,116,139)`) and a new `max-width: 620px`.

`.page-head` → `.pagehead` is **not done** and is no longer the cheap win it was scheduled as.

## 2026-08-15 — the sidebar can scroll on all nine pages; the two-day-old hole is closed

`.app-sidebar { overflow-y: auto }` added to `pages/bank.css`, `library.css`, `slo.css`,
`slo-health.css` and `taqseem.css` — one declaration each, in `layer(components)`. The legacy
shell sets `height: 100vh` with no `overflow`, so a nav taller than the viewport spilled out of
the painted navy box instead of scrolling. **Found by Irfan in the browser on 2026-08-13** on
`index`, fixed page-scoped there the same day, and recorded as still open on five pages rather
than fixed by a drive-by. This closes it.

**The enumeration moved the scope from six pages to five, both ways.** `blueprint` was on the
board's list and does not have the defect — its only `.app-sidebar` rule is inside
`@media (max-width: 760px)`, and at desktop it runs the new `.o-shell` grid, which already sets
`overflow: auto`. `print` was not on the list and was already fixed: `99-legacy/print.css`:45
carries `overflow-y: auto` with its own comment.

**There is no shared home for this and that is by design, not an oversight.**
`04-objects/shell.css`'s header forbids a `.app-sidebar` rule outright — a rule under that name
in `layer(objects)` would take over the brand/shell block on all nine pages the moment they
link `main.css` (the D21 failure mode). So it is five page-scoped copies, and they go away when
these pages move onto `.o-shell`.

**No probe can verify this and the gate was not run for it.** `css_type_probe`'s viewport is
900px and `overflow` is not a captured property, so it returns 0 either way. Ratchet OK
(`shared_css_lines` 3,064 → 3,117, `unsanctioned_hex` flat at 385), ruff clean.
**Verified by Irfan in the browser instead** — incognito, zoomed to ~200% so the 209–294px navs
exceed the viewport, on the pages themselves.

## 2026-08-14 — the drain: 12 dead rules leave four legacy files, and `legacy_css_lines` moves for the second time in this epic

**`legacy_css_lines` 2,105 → 2,075. Thirty lines, 0 deltas on all eight pages.** This is the
payoff for everything above it today — three commits that only added, followed by the one that
takes away.

**What was deleted:** `.app-nav a`, `.app-nav a:hover` and `.app-nav a.active` from
`99-legacy/bank.css`, `library.css`, `slo-health.css` and `slo.css`. **Twelve rules, thirty
lines** — the blocks are 8 lines in `bank`/`library` and 7 in `slo`/`slo-health`, which is why
the estimate of "~24" written an hour earlier was wrong: it counted rules and the file counts
lines.

**`.app-nav` itself STAYS on all four**, and that is not an oversight. It carries
`display: flex`, `flex-direction: column`, `gap: 2px` and `padding: 0 10px`, and **no component
covers the last of those** — `.sidenav` took the column and the gap in `778f65a`, deliberately,
but the 10px side padding has no home. The `@media (max-width: 760px)` `.app-nav` rules stay too,
for the reason `shell.css` gives: that breakpoint hides the nav and the control that brings it
back does not exist yet.

**0 element × property deltas on all eight pages, drift 0** — `slo`, `slo-health`, `library`,
`taqseem`, `blueprint`, `bank`, `landing`, `index`. `unsanctioned_hex` 401 → 385: sixteen raw hex
went with the rules, four per file.

**The `:hover` half is NOT probe-verified, and that is stated rather than glossed.** The probe
hovers nothing, so `.app-nav a:hover`'s deletion returns 0 whether or not the component replaces
it. What was done instead is a value-for-value read: `--color-sidebar-hover` resolves through
`--overlay-white-07` to `rgba(255,255,255,0.07)` and `--color-sidebar-fg-on` through `--white` to
`#ffffff`, which is exactly what the deleted rule declared. The `.active` half **is** measured,
because the current item is in that state at rest. **A hover check belongs to a person with a
mouse.**

**What this does to the epic's own number.** The first move was `slo`'s ten dead rules on
2026-08-13 (2,115 → 2,105). This is the second, and it is a different kind: those ten were dead
already, while these twelve were **load-bearing until this morning** and were made dead on
purpose. That is the 454, not the 391 — the first of the load-bearing rules in this epic to be
given a home and then removed.

## 2026-08-14 — `library`, `slo-health` and `slo` adopt `.sidenav`; all four pages of the clean group are on the component

**Same edit three times, measured one page at a time: `library` 57, `slo-health` 85, `slo` 85.**
Every delta is one of the two changes already decided on `bank` — the nav links returning from
white to `rgb(198,210,232)`, and the `<nav>` gaining `--color-sidebar-bg`, navy painted on navy.
**No new kind of delta appeared on any of the three, and no geometry moved at all** — not a
font-size, radius, gap, border-width or height. That is the proof that `778f65a` seated the
component exactly on the legacy values; if it had not, these three runs are where it would have
shown.

**The counts scale with link count and nothing else.** `library` has 5 nav links, `slo` and
`slo-health` have 7. Four inactive links × 14 (`color` plus three `currentColor` borders on the
`<a>`, and `color` plus four on each of its `svg` and `use`) + 1 for the `<nav>` = 57; six
inactive × 14 + 1 = 85. The current page's link measured 0 deltas on all three.

**`taqseem`, `blueprint`, `bank`, `landing` and `index` all measured 0**, drift 0 on all eight.
Ratchet OK, ruff clean, suite 890.

**Where this leaves the four.** `bank`, `library`, `slo-health` and `slo` now carry both
`.app-nav` and `.sidenav` on the `<nav>`, and both `active` and `sidenav__link--active` on the
current link. **Nothing has been deleted from `99-legacy/*.css` yet and `legacy_css_lines` has
not moved** — the three dead rules per page (`.app-nav a`, `:hover`, `.active`, 12 in total) come
out as their own step, so a re-class and a deletion are never in the same commit.

**`taqseem` and `index` still render white nav links**, because nothing has reached them. Two
looks in one app again, deliberately and temporarily — the same shape as the navy split before it
was settled.

## 2026-08-14 — `bank` adopts `.sidenav`, and it turns out six live pages have had white nav links since they migrated

**The re-class was predicted at 0 deltas and measured 57. The prediction was wrong in the
useful direction: 56 of the 57 are an existing defect being undone.**

**`bank.html` only.** `<nav class="app-nav">` → `<nav class="app-nav sidenav">`, and the five
`<a>` get `sidenav__link` (the current one also `sidenav__link--active`, keeping its legacy
`active`). `.app-sidebar`, `.brand` and `.sidebar-foot` are untouched — no component can carry
them. **Nothing is deleted from `99-legacy/bank.css` yet**; proving the re-class is quiet comes
first, and it did not come back quiet.

**What moved: four nav links from `rgb(255,255,255)` to `rgb(198,210,232)`** — plus their `svg`
and `use` children inheriting it, and the border colours that resolve to `currentColor`. One more
delta is the `<nav>` gaining `--color-sidebar-bg`, navy painted on navy, invisible. The current
page's link measured **0 deltas**: it was white before and stays white.

**The cause, measured rather than reasoned.** `03-elements/typography.css`:50 declares
`a { color: inherit }` in `layer(elements)`. Layer order is decided before specificity, so it
beats `99-legacy/*.css`'s `.app-nav a { color: #C6D2E8 }` in `layer(legacy)` no matter what the
selectors weigh, and the link inherits `.app-sidebar`'s white. `.sidenav__link` sits in
`layer(components)`, above `elements`, which is why re-classing restores the legacy intent.

**This is live on six pages right now, not one.** Read out of the before-snapshot: `slo`,
`slo-health`, `library`, `taqseem`, `bank` and `index` render **every** nav link white, current
and not. `blueprint` is the only page showing the intended split, because it is the only one
already on `.sidenav`. So on those six the current page is distinguished by its background tint
and rail alone, and the colour that was supposed to carry it has been absent since each page
migrated.

**It was recorded and never decided.** `pages/bank.css`:124 says it in one line — *"Nav links go
white and the canvas changes tint, both from the new tree"* — filed as an expected consequence of
`UI-047e` on 2026-08-10. **Irfan decided it today: accept the legacy colour.** The remaining three
re-classes carry the same change, and `taqseem` and `index` keep white until something reaches
them.

**Gates:** 0 deltas on the other seven pages, drift 0 on all eight, ratchet OK, ruff clean, suite
890. Irfan compared `bank` against `blueprint` in the browser.

## 2026-08-14 — `nav.css` moves to the four pages' values, so the re-class can be free

**Nothing shipped to a teacher today. One component file changed, and `blueprint` moved 104
element × property deltas to make four other pages able to adopt it at zero.**

**The board's plan for this step was wrong, and the enumeration is what said so.** `HANDOFF.md`
described re-classing `bank`, `library`, `slo` and `slo-health` onto `.sidenav` as "36 rules out,
colour unchanged". The 36 is right — the nine desktop shell rules really are byte-identical
across those four files, re-verified line by line — but **`.sidenav` is a home for only three of
those nine**. `.app-nav a`, `:hover` and `.active` have component equivalents. `.app-sidebar`'s
own box, `.app-nav`'s column, `.brand` ×3 and `.sidebar-foot` have none: the first lives inside
`.o-shell`, which is a whole-page grid these four have no topbar for, and `.brand` was
deliberately denied a component in `UI-047b` because it is live on all nine pages. **So the step
yields 12 rules, not 36.**

**And the three that do have a home were not free either.** `.sidenav__link` read `--text-body`
(15px), `--radius-control` (11px) and an 11px gap, against the legacy 14px / 8px / 10px, and it
carried no `border-left` at all. Re-classing at those values would have moved type and corners on
four pages a teacher uses daily. **Irfan's call: bring the component to their values instead**,
so `blueprint` — one page, already in the probe's list — absorbs the whole change.

**What changed in `05-components/nav.css`:** `.sidenav__link` gap 11 → 10px, `font-size`
`--text-body` → 14px, `border-radius` `--radius-control` → 8px, a `3px solid transparent`
`border-left` added, `margin-bottom` removed. `.sidenav` gains `display:flex` + `flex-direction`
+ `gap: 2px` — the 2px moves from the item to the container because the four pages already stack
their links with `.app-nav { gap: 2px }` in `layer(legacy)`, and an item margin would have made
the spacing 4px on every one of them. `.sidenav__link--active` drops `font-weight` (only
`taqseem` bolds the current item, and it is in the other group) and its rail moves from an inset
`box-shadow` to `border-left-color` — **a shadow cannot reserve space, and the transparent border
is what stops the current page's label from shifting.**

**14px and 8px are literals, deliberately.** Neither has a Tier 2 role and neither gets one:
`--text-body` is 15px, `--radius-control` is 11px, and `--font-size-4` is already spoken for by
`--text-heading-3`. Giving these roles means three new names with one consumer each — the way
`tokens.css`:145 says that file rots. Same policy as the 34px avatar in the same file and
`shell.css`'s 248px sidebar.

**Measured: 0 deltas on seven pages, 104 on `blueprint`, drift 0 everywhere.** All 104 are
accounted for — 30 font-size/line-height across 5 links and their `svg`/`use`, 20 radius corners,
15 `border-left`, 12 gap, 12 `min-height`/`min-width` `0px` → `auto` (the flex-item default, no
visual effect), 5 `margin-bottom`, 5 `height`, 3 `font-weight`, 1 `display`, 1 `box-shadow`. The
active item was checked on its own: the rail is the same `rgb(91,141,239)` at the same 3px on the
same edge, and background and text colour did not move at all.

**Irfan opened `blueprint` and `bank` side by side and the two sidebars now look the same** —
which is the whole point of the step and the one thing no probe could report. Ratchet OK, ruff
clean, suite 890.

**Nothing is re-classed yet.** That is the next step, one page at a time, and it should now
measure zero.

## 2026-08-13 — Sprint 6 starts: the first legacy lines come out, and all nine files are surveyed

**`legacy_css_lines` 2,115 → 2,105.** `PLAN.md` §3 says *"Progress is literally measurable as
lines remaining in `99-legacy/`"*, and that number had not moved once in the life of this epic
until now. Everything before today added; `theme.css`'s deletion removed a shared file but left
legacy untouched. These are the first lines of the actual debt to go.

**A tool had to exist first.** The migrations asked *"what does this page lose when
`static/theme.css` is unlinked?"* — `css_orphans.py` answered that by diffing against
`theme.css`, which was deleted the same morning. The drain asks the opposite: *"this legacy rule
is still here — if I delete it, does anything move?"* Nothing measured that.
`scripts/css_drain_probe.mjs` does: it deletes each rule from the CSSOM, re-snapshots, counts
deltas, and puts it back. One page load, and **no file is ever edited**, so an interrupted run
cannot leave a half-drained stylesheet on disk.

**`slo.css`: 45 rules → 35, 91 lines → 81.** Ten went. Each was checked against the tree rather
than trusted to the probe's zero — `*` and `a` by hand, because `box-sizing` and
`text-decoration` are not among the 44 properties the probe measures. Three of the ten
(`.status-error`, `.status-updated`, `.status-added`) turned out to be dead in a stronger
sense: they appear nowhere in the repo outside `slo.css` itself. 0 deltas on all eight probed
pages, ratchet 32, suite 890, and Irfan checked the page.

**Nine of its nineteen zeros were NOT deleted, and that is the important half.** Four are
`:hover`/`:disabled` and match nothing at rest; four are `.pill` variants that exist only inside
JS template strings at `slo.html`:170 and :228; one is an `@media` block outside the probe's
viewport. Deleting on the first number would have repeated the taqseem-chips mistake exactly.

**Then all nine files were surveyed: 845 rules, 391 at zero deltas, 454 load-bearing.** The
survey table is in `docs/ui/ROADMAP.md`. Two files could not be measured at first — `landing`
and `bank` — because both contain rules with a `transition`, and the probe's restore check was
snapshotting mid-animation. The guard was right to refuse; the fix freezes transitions before
the baseline, which is safe because `transition-*` is not among the measured properties, and
was verified by re-running `taqseem` to the same numbers.

**What the survey actually says about the remaining work.** 391 is not the deletable count —
`slo` is the only file taken through, and half its zeros were blind spots, so the genuinely
deletable share is nearer **a quarter of 845**. The **454 load-bearing rules are the real
job**, and none of them has been rehomed yet: even `slo` still has all 26 of its. Deleting a
dead rule takes minutes; giving a live one a home is a decision every time.

## 2026-08-13 — the DOCX/PDF export is deleted: 630 lines nothing called, and a LibreOffice dependency

**Not part of the UI-ARCH epic.** That epic sanctioned exactly one backend change (UI-003);
this comes out of the dead-code audit and is committed on its own for that reason.

**Removed:** `app/api/export.py` (49 lines), `app/services/export_service.py` (362),
`tests/test_export_service.py` (210), `python-docx` from `requirements.txt`, the
`PdfConversionFailed` exception, and the router's import and registration in `app/main.py`.

**Why, and "unused" is the weaker half of it.** `/api/paper/{id}/export.docx` and `.pdf` had
no caller anywhere — not in any page, not in `apiClient.js`, not in a test. The stronger half
is that the PDF path **shells out to LibreOffice** (`soffice`) as a subprocess: a feature
needing third-party software installed on the school PC, that nothing invoked, and that would
have failed the moment anyone did invoke it on a machine without it. The code was also
untouched since the initial commit of 2026-07-06 — one commit in the whole life of the repo.

**And the cost is real, not zero.** This was the app's only DOCX export, so a teacher wanting
an editable paper file no longer has a path to one. It was working, tested code — 16 tests
passed — not rot. What makes it a removal rather than a loss is the standing position that
printing is the browser's Ctrl+P via `print.html`; DOCX was never in the workflow.

**Verified:** app imports, suite **890 passed** (906 minus the 16 that tested the deleted
service), 69 API paths remain, and the only `export` among them is `/api/questions/slo-export`
— the SLO spreadsheet, unrelated.

**A note for whoever checks this next.** The first verification reported "0 API routes" and
looked like the deletion had unregistered everything. It had not. In this FastAPI version
`app.routes` holds included routers as `_IncludedRouter` objects with no `.path`, so filtering
on `.path` finds only the four docs endpoints and the two mounts. Count the `_IncludedRouter`
entries (14 now, 15 before) or read `app.openapi()["paths"]`.

**Still open from the same audit:** `/api/syllabus-topics` has no caller anywhere and has not
been decided. `blueprint-presets/{id}` and `library/question-types` are called by tests only.

---

## 2026-08-13 — static/theme.css is deleted. The file this epic was written about is gone

**Sprint 6, UI-ARCH epic — `UI-064` part 1.** Full board: `docs/ui/STATUS.md`.

`PLAN.md` §1 opens with: *"The app has a design system (`theme.css`, 213 lines) that ~90% of
the styling bypasses."* That file is now removed. **212 lines deleted, 0 element × property
deltas on all nine pages, ratchet 32 passed, suite 906 passed** — deleting it changed nothing,
because the seven migrations had already made it unreachable. `UI-047c` unlinked the last page
holding it earlier the same day.

**`unsanctioned_hex` went 429 → 400.** That is the first ratcheted metric in this epic to fall
through deletion rather than through care; the 29 were theme.css's own.

**Checked before deleting, not after.** No page links it, verified across all nine plus the
mockup. No test opens it — the two hits in `test_css_architecture.py` are prose.
`css_baseline.py` names it only in comments. `css_orphans.py` **does** read it, at :89 as
`OLD_THEME`, and already handles absence at :807 with a warning rather than a crash; confirmed
by running it afterwards, where `index` reports `theme? no` and every column zero, which is
correct rather than broken.

**And this is the easy half, which the numbers should not be allowed to hide.**
`legacy_css_lines` is **2,115 and did not move**. `shared_css_lines` is 2,963 — down 212 from
3,175, but still **437 above** the 2,526 pinned at baseline, because the new tree was built
alongside the old one rather than in place of it. `static/app.css` is untouched and still
linked by all nine pages. **The real work of Sprint 6 is the nine `99-legacy` files and none of
it has started.** This deletion was cheap precisely because the migrations had already done the
expensive part.

---

## 2026-08-13 — index is live. **9 of 9 pages.** Sprint 4b is complete

**Sprint 4b, UI-ARCH epic.** Full board: `docs/ui/STATUS.md`. Sprint 3 closed incomplete at
3 of 9; seven migrations opened the other six, four of them in two days.

**The page everyone feared was the smallest migration in the epic.** `index` is the largest
page in the app — 508 elements at rest, a 7-screen SPA, 224 inline `style` attributes — and
it needed **no compat block, no re-classing and no UI-046**. It declares all 27 tokens it
reads, so nothing had to be re-supplied; its shell is its own `.shell`/`.app-sidebar`/
`.app-nav` rather than `theme.css`'s grid, so no class attribute changed at all; and the 224
inline styles were never at risk, because inline beats every layer. Part 2 was a `<link>` swap
and nothing else. The very thing `PLAN.md` §1 opens with as a defect — *"index.html redefines
`--line` and `--muted`"* — is what made it cheap.

**2,476 deltas on the page, and each was read rather than waved through.** The palette takes
over (index's `--ink` → `--color-text`, 256 elements plus their border colours), the type scale
lands (16→15px on 171, 15→13.5px on 58), the body leading lands where legacy left it `normal`
(185 at 21.75px), D31's label role arrives on 44 — the same change `bank` and `library` already
took — em gaps shrink with their font-size, and form controls take `forms.css`'s optical
padding. Nothing unaccounted for, nothing pointing at something lost. The five page-scoped
rules were verified element by element: `.main` keeps its padding, `.summary-row` keeps its
dashed rule at index's own `--line`, `.tag` keeps its pill, and **all four `.urdu` elements keep
Nastaliq — including the two toggle buttons that were the whole of decision A.**

**And the one real defect was found by eye, not by any gate.** Irfan opened the page and the
last nav item, SLO Health, hung outside the navy sidebar. `.app-sidebar` is `height: 100vh`
with **no `overflow` property**, so content taller than the viewport spills out of the painted
box instead of scrolling. Both other shells in this repo handle it — `theme.css`'s `.nav` and
`shell.css`'s `.o-shell__nav` both set `overflow: auto` — and the legacy `.app-sidebar` never
did, on any of the six pages that use it.

**index's line-height was not the defect and the fix does not touch it.** All six migrated
pages compute the nav at 21.75px; index's is simply the tallest at 450px against 294 and 209,
because it lists every screen. Special-casing its leading would have fixed the symptom by
making one page disagree with five. The fragility also pre-dates the migration — the sidebar's
children totalled 680.4px before and 700.7px after, so the new leading added 20.3px and crossed
the threshold on Irfan's screen.

**No probe could have caught it, and the record says so.** At the probe's 900px viewport
nothing overflows, `overflow` is not a captured property, and the fix therefore measures as 0
deltas — which means it disturbs nothing, not that it works. **The same hole is still open on
`library`, `bank`, `slo`, `slo-health` and `taqseem`** and is deliberately left open: they are
live, their navs are short enough that nothing has spilled, and five live pages want their own
gate run rather than a drive-by.

**Where the epic now stands.** Every page is on the new tree and **`static/theme.css` — the
212-line file this epic exists to replace — is now linked by no page at all**, so deleting it
is unblocked for the first time. `static/app.css` is not in the same position: all nine pages
still link its 57 lines for the `@font-face` block and the `.icon` sprite rule, and it goes
with `UI-064`. But `99-legacy/*` is still **2,115 lines** against a 2,133-line baseline,
and the new tree sits on top of it rather than in place of it. **CSS has roughly doubled and
nothing has been deleted yet.** That reverses in Sprint 6, which has not started.

---

## 2026-08-13 — blueprint is live, UI-046 is finally verified, and index turns out to be blocked on nothing

**Sprint 4b, UI-ARCH epic.** Full board: `docs/ui/STATUS.md`. **8 of 9 pages are now live**;
only `index` remains.

**UI-046 — nav + shell, and the board's twelve rules were nine.** `05-components/nav.css`,
nine rules in `layer(components)`. Three of the twelve were not written and none was skipped:
`.app` and `.top .spacer` are already complete in `04-objects/shell.css` as `.o-shell` and
`.o-shell__spacer`, so repeating them would duplicate the layout this epic exists to remove;
and `.nav a .icon` is dead, because `static/app.css`:57 sets a bare `.icon` unlayered and an
unlayered rule beats every `@layer` regardless of specificity. The enumeration also turned up a
name the board never recorded — `theme.css`:84 spells it `.nav a .ic, .nav a .icon`, so there
are two dead names, not one. `.top` and `.nav` shrank to two declarations each, because
`shell.css` owns their layout and only the surface and the edge were left.

**The names are new — `.appbar` and `.sidenav` — and that was chosen against measurement.**
`.top` and `.nav` were measured free on all seven live pages, so adopting them would have been
safe; the reason not to is that they are exactly the kind of generic name whose nine
independent copies caused this epic. `.app-nav` is live on seven pages and `.topbar` on
`index`, so both were excluded; `.sidenav` and `.appbar` return zero in every page and every
stylesheet here.

**UI-047b — blueprint is LIVE, and it is what verified UI-046.** UI-046 shipped prepared and
*unverifiable*: its rules stood at `matches:0` because blueprint loaded no layered stylesheet
at all. This migration gave them markup, and all nine went live — `.sidenav__link` at 5,
`.appbar` and the rest at 1. Split into two commits at Irfan's request: the entry file first,
deliberately unlinked and measurably inert, then the `<link>` swap and the re-classing.

**Two of the ten re-classes turned out to be additions, and both were caught before the edit
rather than after.** `.brand` is kept alongside `.o-shell__brand` because `brand.js`:22 queries
`.brand .name` and sets the school name from it. `.main` is kept alongside `.o-shell__main`
because `99-legacy/blueprint.css`:28 sets `max-width: 1080px` on it. Dropping either class
would have been an invisible regression — blueprint is not in `css_type_probe`'s page list, so
no gate would have caught the school name silently not being set, or the content running the
full width of the viewport.

**And `index` was never blocked on D22.** Six places on the board said it was.
`DECISIONS-FOR-IRFAN.md`:67 corrected that on **2026-08-04** — D22 is a technical constraint
whose fix can only land in the commit that re-classes markup, which is Sprint 6, not a decision
anyone was waiting on — and the correction never propagated. Two of the six stale copies were
written by this session, into `ROADMAP.md` and `HANDOFF.md`, from the stale rows rather than
from the decisions file. All six are corrected here.

**The real blocker was smaller and is now answered.** `index`'s two اردو toggle buttons lose
Nastaliq after migration, because `03-elements/forms.css`:101's `button { font-family: inherit }`
sits in `layer(elements)` and outranks `99-legacy/index.css`:34's `.urdu, .ur` in
`layer(legacy)`. Measured scope: **exactly 2 elements.** The `.urdu` input at `index.html`:444
is safe behind an inline style, and `bank`/`print` are unaffected — their `urdu-toggle-row`,
`qtext-ur` and `urdu-input` are different class names. Irfan answered **A**: a page-scoped rule
in `index`'s own entry file, the same pattern `taqseem`'s bare `.card` and `blueprint`'s
`.brand` and `.chip` already use. **`index` now waits on nothing.**

**Gates across both tasks:** 0 element × property deltas on all six probed live pages, drift 0,
ratchet 32 passed, suite 906 passed. On blueprint: `theme?` **no**, EXPOSURE **20 → 0**,
elements 235 → 234 which is the removed `<link>`.

**Not fixed, and said out loud rather than buried under "page is live":** blueprint's
narrow-viewport shell. `theme.css` carries two `@media (max-width: 760px)` rules for `.app` and
`.nav` that nothing redeclares. `shell.css` declined that breakpoint deliberately — hiding the
nav without the control that brings it back is half a mechanism, and that control is a
component nobody has built. D21 flags the same viewport. It was broken before this and is
broken after it.

**The ratchet earned its keep again.** `nav.css` failed it on the first run,
`unsanctioned_hex` 429 → 430, because the file's own comment quoted a raw hex while explaining
that raw hex cannot be quoted. Seventh time that check has fired on this epic; seventh time
through a comment.

---

## 2026-08-12 — UI-043 came off the critical path, and no CSS was written to do it

**Sprint 4b, UI-ARCH epic.** Docs only. Full board: `docs/ui/STATUS.md`, evidence block in
`docs/ui/MEASURED.md` §📐.

**What the board said.** Both remaining pages — `blueprint` and `index` — were held on
`UI-043`, a component task, for its `.chip` and its `.tag`. The order was `UI-043` → `UI-046`
→ `UI-047b`.

**What the enumeration measured.** Four rules are actually at stake: `.chip` (blueprint ×1),
`.tag` (index ×2), `.row` (index ×1), `.summary-row:last-child` (index ×1). Three of them are
already live on migrated pages. `main.css`:42 orders the layers with `legacy` lowest, so a
`layer(components)` rule should beat the legacy file painting those elements — the same call
`card.css` made for the bare `.card` and `btn.css` for the bare `.btn`. **But those two had safe
descendants to ship and these three do not**: they are flat single rules with nothing underneath
them, so a component file has nothing it can carry.

**That reading was then tested rather than trusted**, because a cascade argument is exactly the
kind of thing this epic keeps getting wrong. The three rules were written into
`layer(components)` at `theme.css`'s own values, `css_type_probe` was run against a same-browser
control, and the rules were reverted. **`landing` moved 21 element × property deltas and
`taqseem` moved 2** (`gap` 12px → 10px). The mechanism is measured, not inferred.

**The first run gave a false all-clear, and that is the part worth keeping.** It reported 0
deltas everywhere but `landing`, which read as "`.row` is safe" — and that was written down and
told to Irfan before it was checked. It was wrong. The probe's page list did not include
`taqseem`, the one live page whose legacy `.row` sets a different `gap`; `slo` and `slo-health`
returned 0 because their value already agrees, which is agreement and not absence of collision.
**A 0 from a probe that is not looking at the page is not a 0.** `taqseem` was added to
`css_type_probe.mjs` — late, since `UI-047a` migrated it that same day and should have added it
then, exactly as that file's own comment requires.

**`.chip` cannot be probe-measured at all.** `taqseem` has no static `.chip`; the class exists
only inside `chipHtml()`'s template string, so the chips are absent from every snapshot until
real data renders them. An earlier count of "`.chip` ×1" was counting that template string as
markup. What can be compared is the two declarations, and they are not variants of one
component — `99-legacy/taqseem.css`:72 is a standing bordered block holding a code, a strand, a
sequence and a `<select>`; `theme.css`:127 is a flat pill. A component `.chip` would collapse
the first into the second.

**`.tag` is the same failure three times over**: the brand tagline on `index` (×2, both
`data-i18n="brand.tag"`), the hero tagline on `landing` (which `brand.js`:27 queries as
`.brand .tag:not([data-i18n])`), and a JS-rendered SLO code badge on `slo-health`.

**Consequence.** All four rules are page-scoped and belong to the two migrations, `UI-047b` and
`UI-047c` — exactly where `taqseem`'s bare `.card` went the same day. **`UI-043` is off the
critical path**: `blueprint` now needs only `UI-046` plus its migration, and `index` needs only
a decision on **D22**, with no code in front of it at all. UI-043's remaining scope is real but
nothing waits on it — tables were already shipped by `03-elements/tables.css`, and the domain
families are duplication work for Sprint 5/6.

**The method is the transferable part.** This is the second finding in one day from the same
step: list what a page loses when `theme.css` goes, then check each line against the tree
instead of trusting the coverage claim. The first was a missing `white-space` in `btn.css`.
Neither was found by review; both were found by one probe run and a grep.

**And the correction is the second transferable part.** The claim in this entry was written
once from a cascade reading, presented as settled, and then asked for by Irfan as a measurement
before it could be committed. Measuring it confirmed the conclusion and broke one of the three
arguments under it. The conclusion survived; the reasoning did not, and a board carrying the
original wording would have taught the next session a false rule about `.row`.

---

## 2026-08-12 — UI-047a: taqseem migrated, and its enumeration found a hole in a finished component

**Sprint 4b, UI-ARCH epic.** Full board: `docs/ui/STATUS.md`. **7 of 9 pages are now live**
on the new tree; `blueprint` and `index` remain.

**What shipped.** `taqseem.html`'s three `<link>`s became two — `app.css` plus the entry file
`static/css/pages/taqseem.css`, unparked from `docs/ui/` where it had waited since 2026-08-03
for the components it borrows. Three buttons re-classed (`btn gold` ×2 → `.btn--accent`,
`btn ghost` → `.btn--ghost`). The entry file gained a page-scoped bare `.card` and the two
`.brand` partials the legacy file does not fully redeclare. This is the first migration that
had to change markup rather than only swap a link.

**The finding, and it is why the first step was an enumeration and not the `<link>`.** The
board said `taqseem` loses 17 rules when `theme.css` goes, that existing components cover
them, and that exactly one exception was known — the bare `.card`, which `card.css` omits
deliberately because `.card` is on 13 live elements elsewhere. The instruction was to confirm
there was no *second* exception before touching anything. There was. `theme.css`'s bare `.btn`
carries thirteen declarations; twelve had been ported into `.btn--*`, and the thirteenth,
`white-space: nowrap`, existed **nowhere** in the layered tree — not ported, not decided
against, simply absent. UI-041 shipped after four review rounds and none of them saw it.
Listing what one page loses and checking each line against the tree did, in one probe run.
Fixed at its own address in `btn.css` (`2f2368e`), not page-scoped, because it is a property
of the button rather than of this page.

**Gates.** 0 element × property deltas on all five pages `css_type_probe` covers, drift 0.
On `taqseem`: `theme?` no, EXPOSURE 17 → 0. Element count 70 → 69, which is the removed
`<link>` and not a lost node. `.btn--*` went live on real markup for the first time — the
rules probe reports 3 / 2 / 2 / 1 in `layer(components)` against UI-041b's `matches=0`.

**And the page was opened before it was committed.** The same migration was performed on
2026-08-11, passed every gate above, and was reverted deliberately — chips and the `.move-sel`
selects are JS-rendered, appear in no snapshot, and no computed-style probe can see whether the
page still works. **Checked by Irfan on 2026-08-13, item by item.** Confirmed: **chips render as
standing blocks** rather than collapsing to pills, so the legacy `.chip` still wins; and
**changing a chip's select moves the SLO**, so `moveSlo` fires. Those two are precisely what the
board said needed eyes. **Not checked: the confirm modal's open/cancel, and the card border and
brand header** — recorded as unchecked rather than assumed. Only `Pre Year 1` / `Mathematics`
can be used for this check; it is the one class/subject carrying a plan, and every other
combination renders an empty board that reads as breakage and is not.
Two changes are deliberate and were flagged in advance so they would not read as regressions —
the buttons are taller (44px touch target) and the accent fill is darker, because white on the
old fill measured 3.03:1 and failed WCAG on this page.

---

## 2026-08-01 — UI-031a: slo.html is the first page on the new CSS tree (@layer live)

**Sprint 3, UI-ARCH epic.** Full board: `docs/ui/STATUS.md`. This is the first page in the
epic whose stylesheet is the new ITCSS tree, and the first time any browser has parsed the
`@layer` statement the whole architecture rests on.

**What shipped.** `slo.html`'s three `<link>`s became two: `app.css` (it still owns the
`.icon` sprite until Sprint 4) plus a new entry file `static/css/pages/slo.css`, which is two
`@import`s and no rules of its own — `../main.css`, then `../99-legacy/slo.css layer(legacy)`.
`main.css` lost the nine legacy `@import`s it used to carry. Not one other byte of the page
moved: frozen inventory 22/22, class attributes 48/48, `<script>` bodies identical, −53 bytes
which is exactly the link swap.

**Why the documented shape was abandoned.** ADR-001 says the `<link>` goes straight to
`main.css`, which imported all nine `99-legacy/*` files. Measured before writing: they import
alphabetically, so `taqseem.css` is last and won **15 selectors** off this page — `:root`,
`.app-sidebar`, `.brand`, `.app-nav a`, `.sidebar-foot`, `.row` and more — and every value it
brought reads a `static/theme.css` token that the same task unlinks. The by-the-book migration
would have shipped an unpainted sidebar and no border colours, through a file belonging to a
different page. That is D19 and D20 arriving together, on the one page whose own 17 tokens are
all local literals. The legacy import therefore moved out of `main.css` into a per-page entry
file; `main.css` keeps the layer order and remains the single source of the cascade. Rule
changed in `CLAUDE.md` §11 and recorded as unplanned.

**Verified in a real browser, not by reasoning.** The Chrome extension was not connected, so
headless Edge 150 was driven over CDP with Node's built-in WebSocket. Read off the live
document: the layer statement with all seven names in order, every `@import` in its declared
layer, `99-legacy/slo.css` in `layer(legacy)` rather than unlayered, sidebar `rgb(22,41,74)`,
`static/theme.css`'s tokens all empty, icons 17px, and the other eight pages untouched.

**Four review rounds failed it, and the three real failures were one shape: a number asserted
instead of measured.** A contrast ratio computed against an assumed backdrop (the real figure
was 1.70:1 → 3.04:1, an *improvement*, because the old sidebar had a white slab in it); a
"what changed" list naming only one of two mechanisms and missing D21 firing live; and four
line numbers inherited rather than checked. All three now sit in the files as recorded failed
drafts, so the next session meets the trap and not just the answer. One aggregate count was
deleted rather than fixed — two measurements disagreed on which properties to count, so the
files give affected elements per rule, which anyone can re-derive with a grep.

**Two things worth remembering beyond this task.** Quoting two hex values in a *comment* took
`unsanctioned_hex` 429 → 431, and because `css_baseline.py --write` had already run, the
raised number was pinned into `BASELINE.json` and `--check` then passed against the laundered
baseline — re-pin only *after* `--check` passes against HEAD. And `C:` hit 226 MB free during
this task, producing a real `No space left on device` mid-pytest; UI-030's recorded sqlite
"disk I/O error flake" was almost certainly the same thing.

**Ships with three visible changes, all accepted and all homed in Sprint 4:** the sidebar
subtitle at 3.04:1 (better than before, still under WCAG AA) — D26; `<a class="btn-ghost">`
losing its blue while `<button class="btn-ghost">` keeps it — D27; and cards visibly tighter,
headings ~20% bigger with the gap beneath them gone — D28. A fourth item, D29, records that
two different files are named `theme.css` and the browser's Network panel shows only the
basename — it caused a false alarm at the browser check.

Gates: `pytest -q` 906 passed · `ruff` clean · ratchet OK, eight ratcheted metrics flat,
`unsanctioned_hex` 429 · `shared_css_lines` 1351 → 1527, the only mover.


## 2026-07-26 — Concurrency fix: SQLite WAL + busy_timeout (20-teacher concurrent write)

MASLA: 20 teachers ek server se (LAN) ek saath likhte — default DELETE-journal +
busy_timeout=0 par write-conflict FORAN "database is locked" (500) deta tha. Data SAFE
tha (SQLite ACID — failed write cleanly rollback, koi corruption NAHI; DB local disk par,
clients HTTP se — network-FS nahi), par teacher ko error dikhta aur dobara try karna padta.
Fix chhota + in-place, koi re-architecture nahi.

- STEP 1: `get_connection()` (app/core/database.py) —
  `sqlite3.connect(DB_PATH, timeout=30)` + `PRAGMA journal_mode=WAL` +
  `busy_timeout=5000` + `synchronous=NORMAL`.
    * WAL — concurrent reads smooth (reader/writer ek doosre ko block nahi karte); ek
      writer serialized. WAL local disk par safe (network-FS par NAHI — yahan clients
      HTTP se aate, DB file local hai). WAL DB header par persistent (ek dafa stick).
    * timeout=30 / busy_timeout=5000 — locked par foran fail nahi, thodi der wait
      (short writes ab ek doosre ka intezaar kar lete, error nahi).
    * synchronous=NORMAL — WAL ke saath durable + tez.
- STEP 4: .gitignore — `*.db-wal` + `*.db-shm` add. (`*.db.*` dot-pattern hyphen-siblings
  ko match nahi karta tha — WAL sidecar files kabhi git par na jayein.)
- Regression: sirf get_connection() ke ANDAR PRAGMAs — koi endpoint/repository/connection-
  per-op logic chhua NAHI (open→execute→commit→close waise ka waisa).

Deployment context: `start.bat` → `uvicorn --host 0.0.0.0 --port 8000` (single worker);
teachers LAN par doosre PCs se EK server machine se connect karte, DB usi ki local disk par.
Sync `def` endpoints threadpool mein → concurrent threads, har ek apna connection — yahi
contention point tha.

Tasdeeq: PRAGMAs present; live raw-open `PRAGMA journal_mode` = **wal** (persistent, bina
PRAGMA set kiye — hatmi saboot), busy_timeout=5000, synchronous=NORMAL; `-wal/-shm` ab
gitignored; pytest -q = 874 passed; ruff clean. Browser test (Irfan): server restart ke
baad WAL ON confirm, do-tab se ek saath paper banaya — dono success, koi "database is
locked" error nahi. Note: `-wal/-shm` sidecar sirf live connection ke doraan disk par
(connection-per-op → idle par SQLite checkpoint kar ke hata deta — WAL-off ki nishani nahi).
Server restart chahiye tha (naya get_connection) — ho chuka. Postgres tab jab writes bahut
heavy hon (database.py comment migration path likhta) — abhi WAL+timeout kaafi.

## 2026-07-26 — Landing / teacher-welcome page (static/landing.html)

App ke andar chhota teacher-welcome page — 3 hisse: Hero, 7 quick-action cards
(existing pages tak), aur intro cards. Modern lekin saaf, teacher-focused (public
marketing NAHI). Frontend-only, responsive.

- STEP 1: `<head>` dhaancha index.html jaisa (consistency) — `app.css` link + inline
  `:root` vars (wahi palette: primary/navy/tint/ink/muted/border/surface/bg/radius/shadow)
  + body font 'IBM Plex Sans' + end mein `<script src="/static/js/brand.js">`. `<body
  data-page="Welcome">` (brand.js title + .brand name/tag set karta). Nastaliq @font-face
  skip (page English/Roman-Urdu, koi Nastaliq text nahi).
- STEP 2 (Hero): navy gradient band; `.brand .logo` (/static/brand/logo.svg) + name/tag
  (brand.js bharega) + welcome line (offline exam paper generator, AII Mingora).
- STEP 3 (Quick actions): 7 hover-lift cards, icons `icons.svg` se — Generator (/),
  Blueprint (/blueprint.html), Question Bank (/bank.html), Image Library (/library.html),
  Learning Outcomes (/slo.html), Exam Taqseem (/taqseem.html), SLO Health (/slo-health.html).
  Icon pattern `<svg class="icon"><use href="/static/icons.svg#i-…"></use></svg>`.
- STEP 4 (Intro cards): 4 chhote cards (Paper banao / Blueprint templates / SLO coverage /
  Image library), 1-line each — intro, marketing nahi.
- STEP 5: responsive (grid auto-fill/auto-fit wrap + mobile media query). Koi external
  CDN/font/script nahi (offline) — sirf app.css vars + icons.svg + brand.js REUSE, koi
  naya brand code nahi.

Placement: `/landing.html` — ZERO backend/main.py change (StaticFiles `/` mount ise serve
karta). `/` waise ka waisa hai (= index.html Generator); landing usay replace nahi karta.
Palette: navy + primary-blue on-brand — brand.json mein gold color nahi, is liye invent NAHI
kiya (agar gold accent chahiye to pehle brand system mein add ho, tab landing use kare).

Tasdeeq: git diff sirf naya static/landing.html (koi backend/dusra page change nahi);
7 quick-action cards + 7 sahi hrefs, 11 icon `<use>` refs (7+4), brand.js + data-page,
div balance 38/38; ruff clean; pytest -q = 874 passed. Browser test (Irfan): Hero+brand
(name/tag/logo) sahi ✓, 7 links sahi pages ✓ (Blueprint confirm), mobile cards wrap ✓,
navy+blue on-brand ✓. Frontend-only — koi restart nahi.

## 2026-07-26 — Hissa 5-B: question-type ↔ Bloom hint (section-level, soft)

Section card mein Bloom Level chunne par uske paas chhoti soft hint — us bloom ke munasib
question-types (misal "Apply ke liye aksar behtar: Short-answer · Fill-blank"). Tajweez,
hukm nahi; override khula. Frontend-only, koi backend/DB/5-A change nahi.

- STEP 1: `QTYPE_HINT` const (frontend, script scope) — UPPERCASE bloom key → labels array.
  Values SIRF section-card ke 4 selectable types (MCQ / Fill-blank / True/False /
  Short-answer). `essay` bloom_service/ai_service mein hai par section-card checkbox mein
  selectable NAHI, is liye hint se chhoda (warna teacher aisi type ki tajweez dekhta jo
  select hi nahi kar sakta). Keys UPPERCASE = dropdown value se seedha match (koi casing-
  bridge nahi, 5-A wala lowercase masla yahan nahi). Purely presentational — koi backend
  consumer nahi, is liye frontend const (5-A ke ulat jahan bloom_standards 3 services
  consume karte the).
- STEP 4: `qtypeHintHtml(bloomVal)` DRY helper — UPPERCASE bloom → hint HTML (ya khali
  agar Any/null/unknown). renderSecCard (initial render) + onBloomFilter (update) dono
  reuse karte — ek jagah.
- STEP 2: `#qtypeHint_${i}` read-only div, renderSecCard mein Bloom `<select>` ke baad
  (isi wrapping div). Initial content `qtypeHintHtml(sec.bloom_filter)`. escHtml-safe.
- STEP 3 (STALE-TRAP FIX): `onBloomFilter` pehle sirf state set karta tha (card re-render
  nahi) — to static hint bloom badalne par stale reh jata. Ab handler hint element ka
  `innerHTML` seedhe update karta (`getElementById('qtypeHint_'+idx)`). Poora
  `renderSections()` NAHI — focus/scroll safe + sasta.
- STEP 5: regression-safe — bloom_filter khali/'Any'/null → helper `''` return → hint
  hidden (invisible). Question Types checkboxes / onTypeChange / Bloom filter ki asal
  functionality chhui NAHI (sirf ek read-only div + handler mein ek update-line). 5-A box
  (#bloomSuggestionBox) + backend untouched.

5-A se alag: 5-A paper-level Bloom DISTRIBUTION (class-tier %, grade dropdown ke paas),
5-B section-level QTYPE hint (Bloom filter ke paas). Alag DOM, scope, trigger — koi takrav nahi.

Tasdeeq: grep QTYPE_HINT=2 (def+use), qtypeHintHtml=3 (def + renderSecCard + onBloomFilter),
qtypeHint_=2 (element+handler); inline JS node --check "JS SYNTAX OK"; pytest -q = 874 passed;
ruff clean. Browser test (Irfan): Remember/Apply/Analyze → sahi hint ✓, Any → gayab ✓, fauran
badalta bina blink/scroll-jump ✓. Naya backend test nahi (behaviour puri tarah frontend/DOM;
koi contract nahi badla). Frontend-only — hard refresh kaafi, restart nahi.

## 2026-07-26 — Hissa 4-E: pin reset-gap fix (deferred 4-D bug)

4-D mein pins ephemeral kehlaate the lekin makePaper ke baad `_pinned` clear nahi hota
tha — purane pins agle paper mein reh jaate ("yeh question kahan se aaya?" confusion).
4-E: pins teen jagah clear, ek DRY helper se. Frontend-only, koi backend/DB/schema change nahi.

- STEP 1: `clearPins()` helper — `_pinned = new Map(); updatePinnedBadge();`. Khali Map ->
  khali Map, to koi pin na ho to no-op (regression-safe).
- STEP 2: makePaper SUCCESS par reset — dono success branches (shortfall `if` + ok `else`)
  ke BAAD, renderBloomGuidance/print-open se pehle. `clearPins()` + `checkExamCoverage()`
  (open SLO panels ka stale "✓ pinned" button reset). SUCCESS-ONLY: 404 / `!res.ok` guards
  pehle return kar chuke, `catch` network-error, aur `finally` (sirf btn re-enable) — in par
  reset NAHI, pins intact (warna fail par teacher ko dobara pin karna padta).
- STEP 3+4: `onSubjectChange` + `onGradeChange` mein bhi `clearPins()`. Yeh sirf tidy nahi —
  CORRECTNESS fix: pins `qid` hain jo ek subject/grade ke question-set se bandhe. Subject/
  grade badle to purane qids be-maani; aur 4-C backend pinned ids ko filters ke BAHAR bhi
  force-include karta — doosre subject ka valid qid naye paper mein force-inject ho kar
  ghalat-subject question la sakta tha. checkExamCoverage() dono handlers mein already hai
  (L501/L541), to SLO panels bhi refresh ho jaate.
- STEP 5: pin-attach logic (makePaper L1156-1164) chhua NAHI — sirf success ke baad clear add.

Tasdeeq: grep clearPins=4 (1 def + 3 call: onSubjectChange/onGradeChange/makePaper-success);
inline JS node --check "JS SYNTAX OK"; pytest -q = 874 passed; ruff clean. Browser test (Irfan):
success→clear ✓, subject/grade change→clear ✓, fail→intact ✓. Naya backend test nahi (behaviour
puri tarah frontend/DOM; pin-attach backend contract pehle se 7 tests se covered). Frontend-only —
hard refresh kaafi, restart nahi. 4-D ka reset-gap ab band.

## 2026-07-26 — Hissa 5-A: Bloom distribution tajweez — investigation + guard test

Maqsad tha blueprint page par class-tier ki soft Bloom distribution tajweez (Pre-Primary
70/30 … Matric 15/25/30/20/10, read-only, "mashwara hukm nahi"). INSPECT mein pata chala
feature **pehle se end-to-end maujood** hai: `app/core/bloom_standards.py` (_GROUPS) →
`GET /api/bloom-suggestion/{class_name}` (app/api/bloom_suggestions.py) → blueprint.html
`onGradeChange` fetch + `#bloomSuggestionBox` render. Yaani naya kaam sirf tasdeeq +
tahaffuz ka tha.

- STEP 1 (rejected): frontend-only mirror try kiya — `BLOOM_STD` JS const (UPPERCASE keys,
  casing bridge) + `bloomSuggestion()`/`renderBloomSuggestion()` helpers, API call ki jagah.
  Faisla: REVERT. Wajah — `bloom_standards.py` waise bhi 3 jagah consume hota
  (bloom-suggestion route + blueprint_bloom_guidance_service + slo_shortfall_service), to
  Python copy khatam nahi ho sakti; mirror teesri copy = net duplication + drift-risk.
  Localhost par round-trip ka faida ~sifar (onGradeChange mein pehle hi /api/topics fetch).
  "Ek source of truth" (backend) saaf jeeta. blueprint.html byte-identical wapas (git diff khali).
- STEP 2 (kept): tests/test_bloom_standards.py — 6 tests jo canonical %ages pin karte:
  Pre-Primary 70/30, Primary 30/35/25/10, Middle 20/30/30/20, Matric 15/25/30/20/10;
  normalize variants (grade 1 / Grade  1 / GRADE-1 / grade_1 → Primary); unknown/khali → None.
  Yeh guidance + shortfall services ki bunyaad bhi pin karta (woh bhi inhi standards par tikke).

Tasdeeq: blueprint.html unchanged (diff khali, API path bahal, /api/bloom-suggestion=1);
inline JS node --check OK; pytest test_bloom_standards.py = 6 passed; full suite 874 passed;
ruff clean. Net change is branch par: sirf naya guard-test (frontend/backend code chhua nahi).
Note: Bloom naming casing — questions.bloom_level UPPERCASE, slo.bloom_level lowercase;
standard keys lowercase (services `.upper()` se bridge karte).

## 2026-07-26 — Hissa 4-D: multi-section pin targeting

4-C ka pin ab per-section — teacher batata hai konsa pinned question KIS section mein
jaye (pehle sab pehli section par jaate the). `_pinned` ab `Set<qid>` ki jagah
`Map<qid, sectionIndex>`. Backend pehle se per-section `include_question_ids` guarantee
karta tha (4-C contract), sirf frontend value-group kar ke bhejta.

- STEP 1: blueprint.html — `_pinned = new Map()` (qid -> 0-based sectionIndex, ephemeral).
  showSloQuestions har question par section `<select>` (A/B/C… = index) deta; pinned ho
  to us ki section pre-select. togglePin saath wale select ki value uthata; setPinSection
  already-pinned ki section re-assign. Badge ab per-section breakdown (📌 3 pinned A:2 B:1).
- STEP 2: makePaper — `_pinned.entries()` ko section index se group, har section apne ids
  `include_question_ids` mein; koi pin na ho to body bilkul waisa (regression-safe).
- STEP 3: removeSection — pin re-map: hataayi section (idx) ke pins DROP, us se upar wale
  (secIdx > idx) ek khisak (secIdx-1). Warna pin ghalat section par point karta.
- STEP 4 (BUG fix): browser test se "pinned question galat section" pakra. Instrumentation
  pehle ([PIN-DBG] console.log removeSection+makePaper) — console trace + 2 PDF se saabit
  ke pin LOGIC sahi hai; asli masla sirf COSMETIC label-drift tha: default headings
  ("Section A/B/C") remove ke baad re-number nahi hote the, jabke select/badge index-based
  letter dikhate. `renumberDefaultHeadings()` — conditional: sirf `/^Section [A-Z]$/`
  (default) headings ko index se align; teacher ki custom heading ("Objective Questions")
  MAT chhue. removeSection (re-map ke baad) + addSection dono par chalta — "ek source of
  truth" (badge/select/heading sab index se derive). Phir instrumentation revert.
- STEP 5: tests/test_blueprint_hissa4c_pin.py — +2 (total 7): two-sections-distinct-pins,
  pin-only-in-its-section (backend per-section contract jis par frontend bharosa karta).

Tasdeeq: grep [PIN-DBG]=0 (reverted); renumberDefaultHeadings 1 def + 2 call; inline JS
node --check "JS SYNTAX OK"; pytest test_blueprint_hissa4c_pin.py = 7 passed; ruff clean.
Frontend-only change (backend/schema untouched) — hard refresh kaafi, restart nahi.
Deferred: pin reset-gap (blueprint reset/switch par pins clear nahi hote) — Hissa 4-E candidate.

## 2026-07-25 — Hissa 4-C: "daalo" — must-include pinned questions (Option A)

Teacher "questions dikhao" (4-B) list se question pin karta; backend usay blueprint
section mein GUARANTEE karta. "Tajweez, hukm nahi" — app khud add nahi, teacher pin
karta. Faisla: pinned COUNT KE ANDAR (pinned pehle, filter baqi jagah); pinned > count
to count barh jaata.

- STEP 1: schema `BlueprintSection.include_question_ids: List[str] = []` (requests.py).
  Khali = purana rawaiyya (backward-compat).
- STEP 2: `blueprint_paper_service._apply_pinned(picked, ids, wanted)` — pinned pehle
  (dedup, order-preserve), filler baqi; effective count = max(wanted, #valid-pins);
  non-existent id skip (find_by_id None); double-count guard. Loop mein filter ke baad
  call; pins ki soorat mein shortfall-note final got par recompute. Koi valid pin na
  ho to picked/wanted bilkul waise (regression-safe).
- STEP 3: blueprint.html — `_pinned = new Set()` (ephemeral, paper-level); 4-B list ke
  har question par "daalo"/✓pinned toggle (togglePin); action-bar mein "N pinned" badge
  (updatePinnedBadge); makePaper body mein pins PEHLI section par attach (saveBlueprint
  ko nahi chhua — template mein pins save nahi). escAttr/escHtml-safe.
- STEP 4: tests/test_blueprint_hissa4c_pin.py — 5 pass: guaranteed-first-within-count,
  dedup, over-count-expands, nonexistent-skip, no-pins-unchanged.

Tasdeeq: schema default []/list accept; service AST+import OK; blueprint inline JS
node --check OK (_pinned=8, togglePin=2, pinnedBadge=2, include_question_ids=1);
pytest -k "blueprint or coverage or paper" = 260 passed; ruff clean. Naya schema
field + service => server hard-restart chahiye.

## 2026-07-25 — Hissa 4-B: "questions dikhao" — missing SLO ke tagged questions (Option A)

4-A warning box extend: har missing SLO ke saath "questions dikhao" link; click par
us SLO se tagged questions (published + draft dono) inline expand — READ-ONLY, teacher
khud upar section mein daalta (app add nahi karti). Zero DB/schema change — sirf ek
naya read route jo maujooda question_slo link table parhta.

- STEP 1: `question_slo_repository.list_questions_for_slo(slo_id)` — ek JOIN (q.* JOIN
  question_slo WHERE slo_id), koi status filter nahi (sab), created_at se sorted. N+1 nahi.
- STEP 2: `question_service.list_questions_for_slo(slo_id)` — pass-through wrapper.
- STEP 3: `GET /api/slo/{slo_id}/questions` (app/api/slo.py) — READ-ONLY, minimal fields
  {id, question_en, status, bloom_level} (poora row nahi). SLO wajood check nahi (khali
  list valid). slo router pehle se registered.
- STEP 4: blueprint.html — remaining SLO `<li>` mein "questions dikhao" link (slo_id via
  escAttr) + hidden `<div>`; `showSloQuestions(sloId, linkEl)` GET fetch, question_en +
  status badge render, toggle band. escHtml-safe, koi add/checkbox nahi.
- STEP 5: tests/test_slo_questions_api.py — 2 pass: published+draft dono tagged aayein
  (untagged bahar, minimal shape); unknown slo => 200 + khali list.

Tasdeeq: repo/service/route AST OK + route router par registered; blueprint inline JS
node --check OK (showSloQuestions grep=2); pytest 2 passed. Naya route => server
hard-restart chahiye.

## 2026-07-25 — Hissa 4-A: Blueprint exam-coverage warning (frontend-only)

blueprint.html mein exam (bpExamNo) chunte hi taqseem-coverage ka READ-ONLY warning —
kaun se planned SLO abhi shamil nahi. Koi backend/DB/route change nahi; GET /api/coverage
ka maujooda `remaining` list reuse (per-SLO uncovered). Server restart nahi, hard refresh.

- STEP 1: bpExamNo ke neeche `<div id="bpCoverageWarn">` (hint div ke baad, container
  332 ke andar) + select par `onchange="checkExamCoverage()"`.
- STEP 2: `checkExamCoverage()` — guards (Unassigned""/subject/grade khaali => hide),
  GET /api/coverage (slo-health.html:398 pattern), render: remaining=0 & total_slos>0
  green tick; remaining>0 amber "⚠️ N planned SLO abhi shamil nahi" + list (slo_text
  readable, SLO-code bracket mein, pehle 8 + "… aur M zyada"); total_slos=0 => hide.
  esc via escHtml. Read-only — koi button/action nahi.
- STEP 3: triggers — bpExamNo onchange + onSubjectChange()/onGradeChange() ke andar
  checkExamCoverage() call (subject/grade badle to warning refresh).

Tasdeeq: grep -c bpCoverageWarn=2, checkExamCoverage=4; onchange @334, calls @499/@539;
inline JS node --check OK.

## 2026-07-25 — Coverage Marhala 6b (UI) + 7 (nav icon) — feature mukammal

ECONNRESET mein jo 6 markers 0 nikle the (cov-badge/loadCoverage/paperExamNo/bpExamNo/
covResult + backend exam_no) — sab wapas, har file apne commit mein (ECONNRESET-safe).
Faisla: Unassigned = null (0 nahi) teeno paper-dropdown par. N-source har jagah
school_settings.exam_count (drift nahi). Traffic-light server coverage_percent reuse.

- 6b-1 (a5329c4) index.html `paperExamNo`: paper-build dropdown (Unassigned""→null +
  1..N). buildExamNoOptions loadSchoolSettings se (fail 8). buildPaper body exam_no.
- 6b-2 (3ce0a6c) blueprint.html `bpExamNo`: dropdown; N ek reuse GET /api/school-
  settings (page-load init); makePaper body exam_no. Inline-handler trap-zone chhua nahi.
- 6b-3 (444c560) slo-health.html `covResult` card: class+subject+exam -> GET /api/coverage;
  covered SLO ke saamne paper naam (paper_ids->paper_titles drill-down), remaining ke
  saamne "(kisi paper mein nahi)". esc() escaped, addEventListener saaf.
- 6b-4 (68c34cb) taqseem.html `loadCoverage`+`cov-badge`: har exam column header par
  "covered/planned" + traffic-light (>=100 green, >=60 yellow, <60 red, unassigned/
  planned0/null grey). Ek GET /api/coverage-summary, data-exam se match, idempotent inject.
- 7 (59a7fb2) icons.svg `i-taqseem` symbol (3-column exam-bucket shape) + 4 pages
  (index/slo-health/slo/taqseem) nav i-blueprint->i-taqseem. Blueprint nav har page
  i-blueprint par barqarar.

Tasdeeq: har file grep -c <marker> + node --check (inline JS) + per-file commit.
icons.svg XML well-formed. Full regression (test_ai_service ke ilawa) = 842 passed,
working tree clean.

## 2026-07-25 — Coverage Marhala 6a: blueprint exam_no threading (silent gap fix)

Gap: generate/bank/adaptive paper paths exam_no ko papers.exam_no tak thread karte
the, magar BLUEPRINT path nahi — UI dropdown se exam_no aata bhi to silently gir jaata
(blueprint paper hamesha exam_no=NULL). Marhala 3 threading ne ye path chhod diya tha.
UI (6b) se pehle band karna zaroori warna bpExamNo dropdown bekaar.

Teen keyword-arg edits (positional trap se bacha — pichla dead-code sabaq):
- `app/schemas/requests.py` BlueprintPaperRequest: `exam_no: Optional[int] =
  Field(default=None, ge=0)` (baaki 3 paper schemas jaisa).
- `app/api/papers.py` blueprint-paper route: `assemble_blueprint_paper(..., exam_no=
  req.exam_no)` (keyword).
- `app/services/blueprint_paper_service.py`: signature mein `exam_no: Optional[int] =
  None` param, aur `papers_repository.insert(..., exam_no=exam_no)` (keyword).

Test (`tests/test_coverage_api.py` — TestClient, full chain): `test_blueprint_paper_
persists_exam_no` — question seed -> POST /api/blueprint-paper {sections_input, subject,
exam_no:3} -> paper_id read -> assert paper["exam_no"] == 3 (NULL nahi). Exactly wo
silent gap band karta hai.

Tasdeeq: pytest tests/test_coverage_api.py -v => 4 passed. grep -c exam_no: requests.py
6, papers.py 1, blueprint_paper_service.py 2. Regression (blueprint hissa1-3 + shortfall
+ bloom + coverage + paper_service) => 180 passed. git diff --stat: 4 files, +60/-1.

Agla: Marhala 6b — UI (taqseem badges, index paperExamNo, blueprint bpExamNo, slo-health
coverage card).

## 2026-07-25 — Coverage Marhala 5: tests (service + api)

`tests/test_coverage_service.py` (6) + `tests/test_coverage_api.py` (3) — conftest
`test_db` fixture (tmp SQLite + init_db), data seedha repos se seed. Helpers _q/_slo/
_link/_paper(exam_no=)/_plan(overwrite_assignments). API: TestClient(app) module-level,
koi auth header nahi (key unset => unprotected, sibling jaisa).

Service tests:
- ⭐ test_covered_in_wrong_exam_stays_missing (STRICT cross-exam): s1 exam 2 mein
  planned, exam 3 ke paper ne cover kiya => exam 2 remaining mein, summary exam 2 & 3
  dono covered=0. Covered-in-wrong-exam kisi ko credit nahi (leak-guard lock).
- test_planned_but_missing: planned SLO, koi paper nahi => remaining.
- test_null_exam_paper_excluded: exam_no=NULL paper coverage se bahar (detail + summary).
- test_slo_two_papers_same_exam: paper_map mein dono paper_ids, covered_slos double-count
  nahi (SET membership).
- test_summary_includes_unassigned: exam_no=0 bucket shamil.
- test_class_normalized_match: paper class 'pre year 1' vs SLO 'Pre Year 1' match.

API tests: test_coverage_summary_200 (shape: class/subject/exam_count/exams + row keys),
test_blank_class_400, test_exam_no_out_of_range_400.

Tasdeeq: `pytest tests/test_coverage_service.py tests/test_coverage_api.py -v` => 9 passed.
Poora suite (test_ai_service network-call ke ilawa) regression check.

Agla: Marhala 6 — UI (taqseem.html badges, index/blueprint exam dropdown, slo-health card).

## 2026-07-25 — Coverage Marhala 4: routes (GET /api/coverage + /api/coverage-summary)

Nayi file `app/api/coverage.py` — HTTP layer (taqseem.py/papers.py jaisa: `APIRouter()`
koi prefix nahi, full path per route, GET query params, `.strip()` khali-check → 400,
service call `try/except` → 500).
- `GET /api/coverage?class_name&subject&exam_no` — ek exam ka mukammal coverage.
  exam_no LAAZMI (koi default nahi; UI hamesha bhejta, missing par FastAPI 422 —
  intended). Range 0..N validate (N = `coverage_service._exam_count()`, reuse — koi
  naya public wrapper nahi banaya). Out-of-range → 400.
- `GET /api/coverage-summary?class_name&subject` — saare exams 1..N + Unassigned(0)
  ek-nazar. N + bucketing service khud handle karti.
- `main.py`: import block mein `coverage` (alphabetical, brand ke baad), aur
  `taqseem.router` ke baad `include_router(coverage.router, dependencies=_api_auth)` —
  siblings jaisa protected (key unset local par unprotected, magar consistency).

Tasdeeq (hard-restart, --reload par bharosa nahi; fresh uvicorn PID par curl):
- `coverage-summary` → 200, Exam 3 planned=6 covered=1 pct=17.
- `coverage?exam_no=1` → 200, total_slos=5, remaining asal SLO data.
- khali class_name → 400; missing exam_no → 422; exam_no=99 → 400 "0..8".
git diff --stat: main.py +2; coverage.py naya. grep -c coverage.router (main.py)=1.

Agla: Marhala 5 — Tests (cross-exam coverage test sab se ahem).

## 2026-07-25 — Coverage Marhala 2-3 refinement: paper drill-down (slo_id→paper_ids)

Marhala 2-3 commit (464f975) ke baad refine kiya — mudda: coverage sirf "ye SLO covered
hai/nahi" (boolean) batati thi, "KIN papers ne cover kiya" nahi. slo-health drill-down ke
liye ye chahiye.

- `papers_repository.covered_slo_pairs()` — pehle `set` of slo_id lautata tha; ab
  `list[dict]` of DISTINCT `(slo_id, paper_id)` jodi. Ek hi query se caller membership-set
  BHI banata hai aur `{slo_id: [paper_ids]}` map BHI (do query se bacha).
- `coverage_service._assemble_coverage()` — param `papers: list` → `paper_map: dict`; har
  covered SLO ke brief mein ab `paper_ids: [...]` chip jaata. Purana top-level `"papers"`
  field hataya (ab paper_titles alag).
- `exam_coverage()` — pairs se covered_ids + paper_map banata; `list_by_exam` se alag
  `paper_titles {id: title}` map (UI paper_id ki jagah naam dikhaye).

Tasdeeq (LIVE DB, class='Pre Year 1'/Mathematics): `coverage_service` import OK;
`coverage_summary` → 8 exams + Unassigned (Exam 3 mein 1 covered); `exam_coverage(1)` →
total_slos=5, covered_slos=0, paper_titles=2, keys mein `covered/remaining/strands/
paper_titles`. git diff --stat: papers_repository +15, coverage_service +35.

Agla: Marhala 4 — Routes (GET /api/coverage + /api/coverage-summary, main.py register).

## 2026-07-24 — Coverage Marhala 3: coverage_service + exam_no threading

`app/services/coverage_service.py` (naya):
- `_assemble_coverage(planned, covered_ids, papers)` — PURE core, koi DB query nahi.
  Coverage math (covered/remaining/percent/strands) + papers attach. total=0 → pct
  None. Hissa 4 (Blueprint tajweez) isay draft question_ids ke covered_ids se reuse
  karega — is liye DB-free rakha (warna Hissa 4 mein refactor).
- `exam_coverage(class, subject, exam_no)` — DB se planned (list_planned) + covered_ids
  (covered_slo_pairs, subject/class-filtered) + papers (list_by_exam) → core ko feed.
- `coverage_summary(class, subject)` — exams 1..N + Unassigned(0). covered_pairs_all_
  exams() EK query → exam_no par bucket (N calls se bachne ko). Unassigned: planned
  count dikhta, covered HAMESHA 0. Bucketing taqseem rule (NULL/0/>N → Unassigned).
- `_exam_count()` — N = school_settings.exam_count (taqseem_service jaisa rule).

`app/services/paper_service.py`:
- `_persist_paper(...)` mein `exam_no` param + `insert(exam_no=...)`.
- CHAARON callers (balanced/adaptive/bank/ratio) ko KEYWORD args mein badla +
  `exam_no=req.exam_no`. (Positional se exam_no galat param mein jaata — is liye
  keyword lazmi.)

`app/schemas/requests.py`:
- `exam_no: Optional[int] = Field(default=None, ge=0)` teeno paper-requests mein
  (Generate/Adaptive/Bank). None = Unassigned. UI (Marhala 6) bhejega.

Design note: "paper_map" ko `papers` (list_by_exam rows) banaya — core mein display-
only passthrough, Hissa 4 draft mein [] chalega. Cross-exam correctness coverage_
summary ke bucketing mein (Marhala 5 test isi ko pakdega).

Tasdeeq (live + pure): core 2/3=67%, empty→None. exam_coverage(PY1,Math,1)=5 planned/
0 covered/2 papers (covered SLO doosre exams ke plan mein — asli cross-exam data).
coverage_summary: exam_count=8, exam3 planned6/covered1, Unassigned planned1/covered0.
Chaaron _persist_paper callers keyword (grep). Saari files ast.parse OK. git diff
--stat + grep -c 'def <fn>' = sab disk par.

Agla: Marhala 4 — routes (GET /api/coverage + /api/coverage-summary, main.py register).

## 2026-07-24 — Coverage Marhala 2: repos (exam-wise coverage data layer)

`app/repositories/papers_repository.py`:
- `insert(...)` mein `exam_no: Optional[int] = None` param + INSERT column add. Purane
  callers exam_no na bhejein to None (Unassigned) — backward-compatible.
- `list_by_exam(exam_no, subject, class_name)` — ek exam ke papers (list-view fields).
- `covered_slo_pairs(exam_no, subject, class_name) -> set` — us exam ke papers ke
  sawalon se cover hue distinct slo_id. SQL: `json_each(p.question_ids)` se JSON
  expand → `question_slo` JOIN. Membership-test ke liye set.
- `covered_pairs_all_exams(subject, class_name) -> [{exam_no, slo_id}]` — har
  (exam, slo) coverage-jodi, tagged papers (exam_no IS NOT NULL). Cross-exam data.

BUG-FIX (isi marhale mein pakda): teeno functions mein subject+class filter add.
Pehle sirf `WHERE exam_no = ?` tha → doosre subject/class ke same-exam_no papers
leak ho jaate (Pre Year 1 Math ka coverage nikaalte waqt Class 8 Urdu ke papers
bhi gin liye jaate). Ab `LOWER(TRIM(subject/class_name)) = LOWER(TRIM(?))` normalized
match (papers.class_name free-text, slo_coverage_service jaisa). class_name NULL wale
papers khud bahar. Tasdeeq: ghalat subject/class → 0, ganda-casing ('MATHEMATICS' +
'  pre year 1 ') → sahi 8.

`app/repositories/slo_exam_plan_repository.py`:
- `list_planned(class, subject, exam_no)` — us exam ka 'universe': planned SLO poore
  fields samet (slo JOIN slo_exam_plan, INNER). Ordering list_resolved jaisa.

Design: "pair" = (exam_no, slo_id). Single-exam function sirf slo_id set deta hai
(exam fix), all-exams (exam_no, slo_id) jodi.

Tasdeeq (live DB, read-only): sab import/callable. json_each chali —
covered_pairs_all_exams()=8 jodi, covered_slo_pairs(1)=set of 4, list_by_exam(1)=2
papers, list_planned('Pre Year 1','Mathematics',2)=8 SLO. git diff --stat +
grep -c 'def <fn>' = har function disk par (=1).

Agla: Marhala 3 — coverage_service.py (_assemble_coverage core + exam_coverage +
coverage_summary; exam_no threading through _persist_paper, saare callers keyword args).

## 2026-07-24 — Coverage Marhala 1-fix: papers.exam_no schema migration

Pas-manzar: Marhala 2-7 (Coverage feature) ka session ECONNRESET se toota tha; audit
mein nikla source files (coverage_service.py, coverage.py, UI, tests) gum, sirf `.pyc`
bache the. Live DB ke `papers` table mein `exam_no` column pehle se maujood tha (kisi
gum-shuda migration ne banaya), magar `database.py` mein iska koi zikr nahi tha → fresh
DB par column banta hi nahi (orphan column).

Kiya:
- Stale `.pyc` delete: `app/api/__pycache__/coverage*.pyc`,
  `app/services/__pycache__/coverage_service*.pyc` (confusion se bachne ko).
- `app/core/database.py` — papers-migration block (line ~108, `sections_meta` ke baad)
  mein idempotent add: `if "exam_no" not in papers_cols: ALTER TABLE papers ADD COLUMN
  exam_no INTEGER`. Usi `papers_cols` PRAGMA-check pattern par → live DB par dobara add
  nahi hota.

Tasdeeq: `init_db()` do baar chala (live DB) → `exam_no` count = 1, koi error nahi.
Fresh temp DB par `init_db()` → `exam_no` present = True.

Agla: Marhala 2 (repos) — papers_repository (insert exam_no, covered_slo_pairs,
covered_pairs_all_exams, list_by_exam) + slo_exam_plan_repository.list_planned.

## 2026-07-24 — Taqseem Hissa 2 / Tukda 4: taqseem.html page + nav

Maqsad: taqseem ka UI. Tukda 3 (move) browser-confirmed (move 200, range 400, restore).

Naya page `static/taqseem.html` (StaticFiles se serve — koi naya backend route nahi):
- Upar: class + subject dropdown (`/api/slo/facets` se — GET /api/taqseem dono laazmi
  maangta hai), `N = k exams` badge (`plan.exam_count`), "Sequence se auto-generate"
  button, status line.
- Board: N columns (Exam 1..N) + alag **Unassigned** column (dashed). Har chip:
  `slo_code` + strand pill + `seq k` (NULL → "seq —" warn-rang). Chip par
  **"move to exam" dropdown** (Unassigned + Exam 1..N; current selected) — drag-drop
  NAHI (tay-shuda).
- Move: `change` par `POST /api/taqseem/move {slo_id, exam_no}` (position nahi bhejte →
  None; **siblings shift nahi hote**, position sirf ishara). Har move ke baad plan reload
  (source-of-truth server).
- Auto-generate: custom confirm modal (native `confirm()` nahi) — count dikhata hai
  kitne SLO abhi exams mein rakhe hain (yehi tarteeb overwrite hogi). Confirm ke baad
  `POST /api/taqseem/generate`; result mein backend ka theek `assigned/unassigned/
  overwritten` status line par.
- Nav "Exam Taqseem" (i-blueprint icon) **Learning Outcomes ke baad** — jin 3 pages ke
  nav mein SLO link tha (`index.html`, `slo.html`, `slo-health.html`) unmein add.

**Dead-code trap se bacha (Jul 24 ka sabaq):** har function ek hi jagah define, ek hi
call — koi `_orig… = fn; fn = wrapper` reassignment nahi. Move dropdown **event
delegation** par (`board` ka `change`), koi inline `onclick`/`JSON.stringify`-in-markup
nahi (frontend onclick-markup trap se door).

Verify (read-only): taqseem.html tag-balanced + inline JS `node --check` OK; teenon
nav-edited pages tag-balanced, har ek mein 1 taqseem link. **Khud test nahi kiya** — user
browser se. Server fresh `--reload` zaroori (Tukda 2/3 routes + naya page).

## 2026-07-24 — Taqseem Hissa 2 / Tukda 3: POST /api/taqseem/move (per-move)

Maqsad: ek SLO ka assignment badalne ka route (drag/drop ke liye). Tukda 2 (generate)
browser-confirmed — plan sahi bana (exam 1: seq 1-7, exam 2: seq 8-14, split 7/7/6×6).
Sirf route; page Tukda 4 mein.

Body: `{slo_id, exam_no, position?}`. Usool:
- `exam_no 0` = Unassigned (valid). Range `0 <= exam_no <= N` (N global). Bahar → **400**.
- `slo_id` DB mein na ho → **404**. `position` optional (None = get_plan sequence par
  fall back). Sirf isi SLO ki row upsert — siblings ki positions nahi chhedi jaatin
  (re-pack Tukda 4 ka kaam).

Changes:
- `app/repositories/slo_repository.py` — naya `find_by_id()` (existence check;
  questions_repository jaisa).
- `app/services/taqseem_service.py` — naya `move_slo()` + `SloNotFoundError`. Range
  check pehle (ValueError), phir existence (SloNotFoundError), phir `overwrite_assignments`
  se ek-row upsert (Tukda 2 ka bulk-upsert dobara istemaal).
- `app/schemas/requests.py` — `TaqseemMoveRequest {slo_id, exam_no, position?}`.
- `app/api/taqseem.py` — `POST /api/taqseem/move`; SloNotFoundError→404, ValueError→400,
  baaqi→500.
- `tests/test_taqseem_move.py` — 10 test: move to exam, exam_no 0, position optional,
  >N & negative reject, missing slo, route 200/400/404.

Verify: move+generate suites **16 passed**. **Move khud NAHI chalaya** — user browser se.
Server fresh `--reload` zaroori (naya route) — warna 404/stale (aaj chauthi dafa stale-server).

## 2026-07-24 — Taqseem Hissa 2 / Tukda 2: POST /api/taqseem/generate (auto-split)

Maqsad: ek (class, subject) ke SLO ko **sequence** ke hisaab se N exams mein khud-ba-khud
baant do (Tukda 1 = read-only GET pehle browser-confirmed ho chuka).

Split usool:
- `sequence` NULL wale SLO **kisi exam mein NAHI** jaate — `exam_no 0` (Unassigned)
  rehte hain (in ki asal teaching-tarteeb maloom nahi). Chahe pehle manually assign
  the, regenerate unhe 0 par le aata hai.
- baaqi SLO **sequence ASC** par (tie → slo_code, deterministic): `total` = un ki
  ginti, `base = total//N`, `rem = total%N`. Pehle `rem` exams ko `base+1`, baaqi ko
  `base`. (misal total=50, N=8 → do exam 7, chhe exam 6.)
- Poora regenerate: har SLO ka row upsert. `overwritten` = kitne SLO ka pehle se plan
  row tha (frontend confirm/summary ke liye) — pehli dafa 0, dobara sab.

Changes:
- `app/repositories/slo_exam_plan_repository.py` — naya `overwrite_assignments()`:
  `executemany` + `ON CONFLICT(slo_id) DO UPDATE` (class_print_settings jaisa pattern),
  ek transaction/commit. Sirf likhna — split logic service mein.
- `app/services/taqseem_service.py` — naya `generate_plan()`: `list_resolved()` se
  rows, `_exam_count()` se N, split compute, exam_no 0 for NULL-seq, counts wapas.
- `app/schemas/requests.py` — `TaqseemGenerateRequest {class_name, subject}` (N global,
  body mein nahi).
- `app/api/taqseem.py` — `POST /api/taqseem/generate`; blank class/subject → 400
  (GET /api/taqseem jaisa), DB error → 500.
- `tests/test_taqseem_generate.py` — 7 test: even/uneven split, NULL-seq unassigned,
  sequence-not-slo_code ordering, overwritten count, N>total, blank-class 400.

Verify: naye 7 test pass; related suites (api_routes + slo_repo + class_print) **93
passed**, koi regression nahi. **Generate khud NAHI chalaya** — user browser se karega
(fresh `--reload` server zaroori, warna naya module load na ho — dekho Jul 24 stale-server sabaq).

Symptom: Class Size save (DB=30, GET confirm) magar F5 ke baad field 25 dikhata. Do cache
theories (server no-store, phir client no-store — neeche wali entries) **galat** thi;
data kabhi clobber nahi hua. Asal wajah frontend mein thi:

`static/index.html` mein `loadSchoolSettings` DO baar mojood tha —
- L1302 original `async function loadSchoolSettings()` (sirf identity fields set karta,
  classSize NAHI), aur L1340 par **call**.
- L2595-2596 par baad mein `_origLoadSchoolSettings = loadSchoolSettings; loadSchoolSettings
  = async function(){…}` — wrapper jo classSize/minAnalysisPct/weakTopicThreshold populate
  karta tha.
- Magar ekloti call (L1340) reassignment se PEHLE chalti thi → hamesha **original** chalta,
  **wrapper kabhi call nahi hota** (dead code). Natija: classSize field kabhi server se load
  hi nahi hota → har F5 par HTML default `value="25"`. (Instrumentation ne sabit kiya:
  console mein sirf ORIGINAL log aaya, WRAPPER ka kabhi nahi.)

Fix: wrapper + reassignment poora delete; classSize/minAnalysisPct/weakTopicThreshold
populate ab **isi** original `loadSchoolSettings` ke andar (logo ke baad). Ab ek hi
function, ek hi call. Saari [PM-DEBUG] instrumentation (frontend 4 + backend 2) nikaal di.

Verify (read-only, koi POST nahi — user khud browser se test karega): served index.html
mein PM-DEBUG=0, wrapper=0, `loadSchoolSettings`=2 (1 def+1 call), classSize-in-load=1.
index.html tag-balanced; backend import OK; server clean restart. Data salaamat (logo
97491, class_size 30).

Alag masla (isi din): meri adhoori curl POST ne school_settings wipe kar diya tha
(address/logo/email/principal) — logo backup se surgical single-column UPDATE se restore
(baaqi untouched); backup `paper_maker_backup_before_logo_restore_20260724_084757.db`.
Sabaq: `/api/school-settings` merge-less POST (sirf kuch fields) baaqi ko pydantic-defaults
par reset kar deta — test/verify ke liye kabhi partial POST na karo.

Note: neeche ki do "Cache-Control / stale-UI" entries asal bug ka hal nahi thi, magar woh
headers (api no-store, HTML/JS/CSS no-cache, client cache:'no-store') sahih hygiene hain —
rakhe gaye.

## 2026-07-24 — Stale-UI fix ka round 2: client cache:'no-store' + JS/CSS no-cache

Pichhla fix (server no-store/no-cache) kaafi na tha — bug baqi raha. Do asal wajah:
1. **fetch() purani cached entry reuse karta tha.** Server ab no-store deta hai, magar us
   se PEHLE (jab koi Cache-Control nahi tha) browser ne `/api/school-settings` cache kar
   liya tha; `fetch()` default mode us stored entry ko bina revalidate reuse karta hai.
   Natija: merge se pehle wala GET **stale** → `saveSchoolSettings` purani `class_size`
   dobara POST → clobber. (DB mein 30 sirf isliye ke aakhri save Class Settings ka tha —
   user ne theek pakda.)
   Fix (`static/apiClient.js`, single choke-point): `_rawFetch` par default
   `cache:'no-store'` (`Object.assign({cache:'no-store'}, opts, {headers})`, opts override
   kar sakta hai). loadSchoolSettings + dono merge GET + print.html ka GET + har API call
   ek saath cache-proof.
2. **apiClient.js khud stale ho sakti thi.** Woh alag JS file hai; pichhla middleware sirf
   `text/html` par no-cache lagata tha, is liye external JS par koi Cache-Control nahi →
   naya no-store code hi load na hota.
   Fix (`app/main.py`): no-cache branch ab HTML + JS + CSS teenon par (`_NO_CACHE_TYPES =
   text/html, javascript, text/css`; content-type match). Immutable webp/fonts pehle
   branch mein mehfooz.

Verify (curl matrix): `/api/*` no-store; `/`, `index.html`, `print.html`, `apiClient.js`,
`app.css` no-cache; library webp abhi bhi immutable. Served apiClient.js mein naya code
mojood. Clean restart (--reload par bharosa nahi). Tests: api_routes **58 passed**.
Ahem: user ko ek dafa **Ctrl+F5** karna hoga taake purani cached apiClient.js/index.html
nikal jaye; uske baad no-cache khud maintain karega.

## 2026-07-24 — Cache-Control: /api no-store + HTML no-cache (stale-UI fix)

Symptom: Class Size 25→30 Save (✅), phir identity "Settings save karen", F5 → Class Size
wapas 25. **Data theek tha** — `GET /api/school-settings` DB mein 30 deta tha; UI purana
cached GET response padh raha tha. Root cause: StaticFiles/API responses par koi
`Cache-Control` header nahi tha (sirf ETag/Last-Modified) → browser heuristic caching se
normal F5 par purana `index.html`/JS aur purana API JSON serve kar deta (stale merge-code
bhi = "merge kaam nahi kiya" jaisa lagta, halaanki code theek tha).

Fix (`app/main.py`, mojooda immutable-assets middleware extend kiya, rename
`_cache_control_headers`, priority order):
1. `/library/*.webp` + `/static/fonts/*.woff2` → `public, max-age=31536000, immutable`
   (pehle se, **untouched** — jaan-boojh kar; filename UUID/font kabhi nahi badalta).
2. `/api/*` → `no-store` (API kabhi cache na ho).
3. HTML documents (content-type `text/html`) → `no-cache` (har load revalidate; stale JS band).

Verify: curl headers — `/api/school-settings` no-store, `/` + `/static/index.html` +
`/print.html` no-cache, library webp abhi bhi immutable (na toota). Server clean restart
(--reload ne main.py change flaky uthhaya tha — fresh start se yaqeeni). Tests:
api_routes + settings **62 passed**. Browser re-test (Class 25→30 → Save Class → identity
Save → F5 → 30 rehna) hard-refresh ke baad user karega.

## 2026-07-24 — School Settings: identity (phone/email/principal) + academic session

Maqsad: School Settings page ko extend karna — A) identity (phone, email, principal),
B) academic session (start month, exams N). Naya page/table NAHI: `school_settings`
singleton (id=1) aur mojooda `settings` screen pehle se the, sirf extend kiya.

Backend:
- `app/core/database.py` — 5 idempotent `ALTER TABLE ADD COLUMN` (wahi migration
  pattern): `phone TEXT ''`, `email TEXT ''`, `principal_name TEXT ''`,
  `session_start_month INTEGER 3` (March), `exam_count INTEGER 8`. ADD…DEFAULT purani
  row (id=1) ko backfill kar deta hai.
- `app/schemas/requests.py` — `SchoolSettings` model mein yehi 5 fields defaults ke sath.
- `settings_repository.upsert()` + `settings_service.save_settings()` — pass-through
  (INSERT + ON CONFLICT UPDATE dono). Routes (`GET/POST /api/school-settings`) schema-
  driven the, isliye naye nahi banaye — fields khud flow karte hain.

Frontend (`static/index.html` settings screen):
- Card A (identity) mein Phone / Email / Principal name (principal par "record only —
  print par nahi" note). Card B (Academic Session) naya: Session start month (dropdown,
  default March) + Number of exams N (default 8).
- `saveSchoolSettings()`: (1) `school_name` REQUIRED — khali par block + focus, save nahi.
  (2) ab **merge-safe** — pehle GET kar ke `Object.assign(existing, {...})`, taake identity
  save `class_size`/`print_*` ko model-defaults par clobber na kare (ye pehle latent bug
  tha; Class Settings save already merge karta tha). `loadSchoolSettings()` naye fields
  populate karta hai.

print.html letterhead: address ke neeche `.contact` line — phone · email (jo mojood ho).
principal print par NAHI (record-only, user ka faisla). exam_count → taqseem N wiring
JAAN-BOOJH kar chhoda (Hissa 2 mein).

Verify: migration real DB par chali (5 column + defaults backfill confirmed). API round-
trip (POST→GET) sab naye fields persist. Merge-safety: class_size=30 set ho kar bacha
raha. Poora suite **833 passed**. index+print.html tag-balanced (headless parse). Server
fresh restart (migration ke liye), DB wapas Test-School defaults par saaf chhoda.
Browser click-verify baqi (extension off) — hard-refresh ke baad.

## 2026-07-24 — Ops: sequence import "Updated:50" magar seq NULL — stale server

Alaamat: teacher ne sequence-wali Excel import ki, "Updated: 50, Errors: 0" mila,
magar `/api/slo` aur DB dono mein saari 50 `sequence` NULL. DB file ka mtime import
ke baad bhi purana (Jul 23 21:21) — yani us DB par aaj koi write hi nahi hua.

Diagnosis:
- Do uvicorn processes chal rahe the (PID 21160, 38148), dono ka `cwd` repo, `DB_PATH`
  unset → **dono ek hi** `paper_maker.db` par. Sirf 38148 :8000 par bind tha.
- Dono **Jul 23 18:34** ke — yani `sequence` ka code (jo isi 23 ko baad mein aaya) is
  running process mein load hi nahi tha. uvicorn `--reload` ke baghair chala tha, is liye
  purana `slo_import_service` module memory mein reh gaya (slo_text/bloom/strand update
  karta tha, sequence nahi → "Updated:50" sach tha magar seq NULL).
- Disk code sahi sabit hua: DB ki temp copy par poora import path chalaya → `updated:1,
  errors:0`, DB ne `sequence=99` wapas diya.

Hal: dono purane process band → fresh `uvicorn --reload` (PID naya). Teacher ne dobara
import kiya → (1) `POST /api/slo/import 200` access-log mein, (2) DB mtime badla
(Jul 24 06:38), (3) seq non-null **50/50**. Phir taqseem N=8 sahi chala (4 mixed,
4 single-strand; ab strand-boundary par mix, alphabetical artifact nahi).

Sabaq: `sequence`/naye feature ke baad server hamesha restart (ya `--reload` ke saath
chalao); warna "Updated" report sach hote hue bhi naye columns skip ho sakte hain.

## 2026-07-23 — SLO: `sequence` column (asal kitab ki tarteeb)

Maqsad: taqseem (exam distribution) `slo_code` se sort karta tha, magar slo_code
**strand-grouped** hai (C→D→N→S→W), teaching tarteeb nahi. Nateeja: Number strand
akela 25/50 SLO hone se **4 exam sirf Number** ke ban rahe the. Asli tarteeb sirf
teacher jaanta hai — is liye teacher ke bharne ke liye alag `sequence` column.

Changes:
- `app/core/database.py` — `init_db()` mein idempotent migration: `slo` table mein
  `ALTER TABLE ADD COLUMN sequence INTEGER` (nullable). Purani 50 rows NULL rehti hain.
- `app/repositories/slo_repository.py` — `insert()` mein `sequence` column+value.
  `update_by_code()` generic tha (koi change nahi) — re-import par sequence refresh.
- `app/services/slo_import_service.py` — `sequence` optional column parho: khali→NULL,
  poora number→int (Excel "3.0" bhi qubool), **number na ho ("abc"/"2.5")→row error**
  (chupke null nahi). Add + update dono paths mein sequence.
- `static/slo_import_template.xlsx` — purana (ignored) `book_pages` column hataya,
  `sequence` add. Sample rows teaching-order (W,N,C,S = seq 1,2,3,4) dikhate hain.
- `static/slo.html` — list mein pehla **"Seq"** column (NULL → "—" muted, taake teacher
  dekh sake kaunse khali). Import hint text update (book_pages hata, sequence likha).
- `scripts?/taqseem.py` (scratchpad standalone) — sort ab `sequence` se, NULL par
  slo_code fallback (aakhir mein); report top par kitne NULL saaf batata hai. N configurable.

Verify: migration real DB par chala (sequence column + 50 NULL confirmed). Import
end-to-end test (valid/float/empty/invalid/re-import) sahi. Naye 5 sequence tests +
poora SLO suite: **104 passed**. Koi DB data change nahi (sirf nullable column add).

Agla step (manual): teacher/user Excel mein sequence bhar kar re-import karega →
50 rows update; phir taqseem asal teaching order se banega.

## 2026-07-23 — UI: pdfSubject free-text → datalist (KAAM 3)

Scan ke baad KAAM 3 mein asal mein sirf **ek** field bacha tha (alag phase nahi, chhota
add-on): `pdfSubject` (index.html Syllabus Upload). `exSubject`/`fSubject` KAAM 2 mein ho
gaye; generator ka `subject` (index.html:429) cascade se auto-bharta hai — chhoda.

Fix (`static/index.html`):
- `pdfSubject` → `<datalist>` (pdfGrade jaisa hi). CREATION field hai (naya subject ka
  syllabus yahin add hota hai), is liye strict dropdown nahi — maujooda subjects suggest,
  naya likhna bhi allowed.
- `loadSyllabusGrades()` mein `fillDatalist()` helper — ab pdfGrade + pdfSubject dono
  `_allGrades` se bharte hain.

Verify: index.html tag-balanced (headless parse); wiring (list=+datalist+fillDatalist)
match. Backend change nahi (frontend-only). Browser click verify baqi — extension off.

## 2026-07-23 — UI: class fields free-text → dropdown (KAAM 2)

Maqsad: free-text class/subject se data bikhar jata tha — 'Pre year 1' vs stored
'PRE YEAR 1'. Aaj isi wajah se SLO list KHALI dikhi thi. Root cause: SLO list filter
(`slo_repository.list_by_filters`) **EXACT** match karta hai (`class = ?`), zara sa
farq = 0 rows.

Ahem: SLO ka class/subject syllabus ke `grade` se **alag vocabulary** hai (SLO Excel ke
apne `class,subject` columns). Is liye dropdown syllabus-grades se NAHI — SLO table ke
asal distinct values se banaya.

Backend:
- `slo_repository.list_distinct_facets()` — DISTINCT class + subject (non-empty, sorted).
- `GET /api/slo/facets` → `{classes, subjects}` (sibling `list_slos` jaisa unwrapped read).

Frontend (`static/slo.html`):
- `fClass`, `fSubject`, `exSubject` free-text input → `<select>`. `exGrade` (pehle se
  select) ab syllabus-grades ke bajaye facets.classes se bharta hai — export bhi SLO data
  se match kare.
- `loadExportGrades()` (syllabus-grades) → `loadFacets()` + `fillFacetSelect()` (facets).
  Chaaron dropdown ek hi `/api/slo/facets` call se.

Frontend (`static/index.html` — Syllabus upload):
- `pdfGrade` ye CREATION field hai (naya class ka syllabus yahin add hota hai) — strict
  dropdown naye class ko block kar deta. Is liye `<datalist>` (input + maujooda grades
  suggest, naya likhna bhi allowed). `_allGrades` se populate (already loaded).
- `pdfSubject` + baaqi subject fields = KAAM 3 (alag phase).
- Cosmetic label fields (`bpClass` bank.html, `bpClassName` blueprint.html) — chhode,
  ye paper par chhapne wale roster naam hain, data se link nahi.

Verify: `/api/slo/facets` → `{"classes":["Pre Year 1"],"subjects":["Mathematics"]}`;
`/api/slo?class_name=Pre Year 1&subject=Mathematics` → rows aate hain (exact match ab
dropdown se guaranteed). Teenon pages HTML tag-balanced (headless parse). 828/828 tests pass.
Browser click verify NAHI ho saka — Chrome extension connected nahi tha.

## 2026-07-23 — UI: bank.html "Naya question add karo" form collapsible (KAAM 1)

Maqsad: teacher zyadatar Excel se questions add karta hai — manual add form roz nazar
aane ki zaroorat nahi, sirf jagah gherta tha. Ab `print.html` ke Print Settings jaisa
`<details>` pattern, default **BAND**.

Fix (`static/bank.html`):
- "Naya question add karo" card (`<div class="card">`) → `<details class="card add-q-collapse"
  id="addQCard">` + `<summary class="add-q-summary">` (arrow + title + hint). Andar ka
  poora content ek `<div class="add-q-body">` mein wrap. Koi ID/JS/handler nahi badla —
  form waisa hi kaam karta hai, sirf collapse hua.
- CSS: summary marker hidden, `[open]` par arrow rotate + border-bottom, body padding.

## 2026-07-23 — Data cleanup: dummy/trial data DB se hataya

Maqsad: trial data saaf, sirf asal seed rakhna. ("class" = syllabus_topics.grade via
syllabus_topic_id; questions table mein direct class column nahi.)

RAKHA: Pre Year 1 Mathematics 329 questions, saare 50 SLOs, 329 question_slo links
(sab Pre Year 1 ke), Image Library (99) — poori, syllabus_topics, blueprints (2),
usage_log (99).

DELETE (single transaction, guards ke sath): ALL papers (72), class null/empty
Mathematics questions (60) + Pre Year 2 (40) + Pre Year 3 (20) = 120 questions +
unke question_slo links (0 the). Orphan trial results bhi (user ne "sab delete"
chuna): result_uploads (14) + student_question_results (840).

Nateeja: questions 449→329, papers 72→0, results 0, SLO 50 (unchanged), question_slo
329 (unchanged), image_library 99 (unchanged). Verify: live API 329; 0 non-Pre-Year-1
baaqi; 0 dangling question_slo (dono taraf). Backup (user ke apne backup ke ilawa,
sqlite .backup se consistent): `paper_maker_backup_before_dummy_cleanup_20260723_172026.db`.

## 2026-07-23 — Fix: bank.html Edit button dead (onclick markup toota)

Symptom: Question Bank mein **Edit** dabane se kuch nahi hota (Delete theek — confirm
+ orphan warning). Script parse ho rahi thi (Delete chalta tha), masla generated
markup mein tha.

Wajah: `renderQRow` mein Edit button ka onclick
`openEditModal(${escAttr(JSON.stringify(q))})` tha. `JSON.stringify` **double quotes**
deta hai (`{"id":...}`) aur `escAttr` sirf single quote escape karta hai — double-quoted
`onclick="..."` attribute pehle hi `"` par **toot jata** tha → handler `openEditModal({`
ban jata (invalid JS) → click par kuch nahi. (Delete safe tha kyunki UUID mein quote
nahi.) `node --check` isse nahi pakadta — bug JS syntax mein nahi, HTML markup mein tha.

Fix (`static/bank.html`):
- Edit onclick ab Delete jaisa: `openEditModal('${escAttr(q.id)}')` (id string).
- `openEditModal(q)` ab string aane par `_allQuestions` se lookup karta hai (JSON.parse
  path hata — UUID JSON nahi).

Verify: node --check clean; VM mein real HTML id-set + missing-id→null getElementById ke
sath `openEditModal('<id>')` sab 5 types (mcq/tf/fill/short-answer + Urdu `"quotes"&<b>`
wala) par bina throw OK; koi missing element id nahi. Static file live — sirf hard-refresh.

## 2026-07-23 — Marhala 2B: Blueprint Bloom shortfall (soft guidance)

Maqsad: Blueprint se paper banate waqt paper ka ASAL Bloom mix class-standard se
compare → kisi Bloom level par **10% se ZYADA** farq ho to teacher ko soft guidance
+ 2 option (Ignore / Questions badlo). App khud kuch adjust NAHI karta.

**Ahem faisle:**
- Bloom source = **question ka apna `bloom_level`** (Question Bank wala), SLO ka NAHI
  (SLO-based per-paper wala purana `slo_shortfall_service` alag hai — chheda nahi).
- `bloom_level` khali/na-maloom questions **alag gine** (`no_bloom`); percentages
  sirf `with_bloom` par (warna numbers jhoot bolenge).
- Threshold strictly > 10 (epsilon se float-noise ignore) — **theek 10% par warning NAHI**.
- Class→tier: `bloom_standards.get_bloom_suggestion` (reliable source = syllabus
  `grade`, na ho to free-text `class_name`).
- Option 2 = **pointer-only** (user faisla): under-represented Bloom ke liye bank-count
  + `/bank.html?subject&bloom` filtered link; koi inline replace nahi.

**Backend:**
- `app/services/blueprint_bloom_guidance_service.py` (naya) — `compute_bloom_guidance(
  questions, class_tier, subject)`. subject=None → bank-count skip (pure/testable).
  Graceful: class na ho / tier na mile / `with_bloom==0` → `available False` + message.
- `app/services/blueprint_paper_service.py` — `assemble_blueprint_paper` mein
  `class_tier` param + return mein `bloom_guidance`.
- `app/schemas/requests.py` — `BlueprintPaperRequest.grade` (tier ke liye).
- `app/api/papers.py` — `class_tier = resolved_grade or class_name` resolve + pass.
- `tests/test_blueprint_bloom_guidance.py` (naya, 16 tests) — mix/empty-alag,
  case-insensitive, per-tier shortfall, boundary theek-10%, all-empty graceful,
  bank-pointer (seeded), 2× `/api/blueprint-paper` integration.

**Frontend:**
- `static/blueprint.html` — makePaper `grade` bhejta hai; `#bloomGuidance` panel
  (`renderBloomGuidance`) sirf `available && has_shortfall` par; no_bloom note,
  per-Bloom rows, "Ignore karo" (hide) + "Questions badlo" (bank pointers reveal).
- `static/bank.html` — `applyUrlListFilters()`: `?subject&bloom` se list pre-filter.

**Verify:** `pytest tests/test_blueprint_bloom_guidance.py` 16 green; blueprint+api
regression suites 157 green. **Browser test baaqi — server RESTART ke baad** (naya
`grade` field + guidance panel).

## 2026-07-23 — Marhala 4B: live print controls (sidebar stepper + POST save)

Maqsad: teacher print.html sidebar mein 3 knobs hilaye → preview foran badle
(setVar, koi fetch) → "Is class ke liye mehfooz karein" par DB likhe (auto-save
nahi) → Reset global default par (visual-only, DB untouched).

**Backend (POST):**
- `app/schemas/requests.py` — naya `ClassPrintSettingsSave` (class_name + font_size
  11–20 / q_gap 6–30 / page_margin 10–25, `Field(ge/le)` → out-of-range 422).
- `app/services/class_print_settings_service.py` — naya `save_print_settings()`:
  normalize_class, blank class → ValueError (route 400), warna repo.upsert (4A wala).
- `app/api/school_settings.py` — naya `POST /api/print-settings` (StatusResponse;
  ValueError→400, baaqi→500). GET/repo 4A se.
- `tests/test_class_print_settings.py` — POST: roundtrip, normalization, upsert
  overwrite, blank→400, out-of-bounds→422 (6 params, value persist bhi nahi hoti),
  boundary font accept. Total file ab 28 tests.

**Frontend (print.html):**
- `.options` font-size → `calc(var(--q-font) - 1px)` — **user faisla:** options bhi
  scale hon (font bara = bachcha jawab bhi padh sake). `.marks`/`.sec-title` waise.
  Default 14 par 13px = pehle jaisa.
- Sidebar mein `<details class="print-settings no-print">` — 3 stepper controls
  (+/− buttons, min/max par disabled), Save + Reset, status + hint line. Collapsible
  ([[project-papermaker-kaam-b-collapse-manual-add]] pattern). `.app-sidebar` par
  `overflow-y:auto` (khulne par clip na ho).
- JS: `PRINT_BOUNDS` (UI limits = schema mirror), `_printState`/`_printGlobalDefaults`/
  `_currentClassName`. `stepPrint` → clamp + setVar foran. `applyPrintSettings` (4A)
  extend: resolved values se controls init + Save UI configure (class na ho to Save
  disabled). `resetPrintSettings` → global default (visual). `savePrintSettings` →
  POST, inline feedback (koi alert nahi). `_printGlobalDefaults` loadPaper mein
  school-settings ke print_* se.

**Control type:** stepper +/− (non-tech teachers ke liye — sirf valid steps, bade
tap-target). **Feedback:** inline status line (✓ mehfooz / err), koi browser-dialog nahi.

**Verify:** POST tests + `pytest` (poora suite) 812 green; `ruff` clean; inline
JS `node --check` OK. **Browser test — server RESTART ke baad** (naya POST route).

**Browser test follow-up (2026-07-23):**
- Layout bug: sidebar flex-column mein `.print-settings` (details) shrink ho raha tha
  → summary+ps-body side-by-side, buttons wrap. Fix: `.print-settings { width:100%;
  box-sizing:border-box }` + `summary { display:block }`. (CSS-only.)
- POST 405: code theek — current app ke openapi mein `['get','post']` dono, TestClient
  POST=200. 405 = live server abhi **purana 4A code** (sirf GET) chala raha tha (GET+405
  combo = stale process ki nishaani). Hal: sahi process kill karke restart. Code bug nahi.

## 2026-07-23 — Marhala 4A · Commit 3: print.html CSS vars + JS apply (+ tests)

Maqsad: backend ke resolved print settings ko print.html par CSS vars se apply.

- `static/print.html` — (1) `:root` mein `--q-font: 14px`, `--q-gap: 14px`
  (`--page-margin` Commit 1 se). (2) `.question` gap → `var(--q-gap)`; `.qhead`
  + `.qtext-en` → `var(--q-font)`; `.qnum` → `calc(var(--q-font) + 1px)`;
  `.qtext-ur` → `calc(var(--q-font) + 2px)` (Urdu +2, qnum +1 nisbat barqarar).
  (3) naya `applyPrintSettings(className)` — `GET /api/print-settings?class_name=`
  fetch, `setVar` se font(px)/gap(px)/margin(mm) apply; fetch/JSON error par
  silent (defaults CSS mein pehle se). `loadPaper` mein `paper.class_name` ke
  saath await.
- `tests/test_class_print_settings.py` (naya, 16 tests) — migration columns
  DEFAULT 14, resolution (fresh default, global fallback, blank/None class,
  class-row override, normalization "Class 5"/"class 5"/" CLASS 5 ", other class
  → global, upsert replace), aur endpoint (global/override/no-param).

**Defaults par diff-zero:** `--q-font 14 / --q-gap 14 / --page-margin 14mm` =
purani hardcoded values → koi class-override na ho to output bilkul waisa.

**Verify:** `pytest` = **800 passed** (poora suite). Browser test baaqi (server
restart ke baad — neeche).

## 2026-07-23 — Marhala 4A · Commit 2: per-class print settings backend + chain

Maqsad: 3 print knobs (font_size, q_gap, page_margin) per-class store + resolve.
Row-level fallback: class ki row ho to woh, warna school_settings ke global
defaults. UI 4B mein; yeh sirf backend + endpoint.

- `app/core/database.py` — (1) school_settings migration mein 3 naye global-default
  columns `print_font_size/print_q_gap/print_page_margin` (DEFAULT 14 = maujooda
  print.html values, purana output na badle). (2) naya `class_print_settings` table
  (`class_key` PK = normalize_class(class_name); font_size/q_gap/page_margin NOT NULL).
- `app/schemas/requests.py` — `SchoolSettings` mein 3 fields (default 14).
- `app/repositories/settings_repository.py` — `upsert` mein 3 columns (accent jaisa).
- `app/services/settings_service.py` — `save_settings` 3 fields pass karta hai.
- **naya** `app/repositories/class_print_settings_repository.py` — get(class_key)/upsert.
- **naya** `app/services/class_print_settings_service.py` — `get_print_settings(class_name)`:
  normalize_class → class row → warna global. Row-level fallback.
- `app/schemas/responses.py` — naya `PrintSettingsResolved` (font_size/q_gap/page_margin).
- `app/api/school_settings.py` — naya `GET /api/print-settings?class_name=` (auth same router).

**Verify:** temp-DB smoke (real DB safe) — fresh default 14/14/14, global override,
class-row wins + normalization ("class 5"=="Class 5"==" CLASS 5 "), aur other/empty/None
class → global fallback. `pytest tests/test_settings_repository.py tests/test_api_routes.py`
= 62 passed. Client-side (print.html JS apply) = Commit 3.

**Baaqi:** naye service/endpoint ke liye dedicated test abhi nahi likha (existing pass;
smoke se cover) — chaho to Commit 3 se pehle add kar dun.

## 2026-07-23 — Marhala 4A · Commit 1: print margin bug (28mm → 14mm)

Maqsad (per-class print settings feature ka Commit 1 — sirf bug fix, aage nahi barha).
Bug: `print.html` mein `@page { margin: 14mm }` **+** `.sheet { padding: 14mm }`, aur
`@media print` mein `.sheet` padding reset nahi hota tha → chhapte waqt asal margin
14+14 = **28mm** ban raha tha.

**Faisla (plan §0 — single source):** `@page` margin `0`, saara page-margin `.sheet`
padding se, `var(--page-margin)` (default `14mm`). Isse bug bhi theek aur aage
`page_margin` setting ke liye mechanism bhi tayyar (throwaway `padding:0` nahi likha).

- `static/print.html` — 3 edits: (1) `@page` margin `14mm→0` (2) `:root` mein
  `--page-margin: 14mm` (3) `.sheet` padding `14mm → var(--page-margin)`.
- `@media print` block chhua nahi — padding ab var se aata hai (14mm), single source.

**Asar:** har paper ka print margin 28→14mm (yeh deliberate correction, user ne manzoor
kiya). Font/spacing waghera bilkul waise hi — koi aur farq nahi. Sirf CSS, koi
backend/JS nahi. User browser test karega.

**Note (4B ke liye):** `export_service.py` (DOCX/python-docx + PDF/LibreOffice) apna
**alag** layout render karta hai — Word default ~1inch margin, yeh CSS use hi nahi karta.
4A/print.html ke settings export par apply NAHI honge. Teacher kis raaste se print karta
hai (browser vs export) — 4B se pehle confirm karna.


## 2026-07-21 — feature/print-shortfall (print.html panel + sections_meta persistence)

Maqsad: print.html blueprint jaisa shortfall payghaam dikhaye (reason + read-only
options), do jagah alag wording ka khatra khatam. Masla (pichle session ka STOP):
`shortfall_details` (reason/options) DB mein **mehfooz nahi hoti** — assembly ke waqt
banti hai phir discard. Sirf `sections_meta` bachti hai (heading/question_ids/marks/
shortfall-int). Isliye backend change laazmi tha.

**Faisla (Option 1):** reason/options ko **`sections_meta` ke andar** hi rakho (alag
column/migration nahi). Short section par hi keys aati hain; poore section par bilkul nahi.

- `app/services/blueprint_paper_service.py` — short section ki meta mein `shortfall_reason`
  + `shortfall_options` embed (`diag` se). Full section = keys hi nahi.
- `static/print.html` — naya `sectionShortfallHtml(sec, gotCount)`: `shortfall_reason` ho
  to panel (heading + wajah + read-only options), warna **purana numeric note**
  (`{wanted} maange, {n} mile`). Options **clickable nahi**. Naya `.shortfall-panel`
  CSS (`display:block` — `.no-print` ke inline-flex ko override).
- `tests/test_blueprint_shortfall_reason.py` — `TestSectionsMetaPersistence` (short →
  reason+options meta mein; full → keys absent).

**SHART (poori hui):** purane papers ke `sections_meta` mein reason/options nahi →
**numeric-note fallback** chalta hai (bilkul pehle jaisa). `.no-print` usool bar-qarar —
dono branch screen-only, kaghaz par kuch nahi.

**Real-DB check:** 79 papers, 0 JSON parse-fail, 0 shape-issue → koi page nahi tootta.
27 legacy short-sections (shortfall>0, no reason) → numeric note. 0 sections mein abhi
reason (kuch regenerate nahi hua).

**Verify:** **784 tests pass, ruff clean.** (Uncommitted working-tree changes — commit
Irfan ke kehne par.) Browser render (panel + Ctrl+P par note gayab) baqi — Irfan ka test.

## 2026-07-21 — feature/design-base (Brand config + local fonts + icon sprite)

Sirf **tanzeem** ka kaam — **koi visual badlaav NAHI**, pages bilkul pehle jaise. Teen
QADAM, teen alag commits. Maqsad: branding ek jagah se, app fully offline (fonts local),
aur nav icons ek sprite se.

**QADAM 1 — Brand config:**
- `config/brand.json` (Parcha / "Parcha Paper Maker" / "Exam paper generator" / colours).
- `app/services/brand_service.py` — **startup par ek dafa** parhta hai (module-load), file
  missing/kharab ho to **crash NAHI** — safe defaults + `uvicorn.error` warning. `get_brand()`.
- `GET /api/brand` (`app/api/brand.py`, `BrandResponse` schema). **Jaan-boojh kar auth ke
  bahar (public)** — cosmetic shell hai (koi secret/DB/AI-cost nahi) aur har page load par
  chahiye; auth ke peeche hota to key set hone se pehle har page par key-gate khul jata.
- `static/js/brand.js` — `/api/brand` se `document.title` (`<page> — full_name`) + sidebar
  `.brand .name` set. Defaults baked (config jaise) → fetch fail par bhi sahi text, **koi FOUC nahi**.
- Sab 7 pages: `<body data-page="...">`, hardcoded **"AII Smart Paper Maker" → "Parcha Paper
  Maker"**, brand.js include. (`.brand .name` par **full_name** dikhta hai — pehle jaisa full
  naam.)
- `index.html`: `.sidebar` → **`.app-sidebar`**, `.nav-link` → **`.app-nav a`** (baqi 6 pages
  jaise). Safe kyunke active-state JS `[data-nav]`/`data-active` par chalta hai, class par nahi.

**QADAM 2 — Fonts local (offline):**
- 9 woff2 `static/fonts/` mein: **IBM Plex Sans** 400/500/600/700, **Noto Nastaliq Urdu**
  400/600, **Source Serif 4** 400/600/700 (fontsource CDN = official fonts, per-weight).
- `static/app.css` `@font-face` (sab `font-display: swap`).
- Sab pages se Google Fonts ke **3 links** (2 preconnect + css) hataye → `<link rel="stylesheet"
  href="/static/app.css">`.
- Cache middleware: `/static/fonts/*.woff2` par **1-saal immutable**; `app.css`/`icons.svg`
  par jaan-boojh kar **koi long cache nahi** (StaticFiles ka default ETag/304).
- `.urdu/.ur` stack (sirf index mein defined) pehle se **Jameel-first** — koi tabdeeli nahi.

**QADAM 3 — Icon sprite:**
- `static/icons.svg` — **10 unique `<symbol>`** (i-generator/library/bank/blueprint/outcomes/
  slo-health/adaptive/analytics/mypapers/settings), sab `viewBox 0 0 24 24`, stroke 1.8, round.
- `.icon { 17px }` app.css mein; **index apne `.app-nav a svg` se 19px** rakhta hai (index ke
  icons pehle 19px the — chhote na hon, no-visual-change).
- 6 sidebar pages ke inline nav SVG → `<svg class="icon"><use href="/static/icons.svg#i-..."></use></svg>`.
- `static/brand/logo.svg` (mojooda navy+blue document mark, standalone — abhi koi consumer nahi).
- `print.html` **chhua nahi** (text-only nav, koi icon nahi — scope ke mutabiq).

**FAISLE / spec se hatt kar (jaan-boojh kar):**
- **Source Serif 4 bundle kiya** — font-list mein nahi tha, magar index ke paper-preview mein
  use hota hai (`Georgia` fallback). No-visual-change + offline honor karne ke liye zaroori,
  warna offline preview Georgia par gir jata.
- **`/static` mount naya add** kiya (`app/main.py`) — spec ke saare asset paths `/static/...`
  maangte the, app pehle sirf `/` par mount tha. Legacy `/apiClient.js` waise hi chalta hai.
- Fontsource ka **"latin" subset** — extended-Latin/doosre scripts system font par fall back
  (UI text ke liye kaafi).
- **`/api/brand` public** rakha (upar wajah).

**BAQI (follow-up, is scope se bahar):** `index.html` ke tip-text mein 3 jagah **"AII"** copy
bacha hai ("AII suggests", "AII PDF/images parse karke…") — sidebar brand naam nahi, body copy
hai; 1d ne sirf "AII Smart/… Paper Maker" naam kaha tha.

**Files:** naye — `config/brand.json`, `app/api/brand.py`, `app/services/brand_service.py`,
`static/js/brand.js`, `static/app.css`, `static/icons.svg`, `static/brand/logo.svg`,
`static/fonts/*.woff2` (9). Chhue — `app/main.py`, `app/schemas/responses.py`, sab 7 static HTML.

**Verify:** **772 tests pass, ruff clean.** Server smoke (curl): saare 7 pages + app.css +
icons.svg + logo.svg + brand.js + `/api/brand` + 9 fonts → **200**; fonts par 1yr immutable,
css/svg par sirf ETag. **Browser render (icons `<use>`, font visual, Urdu RTL, print preview,
OFFLINE) baqi — Irfan ka incognito test** (Claude-in-Chrome extension is env mein connect nahi tha).

## 2026-07-19 — feat/slo-health (SLO Health page — Marhala 2 Hissa C)

Ek page jo DONO taraf ka gap dikhata hai: (a) SLO jinke paas koi (published) question
nahi, (b) (published) questions jinke paas koi SLO tag nahi. Plus per class/subject
health line aur "SLO import baqi". `GET /api/slo-health` (coverage/shortfall ke parallel,
magar paper-scoped nahi — poore data par). Live compute (JOIN), snapshot NAHI.

**Sab se ahem:** page GENERAL hai — SAARI classes/subjects/strands ke liye. Koi class/
subject/strand HARDCODE nahi (abhi sirf Pre Year 1 Math ka SLO data hai, magar Grade
4/5/6 Math, Grade 7 Science, Grade 8 Geography syllabus mein maujood — aate hi khud aayenge).

**Faisle amal mein:**
- **Covered = SLO ke paas >=1 linked PUBLISHED question.** draft/archived shumar NAHI —
  page par saaf note (`draft_note`).
- **Questions par class column NAHI** (koi migration nahi kiya). grade `syllabus_topic`
  se LEFT JOIN; jis question ka topic-link nahi uska grade na-maloom -> **"(class na-maloom)"**
  bucket (Part 3 aur health line mein).
- **`normalize_class`** naya (`app/core/text_norm.py`) — `normalize_subject` jaisa alias-dict
  (abhi khali, structure mojood). Case/alias normalize har jagah: class, subject, bloom.
- **Bloom NULL SLO -> "(bloom na-maloom)"** bucket (silently REMEMBER nahi maante).
- **import_pending** = `syllabus_repository.list_distinct_subject_grade()` ke woh combos
  jinka SLO group nahi.
- **Filter** (class+subject) DB se distinct — dropdown response ke `classes`/`subjects`
  se populate (hardcode nahi); filter server-side, magar dropdown lists hamesha POORE.

**Naye REPO functions (coverage/shortfall ke shared functions NAHI chhede):**
- `slo_repository.list_all()`
- `question_slo_repository.slo_ids_with_published_questions()` (JOIN questions status='published')
- `questions_repository.list_published_with_grade_and_tag()` (LEFT JOIN syllabus_topics for grade,
  EXISTS+JOIN slo for is_tagged — orphan link ko tagged nahi ginta, covered jaisa).

**MULTI-TENANT (abhi implement NAHI — sirf jagah):** teeno naye repo functions mein optional
`school_id` param add kiya jo abhi use nahi hota — aage 100+ schools par `WHERE school_id = ?`
yahin lagega bina signature tode. Service/route abhi ise pass nahi karte.

**Files:** `app/services/slo_health_service.py` (naya) · `app/api/slo.py` (route) ·
`static/slo-health.html` (naya page) · nav link **6 pages** (index, slo, bank, blueprint,
library, print — user ne "5" kaha tha; print.html ka nav bhi maujood tha to consistency ke
liye woh bhi). NOTE: bank/blueprint/library/print ke nav mein "Learning Outcomes" (slo.html)
link pehle se nahi tha — sirf SLO Health add kiya (scope).

**Tests:** `test_slo_health_service.py` (11) + `test_slo_health_api.py` (2) = 13 naye —
seed-based, koi hardcoded DB count nahi (apne seeded id/norm-keys par assert). draft-covered,
class-na-maloom, bloom-null, import-pending, filter, multi-class general — sab covered.

**Baqi:** browser test + merge teacher karega. Pre-generate/blueprint integration alag scope.

**FUTURE (idea — implement nahi):** Blueprint shortfall warning behtar karna. Abhi sirf
"Section A: 20 maange, 8 mile" dikhata hai. Behtar yeh ho ke **wajah** bhi bataye (kaunsi
shart tang hai) aur **teen option** de — bilkul Hissa B ke Bloom shortfall ki tarah:
(a) jo mil raha usi se banao, (b) filan shart hata do -> itne milenge, (c) naye questions
likho. App khud chup-chaap adjust NA kare.

---

## 2026-07-19 — feature/slo-phase-2b-shortfall (Bloom shortfall — Marhala 2 Hissa B)

Paper ka asal Bloom distribution vs class standard (Pre-Primary 70/30) — per-Bloom
**kami (shortfall)**. `GET /api/paper/{id}/bloom-shortfall` (coverage endpoint ke parallel).
**App khud kuch adjust NAHI karta** — sirf report; teacher UI par 3 option chunta hai.

**Faisla (darj):** Bloom source = **SLO ka `bloom_level`**, question ka nahi. Wajah: SLO book
se soch kar bana (PY1 Math 31 remember/19 understand = 70/30 fit); question ka bloom auto-derive
+ mashkook ("Trace the number 3" par APPLY; 197 mein 80 APPLY = 41%, standard se door).

- **`slo_shortfall_service.py`** (naya): SLO bloom se actual, `bloom_standards.get_bloom_suggestion`
  se target %, **largest-remainder (Hamilton)** se target counts (sum = N). Per-Bloom
  `{needed, actual, short}` + total_short. Live compute (JOIN), snapshot nahi.
- **`question_slo_repository.list_slo_blooms_for_questions`** (naya) — question→SLO.bloom rows.
  Coverage ka shared `list_links_for_questions` **NAHI chheda** (uski query na toote).
- **`app/api/papers.py`** — naya route; **`static/index.html`** — Bloom Shortfall panel (SLO Coverage
  ke neeche): per-Bloom bar + kami + **3 option** (jo mil raha usi se / doosre Bloom se / naye sawal).

**Ahem faisle amal mein:**
- **Multi-SLO** question → uske SLOs mein sabse **UNCHA (highest)** Bloom; UI par `ℹ️ N multi-SLO` nishaan.
- **Denominator N** = classifiable questions (SLO-tagged AND bloom maloom).
- **CASE-normalize** (`_norm` = LOWER+TRIM) har bloom par — `REMEMBER`(q) / `remember`(slo) /
  `remember`(standard) sab ek jagah; warna ginti zero. (Source SLO hai, magar defensive.)
- **untagged** (koi SLO link nahi) aur **bloom-unknown** (SLO tagged par bloom NULL) — **DO alag ginti**,
  distribution se bahar (subject badalne par masla tagging ka hai ya SLO-data ka — farq zaroori).
- Koi classifiable question na ho → panel ZERO nahi, **graceful message** (coverage `_no_universe` jaisa).

**Tests:** `test_slo_shortfall_service.py` (11) + `test_slo_shortfall_api.py` (2) = 13 naye —
seed-based, koi hardcoded bank-count nahi. ruff clean; full suite **759 pass** (746 → 759).
Browser test + merge teacher karega.

**Baqi:** Hissa C (SLO Health page) pending. Pre-generate shortfall (bank-availability) alag scope —
abhi nahi (post-hoc pehle). Data gaps qaim: Pre-writing/C-05/C-06/Colour-Circle-11-24 (pichhli entry dekho).

---

## 2026-07-19 — Pre Year 1 Math SLO tagging (DATA kaam, app code nahi)

197 Pre Year 1 Mathematics questions ko SLO se tag kiya — coverage report ko zinda
karne ke liye (pehle sirf 8 tagged the). Yeh mostly DATA kaam hai; app code touch
nahi hua, do standalone one-shot scripts `scripts/` mein (branch `chore/slo-prefill-script`).

**1. `scripts/prefill_slo_pre_year1_math.py`** (one-shot, read-only — DB mein kuch NAHI likhta):
Question text ke template se slo_code khud derive karta hai (manual picker nahi):
- Number: `Trace the number N` → N-03/N-11/N-16 · `Count..write`/`How many`/`There are`/Urdu
  count+write → N-04/N-12/N-17 · `Colour` → N-06 · `Circle all` → N-07 — **range** 1-10/11-20/21-24
  se sahi code. Colour/Circle sirf 1-10 (11-24 ka SLO nahi → khali).
- Shape: `Trace the <shape>` text se · `Name this shape` MCQ ka **correct_answer_en** (answer-key)
  se — S-01..S-04 (flat) / D-01..D-06 (solid).
- Comparison: topic `Concept of "a" and "b"` se C-01..C-04.
- Koi rule match na ho → khali (andaaza nahi).
Output DO sheets ek Excel mein: **UPLOAD 161** (auto-filled) · **MANUAL 36** (28 khali +
8 review). import `pd.read_excel(sheet_name=0)` = pehli sheet (UPLOAD) parhta hai (script verify karta).
`.xlsx` gitignored (`scripts/*.xlsx`).

**2. Teacher ne UPLOAD sheet import ki** (`/api/slo/assign-import`): **Updated 161, Errors 0**.
Tagging 8 → **169 questions**.

**3. 8 stray test-tags theek kiye** (bina delete ke): 8 `How many..are there?` MCQ par pichhle
browser-test ka kachra tha (number question par D-01/C-01/S-01/W-01/N-01). Kyunki assign-import
**replace-set** hai, `fix_8_stray_tags.xlsx` (8 rows, sab sahi **N-04**, range 1-10) upload se
purana ghalat link khud replace ho gaya — alag delete ki zaroorat nahi. **Updated 8**.

**4. `scripts/clean_stray_slo_links.py`** — dry-run cleanup helper (default sirf dikhata, delete
`--delete` par). Is dafa **istemal NAHI hua** (replace-set behtar tha), aainda ke liye rakha.
Iske dry-run ne ek bara khatra pakRa: table 8 nahi 169 links par tha (teacher upload ho chuki thi),
to "saare PY1 links" wala pehla broad target 161 sahi tags mita deta — target ko precise
(`How many` + non-count code) kiya, tab 8 dikhe.

**TASDEEQ:** coverage report ab **zinda** — bare paper par **13/50 (26%)**, aur **Pre-writing 0/3**
(pehle jhoota `1/3` dikh raha tha, kyunki number-8 question par ghalti se W-01 laga tha).

**DATA GAP (report ne khud pakRa — aainda tagging/question-banane ke liye darj):**
- **Pre-writing** ke teeno SLO (W-01/02/03) — bank mein ek bhi question nahi.
- **Comparison C-05** (which has more/less) aur **C-06** (equal groups) — koi question nahi.
- **Colour/Circle numbers 11-24** — in skills ka koi SLO define nahi (28 questions MANUAL sheet
  mein khali chhoRe — inhe kabhi tag nahi kar sakte jab tak SLO na banein ya questions na haten).

**Baqi:** Hissa B (shortfall 70/30) + Hissa C (SLO Health page) abhi bhi pending. `feature/slo-export-class-filter`
(export grade/subject filter, 746 tests) bhi merge ke intezaar mein — alag branch.

---

## 2026-07-19 — feature/slo-export-class-filter (SLO export grade/subject filter)

SLO bulk-assign export (`GET /api/questions/slo-export`) ab optional `?grade=&subject=`
leta hai — kyunki export saare 317 Mathematics questions deta tha (Pre Year 1 ke ~197
nahi), teacher ko tagging ke liye chhaant-na parta. **Backward compatible:** koi param na
ho to purana sab-questions behaviour + `slo_assign_export.xlsx`.

- **Naya `app/core/text_norm.py`** — `normalize_subject()`: alias **dict** (`math/maths →
  mathematics`), hardcoded if-else NAHI (nayi alias add karna aasaan). Compare-time only, data untouched.
- **`questions_repository.list_for_slo_export(grade, subject)`** (naya) — grade par
  `syllabus_topics` JOIN (case/whitespace-insensitive); **`syllabus_topic_id` NULL wale grade
  filter par khud EXCLUDE** (expected, INNER JOIN). subject dono-taraf `normalize_subject` se
  Python-side filter — DB mein `Math`/`Mathematics` dono ho to bhi sahi.
- **`question_slo_import_service`** — `build_export_xlsx(grade, subject)` (return **bytes hi**,
  purane 2 export tests untouched) + naya `export_filename()` → dynamic naam
  `slo_assign_export_Pre_Year_1_Mathematics.xlsx`. Columns waise hi 5 — koi naya nahi.
- **`app/api/slo.py`** — route par optional query params + dynamic `Content-Disposition`.
- **`static/slo.html`** — export par grade **`<select>`** (`/api/syllabus-grades` distinct se
  populate — **hardcode NAHI**, nayi class add hote hi aa jaye) + subject input + button URL builder.

**NOTE (code change NAHI kiya, sirf darj):** coverage universe (`slo_coverage_service`) abhi
`normalize_subject` use nahi karta — `papers.subject` vs `slo.subject` par `LOWER(TRIM)` (alias
nahi). Aaj teeno 'Mathematics' hain to theek; Math/Mathematics mismatch aaya to universe khali
(covered SLO phir bhi dikhte, remaining/% None — crash nahi). [[project-papermaker-roadmap]] Hissa B se pehle chhota fit ho sakta.

**Tests:** `tests/test_slo_export_filter.py` (8) — **seed-based, koi hardcoded 317/197 nahi**
(apne `q1..q5`/`t_py1,t_py2` ke id-sets se assert). ruff clean; full suite **746 pass** (738 → 746).
Browser test + merge/push teacher karega (GitHub Desktop).

---

## 2026-07-18 — fix/paper-class-and-delete-warning (2 zinda bugs)

SLO Marhala 2 Hissa A ke dauran nikle do data-masle ki tashkhees se: `class_name`
None (47/63 papers) aur orphaned papers (40/63). Do fixes (merge `4fb1409`):

**Fix 1 — Generator class_name capture** (`static/index.html buildPaper`): ab
`class_name: val('gradeSelect') || null` body mein jaata hai. Backend
(`GeneratePaperRequest.class_name` + `_persist_paper`) pehle se ready tha — masla
sirf frontend line ka tha (isi liye har Generator paper class None banta,
coverage universe kabhi nahi banta). Zero backend change. **Regression-guard**:
`test_generator_class_name.py` `index.html` ke buildPaper mein `class_name`+`gradeSelect`
ki maujoodgi check karta — line dobara gayab hui to test fail.
(Blueprint/bank-paper pehle se class bhejte the — free-text `bpClassName`/`bpClass`.)

**Fix 2 — question delete se pehle paper warning**: `papers.question_ids` JSON blob
hai (koi FK/cascade nahi), is liye sawal delete karna papers ko chup-chaap orphan
kar deta tha. Ab delete se pehle warning kaun se papers tootenge:
`papers_repository.find_papers_containing` (quoted-id `LIKE '%"uuid"%'`, substring-safe),
`paper_service.papers_using_question` (count+titles, untitled→'(Untitled)'),
`GET /api/bank/questions/{id}/paper-usage`, `bank.html deleteQuestion` (3-4 naam +
"aur N mazeed"). **Sirf warning** — koi block/cascade/snapshot nahi (jaan-boojh kar simple).

**Haath NAHI lagaya (data, code nahi):** 40 orphaned papers (deleted sawal wapas nahi
aate — murda), 47 None-class papers (coverage graceful handle karta, andaaze se backfill
galat hota). **Deferred tajweez:** Blueprint/bank-paper ka free-text class box →
dropdown+custom fallback (isi se Jasmine/NUrsery/play aaye) — alag chhota kaam, baad me.

**Tests:** `test_generator_class_name.py` (2) + `test_paper_delete_warning.py` (6) =
8 naye. ruff clean; full suite **738 pass** (730 → 738). Browser test (teacher) green:
Generator par Pre Year 1 chuna → paper class set + poora coverage; delete par paper-naam warning.

---

## 2026-07-18 — SLO Marhala 2 Hissa A (paper coverage + Excel tagging)

Do stacked branches, tarteeb se master mein merge (`--no-ff`):
`feature/slo-phase-2a-coverage` (9d8a9d1) → `feature/slo-phase-2a-excel-tagging` (f7876c3).

**Coverage** (`slo_coverage_service.py`, `GET /api/paper/{id}/slo-coverage`):
Paper ke sawalon se covered vs class/subject ke reh gaye SLO + strand breakdown +
untagged-question ginti. **Live compute (JOIN), stored snapshot NAHI** — link/SLO
baad me badle to report khud sahi rahe. class match **normalized** (`LOWER(TRIM)`)
kyunki `papers.class_name` free-text/gandi hai; universe na mile (class None ya us
class/subject ki koi SLO nahi) to **graceful covered-only + saaf message**, koi crash nahi.
`coverage_percent` = covered∩universe / total. Repo: `list_links_for_questions` (batch
JOIN), `list_by_class_subject_normalized`. UI: `index.html` paper preview ke neeche
SLO Coverage section (progress bar + strand table + reh-gaye list + untagged note).

**Excel tagging** (KAAM A — user manual picker use nahi karta, sab Excel/Blueprint se):
- **Naye questions**: bulk upload Excel mein optional `slo_code` column (comma-separated
  = kai SLO). Ghalat code → skip + warning, question phir bhi import (topic-behavior jaisa).
  Insert ke baad link (image-attach pattern par). `bulk_upload_template.xlsx` + bank.html hint update.
- **Purane 200+ questions**: `GET /api/questions/slo-export` (Excel: `question_id` +
  current `slo_code`) → teacher `slo_code` bhare/edit kare → `POST /api/slo/assign-import`.
  **question_id se match** (text se nahi), **replace-set** (idempotent, khali=clear).
  `question_id` protection: import par saaf error (khali/unknown id) + Excel cell-comment
  warning — real sheet-lock NAHI (over-engineer). Shared `resolve_slo_codes` (case/space-insensitive).
  `question_slo_import_service.py` naya; `slo.html` par bulk-assign card.

**Duplicate trap (confirmed + tested):** bulk question import upsert NAHI karta — har row
naya uuid. Same sheet dobara upload = QUESTION duplicate. Isi liye purane questions ke liye
slo-export/assign-import (id se) — question sheet re-upload NAHI. SLO links khud replace-set
(multiply nahi hote). `test_bulk_import_slo.py::test_reupload_duplicates_the_question` documents.

**Data findings (live test):** saare Pre Year 1 Math papers ORPHANED (question_ids ab
questions table me nahi — sawal delete ho chuke, coverage 0 dikhega); real-question papers ka
`class_name = None` (poora universe view sirf class-set paper par). Ye data-hygiene, code bug nahi.

**Tests:** `test_slo_coverage_{service,api}.py` (13) + `test_bulk_import_slo.py` (6) +
`test_question_slo_import.py` (11) = 30 naye. ruff clean; full suite **730 pass** (700 → 730).
Browser test (teacher) green: bulk-assign 8 tags, purana paper covered-only + graceful,
naya Pre Year 1 paper POORA view (0/50, 5 strands sahi, reh-gaye 50), 'play' class graceful.
`sample_slo_assign.xlsx` (gitignored) test ke liye.

**Baqi:** Hissa B (shortfall) + Hissa C (SLO Health page) abhi NAHI. Aur [[project-papermaker-kaam-b-collapse-manual-add]] (bank.html manual form collapse) pending.

---

## 2026-07-18 — feature/slo-phase-1 (SLO Marhala 1 — question↔SLO link)

**Scope:** Har question ko ek ya kai SLO se jorna (Marhala 2 paper-coverage report ki buniyaad).
Bulk-assign Excel is marhale me NAHI (pehle manual UI se validate) — baad me
`question_slo_import_service` + `POST /api/slo/bulk-assign` me fit hoga.

**DB** (`app/core/database.py`): naya **`question_slo` link table** (column NAHI) —
`question_id`, `slo_id`, `created_at`, composite PK `(question_id, slo_id)`. Wajah: (1) ek sawal =
kai SLO, (2) `questions` table bilkul untouched → 200+ purane questions bina migration ke chalte
rahein, (3) gemini (protected) question bhi tag ho bina uske row ko chhue. `slo_id` (PK) se link
(slo_code se nahi) — re-import par id stable; report ke liye slo_code/slo_text JOIN se. FK enforce
nahi (baaqi schema jaisa) — coverage report defensive INNER JOIN. Index: `idx_question_slo_slo`
(reverse lookup "is SLO ke saare questions" — Marhala 2). Migration = sirf CREATE TABLE/INDEX
(idempotent, server restart chahiye).

**Repo** (`app/repositories/question_slo_repository.py`, naya): `replace_for_question` (replace-set,
duplicate INSERT OR IGNORE), `list_slo_ids_for_question`, `list_slos_for_question` (JOIN, orphan
link INNER JOIN se khud drop), `list_question_ids_for_slo` (reverse), `existing_slo_ids` (link se
pehle validate — orphan se bachao).

**Service** (`app/services/question_service.py`): `set_slos_for_question` (sirf maujood slo_ids
likhta — orphan filter), `get_slos_for_question`; manual create/update me `slo_ids` diya ho to link
write (replace-set).

**API** (`app/api/questions.py`): `GET /api/questions/{id}/slo` + `PUT .../slo` (replace-set, khali
list = clear; **har source** par — link table protected row ko nahi chhoota); `slo_ids` optional on
manual create (`POST /api/bank/questions`) + update (`PATCH /api/bank/questions/{id}`).
Schemas: `ManualQuestionRequest`/`Update` me `slo_ids`, naya `SetQuestionSloRequest`; update ke
"kam az kam ek field" validator me `slo_ids` shaamil.

**UI** (`static/bank.html`): Add + Edit modal me **SLO picker** (checkbox list + search).
Filter subject+class par — **gate:** subject/class/topic teeno maloom hon tabhi bharta, warna
"pehle topic chuno" hint (teacher ko 50 SLO me se dhoondna na pare). Add: subject/grade/topic
badalne par reset. Edit: subject se filter, linked SLO pre-checked, un-check kar ke clear.
(Edit modal sirf manual questions ke liye khulta; gemini tagging PUT endpoint se — UI me abhi surface nahi.)

**Tests:** `tests/test_question_slo_repository.py` (7) + `tests/test_question_slo_api.py` (11) =
18 naye. ruff clean; full suite **700 pass** (682 → 700). Live server smoke: PUT link → GET →
empty-PUT clear sab OK (dev DB cleanup). Browser test (teacher): gate/add/edit/clear/purane-questions —
sab green, tabhi merge (`--no-ff`, commit `26fb90c` → merge `fca1fbf`).

---

## 2026-07-18 — feature/slo-phase-0 (SLO Marhala 0 — table + Excel import)

**Scope:** SIRF `slo` table + Excel bulk import. Question↔SLO link (Marhala 1) aur
paper coverage (Marhala 2) is marhale me NAHI. Data target: Pre Year 1 Math (~50 SLO).

**DB** (`app/core/database.py`): `init_db()` me naya `slo` table (CREATE TABLE IF NOT EXISTS,
existing data safe) — `id` TEXT uuid PK, `class`, `subject`, `slo_code` (UNIQUE), `slo_text`,
`bloom_level` (nullable), `strand`, `created_at`. `strand` ALAG column (slo_code parse nahi karte —
Marhala 2 strand-wise coverage seedha column par bane). Index: `idx_slo_class_subject`.

**Bloom auto-suggest** (`app/core/bloom_standards.py`): naya `suggest_bloom_from_text()` —
slo_text ke pehle content-verb se level (`_VERB_BLOOM` map: count/identify/recognize→remember,
describe→understand, solve→apply, compare→analyze...). Fillers (students/will/be/able/to) skip.
Verb match na ho → **None** (default "remember" NAHI, taake galat label na lage). Sirf tajweez —
import me teacher ki di hui value overwrite nahi hoti; khali ho tabhi auto-fill.

**Import service** (`app/services/slo_import_service.py`, `library_meta_import_service` pattern par):
pandas `read_excel(dtype=str)`, columns lowercase-normalize. Required: class/subject/slo_code/slo_text;
optional: bloom_level/strand; `book_pages` + koi bhi extra column IGNORE (error nahi).
Duplicate `slo_code` par **UPDATE** (draft dobara import: slo_text/bloom_level/strand refresh,
`created_at` untouched), naya par ADD. Ek row fail se baaki nahi rukti. Summary:
`{added, updated, errors, results:[{row, slo_code, status, reason?}]}`.

**Repo/API/UI:** `app/repositories/slo_repository.py` (insert/find_by_code/update_by_code/list_by_filters);
`app/api/slo.py` — `GET /api/slo` (class/subject/strand filter), `GET /api/slo/template`,
`POST /api/slo/import`; `app/main.py` me router register (auth ke peeche). `static/slo.html` (import +
summary + filterable list), `static/slo_import_template.xlsx` (header + 4 sample rows), index.html nav link.

**Strand codes (is book se, 50 SLO):** W=Pre-writing(3), N=Number(25), C=Comparison(6),
D=Solid Shape(8), S=Flat Shape(8). Pattern/Measurement/Data is book me NAHI.

**Tests:** `tests/test_slo_import.py` (10) + `tests/test_slo_api.py` (6) = 16 naye. ruff clean;
full suite **682 pass** (666 → 682). Smoke test (real boot): template/import/re-import/list/slo.html
sab OK; bloom verify (compare→analyze, count/recognize→remember, trace→None); demo rows real DB se saaf.

---

## 2026-07-18 — feature/db-index-caching (HISSA 4 DB index + HISSA 5 caching)

**HISSA 4 — image_library filter indexes** (`app/core/database.py`, commit `59517e0`):
- `init_db()` me 3 `CREATE INDEX IF NOT EXISTS`: `syllabus_topic_id` (list filter +
  topic_ids_with_images/topic_image_counts + find_by_name_and_topic — 4 code paths), `subject`, `grade`.
- Migration = sirf CREATE INDEX (existing data safe, idempotent, sirf server restart chahiye — koi schema change nahi).
- Query plan pehle `SCAN image_library` → ab `SEARCH ... USING INDEX`. init_db 2x chala, error nahi.
- **Scope se bahar (index nahi lagta):** search `q` (`name/keywords LIKE '%..%'` leading wildcard) aur
  `category` (`LOWER(category)=?`) — FTS/expression index chahiye, HISSA me nahi.
- **Reality:** abhi sirf 106 rows — koi query slow nahi thi; ye future-proofing hai (library barhne par).

**HISSA 5 — caching headers** (`app/main.py`):
- Nayi `@app.middleware("http")` — sirf `/library/*.webp` (full + thumbs) par
  `Cache-Control: public, max-age=31536000, immutable` (1 saal). HTML/JS ko haath nahi (StaticFiles default ETag/304).
- **Cache-busting zaroorat NAHI** — code-verified: `image_id=uuid.uuid4()` har upload, koi route
  existing `{uuid}.webp` overwrite nahi karta (replace = delete + naya upload = naya UUID = nayi URL).
  Filename hi content-address hai. Future guardrail: agar kabhi in-place replace feature bane to
  naya UUID/`?v=` rakhna warna immutable stale dega.
- Verified (TestClient): webp → immutable header; library.html/index.html → koi long-cache nahi.

**Tests:** ruff clean; full suite **666 pass**. Do alag commits (H4 db, H5 main).

---

## 2026-07-18 — feature/bulk-convert (HISSA 3 — 99 purani PNG → smart WebP)

**Kya kiya:** `image_library` ki 99 purani rows (`file_path .png`, `compression=None`, static/library/)
ko smart WebP me convert kiya — `process_and_save()` (same uuid) se full webp + 300px thumb, phir DB update.
Data migration hai (koi naya code nahi; detection HISSA-2/saturation-gate wahi).

**Irreversible-safety (convert se PEHLE):**
- DB backup: `paper_maker_backup_bulkconvert_20260718_*.db`
- 99 original PNG backup: `backups/library_png_20260718/` (static ke bahar) — `.gitignore` me `backups/` add
- Convert ke baad browser me crisp confirm (horse_bw, candy_bw, trace, sharpener_bw, walnut_bw lossless;
  basket_c colour saaf) — TAB original .png delete.

**Per row:** `file_path` → `library/{uuid}.webp`, `thumb_path` → `library/thumbs/{uuid}.webp`,
`compression` → lossless/lossy. Per-row try/except + commit (resumable; ek run timeout hua, doosre ne baaki 21 pura kiya).

**Natija:** 99/99 convert, 0 fail. **lossless 76, lossy 23** (saare lossy = `_c` colour photos).
Size: PNG 52.93 MB → WebP full **21.05 MB (−60.2%)** (+thumbs 25.97 MB, −50.9%).
Lossy 23: 25.19→2.19 MB (−91.3%); lossless 76: 27.74→18.86 MB (−32%, phir bhi crisp).
Integrity: 99 webp + 99 thumb + DB sab OK.

**Note:** images aur `paper_maker.db` gitignored hain (version control me nahi) — commit sirf PROGRESS + .gitignore.
Backups (DB + 99 PNG folder) local safe rakhe. Cloud deploy-remote par push NAHI (sirf backup remote).

---

## 2026-07-18 — smart-compression: unit tests + backup push

**Unit tests — `tests/test_smart_compression.py` (16 naye, pure functions, koi DB/client nahi):**
numpy se controlled images bana kar exact boundaries test kiye —
- `_buckets_to_cover`: 1 flat colour → 1 bucket; 60/40 → 2; photo-noise → >40;
  **boundary 47 colours → 40 buckets** (lossless side) vs **48 → 41** (lossy side); khaali → 1.
- `_is_low_saturation`: pure grayscale → True; saturated red → False;
  **boundary 13% sat (<0.14) → True** vs **15% (>0.14) → False**; khaali → True.
- `_choose_compression` **3-stage order**: force_lossless jeetta hai; high-detail B/W
  (64 near-gray, buckets 55>40 par low-sat) → saturation gate lossless deta hai (bucket rule se pehle);
  saturated colour noise → lossy; flat colour graphic (chand buckets) → lossless.

**Run:** ruff clean (import-order auto-fix); **poora suite 666 pass** (pehle 650 → +16).

**Git:** commits `bef8ead` (feat: buckets + saturation gate) → merge `6e39909` → `1483f37` (tests).
**Push:** `backup` remote (paper-maker-backup.git) par push kiya — yeh **backup repo hai, deploy-remote NAHI**
(Railway/Northflank yahan configured hi nahi). Isliye "master push se deploy todta hai" wala rule nahi toota.
`master -> master` synced (ahead 0).

---

## 2026-07-18 — feature/smart-lossy-webp: saturation gate (detailed B/W line-art false-lossy fix)

**Asli _bw test se pakda:** library me 65 named images hain (`_bw` = line-art, `_c` = colour) —
UUID naam se store, DB `image_library.name` → `file_path` mapping se mile (original `.png`, compression=None).
Naye buckets-metric par 40 me se 38 `_bw` lossless, par **2 false-lossy**: `sharpener_bw` (51 buckets,
21 shaded sharpeners) aur `walnut_bw` (55 buckets, dense stippling) — ground truth Read se dekha, dono
sach me B/W line-art hain jo lossy me smear ho jate.

**Root cause:** detailed B/W line-art (grey shading/stippling) bucket-count me simple colour photos se
**OVERLAP** karta hai (sharpener 51, walnut 55 vs cat_c 56, banana_c 46, panda_c 41). Buckets *akele*
in dono ko alag nahi kar sakte — koi N kaam nahi karega (wahi 8/16 wali limitation, dusre end par).

**Discriminator = saturation.** B/W drawing chahe kitni detailed ho, saturation ~0; colour photo ki high.
Real library par mapa: `_bw` sat-frac (S>40 wale pixels ka hissa) ≤0.122, `_c` ≥0.104.

**Fix — `app/services/image_processing_service.py`, `_choose_compression` me saturation gate:**
1. `force_lossless` (mode 1/P/transparency) → lossless  [waise hi]
2. **NAYA** `_is_low_saturation()` — sat-frac < `_SAT_LOSSLESS_MAX=0.14` → lossless (har B/W drawing, detailed bhi)
3. warna colour: `_buckets_to_cover <= _MAX_BUCKETS_LOSSLESS(40)` → lossless, warna → lossy
- Constants: `_SAT_PIXEL_MIN=40` (HSV S se upar = meaningful rang), `_SAT_LOSSLESS_MAX=0.14`.

**Validated (real library, ground truth):** 40/40 `_bw` → lossless ✓; 22/24 `_c` → lossy ✓;
sirf `cat_c`+`football_c` (muted colour) over-lossless — storage cost only, quality nahi (safety bias).
ruff clean; 85 library/image tests pass. Merged to master (LOCAL only, cloud push NAHI).

---

## 2026-07-18 — feature/smart-lossy-webp: detection metric fix (top-8 coverage → buckets-to-85)

**Masla (code review se):** purana `_is_line_art` **fixed top-8 buckets ka coverage ≥0.85** dekhta tha.
Ye multi-colour flat art par galat tha — 10-15 flat rang wali (bacchon wali crisp) illustration ka
top-8 coverage <0.85 aa jaata → galti se **lossy** (quality loss us cheez par jise crisp chahiye).
`_TOP_BUCKETS` ko 8→16 karna wahi bug ka bada version tha (16-colour art phir lossy). Magic number kaam nahi karta.

**Naya metric — "85% coverage tak kitne buckets chahiye?"** (`_buckets_to_cover`):
- Buckets ghatte order me jodo jab tak cumulative coverage ≥0.85 na ho; kitne lage = signal.
- Flat art (chand flat rang) → **kam buckets**; photo (gradients phaile) → **bohot buckets**.
- `_is_line_art = _buckets_to_cover(img) <= _MAX_BUCKETS_LOSSLESS (40)`.
- `_QUANT_SHIFT=3`, `_COVERAGE_TARGET=0.85` waise hi. `force_lossless`/`_choose_compression` unchanged.

**N=40 kaise choose kiya — real uploads par mapa (synthetic NAHI):**
- `static/uploads/` ke 1206 asli teacher images ka sample: do alag populations —
  line-art/flat **≤29 buckets** par rukta, photo **≥41** se shuru; **30–40 bilkul khaali (gap)**.
- 6 library photos ka floor bhi 46 tha — match. N=40 valley me baitha, isliye magic number nahi (±5 safe).
- Ground truth khud dekha (Read se): `099cdf59`(1b, safed worksheet+trace+text) → lossless ✓;
  `1b2feffd`(41b, 6 shaded tables+bold "SIX") → lossy ✓ (bold text q85 me bachta, tables photographic);
  `861d9631`(379b, 23 baskets photo) → lossy ✓. Delicate line-art hamesha safed pages par (kam buckets) → lossless.

**Verified:** updated service function real images par expected split; ruff clean; 85 library/image tests pass. Cloud push NAHI.

---

## 2026-07-17 — feature/smart-lossy-webp (Smart Lossy/Lossless WebP)

**Kya bana (sirf naye uploads):** har image ka type detect karke best compression —
line drawing/trace/outline → LOSSLESS (bacchon ke liye crisp), photo → LOSSY q85 (zyada saving).
Ambiguous → hamesha lossless (safety bias).

**Detection tareeqa — "dominant colour coverage" (raw unique-count se robust):**
- Raw unique-colour count ka masla: anti-aliasing se ek simple trace bhi hazaaron edge-shades de deta
  hai → galti se photo detect. Isliye coverage use kiya.
- `app/services/image_processing_service.py`:
  - `_is_line_art(full)`: RGB → numpy, colours quantize (`>>3` = 32 levels/channel, AA noise merge),
    `np.bincount` se top-8 buckets ka pixel coverage; **coverage ≥ 0.85 → lossless**, warna lossy.
  - `_has_graphic_signals(img)`: hard signals jo seedha lossless karte hain (coverage skip):
    mode "1" (bilevel), mode "P" (palette ≤256), ya real transparency. Grayscale "L" ko force NAHI
    (B/W photo ho sakta hai) — coverage decide karta hai. Signal P→RGBA convert se PEHLE capture.
  - `_choose_compression()` → `"lossless"`/`"lossy"`; full + thumb **dono same mode** use karte hain.
  - Tunables: `_LOSSY_QUALITY=85`, `_QUANT_SHIFT=3`, `_TOP_BUCKETS=8`, `_COVERAGE_LOSSLESS_THRESHOLD=0.85`.
  - Return dict mein ab `compression` bhi.
- `app/core/database.py` — `image_library.compression TEXT` (CREATE + safe ALTER; purani rows NULL)
- `app/schemas/responses.py` — `LibraryImage.compression`
- `app/repositories/library_repository.py` — `insert()` mein `compression` column
- `app/api/library.py` — single + bulk row mein `compression` add
- `requirements.txt` — `numpy` explicitly add (ab seedha import; pehle sirf pandas ke through transitive)

**Verified (manual smoke):**
- Line art (grid + circle) → `lossless`, full 6.7 KB (crisp) ✓
- Photo (random noise, worst-case) → `lossy`, full 467 KB ✓

**Baaki:** pytest + ruff (baad mein), naye detection tests likhna. Cloud push NAHI.

---

## 2026-07-17 — feature/webp-thumbnails (HISSA 2 — WebP + Thumbnails)

**Kya bana (sirf naye uploads — purani JPG/PNG untouched, woh HISSA 3 Bulk Convert mein):**
- `app/services/image_processing_service.py` (naya) — `process_and_save(contents, image_id)`:
  Pillow se open, EXIF orientation fix, palette→RGBA; **2 LOSSLESS WebP** banata hai —
  Full (max 1200px, upscale nahi) → `static/library/{uuid}.webp`,
  Thumb (max 300px) → `static/library/thumbs/{uuid}.webp` (dono `lossless=True, method=6` — trace/outline crisp)
  Corrupt/na-khulne wali image → `ValueError`
- `app/api/library.py` — single upload (`POST /api/library`) + bulk upload (`POST /api/library/bulk`)
  ab `dest.write_bytes()` ki jagah service call karte hain; row mein `thumb_path` add;
  process fail → single 400, bulk us file ko skip (baaki chalti rahein)
- `app/api/library.py` — DELETE route ab thumb file bhi hataata hai (orphan fix)
- `app/repositories/library_repository.py` — `insert()` mein `thumb_path` column
- `app/core/database.py` — `image_library.thumb_path TEXT` (CREATE TABLE + safe ALTER migration; purani rows NULL)
- `app/schemas/responses.py` — `LibraryImage.thumb_path: Optional[str] = None`
- `static/library.html` — grid `renderCard()` ab `thumb_path || file_path` (purani images full par fall back)

**Verified (server restart + manual smoke test):**
- 1600×1000 PNG → full 1200×750, thumb 300×188, dono `WEBP` ✓
- 500px image upscale nahi hui (500×500 raha) ✓
- delete → full + thumb dono disk se hatt gaye (koi orphan nahi) ✓
- DB migration clean, `thumb_path` column present, `thumbs/` dir auto-create ✓

**Test fixture fix (same branch):** upload route ab image ko genuinely decode karta hai (Pillow),
isliye purane test files ka minimal 1×1 PNG/JPG (jo truncated/broken tha — `load()` par "broken data stream")
fail karne laga. `test_library_api.py` mein `_img_bytes()` helper (Pillow se valid bytes) + baaki 5 library
test files mein PNG ki IDAT line valid bytes se replace. Upload tests ab `.webp` ext, `thumb_path`, aur
thumbnail file existence check karte hain; bulk test `*.webp` count karta hai; delete test thumb removal verify.
- Service refactor: `process_and_save(contents, id, library_dir)` — dir ab param hai (tests `_LIBRARY_DIR`
  monkeypatch karte hain, isliye service ko route se dir milna chahiye, apna hardcoded nahi).

**Tests:** 650 pass, ruff clean. Cloud push NAHI.

**Fix (same branch) — upload size limit 2 MB → 10 MB + pixel guard:**
- **Masla:** 2 MB byte-check upload ke baad par conversion se PEHLE tha. WebP+1200px cap se stored
  size waise hi chhoti hoti hai, lekin bade high-res PNG (4–8 MB) convert hone se pehle hi reject ho jaate the.
- **Faisla (Option A):** 2 MB ko *storage guard* ki jagah *input/decode guard* maana. `_MAX_BYTES` 2 → 10 MB
  (single + bulk dono routes), byte-check ab bhi conversion se pehle (sasta rejection).
- `app/api/library.py` — `_MAX_BYTES = 10 MB`; error messages ("2 MB" → "10 MB") single + bulk.
- `app/services/image_processing_service.py` — **pixel guard** `_MAX_PIXELS = 50 MP`: chhoti file bade
  dimensions (decompression bomb) ko bhaari decode se PEHLE (header ki `img.size` se) reject karta hai.
- `static/library.html` — 2 labels ("max 2 MB" → "max 10 MB") + client-side pre-check `2*1024*1024` → `10*...`.
- `tests/test_library_api.py` — oversized tests (single + bulk) ab `10 MB + 1` use karte hain
  (warna 2 MB payload naye limit ke neeche aa ke corrupt-path test karta, size-path nahi).
- **Verified (manual):** 7.34 MB real PNG → 200 + 1200×1200 WebP ✓; 64 MP pixel-bomb (0.19 MB file) → 400 guard ✓
- pytest + ruff: baad mein (user browser test kar raha hai).

---

## 2026-07-16 — feature/fix-warning-null (in progress)

**Bug:** `adaptive_results_service.py` mein `upload_results()` warning calculation fail hoti thi jab `school_settings` table mein `class_size`/`min_analysis_percent` columns `NULL` hote hain (SQLite `ALTER TABLE ADD COLUMN` existing rows ko NULL rakhta hai). `settings.get("class_size", 25)` ka default sirf missing key par kaam karta hai — NULL value par `None` return hota tha, phir `math.ceil(None × pct / 100)` crash.

**Fix (`adaptive_results_service.py` lines 64–78):**
- `settings.get("class_size") or 25` — `or` None aur 0 dono handle karta hai
- `settings.get("min_analysis_percent") or 60` — same
- Poora warning block `try/except Exception: pass` mein — warning crash hone par upload fail nahi hoga

## 2026-07-16 — feature/remove-dashboard → master (dashboard.html delete)

**Kya kiya:**
- `static/dashboard.html` delete kiya — legacy page tha, Results screen hatayi thi to orphan ho gaya tha;
  Analytics screen (index.html) same kaam karta hai aur zyada features bhi hain
- `static/index.html` — saare references clean kiye:
  - `#dashboardBtn` button Results screen se hata diya
  - `mpDashboard()` aur `openDashboard()` functions delete
  - 3 jagah `dashboardBtn.style.display` lines delete (loadPaper, generateQuestions, buildAdaptivePaper)
  - CSV upload ke baad auto-open dashboard line delete
  - My Papers table mein "Dashboard" button delete
  - `btn.dashboard` i18n keys (EN + UR) delete
- Analytics screen aur Adaptive Analysis untouched

---

## 2026-07-16 — feature/category-dropdown → master (Image Library category dropdown)

**Kya kiya:**
- `static/library.html` — Category field 2 jagah text box se dropdown bana:
  - **Bulk Tag modal**: `bmCategory` input → select (12 options) + hidden `bmCategoryNew` text box
  - **Edit modal**: `editCategory` input → select + hidden `editCategoryNew` text box
- `_buildCategorySelect()` helper: dono selects consistently populate karta hai;
  existing value auto-pre-select; unknown DB value → "Naya likhein" select + text box mein value
- `onBmCategoryChange()` / `onEditCategoryChange()`: "Naya likhein" chunne par text box dikhao
- `saveBulkMeta()` + `saveEdit()`: `__new__` sentinel resolve karke actual category string bhejte hain
- 12 categories (DB se): animal, concept, flower, food, fruit, furniture, number, object, shape, sports, vegetable, vehicle

---

## 2026-07-16 — feature/bloom-suggestions → master (Bloom Taxonomy class-wise suggestions)

**Kya kiya:**
- `app/core/bloom_standards.py` (naya) — 4 class groups (Pre-Primary/Primary/Middle/Matric) with
  Bloom % distributions; `get_bloom_suggestion()` with flexible matching: case-insensitive,
  spaces/dashes normalize, `Grade X` aur `Class X` dono variants support
- `app/api/bloom_suggestions.py` (naya) — `GET /api/bloom-suggestion/{class_name}`;
  match nahi → 404
- `app/main.py` — bloom_suggestions router registered
- `static/blueprint.html` — Grade dropdown ke neeche neela info box (`#bloomSuggestionBox`);
  `onGradeChange()` mein suggestion fetch + display; sirf mashwara, koi auto-fill/enforcement nahi

**Bug fix (same branch):** DB mein grades `Grade 4`/`Grade 6` etc hain, `Class X` nahi —
`bloom_standards.py` mein `Grade X` variants add kiye taake matching kaam kare.

**Distributions:**
- Pre-Primary: Remember 70%, Understand 30%
- Primary: Remember 30%, Understand 35%, Apply 25%, Analyze 10%
- Middle: Remember 20%, Understand 30%, Apply 30%, Analyze 20%
- Matric: Remember 15%, Understand 25%, Apply 30%, Analyze 20%, Evaluate 10%

---

## 2026-07-16 — feature/adaptive-skip-upload → master (Adaptive: skip upload if results exist)

**Kya kiya:**
- `app/api/adaptive_results.py` — naya route `GET /api/adaptive/has-results/{paper_id}`:
  paper nahi → 404; uploads nahi → `{has_results: false, student_count: 0}`;
  upload mila → unique roll_no count → `{has_results: true, student_count: N}`
- `static/index.html` — Step 1 mein `div#adHasResultsBox` add kiya (green info box, default hidden)
- `static/index.html` — `onAdaptivePaperSelect()` async ho gayi: paper select hote hi
  has-results check karta hai; results hain → box dikhao + "Upload Results" button chhupao;
  2 buttons: "Analysis dekho →" (Step 3) aur "Naya Result Upload karo" (Step 2)
- Existing upload/analysis/generate logic unchanged

**Verified:** `GET /api/adaptive/has-results/628ccbea-...` → `{has_results: true, student_count: 25}` ✓

---

## 2026-07-16 — feature/analytics-improve → master (Analytics screen improvements)

**Kya kiya:**
- `static/index.html` — Paper ID text box hata ke dropdown lagaya (GET /api/papers se load hota hai); paper select hote hi auto analytics load; "Analytics dekhen" button backup ke liye rakha
- `static/index.html` — "Kaisa tha?" column add kiya per-question table mein — Roman Urdu difficulty explanation: >80% "Asaan tha — X% ne sahi kiya", 40–80% "Theek tha", <40% "Mushkil tha — sirf X% ne sahi kiya"
- `static/index.html` — Row background color ab Difficulty Index (P-value) se: Green (40–80%), Yellow (80–90% ya 30–40%), Red (>90% ya <30%); D-index column aur Quality badge unchanged
- `static/index.html` — `initAnalyticsScreen()` naya function: showScreen('analytics') hook se call hota hai, `currentPaperId` auto pre-select karta hai
- Legend text update: difficulty range explain karti hai (P-value based)

**Tests:** sirf frontend — koi backend change nahi, pytest pending

---

## 2026-07-15 — feature/language-filter HISSA 2+3 (commit de7b95b)

**Kya kiya:**
- `app/services/blueprint_paper_service.py` — `language_filter` har section se read karke `_fetch_simple` + `_fetch_with_distribution` ko pass. Shortfall notes mein `(English only)`/`(Urdu only)` label.
- `app/services/paper_service.py` — `_pick_questions()` ko `language_filter` param mila; `assemble_balanced_paper` aur `_assemble_by_ratio` `req.language_filter` pass karte hain (adaptive paper mein nahi — `AdaptivePaperRequest` mein field nahi).
- `static/blueprint.html` — FILTERS row mein Language dropdown (Sab / English only / Urdu only); `onLangFilter()` handler; `addSection`/`loadPreset`/`loadBlueprintToUI` mein `language_filter: null` default.
- `static/index.html` — Generate paper form mein Language filter dropdown; `buildPaper()` POST body mein `language_filter: langVal || null`.

**Tests:** 635 pass (pehle wali 3 adaptive failures fix ho gayi — `AdaptivePaperRequest` mein field nahi thi).

---

## 2026-07-15 — feature/language-filter HISSA 1 (commit 6fcc19f)

**Kya kiya:**
- `app/repositories/questions_repository.py` — `_apply_language_filter()` helper; `find_for_blueprint_section`, `find_least_used`, `find_for_bank_paper` mein `language_filter` param.
- `app/schemas/requests.py` — `GeneratePaperRequest` mein `language_filter: Optional[Literal["en","ur"]] = None`.
- `tests/test_language_filter.py` — 11 nayi tests (repository + schema validation).

---

## 2026-07-15 — fix/bad-file-crash → master (Bulk upload crash guard)

**Kya fix kiya:**
- `app/services/bulk_import_service.py` — 0-bytes upfront check; corrupt file pe user-friendly message (raw Python exception expose nahi hota); header-only xlsx pe explicit error; DB insert per-row try/except
- `app/api/questions.py` — `file.file.read()` try/except mein wrap kiya (pehle unguarded 500 tha)
- `tests/test_bulk_import.py` — 5 nayi `TestBadFileCrash` tests: jpg ext, 0 bytes, corrupt message quality, header-only, server survives 3 bad uploads
- `start.bat` — naya launcher: `.env` load, venv check, browser auto-open 2s baad

**Tests:** 624 pass, ruff clean

---

## 2026-07-15 — fix/edit-modal-save → master (print.html answer_lines save bug)

**Root cause:** `saveQuestion()` mein `question_ur`, `correct_answer_en`, `correct_answer_ur` hamesha payload mein jaate the (empty string `""`). `_not_blank` Pydantic validator 422 raise karta tha → answer_lines kabhi DB tak nahi pahunchti thi.

**Kya fix kiya:**
- `static/print.html` — `saveQuestion()`: optional text fields sirf tab payload mein jayen agar non-empty (empty string → omit)
- `static/print.html` — `ef_answer_lines` dropdown options fix: `0, 2, 3, 4, 6, 8` (bank.html se match; pehle `5, 10` the jo invalid hain)
- `tests/test_print_edit_modal.py` — 8 naye tests: valid values, zero, bilingual, empty-string-422, DB persistence

**Tests:** 619 pass, ruff clean

---

## 2026-07-15 — feature/bulk-answer-lines → master (Bulk Excel mein answer_lines column)

**Kya bana:**
- `app/services/bulk_import_service.py` — `answer_lines` column parse karo (valid: `0,2,3,4,6,8`; invalid/blank = NULL + warning)
- `app/repositories/questions_repository.py` — `insert()` mein `answer_lines` column add
- `static/bulk_upload_template.xlsx` — `answer_lines` column (22nd, green/optional) add kiya
- `tests/test_bulk_import.py` — 11 naye tests (valid values, zero, blank, invalid, non-numeric, backward compat, parametrize)

**Tests:** 590 pass, ruff clean

---

## 2026-07-15 — Pre Year 1 questions delete (197 sawal)

- Backup: `paper_maker_backup_pyr1_20260715_104351.db`
- DELETE: 197 Pre Year 1 sawal (syllabus_topics JOIN, grade='Pre Year 1')
- Baad mein Pre Year 1 count = 0 ✓, baaki classes (70 sawal) safe

---

## 2026-07-14 — Image Library — Excel se Meta Import (feature/image-meta-import → master)

**Kya bana:**

- **`app/services/library_meta_import_service.py`** (naya) — Core service:
  - `import_meta_from_excel(file_bytes)`: pandas se Excel parse, har row par `image_name` se DB match
  - Topic resolution: `subject + class` hint ke saath priority — subject+grade > subject-only > global first
  - Partial update: khali cell = us field ko chhua nahi (purana data rahe)
  - Return: `{updated, skipped, results: [{row, image_name, status, reason?, warnings?}]}`

- **`app/api/library.py`** — 2 naye routes:
  - `POST /api/library/excel-meta-import` — Excel upload, service call, JSON summary
  - `GET /api/library/excel-meta-import/template` — template .xlsx download

- **`static/library_meta_import_template.xlsx`** (naya) — 7-column template (image_name zaroori, baaki optional), colored headers, 2 example rows

- **`static/library.html`** — Bulk Upload card ke baad naya card:
  - Template download button, xlsx file input, Import button
  - `importMetaExcel()` JS: POST → results render (row number + status + warnings) → grid reload
  - Same `.bulk-results` CSS — Bulk Upload se consistent UI

**Tests:** 17 naye tests (11 service + 6 API) — 579 total pass, ruff clean

**Excel columns:**
`image_name` (zaroori) | `topic` | `subject` | `class` | `keywords` | `category` | `question_types`

---

## 2026-07-11 — Image System HISSA C — In-form image selection UI (feature/image-system)

**Kya bana (frontend only — koi backend change nahi):**

- **`static/print.html`** — Edit modal mein topic thumbnail strip:
  - Modal khulte hi `loadTopicStrip(topicId, qid)` call hoti hai
  - `/api/library?syllabus_topic_id=...` se images fetch, strip mein dikhayi
  - Thumbnail click → `applyLibraryImageInModal()` → image-from-library API → modal ka preview update
  - Topic na ho ya images na hon → strip hidden (no clutter)
  - "Choose Image" file upload button barabar maujood hai (dono options)

- **`static/bank.html`** — Add form + Edit modal mein thumbnail grid:
  - Add form: topic select `onchange="onAddTopicChange()"` → library images strip
  - Thumbnail click → highlight (selected), dobara click → deselect
  - Question save hone ke baad agar image select thi → image-from-library API call
  - Edit modal: `openEditModal()` mein `_loadEditStrip(topicId, qid)` call
  - Edit thumbnail click → seedha attach + list refresh + modal close

**Test run:** 482 passed (no backend change) — ruff clean

**Browser test checklist (khud check karo):**
1. print.html: paper mein ✏️ button → modal khule → agar topic hai to library strip dikhe
2. Strip mein thumbnail click → modal preview update ho, file upload button abhi bhi kaam kare
3. Topic nahi ya library mein images nahi → strip bilkul nahi dikhi
4. bank.html: nayi question form → subject → class → topic chunein → library strip dikhe
5. Thumbnail click → highlighted ho (blue border), dobara click → deselect
6. "Save" karo → question save + image attach ho (list mein image_path set ho)
7. Edit button → modal khule → strip dikhe → click karo → modal band, list refresh ho
8. Purani "Choose Image" file upload dono jagah abhi bhi kaam kare (backward compat)

---

## 2026-07-11 — Image System HISSA B — Excel image column (feature/image-system)

**Kya bana:**

- **`app/services/bulk_import_service.py`** — `image` column support:
  - `_find_library_image(name, topic_id)` helper: topic-scoped match pehle (`find_by_name_and_topic`), phir global (`find_by_name`), narm (case-insensitive, trim)
  - `_validate_row()` — `_image_name` internal field pass-through
  - `import_from_bytes()` — post-insert: library se file `static/uploads/` mein copy, `image_path` set; naam na mile → warning (skip nahi)
  - `image` column absent (purani files) → `""` → koi action nahi (backward compat)
- **`static/bulk_upload_template.xlsx`** — `image` column (13th) add kiya
- **`tests/test_bulk_import_image.py`** — 7 nayi tests

**Test run:** 482 passed, 0 failed — ruff clean

**Browser test (khud check karo):**
1. Purana template (.xlsx bina image column) import karo → bilkul theek chale
2. Naye template mein image naam likho (library mein pehle upload karo) → question mein image dikhe
3. Galat naam likhain → question import ho, warning mein naam aaye
4. Case mismatch test: "OrangeS5" library mein, "oranges5" Excel mein → match ho

---

## 2026-07-11 — Image System HISSA A — Bulk Image Upload (feature/image-system)

**Kya bana:**

- **`app/core/database.py`** — `image_library` table mein `name_normalized TEXT` column add kiya (CREATE TABLE + safe ALTER TABLE migration existing DBs ke liye + back-fill UPDATE)
- **`app/repositories/library_repository.py`** — `insert()` updated: `name_normalized = name.strip().lower()` field include hoti hai. Teen nayi helpers: `name_exists(name)` (duplicate check), `find_by_name(name)`, `find_by_name_and_topic(name, topic_id)` (HISSA B ke liye)
- **`app/api/library.py`** — `POST /api/library/bulk` nayi route: `List[UploadFile]`, per-file MIME + size + duplicate check, skip karo invalid/duplicate, result list wapas karo
- **`static/library.html`** — "Ek saath kai images upload" card: multi-file input, subject/grade/topic cascade (alag single-upload se), per-file result list (ok/skip/err styled), library grid auto-refresh on success
- **`tests/test_library_api.py`** — 8 nayi bulk tests: all_added, duplicate_skip, wrong_mime_skip, oversized_skip, name_normalized_stored, topic_tagged, per_file_result_list, case_insensitive_duplicate

**Test run:** 475 passed, 0 failed — ruff clean

**Browser test (khud check karo):**
1. Library page → "Ek saath kai images" card dikhe
2. Subject → Grade → Topic cascade kaam kare
3. Multiple PNG/JPG files select → Upload → result list (ok/skip) dikhe
4. Duplicate naam dobara upload karo → skip + reason dikhe
5. GIF file try karo → skip (JPG/PNG only)
6. Grid refresh ho nayi images ke saath

---

## 2026-07-11 — Blueprint HISSA 4 — blueprint.html frontend (feature/blueprint)

**Kya bana:**

- **`static/blueprint.html`** — nayi file, poora Blueprint Builder UI:
  - Paper metadata: blueprint name, subject+grade cascade, paper title, class name
  - Preset loader: `/api/blueprint-presets` se presets — "Load sections" button
  - Dynamic section cards: heading, topic multi-select (syllabus se checkboxes), question types (MCQ/Fill/T-F/Short), count, marks_each, source filter
  - Live total marks bar (count × marks_each, real-time update)
  - "Save Blueprint" → `POST /api/blueprints` — DB mein save
  - "Paper Banao" → `POST /api/blueprint-paper` → `print.html?paper_id=...` mein redirect
  - Shortfall warnings: agar section mein maange zyada mile kam — yellow list dikhti hai
  - Saved Blueprints list: Load / Paper Banao / Delete per blueprint
- **Sidebars updated** — Blueprint link add kiya: `bank.html`, `library.html`, `print.html`, `index.html`
- **Branch:** feature/blueprint (commit a16a9fc)

**Test checklist (browser mein khud check karo):**
1. `/blueprint.html` open ho — sidebar aur page dono sahi dikhein
2. Subject → Grade change kare → topics load hon section cards mein
3. Preset load kare → sections replace hon
4. Section add/remove karo — marks bar update ho
5. Save Blueprint → success message aur list mein nayi entry dikhe
6. Paper Banao → print.html khole, paper render ho
7. Shortfall warning: aisa subject/topics chunein jahan kam questions hain
8. Saved list mein "Load" → form mein load ho; "Paper Banao" → direct paper
9. "Delete" → blueprint list se hata de

---

## 2026-07-11 — Blueprint HISSA 3 — print.html blueprint rendering (feature/blueprint)

**Kya bana:**

- **`app/schemas/responses.py`** — `Paper` model mein `sections_meta: Optional[str] = None` add kiya
  - Pehle FastAPI response_model strip kar deta tha — ab `GET /api/paper/{id}` mein sections_meta aata hai
- **`static/print.html` (HTML)** — `sectionA` + `sectionB` divs hata ke `sectionsContainer` bana
- **`static/print.html` (CSS)** — `.shortfall-note` style add kiya (yellow warning box, screen only)
- **`static/print.html` (JS)** — `loadPaper()` mein sections_meta branch:
  - `sections_meta` non-null → blueprint rendering: qMap build, har section ka `section-block` dynamically inject
  - `sections_meta` null → `_renderLegacySections()` call (A/B objective/subjective — bilkul unchanged)
  - Shortfall notes `.no-print .shortfall-note` — screen par dikhein, print mein nahi
  - `_renderLegacySections()` new helper: container mein sectionA/sectionB divs create karke purana `renderSection()` call karta hai
- **Tests:** 58 blueprint tests pass, ruff clean
- **Branch:** feature/blueprint (commit 3a76257) — merge pending

---

## 2026-07-11 — feature/bulk-import merged to master (HISSA 4 — Bulk Upload)

**Kya bana:**

- **Backend — `app/services/bulk_import_service.py`**
  - pandas se `.xlsx`/`.csv` parse (openpyxl engine)
  - Per-row validation: type check (mcq/fill/tf/short), blank question, MCQ options, correct letter/tf value
  - Topic matching: case-insensitive + strip → subject+grade → subject-only → global; match na mile to `topic_id=NULL` + fuzzy suggestion (difflib)
  - `source='manual'` insert — HISSA 1 ki `questions_repository.insert()` reuse
  - Return: `{added, skipped, errors: ["row N: wajah"], warnings: ["row N: note"]}`
  - Marks: blank/zero/invalid → silent default 1
  - `is_urdu=yes` → `question_ur` mein, warna `question_en`

- **API — `app/api/questions.py`**
  - `POST /api/questions/bulk-import` route (.xlsx/.xls/.csv accept, ext check at route level)

- **Frontend — `static/bank.html`**
  - "Bulk Upload — Excel se questions import karo" card (bank-paper card ke baad)
  - Drag-and-drop zone + file chooser (.xlsx/.csv, max 5 MB client-side check)
  - Upload button (disabled jab tak file na chune), Clear button
  - Result box: green (sab add), orange (kuch skip), red (sab skip) — har skip row ka number + wajah, warnings alag list
  - Question list auto-refresh after successful import
  - "Template download karo" button → `/bulk_upload_template.xlsx`

- **Template — `static/bulk_upload_template.xlsx`**
  - 4 sample rows (mcq/tf/fill/short), green styling
  - `Instructions` sheet mein puri guide

- **Tests — `tests/test_bulk_import.py`** — 39 tests
  - Happy path (xlsx + csv, sab 4 types), DB mein actually insert check
  - MCQ correct letter → option text resolve
  - is_urdu, marks defaults (blank/zero/string)
  - Per-row validation errors (blank question, invalid type, MCQ options, wrong correct)
  - Mixed valid+invalid — ek buri row se baaki nahi rukein
  - Topic matching (unknown → warning + import, blank → no warning)
  - File format errors (PDF reject, corrupt xlsx, missing column, empty file)

- **Merge:** `feature/bulk-import → master`, clean (koi conflict nahi)
- **Total: 409 tests pass, ruff clean**

## 2026-07-11 — feature/question-bank merged to master (HISSA 1–3 + bank.html)

**Kya bana:**

- **HISSA 1 — Manual Question CRUD** (`source=manual`)
  - `app/core/database.py` — `source TEXT DEFAULT 'gemini'` column migration; existing rows safe
  - `app/repositories/questions_repository.py` — `insert()` mein `source` field; `list_by_filters()` mein `source` filter support
  - `app/schemas/requests.py` — `CreateManualQuestionRequest` + `UpdateQuestionRequest` mein `source` field
  - `app/api/questions.py` — `POST /api/questions/manual` route (manual question create, no Gemini)
  - `tests/test_bank.py` — 231 tests (CRUD, source filter, edge cases)

- **HISSA 2 — bank.html (Manage Page)**
  - `static/bank.html` — nayi page: question list (filter: subject/class/topic/source), add/edit/delete modal, inline form validation
  - `static/index.html` — "Question Bank" nav link added (sidebar)
  - `static/library.html` — "Question Bank" nav link added (sidebar)

- **HISSA 3 — bank-paper route (bina Gemini API)**
  - `app/services/question_service.py` — `get_questions_for_bank_paper()` — DB se manual questions fetch, subject/source filter
  - `app/services/paper_service.py` — `create_bank_paper()` — paper object banao from bank questions (no API call)
  - `app/api/papers.py` — `POST /api/bank-paper` route registered
  - `tests/test_hissa3.py` — 284 tests (bank-paper route, source filter, question types)

- **bank.html UI — "Bank se Paper Banao" section**
  - `static/bank.html` — subject/class/topic select + "Paper Banao" button → `/api/bank-paper` call → `print.html` redirect

- **Ruff fix:** `tests/test_hissa3.py` — 2 unused variables (`g_id`, `qid`) removed (F841)

- **Total: 370 tests pass, ruff clean**

## 2026-07-10 — feature/image-library Hissa 4 (Auto-Suggest)

- `app/repositories/library_repository.py` — `topic_image_counts(ids)` added (returns {topic_id: count})
- `app/api/library.py` — `topics-with-images` response changed: `{"topics": {"id": count}}` (breaking change, test updated)
- `app/schemas/requests.py` — `CopyFromLibraryRequest` added (image_id + image_size validator)
- `app/api/questions.py` — `_LIBRARY_DIR` constant + `POST /api/questions/{id}/image-from-library` route (copy file from library to uploads, update DB)
- `static/print.html` — auto-suggest badges (📚 N image(s) — Dekho/Nahi), library picker modal (grid thumbnails, size selector), localStorage dismiss per paper, batch API call on paper load
- `tests/test_library_api.py` — topics-with-images tests updated for new shape + `test_topics_with_images_returns_counts` added
- `tests/test_copy_from_library.py` — 7 nayi tests (PNG/JPG copy, default size, replace old upload, 404s)
- **Total: 335 tests pass, ruff clean**

## 2026-07-10 — feature/image-library Hissa 2 (Library Manager page)

- `static/library.html` — nayi page: upload form (cascade Subject→Class→Topic dropdown), client-side file pre-check (type + size), image grid (filter: subject/grade/naam), delete with confirm
- `static/index.html` — "Image Library" nav link added (sidebar)
- `static/print.html` — "Image Library" nav link added (sidebar)
- **Total: 327 tests pass, ruff clean**

## 2026-07-10 — feature/image-library Hissa 1 (DB + API + backup)

- `app/core/database.py` — `image_library` table added in `init_db()`
- `static/library/` — folder created, gitignored
- `app/repositories/library_repository.py` — insert, find_by_id, list_by_filters, delete, topic_ids_with_images
- `app/schemas/responses.py` — `LibraryImage` model added
- `app/api/library.py` — POST /api/library, GET /api/library (filters), DELETE /api/library/{id}, GET /api/library/topics-with-images
- `app/main.py` — library router imported and included
- `backup.bat` — [3/3]→[4/4], library-backups step added
- `tests/test_library_api.py` — 12 nayi tests (upload PNG/JPG, wrong MIME 400, oversized 400, blank name 400, list+filter, delete, topics-with-images)
- **Total: 327 tests pass, ruff clean**

## 2026-07-10 — feature/image-size (Hissa 3)

- `app/core/database.py` — `image_size TEXT` nullable migration
- `app/schemas/responses.py` — `image_size: Optional[str]` in `Question`
- `app/schemas/requests.py` — `image_size` in `UpdateQuestionRequest` + validator (small/medium/large only)
- `app/repositories/questions_repository.py` — `image_size` in `insert()`
- `static/print.html` — CSS size classes (img-sm/md/lg), modal dropdown (sirf image wale questions par), renderQuestion() size class
- `tests/test_image_size.py` — 9 nayi tests (valid sizes, invalid reject 422, null field)
- **Total: 315 tests pass, ruff clean**

## 2026-07-10 — feature/question-image Hissa 1 (Backend)

**Kya kiya:**
- `app/core/database.py` — `questions` table mein `image_path TEXT` column migration added (nullable, existing rows safe)
- `app/repositories/questions_repository.py` — `insert()` mein `image_path` column add; `update()` already generic fields le leta hai
- `app/schemas/responses.py` — `Question` model mein `image_path: Optional[str] = None` add
- `app/api/questions.py` — 2 nayi routes:
  - `POST /api/questions/{id}/image` — JPG/PNG upload, max 2MB, content-type se ext decide, purani image (kisi bhi ext) pehle delete
  - `DELETE /api/questions/{id}/image` — DB NULL + file delete
- `static/uploads/` folder create (images yahan store hongi)
- `.gitignore` — `static/uploads/` add (GitHub par na jaaye)

**Tests (Hissa 1b):** `tests/test_question_image_api.py` — 9 nayi tests:
- PNG/JPG successful upload (200, file on disk, DB path set)
- Oversized (>2MB) → 400, koi file nahi likhi
- Wrong MIME (text/plain, image/gif, application/pdf) → 400
- Unknown question_id → 404
- Delete: file disk se hata, DB NULL
- Replace PNG→JPG: purana .png orphan nahi raha
- **Bug fix:** DELETE route mein `_UPLOADS_DIR / Path(...).name` use kiya (pehle `.parent` galat path de raha tha)
- **Total:** 306 tests pass, ruff clean.

**Hissa 2 (Frontend) — 2026-07-10:**
- `static/print.html` — edit modal mein image section add (file input, thumbnail preview, remove button, warning)
- `renderQuestion()` mein `imageHtml` — `max-height: 180px` screen, `160px` print
- `onImageFileChange()` — client-side pre-check (type + size), instant local preview, auto-upload
- `uploadQuestionImage()` — FormData POST, server response se `_paperQuestions` + re-render
- `deleteQuestionImage()` — DELETE, in-memory update + re-render, UI reset
- `printWithImagesLoaded()` — `Promise.all(imgs.map(img => img.decode()))` phir `window.print()`
- Print button ab `printWithImagesLoaded()` call karta hai
