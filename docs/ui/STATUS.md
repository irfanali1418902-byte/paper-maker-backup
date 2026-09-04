# UI-ARCH — Status Board

> **Fresh session: read THIS file first. Do not read PROGRESS.md (2000+ lines).**
> Full plan: `docs/ui/PLAN.md` · Rules: `CLAUDE.md` §11–12 · Parking lot: `docs/ui/DEFERRED.md`

---

## 📅 PLAN — **2026-09-04 ke liye**, is tarteeb mein

> *(Likha 2026-09-04, us din subah poora audit chalane ke BAAD. Heading mein tareekh
> hai, "kal" nahi — is repo mein har relative label basi ho kar jhoot ban chuka hai:
> `HANDOFF.md` ka banner nau din, P0 rows mahinon. Agla session pehle ye tareekh dekhe:
> agar aaj 09-04 nahi hai to **is plan ke adad dobara naapo**, ROADMAP §E ka qaida.)*
>
> ### ⚠ SAB SE PEHLE: BRANCH BADAL CHUKI HAI
> **Epic `master` mein merge ho chuka (`dc9436a`, 2026-09-03) aur kaam ab `master` par
> hota hai, `feat/ui-architecture` par NAHI.** Is file ki bahut si zaban abhi bhi epic-
> branch ke waqt ki hai — jahan "is branch par nahi" jaisa jumla mile, wo ab tareekhi hai.
> `master` `backup/master` se **226 aage aur un-pushed** hai; push Irfan GitHub Desktop
> se khud karta hai.
>
> ### 2026-09-04 ki seeding — ✅ PRE YEAR 2 MUKAMMAL, aur DO ANDESHE GHALAT NIKLE
> **18/18 topics, 72 sawal, koi FAIL nahi, quota bilkul nahi lagi** (09-02 aur 09-03 dono
> dafa lagi thi). Bank **1126 → 1198**. **PY2 ab 87/87 — PY3 ke saath mukammal.**
> **Baqi sirf PY1 ke 10 topics.** `integrity_check` ok, har topic par poore 4 sawal.
>
> **1. Dohraav ka andesha ghalat nikla — aur ye khaas tor par naapa gaya tha.** Board ne
> tanbeeh ki thi ke baqi 18 topics mein sirf 10 alag titles hain aur *"Practice of
> subtraction"* **paanch baar** hai. Naapa gaya: **naye 72 ke andar 0 dohre, aur poore
> bank ke khilaf bhi 0** — kal ke batch mein 2 thay. Un paanch yaksan-naam topics par
> alag alag: **har ek par 4 sawal, chaaron alag** — yani paanch qareeb-yaksan prompts se
> **20 mukhtalif sawal**. PY3 par yehi shakl thi aur wahan bhi natija mauzoon tha.
> ⚠ **Magar ye PY1 ka saboot NAHI hai** — wahan 10 topics mein sirf **3** alag titles hain
> aur ek title **saat baar**, jo is se bhi tang soorat hai. **Wahan bhi naapna hoga.**
>
> **2. D60 ka naya check PASS hua, aur wo tawaqqu nahi, naap hai.** Merge ke baad pehli
> seeding: naye 72 mein khaali `learning_outcome` **0**, aur bank ka kul khaali
> **130 par barqarar** (sab `manual`). **Backfill ki zaroorat waqai khatam.**
>
> **Dhaancha 72/72 saaf:** khaali sawal/jawab/tashreeh/Urdu **0**, MCQ bina options **0**,
> MCQ ka jawab options mein **32/32**.
>
> ### 2026-09-04, PY1 ki seeding — quota ne roka, aur EK NAYA MASLA BANA
> **16 sawal, 4/8 topics** (2 chhue hi nahi gaye), 4 par HTTP 429, musalsal teen par
> script khud ruki. **PY1 ab 75/81, baqi 6.** Bank **1198 → 1214**. `integrity_check` ok.
> **D60 ka check phir pass:** khaali `learning_outcome` **130 par barqarar**.
> **Dohraav:** naye 16 ke andar **0**; poore bank ke khilaf **1**, aur wo bhi do alag
> grades mein (*"Count the stars…"* PY1 banaam PY2, marks 4 banaam 5). Saat yaksan-naam
> topics ka andesha yahan bhi nahi laga.
>
> ### ⚠ NAYA MASLA — PY1 AB KHUD DO PAIMANON PAR HAI, AUR YE AAJ BANA
> §1 ki row 2 kehti thi *"PY1 ke har short-answer par 1 mark"*. **Naapne par wo adhoora
> tha: PY1 ka POORA grade 1-mark par tha** — 61 MCQ, 240 short-answer, 28 true-false, sab
> `avg 1.0`, `min 1`, `max 1`. **Aaj ke 16 naye sawal us paimane par NAHI aaye:**
>
> ```
>                    PY1 purane (329)   PY1 naye (16)   PY3 ke liye nisbat
> multiple-choice    avg 1.0            avg 3.4         3.08
> short-answer       avg 1.0            avg 6.14        4.81
> true-false         avg 1.0            avg 2.75        2.18
> ```
>
> **Naye short-answer 6.14 par hain — PY3 (4.81) se bhi ooper**, yani ye sirf "PY2/PY3
> wala paimana" nahi, us se bhi bhaari. **Ab ek hi grade ke andar do paimane hain:** 329
> sawal 1-mark par aur 16 sawal 2–7 par. PY1 ka koi bhi mila-jula paper ab andar se
> be-tarteeb marks dega — **aur ye 09-04 se pehle mojood nahi tha.**
> **✅ FAISLA: (a) — Irfan, 2026-09-04, aur usi din laagu.** Naye sawal 1-mark par le
> aaye gaye; purana bank bilkul nahi chhua gaya. **PY1 phir ek hi paimane par hai:**
> teenon qismein `avg 1.0 / min 1 / max 1`, aur `marks <> 1` wale **0**.
>
> **Set shart se chuna gaya, "aakhri 16 rows" se NAHI** — aur is ne apni qeemat foran
> dikhai: shart (`grade='Pre Year 1' AND marks <> 1`) ne **15** rows pakre, 16 nahi,
> kyunke naye 16 mein se ek MCQ pehle hi 1-mark par aaya tha. "Aakhri 16" likhne se ek
> row be-wajah likhi jati. Aur chunke PY1 ke purane 329 sab pehle se 1 par thay, ye
> shart khud sabit karti hai ke koi purana row is mein aa hi nahi sakta.
> **Backup se row-by-row diff:** *rows pehle 1214 ab 1214, gayab 0, naye 0, badle hue
> columns `{marks: 15}`*, `integrity_check` ok.
>
> ⚠ **Ye sirf aaj ke rows ka ilaaj hai, sabab ka nahi.** `seed_bank.py` ko PY1 ka paimana
> maloom nahi — **agle batch ke sawal phir 2–7 par aayenge** aur yehi `UPDATE` dobara
> chalani paregi. **Baqi 6 topics seed karne ke foran baad ye check karo:**
> `select count(*) from questions q join syllabus_topics t on t.id=q.syllabus_topic_id
> where t.grade='Pre Year 1' and q.marks <> 1` — **0 aana chahiye.**
>
> ### 2026-09-04 ka audit — DB aur code raat bhar nahi hile, magar EK ADAD BADLA
> Sab dobara naapa gaya aur barabar mila: bank **1126**, PY1 71/81, PY2 69/87, PY3 87/87,
> **baqi 28**, khaali `learning_outcome` **130 (sab `manual`)**, `integrity_check` ok,
> **1083 pass**, ruff saaf, `legacy_css_lines` **1697**, `unsanctioned_hex` **300**.
>
> **Magar audit ka scope 276 → 254 ho gaya** (rule-block 1326 → **1303**, agree 86 → **77**,
> disagree 190 → **177**), kyunke 09-03 ke teen kaam un rules ko legacy se nikal le gaye,
> is liye wo scope se bhi nikal gaye. **Is ne 09-03 ki shaam ka mera apna hisaab ghalat
> sabit kiya:** maine "target se ~21 lines door" likha tha, purana scope 276 istemal karke.
> Sahi hisaab §4 mein hai aur wo **43** hai. **Sabaq wahi purana: apne hi kal ke adad ko
> naape baghair dobara mat quote karo.**
> *(Neeche wala khulasa **2026-09-02 ko din ke beech** likha gaya tha aur usi din ka baqi
> kaam us mein nahi tha — **2026-09-03 ko dobara naap kar theek kiya gaya**, purane alfaz
> ~~strike~~ ke saath mojood hain. Plan ke qadam (§1–§4) us waqt bhi durust thay.)*
>
> **2026-09-03 ka natija — seeding chali, backfill chali, aur poora board dobara naapa gaya.**
> **Seeding:** PY2 ke 39 topics maange; **exit code 0, magar run beech mein ruki** — 25
> topics chhue, **21 bane (84 sawal)**, 4 par HTTP 429, **14 topics chhue hi nahi gaye**.
> Bank **1042 → 1126**, PY2 **48 → 69/87**. **Baqi ab 28: PY2 ke 18, PY1 ke 10.**
> **Dhaancha saaf** (84 par naapa): khaali sawal/jawab/tashreeh/Urdu **0**, MCQ bina
> options **0**, MCQ ka jawab options mein **37/37**, har topic par poore 4 — 21/21.
> **D60 ka backfill chal gaya:** 84 rows, backup se row-by-row diff —
> *rows pehle 1126 ab 1126, gayab 0, naye 0, badle hue columns `{learning_outcome: 84}`*,
> `integrity_check` ok. Khaali `learning_outcome` phir **130** (wohi manual/topic-NULL wale).
> **Audit ka natija:** board ke **11 daawe naape gaye aur sab sach nikle** (item 8 ke
> teenon rules ki qadrein, `.brand .tag`, `body` ke 6/7, item 9, 1706/300, scope 276,
> jaali jode, D60, tests, `f547f21` master par nahi) — **chhe jagah farq nikla**, sab
> neeche apni apni jagah theek kar diya gaya.
>
> ⚠ **Sab se ahem farq — PY2 ka dohraav-khatra ULTA ho gaya hai. §1 dekho.**
>
> **2026-09-02 ka natija — din audit par gaya, seeding quota par mari gayi.**
> Irfan ne audit maanga; **board pehli baar poora sach nikla** (310/214/96, 1030 sawal,
> 1706 lines, scope 276, 1075 pass — sab dobara naape gaye aur sab barabar), sirf
> commit-count basi tha (45 likha, **50** tha).
>
> ⚠ **Ye is paragraph ke adad us lamhe ke hain jab audit chali — seeding aur D57 se
> PEHLE — is liye ye basi nahi, "us waqt ka" hain. Aaj ke adad khulase ke aakhir mein
> hain (naapa 09-03).** Do farq jaan-boojh kar chhore gaye aur dono ka hisaab poora hai:
> **1075 → 1078 pass** = D57 ke teen naye test (`tests/test_brand_hooks.py`, `7868fdf`);
> **214/96 → 217/93 seeded/baqi** aur **1030 → 1042 sawal** = usi din ki seeding (PY2 ke
> teen topics). **Adad yahan se mat quote karo — §1 ki bank table aur khulase ka aakhri
> paragraph parho.**
>
> **Seeding:** PY2 ke 42 topics maange, **quota chauthe topic par lag gaya** — sirf
> **12 sawal, 3/7 topics**, 35 topics chhue hi nahi gaye. Bank **1030 → 1042**,
> PY2 45 → **48/87**. **Baqi ba-ikhtiyar 49 topics: PY2 ke 39, PY1 ke 10.**
>
> **`persist_batch` ka surakh (`DEFERRED.md` D60):** `learning_outcome` kabhi save nahi
> hota tha — 571/571 gemini sawal khaali. Fix `master` se kaati branch par
> (`fix/persist-batch-learning-outcome`, `f547f21`, ek line + paanch tests, 980 pass),
> **is branch par nahi** — `PLAN.md` §6 yahan service tabdeeli mana karta hai.
> **Backfill chal gaya:** 583 rows syllabus se bhari gayin, koi AI call nahi;
> khaali `learning_outcome` **701 → 130**, aur wo 130 English bulk-import ki hain
> jin ka `syllabus_topic_id` NULL hai. Backup se row-by-row diff: **sirf
> `learning_outcome` badla, 583 rows, koi row na gayi na aayi.**
>
> ~~**CSS par aaj kuch nahi hua** — 1706 jyun ka tyun.~~ ⚠ **Ye jumla us waqt likha gaya
> jab item 9 aur D59 baqi thay; usi din dono ho gaye. Naapa 2026-09-03:**
> **CSS par kaam HUA, magar `legacy_css_lines` phir bhi 1706 — aur ye tazad nahi:**
> item 9 (UI-075) ne `static/app.css` (57 lines) li, jo `static/css/` se bahar hai aur is
> counter mein kabhi thi hi nahi; D59 ne `scripts/` ki do probe files (1039 lines) leen, jo
> CSS hain hi nahi. **Drain ka faasla waisa ka waisa hai** — §3/§4 ka tail (item 8 ka tail,
> `.tag`, `body`) ab bhi baqi.
>
> **Paanch DEFERRED rows band hueen: D5, D57, D59, D29, D30 — aur in mein se CHAAR ka apna
> bayan naapne par ghalat nikla** (D59 ki *"deleting it is tempting and wrong"* wali dalil,
> D57 ka poora symptom, D29 aur D30 apni hi peshgoi par mareen). **Row par bharosa mat karo
> — is repo ki sab se baar-baar aane wali bimari yehi hai.** D60 khuli hai (fix
> `master`-wali branch par, is branch par nahi).
>
> ~~**Browser check phir nahi hua** (ab chaar sessions se khula).~~ ✅ **09-03 KO BAND HO
> GAYA — aath mein se aath.** Chaar khud naape jate hain, baqi chaar Irfan ne aankh se
> dekhe aur chaaron theek. Ye row `2026-08-28` se latki hui thi.
>
> ~~Do commit bane, **dono un-pushed**.~~ → **09-02 ko chhe commit bane** (`566d722` …
> `38256b2`), **sab un-pushed**; `master` se ~~56~~ **59 aage, 0 peechhe** (09-03 ke apne
> docs commits mila kar — **is adad ko yahan se mat quote karo, naapo**).
> Tests **1078 pass** (2026-09-03 ko chalaye), ruff saaf; bank ~~1042~~ **1126**, khaali
> `learning_outcome` **130** (sab `syllabus_topic_id` NULL) — sab dobara naape gaye.

**1. SEEDING — PEHLA KAAM, subah sab se pehle.** Quota-bound hai, waqt-bound nahi: subah
nahi chala to din ka quota zaya. ~~**Baqi ba-ikhtiyar 49 topics — PY2 ke 39, phir PY1 ke
10.**~~ **Naapa 2026-09-04: baqi 28 — PY2 ke 18, phir PY1 ke 10.**

> ### ✅ D60 BAND HO CHUKI — BACKFILL AB NAHI CHALANI, MAGAR NAAPNA ZAROORI HAI
> `f547f21` ab `master` par hai (merge `dc9436a`), aur `question_service.py`:65 par wo
> khana mojood hai. **Yani yahan se chalayi gayi seeding ka `learning_outcome` khud
> bharna chahiye aur backfill ki zaroorat khatam.** ⚠ **Magar ye TAWAQQU hai, naap nahi:
> pehle batch ke baad khaali ginti khud dekho** —
> `select count(*) from questions where learning_outcome is null or trim(learning_outcome)=''`
> — jo **130 se barhna nahi chahiye** (wo 130 bulk-import ke hain, D61). Agar barhe, to
> fix merge hone ke bawajood kaam nahi kar rahi aur **D60 dobara kholni paregi**.

> ### ⚠ BACKUP: `.db` FILE COPY KARNA AB KAAFI NAHI
> 2026-09-04 ko `paper_maker.db-wal` mojood mila (09-03 ko nahi tha). WAL mode mein
> seedhi file copy adhoori ho sakti hai. Backup **sqlite ke apne backup API se lo**:
> ```
> python -c "import sqlite3; s=sqlite3.connect('file:paper_maker.db?mode=ro',uri=True); d=sqlite3.connect('BACKUP.db'); s.backup(d)"
> ```
> Phir backup par `integrity_check` aur row-ginti dono naapo.

> **Quota ka anjaam aankhon se dekha gaya, dono din:** `FAIL: Gemini ka quota/rate-limit
> lag gaya (HTTP 429)`. **Output ka tail parho, sirf exit code par mat jao** — 09-02 ko
> exit code **0** tha jab ke 168 mein se sirf **12** sawal bane.
>
> ⚠ **09-01 ka wo jumla ke "script rukti nahi, har baqi topic par yehi FAIL deti hai"
> GHALAT tha — 09-02 ko naapa gaya.** `seed_bank.py`:59 par
> `MAX_CONSECUTIVE_RATE_LIMITS = 3` hai: musalsal teen 429 par script **jaan-boojh kar
> rukti hai** aur saaf likhti hai —
>
> ```
>   RUK GAYE: musalsal 3 dafa rate limit.
> Kul mehfooz: 12 sawal, 3/7 topics
> Run beech mein ruki -- 35 topics chhu-e bhi nahi gaye.
> ```
>
> **Aur is se 09-01 ka wo muamma bhi hal hota hai jise ye board "kyun kata, maloom nahi"
> kehta hai** — wo qareeb yaqeenan yehi stop tha, jo sirf is liye nazar nahi aaya ke us
> din output file khali reh gayi thi. **Nasihat sahi thi, wajah ghalat.**
>
> **Quota ki hadd din-ba-din alag hai, is liye us par plan mat bandho:** 09-01 ko ~180
> sawal ke baad lagi, 09-02 ko **chauthe topic par** hi lag gayi.
>
> **Output hamesha file mein bhejo** (`> seed.log 2>&1`) — do baar ye tail sirf is liye
> nahi parha ja saka ke wo kahin mehfooz hi nahi hua tha.
>
> ⚠ **`python -u` LAZMI hai, aur ye 2026-09-03 ko naapa gaya.** Sirf redirect kaafi nahi:
> file par Python ka stdout **block-buffered** hota hai. Us din 10 topics ho chuke thay
> (DB mein 1082 sawal) aur `seed_20260903.log` phir bhi **0 bytes** tha — poora output
> aakhir mein ek saath gira. Yani **agar run beech mein maar di jaye ya crash ho, tail
> buffer ke saath ghayab ho jata hai** — 09-01 ki khali log file ki qareeb-yaqeeni wajah
> yehi hai, redirect ki kami nahi. `-u` ke saath har topic foran file mein likha jayega,
> aur chalte hue `tail -f` bhi kaam karega.
>
> **Chalte hue progress dekhne ka doosra (aur zyada qabil-e-aitmad) tareeqa DB hai** —
> script har topic ke baad commit karti hai, is liye ye read-only ginti buffering se
> bilkul mutassir nahi hoti:
> `select count(*) from questions` — 09-03 ko isi se pata chala ke run zinda hai.

```
python -u -m scripts.seed_bank --subject Mathematics --grade "Pre Year 2"   --types "multiple-choice,short-answer,true-false" --bloom foundational   --max-topics 87 --write > seed.log 2>&1
```

> ⚠ **PY1 ke 10 topics ko purana plan ginta hi nahi tha** (wo "baqi 87" kehta tha, jo
> sirf PY3+PY2 tha). 2026-09-01 ko naapne par nikle: **Pre Year 1 = 71/81 seeded, 10
> khaali.** PY2 khatam hote hi wohi command `--grade "Pre Year 1"` ke saath.
>
> **Defaults NAHI** — pre-school par `fill-blank`/`essay`/`balanced` ghalat hain.
>
> **Pehle dry run, phir `--write`, aur `--write` se pehle backup.** Namoona:
> `paper_maker_backup_before_preyear2_seed_20260901.db`.
>
> **Dobara chalana mehfooz hai, aur ye do baar naapa ja chuka hai:** `--include-seeded`
> ke baghair script pehle se seeded topics chhorti hai, aur **har topic ke baad commit
> karti hai** — is liye beech mein ruk jane par bhi koi topic adhoora nahi rehta.
> 09-01 (18 topics ke baad ruki) aur 09-02 (3 ke baad) — **dono dafa DB saaf**:
> `integrity_check` ok, har chhue topic mein poore 4 sawal.
>
> **Rows aankh se dekho — do alag khatre hain, aur dono ki shakl alag hai:**
> 1. **Jaali syllabus** — 2026-08-21 ko paanch rows ek jaisi nikleen, 44 ghalat sawal
>    delete karne pare. Chaar jaali jode (G5, G6, Science G7, Geography G8) **seed karna
>    mana hai** jab tak asal syllabus import na ho. 09-02 ko naapa: chaaron ab bhi **0**.
> 2. **Dohraya hua title** — ⚠ **09-03 ko dobara naapa aur ye tasveer PALAT gayi. Ab
>    DONO khatarnaak hain, sirf PY1 nahi:**
>
>    ```
>    baqi topics   alag titles   LO == title
>    PY2   18          10           18/18   <- "Practice of subtraction" PAANCH baar
>    PY1   10           3           10/10   <- "Practice and Review of number and
>                                                value" SAAT baar
>    ```
>
>    ~~09-02: PY2 39 baqi, ~30 alag titles, 41/42 — yani "PY1 sab se khatarnaak nikla,
>    PY2 nahi"~~. **Wo jumla ab ghalat hai, aur wajah samajhna zaroori hai: 09-03 ki run
>    ne 21 topics banaye aur wo zyadatar ALAG titles wale thay — is liye jo bache hain wo
>    dohre hain.** Yani har run ke baad ye ginti **kharab hoti jayegi**, behtar nahi.
>    **Agli PY2 run ab PY1 jitni khatarnaak hai — dono ke baad dohraav zaroor naapo.**
>    PY3 par yehi shakl thi aur natija phir bhi mauzoon nikla tha (16 sawal, 16 ke 16
>    alag) — **magar wo saboot nahi hai.**
>
>    **09-03 ki run par dohraav naapa gaya, aur natija mauzoon tha:** naye 84 ke andar
>    **0** dohre; poore bank ke khilaf **2** — dono **do alag grades** mein (*"Which of
>    these shapes is a triangle?"* PY2 banaam PY3, aur *"If you have 3 red flowers…"*
>    PY2 banaam PY3). 2/84 pichhle batches ke barabar hai. **Faisla Irfan ka, maine kuch
>    delete nahi kiya.**

**BANK KA HISAAB — 2026-09-04 ko naapa gaya (adad yahan se parho, yaad se nahi):**

```
grade         topics  seeded  baqi   sawal
Pre Year 1        81      75     6     345   <- baqi 6, quota par ruki
Pre Year 2        87      87     0     348   <- mukammal 2026-09-04
Pre Year 3        87      87     0     348   <- mukammal
Grade 4           11      11     0      43
G5/G6/Sci7/Geo8   44       0    44       0   <- JAALI, seed karna mana
KUL              310     260    50    1084
```

> ~~09-02: PY2 48/39/192, KUL 217/93/912~~ — 09-03 ki seeding ke baad badal gaya.
> **Jaali chaar jode ka poora naam (09-03 ko naapa, board pehle sirf "G5/G6" likhta tha):
> Grade 5 Mathematics, Grade 6 Mathematics, Grade 7 Science, Grade 8 Geography — 11-11
> topics, chaaron par sawal `0`.**

> **`1084` topic-se-jure sawal hain; `questions` table mein kul 1214 hain.** Farq wo
> **130 English sawal** hain jin ka `syllabus_topic_id` NULL hai (bulk Excel import) —
> un ke liye koi syllabus row hai hi nahi. **Dono adad theek hain, bas alag cheez
> ginte hain** — jo bhi "bank ka size" likhe, batae ke kaun sa.

**DO CHEEZEIN JO NAAPI GAYIN AUR THEEK NAHI HAIN — faisla Irfan ka, maine kuch nahi badla:**

1. **`learning_outcome` har seed-shuda sawal mein khaali hai.** 09-01 ke 164 mein se 164
   khaali — magar ye aaj ka bug **nahi**: 08-31, 08-26, 08-23, 08-22, 08-21 —
   **har batch 100% khaali**. Sirf 07-15/07-19 wale (alag raste se aaye) bhare hain.
   Khamoshi se chal raha tha.
   > **⚠ 2026-09-02 — is row ke do adad ghalat thay aur wajah bhi ghalat thi. Dekhein
   > `DEFERRED.md` D60.** (a) Ye row **`seed_bank.py`** par ilzaam lagati thi; script
   > theek bhejti hai (`:146`) — surakh `question_service.py` ke **`persist_batch()`**
   > mein tha, jise `/api/generate` bhi bulata hai. (b) Row **"701 khaali"** ke saath
   > **07-30** ko seed batch gin rahi thi. Naapa gaya: bug ka daira **571** hai
   > (`source='gemini'`, 571/571 khaali); 07-30 wale **130 rows bulk Excel import** hain
   > aur `bulk_import_service.py:334` un ka khana **bharta** hai — wo Excel ka column
   > khaali hone se khaali hain. **Fix `f547f21` par ho chuki hai magar `master`-wali
   > branch par — IS branch par nahi**, is liye yahan se chalayi gayi seeding ab bhi
   > khaali likhegi aur baad mein **backfill** chahiye (syllabus se SQL, muft).
   > **✅ BACKFILL 09-02 KO CHAL GAYA:** 583 rows bhari gayin, khaali **701 → 130**.
   > Backup se row-by-row diff liya gaya — **sirf `learning_outcome` badla, 583 rows,
   > koi row na gayi na aayi**, `integrity_check` ok. Bache hue 130 wohi English
   > bulk-import wale hain (`syllabus_topic_id` NULL) — **un ki wajah ye bug nahi hai**
   > aur unhein syllabus se nahi bhara ja sakta; wo Excel ya manual ka kaam hai.
   > ⚠ **Har seeding ke baad ise dobara chalana parega** jab tak `master` merge na ho —
   > wo ek line is branch par nahi hai.
   > **✅ DOBARA CHAL GAYA 2026-09-03, aur is ne wo tanbeeh sahi sabit ki:** 09-03 ki
   > seeding ke **84/84** naye sawal khaali `learning_outcome` ke saath likhe gaye —
   > yani surakh is branch par bilkul zinda hai. Backfill ne **84 rows** bhari; backup se
   > row-by-row diff — *rows pehle 1126 ab 1126, gayab 0, naye 0, badle hue columns
   > `{learning_outcome: 84}`*, `integrity_check` ok. Khaali phir **130** (wohi manual).
   > **84/84 bhari hui qadr apne topic ke barabar hai** — sirf "khaali nahi" nahi naapa.
   > ⚠ **Magar ek baat jo backfill se nahi banti:** in topics ka apna `learning_outcome`
   > akser **title hi hota hai** (baqi PY2 ke 18 mein **18/18**, PY1 ke 10 mein **10/10**),
   > is liye bhara hua khana asal maloomat nahi, **sirf title ki nakal** hai. Ye syllabus
   > ke data ki kharabi hai, is bug ki nahi — aur `master` merge is ko theek nahi karega.
2. **PY1 aur PY2/PY3 ke marks ka paimana alag hai.** ⚠ **2026-09-04 ko naapne par ye row
   do jagah adhoori nikli.** (a) Baat sirf short-answer ki nahi thi: **PY1 ka poora grade
   1-mark par tha** — 61 MCQ, 240 short-answer, 28 true-false, sab `avg 1.0 / min 1 /
   max 1`. (b) **Aur ab ye "PY1 banaam PY2/PY3" ka masla nahi raha — PY1 KHUD DO PAIMANON
   PAR HAI**, kyunke 09-04 ke 16 naye sawal `avg 3.4 / 6.14 / 2.75` par aaye. Tafseel
   ooper 09-04 ke block mein, teen soorton ke saath. ~~Purana matn:~~ PY1 ke har
   short-answer par **1 mark** (240 sawal, sab 1); PY2/PY3 ke short-answer par **avg ~4.5** (3–7). 09-01 ka
   batch (4.4 / 4.55) pichhle sab AI batches ke barabar hai — **behkaav aaj nahi aaya**,
   magar bank mein do paimane mojood hain. Mile-jule paper ka total ajeeb banega.

**Dhaancha saaf hai** (09-01 ke 164 par naapa): khaali sawal 0, khaali jawab 0, MCQ bina
options 0, MCQ ka jawab options mein 68/68, Urdu 164/164, tashreeh 164/164. Dohraav:
poori PY3 348 mein se 2, PY2 164 mein se 1.

**2. BROWSER CHECK — ✅ BAND, 2026-09-03. AATH MEIN SE AATH.**
Chaar khud naape jate hain; baqi chaar Irfan ne **2026-09-03 ko aankh se dekhe aur
chaaron THEEK** — wo row jo `2026-08-28` se latki hui thi aur paanch session khuli rahi.
Server: `python -m uvicorn app.main:app --port 8000`, phir kholo:

### 👉 `http://127.0.0.1:8000/static/dev/ui-check.html`

`static/dev/ui-check.html` (banai 2026-09-01) har page ko **iframe mein kholti hai — same
origin, is liye andar dekh sakti hai** — aur jo naapa ja sakta hai khud naap kar THEEK /
KHARAB likh deti hai. Jo click ke baghair nahi banta, us par **AANKH** likhti hai aur
neeche batati hai ke kya karna hai. **Wo AANKH wale kabhi apne aap ✅ nahi honge** —
un chaar ka ✅ Irfan ki aankh se aaya hai, script se nahi.

> ⚠ **YE ✅ EK LAMHE KA HAI, HAMESHA KA NAHI.** Chaar khud-naape rows har run par dobara
> naap lete hain; **chaar aankh wale nahi**. Jo bhi CSS chhue, wo ye chaar dobara khulwa
> deta hai — 09-03 ko item 8 isi liye pehle chalaya gaya aur phir aankh maangi gayi.
> **Agar aap ne aankh se dekhe baghair CSS badli, to in chaar ka ✅ ab aap ka daawa hai,
> naap nahi.**

| dekho | kahan | halat (chaar khud-naape 09-01, chaar aankh se 09-03) |
|---|---|---|
| do SLO boxes ka border (add / edit) | `bank.html` — UI-072 ki waahid pixel tabdeeli | ✅ dono par `1px solid rgb(234,237,243)` |
| pagination buttons ka rang | `library.html` — **kaala dikhe to `color: inherit` fail hai** | ✅ `rgb(15,23,42)`, body ke barabar — kaala nahi |
| disabled **button** par 🚫 cursor | `bank.html` | ✅ `not-allowed` |
| heading ke neeche subtitle | `bank` · `library` · `slo-health` — saath ek line par aaya to bug | ✅ teenon par `p` ka top 65.4px, `h1` ka bottom 62.4px |
| import counters styled hain | `slo.html` (Excel import ke baad) | ✅ **Irfan, 09-03** |
| chips column mein | `taqseem.html` (class + subject chuno) | ✅ **Irfan, 09-03** |
| shortfall warning ka andar ka text | `blueprint.html` (paper banao) | ✅ **Irfan, 09-03** |
| **paper theek chhapta hai** | `print.html?paper_id=1cec8e77-2c1b-490e-babe-758bdef53f93` — **UI-073 ka asar**, Ctrl+P preview bhi | ✅ **Irfan, 09-03**, screen + Ctrl+P dono |

> ⚠ **`disabled` wala row ab saaf likha gaya hai: sirf `button`.** Pehli chalaayi mein
> check ne pehla disabled element uthaya, jo `<select>` tha, aur **jhoota KHARAB** de
> diya. `forms.css:211` ka rule `button:disabled` hai — disabled `<select>` ka `default`
> cursor **bug nahi**, aur us file ka apna comment ye wajah likhta hai. Check ab dono
> qadrein alag alag dikhata hai.

**3. CSS — jo bacha, is tarteeb mein.** `legacy_css_lines` **1697**, target **~1500**
(2026-09-04 ko nazar-e-sani hui — `DECISIONS-FOR-IRFAN.md` §7; purana `~1400` mansookh).

> ⚠ **Comment ki apni qeemat hai — 09-01 ko naapa gaya.** UI-074 mein 7-line ka wazahati
> comment likhne se `legacy_css_lines` **1707 → 1713** ho gaya **aur `unsanctioned_hex`
> 301 → 302**, kyunke hex comment ke andar likha gaya tha aur counter use ginta hai.
> **Wazahat PROGRESS.md mein likho, legacy file mein nahi.**

* ~~**Item 8 ka tail**~~ ✅ **HO GAYA 2026-09-03 (UI-076) — faisla `A`, aur kaam bhi usi
  din.** `.strip-empty` + `.list-empty` naye `05-components/empty.css` mein,
  `.options-grid` `05-components/field.css` mein; har page ka farq us ke `pages/*.css`
  ke `@layer components` mein. **Qadrein ek bhi nahi badli.**
  **Gate dono chale: inject probe 0 deltas, aur `css_type_probe` das pages × paanch
  viewports par 0 deltas (~24 lakh muqable).**
  `legacy_css_lines` **1706 → 1704**, `unsanctioned_hex` **300 par barqarar**.
  ⚠ **Do cheezein jo is kaam ne sikhayin aur agla session inhein na bhoole:**
  1. **`grid-template-columns` component mein jate hi bank ka `@760` override MAR raha
     tha** — wo `layer(legacy)` mein tha aur component `layer(components)` mein hai;
     **media query layer order ko nahi badalti.** Us ko `pages/bank.css` mein uthana
     para. Narrow viewport is kaam ka asal khatra tha, isi liye gate paanchon viewports
     par chalaya gaya, sirf 1280 par nahi.
  2. **Pehli koshish mein `legacy_css_lines` 1706 → 1708 BARH gayi aur `unsanctioned_hex`
     300 → 306** — kyunke pointer comments do-do line ke thay aur un ke andar hex likhe
     thay. Board ki apni tanbeeh (§3: "wazahat legacy file mein nahi") isi jagah lagti
     hai, aur ratchet is se toot sakti thi. Comments ek-ek line ke kiye gaye aur hex
     nikale gaye.
  ~~Purana kaam ka nuqta:~~ ~~pehla qadam CSS nahi:~~
  1. **`css_inject_probe.mjs` ki fixtures** `.strip-empty` + `.list-empty` ke liye likho.
     Ye dono JS se bante hain, is liye `css_type_probe`/`css_state_probe` inhein **sifar**
     ginte hain aur **ghalat tabdeeli par bhi 0 deltas denge** (D45 ki shakl, `PROBES.md`
     rule 10). Fixtures ke baghair gate jhoota "theek hai" dega.
  2. Mushtarka declarations `05-components/` mein; `bank` 8px/8px, `print` 6px/0,
     `blueprint` 30px padding — **har page apna farq apni `pages/*.css` mein**, qadrein
     nahi badleen, **koi dikhne wali tabdeeli nahi.**
  3. `.options-grid` ka `@760` wala `1fr` override **sirf `bank`** par hai — wahin rahe.
  ⚠ **`unsanctioned_hex` is se NAHI ghatega:** wo faida `B` ka tha (print ka hardcoded hex
  `var(--muted2)` ke haq mein marta), aur `A` page ka farq qaim rakhta hai. Target ka
  hisaab likhte waqt ye line parho. Tafseel: `DECISIONS-FOR-IRFAN.md` §6.
  ~~Purana row:~~ ~~**⛔ ab FAISLA-TALAB hai, "6 lines delete" nahi.**~~
  `.options-grid`, `.strip-empty`, `.list-empty` — **teenon ki do-do copies hain aur har
  jodi mein qadrein alag hain** (naapa 2026-09-01: `.options-grid` gap **8px** banaam
  **6px**; `.list-empty` padding **40px 20px** banaam **30px**; `.strip-empty` mein
  `var(--muted2)` banaam hardcoded hex). Isi liye audit ne inhein `disagree` mein rakha
  hai. **Teen soortein `DECISIONS-FOR-IRFAN.md` §6 mein likhi hain — pehle jawab, phir
  kaam.**
  ⚠ **`.strip-empty` aur `.list-empty` JS se bante hain** — `css_type_probe` inhein sifar
  ginta hai, yani **ghalat tabdeeli par bhi 0 deltas dega.** `css_inject_probe.mjs` ke
  fixtures mein ye do nahi hain; kaam se pehle fixtures likhni parengi.
* ~~**`index` ki do murda `.tag` declarations**~~ — **✅ UI-074, aur ab UI-078 (2026-09-03)
  se poori tarah band.** Jo ek declaration zinda thi (`.brand .tag` ka `letter-spacing`)
  wo delete nahi, **`pages/index.css` mein uthai gayi**; saath hi `landing` ki
  `.brand .tag` bhi uthai — **us ki chaaron declarations zinda thin**, kyunke landing ki
  apni file mein koi `.tag` rule hai hi nahi. `legacy_css_lines` **1699 → 1697**,
  `unsanctioned_hex` 300 par barqarar, **probe 0 deltas** (das pages × paanch viewports).
  **`pages/index.css` ka jhoota jumla theek ho gaya:** wo kehta tha *"Both legacy `.tag`
  declarations can go"* jab ke usi comment ki agli line kehti thi *"only `letter-spacing`
  ever survived"* — do line mein apne aap se ulat. Ab strike ke saath wajah likhi hai.
  ⚠ **Naapte waqt ek naya farq nikla: `index` par ek hi tagline do jagah likha hai
  (`index.html`:16 aur `:50`) aur DO ALAG TARAH paint hota hai** — `.brand` wale par
  `letter-spacing` 0.44px, doosre par `normal`. Ye aaj ka bug nahi; **`DEFERRED.md` D62**,
  faisla Irfan ka.
  ~~Purana row:~~
  09-01 ko dono alag alag naapi gayin: **`.topbar .tag` (`:288`) waqai murda thi —
  delete ho gayi** (0 deltas, das pages × paanch viewports). **Magar `.brand .tag`
  (`:32`) ZINDA hai** — 0.44px letter-spacing, jo kahin aur declare nahi hota. **Wo
  chhori gayi hai; use delete mat karna.** `pages/index.css:245` ka comment
  (*"Both legacy `.tag` declarations can go"*) **is baare mein ghalat hai.**
* ~~**`body` ka bacha hua hissa**~~ ✅ **HO GAYA 2026-09-03 (UI-077) — faisla: `plan.css`
  wala namoona sab par.** Chhe pages (`bank`, `library`, `print`, `slo`, `slo-health`,
  `taqseem`) ki `body { display: flex; min-height: 100vh }` aur un ka `@media`
  `flex-direction: column` `99-legacy/` se nikal kar **har page ki apni `pages/*.css` ke
  `@layer objects`** mein — bilkul waise jaise `plan` pehle se karta tha. Qadrein nahi badlin.
  `legacy_css_lines` **1704 → 1699**, `unsanctioned_hex` 300 par barqarar.
  **Gate: `css_type_probe`, das pages × paanch viewports — chhe pages par 0 deltas.**
  ⚠ **CHAAR CHEEZEIN JO NAAPNE PAR NIKLEEN, AUR TEEN BOARD KE KHILAF THIN:**
  1. **Shared file mein ye rule NAHI ja sakti thi.** `body` bare selector hai; ek
     `04-objects/` wali rule das ke das pages par lagti aur `index`/`landing`/`blueprint`
     — jin ki body aaj **`block`** hai — sab flex ho jate. Isi liye har page ki apni file.
  2. **`print` ki chhapai toot rahi thi.** `@media print { body { display: block } }`
     `layer(legacy)` mein tha; `display: flex` ke objects mein jate hi wo haar jata aur
     **paper flex layout mein chhapta**. Us ek declaration ko `pages/print.css` ke usi
     layer mein uthana pada (base rule ke BAAD — tarteeb badalna is ko tor dega).
     `background` jaan-boojh kar legacy mein chhora: upar le jane se murda declaration
     zinda ho sakti thi. **Naapa gaya: print media mein body ab bhi `block`.**
  3. **Board kehta tha "`flex-direction: column` saat files mein byte-identical".** Rule
     ka matn barabar hai, **media query nahi**: `bank`/`library`/`print`/`blueprint` **760px**
     par hain aur `slo`/`slo-health`/`taqseem` **720px** par. Har page ne apna breakpoint
     rakha — unhein barabar karna ek dikhne wali tabdeeli hoti jo kisi ne nahi maangi.
  4. **Saatwin copy MURDA thi.** `blueprint` ki body `display: block` hai (dono widths par
     naapa), aur flex-direction non-flex body par kuch nahi karti. Wo rule delete ki gayi.
     **Is par probe ne 3 deltas diye — sirf `flex-direction`, sirf 760 se neeche wale
     teen widths par — aur ye peshgoi delete se PEHLE likhi gayi thi.** Render kuch nahi
     badla, kyunke body block hai.
  ~~Purana row:~~ (UI-073 ne sirf murda hissa liya): `display:flex` +
  `min-height:100vh` chhe pages par — `pages/plan.css` ka `@layer objects { body }`
  namoona mojood hai, **faisla Irfan ka**; `@media` ka `flex-direction: column` saat
  files mein byte-identical — **magar media-query + layer wali shakl hai, uthane se
  pehle naapo** (UI-05x mein isi ne 75 deltas diye thay); `html, body { height: 100% }`
  **naapa nahi gaya**; `index` ke teen `body.lang-ur` (`05-components/urdu.css` mojood
  hai, magar khandan badalna apna faisla hai).
* ~~**Item 9**~~ ✅ **HO GAYA 2026-09-02 (UI-075).** `static/app.css` delete (57 lines);
  us ka `.icon` rule ab `05-components/icon.css` mein; **das ke das pages ab EK hi
  stylesheet link karte hain**; dono mockups `docs/design/` mein — **D5 band**.
  **Gate: `css_type_probe` — das pages × paanch viewports, 0 element × property deltas.**
  `.icon` nau icon-wale pages par 17×17. Irfan ne browser mein OK kiya.
  ⚠ **Review ne FAIL diya tha aur theek diya:** maine likha tha ke 17px ab layer order se
  `99-legacy/landing.css` ki 22px ko harata hai — **wo rule UI-060 ne 2026-08-16 ko delete
  kar diya tha.** `.icon` ab be-muqabla hai. **Ek header jo cascade bayan karta hai utna hi
  basi hota hai jitna carried number** — ye wala apni rule se sattrah din zyada jiya.
  D59 (jo item 9 ki rukawat thi) usi din band hua: `css_orphans.py` + `css_rules_probe.mjs`
  delete, 1039 lines — us row ki apni dalil bhi naapne par ghalat nikli.
* ~~**Phir `master` merge**~~ ✅ **HO GAYA 2026-09-03 — `dc9436a`.** Tarteeb jaan-boojh kar
  ye rakhi gayi: **pehle `f547f21` `master` mein fast-forward** (D60 ki wo ek line), **phir
  epic us ke ooper `--no-ff` merge**. Ulta karne se wo line epic ke saath na aati.
  **Naapa gaya merge se PEHLE:** epic ne `question_service.py` aur `test_persist_batch.py`
  chhui hi nahi thin, is liye conflict mumkin nahi tha — aur merge waqai bila-conflict hua.
  **Naapa gaya merge ke BAAD:** `1083 pass` (epic ke 1078 + fix ke 5), ruff saaf,
  `legacy_css_lines` **1697**, `unsanctioned_hex` **300**, aur `question_service.py`:65 par
  wo khana mojood hai jis ki kami D60 thi. **D60 band.**
  ⚠ **Push NAHI kiya gaya** — wo Irfan GitHub Desktop se khud karta hai.
  ~~Purana row:~~ ~~09-02 ko naapa: **52 aage** (is commit se pehle), **0 peechhe**~~
  **(09-03 ko 56 tha — yani ye adad yahan likhte hi basi ho gaya, jo isi row ki apni tanbeeh
  ka saboot hai. Ab yahan koi adad nahi; command chalao):**
  ⚠ **Ye adad har commit par badalta hai — isay yahan se mat quote karo, naapo:**
  `git rev-list --left-right --count master...HEAD`. Board is se pehle do baar basi
  mila (09-01 ne 45 likha, 09-02 ko 50 tha). **Item 9 ab ho chuka hai, is liye ye rukawat
  khatam** — ~~merge ke raaste mein sirf item 8 ka tail bacha hai, jo §6 ke jawab par ruka
  hai~~ **(09-03: §6 ka jawab `A` aa gaya, is liye item 8 ka tail ab RUKAWAT nahi, KAAM
  hai — dekhein ooper). Merge se pehle wo kaam aur `body`/`.tag` ka tail hona chahiye.** ⚠ Merge ke waqt `master` par `fix/persist-batch-learning-outcome` (D60 ka fix) bhi
  shamil hona chahiye, warna wo ek line yahan nahi aayegi.

**4. ⚠ TARGET KA HISAAB TANG HAI — ye agle session ki pehli CSS baat hai.**

~~Target `~1400` **Irfan ka faisla hai aur qaim hai**~~ **→ 2026-09-04 ko NAZAR-E-SANI HUI.
Naya target `~1500`** (`DECISIONS-FOR-IRFAN.md` §7, jawab A). Neeche ka poora hisaab wahi
saboot hai jis par ye nazar-e-sani hui — use padha jaye, mitaya nahi.
Magar UI-073 ke baad audit dobara chali aur scope **ghat gaya**:

```
             faisle ke waqt   2026-09-01   2026-09-03   2026-09-04
rule-block        1359           1327         1326         1303
page-only         1051 (77%)     1051 (79%)   1050 (79%)   1049 (81%)
agree               76             86           86           77
disagree           232            190          190          177
scope mein         308            276          276          254
```

> **09-03 ki subah:** rule-block aur page-only ek-ek kam, `scope` 276 par barabar.
>
> ### ⚠ 09-04 KO SCOPE 276 → 254 GIR GAYA, AUR YEHI IS PAGE KA ASAL MAZMOON HAI
> Wajah na-kaami nahi, **kaamyabi** hai: 09-03 ke teen kaam (item 8 ka tail, `body`,
> `.tag`) un rules ko `99-legacy/` se nikal le gaye, is liye wo `disagree`/`agree` se bhi
> nikal gayin. **Magar do adad saath saath badle aur ye tanasub kaam ke KHILAF hai:**
>
> ```
> 09-03 subah   legacy 1706   scope 276   →  1706 − 276 = 1430   (target se 30 door)
> 09-04 subah   legacy 1697   scope 254   →  1697 − 254 = 1443   (target se 43 door)
> ```
>
> **Din bhar ke teen kaam ne legacy sirf 9 lines ghatai magar scope 22 ghata di — yani
> target QAREEB nahi, DOOR hua.** Ye har us kaam par dobara hoga jo rules ko legacy se
> nikalta hai, kyunke nikli hui rule apni lines apne saath le jati hai magar scope se
> apne se ZYADA hissa kaat ti hai (rule-block lines 1326 → 1303 = 23, jab ke legacy 9).
>
> **Natija saaf hai aur ise chhupana nahi chahiye: `~1400` scope ke andar reh kar KABHI
> nahi aayega, aur har guzarte kaam ke saath faasla barhega.** §5 ka faisla 2026-08-31 ko
> us waqt liya gaya tha jab scope **308** tha; wo bunyaad ab mojood nahi. Teen raaste
> `DECISIONS-FOR-IRFAN.md` §7 mein likhe hain — **ye faisla Irfan ka hai, aur is se pehle
> koi aur CSS drain shuru karna waqt zaya karna hai.**

**`1706 − 276 = 1430`** — yani sirf rules delete karne se **1400 nahi aata, ~30 lines
reh jati hain.** *(09-04: aur ye adad khud bhi ummeed-afza tha — asal hisaab neeche.)* Ye na-kaami nahi hai aur target badalne ki wajah bhi nahi: `legacy_css_lines`
**1706** poori file ginta hai, jab ke audit ka **1326** sirf rule-block lines hai — beech ka
farq comments, blank lines aur `@media` ke bracket hain, **jo apni rules ke saath khud
jate hain** (UI-073 mein 34 rule-lines ke saath 8 comment-lines bhi gayin, magar naye
comment 6 wapas aaye). Yani 1400 **ban sakta hai, magar khud-ba-khud nahi**.

### ✅ 2026-09-04 — NAZAR-E-SANI HO GAYI. NAYA TARGET `~1500`, AUR YE NAAPA HUA HAI

Ooper ka poora andesha durust nikla, aur us ka jawab `DECISIONS-FOR-IRFAN.md` §7 mein
hai: **A — target par nazar-e-sani**. Naya adad andaze se nahi, **09-03 ke apne kaam se
nikle model** se bana:

```
09-03:  rule lines nikleen     −23
        pointer comments aaye  +14
        legacy ka asal farq     −9      aur 1706 − 23 + 14 = 1697  ✓
```

**Har nikli hui rule apne peechhe ~0.6 comment line chhorti hai** — `/* X: 05-components/… */`
likhna parta hai aur counter use ginta hai. Bacha hua scope **254 lines, 100 rules** mein:

```
abhi           1697
agree ka kaam   −47   (77 lines, ~30 comment wapas)   → ~1650  ← checkpoint
disagree ka    −147   (177 lines, ~30 comment wapas)  → ~1500  ← target
```

**`~1650` checkpoint hai, target nahi:** wahan tak **koi naya faisla darkar nahi**. Us se
aage ke ~150 lines ke liye **taqreeban 50 aur faisle Irfan se lene parenge** — `disagree`
ke 50 rules, aur item 8 ka poora tail un mein se sirf **teen** tha. Ye qeemat pehle se
likhi ja rahi hai.

⚠ **Ye model EK naape hue din par khara hai.** Agla kaam khatam ho to tanasub dobara
naapo; 0.6 se bahut alag nikle to adad phir dekhna hoga — **magar ab tareeqa mojood hai,
sirf number badlega.**

**Agla CSS kaam: `agree` wale rules.** Pehla batch 2026-09-04 ko ho gaya (UI-079):
`.slo-main` → `04-objects/slo-main.css`, `.empty-state` + `.card .hint` →
`05-components/empty.css`. **Gate: 0 deltas** (das pages × paanch viewports).
`legacy_css_lines` **1697 → 1695**, scope **254 → 248**. Baqi `agree`: **71 lines**.

### ⚠ 2026-09-04 SHAAM — TARGET KA MODEL USI DIN GHALAT SABIT HUA, AUR GHALTI MERI THI

Subah ka model kehta tha "har rule ~0.6 comment line chhorti hai", **magar phir main ne
us ka ULTA istemal kar liya**: `agree` ke 77 lines par sirf ~30 comment gine (yani 0.39
rate) aur 47 lines ki bachat likh di. **Agar 0.6 sach hai to 77 lines par ~46 comment
aate hain aur bachat 31 hoti hai.** Do naape hue din ab ye kehte hain:

```
09-03   rule-block −23   legacy −9    bachat ka tanasub 0.39
09-04   rule-block  −6   legacy −2    bachat ka tanasub 0.33
```

Dono ~0.35 par hain, 0.61 par nahi. **Durust peshgoi:**

```
abhi                1695
agree ka baqi kaam   −25   (71 lines × 0.35)   → ~1670
disagree ka kaam     −62   (177 lines × 0.35)  → ~1608
```

**Yani asal farsh `~1600` hai, `~1500` nahi.** ⚠ **Magar target dobara badalne se pehle
ye samjhein: asal lever target nahi, POINTER COMMENT ki policy hai.** Wo 0.65 lines jo
har rule ke peechhe reh jati hain, **hamari apni likhi hui hain** — `/* X: 05-components/… */`.
Agar legacy mein pointer comment likhna band kar dein to tanasub 1.0 ho jata hai aur
`1695 − 248 = 1447` — yani `~1450`, jo `~1400` ke qareeb hai.

**✅ FAISLA: (b) — Irfan, 2026-09-04, aur usi din laagu.** `99-legacy/` mein pointer
comment likhna **band**. Qaida ab `CLAUDE.md` **§11.1** mein hai — wahan se parho, yahan
se nahi, kyunke wo har CSS task par lagta hai aur ye page ek din ka khulasa hai.

**Purane 39 pointers usi din delete kiye gaye** (jo sirf pata dete thay). **`legacy_css_lines`
1695 → 1629**, `unsanctioned_hex` 300 par barqarar, aur **`css_type_probe` par 0 deltas** —
das pages × paanch viewports — yani wo 66 lines sirf wazan thin, koi rule nahi gayi.
**Teen comment jaan-boojh kar chhore gaye** kyunke un mein pate ke ilawa naapi hui baat
thi (*"its compact look was dead — D43"*, *"chaaron declarations zinda thin"*) — wo
maloomat hai, pointer nahi.

**Naya faasla, aur ab tanasub 1.0 hai:**

```
abhi                1629
agree ka baqi kaam   −71   → ~1558
disagree ka kaam    −177   → ~1381
```

### 2026-09-04 — `agree` ka doosra batch (UI-081), aur `agree` ki asal hadd

Uthaye gaye: `.btn-danger` + `:hover`, `.btn-edit` (base), `.modal-overlay` (band halat),
`.modal-header h3`, `.strip-filter input`. **Gate: 0 deltas** (das pages × paanch
viewports). `legacy_css_lines` **1629 → 1593**, `unsanctioned_hex` **300 → 298** (do hex
ka dohraav khatam). `agree` ab **71 → 36 lines**.

**Jo saath NAHI aaya, aur har ek ki wajah naapi hui hai:**

| kya | kyun ruka |
|---|---|
| `.btn-edit:hover` | bank aur library par do alag soortein — audit ne bhi `agree` mein nahi rakha |
| `.modal-overlay` ka khulne wala selector | index `[data-open="1"]`, library `.open` — do alag hooks |
| `.app-nav` (5 files) | **D64** — index aur print par markup hai magar rule nahi; un ka `padding-left` 0px hai, baqi paanch ka 10px |
| `.row` (3 files) | **D63** — index ka rule `flex-wrap` declare hi nahi karta |
| `input[type=text/number]` | **D51** — ye teen properties layer upar le jane par CHHE pages tor chuki hain, 2026-08-27 ko naapa gaya |
| `label` / `label:first-of-type` | abhi nahi kiya. Chaar pages par zinda (`margin-top` 14px), magar `print` par 11 label hain jin ke paas ye rule nahi — apna gate maangta hai |
| `html, body { height: 100% }` | **abhi tak naapa nahi gaya** (board ye pehle se kehta hai) |

### ⚠ `AGREE` KA MATLAB "MEHFOOZ" NAHI HAI — YE AAJ TEEN DAFA SABIT HUA

Audit ka `agree` sirf itna kehta hai ke **jin files mein rule MOJOOD hai wo aapas mein
muttafiq hain.** Wo ye nahi dekhta ke **kisi aur page par MARKUP mojood hai magar rule
nahi** — aur wahi page component aate hi badal jata hai. Ek hi din mein isi sawal se
teen cheezein ruki: `.row` (D63), `.app-nav` (D64), aur `.card .hint` ka murda margin
(UI-079). **Is liye ab har selector par `css_selector_probe` das ke das pages par chalao,
chahe audit us ko `agree` hi kyun na kahe.**

⚠ **Aur `css_selector_probe` ki apni ek hadd hai jo aaj pakri gayi: wo sirf PEHLA element
parhta hai** (`getComputedStyle(els[0])`). `label` par is ne `margin-top: 0px` dikhaya
aur ye "murda hai" wala ghalat natija de raha tha — kyunke pehla `label` hamesha
`label:first-of-type` hota hai, jis par 0 durust hai. `label:not(:first-of-type)` se
naapne par asal qadr **14px** nikli. **Jab ek selector ke kai elements hon aur un mein
farq mumkin ho, alag selector se dobara naapo.** (`PROBES.md` rule 12.)

Yani **`~1400` ab pahunch mein wapas aa gaya hai** — magar wo poora scope khatam karne
par, jis ke liye `disagree` ke ~50 faisle darkar hain. **Target `~1450` par rakha gaya
hai** (§7), jo `agree` khatam + `disagree` ka aadha hissa hai.

**Agle session ka kaam:** item 8 + `.tag` + `body` ka tail lo, phir **dobara naapo aur ye
number board par likho.** Agar tab bhi faasla bache to **Irfan ko wajah ke saath batao** —
chupke se target mat badalna.

> **09-01 ka asar chhota tha:** UI-074 ne ek murda rule li — `legacy_css_lines` 1707 →
> **1706**, `unsanctioned_hex` 301 → **300**. Deleted rule `page-only` thi, is liye
> **scope 276 par jyun ka tyun hai** aur faasla ab bhi **~30 lines** ka hai.

**Aur jo bilkul na karna ho:** `master` merge item 9 se pehle.

---

## ▶ NEXT SESSION — START HERE (2026-08-28)

**ITEMS 1–7 ARE DONE, AND ITEM 8 HAS BEEN SURVEYED — IT IS NOT WHAT ITS ROW SAYS.**

The row calls `other` "134 lines, 15 rules, nobody has read them, unknown". Read on
2026-08-29: **128 of those 134 lines are ONE selector, `:root`, in all nine legacy
files.** The rest is three rules totalling six lines (`.options-grid`, `.strip-empty`,
`.list-empty`).

Of the 150 tokens those `:root` blocks declared, **44 were dead and UI-072 deleted them**
(0 deltas on all ten pages). **The 106 that remain are not a family and cannot be
drained as one** — each one leaves when its last consumer leaves, which makes them the
drain's terminal state, not a session. **That is also why the target arithmetic stopped
closing**: those lines were being counted as available work.

**So what is actually left of item 8 is six lines in three rules.** Take them with
whatever tail work remains; there is no survey session to run and no 3–5 sessions to
schedule.

Three things any remaining session must still fold in:

* **Add `body` to the survey — 38 lines across six files.** The audit's family regex files
  it under `shell/nav`, which is ticked ✅, so **no row schedules it.** After `other` it is
  the largest single `disagree` item in the repo.
* **`.slo-main` / `.empty-state` are filed under `chip/pill/row`** and are neither. Expect
  more of this: the labels are as unreliable as the counts.
* **`scripts/css_inject_probe.mjs` exists now (PROBES.md rule 10).** Before scheduling any
  family out of `other`, check whether it is JS-built — three of item 7's four were, and
  both snapshot probes report 0 deltas on those whether the CSS is right or wrong.

⚠ **Item 7 was split into two sessions because four families and five decisions in one
diff breaks the project's own reviewability rule. That split was right and should be the
default for any multi-family row.**

⚠ **The census lesson has now fired THREE sessions running, and item 7 is four families
in one row — the highest-risk shape yet for it.** Item 5's "58 lines, 5 files" missed an
eighth modal (page-only). Item 6's `card` said "6 files" and was **eight** — two of them
were page-scoped copies in `pages/*.css`, which `css_duplication_audit.py` cannot see
because it reads `99-legacy/` only. Its `brand` bucket made the opposite error and counted
**too much**: `landing`'s `.brand` is a hero block in a gradient header, not a sidebar
brand at all. **Count the thing in the MARKUP, and check `pages/*.css` as well as
`99-legacy/`, before trusting the bucket.**

⚠ **And `btn` is the one family card.css's header explicitly says is NOT safe yet** — see
its closing line. `slo.html` has two live `class="btn"` buttons and a bare `.btn` in
layer(components) would take them. Read that note before planning item 7.

## UI-071 — item 7, doosra nisf: `shortfall` + `chip/pill/row`. **2026-08-29. Item 7 mukammal.**

`legacy_css_lines` **1757 → 1751**, hex **333** (nahi hila). 1075 pass, ruff saaf, frozen
yaksan. Type **36**, state **0**, **injection probe 0**. Tafseel `PROGRESS.md` 2026-08-29.

⚠ **PEHLE YE MALOOM HUA KE IS NISF KA ZYADA HISSA NAAPA HI NAHI JA SAKTA.** 31 lines mein
se **26** aisi thin jin ko koi probe dekh hi nahi sakta — `.shortfall-panel`, `.pill`,
`.chips` teeno **JS se bante hain**, to dono gates un par har haal mein 0 deltas dete hain.
D45 wali shakal, aur **D12 ise 2026-07-28 se darj kar rahi thi**. Irfan: harness banao.

**`scripts/css_inject_probe.mjs` — naya gate, `PROBES.md` rule 10.** Har khandan ka apna
builder-markup asal container mein daal kar naapta hai; output `css_type_probe` ki shakal ka
hai to `css_type_diff` bina tabdeeli ke parhta hai.

**Us ka pehla nateeja:** `shortfall` ki chhe rules `layer(legacy)` se `layer(components)`
gayin aur **blueprint/print par 0 deltas** — ye saboot koi maujooda gate de hi nahi sakta tha.

**Irfan ke faisle:** shortfall ke do dabbe alag rahenge, sirf chhe andar wale rules component
par. `.chips` → `taqseem` par `.col-chips`. *(`.pill` → `.sum-pill` maine khud kiya, poochha
nahi tha — `.chips` wala usool laga diya. Ulta kiya ja sakta hai.)*

⚠ **Aur jo wajah pehle di gayi thi wo ghalat thi:** "print chhapta hai, amber toner kharch
karta hai" — panel `no-print` hai, **kabhi chhapta hi nahi**. Irfan ko durust haqeeqat par
faisla dobara diya gaya, aur wo wohi raha.

⚠ **Review ne naye gate ko FAIL kiya aur theek kiya** — teen fixtures pehle hi din ghalat
thay (`index` ka container `.pill` ki asal jagah nahi thi; `taqseem` ke bachche `.tag` thay
jab ke asal `.chip` hain). **Jo fixture resolve ho jaye zaroori nahi ke wafadar ho.**

⚠ **Ratchet PAANCHWEEN dafa upar gaya** (1751 → 1755), phir comment se. **Hal ab likha hua
hai: legacy mein wajah rule ki line ke AAKHIR mein daalo, upar alag line par nahi** — wajah
bhi darj rehti hai aur metric nahi hilta.

⬜ **Browser check nahi hua.**

## UI-070 — item 7, pehla nisf: `btn` + `page-head`. **2026-08-28.**

`legacy_css_lines` **1759 → 1757**, hex **334 → 333**. 1075 pass, ruff saaf. Type 2543,
state **1530 — jin mein 1050 `cursor: pointer → not-allowed`**. Frozen inventory yaksan.
Tafseel `PROGRESS.md` 2026-08-28.

**D49 ka nateeja ship hua.** `forms.css` ko `button:disabled { cursor: not-allowed }` mila
— usi file mein, kyunke jise harana tha (`button { cursor: pointer }`) wo teen satar upar
hai; ek hi layer, `(0,1,1)` banaam `(0,0,1)`. UI-063 ka faisla **pehli dafa render hua**.
⚠ Magar "har disabled button" ghalat lafz hai: `layer(components)` ka bare-class
`cursor: pointer` ise harata hai. `btn.css`:380 `.btn-cancel` aur `pages/print.css`:291
`.ps-range-all` ke apne `:disabled` nahi hain — aaj dono kabhi disabled hote hi nahi.

**`.btn-danger`/`.btn-edit` `bank` ki size par.** ⚠ **Faisla pehle GHALAT ginti par diya
gaya tha.** Maine markup gina — ek-ek — magar ye buttons **JS se bante hain**: probe kehta
hai `bank` 459, `library` 24. Sahi ginti par faisla ulat gaya. **Markup ginna kaafi nahi
jab markup JS banata ho (D12); `n` probe se lo.**

**`.page-head` → `.pagehead`, saaton pages ab ek jaise**, aur `.page-head` ab kahin nahi.
⚠ **Pehli koshish tori thi:** `.pagehead` `display:flex` hai aur maujooda chaar pages apne
`h1`+`p` ko ek `<div>` mein lapetate hain. Bina wrapper ke `slo-health` ka h1 do lines par
gaya aur us ka teesra child `#draftNote` dab gaya. **Warning un chaar pages ke MARKUP
comment mein pehle se likhi thi — maine CSS parhi, markup ka comment nahi.** Ab teeno nayi
pages par bhi wohi comment hai.

**`card.css` ka teesra basi dawa theek** — `.pagehead` "0 matches, measured" jab ke wo
chaar pages par live tha. **UI-068 ne isi header ke do dawe theek kiye thay aur yehi
chhod diya.** Sabaq: ek jumla ghalat mile to poora block parho.

**D47(a) band** — `forms.css` ka jhoota focus comment durust. **D47(b) khuli hai.**

⚠ **Ratchet CHAUTHI dafa upar gaya** (1759 → 1760) mere comment se, aur usi comment mein
**doosri dafa** ek raw hex tha. Dono theek; magar ye qaida ab **saat** dafa fail ho chuka
hai aur **har dafa comment ke zariye**.

⬜ **Browser check nahi hua.**

**The whole remaining plan — both tracks, all six sessions, and when each deferred row is
due — is `docs/ui/ROADMAP.md` → "📋 THE PLAN FROM HERE", settled 2026-08-27.** Read that
before planning anything; it is newer than everything above it in that file.

**Current numbers, measured 2026-08-29 after UI-072** — re-measure, do not quote:
`legacy_css_lines` **1,732** · `unsanctioned_hex` **308** · unresolved `var()` **0**.

⚠ **THE TARGET IS NO LONGER ~1,350 AND NOBODY HAS PICKED THE NEW ONE.** The full audit ran
2026-08-28: available work is measured on rule-block lines (1,398) while `legacy_css_lines`
counts every line (1,759), and the 361-line remainder — `:root` blocks, `@media` wrappers,
comments — is not something the drain removes. So **1,759 − 351 = 1,408**, and that floor
rises every session. **Three findings, all in `ROADMAP.md`'s re-measure block and
`PROGRESS.md` 2026-08-28:** the target arithmetic no longer closes; **156 of the 351 lines
sit in families the board already ticks ✅** (a tick means the decision was taken, not that
the lines went); and the audit's own family labels can be wrong — **`body`, 38 lines across
six files, is filed under `shell/nav` and is scheduled by nothing.**

## UI-068/069 — `card` + `brand`. **2026-08-28. Item 6. Ek commit, do families.**

`legacy_css_lines` **1798 → 1759 (−39)**, hex **338 → 334**. 1075 pass, ruff saaf.
Type probe 1284 (card) + 297 (brand), state probe **0**. Frozen inventory das pages par
yaksan. Tafseel `PROGRESS.md` 2026-08-28.

**Irfan ke teen faisle:** card = naye tree ki qeematein (`--radius-container`,
`--shadow-card`, `--space-gap`) · sidebar subtitle = `--color-sidebar-fg-muted` ·
taqseem ka brand shared values qubool kare (divider gaya).

⚠ **`card.css` ka header teen hafte se ghalat tha aur khud ko theek nahi kar sakta tha.**
Wo kehta tha *"13 elements — slo 3, slo-health 6, library 4, measured 2026-08-08"*, aur
usi jumle ki bina par bare `.card` rule ko rok rakha tha. Asal adad **46 markup mein / 42
DOM mein** (farq index ke chaar JS-template cards ka). **Jab dekhne se rokne ki wajah aur
adad ek hi paragraph mein likhe hon, to adad kabhi theek nahi hota.**

**Do bug naap kar nikle, dono pehle se maujood:**
1. **`print` ka brand navy kinare se chipka tha — padding 0**, saat sidebar pages mein
   akela. UI-065 ne `.app-sidebar { padding: 24px 18px }` hataya, `.brand` ko badal mein
   kuch na mila. `sidenav__brand` dene se theek.
2. **Sidebar ka subtitle chhe pages par slate-500 tha, navy par — ~3.1:1, AA se neeche.**
   Wajah legacy nahi thi: `03-elements/typography.css:88` ka bare `small { color }`
   layer(elements) mein jeet raha tha. Purana note kehta tha legacy "dead" hai — sach —
   **magar us ne kabhi nahi poochha ke JEETA KAUN.**

**D51 phir teen dafa:** bare `.card` ko component mein rakhne se `bank` ki
`.add-q-collapse` / `.bp-card` / `.bulk-card` aur `index` ki `@media(760)` padding sab
haar rahi thin — naap kar `pages/*.css` mein uthai gayin. Probe mein `padding` ka ek bhi
delta na aana hi is ka saboot hai.

⚠ **Ratchet is dafa upar NAHI gaya** (chauthi dafa se bacha). Magar review ne pakda ke
maine `nav.css` ke comment mein ek hex likh diya tha **aur usi paragraph mein likha tha
"no hex is spelled here"**. `99-legacy/print.css` phir bhi **+1 line** hai — waahid legacy
file jo barhi.

✅ **BROWSER CHECK HO GAYA — Irfan, 2026-08-28. Teen session ke baad pehli dafa ye khana
bhara hua hai.** Saaton item dekhe gaye aur sab theek: cards ka naya border rang
(`bank`, `slo-health`), kone 14→16px, `index` ke cards ka naya 22px faasla, `print` ka
sidebar (ab 22px inset — wo bug jo UI-065 se chala aa raha tha), `taqseem` ka brand
(divider gaya), subtitle ka rang (`library`), aur `landing`/`blueprint` par kuch na hilna.

**Is se D55 ka nisf tay ho gaya:** border ka rang badalna **defect nahi hai**, Irfan ne
dekh kar qubool kiya. Row khuli rehti hai magar ab wo *"cards toot gaye"* nahi balki
*"poori app mein do border rang hain"* wali consistency row hai — aur agla khandan jo
component par aayega wohi seam phir dikhayega.

**Do cheezein jaan-boojh kar chhori gayin:** `print` ka brand ab bhi 18px/700 hai (us ke
markup mein `.name` element hai hi nahi — qeemat ka faisla, poochha nahi gaya), aur
`.card-title` ki teen qeematein abhi ek nahi ki gayin (index 600/15/6px vs teen pages
700/14.5/16px — chautha faisla jo is row mein nahi tha).

**Naye rows: D54** (`--space-inset` "card / panel padding" kehta hai magar 24px hai, jab
ke har card 22px padta hai) · **D55** (do border rang) · **D56** (`plan.html` kisi probe
ki page list mein nahi) · **D57** (`brand.js` `print`/`plan` tak pohanchta hi nahi) ·
**D58** (do comments ek doosre ke ulat cascade ka dawa karte hain).

## UI-067 — `modal`. **2026-08-28. Item 5. Teen system rehne diye, shakal ek kar di.**

`legacy_css_lines` **1799 → 1798**, hex **338** (nahi hila — is family mein sab `rgba()` tha).
1075 pass, ruff saaf. Type 220 deltas, state 30 — har ek maqsood. `PROGRESS.md` 2026-08-28.

**Irfan, 2026-08-28: class names mat chhero, qeematein ek karo.** Naam badalne se paanch
pages ka markup aur JS chhoona parta aur **ek line CSS kam na hoti**; jo nazar aata hai wo
shakal aur rang hai.

⚠ **Audit ka adad ghalat tha: sat nahi, AATH modals hain.** Row kehti thi "58 lines, 5
files". Markup se ginne par **chaar wrapper naam** nikle, aur aathwan modal — `print` ka
`.lib-picker-overlay` library picker — **kisi bucket mein tha hi nahi**, kyunke wo page-only
hai. Use chhorna faisle ko adhoora chhorta. **Bucket par nahi, markup par gino.**

**Ek sawal ka jawab pehle se maujood tha:** `theme.css`:183 `--radius-container` khud kehta
hai *"cards, panels, modals"* — 16px. Radius naya faisla nahi, ek **be-istemal role** tha.
Chhe radii (10/12/12/14/16/`var(--radius)`) ab ek.

Do naye token: `--color-scrim` (Irfan: navy .45; channels `--slate-900` ke, library ke
`rgba(22,33,58,.45)` ke nahi — teesri navy banana wohi drift hai) aur `--shadow-modal`
(paanch shadow ki jagah ek).

**Naapa gaya:** `library` 90, `print` 60, `bank` 40, `index` 20, `taqseem` 10; `slo`,
`slo-health`, `blueprint`, `landing` par **0** — un par modal hai hi nahi. `index` aur
`taqseem` par radius delta nahi aaya kyunke wo dono pehle se 16px thay.

⚠ **Ratchet phir upar gaya (1799 → 1800), phir legacy comments se. TEESRI DAFA.**

⬜ **Browser check nahi hua.** Koi modal khol kar: peechay ka andhera, kone (16px — `bank`
12 se aur `print` 10 se aaye hain), aur `print` ka library picker.

⚠ **Four things this week established that the next session should not re-learn:**

1. **Measure the ratchet against `HEAD`, not `BASELINE.json`** — that file is 30+ lines stale.
2. **`css_type_probe` now reads five width bands** and prints any unobserved band every run.
   A delta keyed `@700`/`@520` is a narrow-width one.
3. **Do not write long comments into `99-legacy/*.css`.** `legacy_css_lines` counts every
   line, comments included — UI-065's first draft made the number go **up** while deleting
   rules, **and UI-066 did it again** (1,806 → 1,821 while deleting rules). Twice in two
   sessions. Reasoning belongs in `PROGRESS.md`; the CSS gets a one-line pointer.
4. **A rule cannot simply move UP a layer.** UI-066 lifted three live declarations into
   `layer(elements)` and broke six pages, because every compact override in this app sits in
   `layer(legacy)` and loses to anything above it whatever its specificity. **Before moving a
   rule up, ask what in legacy was overriding it.** D51.

**Still open:** **D47** (`forms.css` — lying comment + ring-vs-glow decision), **D49** (no
gate can see `cursor`), **D48**, **D50**, **D51**, **D52**. None blocks item 5.

## UI-066 — `field/filter` disagree. **2026-08-27. Item 4. 59 lines mein se 12 zinda thin.**

`legacy_css_lines` **1806 → 1799 (−7)**, hex 347 → **338 (−9)**. 1075 pass, ruff saaf.
Tafseel `PROGRESS.md` 2026-08-27.

**Row ka sawal — "which control sizing wins" — adhoora tha.** Teen sizing chal rahi thin,
magar un ki **saat properties har jagah pehle se murda** thin: `forms.css` (layer `elements`)
unhi controls par wo saat khud declare karta hai aur legacy sab se kamzor layer hai. Zinda
sirf **`width`, `min-height`, `margin-top`** thin. `slo`:35 to poori tarah murda thi.
Irfan: **44px / 6px, aksariyat wali.**

**Do sooraakh naap kar nikle.** `index` ke **11 inputs par `type` attribute hai hi nahi** aur
`forms.css` ka selector list attribute par hai — un ko bare `input, select` paint kar rahi
thi, aur us rule ko delete karna unhein UA default par gira deta. `forms.css`:53 ab
`input:not([type])` + `input[type="email"]` bhi bulata hai. Doosra: **file inputs us set se
bahar hain**, to `library`/`index`/`slo` par unhein apni box rule mili.

⚠ **Aur pehla draft chhe pages tor raha tha.** Teen zinda properties `forms.css` mein rakhne
se `bank` `.opt-input-wrap` 38→44px (16 elements) aur `.float-bar` 34→44px, `blueprint` ke
filter controls 38/36→44px, `print` ke modal controls 0→44px aur width auto→100%,
`slo-health` ke selects 157→903px. **Chaar us family mein the hi nahi.** Wajah: har compact
override khud legacy mein hai. Teenon wapas per-page legacy mein gayin — **D51**.

**Naapa gaya:** sirf `index` (1350), `slo` (162), `library` (150) hile; `bank`, `blueprint`,
`print`, `taqseem`, `slo-health`, `landing` par **0 / 0**, dono probe.

⚠ **Review ne chaar defect nikale.** Pehla: `index` ka `#accentColor` (`input[type="color"]`,
`forms.css` se bahar) be-libaas ho gaya tha. **[2026-08-28 durusti: yahan likha tha ke probe
ne is par 0 delta diya aur koi gate pakad nahi sakta tha — ghalat. Probe ne 30 deltas diye
the; `css_type_diff.mjs`:42 ka `LIST_CAP = 60` sirf chhapi hui list kaatta hai, count nahi.
Dekho D53.]** Doosra: `slo` par `margin-top: 6px`
ki koi buniyad nahi thi — us page par **ek bhi `<label>` nahi** aur us ka `.row` centred flex
hai. Teesra: untyped inputs gyarah nahi **baara** hain (baarhwan JS template literal mein,
yani probe se bhi bahar). Chautha: is commit ne `forms.css` mein 45 lines joreen aur **chhe
files ke line refs** khisak diye. Chaaron band.

⬜ **Browser check nahi hua** — extension phir connect nahi hui. Dekhna hai: `index` ke
fields (ab 44px/13.5px), `slo` ke selects (40 → 44px) aur file input, `library` ke teen file
inputs, aur **D52** ke teen checkbox.

---

## UI-065 — shell/nav. **2026-08-27. Item 3. Ek shell — aur do hafte purana bug mila.**

`legacy_css_lines` **1841 → 1806 (−35)**, hex 349 → 347. 1075 pass, ruff saaf.
Tafseel `PROGRESS.md` 2026-08-27.

**ROADMAP ki row ghalat thi.** *"Three navies"* — nahi. Saaton page `rgb(22,41,74)` paint
karte hain; teen **hijje**, aik rang. Asal faisla ye tha ke `taqseem` aur `print` component
par aayen ya nahi. Irfan: **aayen.**

**Aur us ne aik purana bug pakda, jo is task ka asal nateeja hai.** `nav.css` mein koi
`@media` tha hi nahi aur `legacy` **sab se kamzor layer** hai — to har page ka apna collapse
rule component se harta tha. **700px par, kisi tabdeeli se pehle:** paanch component pages
248px sticky (**toota**), `taqseem`/`print` 700px static (theek). Yani wohi do theek thay jo
component par nahi thay. **Har gate se guzarta raha kyunke har probe 1280 par chalta tha —
UI-064 isi liye pehle aaya.** Jad se theek: `nav.css` ka apna `@media (max-width:760px)`.

**Naapa gaya: desktop (1280/900) par sirf `print` (74) aur `taqseem` (11)** — yani wohi do
manzoor-shuda move. Baqi saat par **sifar**. Narrow bands par collapse ka fix.

**Do slip, shipping se pehle naap kar pakdi gayin:** pehla `@media` `.sidenav` par tha aur
`blueprint` ko tor raha tha (wo `o-shell__nav sidenav` carry karta hai — wohi nav, magar top
bar) → ab `.sidenav__panel .sidenav`; aur `.brand` do dafa ghalat delete hui (dono jagah
element maujood hai, aur brand **item 6** ki family hai).

## ▶ previous entry (2026-08-26)

**The ordered finishing plan is `docs/ui/ROADMAP.md` → "⛳ THE FINISHING PLAN".** Nine items,
one family per session.

**Item 1 (the button task) is DONE — it shipped as UI-063 on 2026-08-26. Take item 2.**

⚠ **But read this before crossing item 1 off in your head, because it did not land whole:**

* **D44 and D46 are closed. D47 is NOT**, and `ROADMAP.md`:229 scopes item 1 as
  "D44 + D46 + **D47(b)**". `forms.css` was never touched. **Item 1 is two thirds done**, and
  review found that, not a gate. Either finish D47 first or re-scope the row honestly — do not
  let it sit closed-looking and open.
* **A third of the decision is unverified.** `cursor: not-allowed` produced **zero deltas**,
  and a control proved the gate cannot see `cursor` under `:disabled` at all. **D49.**
* **The claim was too strong.** "Every filled legacy button" is really every filled
  *light-surface action* button. Carve-outs: the on-dark family (**D48**, and it still hovers
  in the opposite direction) and two navy-filled segmented controls (**D50**).

**Item 2 is the viewport pass, and it is a tooling task, not a drain.** `shell/nav`'s 23
`agree` lines are six `@media (max-width: 720/760px)` rules and **every probe in this repo runs
at 1280×900**, so no gate can see them. That is D45's shape exactly. Item 3 (`shell/nav`, 99
lines, the biggest family) is blind without it.

**Copy-pasteable prompt for that session** (`CLAUDE.md` §12.8):

> Take **item 2** of `docs/ui/ROADMAP.md`'s "⛳ THE FINISHING PLAN" — the viewport pass. Add a
> second viewport to `css_type_probe.mjs` and `css_state_probe.mjs` so the six `@media`
> rules in `shell/nav` are measurable before item 3 touches them. Read `CLAUDE.md` §11–12 and
> this file's UI-065 and UI-063 sections first. **Prove it by control the way UI-065 did** —
> mutate one rule that only applies below the breakpoint and show the old probe returns 0 and
> the new one returns 1. **Change no page CSS**; this is an instrument, and the ratchet should
> not move.

**Gates for every session from here:** `pytest` (1075) · `ruff` · `css_baseline.py` (ratchet
never rises) · `css_type_probe` + **`css_state_probe`** before/after · review agent, one round
· Irfan's browser · then commit. Never push.

⚠ **MEASURE THE RATCHET AGAINST `HEAD`, NOT AGAINST `BASELINE.json`.** UI-063 was first
reported as `−32` legacy lines and `−7` hex. Its real effect is **`−1` line and zero net hex**;
the rest was pre-existing drift against a baseline file that is **31 lines stale**. Diffing
against a stale number and booking the difference as your result looks exactly like success.

**Current numbers, measured 2026-08-26** — re-measure, do not quote these:
`legacy_css_lines` **1,841** · `unsanctioned_hex` **349** · agree **68** / disagree **422**
lines remaining · target **~1,350**.

**Branch:** `feat/ui-architecture` · **Baseline tag:** `ui-baseline`
**Last updated:** 2026-08-13 (**UI-047c — 9 OF 9 PAGES, and `static/theme.css` is DELETED.**)
— **every page is on the new tree and none is HELD.** Sprint 3 closed incomplete at 3 of 9;
seven migrations opened the other six, four of them on 2026-08-12/13.

> ### ⚠ 2026-08-21 — IS FILE KE ADAD 2026-08-13 KE HAIN, AAJ KE NAHI
>
> Neeche ka poora board us din likha gaya tha. Us ke baad kaam hua magar yahan darj
> nahi hua, to **kai adad ab ghalat hain.** Aaj naape gaye:
>
> | metric | is file mein | asal (2026-08-21) |
> |---|---|---|
> | `legacy_css_lines` | 2,115 ("has not moved a line") | **1,875** (−240) |
> | `unsanctioned_hex` | 429 → 400 | **356** |
> | `total_css_lines` | — | **1,875** |
> | `inline_style_attrs` | 466 | **466** (Sprint 5 abhi chhua nahi gaya) |
>
> **Kisi bhi adad par kaam shuru karne se pehle `python scripts/css_baseline.py`
> chalayen.** Is epic mein purane adad par bharosa karna baar baar mehnga para hai —
> `ROADMAP.md` ki P0 rows bhi isi tarah mahinon jhooti khuli pari rahin.
>
> **Jo ab bhi sach hai:** NEXT TASK Sprint 6 (the drain) hi hai, 9 legacy files
> mojood hain, aur Sprint 5 (inline styles) shuru nahi hua.
>
> **Aur ye:** 2026-08-21 ko is branch par 7 commits gaye jo **is epic ke nahi** —
> seeding tool, bloom fix, prompt fix, grade filter, manual essay. Branch ka naam
> `feat/ui-architecture` hai magar us ka mazmoon ab sirf UI nahi raha.

---

## UI-064 — the viewport pass. **2026-08-27. Auzaar, drain nahi — kisi page ka CSS nahi badla.**

Ratchet **1841 → 1841**, 1075 pass, ruff saaf. Tafseel `PROGRESS.md` 2026-08-27.

**Masla:** har probe 1280×900 par chalta tha, aur `static/css/` ki **15 screen `@media`
queries mein se sirf 1** ka mushahida hota tha. Baqi chaar bands mein **14 + 13 + 10 + 2**
rules bilkul be-naapi thin.

**Aadha masla width tha hi nahi:** `flex-direction` media blocks ke andar **22 dafa** aata
hai aur property list mein tha hi nahi — sirf viewport barhane se probe band tak pahunch kar
bhi andha rehta.

**Control (do mutation, `slo` ke 720px block par):** HEAD ka probe **0 / 0**, naya probe
**12 / 72**. Aur us 72 mein se **sirf 2** nayi properties par the — **asal andhapan width
tha**, property list nahi; properties diff ko wajah ka naam dene ke liye hain.

**Naya:** `scripts/css_breakpoints.mjs` — bands nikalta hai aur dono probe **har run mein
apna blind spot khud chhapte hain**. `css_state_probe` jaan-boojh kar 1280 par hai: **kisi
`@media` ke andar aik bhi state rule nahi** (naapa gaya).

**Review ne chaar defect nikale, chaaron band:** 336 MB untracked probe output (ab
gitignored) · flag parsing chup-chaap tootti thi · `keysPerViewport` jaancha nahi jata tha ·
300 ms ki wajah galat likhi thi (asal wajah transitions hai, ab motion band hoti hai).

## UI-063 — the button task. **2026-08-26. D44 + D46 band, D47 nahi. Ek radius, ek disabled.**

`legacy_css_lines` **1842 → 1841** · `unsanctioned_hex` **349 → 349** · **1075 pass**, ruff saaf.
Tafseel `PROGRESS.md` 2026-08-26 par.

**Faisla (Irfan, 2026-08-25):** radius `--radius-control` (11px) · hover ek simt (light-surface
ab **halka**) · disabled `.5` + `not-allowed`.

**Naapa gaya — state probe 1,054 deltas, rest 206, aur sirf teen property hili:**
`border-*-radius` (940/188) · `background-color` (75/15) · `opacity` (39/3). `font-size`,
`padding`, `min-height`, `box-shadow`, `outline-*`, `border-color` — **sifar**. Har chhua hua
selector aik button. `slo-health` / `taqseem` / `landing` par **0** (un ki `--radius-btn` pehle
se mari hui thi).

**Chaar cheezein jo is task se seekhi gayin aur agle session ka rukh badalti hain:**

1. **Ye kaam bina kisi gate ke working tree mein para tha** — na commit, na PROGRESS, na probe.
   Item 1 code ki tarah mukammal tha, darj ki tarah mojood hi nahi. Session ka aakhri qadam
   code nahi, **darj** hai.
2. **Ratchet stale baseline ke khilaf naapa gaya tha** aur `−32`/`−7` is kaam ke naam likh
   diye gaye. Asal `−1` aur **sifar**. `HEAD` ke khilaf naapo.
3. **`cursor` ko koi gate nahi dekhta** — control se sabit, **D49**. Faisle ka teesra hissa
   aaj tak ghair-tasdeeq-shuda hai.
4. **Daira daawe se chhota nikla** — light-surface tak mehdood. **D48** (on-dark, aur wo abhi
   bhi ulti simt mein hover karta hai), **D50** (do navy segmented control).

## UI-065 — state probe (D45 band). **2026-08-25. Auzaar hai, kisi page ka CSS nahi badla.**

`scripts/css_state_probe.mjs` — naya file. **Ye drain nahi, auzaar hai**, aur jaan-boojh kar
drain se pehle banaya gaya. Kisi page ka koi byte nahi badla; ratchet chhua tak nahi.

### Kyun — aur ye control se sabit hua, daawe se nahi

Is repo ka har probe page ko **rest par** parhta tha. Yani `:hover` / `:focus-visible` /
`:disabled` ki koi bhi declaration **0 deltas** deti thi, chahe wo durust ho ya ghalat. Do
task do din mein isi se kate: UI-061 ne chaar pages se `input:focus` delete ki (sabot sirf
layer-order ka istidlal tha), aur UI-062 ne `.btn-cancel:hover` ka grey badal diya aur
**pytest, ruff, ratchet aur 34 measured deltas — sab paas ho gaye.**

**Control, 2026-08-25, `bank` par wohi hover declaration mutate kar ke:**

| probe | deltas |
|---|---|
| `css_type_probe.mjs` (rest), nau ke nau pages | **0** |
| `css_state_probe.mjs`, akela `bank` | **1** — `button.btn-cancel::hover  background-color` |

Dono adad ek hi mutation aur ek hi browser se. Mutation ke baad `btn.css` HEAD ke barabar
restore ho gayi (`git diff --quiet` saaf).

### Do faisle jo is ki qeemat tay karte hain

**1. Ye `css_type_probe` ki bilkul wohi JSON shape likhta hai**, is liye `css_type_diff.mjs`
**bina kisi tabdeeli ke** dono parhta hai — `--names` sameet. Koi naya diff tool seekhna nahi
parta. Keys `<path>::<state>` hain aur `<path>` wala hissa byte-identical hai, to state diff
ka path rest diff mein paste kiya ja sakta hai.

**2. `outline-*` shamil hai — `css_type_probe` mein wo bilkul nahi hai.** Bina us ke probe ring
ka aana, rang badalna ya gayab hona dekh hi nahi sakta.

`:disabled` alag hai: wo forceable flag nahi, **attribute** hai. Set kar ke snapshot liya jata
hai phir bahaal — aur bahaali ka count output mein darj hota hai (`disabledRestored`).

### Review ne pehla version FAIL kiya, aur wo durust tha

Pehle version ne akela `focus-visible` force kiya tha. **`:focus-visible` kisi `:focus` rule
ko match nahi karta**, is liye repo ki har `input:focus` rule — `forms.css`:79 sameet, aur
wohi chaar jo **UI-061 ne delete ki thin** — rest ke barabar naapi gayi. Yani jo auzaar theek
usi sooraakh ke liye bana tha, wo us sooraakh par andha tha. **Koi error nahi aaya, records
poore the — bas sab resting values the.**

Ab focus **do pass** hai: `focus` (akela `:focus` — pointer focus, yehi `forms.css`:79 ko
dekhta hai) aur `focus-visible` (**dono** force — asal tab-stop dono ko match karta hai).

### Jo isi waqt naap kar mila

* **Fields par focus ring `outline` NAHI hai — glow hai.** `select#fSubject` par dono
  pseudo-class force karne se: `border-top-color rgb(14,165,164)`, `box-shadow rgb(220,245,244)
  0 0 0 3px`, aur `outline-style: none`. Wajah: `input:focus` (0,1,1) usi layer mein
  `:focus-visible` (0,1,0) ko harata hai. **`forms.css`:76 ka comment is ka ulta kehta hai** —
  **D47**. Is section ke pehle draft ne "focus ring = `outline: 2px solid`" likha tha; wo
  **buttons ke liye sahi, fields ke liye ghalat** tha.
* **`.btn-save:hover` = indigo-500 jabke rest par indigo-600** — UI-062 mein jo "hover ab
  halka karta hai, gehra nahi" likha gaya tha, wo ab **naapa hua** adad hai.
* **`.btn-cancel:hover` = `rgb(250,251,254)`** — pehli dafa naapa gaya. Wo daawa jo UI-062
  mein "kisi tarah tasdeeq-shuda nahi" darj hua tha, ab band hai.
* **`.btn-save:disabled` opacity `0.6`, `.btn-cancel` ka koi disabled rule hi nahi** (opacity
  1 rehti hai). Ye **D46** ka maal hai aur ab naapne ke qabil.

### Daira — chhota, magar review ke baad teen selector chaura

Interactive elements, **aur `tbody tr`, `.q-row`, `.bp-row`**. Review ne `static/css/` ke
**66** state selectors ginn kar teen **zinda `:hover` rules** dhoondein jo tag list kabhi
pakad hi nahi sakti thi — `tbody tr:hover` (**slo**, ek LIVE gate page), `.q-row:hover`
(bank), `.bp-row:hover` (blueprint). Daira jo zinda rule chhor de wo daira nahi, sooraakh hai.
Asar: `slo` 20 → **135**, `bank` 1,533 → **1,992**, `blueprint` 63 → **65**.

Nau pages, paanch states, **~30 second, 13,100 records, 0 errors**.

⚠ **Pehle yahan "~41 second, 8,112 records" likha tha aur review ne akele `bank` ko 445 second
par naapa.** Dono adad asli the: pehla version har `forcePseudoState` ka alag round-trip
awaited karta tha, aur wo latency par hai — machine ke bojh se das guna oopar neeche. Ab calls
saath bheji jati hain aur ek dafa await hoti hain. Naya adad **zyada states aur zyada elements
ke saath** hai.

⬜ **Ab tak koi baseline commit nahi hui.** Probe maujood hai; agla task (D44) us ka pehla
asal istemaal hoga — us se pehle aur baad mein chalana **laazmi** hai, kyunke wo task poora ka
poora hover aur disabled surfaces par hai.

---

## UI-062 — `modal` family. **2026-08-25. 34 deltas, aur teenon manzoor-shuda.**

**1075 pass** · ruff saaf · `legacy_css_lines` **1864 → 1842 (−22)** · `unsanctioned_hex`
**353 → 349 (−4)** · `css_type_diff`: **bank 13, print 21, baqi saat pages 0**.

**Ye epic ka pehla drain hai jis mein deltas jaan-boojh kar sifar nahi hain.** Har ek naapa
gaya delta `.btn-cancel` ya `.btn-save` par hai. **Chaar cheezein badlin, teen nahi:**

| kya badla | pehle | ab | deltas mein? |
|---|---|---|---|
| `.btn-save` background | `--primary` (navy) | **`--color-action` (indigo)** | haan |
| radius, dono buttons | bank 10px / print 8px | **`--radius-control` (11px)** | haan |
| `.btn-cancel` border | `--border` | **`--color-border`** (halka) | haan |
| **hover, dono buttons** | har page ka apna grey | **ek Tier 2 role** | **nahi — 0 deltas** |

⚠ **Chauthi row pehle likhi hi nahi gayi thi, aur review ne pakdi.** Wajah wohi hai jo use
khatarnak banati hai: `css_type_probe` **rest par** naapta hai, to hover ka koi delta banta hi
nahi. `.btn-cancel:hover` legacy mein `var(--bg)` tha — **bank `#EEF1F6`, print `#F5F7FB`,
yani dono alag** — aur ab dono `--color-surface-sunken` par hain, ek teesri qeemat jo kisi
page par nahi thi. Dono ka mukhtalif hona wohi baat hai jo `modal.css` ke parked note ne
radius ke saath likhi thi, aur ye Irfan ke saamne rakhe gaye faisle ke preview mein shamil
tha. **Magar "teen cheezein badlin" likhna ghalat tha.**

⚠ **Ek nateeja jo faisle mein shamil NAHI tha:** `.btn-save:hover` `--primary-hover` se
`--color-action-hover` par gaya, jo **simt ulat deta hai** — legacy hover par gehra hota tha,
naya halka hota hai (indigo-500 vs indigo-600). Ye action role apnane ka lazmi nateeja hai
aur `.btn--primary:hover` se milta hai, magar ab app mein kuch filled buttons gehre hote hain
aur kuch halke. Ye D44 ke button task ka hissa hai.

`font-size` aur `padding` **bilkul nahi hile** — naap kar tasdeeq hua, aur jaan-boojh kar
aisa rakha gaya (neeche dekhein).

### Ye family `modal.css` 2026-08-16 se park kar rakhi thi, aur wajah durust thi

Us file ka header kehta hai: *"they LOOK identical in both files and are not — bank's
`--radius-btn` is 10px, print's is 8px."* Naapa gaya aur aaj bhi bilkul aisa hi tha. Rule ka
matn dono files mein byte-identical hai; farq sirf is se aata hai ke har page apna token
alag declare karta hai. **Is liye component tab hi ban sakta tha jab ek radius jeete**, aur
wo faisla Irfan ka tha — 2026-08-25, `--radius-control`.

### Asal daryaft: bank par do primary rang saath saath chal rahe the

`.btn-primary` UI-041 mein `--color-action` (indigo `rgb(79,70,229)`) le chuka tha.
`.btn-save` nahi — wo legacy `--primary` (navy `rgb(46,90,172)`) par khada raha. **Yani bank
ek hi screen par do mukhtalif filled action buttons paint kar raha tha**, aur ye kahin darj
nahi tha. Ye D27 ka wohi defect hai. Isi liye rang badalna is task ka **maqsad** hai, koi
side-effect nahi — aur Irfan ne poori tasveer dekh kar chuna.

### Geometry jaan-boojh kar nahi hilayi

`.btn-save` ko seedha `.btn--primary` ke selector list mein jorna aasan tha aur **ghalat**:
us se `font-size` 14→15px, `font-weight` 600→700, aur `min-height` 44px bhi aa jata — teenon
mein se koi faisle mein shamil nahi tha. Us ki jagah `btn.css` ke aakhir wale `.btn-primary`
block ka wohi tareeqa apnaya gaya: **legacy naam, component ke rang/token, apni measured
geometry.** 14px type scale ka member nahi hai aur us ke liye koi token ijaad nahi kiya gaya.

`opacity: .6` bhi measured legacy qeemat par hai, is file ke `.btn--*` wale `.5` par nahi —
disabled opacity ko nau files mein yaksan karna apna task hai, is mein chhupaya nahi gaya.

### Ek naya nuqsan jo darj kiya gaya, chhupaya nahi — D44

`btn.css`:275 `.btn-primary` ko jaan-boojh kar 10px literal par rakhta hai. Ab bank ek hi
flow mein **10px primary aur 11px save** paint karega. UI-062 se pehle dono 10px par mutafiq
the (dono wohi legacy `--radius-btn` parhte the). Ye radius ke faisle ka nateeja nahi, us
10px hold ka baqaya hai — **D44**, aur agla button task usay band karega.

### Browser check — **hua, aur jo hissa ahem tha wohi confirm hua** (2026-08-25)

Chrome extension is baar bhi connect nahi hui; Irfan ne khud incognito + hard refresh par
dekha. Jo darj karne laayaq hai wo ye hai ke **kya dekha gaya aur kya nahi:**

| | |
|---|---|
| ✅ **CONFIRMED** | `bank` ka Save button **indigo** hai — is task ki sab se bari nazar aane wali tabdeeli |
| ✅ **CONFIRMED** | `bank` par input/select par **focus ring aata hai** |
| ✅ **CONFIRMED** | `print` ka edit modal theek hai — wahi page jahan radius ka farq sab se bara tha (8px → 11px) |
| ⬜ **NAHI DEKHA** | `index` / `library` / `blueprint` ke labels aur focus; strip filter ka box; `.btn-cancel:hover` ka naya grey |
| ⬜ **RAAY BAQI** | D44 — bank par 10px primary aur 11px save ka farq kitna khatakta hai |

**Focus ring ki tasdeeq UI-062 se zyada UI-061 ke liye ahem hai.** Us task ne chaar pages se
`input:focus` ki rules **delete** ki thin aur us ka poora sabot layer-order ka istidlal plus
rest par 0 deltas tha — kyunke is repo mein focus naapne ka koi auzaar hai hi nahi (**D45**).
Ab wo daawa aankh se poora ho gaya. **Magar D45 band nahi hui:** ye gap is dafa **haath se**
bhara gaya, auzaar se nahi, aur agli dafa koi haath maujood na hoga.

⚠ `.btn-cancel:hover` ka naya grey **ab bhi kisi tarah tasdeeq-shuda nahi** — na probe use
naap sakta (rest par 0 deltas), na wo dekha gaya. Yehi D45 ka asal nuqta hai.

---

## UI-061 — `field/filter` agree drain. **2026-08-24. 9 pages par 0 deltas.**

**1075 pass** · ruff saaf · `legacy_css_lines` **1873 → 1864 (−9)** · `unsanctioned_hex`
**356 → 353 (−3)** · `css_type_diff` nau ke nau pages par **0 element × property deltas**.

Sprint 6 ka pehla **per-family** task. Chhui gayi files: `99-legacy/` mein
`bank`, `blueprint`, `index`, `library`, `print`; aur `05-components/field.css`.

### Bara nateeja: ye bucket "shared CSS" nahi tha, **murda CSS** tha

`css_duplication_audit.py` in rules ko `agree` kehta hai — aur wo durust hai, dono/chaaron
legacy files bilkul ek jaisa likhti hain. Magar script ka apna header chetawni deta hai ke
wo **matn** milata hai, **paint** nahi. Naapne par teenon khandan murda nikle:

| rule | file kya kehti hai | asal mein kya computes hota hai |
|---|---|---|
| `label` (4 pages) | `font-size: 12.5px` | **12px** — `forms.css`:47 jeet raha hai |
| `input:focus, select:focus` (4 pages) | `--primary` + `--tint` ring | poori rule bekaar — `forms.css`:79 wohi teen properties deta hai |
| `.strip-filter input/select` (2 pages) | `12px` / `4px 9px` / radius `7px` | **13.5px / 11px / radius 11px** — dekho D43 |

Wajah har jagah aik hai: `main.css`:42 ka layer order `legacy` ko sab se neeche rakhta hai,
aur **layer specificity se pehle tay hota hai**. `.strip-filter input:focus` ki specificity
`(0,2,1)` hai aur `forms.css` ke `input:focus` ki `(0,1,1)` — phir bhi legacy haarti hai.

**Is liye is task ka bara hissa "component banao" nahi, "murda rule mitao" tha** — aur wohi
sab se mehfooz simt hai: jo declaration aaj apply hi nahi ho rahi, us ke hatne se kuch hil
nahi sakta. 0 deltas isi ki tasdeeq hain.

### Jo waqai component bana

Sirf **`.strip-filter` ka container** — `bank` aur `print` par byte-identical bhi hai aur
computed bhi (`display:flex`, `column-gap:6px`, `align-items:center`, `margin-bottom:8px`,
`flex-wrap:wrap`). `field.css` mein gaya, saath `min-height: 30px` — **sirf yehi ek
declaration zinda thi.**

⚠ **Baqi saat declarations jaan-boojh kar sath nahi layi gayin.** Unhein `layer(components)`
mein copy karna unhein **zinda kar deta** aur do live pages badal deta — bilkul wohi jaal jo
UI-042 mein 75 deltas hila chuka hai. Wo faisla `DEFERRED.md` **D43** par hai.

### Jo pehle se tay tha aur chhua nahi gaya

* **`label:first-of-type`** — `field.css`:66 pehle se likhta hai ke ye legacy mein rahegi,
  warna print ke 11 labels tak pahunch jayegi. Agree list mein thi, magar faisla purana hai.
* **`.type-checks input[type="checkbox"]`** — `field.css`:18–24 saaf mana karti hai
  (blueprint par `.topic-check-row` se takrati hai, ek page par do checkbox shakal ban
  jatein). Chhui nahi gayi.

### `PLAN.md` se takraav — Irfan ka faisla

`PLAN.md`:381 Sprint 6 ko **per-page** likhta hai (*"drain to zero, delete it"*). 2026-08-19
ke faisle ke baad ye mumkin nahi raha — 66% page-only lines jaan-boojh kar skip hain, to koi
file zero par nahi jayegi. **Irfan ne 2026-08-24 ko per-family chuna.** `PLAN.md`:381 abhi
bhi purana lehja rakhta hai.

### NEXT TASK ke liye

Agree bucket ab **92 lines** hai. Us ki poori taqseem — teen adad jama karke 92 banta hai,
aur ye is liye likha hai ke agla session "field/filter mukammal ho gaya" na samajh le:

| | lines | halat |
|---|--:|---|
| `modal` (bank+print) | 26 | **khula — agla tajweez-shuda task** |
| `shortfall` (blueprint+print) | 12 | khula |
| `page-head` | 6 | khula |
| `brand` / `btn-*` / `card` / `chip` | 9 | khula |
| `shell/nav` | 23 | **aakhir mein** — 7 mein se 6 rules `@media (max-width: 720/760px)` ke andar hain aur probe 1280px par chalta hai, yani **naapi nahi ja saktin** |
| `field/filter` ka bacha hua hissa | **16** | zail mein |

**`field/filter` mukammal NAHI hua** — us ki 16 lines ab bhi legacy mein hain:

* `.type-checks input[type="checkbox"]` (6, bank+blueprint) — `field.css`:18–24 ka purana faisla
* `label:first-of-type` (4, chaar files) — `field.css`:66 ka purana faisla
* `label { display: block; margin-top: 14px }` (4, chaar files) — **koi darj wajah nahi.** Ye
  zinda hain (forms.css inhein declare nahi karti), magar inhein `layer(elements)` par le
  jana print ke 11 labels tak pahunch jayega — wohi khatra jo `field.css`:66 likhta hai
* `.strip-filter input { flex: 1; min-width: 90px }` (2, bank+print) — **koi darj wajah nahi**

Aakhri do nuqte (6 lines) ek chhote faisle ke muntazir hain, mafqood nahi.

### Browser check — **baad mein hua, 2026-08-25** (UI-062 ke saath)

Jab ye task likha gaya tab check nahi hua tha aur wo yahan darj kiya gaya tha. **Ab hissa
ban chuka hai:** Irfan ne `bank` par input/select par click kar ke dekha — **focus ring aata
hai.**

**Yehi is task ka sab se kamzor daawa tha.** Yahan chaar pages se `input:focus` ki poori
rules delete ki gayin, aur un ke murda hone ka sabot **sirf** layer-order ka istidlal plus
rest par 0 deltas tha — kyunke focus naapne ka koi auzaar is repo mein nahi hai (**D45**).
Agar wo istidlal ghalat hota, ring gayab hota aur **koi bhi gate na pakadta.** Ab wo aankh se
poora ho gaya.

⬜ **Ab bhi nahi dekha:** `index` / `library` / `blueprint` ke labels, aur strip filter ka
box. Baqi daawa wohi hai jo tha: headless Edge par nau pages ke 367,048 element × property
jode mein se **ek bhi nahi hila**.

---

## UI-060 — `slo.css` ka drain map. **2026-08-22. NAQSHA HAI, KOI CODE NAHI BADLA.**

Sprint 6 ka pehla page. Ye section **sirf naap aur naqsha** hai — `slo.css`, `slo.html`
aur kisi component file ko is commit mein chhua nahi gaya. Irfan ne "pehle naqsha,
phir code" chuna (B), kyunke is epic ne chaar dafa "parh kar raay banana" fail kiya.

### Pehla nateeja: is file mein ek bhi rule aisa nahi jo naap kar delete ho sake

`node scripts/css_drain_probe.mjs slo` — 25 rules, 931 elements, 1280×900:

```
DEAD (0 deltas, candidates): 7
LIVE (load-bearing):        18
```

**Saaton zeros false positive hain**, probe ke apne char documented hudood par parkhne
se — ye us header ka "a zero is a CANDIDATE, not a verdict" pehli dafa waqai kaam aaya:

| rule | probe 0 kyun bola | tasdeeq |
|---|---|---|
| `.btn:hover`, `.btn:disabled` | STATE — rest par match nahi | — |
| `.pill`, `.pill.add`, `.pill.upd`, `.pill.err` | JS-RENDERED | `slo.html`:69 `.summary` shuru mein `display:none`; pills :170 `innerHTML` se bante, :179 par summary khulti hai |
| `@media (max-width: 720px)` | VIEWPORT | 1280 par apply hi nahi hota |

**To drain "murda rules hatao" nahi, poori migration hai.** File 59 lines ki hai —
chhoti — magar 25 ke 25 rules zinda hain. **Line count kaam ka paimana nahi**; ye file
"sab se aasan" isi ghalat paimane par chuni gayi thi.

### Doosra nateeja: `:root` ko alag se mat chhero — wo aakhir mein khud marega

`:root` ke **1232** deltas sirf isliye hain ke **isi file ke baaqi 24 rules** us ke
`var(--ink)` / `var(--muted)` / `var(--primary)` parhte hain. Jaise-jaise wo rules tree
ke tokens par jayenge, `:root` bekaar hota jayega aur aakhri qadam par khali file ke
saath uthega. Ise pehle hatane ki koshish poori page tor degi.

### Naqsha — 25 rules, har ek ka ghar

Har "mojood hai" cell code se tasdeeq-shuda hai, yaad se nahi.

| # | rule | deltas | ghar | halat |
|--:|---|--:|---|---|
| 1 | `:root` (17 tokens) | 1232 | — | **aakhir mein khud marega** |
| 2 | `html, body` | 3 | `04-objects/shell.css` | `.o-shell` ka `height:100vh` ise ghair-zaroori kar deta hai |
| 3 | `body {display:flex}` | 865 | `.o-shell` | **mojood** (`shell.css`:83) |
| 4 | `.app-nav` | 9 | `.o-shell__nav` + `.sidenav` | **mojood**; 9 deltas = `padding-right`, milana paregi |
| 5 | `.slo-main` | 609 | `.o-shell__main` | **mojood** (`shell.css`:137) |
| 6 | `.page-head` | 1 | `.pagehead` | **mojood** (`card.css`:83) |
| 7 | `.page-head p` | 14 | `.pagehead p` | **mojood** (`card.css`:104) |
| 8 | `.card` | 609 | `card.css` | ⚠ **bare `.card` mojood NAHI, jaan-boojh kar** |
| 9 | `.card .hint` | 79 | `card.css` | naya rule chahiye |
| 10 | `.row` | 46 | `.field-row` | **mojood** (`field.css`:34), markup re-class |
| 11 | `.btn` | 54 | `.btn--primary` | ⚠ **bare `.btn` mojood NAHI, jaan-boojh kar** |
| 12 | `.btn:hover` | state | `.btn--primary:hover` | **mojood** (`btn.css`:182) |
| 13 | `.btn:disabled` | state | `btn.css` | `.btn--accent:disabled` hai, primary ka dekhna hoga |
| 14 | `input[type=file], select, input[type=text]` | 56 | `03-elements/forms.css` | **mojood** (:57–81) |
| 15 | `.summary` | 42 | page entry file | JS toggle, page-scoped rahe |
| 16 | `.pills` | 4 | `status.css` | naya |
| 17–20 | `.pill` + `.add`/`.upd`/`.err` | JS | `status.css` | **wahi teen semantics** jo `.status-bar.ok/.err/.warn` (`status.css`:34–46) |
| 21 | `td.code` | 925 | ⚠ **koi ghar nahi** | `tables.css` element-only hai apne contract se; `td.code` class hai |
| 22 | `.bloom` | 2294 | ⚠ **koi ghar nahi** | badge — naya component ya `status.css` |
| 23 | `.bloom.empty` | 30 | wahi | |
| 24 | `.empty-state` | 9 | `status.css` | naya |
| 25 | `@media (max-width:720px)` | **UNMEASURED** | `.o-shell` grid | 1280 par naapa hi nahi ja sakta |

**Sidebar ka aadha kaam pehle se hua para hai** — `slo.html`:12–47 dohri class rakhta hai
(`app-sidebar sidenav__panel`, `app-nav sidenav`, `sidebar-foot sidenav__foot`). Legacy
naam wahan waise hi latke hain; shell slice unhe utha legi.

### DO BAROOD — dono `05-components/` ke apne headers mein pehle se darj

Ye is page ka masla nahi, **poore Sprint 6 ka** hai, aur dono ek hi shakal ke hain:

- **`btn.css`:37** — bare `.btn { }` jaan-boojh kar nahi hai. `slo.html` ke **2** buttons
  `class="btn"` rakhte hain aur `99-legacy/slo.css`:50 se rangte hain. `layer(components)`
  legacy ko haraata hai, to bare `.btn` un dono ko **foran** repaint kar dega.
- **`card.css`:6** — bare `.card { }` bhi nahi hai, aur us ka header saaf kehta hai:
  *adding one repaints three live pages*. `.card.has-ch` / `.card > .ch` / `.card > .cb`
  isi liye abhi tak inert hain.

**Dono sirf usi commit mein khul sakte hain jo us page ka markup re-class karta hai.**
Yeh Sprint 6 ka markazi qaida hai: **component pehle nahi, migration ke saath.**

### Tajweez-kardah tarteeb — chaar slice, har slice par apna 0-delta gate

Sab se kam ta'alluq wale pehle, taake har slice akela naapa ja sake:

| slice | rules | kyun yahan | barood |
|---|---|---|---|
| **S1 — pagehead** ✅ **DONE 2026-08-22** | 6, 7 | dono ka ghar **pehle se mojood** | ⚠ do cheezein niklin — neeche |
| **S2 — badges** | 16–20, 22, 23, 24 | shell se bilkul azad; `.pill*` `status.css` ki mojooda `ok/err/warn` trio par baithte hain | `.bloom` (2294) ka ghar tay karna |
| **S3 — card + row + btn + inputs** | 8–14 | yahin dono barood phatte hain | bare `.card` + bare `.btn`, teen live pages |
| **S4 — shell + mop-up** | 2–5, 25, phir 15, 21, aur aakhir mein 1 | `.o-shell` par jana; `:root` yahan khud girta hai | sab se bara qadam |

**S1 pehla isliye nahi ke chhota hai — isliye ke us mein koi faisla nahi hai.** S2 ka
`.bloom` aur S3 ke dono bare rules asal faisle hain aur Irfan ke saamne alag se aane
chahiyen.

**Gate har slice par**: `node scripts/css_drain_probe.mjs slo` + `css_type_probe` HEAD ke
khilaf, aur `python scripts/css_baseline.py` (`legacy_css_lines` sirf **neeche** jaye).

---

### S1 — pagehead. **DONE 2026-08-22. LIVE.** `legacy_css_lines` pehli dafa gira: **1875 → 1873**

`slo.css` ke do rules gaye; `slo.html`:51 ab `.pagehead` (`card.css`:83) pehnta hai.

| gate | nateeja |
|---|---|
| baaqi 8 pages, element × property | **0 deltas har page par** — koi bleed nahi |
| `slo` ke deltas | **7**, aur saaton **usi ek `<div>`** par |
| drift | **0/0** har page, dono runs |
| drain probe LIVE rules | 18 → **16** |
| pytest / ruff / ratchet | 1055 pass · saaf · har ratcheted metric **+0** |

**`.pagehead` `display:flex` hai — inner `<div>` lazmi hai.** Us ke baghair `h1` aur `p`
flex items ban kar **ek doosre ke baghal mein** aa jate hain. `blueprint.html` ne yehi
ghalti ki thi aur 2026-08-15 tak aisi hi chali; us ka markup (`:53–61`) is commit ka
namoona hai. **Isi liye S1 "koi faisla nahi" wala slice nahi tha** — wo daawa is board
par ghalat likha gaya tha aur markup parhne par toota.

**Saat deltas mein se chhe maqsood hain**, Modern target ke mutabiq (`mockup-modern.html`
:97–99): `display` block→flex, `column-gap`/`row-gap` →14px, `align-items`→flex-end,
`margin-top` 0→6px, `margin-bottom` 24px→22px (`--space-gap`).

**Saatwan — `height` 45.95px → 68.52px — dekhne wali cheez hai.** Sabab: `.pagehead p`
ka `max-width: 620px`. Subtitle pehle 949px chaura tha aur **ek line** thi; ab 620px par
**do lines** mein lipatta hai (p ki height 19.56 → 39.13px). `h1` bilkul nahi hila —
font, size, weight, colour, line-height sab wahi.

**Aur ek cheez jo naapne par hi mili: contrast neeche gaya.** `p` ka rang legacy
`rgb(91,102,120)` (**5.47:1**) se component ke `rgb(100,116,139)` (**4.48:1**) par gaya —
AA ki hadd 4.5:1 se **0.02 neeche**. **Ye is task ka paida karda nahi**: `blueprint` yehi
value 2026-08-15 se dikha raha hai, usi run ke BEFORE snapshot se tasdeeq-shuda. Poori
tafseel aur wajah ke ye S1 ke andar theek kyun nahi kiya gaya — **D41**.

**`99-legacy/slo.css` mein koi wazahati comment nahi chhora**, jaan-boojh kar: wo file
append-never hai, aur do line ka comment theek utni lines le leta jitni do rules ne
chhori thin — `legacy_css_lines` 1875 par jama rehta aur Sprint 6 ka poora maqsad fauat
ho jata. Wazahat yahan hai, wahan nahi.


## NEXT TASK → **Sprint 6 (`UI-060..064`) — the drain.** ~~`UI-047c`~~ ✅ **DONE 2026-08-13: `index` is LIVE and every page is migrated.** From here CSS goes DOWN for the first time: `99-legacy/*` is **2,115 lines** across nine files, and **`static/theme.css` is GONE — deleted 2026-08-13 in `UI-064` part 1, 212 lines, 0 deltas on all nine pages.** `unsanctioned_hex` fell 429 → 400 with it, the first ratcheted metric to drop through deletion rather than through care. **`static/app.css` remains** — all nine pages still link its 57 lines for the `@font-face` block and the `.icon` sprite, and it goes with the rest of `UI-064`. **The real work of Sprint 6 has not started**: `legacy_css_lines` is still 2,115 and has not moved a line. **[2026-08-21 — YEH JUMLA AB GHALAT HAI. Naapa gaya: `legacy_css_lines` = 1,875 (−240), abhi bhi 9 files. `unsanctioned_hex` = 356, na ke 400. Sprint 6 waqai shuru ho chuka hai. Neeche ki poori row us waqt ki hai jab ye adad 2,115 the — us ke har adad ko isi shak se parhein aur `python scripts/css_baseline.py` se naap lein. Jo cheez ab bhi sach hai: NEXT TASK Sprint 6 hi hai, aur Sprint 5 (inline styles, 466 par jama) abhi tak chhua nahi gaya.]** Sprints 5 (inline styles) and the rest of Sprint 4 (`UI-042`, `UI-043`) are deliberately skipped — nothing waits on them and much of Sprint 5 is expected to fall out of the drain. See `ROADMAP.md`. ~~**OPEN DEFECT, not fixed and not forgotten: `.app-sidebar` has `height:100vh` and no `overflow`, on all six pages that use it.** `index` was the first with a nav tall enough to spill and is fixed page-scoped; the other five are untouched.~~ **✅ BAND — naapa gaya 2026-08-22.** Saaton pages jo `.app-sidebar` use karti hain un par `overflow-y: auto` mojood hai, aur koi bhi media query ke peeche nahi: `bank`/`library`/`slo`/`slo-health`/`taqseem` apni `pages/*.css` mein (layer components), `index` ko `.sidenav__panel` se milta hai (`05-components/nav.css`:217), aur `print` ki apni legacy base rule mein pehle se tha. Row ne likhne ke baad hone wale kaam ko darj nahi kiya — **is file ka har daawa isi shak se parhein.** ORIGINAL ROW → **`UI-047c`** (`index`) — the last page, and **nothing stands in front of it**. `UI-046` and `UI-047b` both landed 2026-08-13 and **`blueprint` is LIVE: 8 of 9 pages.** That migration verified UI-046 for the first time — its nine rules went from `matches:0`, unverifiable because `blueprint` loaded no layered sheet at all, to live on real markup. **`index` was recorded as blocked on D22 in six places and that was wrong**; `DECISIONS-FOR-IRFAN.md`:67 corrected it on 2026-08-04 and the correction had not propagated. D22 is a technical constraint whose fix can only land in the commit that re-classes markup (Sprint 6), not a decision. The real blocker was narrower — `index`'s two اردو toggle buttons lose Nastaliq because `forms.css`:101's `button { font-family: inherit }` outranks `99-legacy/index.css`:34 by layer order — and **Irfan answered it A on 2026-08-13: page-scoped in `index`'s entry file.** `index` is unblocked.

### UI-047a — **`taqseem`'s migration. DONE 2026-08-12. LIVE.**

| | measured |
|---|---|
| orphan rules enumerated | **17**, reproducing the 2026-08-11 count exactly |
| covered by existing components | **15** — `card.css` ×7, `btn.css` ×6, `forms.css` ×3 (counting `:focus-visible`) |
| exceptions | **2.** Bare `.card`, known — now page-scoped in the entry file. `white-space: nowrap`, **unknown until this task** — absent from the whole tree, fixed in `btn.css` |
| live-page deltas | **0** element × property on all five `css_type_probe` covers, drift **0** |
| `theme?` / EXPOSURE on `taqseem` | **no** / **17 → 0** |
| element count | 70 → **69**, and that is the removed `<link>` — markup diff is one deleted line and three class attributes |
| `.btn--*` in the CSSOM | shared **3**, filled **2**, `.btn--accent` **2**, `.btn--ghost` **1**, `.btn--primary` **0** — all `layer(components)`, depth 2, against UI-041b's `matches=0` |
| browser-verified | **partly, and the confirmed half is the half that mattered.** Irfan checked on 2026-08-13, on `Pre Year 1` / `Mathematics` — the only class/subject with a plan (`has_plan=true`, 50 SLOs). **CONFIRMED: chips render as standing blocks** (not collapsed to pills, so legacy `.chip` still wins) **and changing a chip's select moves the SLO** (`moveSlo` fires). Those two are exactly what this block said needed eyes. **NOT CHECKED: the confirm modal's open/cancel, and the card border / brand header.** Recorded as unchecked rather than assumed. An earlier draft of this row claimed all five |

**The 2026-08-11 attempt passed every gate in this table and was reverted anyway**, because chips
and `.move-sel` are JS-rendered and appear in no snapshot. That is the whole reason this row can
say "live" rather than "prepared".

### UI-045 — **the display / hero type step. DONE 2026-08-07. PREPARED, NOT LIVE.**

**One Tier 1 step, one Tier 2 role, one rule.** `--font-size-8: 30px` (measured from
`99-legacy/landing.css`:48, not extrapolated), `--text-display`, and
`.hero h1 { font-size: var(--text-display); line-height: 1.2; margin-bottom: 12px }` in
**`docs/ui/parked-landing.css`** — the UI-044b shape, a rule in a page entry file that is not
under `static/` and cannot reach a live page.

**Three declarations, not one**, because three things lose to the new tree and the board had
only ever recorded the first: `font-size` (`h1`'s `--text-heading-1`), `line-height`
(`--leading-heading` → 1.1), and `margin-bottom` (`02-generic/reset.css`:79-91). All three lose
by layer order, which is decided before specificity.

**Proven by a three-state swap — migrate, measure, revert — not by reading the cascade:**

| | `font-size` | `line-height` | `margin-bottom` | `h1` height | `.icon` |
|---|---|---|---|---|---|
| **A** HEAD | 30px | 36px | 12px | 72px | **11 at 22px** |
| **B** migrated, no rule | 24px | 26.4px | 0px | 52.78px | **11 at 17px** |
| **C** migrated + rule | **30px** | **36px** | **12px** | **72px** | **11 at 17px** |

**C equals A exactly on the hero, and the rule's isolated effect (B→C) is 8 element × property
deltas** — `font-size` 1, `line-height` 1, `margin-bottom` 1, `height` 5 (the `h1` and its
containers). Nothing else on the page moved.

**IT DID NOT RELEASE `landing`** — `UI-047d` did, on 2026-08-10, once Irfan accepted 17px icons.
The icons are 17px in **both** migrated states; the rule never touches them.

Migrating the page costs **285** element × property deltas. **This rule changes 8 of them and
restores 6 to HEAD** — an earlier version of this line said "fixes 8" and the arithmetic that
follows from it is wrong. The 6 that cancel are the `h1`'s four properties plus `.hero` and
`.hero-inner` heights; the 2 that do **not** are `html` and `body` height, because the page below
the hero is genuinely shorter (**1010.27px → 993.953px**). So the live migration measures
**285 − 6 = 279**, reproduced three ways on 2026-08-10.

**Live-page gate: 314,996 element × property comparisons, 0 deltas, 0 paths in only one
snapshot, drift 0** on `slo`, `slo-health`, `library` and `bank`. The two token names reach all
three live pages through `01-settings/` and **nothing reads them**, which is the reason to expect
zero — the measurement is what makes it a fact. **No fallbacks were added** (D37: `settings` is
after `legacy` in `main.css`:42 and cannot lose to it).

### UI-041 — **the button component. DONE 2026-08-07. PREPARED, NOT LIVE. Reviewed in four rounds; round 4 PASSED.**

> **DoD #6 is met, and it took four rounds — which is the finding worth carrying, not a
> footnote.** Verdicts: round 1 **FAIL** (three blocking), round 2 **FAIL** (one blocking,
> three notes), round 3 **FAIL** (one blocking, seven notes), round 4 **PASS with notes**
> (2026-08-07). Rounds 1–2 ran on 2026-08-06 and the task was committed unreviewed at
> `8b9b055` so a long session could end on a clean tree; rounds 3 and 4 ran on 2026-08-07.
>
> **ONLY ONE FINDING IN FOUR ROUNDS TOUCHED A CSS RULE, and it was round 1's** — the
> `:focus-visible` ring, removed because its premise was false (F2 below). **Everything after
> that was prose, citations and counts.** That is measured, not asserted: strip the comments
> from `btn.css` and its declarations are **byte-identical across `a420ee0` → `8b9b055` → the
> round-3 remediation** (882 chars each way, both remediations comment-only). The component's
> CSS has not moved since the first commit.
>
> **So the thing that failed three times was the documentation, not the button.** Round 3's own
> blocking finding was *created by round 2's remediation* — a summary line asserting UI-041 was
> "done" while the body of the same board said DoD #6 was unmet. Notes rose 0 → 3 → 7 across the
> rounds while blocking findings fell 3 → 1 → 1: each remediation added prose, and prose making
> precise numeric claims is surface for the next reviewer. **A component this small does not
> need 165 lines of board prose. If UI-040 repeats this shape, shrink the prose instead of
> defending it.**
>
> **Round 4 verified the three things that would have mattered if wrong**, independently rather
> than on this board's word: `btn.css`'s change is comment-only, the probe's `PROPS` is
> untouched at 44 distinct entries, and the gates are green (pytest **906**, ruff clean, ratchet
> OK, `unsanctioned_hex` **429**, zero raw hex in `btn.css` including comments).
>
> **Three notes were left unfixed at round 4 and are fixed in this commit** — a stale
> `shared_css_lines` figure in the ledger row, and `NEXT-SESSION.md` (deleted 2026-08-20, extract at `MEASURED.md`) being one round behind.

> **Like UI-044a, this ships nothing today.** `static/css/05-components/btn.css` is imported by
> `main.css` and therefore reaches all three live pages — and **matches zero elements on them**.
> Every selector in it is `.btn--*`, and `.btn--` appears in **no markup anywhere in this repo**.
> **It activates when a page migrates and its markup is re-classed, not before.**

**Two variants, and the file is honest that two is a scoping decision rather than the measured
ceiling.** **21 button classes** across the nine legacy files plus `theme.css`;
two roles cover the bulk — a filled action and an outlined secondary — with the remainder being
size and context variants of those two, plus danger. *(This said "thirteen shapes" until review
could not reproduce it. The counting rule is now written out in `btn.css`'s header — distinct
base class names, deduped across files, pseudo-classes and compound/contextual variants folded
into their base. Count the compounds separately and it is 30, so the rule is the number.)*

```
.btn--primary    filled    --color-action / --color-on-action
.btn--ghost      outlined  --color-surface / --color-border / --color-text
```

**Proof that the three live pages did not move — measured both ways, not argued:**

| check | result |
|---|---|
| `.btn--` in `slo.html` / `slo-health.html` / `library.html` markup | **0 / 0 / 0** |
| `css_type_probe.mjs` before vs after, **44 properties × 7,159 elements** | **0 element × property deltas**, 0 paths in only one snapshot |
| determinism | `driftCount` **0** on both runs, all four pages |
| `git diff` on the five legacy files holding `.btn-primary`/`.btn-ghost` | **empty — none was opened** |
| `git diff` on `03-elements/forms.css` | **empty — D22 stays parked** |
| raw hex in `btn.css`, comments included | **0**; `unsanctioned_hex` flat at **429** |

**THE PROBE'S PROPERTY SET WAS EXTENDED FIRST — and the first version of this paragraph
justified it with the one example that does not hold.** It said a rule flattening `library`'s
buttons to borderless would have reported zero deltas under the old 18 properties. **Review
mutation-tested that in-browser and it is false**: `box-sizing` is `border-box` globally
(`02-generic/reset.css`:73), so removing a 1px border changes used `width`/`height` — both in
the original set — on the button and on its flex siblings. On `library`, `button { border: none }`
produces **172 element × property deltas** within the old 18, and the narrower
`.btn-primary,.btn-ghost { border: none }` produces **18**. *(Both numbers are deltas, not
properties — "172 of the old 18" was the earlier phrasing and it cannot be read literally.)*

**The extension is still right, on the three things that genuinely are invisible.** Same
mutation test, same page: `border-radius: 0` → **0 deltas**, `box-shadow: none` → **0**,
`cursor: default` → **0**. `library.css`:86 gives `.btn-ghost` a 9px radius and `library.css`:76
gives `.btn-primary` a shadow and a 10px radius — a component that changed any of them would
have passed the gate silently. The set is now 44 properties. Do not shrink it back.

**There is deliberately no bare `.btn { }` rule, and adding one breaks a live page.** `slo.html`
carries `class="btn"` on `#importBtn` and `#assignBtn`, drawn by `99-legacy/slo.css`:50 in
`layer(legacy)`. This file is `layer(components)`, which outranks legacy — a bare `.btn` here
repaints those two buttons immediately. The skeleton therefore sits on the modifier list and the
class API is `class="btn btn--primary"`. **A bare block rule becomes safe only once Sprint 6
drains the legacy files.** Note `.btn-primary` and `.btn--primary` differ by one hyphen; that is
load-bearing.

**Colour comes from Tier 2, geometry from `99-legacy/bank.css`:139/:149.** That split is what
`bank` itself does — it writes `background: var(--primary)`, not a literal. Where the token
scale has no member, bank's measured pixel value is kept, and every divergence is recorded in
the file header: radius 10/9px → `--radius-control` (11px), size 14.5/13px → `--text-body` /
`--text-control` (15/13.5px), gap 7px → `--space-gap-tight` (8px). Weights and the primary's
8px gap are exact.

**WHAT THIS COMPONENT DOES NOT YET COVER — read before migrating `bank` or `blueprint`:**

- **`bank`'s filled button has an action-tinted drop shadow and this one is flat.** There is no
  Tier 2 token for a tinted shadow and inventing the tint would be inventing a design decision.
  Whoever migrates `bank` settles it.
- **Four shapes have no home yet**: `secondary` (blueprint, a 1.5px **`--primary`**-bordered
  button — `blueprint.css`:63 reads `1.5px solid var(--primary)` and `:5` sets
  `--primary: var(--brand)`, so it is brand-bordered, **not** this tree's teal `--color-accent`;
  the 1.5px is right and the colour word was wrong), `danger`, the `accent`/gold fill
  (`taqseem`, 2 instances, from `theme.css`), and an on-dark ghost (bank's feedback bar).
- **`danger` is not a held-page-only problem — it is on a LIVE page.** This board said
  "bank + blueprint"; review found `99-legacy/library.css`:94 declares `.btn-danger` too and
  `library` renders one per row (24 at the time of measurement). So the first page that will
  need a danger variant is one already on the new tree, not one of the six held.
- **The size grid does not fit two pages.** Roles repeat at several sizes — ghost min-height is
  36px on bank and blueprint, **40px on library, 48px on index**; primary is 44px but **52px on
  index**. A four-step grid (24/36/44/52) covers everything except library's 40 and index's 48.
  Those two need either ±4px accepted or two more steps, **at migration time, by measurement.**

**What UI-041 did NOT release.** None of the six held pages. `taqseem` is the only one whose
buttons this unblocks — its three are drawn by `static/theme.css`, which its migration unlinks,
so they must be re-classed in that commit — and `taqseem` also needs UI-040. **`index` is not
unblocked by this task**: its `.gen-btn`/`.ghost-btn` controls come from its own legacy file and
survive migration untouched — **28 elements**, 14 each, out of `index.html`'s 39 `<button>`s.
*(An earlier draft said "~29 buttons". 29 is the count of the two class **strings** in the
markup; the 29th is `.ghost-btn` on an `<a>` — the excel-template download link — which is a
live D27 instance on this page, and the other 11 `<button>`s carry neither class.)* its actual blocker is the `button { font-family: inherit }`
Nastaliq loss and `.main`'s layout, and **the reset half is exactly what D22 keeps parked.**
`blueprint` and `bank` likewise keep their own legacy button rules through migration.

**D27 is fixed in this file, and is not yet fixed on any page.** `.btn--ghost` sets `color`
explicitly, so an `<a>` and a `<button>` carrying it paint identically. The live defect remains:
measured this session, `slo.html`'s `<a class="btn-ghost">` is `rgb(15,23,42)` against its
sibling `<button>`'s `rgb(46,90,172)`, and **`library` has the same split** (`rgb(15,23,42)` vs
`rgb(22,33,58)`) — an instance D27 predicted and no one had measured. Both clear when those
pages are re-classed, not before.

#### F2 — a focus ring was added on 2026-08-06 and **removed the same day**. The premise was wrong.

The rule was `.btn--primary:focus-visible, .btn--ghost:focus-visible { outline: 2px solid
var(--color-action); outline-offset: 2px }`, and the comment defending it claimed **"no legacy
button in this repo declares a focus style at all"**, calling it the file's one invented
decision.

**That claim is false and review caught it.** `03-elements/forms.css`:106 already carries a bare
`:focus-visible { outline: 2px solid var(--color-accent); outline-offset: 2px }` in
`layer(elements)` — **live on all three live pages since UI-021** — ported from
`static/theme.css`:212, which still carries the same rule on the four pages that link it.
Buttons already have a ring everywhere except `landing` and `print`.

**So the rule was not adding accessibility, it was changing a colour — and adding a second ring
colour to the same screen.** A `0,2,0` selector in `layer(components)` beats `forms.css`'s
`0,1,0` in `layer(elements)`, so any re-classed page would have shown **buttons ringed indigo
while every other focusable element stayed teal**. Measured on `slo.html` before removal: the
same button reads `rgb(14,165,164)` as `btn` and `rgb(79,70,229)` as `btn btn--primary`.
**That is D27's defect — one control, two appearances — in a different place**, which is why the
rule is gone rather than documented and kept.

**Recorded rather than quietly dropped, because the mistake is the reusable part**: a component
in `layer(components)` silently outranks the element layer, so "adding" a style to a component
is often overriding one the tree already has. The geometry was never invented either — 2px with
a 2px offset is the tree's existing convention, which the removed comment did not know it was
restating. If a button-specific ring is ever wanted it needs a Tier 2 focus token and a decision
about the whole tree's ring colour, not a component override.

`btn.css` therefore ships **no focus rule**, and the file says so in place of the removed one.

#### F1 — token fallbacks: proposed, measured, and declined. **D37**

The proposal was `var(--color-action, <hex>)` on every component token, so a button could not
go unpainted if a token failed to resolve. **Two things stopped it, and the second is the one
worth carrying.**

First, mechanically: a raw hex in `05-components/` takes `unsanctioned_hex` from 429 to 430 and
**fails the ratchet test** — PLAN §2 is explicit that this is a test and not a review
convention. (The hex named in the request, a dark green, is also not `bank`'s value: `bank.css`
:141 reads `var(--primary)` and `--primary` is the blue that computes to `rgb(46,90,172)`.)

Second, and this is why it became a D row rather than a workaround: **the failure it defends
against cannot happen in the direction feared.** `main.css`:42 orders the layers
`legacy, settings, …` — settings comes *after* legacy, so legacy cannot shadow a settings
token. Measured: **none of the 12 tokens `btn.css` reads is defined in any legacy file or in
`theme.css`**, and two of them demonstrably resolve on all three live pages right now — body
15px (`--text-body`) and `slo`'s anchor `rgb(15,23,42)` (`--color-text`). Body's 21.75px line
box shows `--leading-body` resolving too, but that is a settings token outside `btn.css`'s
twelve; an earlier draft counted it as a third and review caught it. **`D35` is the row that already retired this
exact mechanism** — it reported a `--space-*` regression attributed to settings losing to a
legacy unlayered `:root`, and the swap-and-measure found the printed margin does not move at
all. **Do not cite D35 as a precedent for adding fallbacks; it is the precedent for not
adding them.** Full reasoning and the two bleed directions that ARE real — unlayered
`theme.css`, and inline `style` on `documentElement` — are in **D37**.

### UI-044b — **print-media leading. D36 solved 2026-08-05. PREPARED, NOT LIVE.**

> **Like UI-044a, this ships nothing today.** The rule lives in **`docs/ui/parked-print.css`**,
> which is `print`'s parked entry file — `print` is HELD, `static/css/pages/print.css` does not
> exist, and the file is not under `static/` at all. **Ratchet impact is literally zero**
> (`shared_css_lines` 1685 → 1685) and no page can reach it. **It activates in the same commit
> that migrates `print`, and not before.**

**The rule:**

```css
@layer components {
  @media print {
    body { line-height: normal; }
  }
}
```

**What it fixes.** `99-legacy/print.css`'s `body` declares neither a line-height nor a font-size,
so it inherited the browser's `normal`/16px. Once the page loads `main.css`,
`03-elements/typography.css`:41's `body { line-height: var(--leading-body) }` sits in
`layer(elements)`, beats `layer(legacy)`, and every line box on the printed paper opens up —
which is D36.

**Both candidate fixes were measured on all three papers, not reasoned about:**

| | `0d04c750` | `a5015cda` | `9ade2655` |
|---|---:|---:|---:|
| HEAD | 2 | 6 | 7 |
| migrated, no rule — **D36** | **3** | 6 | 7 |
| `line-height: normal` | **2** ✅ | 6 | 7 |
| `line-height` **+** `font-size: medium` | 2 | 6 | 7 |

**Adding `font-size` changes nothing, so it is not in the rule.** The smaller fix ships.

**What this does NOT claim.** The sheet returns to HEAD's **page count**, not HEAD's height:
2170.81px at HEAD, 2300.69px broken, **2168.61px fixed** — 2.2px *shorter* than HEAD, because
the base font-size stays at the new tree's 15px. The page count is what a teacher holds; that is
what is restored, and "identical to HEAD" would be the wrong claim.

### Why the rule is in the entry file and not in `03-elements` — measured, and it changed the answer

The architecturally tidy home is `03-elements/typography.css`: it is an element rule and fits
that file's contract. **It was measured there first, and the three LIVE pages moved.** Their
print output had never been measured before this task — the earlier gates were screen-only:

| live page, **print media** | HEAD | rule in shared tree | rule in entry file |
|---|---|---|---|
| `slo` | 21.75px, **22 pages** | `normal`, **20 pages** | **21.75px, 22 pages — 0 deltas** |
| `slo-health` | 21.75px, 2 pages | `normal`, 2 pages | **21.75px, 2 pages — 0 deltas** |
| `library` | 21.75px, 6 pages | `normal`, 6 pages | **21.75px, 6 pages — 0 deltas** |

**`slo`'s printed output would have gone from 22 sheets to 20.** "Nobody prints `slo-health`" was
an available assumption and this epic's most repeated failure is exactly that shape, so it was
measured instead. Irfan chose the entry file on those numbers.

**The deviation this creates is recorded rather than hidden.** `pages/*.css` entry files are
documented as exactly two `@import` lines; this one now carries a rule. The trade is stated in
the file's own header: a page-scoped fix that cannot touch a live page, at the cost of a type
decision living in a page file — so **`bank` or `index`, if either is ever printed after
migrating, will hit the same bug and need the same rule.** Whoever moves this into the shared
tree must re-measure the live pages' **print** output, not just their screen output.

**`@layer components`, not unlayered.** A bare rule in an entry file would be unlayered and beat
every `@layer` — the hazard that file's own header warns about. Declaring it in `components` puts
it above `elements`, where it must be to win, and below `utilities`, where a later override can
still reach it.

### UI-044a — **Nastaliq leading. Committed 2026-08-05. PREPARED, NOT LIVE.**

> **READ THIS BEFORE ANYTHING ELSE IN THIS SECTION.** The rule is in the tree and imported by
> `main.css`, and **it currently reaches nothing.** Measured, not reasoned:
>
> | page | links `main.css`? | `.q-text .qt.rtl` elements |
> |---|---|---:|
> | `bank` | **no** — HELD at HEAD on its three `<link>`s | **24** |
> | `taqseem` | **no** — HELD at HEAD | 0 (it has no Urdu at all) |
> | `slo`, `slo-health`, `library` | **yes** | **0** |
>
> **So the rule loads on three pages that have no Urdu, and the one page with 24 Urdu elements
> never loads it. Net effect on every page today: zero.** This is deliberate — foundation
> first, the shape UI-021 used — but it must not be read as "bank is fixed". **It activates the
> moment `bank` migrates, and not before.**

**What shipped, and it is the first thing ever to land in `layer(components)`:**
`05-components/urdu.css` with one rule — `.q-text .qt.rtl { line-height: var(--leading-nastaliq) }` —
plus `--line-height-nastaliq: normal` (Tier 1) and `--leading-nastaliq` (Tier 2), and the import
in `main.css`. **No page's `<link>` block was touched and no page was migrated.**

**Why it is in `05-components` and not where the problem is.** `03-elements/typography.css`:41's
`body { line-height: var(--leading-body) }` is in `layer(elements)` and takes the leading of any
legacy rule that declares none — including `99-legacy/bank.css`:229 `.q-text .qt.rtl`, which sets
Nastaliq and a size and no line-height. The fix cannot go in `99-legacy/` (append-never,
CLAUDE.md:387) and cannot go in `03-elements/` (element selectors only, by those files' own
contract — `.qt.rtl` is a class). `layer(components)` outranks `layer(elements)` without editing it.

**The app already had a Nastaliq leading; it was not a token.** Ten Nastaliq rules across three
legacy files, **eight of which declare their own line-height** — 1.7, 1.7, 1.8, 1.9, 1.9, 2.0.
**Only two declare none**, and they are exactly the two known defects: `bank.css`:229 (fixed here)
and `print.css`:126 `.letterhead .school-ur` (**D33 — NOT fixed here**, see below).

**`normal` was chosen over a ratio, and the choice was measured both ways.** At 15px the font's
own metrics give **38px** — a 2.53× multiplier where Latin's is ~1.3×. Every ratio the app
already uses for Urdu (1.7–2.0) is *tighter* than the font asks for. `normal` restores exactly
what `bank.html` renders at HEAD today, so unholding the page stays a migration rather than a
redesign. **A/B'd in the browser against 2.6**: 39px vs 38px — **1px per line**, 24px across the
whole 24-question list, which is the useful finding: `normal` and 2.6 are effectively the same
place. **2.0 was never rendered** and would be 30px, a 21% tightening; switching later is one
value in `01-settings/tokens.css`, which is what the token is for.

**`bank`'s Urdu, measured in three states** (headless Edge 151, 1280×900, webfont awaited, drift 0):

| state | `line-height` | line box |
|---|---|---|
| **A** — HEAD, what a teacher sees today | `normal` | **38px** |
| **B** — migrated, no rule (the state it was HELD on) | 21.75px | 21.75px |
| **C** — migrated + this rule | `normal` | **38px** |

**C equals A exactly.** Irfan confirmed it in the browser on the Urdu questions
(سیب گنو اور نمبر لکھو) — no overlap, Nastaliq intact.

**The rule's isolated effect (B vs C, both migrated, only the rule differing): 74 elements.**
`line-height` on **24** — precisely the 24 Urdu-only questions — and `height` on 74, being those
24 plus their `.q-text`, `.q-row` and two containers. **Nothing else moved**: no colour, no
font-size, no padding, no margin, no width, and **435 English `.qt` elements were untouched, 0
of 435.**

### The live-page regression gate — **128,862 comparisons, 0 deltas**

Irfan's condition on this task: `typography.css` and its neighbours reach all nine pages, so the
three pages **live on the new tree today** must not move. Measured HEAD vs the shipping state
over a property set of 18 fixed before measuring:

| page | aligned elements | only-HEAD | only-new | **deltas** |
|---|---:|---:|---:|---:|
| `slo` | 930 | 0 | 0 | **0** |
| `slo-health` | 190 | 0 | 0 | **0** |
| `library` | 661 | 0 | 0 | **0** |
| `bank` (HELD, at HEAD) | 5378 | 0 | 0 | **0** |

Drift 0 on all four. **"Byte-identical" is not the test and cannot be** — the CSS files themselves
change; zero element × property deltas is the measurable equivalent, and that is what passed.
The three live pages carry **zero Urdu elements** (measured, not assumed), so the selector cannot
match them — but that was proven rather than argued.

### `bank` stays HELD — and its original hold reason is now resolved

**`bank`'s recorded hold was the Urdu line-height, and UI-044a solves it — but solves it in a
file `bank` does not yet load.** It stays HELD on Irfan's call pending **D31** — the two
`<label>`s in `.urdu-toggle-row` at 4.44:1 against AA's 4.5:1 — whose home is **UI-042**
(`field` component). Note what the board says about that: D31 was flagged at handover and
`PLAN.md`:210 lists UI-042 as releasing **no held page**, so this is a new and more
conservative hold than the one recorded, not the continuation of an old one.

**Two labels on the board have been kept accurate rather than copied from the brief, because
they would contradict the code:**

- **The token is `normal`, not `2.0`.** `01-settings/tokens.css` reads
  `--line-height-nastaliq: normal`, which is **38px** at 15px and restores HEAD exactly. `2.0`
  would be **30px**, a 21% tightening that has never been rendered or looked at. Switching is
  one value in that file if it is ever wanted.
- **`taqseem` is not part of this.** Its legacy file contains zero `Nastaliq` / `urdu` / `.rtl`
  matches, so it has no Urdu overlap to fix and this rule cannot affect it. Its blocker is
  `.btn`/`.card`/`.pagehead` — **UI-041 + UI-040**, not UI-043, which is tables and domain
  components and releases no held page.

### What UI-044a has NOT done yet

- **D33 — `print.css`:126 `.letterhead .school-ur` is untouched.** `print.html` is HELD and
  unmigrated, so it does not link `main.css` and a rule here cannot reach it. **When `print`
  migrates, add its selector to `05-components/urdu.css`** — the file's header says so.
- **D36 — the print pagination regression is untouched.** That is **UI-044b**, the print-media
  leading half, and it is the next task. It cannot be solved by moving
  `--leading-body`: the three live pages inherit that same 1.45 and would move with it.
- **`taqseem` has no Urdu at all** (measured — zero `Nastaliq`/`urdu`/`.rtl` matches in its
  legacy file), so nothing in this task touches it.

`BASELINE.json` re-pinned: `shared_css_lines` **1616 → 1685**. `unsanctioned_hex` flat at 429 —
no hex reached the new files.

### Sprint 4 is re-scoped and re-ordered — **D34 resolved 2026-08-05, docs only**

`PLAN.md`'s Sprint 4 was four tasks ordered by duplication count, and **three of the six held
pages were waiting on work no task ID owned.** It is now **seven tasks ordered by how many held
pages each releases.** Three IDs are new. The full table and the per-page blocker map live in
`PLAN.md` §Sprint 4 — this is the summary:

**A COMPONENT TASK CANNOT RELEASE A PAGE — A MIGRATION DOES.** This column said otherwise in
every component row until 2026-08-08. A component ships new names into `layer(components)`; a
page opens when its markup is re-classed and its `<link>` block changes. Measured false three
times before the pattern was named: UI-045/`landing`, UI-046/`blueprint`, UI-040/`taqseem`. The
counts below are from §"THE SIX HELD PAGES, MEASURED".

| order | ID | prepares / releases |
|---:|---|---|
| **1a** | **UI-044a** ✅ done — Nastaliq leading | **prepared, not live**; activates when `bank` migrates |
| **1b** | **UI-044b** ✅ done — print-media leading | **prepared, not live**, in `print`'s parked entry file · settles **D36** |
| **2** | **UI-045** ✅ done — display / hero type step | **prepared component, released nothing.** `landing` also needs its icons settled — and **no component can do that**, see the two unowned blockers below |
| **3** | UI-041 ✅ done — button | **prepared component, released nothing.** 6 of `taqseem`'s 17 — **not the gold fill** |
| **4** | **UI-046** — nav + shell components | **prepares component, releases nothing.** 12 of `blueprint`'s 20 |
| **5** | UI-040 ✅ done — card + pagehead | **prepared component, released nothing.** 7 of `taqseem`'s 8 card rules, 3 of `blueprint`'s 20 |
| 6–7 | UI-042 modal/field · UI-043 tables/domain | **prepare components, release nothing.** UI-043 carries `blueprint`'s `.chip` and `index`'s `.tag` |

**UI-044b and UI-045 are both done and NEITHER released a page.** This line said they would
"release two more of the six, and each completes its pages outright"; both halves were measured
false — UI-044b's fix is parked and `print` stays HELD, and UI-045 restores `landing`'s hero
while its 11 icons still fall 22px → 17px. **UI-044 (a+b) is the single highest-value task in
the epic right now**: `bank`'s hold and `print`'s D33 are one problem in two places, and D36
comes from the same leading change, so one task settles all three.

**D32 is done (2026-08-08) and UI-046 is clear.** `css_orphans.py` now reads inline `style=""`;
`blueprint`'s **9 bare markup reads** are measured, and the re-run reproduced D32's recorded
nine-page sweep exactly.

**Nothing in Sprint 4 is scheduled for `--space-*`.** An earlier plan treated a space-token
layer fix as the foundation that would open several pages at once; **D35 measured it and the
mechanism does not exist on this branch.** See D35.

### THE SIX HELD PAGES, MEASURED — 2026-08-08, Edge 151, drift 0 on every page

**Every number below was produced by `scripts/css_orphans.py --rules`, not estimated.** It is
recorded here because it was measured while scoping UI-046 and UI-040 and had nowhere on the
board to live — the shape this epic already lost once, when the first `print` session left its
measurement scripts in a scratchpad (`docs/ui/PROBES.md` header).

**"Real" subtracts the orphans the new tree already declares.** `03-elements/forms.css` carries
`:focus-visible` (:106) and the `input`/`select`/`textarea` family (:53-57, :79-81), which are
the same selectors `static/theme.css` declares at :196, :199 and :212 — so a page whose only
orphans are those is not exposed at all.

| page | links `theme.css`? | orphan rules | **real** | what they are |
|---|---|---:|---:|---|
| `blueprint` | yes | 20 | **19** | 12 nav/shell · 3 brand · 3 card · 1 chip |
| ~~`taqseem`~~ ✅ | **no** — migrated 2026-08-12 | **17** | **0** | UI-047a: 15 covered by components, bare `.card` page-scoped, `white-space` fixed in `btn.css` |
| `index` | yes | 5 | **3** | `.tag` ×2 · `.row` · `.summary-row:last-child` · **plus 4 partial rules**. Re-checked 2026-08-12: all three are **page-scoped work for `UI-047c`**, not UI-043 — each is live on a migrated page under a different meaning. The other 2 orphans are covered: `input[type=number]` → `forms.css`:54, `:focus-visible` → `forms.css`:106 |
| `bank` | yes | 1 | **0** | its one orphan is `:focus-visible` |
| `landing` | **no** | 2 | **0** | D9 — never linked it, so both already fall through |
| `print` | **no** | 3 | **0** | D9 |

**`taqseem` is 17, not the 16 this board carried.** Re-counted, not copied.

**`blueprint`'s 20, by which task owns them** — this is what makes "UI-046 releases `blueprint`"
impossible, and it was found by enumerating the rules rather than by reading the old summary:

| owner | n | rules |
|---|---:|---|
| **UI-046** nav + shell | **12** | `.app` · `.top` · `.top .crumbs` · `.top .crumbs b` · `.top .spacer` · `.top .avatar` · `.nav` · `.nav .grp` · `.nav a` · `.nav a .icon` · `.nav a:hover` · `.nav a.active` |
| brand | 3 | `.brand .logo` · `.brand b` · `.brand small` |
| **UI-040** card | 3 | `.card > .ch` · `.card > .ch h3` · `.card > .cb` — **shipped 2026-08-08** |
| **UI-043** chip | 1 | `.chip` |
| already covered | 1 | `:focus-visible` |

**Plus three partial rules** — the selector is redeclared but properties still go: `.brand` (7),
`.main` (`grid-area`, `overflow`, `padding`), `.pagehead p` (`margin-top`, `max-width`) — **and
two media-query rules nothing redeclares**, `@media (max-width: 760px)`'s `.app` and `.nav`, so
the narrow-viewport shell breaks too. Neither group is inside the 20.

**`taqseem`'s 17, the same way:** **8** card/pagehead (UI-040 shipped 7 of them; the 8th is the
bare `.card`, which arrives with the migration's re-classing), **6** button, **3** already
covered. Plus two partials: `.brand` (`background`, `color`, `grid-area`) and `.brand small`
(`font-weight`).

#### Two blockers that no task currently owns

**1. There is no gold button, and `taqseem` cannot migrate without one.** Measured:
`taqseem.html` carries `btn gold` ×2 and `btn ghost` ×1. `btn.css` ships `.btn--primary` and
`.btn--ghost` only, and **this board's UI-041 ledger row lists the gold fill among the four
shapes with no home** (accent/gold, with secondary, danger and on-dark) — `btn.css`'s own header
carries no such list; it points here. So `taqseem`'s migration needs either a new modifier in a
reviewed component or its own page-scoped rule — that is **`UI-041b`**.

**2. `landing`'s icons cannot be fixed from any layer.** `.icon { 17px }` is in **unlayered**
`static/app.css`:57, which all nine pages link, and **unlayered styles beat every `@layer`**
(`main.css`:73-74 states this rule). `99-legacy/landing.css`:26's 22px wins today only by
document order and loses the moment the page is layered — 11 icons, measured. **No component in
the new tree can reach it.** The choice is editing `app.css` (live on all nine pages) or an
unlayered rule in `landing`'s own entry file. UI-046 was recorded as fixing this and cannot.

**Both now have homes on the board: the gold fill is `UI-041b` (`.btn--accent`, which also
settles D7), and the six migrations are `UI-047a-f`. See `PLAN.md` §Sprint 4b** — added the same
day, because the migrations had been a single line at the bottom of the roadmap and that is what
let five component tasks ship while the board read as though pages were opening.

### `print` — **HELD (2026-08-05), on Irfan's call.** Nothing was swapped, nothing reverted

**`print` is the sixth held page and the only one held without its migration ever being
performed in the session that held it.** The entry file stays parked at
`docs/ui/parked-print.css`; `print.html` is untouched at HEAD on its two original `<link>`s;
`static/css/pages/print.css` was never created. **There was therefore nothing to revert** —
`git status` was clean before this docs-only commit and `git diff` against the previous
commit touches nothing under `static/`. `shared_css_lines` stays at **1616** and
`BASELINE.json` is **not** re-pinned, for the same reason `taqseem`'s hold did not re-pin it:
nothing shipped.

**The hold is Irfan's call and it is the safe direction** — a held page ships nothing. **The
reason it was held turned out not to be the reason it should stay held, and both halves of
that are now measured.**

**The reported mechanism is retired — D35.** A right margin moving 48px → 24px and a
`.count-grid` collapsing on Q10, blamed on `--space-*` in `layer(settings)` losing to a legacy
unlayered `:root`. The swap was performed, the AFTER half measured in print media on three real
papers, and the tree reverted. **The margin does not move**: `.sheet` padding is 52.9134px on
all four sides before *and* after, every ancestor is 0 both ways, and **zero box deltas land on
the margin chain**. `.count-grid` exists nowhere in the repo, no legacy file reads `--space-*`,
and `main.css`:42 puts `legacy` first and weakest. See D35 for the full settlement.

**But a real regression was found in the same run — D36, and it justifies the hold.**
`0d04c750` goes **2 → 3 printed pages**, its sheet growing +129.9px (**+6.0%**). The other two
papers hold at 6 and 7. This is **D21/F3's line-height growth crossing an A4 boundary**, not a
margin fault — and it is exactly what F3 predicted and could not measure ("one paper's margin,
not a guarantee"). **The consequence is physical: one more sheet per exam, per student**, on
the Ctrl+P page. **`print`'s blocker is now the leading decision — UI-044b — and D33 waits on
UI-044a's file, which already exists.**

### The margin test — **BOTH halves are now run**, and the margin is clean

The deciding test `MEASURED.md` recorded as unrun has been run end to end: BEFORE at HEAD,
then the one-line swap, then AFTER in **print media**, then revert. **These numbers stand on
their own and should not be re-measured:**

| | |
|---|---|
| browser | `Edg/151.0.4129.59` — the board's "Edge 151" confirmed |
| papers | `0d04c750` 20Q · `a5015cda` 20Q/19 images · `9ade2655` 25Q/25 images — real papers, never a blank page |
| media / fonts | `print` / `loaded` — `document.fonts.ready` awaited before any box was believed |
| drift | **0** on all three, two snapshots with no action between |
| `@page` | `@page { size: a4; margin: 0px }`, **unlayered**, from `99-legacy/print.css` |
| `html` / `body` / `.print-main` | padding, margin and border-width all **0 0 0 0** |
| **`.sheet`** | padding **52.9134px** on all four sides = **exactly 14mm** |
| knobs | `--page-margin: 14mm`, `--q-font: 14px`, `--q-gap: 14px`, all on `documentElement.style` |
| sheet height | 6323.81px — independently reproducing the earlier session's 6324 |
| elements | **555** on `9ade2655` — independently reproducing the qadam-2 probe's 555 |

**So `print.css`:1-2's single-source claim is no longer a comment, it is measured**: the whole
printed page margin is `.sheet`'s padding and every ancestor above it is zero. **There is no
48px or 24px anywhere on that chain** — `.print-main`'s 24px is screen-only and `print.css`:219
zeroes it in print media.

**A number on the board disagreed with HEAD, and the disagreement turned out to be the finding.**
`MEASURED.md`'s test-data table gives `0d04c750` as **3 pages**; at HEAD it is **2**, and
**migrated it is 3**. The table's figure was almost certainly recorded from the *migrated* state
in the first `print` session — so it was never a typo, it was **D36 showing up a session early
and being read as test data.** The other two reproduce exactly (`a5015cda` 6, `9ade2655` 7).

**The 48 padding deltas are named, and they are harmless.** All 12 elements × 4 sides are form
controls taking `03-elements/forms.css`:68's `padding: 9px 11px` — `#ef_question_en`,
`#ef_question_ur`, `#ef_correct_en`, `#ef_correct_ur`, `#ef_marks`, `#ef_answer_lines`,
`#ef_image_size`, `#efStripSearch`, `#efStripQType`, `#libPickerSearch`, `#libPickerQType`,
`#libPickerSize`. Every one sits inside the edit modal, topic strip or library picker, i.e.
`.no-print` chrome, so **their effect on the printed artefact is zero.**

**`@page` survives the layer import**, verified two independent ways: an import-aware CSSOM walk
finds `@page { size: a4; margin: 0px }` at `layer=legacy`, and all six PDFs carry an identical
A4 MediaBox (594.96 × 841.92) — had it stopped applying, `preferCSSPageSize` would have fallen
back to Letter.

**What is still NOT checked:** a **real printer**. Everything above is `Page.printToPDF`, which
is the right tool for measuring CSS and is not proof of what a physical print does. Check a real
print preview at the page edges before `print` is ever unheld.

**Three of nine pages are live on the new tree, not seven.** `slo` (UI-031a), `slo-health` and
`library` (UI-031b) are migrated. **Six now wait on Sprint 4**, each **HELD on Irfan's call**:
`landing` and `taqseem`, then `blueprint` (2026-08-04, on the checks alone, before any entry
file was written), then `bank` (2026-08-04) and `index` (2026-08-05), both of which were
migrated, measured in a browser and **reverted**, and finally `print` (2026-08-05), which was
**never swapped in the session that held it**. Their blocks are below, and **every one of the
six is at HEAD**: `blueprint`, `bank` and `index` carry their three `<link>`s including
`/static/theme.css`; `print` carries its two and still links its legacy file directly.

**UI-032 is closed and Sprint 3 ends at 3 of 9, not 4.** `print` was the last page that could
have landed in it; with that page held there is nothing left in the task, so Sprint 4 starts
from six held pages rather than five. **Read `D34` before planning it** — three of those six
need work no Sprint 4 task ID currently owns, and `print` does not change that count.

**What UI-032 meant at the time: `print`, and nothing else.** Both orphan checks said all three of
`bank`/`index`/`print` were repetitions of `slo-health`/`library` — rule exposure
**0 / 3 / 0**, token exposure **0 / 0 / 0** — and **two of the three were taken on that basis
and neither could ship.** **Read that as the warning it is: passing both checks is necessary
and not sufficient, for the fifth time in this epic** (`taqseem` on rules, `blueprint` on both
halves at once, `bank` on Urdu line-height, `index` on Urdu font-family and `.main`'s padding,
and now `print` — the last three measured by neither check). **`print` is the extreme case:
both its checks are 0, its migration was measured and approved on sight in a real Ctrl+P
preview, and it is still held.**

**`index` is HELD (2026-08-05).** Its entry file is parked at `docs/ui/parked-index.css` and
`index.html` is back on its three `<link>`s at HEAD. Two regressions stopped it, and both are
Sprint 4 component work rather than anything wrong with the page:

1. **The Urdu language toggle loses Nastaliq.** `03-elements/forms.css`:101
   `button { font-family: inherit }` is in `layer(elements)`; `99-legacy/index.css`:34
   `.urdu, .ur { font-family: 'Jameel Noori Nastaleeq', 'Noto Nastaliq Urdu', serif }` is in
   `layer(legacy)`. Layer order is decided before specificity, so the bare element rule wins and
   `index.html`:21's اردو button renders in the body's Latin sans. **This is D22's button reset
   arriving through the one declaration `forms.css`'s own header calls harmless** — and it lands
   on the control a teacher uses to put the app into Urdu.
2. **`.main` loses its padding and its scroll container.** `static/theme.css`:89
   `.main { grid-area: main; overflow: auto; padding: var(--pad) 28px 44px }` goes with the
   link, and `99-legacy/index.css`:73's own `.main` sets only `flex: 1; min-width: 0; display:
   flex; flex-direction: column`. Measured: the content area moves **28px left, 32px up, and
   grows 56px wider** on every screen. `grid-area: main → auto` is inert here (this page's shell
   is `.shell { display: flex }`, not the `.app` grid theme.css wrote that rule for); the
   padding and `overflow: auto` are not.

**Both were confirmed on screenshots before the call was made, and the second one looks worse
than its numbers read**: with the top padding gone the heading collides with the `.tag` chip —
which is the two findings compounding, since `.tag` has by then lost the background and radius
that gave it its own visual box. **The delta table alone did not say that.** It is the same
lesson `bank` wrote: the numbers say what moved, and only eyes say whether the page is still
right.

**Six of nine pages are now HELD** — `landing`, `taqseem`, `blueprint`, `bank`, `index` and
`print` — and none of them is a pending migration. **UI-032 has nothing left in it.**
(This line read "Five of nine … `print` is the only page left in UI-032" until `print` was
held on 2026-08-05. Corrected where it was written, per the rule UI-021 wrote about stale
counts — the epic's most-repeated failure is a number carried instead of re-counted.)

**`bank` is HELD, and the reason is not either orphan check.** Its entry file is parked at
`docs/ui/parked-bank.css` and `bank.html` is back on its three `<link>`s at HEAD. What stopped
it is what the **new tree** does to Urdu question text: `99-legacy/bank.css`:229
`.q-text .qt.rtl` sets `'Noto Nastaliq Urdu'` and a size but **no `line-height`**, so the line
box came from the font's own metrics — and `03-elements/typography.css`:41's
`body { line-height: var(--leading-body) }` is in `layer(elements)`, beats `layer(legacy)`, and
takes it over. Measured on the 24 Urdu-only questions in this DB: **38px → 21.75px, a 43%
cut**, on the one script in the app whose glyphs paint well outside their em box. Nothing
clips — no `.q-row`/`.q-text`/`.qt` sets `overflow` — so the failure mode is overlap and the
row's 14px padding absorbs some of it, which is why this needed **eyes and not a number**.
Irfan looked and held it: Nastaliq gets a proper look in Sprint 4, not a patch in a hurry.
**This is D21 firing on the first migrated page that actually renders Urdu** — `print` could
not exercise it, because no paper in this DB has Urdu question text.

`blueprint` is out of scope for the migration too; it is measured, held, and waiting with
`landing` and `taqseem`. **Nothing is parked for it — no entry file was written, per the rule
that the decision comes first.** Its exposure also turned out to be understated: see D32.

*(An earlier draft of this block said Sprint 3's migrations were "done as far as they can go"
and sent the next session to Sprint 4. That was wrong — it read the two HELD pages as the only
remainder and missed the four unmigrated ones. Corrected here rather than left, per the rule
UI-021 wrote about stale predictions.)*

**BOTH CHECKS HAVE NOW BEEN RUN ON ALL FOUR PAGES, and neither is prose any more — both are
`scripts/css_orphans.py`.** No file was migrated and no page's `<link>` was touched — the only
things this measurement wrote are the script, its browser driver, and this block. Re-run rather
than trusting the tables below; that is why it was written as a script and not as prose:

```
python scripts/css_orphans.py --names                       # tokens (check 1)
uvicorn app.main:app                                        # then, in another shell
python scripts/css_orphans.py --rules blueprint bank index print --paper-id <id> --names
```

`--rules` parses `static/theme.css`, runs every selector through `querySelectorAll` against
the live page in headless Edge (its own `--user-data-dir`, killed by the pid it spawned — the
UI-031a hazard), and subtracts what the page's own `99-legacy/<page>.css` redeclares. It
drives the browser through `scripts/css_rules_probe.mjs`.

### The result — four pages, both checks, one table

| page | theme? | tokens: supplied / compat | rules: match / redecl / partial / **orphan** | rule EXPOSURE | verdict |
|---|---|---:|---:|---:|---|
| `blueprint` | yes | 21 / 19 | 29 / 6 / 3 / **20** | **20** (19 + `:focus-visible`) | **HELD** |
| `bank` | yes | 0 / 0 | 6 / 3 / 2 / **1** | **0** — the one orphan is `:focus-visible`, which `03-elements/forms.css` declares | repetition — **yet HELD**, on something neither check measures |
| `index` | yes | 0 / 0 | 11 / 2 / 4 / **5** | **3** — `input[type=number]` and `:focus-visible` are both in `forms.css` | repetition — **yet HELD**, on two things neither check measures |
| `print` | **no** | 0 / 0 | 5 / 0 / 2 / **3** | **0** by D9 — the file is not linked, so all three already fail to apply today | clean on both checks — **yet HELD** (2026-08-05), like `bank` and `index` before it |

**This table's token column is STYLESHEET-ONLY, and D32 is the third column it does not have.**
Since 2026-08-08 `css_orphans.py` also reads inline `style=""` and reports it separately as
`mkRead` / `mkOrph` / `mkBare`. For these four pages: `blueprint` **9 markup reads with no
fallback** — `--accent`, `--accent-soft`, `--brand`, `--chip-bg`, `--fg`, `--green`,
`--green-bg`, `--muted`, `--red`, all `theme.css`-only — `bank` **1** (`--line`, fallback
present, so it drops silently rather than failing), `index` and `print` **0**. So
`blueprint`'s real exposure is 20 orphan rules **plus** 21 orphan tokens **plus** 9 bare markup
reads, and the "21 / 19" cell below understates it.

Measured at 1280×900 in **Edge 151** (this board said 150; the dev PC has moved). Every page
was probed **twice with no action in between and drift was 0 on all four**, and a second full
run from a fresh browser launch reproduced every number *and* every element count
(235 / 5378 / 508 / 555) — the determinism check UI-031b established, applied here to the
counts rather than to a diff. `static/theme.css` is **119 rule blocks**; the `:root` block is
excluded because everything in it is the token half's, leaving **118** probed.

**The unit is the rule block (`{}`), not the selector**, so these numbers are comparable with
`taqseem`'s hand measurement — `input[type=text], input[type=number], input[type=search],
select, textarea` is five selectors and one rule. **The method was validated against
`taqseem` before any new page was believed**: it reports 21 matched / 17 orphan where UI-031c
measured 20 / 16, and the whole of the difference is `:focus-visible`, a state-only rule with
no elements of its own that a `querySelectorAll` method can only report as universal and a
hand method never listed. Subtract it and the two agree exactly, including the redeclared
count. It is broken out as its own `state` column for that reason, and it applies identically
to all nine pages, so it is real but it is never a page's finding.

### `blueprint` — **HELD.** This board's "probably clean" was wrong, and it is worse than `taqseem`

**The prediction is corrected where it was made, not only here.** This block used to read: *its
own legacy file declares 10 `.btn` and 4 `.card` rules and it is the one page that already
carries `.pagehead` rules of its own, so the rule half is probably clean — probably is not
measured.* Measured: **20 orphan rules**, and they are the **entire application shell** —

`.app` (the grid itself: `grid-template-areas`, `grid-template-columns/rows`, `height:100vh`),
`.top` · `.top .crumbs` · `.top .crumbs b` · `.top .spacer` · `.top .avatar`,
`.nav` · `.nav .grp` · `.nav a` (×5) · `.nav a .icon` (×5) · `.nav a:hover` · `.nav a.active`,
`.brand .logo` · `.brand b` · `.brand small`, `.card > .ch` · `.card > .ch h3` · `.card > .cb`,
`.chip`, and `:focus-visible`.

Two more (`.app`, `.nav` inside `@media (max-width: 760px)`) are also redeclared nowhere; they
are reported separately because a page measured at one width cannot count them.
`blueprint.css` declares **no** `.app`, `.nav`, `.top`, `.ch`, `.cb` or `.chip` rule at all —
verified by grep, not inferred — its only mention of that shell is the dead
`@media` block D15 already records, which styles `.app-sidebar`/`.app-nav`, classes the markup
does not have. **Nothing in the new tree replaces them either**: `04-objects/shell.css` uses
`o-shell__*` names, which `blueprint.html`'s markup does not use, and none of the twenty
selectors above appears anywhere under `static/css/` outside `99-legacy/`.

**So `taqseem` lost its buttons and card chrome; `blueprint` would lose the grid that puts the
page together.** It is also the **first page exposed on both halves at once** — 21 orphan
tokens (19 needing a compat block) *and* 20 orphan rules. Both of its halves are already
solved on paper: `docs/ui/parked-taqseem.css`'s compatibility block covers its 19 tokens
(finding 4 of the token check), and the rule half needs Sprint 4's shell/nav components, which
is the same thing `taqseem` is waiting for.

**Taken to Irfan on 2026-08-04 and HELD** — the decision was made before any entry file was
written, which is why nothing is parked for this page and `blueprint.html` is untouched at
HEAD, still on its three `<link>`s. It resumes when Sprint 4's shell/nav components exist, and
its token half needs no new work: `parked-taqseem.css`'s block already covers all 19.

### `bank` — the cleanest page on both checks, and it still could not ship

366 lines, 5378 elements live, and only **6** of `static/theme.css`'s 118 rules reach it at
all. One is orphaned (`:focus-visible`) and `03-elements/forms.css` declares it, so **the rule
exposure is 0**. `bank.css`:80 declares `input[type="text"], input[type="number"], select,
textarea` itself. Both halves are clean; this is a repetition of `slo-health`/`library`.

Its two `partial` rules are the already-accepted deltas, below.

### `index` — **HELD.** Both checks were right about their own halves, and neither could see what stopped it

Three real orphan rules: **`.tag`** (×2), **`.row`** (×1), **`.summary-row:last-child`** (×1).
Each has a near-miss in `index.css` that does *not* cover it — `.brand .tag`:53 and
`.topbar .tag`:317 carry colour and size but not the chip's background, padding, radius or
family; `.topbar .row`:311 is more specific than theme's `.row` and already wins today. The
other two orphans (`input[type=number]`, `:focus-visible`) are in `forms.css`.

**All seven screens were measured**, not just the default one: `showScreen()` was driven
through `generate`, `mypapers`, `analytics`, `adaptive`, `results`, `settings`, `syllabus`, and
the counts are the union. The DOM grows **508 → 783** elements across them (the qadam-2 probe
recorded 771; the difference is this DB's paper list, not CSS — re-measured, not carried over).

**Measured before and after the swap**, in Edge 151 at 1280×900, over a property set of **58
fixed before measuring**: **5592 aligned elements across all seven screens plus the default
view, 32941 element × property deltas, 1053 distinct (element × property × before × after)
changes, 0 paths present in only one snapshot.** Render proven deterministic first — the
default view snapshotted twice with no action between, **drift 0**. Element counts fall by
exactly 1 per screen (508 → 507, 783 → 782): that is the removed `<link>`, itself an element,
the same −1 `taqseem` and `bank` recorded.

**The two regressions that stopped it are in the NEXT TASK block above.** What follows is
everything else the swap does, so that whoever resumes this page does not re-measure it:

- **`.summary-row` loses its dashed rule**, ×24 — `border-bottom: 1px dashed rgb(237,240,245)`
  → `0px none`. `index.css`:144 declares the selector and not the property, so a selector-only
  check calls this page clean. **This is the `partial` column being right**, and it was
  predicted here before the swap rather than found by it.
- **`.tag` loses its chip**, ×16 — `background-color rgb(220,245,244)` → transparent and all
  four radii `5px` → `0px`, leaving bare text where the badge was. The near-misses at
  `index.css`:53 and :317 carry colour and size only, exactly as the rule check said.
- **The white slab is gone for the fifth page running** — `.brand` in the navy sidebar, plus
  its text going white. Improvement, and by now a `static/theme.css` fact rather than a
  per-page quirk.
- **Base type and leading move as documented**: `font-size` 16px → 15px, `line-height` `normal`
  → 21.75px on **3978** element-instances (body's value, inherited). D21/D28, unchanged.
- **Nav icons 19px → 17px** and nav links re-coloured, the identical `slo-health`/`library`
  finding.

**One inline style turns out to be load-bearing, and Sprint 5 needs to know before it starts.**
The Urdu school-name field at `index.html`:443 keeps its Nastaliq **only** because the family is
written in an inline `style=""`, which outranks every layer. It is one of this page's 224 inline
attributes. `#hpUr`:470 is a `<div>` and keeps the family from `.urdu` because `forms.css`'s
rule is `button`. **Burning the inline attributes down without moving that family into CSS first
would take the settings field the same way the toggle went.**

**One gap, stated rather than papered over, exactly as `print`'s is:** the `.paper-sheet` live
preview **did not render in either snapshot** — the page was measured with no paper preview open
— so `index.css`:169 `.ph-ur` and :179 `.q-ur` were **not exercised in the browser**. Neither
declares a `line-height`; what is verified is that their ancestor `.paper-sheet`:165 declares
`line-height: 1.55`, so the `body` rule that took `bank` cannot reach them. That is a reading of
the cascade, not a measurement of the page, and it should be measured whenever this page
resumes.

### `print` — 0 by measurement, not by assumption

Three rules match its elements, and **all three are already inert**, because `print.html` does
not link `/static/theme.css` (D9 — the script measures the link rather than assuming it). A
migration cannot change them. Measured on a **real exam paper** (25 questions, 25 with images,
27 `<img>`, 555 elements), never a blank page. **One gap, stated rather than papered over:
none of the 21 papers in this DB has any Urdu question text**, so the Urdu half of that
instruction was not exercised — Urdu on this page can only come from the header and labels.

### `partial` — the column that caught what selector-equality gets wrong

A page redeclaring a *selector* does not mean it redeclares the *properties*. That direction of
error is the dangerous one, because it reports a page clean:

- **`.brand` is partial on all four pages** — theme.css:62 gives it `background`,
  `border-bottom`, `grid-area`, and the page's own rule does not. **This is the white slab**,
  removed on `slo`, `slo-health` and `library`, and the check found it independently rather
  than being told. Same for **`.brand small`** on `bank` and `print` (`text-transform`,
  `letter-spacing`, `opacity`) — the uppercase `slo-health` lost.
- **`index.css`:144 `.summary-row` has no `border-bottom`**, so the dashed rule between the
  rows goes with the link. A selector-only check calls that page clean.
- `blueprint` and `index` also lose `.main`'s `grid-area`, `overflow` and `padding`, and
  `blueprint` `.pagehead p`'s `margin-top`/`max-width`.

These are per-selector, so a property could still arrive from a *different* legacy selector
matching the same element. The check is deliberately conservative in that direction; the
migration task's before/after diff is what settles each one.

### Two bugs in the script, both of which moved real numbers

Recorded because both were found by cross-checking a result against the files, which is the
only reason the table above is not wrong:

1. **`input[type=text]` vs `input[type="text"]`.** `static/theme.css` writes the attribute
   value unquoted and both `forms.css` and the legacy files quote it. Normalised naively the
   same rule reads as two, and a page reports an orphan it does not have: **`blueprint` 21 → 20
   and `bank` 2 → 1** once attribute quotes were normalised away.
2. **No property-level check at all**, which produced the false *safe* described above. The
   `partial` column is the fix.

### What did NOT render, and why it does not move the numbers

`blueprint` was measured in its default empty state — no class/subject/exam chosen, `#secList`
holding one empty-state child and `#bpList` two — so its section builder never rendered. That
is **not** a lower bound on its theme.css exposure, and this was measured rather than assumed:
**`blueprint`'s JavaScript assigns no `static/theme.css` class at all.** 44 class tokens were
extracted from its script (the control that proves the extraction works), and the intersection
with theme.css's class names is empty; its one dynamically-built class resolves to
`bg-under`/`bg-over`/`''`. The same holds for `bank` (26 tokens) and `print` (42). `index` has
six — `card`, `bar`, `num`, `sub`, `ur`, `urdu` — of which `card` is already counted and the
rest are inert: `.stat .bar`/`.stat .num`/`.stat .sub` need a `.stat` ancestor and
`.langsw button.ur` a `.langsw`, and neither class exists on any of the four pages. All nine
dynamic class sites across the four pages were read individually; every value is a page-local
name (`q-bad`, `q-review`, `q-good`, `qt rtl`, `img-sm`, `type-badge`).

`bank`'s modals are in the DOM but closed (`[data-open="1"]` is 0), and `index` carries one
closed modal — `querySelectorAll` sees them either way.

**Worth knowing for Sprint 6:** `static/theme.css`'s whole component library matches **zero**
elements on all four pages — `.sec`, `.qrow`, `.pin`, `.switch`, `.segbtns`, `.bloom`, `.stat`,
`.badge`, `.tbl`, `.grid`, `.toolbar`, `.field`, `.panel-soft`, `.langsw` — including the block
commented "section builder (blueprint)". It was written for the mockup, not for the live pages.

### What is otherwise still true of each page

- **`blueprint`** — the first already-token-clean page (UI-015): its `:root` aliases onto
  `static/theme.css` tokens, which is exactly the D20 shape. Its own file declares 10 `.btn`
  and 4 `.card` rules, and it does carry its own `.pagehead` — none of which was enough, see
  above.
- **`bank`** — 366 lines, 62 raw hex.
- **`index`** — an SPA: 7 screens via `showScreen()`, sidebar with `onclick` rather than
  `href`, and 224 of the project's 466 inline `style=""` attrs. Sprint 5's burn-down is NOT to
  be started here; the inline values must come out byte-identical.
- **`print`** — only 2 `<link>`s, and it is the **Ctrl+P page**, the highest-consequence one
  in the epic. Whatever else is true, its output is re-checked on a real exam paper.

**`landing` is HELD, not pending — do not just migrate it.** It was built, measured and passed
its gates, then held on Irfan's call because it visibly degrades the app's front door: this
page's legacy `h1` is the largest in the project and the new tree's is smaller, so the hero
headline shrinks and `reset.css` zeroes the 12px gap beneath it, leaving the title jammed
against the paragraph. **This sentence said "shrinks from two lines to one" until 2026-08-07,
when UI-045 measured it: the headline stays at two lines in both states** — 30px/36px/72px at
HEAD, 24px/26.4px/52.78px migrated, and 52.78 ÷ 26.4 is two lines exactly, because
`max-width: 640px` holds the wrap. The shrink and the dead gap are real; the reflow was not. Its finished entry file is parked at
`docs/ui/parked-landing.css` with the full measurement and restore instructions in its header —
**read that before touching this page.** The real fix is a hero/display type step, which is
Sprint 4's typography work, so landing should resume *after* that lands, not before. **Note
that no Sprint 4 task currently owns it:** `PLAN.md`:195-198 gives UI-040..043 as card,
button, modal/field and tables/domain — a display type step is in none of them, so it needs
either an ID of its own or an explicit home inside one before landing can resume. It also
loses its `.icon` override (22px → 17px on 11 icons) the moment its file becomes layered,
because `app.css` is unlayered and beats it — the first time UI-031a's warning about that
actually fired.

**`taqseem` is HELD too, and the finding is bigger than the D20 it was carved out for.** It was
taken as a token problem — its legacy file reads `static/theme.css` tokens with no fallback —
and that half went exactly as planned: the real count is **26 read-but-never-declared** (this
board said 20; corrected by measurement), **3** of which (`--font-display`, `--font-body`,
`--font-data`) Tier 2 already declares under the deliberate collision, leaving **23** for a
compatibility block. All 23 map 1:1 onto existing Tier 2 roles with **no value change and no
literal**, declared names collide with `01-settings/` **zero** times, and the block was
verified in the browser: all 23 resolve, none empty. That file exists and works.

**It was held because the page also borrows RULES from `static/theme.css`, not just tokens —
and no grep over custom properties can see that.** Measured against the live DOM: **20**
`static/theme.css` rules match elements on this page and **16 of them are not redeclared
anywhere in `99-legacy/taqseem.css`** — `.btn`, `.btn.gold`, `.btn.ghost`, `.btn:hover`,
`.btn:disabled`, `.card`, `.card.has-ch`, `.card > .ch`, `.card > .ch h3`, `.card > .cb`,
`.pagehead`, `.pagehead h1`, `.pagehead p`, and two `input`/`:focus` rules. Dropping the link
therefore does not "remove theme.css bleed" here, it **removes the page's buttons and card
chrome**: measured after the swap, the three `.btn`s fell all the way back to UA default
(background `rgb(240,240,240)`, 2px border, padding 1px 6px, `display:block`, weight 400,
radius 0) and `.card`'s `box-shadow` went to `none`. The new tree has no replacement yet —
`.btn`/`.card` are Sprint 4 components and D22 parks the button reset until UI-041.

**This is a property of `taqseem` alone, and that is why three clean pages made it look
routine.** Counted per legacy file: `slo` declares 5 `.btn` and 3 `.card` rules of its own,
`slo-health` 2 and 3, `library` 13 and 3, `blueprint` 10 and 4 — **`taqseem` declares 0 and 0**
and leaned entirely on the shared stylesheet. The markup uses all of them (`btn gold` ×2,
`btn ghost`, `card has-ch`, `pagehead`).

**So the check this board prescribed was necessary but NOT sufficient, and that is the lesson
to carry to `blueprint` and every remaining page.** Two greps over `var()` and `--name:` decide
the *token* question only. The rule question is a different measurement and needs the DOM:
parse `static/theme.css`, run each selector through `querySelectorAll` on the live page, and
subtract the selectors the page's own legacy file redeclares. **Run both before deciding any
page.** That measurement is now `scripts/css_orphans.py --rules`, and it has been run on all
four remaining pages — see the NEXT TASK block above.

**This paragraph used to end: *"`blueprint` is the next page that will meet this (D20 lists it
at 17 orphan tokens) and its `.btn`/`.card` counts above say the rule half is probably clean
there — probably is not measured, so measure it."* It was measured, and the prediction was
wrong in both halves.** Its tokens are **21**, not 17, and its rule half is not clean but
**20 orphan rules — the whole application shell**, `.app` grid included. The `.btn`/`.card`
counts were a real signal about buttons and cards and said nothing about the shell, which is
the part `blueprint` borrows. `taqseem` 0/0 was the loudest case of a general fact, not the
only case. Detail and the full list are in the NEXT TASK block.

**The work already done is not wasted, and it is parked exactly like landing's:**
`docs/ui/parked-taqseem.css` carries the two `@import`s and the 23-token compatibility block,
ratchet-clean (no raw hex), with the restore instructions in its header — **read that header
before touching this page.** It sits in `docs/` for the same reason
`docs/ui/parked-landing.css` does: anything under `static/css/` counts toward
`shared_css_lines` even when no page links it, so leaving it in place would let the next
task's `--write` bury 61 unlinked lines inside its own number. `shared_css_lines` is therefore
back at **1616** and `BASELINE.json` was not re-pinned — nothing shipped. `taqseem.html` is
untouched at HEAD, still on its three `<link>`s.

**`blueprint` is the third HELD page, and it is the largest of the three.** Held on Irfan's
call on 2026-08-04, straight off the measurement, **before any entry file was written** — so
unlike `landing` and `taqseem` there is nothing parked for it and nothing to restore;
`blueprint.html` is untouched at HEAD on its three `<link>`s. It is the only page exposed on
**both** halves at once: 21 orphan tokens (19 needing a compat block) **and** 20 orphan rules
that are the entire application shell, `.app`'s grid included. Where `taqseem` loses its
buttons and card chrome, `blueprint` loses the layout. Both halves are already answered on
paper — `docs/ui/parked-taqseem.css`'s block covers its 19 tokens as an exact subset, and the
rule half is the same Sprint 4 shell/nav work `taqseem` waits on — so this is a scheduling
hold, not an unsolved problem. **All three held pages resume after Sprint 4, and none of them
is a pending migration: do not just migrate them.**

**The shape, decided in UI-031a and not to be relitigated:** each page gets a two-line entry
file `static/css/pages/<page>.css` — `@import url("../main.css");` then
`@import url("../99-legacy/<page>.css") layer(legacy);` — and its `<link>` block becomes
`app.css` + that entry file. `main.css` no longer imports any legacy file. Copy
`pages/slo.css`, read its header first; it documents why each line is what it is.

**Do them one at a time, with a browser open, and measure per page before writing:**

- **Run the orphan-token check first — two greps — but know that it decides only HALF the
  page.** Collect the names the page's `99-legacy/<page>.css` *declares* and the names it
  *reads via `var()`*; the set it reads but does not declare is the D20 exposure. `slo` **0**,
  `slo-health` **0**, `library` **0**, `taqseem` **26** (this line said 20 until `taqseem` was
  measured). Also diff its declared names against `01-settings/tokens.css` +
  `01-settings/theme.css` together — a shared name means the token changes owner when the tree
  arrives. Zero collisions on all four pages checked so far.
- **Then run the orphan-RULE check, which is the half that held `taqseem`.** A page can borrow
  whole rules from `static/theme.css`, not just token values, and no grep over custom
  properties will show it. Parse `static/theme.css`, run every selector through
  `querySelectorAll` against the live page, and subtract the selectors the page's own legacy
  file redeclares — what is left disappears the moment the link goes. `taqseem`: **16**
  (`.btn*`, `.card*`, `.pagehead*`, two `input`/`:focus`), which is its whole button and card
  chrome. Cheap sanity check before the browser work: `.btn`/`.card` rule counts per legacy
  file — `slo` 5/3, `slo-health` 2/3, `library` 13/3, `blueprint` 10/4, **`taqseem` 0/0**.
- **Diff every page against BOTH mechanisms**, not just one — see `pages/slo.css`'s
  "WHAT ACTUALLY CHANGED" block. (1) `static/theme.css` bleed being removed, which is
  per-page and unpredictable: on `slo` it took a **white slab** out of the navy sidebar and
  un-flexed 115 badges; on `slo-health` the **same white slab** was sitting there too and is
  now gone, along with the uppercase and letter-spacing theme.css was putting on `.brand
  small`. Two for two: treat the slab as a `static/theme.css` fact, not a `slo` quirk. (2) The new tree beating `layer(legacy)` — D21, live: `reset.css`
  zeroes legacy class margins, `typography.css` grows `h1`/`h2`, `forms.css` re-fonts buttons.
- **Bare element selectors in `layer(elements)` reach further than the class rules suggest.**
  `slo-health` found two the review of `slo` did not name: `typography.css`'s `a { color:
  inherit }` beat legacy's `.app-nav a` colour, turning **all six** inactive nav links white
  (the active one already was), so active/inactive now differ only by background and left
  border; and `small { }` beat `.brand small`, taking the sidebar subtitle's size and colour.
  Check `a`, `small`, `th`, `td`, `h1`, `h2` against the page's own class rules on every page.
- **Prove the render is deterministic before you diff it.** Two identical before-snapshots,
  then compare. `slo-health` was 191 elements with **0** run-to-run drift; without that check a
  data-driven page's jitter reads as a CSS delta. And **align out the `<link>` you removed** —
  it is itself an element in `querySelectorAll("*")`, so the count legitimately drops by one.
- **Define the property set before quoting any aggregate**, or do not quote one (the rule
  `pages/slo.css` states, after two counts of the same migration disagreed). `slo-health`:
  **1463** element × property deltas over a set of 36 properties fixed in advance.
- **Measure the backdrop, never assume it** — the single most repeated failure on this epic
  (D26's first draft, and three more like it). On `slo-health` the subtitle's *before* backdrop
  was the white slab, not the navy sidebar, which flips the sign of the result: **2.20:1 →
  3.04:1, an improvement**, still under AA. Table `th` went the other way, **5.81:1 → 4.60:1**,
  which clears AA by 0.1 — worth knowing before someone "tidies" `--color-text-muted`.
- **A page renders less than you think.** `slo-health`'s measurement covers only what the
  current DB produced: four cards sat in empty states and the `.cov-*` blocks never rendered at
  all (they need a class + subject + exam chosen). Say which parts you did *not* measure in the
  handover, and put them in the click-list.
- **`landing.html` has no `theme.css` and no sidebar** (D9) — expect a different delta shape.
- **`library.css` carries `--text`, which is defined nowhere** (D14). Inert today; confirm it
  stays inert rather than assuming.
- **`app.css` stays linked** on every migrated page until Sprint 4 — it owns `.icon`.
- **Quote FULL PATHS in the handover click-list** (D29). Two files are named `theme.css` and
  the Network panel shows only the basename; the bare word cost a false alarm on UI-031a.

**Not carried over from UI-031a, deliberately:** `config/nav.json` was **not** rendered and
no `o-shell__*` class was added to the markup — the page's own legacy file still lays out and
paints its sidebar, so the shell object applies to nothing. Sprint 4's nav component is what
consumes both. Do the same here unless there is a reason not to; adding markup multiplies the
diff and the frozen-inventory risk across every page it touches. `slo-health` held to it: the
only bytes that moved were its `<link>` block, **−53**, and the frozen inventory (19), class
attributes (74) and all three `<script>` bodies came out identical.

**Still open from UI-030:** the `<760px` breakpoint is not in `shell.css` — it hides the nav
and the toggle that gives it back is a Sprint 4 component. Untested on a migrated page so far.

---

## Previous task → **UI-031a** — `slo.html` onto the new tree · **the first live page**

**`@layer` has now been parsed by a browser**, and the cascade this epic is built on resolved
on a real page for the first time. Verified in headless Edge 150 via CDP: the
`CSSLayerStatementRule` carries all seven names in order, every import lands in its declared
layer, and `99-legacy/slo.css` arrives in `layer(legacy)` rather than unlayered. Blocked item
1 (the school PC) is **still open** — this is the dev PC.

**D19 was resolved by changing the load mechanism, and the documented shape would have broken
the page.** Measured before writing: `main.css` imported all nine legacy files, they import
alphabetically, so `taqseem.css` is last and won **15 selectors** off `slo` — `:root`,
`.app-sidebar`, `.brand`, `.brand .name`, `.brand small`, `.app-nav`, `.app-nav a`,
`.app-nav a.active`, `.sidebar-foot`, `.row`, `body`, `html, body`, `a`, `*`. Every value it
brought reads a `static/theme.css` token that the same task unlinks, so "drop `theme.css`,
link `main.css`" would have shipped an **unpainted sidebar and no border colours**, through a
file belonging to a different page — **D20 arriving by the back door**, on the one page whose
own tokens are all local literals. So the legacy import moved out of `main.css` and into a
per-page entry file. `main.css` keeps the layer order and the shared tree and remains the
single source of the cascade (exactly one layer statement in the document).

**`CLAUDE.md` §11's link rule changed with it** — the `<link>` now goes to
`/static/css/pages/<page>.css`, not `main.css` directly. Recorded as unplanned in both the
rule and the file headers.

**Three visible changes nobody predicted, all `static/theme.css` bleed being removed**: the
`.brand` block had a **white slab** inside the navy sidebar (`theme.css`:62 paints it, because
there `.brand` is a cell in the `.app` topbar grid and this page has no `.app`); `.bloom` was
`display:flex` on 115 badges from a **bar-chart component** meant for another page; nav links
were the wrong grey. All three are fixes, and the first is why D26's first draft was wrong.

**Four rounds of review FAILED this, and the three real failures are one shape: a number
asserted instead of measured.** (1) D26 computed a contrast ratio against an *assumed* navy
backdrop — both colours were measured in the browser, the backdrop was not; the real figure is
**1.70:1 → 3.04:1, an improvement**, not the "6.59 → 3.04 regression" first written. (2) The
"what changed" block named only one mechanism, missing **D21 firing live** — `reset.css`
zeroing `.card .hint`'s 16px, `typography.css` taking `h1` to 24px, `forms.css` taking buttons
off Arial. (3) Four line numbers were inherited rather than checked: `forms.css:58` is the
input/select/textarea rule and **cannot match a button** (:101-102 does), `:102` is not the
border (:62 is), `reset.css`'s `margin:0` is at :91. **All three are recorded in the files as
failed drafts**, so the next session meets the trap, not just the answer. An aggregate
delta count was **removed rather than corrected**: two independent measurements disagreed
because they used different property sets, so the files now give affected *elements* per rule,
which is re-derivable from markup with a grep.

**A hex in a comment tripped the ratchet — and `--write` nearly laundered it.** Quoting two
border colours in prose took `unsanctioned_hex` **429 → 431**; because `css_baseline.py
--write` had already run, the raised number was pinned into `BASELINE.json` and `--check` then
reported OK against the laundered baseline. Fixed by removing the hex and
`git checkout docs/ui/BASELINE.json` before re-pinning. **Re-pin only after `--check` passes
against HEAD's baseline, never before.** The reviewer mutation-tested the guard afterwards
(hex restored → 429 → 431, exit 1).

**Irfan's browser check found a fourth false alarm, and was right to stop on it.** `theme.css`
appeared in the Network panel with initiator `main.css:87`. **Two different files carry that
basename**: `/static/theme.css` (13787 B, the old stylesheet, genuinely gone from this page)
and `/static/css/01-settings/theme.css` (8682 B, the Tier 2 palette, which must load). The
handover said "theme.css gone" instead of naming the path. **D29** records it; quote full
paths from here.

**Three visible changes ship with this page and are Irfan's accepted trade** — all with a
Sprint 4 home, none fixable inside a task scoped to one page's `<link>` block: **D26** the
sidebar subtitle at 3.04:1 (better than before, still under AA), **D27** `<a class="btn-ghost">`
losing its blue while `<button class="btn-ghost">` keeps it, **D28** cards visibly tighter —
headings ~20% bigger with the gap beneath them gone.

---

## Previous task → UI-030 — **`04-objects/shell.css` + nav config; still no page touched**

`.o-shell__*`, layout only, zero cosmetics, plus `config/nav.json` as data that nothing reads
yet. **Two reviews FAILED it**, the second on errors introduced by the first round of fixes
(see the task log). The finding worth carrying: **every one of the mockup's shell class names is
already taken**, and in two different ways — `.brand` (nine legacy files), `.main` (two) and
`.spacer` (one) sit in `layer(legacy)` and would be **silently overridden** by `layer(objects)`,
while `.app`/`.top`/`.nav` are in unlayered `static/theme.css` and *beat* the new layer instead.
Three and three. The `o-*` prefix (`PLAN.md`:125) is what makes the file safe, not tidiness —
and putting `.spacer` on the wrong side of that split is exactly what the second review caught.

**D21's height half is closed as unnecessary, not deferred again.** `html, body { height: 100% }`
was predicted to be UI-030's to land; it never landed, because `.o-shell` uses `height: 100vh`,
which needs no percentage chain from `body`. The design target carries both and only the second
is load-bearing. **`print.html` is therefore untouched** — the risk D21 existed to flag is not
taken at all.

**`--weight-medium` (500) did NOT land here either**, against the board's own prediction:
`04-objects` is layout-only and cannot consume a weight. It lands with `05-components/nav.css`
in Sprint 4. Both stale predictions were corrected where they were written, not just here.

**Sprint 3 (UI-031/032) is where the traps are: D19, D20 and now D21/D22 are one decision.**
`blueprint.html` and `taqseem.html` are the two pages that actually break (D20: 17 and 20
orphaned tokens, none fallback-protected). Add to that list, all landing in the same session:
base type goes **16px → 15px on nine pages** (`typography.css` `body`), `slo`/`slo-health`
tables take the design target's metrics (`tables.css`), and the button appearance reset is
still parked in **UI-041** (D22) so it does *not* land with them.

---

## The pre-Sprint-3 browser session — **done 2026-07-31**, with one item still open

Ran after UI-021, before any page's `<link>` changed — the point being that a revert was still
cheap. Two halves: Irfan in a real browser, and an agent over live HTTP against
`uvicorn app.main:app` on `127.0.0.1:8000`.

**Closed — Irfan, in the browser:**

- **`print.html` Ctrl+P: margin ~14mm, not 28mm.** Checked on a **real exam paper** (Pre Year 1
  Math), not a blank page — **Urdu, images and page breaks all correct**. This was the epic's
  highest-risk unknown and it is now closed for Sprint 1's extraction. *(This block warned that
  it was not closed for UI-030, "which lands `html, body { height: 100% }` on a page that has no
  such rule today". **UI-030 never landed that rule** — `.o-shell` uses `height: 100vh` instead,
  so print.html was not touched and D21's height half is closed as unnecessary.)*
- **All nine pages load styled** — `slo`, `slo-health`, `taqseem`, `landing`, `library`,
  `blueprint`, `bank`, `index`, `print`. No unstyled flash, no broken layout.

**Closed — over live HTTP:**

- Nine pages **200**, each with **0 `<style>` blocks** — Sprint 1 verified live, not just on disk.
- Every referenced stylesheet **200 / `text/css`**; no 404. `landing` and `print` carry 2 sheets
  (no `theme.css` — D9 live-confirmed), the other seven carry 3.
- **`main.css` is linked by zero of the nine** — "zero visual effect" is now a measurement.
- All 16 live `@import`s in `main.css` resolve **200** in their declared layer order.
- **All nine `woff2` return 200 through the `../../fonts/` relative path.** Better evidence than
  UI-021's disk check: `url()` actually resolved through the server. The one silent-404 risk the
  new tree introduced is closed.
- Dev PC: **Edge 150.0.4078.96, Chrome 150.0.7871.187** — both far past ADR-001's floor of 99.

**STILL OPEN, and do not let this board be read as saying otherwise:**

1. **The school PC's Edge version.** Irfan checks later. ADR-001 accepts `@layer`'s hard-fail
   risk *purely* on Edge auto-updating, and that is still untested on the machine that matters.
2. **No browser has ever parsed `main.css`.** "The pages didn't break" does **not** evidence
   `@layer` working, because no page loads `main.css` — that result is equally consistent with
   the `@layer` line never having been read. What actually retires the risk is the version
   numbers above (`@layer` shipped in 99; these are 150), plus the first page that links
   `main.css` in **UI-031**. Treat the cascade this epic is built on as *unobserved* until then:
   layer order beating specificity, `layer(elements)` overriding legacy classes, and D19/D20/D21
   all resolve for the first time on a real page in that task. **Open UI-031 with a browser.**

---

## Previous task → UI-021 — **done; Sprint 2 foundation complete**

**UI-021** (`docs/ui/PLAN.md` §Sprint-2): `02-generic` reset + fonts + `03-elements`
typography / forms / tables. Five new files, `main.css`'s five `@import`s uncommented in
place, **not one `.html` byte touched**. Same shape as UI-020, same zero visual effect.

**The one thing a fresh session must take from it: a "reset" in this tree is not neutral.**
`layer(generic)` and `layer(elements)` both **outrank `layer(legacy)`**, and layer order beats
selector specificity — so a bare element selector in the new tree overrides a *class* rule in
any of the 2115 legacy lines. That is what "legacy demoted" buys, and it is also what makes a
carelessly-ported reset destructive. UI-021 shipped a reset *smaller* than the design target's
for exactly this reason (**D21**), and parked the button appearance reset entirely (**D22**).
No ratchet metric sees this class of break — it counts lines and hex, not whether a list still
indents.

---

## Earlier → UI-020 — **done; the ratchet was ready for it**

**Sprint 1 is complete.** All nine pages load their CSS from `static/css/99-legacy/`.
`style_blocks` **0** · `css_lines_in_html` **0** · `hardcoded_hex` **0** ·
`legacy_css_lines` **2115** across nine files. Not one colour was deleted getting here —
`unsanctioned_hex` is still **429**, exactly where it started. The debt is fully
relocated and none of it is yet repaid. **That is the point.** Sprint 2 begins the
foundation the burn-down needs; the repayment itself is Sprints 5–6.

**UI-020a is done** (see the task log): the hex ratchet now distinguishes the sanctioned Tier 1
palette from everything else, which is what makes UI-020 writable at all. Do not relitigate it.

**UI-020** (`docs/ui/PLAN.md` §Sprint-2): `main.css` + import order + legacy demoted +
`01-settings` 3-tier tokens (Modern palette). Read PLAN.md and ADR-001 before planning —
this is the first task that *authors* CSS rather than moving it, so the rules that governed
Sprint 1 no longer all apply. Expect ADR-001's `@layer` decision (locked 2026-07-28) to
matter here for the first time.

**The contract changes shape at UI-020, and the metrics change with it.** Sprint 1's
invariant was "`total_css_lines` falls by exactly 2, nothing else moves." That is over.
UI-020 *adds* files under `static/css/`, so **`shared_css_lines` must rise** — it has been
flat at 269 through nine tasks and a rise was a FAIL every time. From here it is expected.
Re-read the ratchet's notes below before assuming a moving number is a defect, and set the
expected movement in the plan **before** writing, so the review agent has something to hold
you to.

**What UI-020 must get right, beyond the obvious:**

- **`unsanctioned_hex` must stay flat at 429.** Authoring `tokens.css` raises
  `total_hardcoded_hex` and `token_hex` together and leaves `unsanctioned_hex` alone — that
  is ratchet-neutral and correct. But **any raw hex in `01-settings/theme.css` (Tier 2) will
  fail**, because only `tokens.css` is exempt. Tier 2 reads `var(--tier-1)`, never a literal.
- **Author `tokens.css` one declaration per line.** `PLAN.md` §2's example is a single line,
  which satisfies `test_tokens_file_holds_only_token_hex` vacuously (D17).
- **`total_css_lines` and `legacy_css_lines` stay at 2115.** `01-settings/` is not
  `99-legacy/`; the new tree lands in `shared_css_lines`.
- **No page head is touched.** The single `<link>` to `main.css` is **Sprint 3** (§11 marks
  that rule end-state). UI-020 therefore has zero visual effect by construction.
- `git add static/css/` **explicitly** — new files there are not staged by adding modified
  files alone.
- After UI-020, `test_tokens_file_holds_only_token_hex` stops skipping: expect **906 passed,
  0 skipped**, not 905/1.

Still true, and still the thing that catches real mistakes: `unsanctioned_hex` may only
fall by genuine deletion, and no page may gain a `<style>` block.

---

## Progress

`99-legacy/` lines remaining is the real progress metric. **2133 → 0.**

| Sprint | Tasks | Done | State |
|---|---|---|---|
| 0 Guardrails | UI-000..003 | **4/4** | **done** |
| 1 Extraction | UI-010..018 | **9/9** | **done** |
| 2 Foundation | UI-020..021 | **2/2** | **done** |
| 3 Shell | UI-030..032 | **2/3** | in progress — **UI-032's MEASUREMENT is done (both checks, all four pages, 2026-08-04) but no page is migrated**; those four are still on their old `<link>`s. Verdicts: `bank` and `index` are repetitions, `print` is 0 by D9, and **`blueprint` measures like a fourth held page** — 21 orphan tokens *and* 20 orphan rules, the whole `.app`/`.top`/`.nav` shell, so it needs Irfan and Sprint 4's components, not an entry file. UI-031: `slo`, `slo-health`, `library` live; **`landing` HELD** (hero regression, resumes after Sprint 4 typography) and **`taqseem` HELD** as UI-031c (16 orphan RULES — its buttons and cards live only in `static/theme.css`; resumes after Sprint 4 components). Both measured, neither to be re-attempted before Sprint 4 |
| 4 Components | UI-040..046 | **4/7** | in progress — **UI-044a, UI-044b, UI-041, UI-045 and UI-040 done, all five PREPARED-NOT-LIVE**; **none released a held page, including UI-045, which the board predicted would release `landing` and does not** (D34's pattern again — `landing`'s second blocker is the icons, and **no component task can fix it**: `UI-047d`). Next: **UI-041b**, then UI-046, UI-042, UI-043 |
| 4b Migrations | UI-047a..f | **3/6** | **`UI-047f` `print` LIVE 2026-08-11 — and it is the first page in this epic unheld by a physical printer rather than a probe.** Irfan printed all three papers: edges inside, slate ink clean, and `0d04c750` at **2 pages, not 3**. **D36 and D33 are both Resolved.** D36's parked fix (`@media print { body { line-height: normal } }`) went live with the migration and held at **2 / 6 / 7**, measured once before the D33 selector landed and again after. D33's selector — `.letterhead .school-ur` — was added to `05-components/urdu.css` in this commit, exactly as that file's header instructed, **and then VERIFIED ON PAPER the same day**: `school_name_ur` was temporarily filled with a real Nastaliq string, all three papers printed, and Irfan confirmed the letterhead sits on its own clean line with no overlap. Measured beside it: box **47px**, ink **47px**. The field was restored to empty afterwards — the string used was an invented transliteration, not AII's registered name. **Two findings came out of that test, neither predicted.** (1) **Page counts are data-dependent — `2/6/7` assumes an empty Urdu name; filled, it is `3/6/7`** — the cause is the extra 47px letterhead line, not any CSS fix, proven by re-measuring with the D33 selector removed (3 pages either way). That is **D38**. (2) **D33's own framing was incomplete**: in print media the letterhead already inherits `normal` from UI-044b's `@media print { body { line-height: normal } }`, so the `urdu.css` selector is **redundant in print** and earns its place on **screen** — the second half read from the cascade, not measured. Print-media deltas HEAD → migrated: **~669–735 per paper, of which `color` is 416–502** — F1, the ink change, the only thing that reaches the printed artefact. The 5 `<a>` deltas are sidebar nav links inside `aside.app-sidebar`, which is `display:none` in print: **zero effect on paper.** `shared_css_lines` 2322 → **2520**, `unsanctioned_hex` flat at 429, pytest 906, ruff clean, 0 deltas on all five other pages. Next: `UI-047a` `taqseem`, in a fresh session. — earlier: **`UI-047d` `landing` LIVE 2026-08-10** — first page opened since Sprint 3; 279 deltas, hero restored to HEAD exactly, 11 icons 22px → 17px on Irfan's decision (A); 0 deltas on every other page. **`UI-047e` `bank` LIVE 2026-08-10** — 17800 deltas, 5378 → 5377 elements (the removed `<link>`), **and the Urdu it was held on did not move: 24 questions, `normal`/38px before and after**, because UI-044a's `urdu.css` finally reached real markup. D31 answered **B**: `--color-text-muted-strong` (`--slate-600`), two labels 4.44 → 7.07. **This one changed a LIVE page deliberately** — `library`'s 44 labels, 220 deltas, nothing else; `slo`/`slo-health`/`landing` 0. `shared_css_lines` 2022 → **2263**, `unsanctioned_hex` flat at 429 throughout, pytest 906, ruff clean, drift 0. Next: `UI-047f` `print`, which needs only a printer check |
| 5 Inline burn-down | UI-050..052 | 0/3 | not started |
| 6 Legacy kill | UI-060..064 | 0/5 | not started |
| 7 Optional | UI-070 | 0/1 | not started |

### Task log

| ID | Task | Status | Commit | Note |
|---|---|---|---|---|
| UI-000 | Commit baseline, tag, branch | **done** | `addb2fb`, `985f47b` | tagged `ui-baseline`; tree had been dirty (theme.css Modern rewrite + 7 link lines + untracked mockups) |
| UI-001 | Planning docs + CLAUDE.md §11–12 | **done** | `6c381fa` | this document set |
| UI-002 | Ratchet test + BASELINE.json | **done** | `b215666` | 26 tests, 900 passed. 3 extra metrics added (see below). Reviewed twice; 2nd pass found the JS-class check is JS-side only → D11 |
| UI-003 | Remove dead `primary`/`navy` from brand config | **done** | `2eba2f8` | closes D6. Re-verified unused at implementation. Also fixed `api/brand.py` docstring; logo.svg's same hex → D13 |
| UI-010 | Extract `slo.html` CSS → `99-legacy/slo.css` | **done** | `cbd567a` | 91 lines moved verbatim, two reviewers byte-compared. Fixed 2 ratchet defects the first real extraction exposed: `hardcoded_hex` blind to `.css` files → added `total_hardcoded_hex`; a ratchet test anchored to `baseline` broke once a metric legitimately moved |
| UI-011 | Extract `slo-health.html` CSS → `99-legacy/slo-health.css` | **done** | `c05da55` | 111 lines moved verbatim; byte-compared against the original `<style>` inner, exact match at 5754 chars. Metrics landed exactly as predicted. Was built in a prior session but left **uncommitted** — caught at the start of UI-012, verified and committed then |
| UI-012 | Extract `taqseem.html` CSS → `99-legacy/taqseem.css` | **done** | `93f51b9` | 115 lines moved verbatim (6482 chars, exact match). Reviewer substituted the block back in at the `<link>` site and reconstructed `HEAD` byte-for-byte — proves both the verbatim cut and that nothing outside the block moved. Metrics landed exactly as predicted |
| UI-013 | Extract `landing.html` CSS → `99-legacy/landing.css` | **done** | `a9e876c` | 100 lines moved verbatim (3766 chars, exact match); `HEAD` reconstructed byte-for-byte. **This page had no `theme.css` link** — head one line shorter, so the `<link>` went to line 8; none was added, since adding one is a visual change. Metrics landed exactly as predicted |
| UI-013a | `CLAUDE.md` §11 — mark hard rules as end-state | **done** | `4a56b5b` | Docs only, no metric movement. §11's "one `<link>` per page" and "raw hex = CI failure" read as flat rules, but every Sprint 1 page necessarily breaks both in transit — a fresh session could "fix" it mid-sprint and revert a reviewed extraction. Adds an END-STATE preamble and marks the three affected rules with the sprint that retires each. Raised by UI-012's reviewer; committed separately so the extraction diff stayed reviewable |
| UI-014 | Extract `library.html` CSS → `99-legacy/library.css` | **done** | `19448a6` | 251 lines moved verbatim (11677 chars, exact match); `HEAD` reconstructed byte-for-byte at all **67668 bytes**. Largest extraction so far, 2.5× UI-013 — no re-indent or trailing-whitespace drift on any of the 251 lines. The ~39k script body byte-identical (39296 both sides). Found and deferred **D14** (`.pg-btn` reads `var(--text)`, which is defined nowhere) rather than fixing it. Metrics landed exactly as predicted |
| UI-015 | Extract `blueprint.html` CSS → `99-legacy/blueprint.css` | **done** | `5c7f752` | 277 lines moved verbatim (13378 chars, exact match); `HEAD` reconstructed byte-for-byte at all **66883 bytes**, the 46511-byte `<script>` body byte-identical. **First already-token-clean page** — its `:root` aliases onto `theme.css` tokens, so the whole block carried exactly one raw hex (`#fff` in `.btn-primary`), left untouched. `hardcoded_hex` therefore moved only 211 → 210, as predicted. Found and deferred **D15** (a `@media (max-width:760px)` block styling `.app-sidebar`/`.app-nav`/`.sidebar-foot`/`.bp-main`, none of which exist anywhere) rather than fixing it. Metrics landed exactly as predicted |
| UI-016 | Extract `bank.html` CSS → `99-legacy/bank.css` | **done** | `fcdfda1` | 366 lines moved verbatim (18015 chars, sha256 identical both sides); `HEAD` reconstructed byte-for-byte at all **94162 bytes**, the ~1830-line `<script>` body proven untouched. **Largest extraction of the sprint**, ~1.5× UI-014 — reviewer classified drift per line across all 366 and found none, with the indent-depth histogram (`{2: 214, 4: 124}`, 338 indented lines) identical on both sides. All **62 raw hex moved unconverted** in the same order (`var(` flat at 90), the inverse of UI-015's token-clean page. Reviewer additionally served the app and confirmed `/static/css/99-legacy/bank.css` returns **200, text/css, 18015 bytes** — the first live 404-check of the sprint. Frozen inventory 152 → 152. Metrics landed exactly as predicted |

| UI-017a | Ratchet — frozen inventory counted CSS attribute selectors as markup | **done** | `6c2829c` | Guardrail fix, no metric movement. `FROZEN_ATTR_RE` ran over the raw page source including `<style>` blocks, so a quoted attribute *selector* (`.modal-overlay[data-open="1"]`) was indistinguishable from a real markup attribute — extracting the block read as vanished handlers and failed two tests on a correct task. index.html had six (`[data-active="1"]` ×5, `[data-open="1"]`). Now scans markup only, via the `STYLE_ELEMENT_RE` that already existed. Effect surgical: index.html 269 → 263, other eight pages byte-identical, no ratcheted metric moved. Reviewer **mutation-tested** it rather than accepting the argument — five renames (`id`, `onclick`, `data-nav`, `data-lang-opt`, a dropped `data-active`) are all still caught — and found the decisive fact: `data-open="1"` never appears in index.html markup at all, JS sets it at runtime and the markup's `data-open="0"` survives in the inventory. Split from UI-017 so a self-referential guardrail change got reviewed on its own, per UI-013a precedent |
| UI-017 | Extract `index.html` CSS → `99-legacy/index.css` | **done** | `36f3c61` | 337 lines moved verbatim (17681 chars, exact match); `HEAD` reconstructed byte-for-byte at all **130737 bytes**, with all 3 `<script>` blocks (1712 lines) identical. Zero drift on any of 337 lines. All **61 raw hex** moved unconverted (`var(` flat at 87). **Scope trap held**: this page holds 224 of the project's 466 inline `style=""` attrs and 57 of the 76 inline hex — the full inline value sequence is byte-identical, so Sprint 5's work was not started early. The block's `@font-face` uses only `local()` and the block has **0 `url()`**, so relocating the CSS could not break a relative path — worth checking on every future move, since `url()` resolves against the stylesheet, not the document. Exposed the ratchet defect fixed in UI-017a. Reviewer served the app: `/` returns 200 with 0 `<style>` blocks and all three stylesheets 200. Metrics landed exactly as predicted |
| UI-018a | Ratchet test — re-anchor the cwd-independence canary | **done** | `549d0e3` | Test only, no metric movement. `test_measurement_is_cwd_independent` guards CLAUDE.md §12.9: a cwd-relative glob finds no pages from `C:\Users\MCS` and reports a triumphant zero for every metric. Its "we found pages" canary was `style_blocks > 0` — which Sprint 1 drives to 0 by design, so at UI-018 it fired on success. Re-anchored to `per_page` non-empty **and** the same page set. Reviewer mutation-tested it: with `page_paths()` swapped for a cwd-relative glob the new canary still catches it, and a second mutation (4 of 9 pages found) is caught only by the set-equality half — so that half is load-bearing, not decoration. It also established there is **no surviving metric** fit for the job: the six per-page metrics are all driven to 0 by the plan, and the five tree-level ones read `.css` directly so they stay non-zero with zero pages found — blind to the trap entirely. Page count is the only correct anchor. Same class as the defect UI-010 fixed |
| UI-018 | Extract `print.html` CSS → `99-legacy/print.css` | **done** | `6075ed0` | **Last extraction of Sprint 1.** 467 lines moved verbatim (20209 chars, sha256 identical both sides); `HEAD` reconstructed byte-for-byte at all **66389 bytes**, the 35711-byte script body identical. Zero drift on any of 467 lines (indent histogram identical). All **87 raw hex** — every one left in the project — moved unconverted, taking `hardcoded_hex` to **0**. **This head has no `theme.css`** (D9), so the `<link>` went to line 8 and none was added; the page carries exactly 2 stylesheets. Print-critical rules verified intact: 1 `@page { size: A4; margin: 0 }`, 2 `@media print`, and the three JS-driven knobs (`--page-margin: 14mm`, `--q-font: 14px`, `--q-gap: 14px`) still defined with their defaults. Reviewer reasoned the cascade explicitly: `setProperty` on `documentElement.style` writes the style attribute, which outranks author *normal* rules regardless of whether they came from a `<style>` or a `<link>` — the move is cascade-neutral. **Corrects a wrong number this board carried**: the UI-017 handoff said "3 `@page` / 3 `@media print`" from a raw grep that counted prose mentions inside CSS comments. Comments stripped, it is **1 and 2**, confirmed by two independent counts. `PLAN.md`'s "5 `@media print`" is wrong too → **D16**, not edited in passing (§12 rule 11). Metrics landed exactly as predicted |
| UI-020a | Ratchet — sanction Tier 1 token hex, ratchet `unsanctioned_hex` | **done** | `4273da6` | Guardrail fix, no CSS authored. **UI-020 was literally unwritable before this.** `total_hardcoded_hex` was ratcheted and summed hex across *every* `.css` under `static/` (`rglob`), but Tier 1 tokens are raw hex by definition, so authoring `01-settings/tokens.css` at all pushed 429 → ~451 and failed `test_metric_never_increases`. Meanwhile ADR-001:98–99 and §11 both define the invariant as "a raw hex outside `01-settings/tokens.css` is a CI failure" — the end state has hex *inside* that file, so this board's own target of 0 was unreachable by construction. Adds `token_hex` (that one file) + `unsanctioned_hex` (everything else, **ratcheted**); `total_hardcoded_hex` keeps its exact definition and goes informational, so every number in this log stays comparable. `RATCHETED_METRICS` is 8 both sides — one swapped, none dropped (reviewer AST-parsed both revisions). **First review FAILED it, and was right**: the new exemption-scope test asserted against `current` rather than the re-measurement, so it held only while `tokens.css` was absent and would have failed the suite deterministically on the very next task — the UI-018a defect class exactly. Reproduced at `assert 431 == (429 - 3)` before fixing, then re-verified invariant with a real `tokens.css` at **1, 5, 22 and 40 hex**: `unsanctioned_hex` pinned at **429** every time, and `total_hardcoded_hex` hit exactly **451** at 22, matching the projection. Second reviewer mutation-tested the exemption four ways (3 of 4 broadenings caught → D18) and proved hex outside `tokens.css` still trips the ratchet as the *only* failure, isolated so line counts stayed flat. Two limits recorded rather than oversold: the tokens-file guard is line-based (**D17** — PLAN.md's own tokens example is a single line, so UI-020 must author one declaration per line or the guard is vacuous) and the scope test cannot catch a `TOKENS_PATH.parent` broadening (**D18**) |
| UI-020 | `main.css` + import order + legacy demoted + `01-settings` 3-tier tokens | **done** | `01a27f6` | **First task in the epic that AUTHORS CSS rather than moving it.** Three new files, 310 insertions, **not one `.html` byte touched** — `main.css` is linked nowhere (verified over HTTP on all nine pages), so this task has zero visual effect by construction and needed no browser check. `main.css` = `@layer legacy, settings, generic, elements, objects, components, utilities` + 11 `@import`s, and **12 code lines total**; the nine `99-legacy/*` come first into the lowest layer, which is what "legacy demoted" means. They are `@import`ed rather than `<link>`ed because **a plain `<link>` is unlayered and unlayered normal declarations outrank every `@layer`** — linking would invert the cascade this file exists to establish. `tokens.css` = 19 Tier 1 primitives, one declaration per line (D17 — PLAN.md's own example is a single line and would satisfy the guard vacuously); `01-settings/theme.css` = 31 Tier 2 roles, **every one a `var()`, zero raw hex**. Reviewers verified 0 dangling refs and **0 unconsumed primitives** — 5 were deleted (`--font-urdu`, `--radius-1`, `--space-1/-4/-7`) to keep that invariant exact, so the space/radius scales have deliberate documented gaps. Palette is 1:1 with `static/theme.css`'s 19 distinct values, nothing invented. **`unsanctioned_hex` flat at 429** — the ratchet UI-020a built did its job on the first try: a hex quoted in a *Tier 2 comment* took it 429 → 430 and was caught before commit. **First review FAILED it** on three false claims in the comments (§12.12): "linked by 8 pages" (it is **7** — D9), "names do NOT collide" (**three do**: `--font-display`/`--font-body`/`--font-data`, and they must NOT be renamed because `blueprint.css`/`taqseem.css` read them), and D19 missing the token half → **D20**. All three measured and fixed, then re-reviewed PASS |
| UI-030 | `04-objects/shell.css` + `config/nav.json` | **done** | `704a76a` | **First Sprint 3 task, and still no page touched** — `main.css` is linked by none of the nine (verified live), so this is the last task that is safe by construction. `shell.css` = 6 rules, 23 declarations, `.o-shell__*`, **layout only**: not one background, border, colour, font or shadow, and zero raw hex. **The naming is the finding.** `PLAN.md`:125 gives `o-*` to layout objects, and taking the prefix is what makes the file safe rather than tidy: measured per name, **every one of the mockup's shell class names is already taken, in two different ways.** `.brand` (all nine legacy files), `.main` (blueprint + index) and `.spacer` (blueprint) are in `layer(legacy)`, so a rule of that name here would silently override nine pages at once — D21 at nine-page scale. `.app`, `.top` and `.nav` are in `static/theme.css` and no legacy file, which is the opposite case: unlayered, so they *beat* `layer(objects)` and then vanish when a page drops the link. `o-shell__*` appears nowhere in the project. **D21's height half is CLOSED as unnecessary, not deferred again**: `html, body { height: 100% }` never landed, because `.o-shell` uses `height: 100vh`, which resolves against the viewport and needs no percentage chain from `body` — the design target carries both (`mockup:16` and `:58`) and only the second is load-bearing, so **`print.html`'s Ctrl+P risk is not taken at all**. `--weight-medium` (500) did not land either, against this board's own prediction: a layout-only file cannot consume a weight, so it goes with `05-components/nav.css`. **Both stale predictions were corrected where they were written** (`tokens.css`, `reset.css`), per the rule UI-021 wrote after making the same mistake. `config/nav.json` = 4 groups / 11 items, **measured, not invented**: all 11 icon ids verified in `icons.svg` (an exact set match), all 7 urls 200, all 5 screen values real `showScreen` targets, groups and order 1:1 with the mockup, labels from the live pages. Found **D24** (`nav.mypapers` referenced by markup but in neither i18n table; `syllabus` is an orphaned screen) and **D25** (four nav destinations have no address at all, which is half of why the nav drifted into three versions). One layout omission is stated in the file that omits it: the `<760px` collapse hides the nav, and the control that gives it back is a Sprint 4 component. **TWO reviews FAILED this, and both were right.** The first caught three claims asserted instead of counted: "the mockup's nav is 12 items" (it is **11**, contradicted by the same paragraph two lines up), D25's "missing *exactly* the items that cannot be linked" (false — the 5-item pages also drop `/slo.html` and `/taqseem.html`, which have URLs, so that half **is** arbitrary drift), and `main.css` calling all four names a legacy collision. The second review then caught **two new false claims introduced by those very fixes**: the corrected `main.css` split put `.spacer` in the theme.css-only bucket when `blueprint.css:243` styles it — contradicting this task's own `shell.css`:21 — and the new `<760px` note said "six of the nine legacy files" when it is **five files, six blocks** (`index.css` has two), the same read-the-adjacent-number error as "12 items". Both fixed and re-verified independently. The reviewer also proved the two prose-only edits changed no CSS: `tokens.css` and `reset.css` are byte-identical to `HEAD` with comments stripped |
| UI-031a | Migrate `slo.html` onto the new tree via `static/css/pages/slo.css` | **done** | `f2493a0` | **The first page in the epic whose stylesheet is the new tree, and the first time any browser has parsed `@layer`.** Three files: `pages/slo.css` (new, two `@import`s and no rules of its own), `main.css` (the nine legacy `@import`s removed), `slo.html` (three `<link>`s → two: `app.css` + the entry file; **not one other byte** — 22/22 frozen attrs, 48/48 class attrs, `<script>` bodies identical, −53 bytes exactly the link swap). **D19 resolved by moving the legacy import out of `main.css`**, because the documented shape was measured to break the page: nine files import alphabetically, `taqseem.css` is last and won **15 selectors** off `slo` including `:root`, `.app-sidebar` and `.app-nav a`, and every value it brought reads a `static/theme.css` token the task unlinks — an unpainted sidebar via a file belonging to another page (**D20 by the back door**, on the one page whose own 17 tokens are all local literals). `main.css` keeps the layer order and stays the single source of the cascade; `CLAUDE.md` §11's link rule changed with it. **Verified in headless Edge 150 over CDP**, not by reasoning: layer statement with all seven names in order, every import in its declared layer, `99-legacy/slo.css` in `layer(legacy)`, sidebar `rgb(22,41,74)`, `static/theme.css`'s tokens all `<EMPTY>`, icons 17px, and the other eight pages byte-identical. **Four review rounds FAILED it and all three real failures were the same shape — a number asserted rather than measured**: D26's contrast computed against an assumed backdrop (real figure **1.70:1 → 3.04:1, an improvement**, not a regression); the change taxonomy naming only theme.css bleed and missing **D21 firing live**; and four inherited line numbers (`forms.css:58` is the input/select rule and cannot match a button). All three are recorded in the files as failed drafts. An aggregate delta count was **removed rather than corrected** — two measurements disagreed on property set, so the files give affected *elements* per rule, re-derivable with a grep. **A hex quoted in a comment took `unsanctioned_hex` 429 → 431 and `--write` pinned it** before `--check` ran; fixed with `git checkout` on the baseline, then re-pinned — **re-pin only after `--check` passes against HEAD**. Ships with three visible changes, all Sprint 4's to fix: **D26** subtitle at 3.04:1, **D27** ghost `<a>` vs `<button>` in two colours, **D28** cards tighter. Also found **D29**: two files are named `theme.css` and the Network panel shows only the basename — it caused a false alarm at Irfan's browser check, which he stopped on rather than assuming |
| UI-031b | Migrate `slo-health.html` onto the new tree via `pages/slo-health.css` | **done** | `8e9b839` | **Second live page, and the first repetition of UI-031a's mechanism — it needed no new decision, which was the thing being tested.** Three files: `pages/slo-health.css` (new, 49 lines, two `@import`s and no rules of its own), `slo-health.html` (three `<link>`s → two: `app.css` + the entry file), `BASELINE.json` (re-pinned). **−53 bytes, all of it the link block**; frozen inventory 19/19, class attrs 74/74, all three `<script>` bodies identical. **D20 does not hit this page, measured not assumed**: the legacy file declares 17 custom properties and reads 15, and the read-but-not-declared set is **empty**, so unlinking `/static/theme.css` orphans nothing; zero of its names collide with `01-settings/tokens.css` + `01-settings/theme.css`. Two are declared and never read (`--ok-bg`, `--primary-hover`) — pre-existing, left alone. **Cascade re-verified on this page in headless Edge 150 over CDP**, by recursing the CSSOM rather than reading the top level: the layer statement carries all seven names in order from `main.css`, all ten `@import`s sit in their declared layer, `99-legacy/slo-health.css` is in `layer(legacy)`, and every stylesheet plus four `woff2` returned 200. **The white slab is not a `slo` quirk — it is a `static/theme.css` fact.** The same `.brand` white background sat inside this page's navy sidebar too, and is gone; screenshots before/after. Also from theme.css: the subtitle's uppercase and letter-spacing. **Two `layer(elements)` element selectors reached past class rules and neither was named in UI-031a's review**: `a { color: inherit }` took all six inactive nav links from the legacy grey to white, so active/inactive now differ only by background and left border; and `small { }` took the sidebar subtitle's size and colour off `.brand small`. **Contrast measured against real backdrops, both directions**: subtitle **2.20:1 → 3.04:1** (an improvement, because the *before* backdrop was the white slab and not the navy — the same trap D26's first draft fell into), still under AA and still D26's to fix; `th` **5.81:1 → 4.60:1**, a fall that clears AA by 0.1. Tables took the design target's metrics (`tables.css` `th`/`td` padding to 24px horizontal, `vertical-align` top → middle on 38 cells, and `tr:last-child td` dropping the rule under the final row on 10 cells — deliberate, `tables.css`:63-66). Cards tighter again: D28, unchanged. **1463 element × property deltas over a property set of 36 fixed before measuring**, on a render first proven deterministic (two before-snapshots, 191 elements, 0 drift). **Stated limit: four cards were in empty states and the `.cov-*` blocks never rendered**, so that part of the page is unmeasured. **Process gaps, recorded rather than papered over: the independent review agent (§12 step 5) did not run on this task, and Irfan committed it himself** — so this row is the implementer's evidence only, not a reviewed result. The commit message says "theme.css link → main.css import"; the link actually goes to the per-page entry file, which is the whole of D19 — message only, code is correct |
| UI-031b | Migrate `library.html` onto the new tree via `pages/library.css` · `landing` HELD | **done** | `5291bdc` | **Third live page, and the biggest legacy file migrated so far.** `library.html`'s three `<link>`s → two (`app.css` + the entry file), **−53 bytes, all of it the link block**; frozen inventory 93/93, class attrs 94/94, **inline `style=""` 48/48**, all three `<script>` bodies identical. **Measurements, short form:** 2811 element × property deltas over a property set of 35 fixed before measuring, across 659 aligned elements; the page's one big visible change is its **44 `<label>`s** taking `03-elements/forms.css`'s bare `label` rule — 42 change size, 12 go weight 500→600, 2 change colour only — at **15.59:1/16.00:1 → 4.76:1, which still clears AA** (4.5 for normal text at these sizes; a review round called this a failure and was wrong, adjudicated by a later round). **D14 confirmed inert, measured not assumed**: `--text:` is declared nowhere in the project, so `/static/theme.css` never supplied it either — 5 of the 6 `.pg-btn` change colour by ordinary inheritance and the 6th is `.pg-btn.active`, which takes white by class and never reaches the invalid `var()`. D20 does not hit the page. The `static/theme.css` white slab in the sidebar is gone for the **third time in three pages** — treat it as a `theme.css` fact, not a per-page quirk. **EXPECTED ON THE BROWSER CHECK, so nothing here is a surprise: D21/D27/D28 — cards visibly tighter (`reset.css` zeroes legacy class margins), nav links all white (`typography.css`'s `a { color: inherit }` beats `.app-nav a`, so active/inactive now differ only by background and left border), and buttons re-fonted by `forms.css`.** **FOUR review rounds: three FAILED, and not one of them touched the CSS** — every finding was a measurement written into the entry file's comment that could not be re-derived from a stylesheet (a wrong page-count noun, an unreproducible aggregate, a miscounted property set, a wrong line citation, "six `.pg-btn`" when it was five, a font-size pair copied from a reviewer, and a settle-render claim taken from a review agent **without re-measuring it — it did not reproduce**). Irfan's call ended it: **strip the numbers from the comment entirely** and keep them here, where the board keeps every other task's and where a reviewer can check them. The entry file went 141 → 39 lines and passed on the next round. Two process facts worth carrying: writing a colour literal into that comment took `unsanctioned_hex` **429 → 430** and the ratchet caught it pre-review (third time in this epic); and a claim from a review agent is not evidence — verify it like any other number |
| UI-031c | `taqseem` onto the new tree — **ATTEMPTED, MEASURED, HELD** | **held** | `2085867` | **Not a migration: a measurement that changed the decision.** The D20 half worked. The orphan-token check gave **26** read-but-never-declared (the board said 20), of which Tier 2 already declares **3** under the deliberate `--font-*` collision, so the entry file carries a **23-token compatibility block** in `@layer legacy` — every one mapping 1:1 onto an existing Tier 2 role, **no value change, no literal, `unsanctioned_hex` flat at 429**, zero declared-name collisions with `01-settings/`. Verified live: all 23 resolve non-empty after the swap, `--color-canvas`/`--color-surface`/`--color-text`/`--color-border`/`--color-action` go `<EMPTY>` → real values, and the three font names resolve from Tier 2 exactly as its header predicts. **What stopped it is the half no grep can see: 20 `static/theme.css` rules match this page's elements and 16 are redeclared nowhere in its own legacy file** — the entire `.btn`/`.card`/`.pagehead` set plus two `input`/`:focus` rules. Swapped and measured: the 3 buttons fell to **UA default** (`rgb(240,240,240)`, 2px border, 1px 6px padding, `display:block`, weight 400, radius 0) and `.card`'s shadow went to `none`. **`taqseem` is the only page this hits** — own-file `.btn`/`.card` rule counts are `slo` 5/3, `slo-health` 2/3, `library` 13/3, `blueprint` 10/4, **`taqseem` 0/0** — which is precisely why three clean pages made it look routine. Measurement quality, for the record: render proven deterministic first (**70 elements, two before-snapshots, 0 drift**), **306 element × property deltas over a property set of 35 fixed before measuring**, across **67 aligned elements** (70 → 69 is the removed `<link>`, itself an element). The swap itself was clean and is the shape the eventual task will take: **−53 bytes, all of it the link block**, frozen attrs 15/15, class attrs 44/44, inline `style=""` 4/4, all three `<script>` bodies identical. **Then reverted on Irfan's call** — `taqseem.html` is at HEAD and the entry file was parked at **`docs/ui/parked-taqseem.css`**, following the `landing` precedent exactly: under `static/css/` its 61 lines counted toward `shared_css_lines` with no page loading them, and `docs/` is outside the metric, so **`shared_css_lines` is back at 1616 and `BASELINE.json` was not re-pinned**. One process note: an invariant check first reported the `<script>` bodies as differing; that was `git show` being decoded with the locale codec against a UTF-8 file (em-dash in the title, Urdu in the scripts), not a real change — `git diff` said 1 insertion / 2 deletions throughout. Decode explicitly before comparing bytes. **Not reviewed by an independent agent** — it never reached that gate, because the task was withdrawn rather than finished |
| UI-032 (measurement) | Both orphan checks over `blueprint`, `bank`, `index`, `print` — **as scripts** · `blueprint` HELD | **measured; nothing migrated** | `64484d9`, `8adcf17` | **No CSS, HTML or `<link>` touched — the only things written are two scripts and this board.** The checks this board had prescribed as prose are now `scripts/css_orphans.py`: `--names` for the token half (all nine pages) and `--rules` for the rule half, which parses `static/theme.css`, runs every selector through `querySelectorAll` against the live page in headless Edge via `scripts/css_rules_probe.mjs`, and subtracts what the page's own legacy file redeclares. 118 rule blocks probed (`:root` excluded — that is the token half's). **Both methods were validated against already-measured pages before any new number was believed**: the token half reproduces `taqseem` 26/3/23 and `library`'s D14 `--text`; the rule half reports `taqseem` 21 matched / 17 orphan against UI-031c's hand-measured 20/16, the whole difference being `:focus-visible`, a state-only rule a `querySelectorAll` method can only report as universal — it is its own column and is never a page's finding. **Result: `bank` 0, `index` 3, `print` 0 by D9, `blueprint` 20 — and `blueprint` is HELD.** It is the first page exposed on **both** halves at once (21 orphan tokens **and** 20 orphan rules) and its orphans are the **entire application shell** — `.app`'s grid, `.top`, `.nav` and its links/icons, `.brand .logo/b/small`, `.card > .ch/.cb`, `.chip` — none of which `blueprint.css` declares (grep, not inference) and none of which the new tree replaces (`04-objects/shell.css` uses `o-shell__*`, names its markup does not carry). `taqseem` loses its buttons; `blueprint` would lose the layout. **Held on Irfan's call the same day, before any entry file was written**, so unlike `landing` and `taqseem` nothing is parked for it and there is nothing to restore. **This board's own predictions were wrong in both halves and are corrected where they were written**: `blueprint`'s tokens were listed at 17 (an estimate, never re-measured — the same shape as `taqseem`'s "20", which measured 26) and its rule half was predicted "probably clean" off its 10 `.btn` / 4 `.card` counts, which were a real signal about buttons and said nothing about the shell. **Two script bugs found by cross-checking results against the files, both of which moved real numbers**: `static/theme.css` writes attribute values unquoted and the legacy files quote them, so un-normalised one rule read as two (`blueprint` 21 → 20, `bank` 2 → 1); and there was no property-level check at all, which produced a false *safe* — a page redeclaring a **selector** does not redeclare the **properties**, and that direction of error reports a page clean. The `partial` column is the fix, and it independently re-found the white-slab `.brand` on all four pages and `index.css`:144's `.summary-row` missing its `border-bottom`. Measured at 1280×900 in **Edge 151** (this board said 150; the dev PC moved). Determinism per UI-031b: every page probed twice with no action between, **drift 0 on all four**, and a second run from a fresh browser launch reproduced every number and every element count (235 / 5378 / 508 / 555). `index` was measured across **all seven** `showScreen()` screens, not the default one — the DOM grows 508 → 771. `print` was measured on a **real 25-question paper** (27 `<img>`, 555 elements), never a blank page. Dynamic classes were extracted from each page's JS and intersected with theme.css's names: empty for `blueprint` (44 tokens), `bank` (26) and `print` (42); `index`'s six are inert. **One gap stated rather than papered over: no paper in this DB has Urdu question text**, so the Urdu half of `print` was not exercised. **Not reviewed by an independent agent** — no page was changed, so it never reached that gate |
| UI-032 | `bank` onto the new tree — **ATTEMPTED, MEASURED, HELD** | **held** | `5749f32` | **The cleanest page on both orphan checks, and it still could not ship — the third time in this epic that passing every prescribed check was necessary and not sufficient.** The swap itself was exactly the shape the board predicts: `bank.html`'s three `<link>`s → two, **−53 bytes, one hunk, nothing else in the file moved** (frozen inventory 152/152, class attrs 125/125, inline `style=""` 90/90, `<script>` bodies identical), plus a two-`@import` entry file with no rules of its own. Both halves measured **0 exposure**: the legacy file declares its own 19 tokens as literals with zero collisions against `01-settings/`, and of the six `static/theme.css` rules that reach the page **3 are redeclared** by `bank.css` itself (`:80`'s input/select/textarea block among them), **2 are PARTIAL** (`.brand`, `.brand small` — the white slab and the uppercase subtitle, properties that do go) and **1 is orphan** (`:focus-visible`, which `03-elements/forms.css` supplies). **What stopped it is measured by neither check: Urdu.** `99-legacy/bank.css`:229 `.q-text .qt.rtl` sets `'Noto Nastaliq Urdu'` and a size but **no `line-height`**, so the line box came from the font's metrics; `03-elements/typography.css`:41's `body { line-height: var(--leading-body) }` is in `layer(elements)`, beats `layer(legacy)`, and takes it — **38px → 21.75px on the 24 Urdu-only questions in this DB, a 43% cut**, on the one script whose glyphs paint far outside their em box. **Nothing clips** (no `overflow` on `.q-row`/`.q-text`/`.qt`), so the failure mode is overlap and the row's 14px padding absorbs part of it — which is exactly why this was taken to a real browser instead of settled from the number. **Irfan looked and held it**: Nastaliq gets a proper look in Sprint 4. D21 firing on the **first migrated page that actually renders Urdu**; `print` could not exercise it (no paper in this DB has Urdu question text). **Measurement quality:** render proven deterministic first — two full page loads per state, **5378/5378 before and 5377/5377 after, 5370 body nodes both, key-drift 0 and value-drift 0** — the 5378 independently reproducing `css_orphans --rules`' own count, and the −1 being the removed `<link>`, itself an element. **16360 element × property deltas over a property set of 35 fixed before measuring**, across 5370 aligned elements (0 before-only, 0 after-only), in **Edge 151** at 1280×900. Every delta resolves to theme.css bleed removed or the new tree beating `layer(legacy)`; nothing collapsed to zero size, no text went invisible, no control lost its box. Named changes for whenever this page resumes: the **white slab gone for the fourth page running** (and `.brand` re-stacks, flex → block, a layout change and not only a colour one), `.brand small` losing theme.css's uppercase/letter-spacing/opacity onto D26's sub-AA ratio, **59 labels** taking `forms.css`'s bare `label` over `bank.css`:78's, **4 nav links + their icons going white** (`typography.css`'s `a { color: inherit }`, the identical `slo-health` finding), the canvas changing tint, and inputs taking `--color-border`, `--radius-sm` and the new padding. **Tokens: 12 measured live + 7 derived statically**, stated that way rather than as "19 measured" — the 7 unprobed ones are error/success-path colours no snapshot could reach because those paths did not run. **Three findings went to the board rather than being fixed (§12.2): D31** (`--color-text-muted` crosses AA on a *tinted* surface — 57 labels on white pass at 4.76:1, the 2 in `.urdu-toggle-row` fail at 4.44:1; backdrops measured by ancestor walk, not assumed, per D26's failure); **D32** (the token check reads stylesheets and never the markup — found via `bank.html`'s inline `var(--line, …)`, then swept across all nine pages: nothing shipped is affected, `index` is clean despite holding 224 of the project's inline styles, and **`blueprint` reads nine theme.css-only tokens inline with no fallback**, so its exposure was understated and its hold is the more obviously right call); and a **D30 update** (3 pages now link `/static/theme.css`, 5 are unmigrated — the two counts have drifted two apart). **The independent review FAILED this task and was right**, on four blocking findings: the entry file asserted "the rules that reach it are redeclared … takes nothing away", which is the exact selector-vs-property error the `partial` column exists to catch and which the same file contradicted twelve lines later; "orphans no token" was true of the stylesheet and false of the page; the Urdu line box was sitting in the implementer's own delta table and written down nowhere; and the entry file pointed at a STATUS.md row that did not yet exist. All four are fixed here. **The ratchet also caught a hex literal quoted in the entry file's comment — `unsanctioned_hex` 429 → 430 — for the fourth time in this epic**; the literal was removed and the file now says so in place. **Parked at `docs/ui/parked-bank.css`**, following `landing` and `taqseem` exactly: under `static/css/` its lines count toward `shared_css_lines` with no page loading them, so `shared_css_lines` is **back at 1616** and `BASELINE.json` was not left re-pinned — nothing shipped. `bank.html` is untouched at HEAD on its three `<link>`s |
| UI-032 | `index` onto the new tree — **ATTEMPTED, MEASURED, HELD** | **held** | *(this commit)* | **The fourth page in a row where both prescribed checks passed their own halves and something neither one measures stopped the page.** Token exposure **0** (27 declared, 21 read, all its own — no compatibility block needed and none written), rule exposure **3**, each with a named near-miss in `index.css`. The swap itself was the shape the board predicts: three `<link>`s → two, plus a two-`@import` entry file with no rules of its own. **Two regressions held it, and both are Sprint 4 component families. (1) The Urdu language toggle loses Nastaliq:** `03-elements/forms.css`:101 `button { font-family: inherit }` sits in `layer(elements)` and `99-legacy/index.css`:34 `.urdu, .ur` in `layer(legacy)`; layer order is decided before specificity, so the bare element rule wins and `index.html`:21's اردو button renders in the body's Latin sans — **D22's button reset arriving through the one declaration `forms.css`'s own header calls harmless**, landing on the control a teacher uses to put the app into Urdu. **(2) `.main` loses its padding and its scroll container:** `static/theme.css`:89 gives it `overflow: auto` and `padding: var(--pad) 28px 44px`, `index.css`:73's own `.main` sets only `flex`/`min-width`/`display`/`flex-direction`, and the content area measured **28px left, 32px up, 56px wider** on every screen (`grid-area: main → auto` is inert — this page's shell is `.shell { display: flex }`, not the `.app` grid that rule was written for). **This is NOT the `bank` finding repeating**: `index`'s Urdu paths both carry a `line-height` (`.urdu` sets `2` itself; `.paper-sheet`:165 sets `1.55` on the ancestor of `.ph-ur`/`.q-ur`), so `typography.css`:41's `body` rule cannot reach them — the property that broke here is `font-family`, and the first pass at this page looked only at line-height and would have missed it. **Measurement quality:** render proven deterministic first (default view snapshotted twice, no action between, **drift 0**); **32941 element × property deltas over a property set of 58 fixed before measuring**, across **5592 aligned elements** over all seven `showScreen()` screens plus the default view, **0 paths in only one snapshot**, in Edge 151 at 1280×900. Element counts fall by exactly 1 per screen — the removed `<link>`, itself an element, the same −1 `taqseem` and `bank` recorded. Other measured changes, so this page is not re-measured when it resumes: **`.summary-row` loses its dashed rule ×24** (the `partial` column being right, and predicted here before the swap rather than found by it), **`.tag` loses its chip ×16** (background → transparent, all four radii 5px → 0), **the white slab gone for the fifth page running**, base type 16 → 15px and `line-height` `normal` → 21.75px on **3978** instances, nav icons 19 → 17px. **One inline style is accidentally load-bearing and Sprint 5 must know before it starts:** the Urdu school-name field at `index.html`:443 keeps Nastaliq only because the family is in an inline `style=""`, which outranks every layer — burning the 224 inline attributes down without moving that family into CSS first takes the settings field the same way the toggle went. **One gap stated rather than papered over, exactly as `print`'s is: the `.paper-sheet` live preview did not render in either snapshot**, so `.ph-ur`:169 and `.q-ur`:179 were not exercised in the browser; what is verified is that their ancestor declares `line-height: 1.55`, which is a reading of the cascade and not a measurement of the page. **Reverted on Irfan's call** — `index.html` is at HEAD on its three `<link>`s and the entry file is parked at **`docs/ui/parked-index.css`**, following `landing`/`taqseem`/`bank` exactly: under `static/css/` its lines count toward `shared_css_lines` with no page loading them, and `docs/` is outside the metric. **Ratchet re-run after the revert: every metric +0, `shared_css_lines` at 1616, so `BASELINE.json` was not re-pinned — nothing shipped.** **Not reviewed by an independent agent** — the task was withdrawn rather than finished, the same gate `taqseem` and the UI-032 measurement never reached |
| UI-021 | `02-generic` reset + fonts · `03-elements` typography / forms / tables | **done** | `8ecb3cc` | **Sprint 2 complete.** Five new files (449 lines), `main.css`'s five `@import`s uncommented **in place** — the order is the cascade — and **not one `.html` byte touched**, so zero visual effect again by construction. `shared_css_lines` 573 → **1178**, the only metric that moved; `unsanctioned_hex` **flat at 429** and the new tree carries **zero raw hex**. Tier 1 gained 15 primitives (7 type steps, 2 weights, 2 leadings, `--font-serif`, `--font-nastaliq`) and Tier 2 13 roles, verified **0 dangling refs and 0 unconsumed primitives** — UI-020's invariant held exactly. **It predicted it would add space steps and did NOT**: control padding (9px 11px) and cell padding (10px/11px) are optical one-offs, left literal, and the one structural value needed was already `--space-inset`; the stale prediction was corrected in `tokens.css` rather than left to mislead. All nine `woff2` resolved on disk against `../../fonts/` — `url()` resolves against the *stylesheet*, the first such path in the tree. **The finding that outlives the task is D21: a reset in this tree is not neutral.** `layer(generic)`/`layer(elements)` outrank `layer(legacy)`, so a bare element selector beats a legacy *class* rule; the design target's `* { padding: 0 }` would have flattened `index.css:267`'s RTL list indentation, so the universal padding kill was **not** ported, the margin reset is targeted at block text elements, and `img` gets `max-width` without the usual `display:block` (it would break the inline `.icon` sprite). Each omission is stated in the file that omits it. **D22** parks the button appearance reset for UI-041 — `border:none; background:none; color:inherit` from `layer(elements)` would flatten `.btn-primary`/`.btn-ghost` across eight legacy files. **The first review FAILED it and was right**: the file shipped `font: inherit`, which is not a synonym for `font-family: inherit` — the shorthand also resets size, weight, style, variant, stretch and line-height, dragging every legacy button to 15px/400 and stripping the 600/700 weights they set by class. Fixed to the longhand, then re-reviewed PASS. Review also corrected three counts that were guessed rather than measured (`html, body {height:100%}` is 7 of 9 files, **not 8 — `print.css` is the second exception and it is the Ctrl+P page**; "exactly two pseudo-element rules" was a wrong generalisation from a `::before`-only grep; a Tier 2 comment's "20 unconsumed roles" mixed two different sets). **D23** records that `--font-mono`/`--font-data` name "IBM Plex Mono", which **no `@font-face` declares and no woff2 in the repo provides** — pre-existing since before this epic, always falling through to `ui-monospace`; the fix is a font-asset decision for Irfan, not CSS |
| UI-040 | `05-components/card.css` — card chrome + pagehead | **done** | *(this commit)* | **PREPARED, NOT LIVE — prepares a component and releases nothing.** **Seven rules, and the eighth is deliberately absent**: no bare `.card { }`, because `.card` is carried by **13 live elements** (`slo` 3, `slo-health` 6, `library` 4) and `layer(components)` outranks `layer(legacy)` — the same call `btn.css` made for `slo`'s two live `.btn` buttons, and safe only once Sprint 6 drains the legacy files. **The four `.card`-descendant rules are inert for a reason that can stop being true, so it is written in the file**: not because `.card` is absent from live pages (it is present) but because `.ch` / `.cb` / `.has-ch` are — measured **0/0/0** in source markup, **0/0/0** in the settled DOM after data load, and **no JS on any live page writes them** (every class token the inline scripts and `apiClient.js`/`brand.js` write was enumerated; intersection empty). The three `.pagehead` rules stay off the live pages on **one hyphen** — they spell it `.page-head` (`PLAN.md`:48's recorded fork). **Gate: `css_type_probe.mjs` before vs after, 44 properties × 7,159 elements = 314,996 comparisons, 0 deltas, 0 paths in only one snapshot, drift 0** on `slo`/`slo-health`/`library`/`bank`; review confirmed the file is loaded and parsed on each live page (7 rules in the CSSOM) and matches **0 elements**, so it is inert rather than unreachable. **Zero value divergence** — every token traced Tier 2 → Tier 1 resolves to exactly what `theme.css` resolved to, unlike `btn.css`'s ±1/±2. **What it does NOT release**: `taqseem` gets 7 of its 8 card/pagehead rules and stays HELD — it also needs its 6 button rules re-classed and **a gold fill `btn.css` does not carry** (`btn gold` ×2); `blueprint` gets 3 of its 20 orphan rules and stays HELD. `shared_css_lines` 1880 → **2022**; `unsanctioned_hex` flat at 429. **The ratchet failed once during this task, at 429 → 433, on four raw hex in the header's own mapping table — the fifth time this check has fired on this epic and the fifth time through a comment.** Reviewed in two rounds: PASS-with-notes, then PASS |
| UI-045 | display / hero type step — `--font-size-8` / `--text-display` + one rule in `docs/ui/parked-landing.css` | **done** | *(this commit)* | **PREPARED, NOT LIVE.** 30px is measured from `99-legacy/landing.css`:48, not extrapolated; the rule is the UI-044b shape, in a page entry file outside `static/`. **Three declarations, not one** — `font-size`, `line-height` (1.2, against `--leading-heading`'s 1.1) and `margin-bottom` (against `02-generic/reset.css`:79-91) all lose by layer order. **Three-state swap, measured then reverted**: HEAD 30px/36px/12px/h1 72px · migrated-no-rule 24px/26.4px/0px/52.78px · migrated+rule **back to HEAD exactly**, rule's isolated effect **8 element × property deltas**. **Live-page gate 314,996 comparisons, 0 deltas, drift 0** on all four pages — the two token names reach the live pages and nothing reads them. No fallbacks (D37). **RELEASED NO PAGE**: `.icon` is 17px in both migrated states (22px at HEAD, 11 icons), so `landing` still needs the icon decision (**`UI-047d`**, reachable by no component); migrating it costs 285 deltas and this fixes 8. `shared_css_lines` 1871 → **1880**; `unsanctioned_hex` flat at 429. **Corrected a board claim while here**: "the hero shrinks from two lines to one" is false — it is two lines in both states, `max-width: 640px` holding the wrap |
| UI-041 | `05-components/btn.css` — the button component | **done** | `a420ee0` + `8b9b055` + *(this commit)* | **PREPARED, NOT LIVE — the urdu.css shape. Four review rounds: FAIL / FAIL / FAIL / PASS-with-notes (2026-08-07).** Exactly one finding in the four touched a CSS rule — round 1's `:focus-visible` ring — and the declarations have been byte-identical since `a420ee0` (882 chars, comments stripped, verified at both remediations). The three later rounds found prose, citations and counts. Two variants (`.btn--primary`, `.btn--ghost`), imported by `main.css`, reaching all three live pages and **matching zero elements on them**: `.btn--` is in no markup in the repo. Proven both ways — markup count **0/0/0**, and `css_type_probe.mjs` before vs after over **44 properties × 7,159 elements returned 0 deltas**, `driftCount` 0 on every run. The five legacy files holding `.btn-primary`/`.btn-ghost` were **never opened** (`git diff` empty) and neither was `03-elements/forms.css` — **D22 stays parked**, because a `.btn--*` component cannot win back buttons that carry `.btn-primary`. `shared_css_lines` 1685 → **1871**, the only metric that moved — 1809 at the first commit, then 1868 and 1871 as three review rounds turned findings into comments, so treat `BASELINE.json` as the authority rather than this figure; `unsanctioned_hex` **flat at 429**, zero raw hex in the file including its comments. **The probe's property set was extended, and the first justification for it was wrong** — it claimed a borderless-button regression would have shown zero deltas under the old 18 properties, and review mutation-tested that: on `library`, `button { border: none }` produces **172 element × property deltas** within the old 18 (deltas, not properties — the earlier phrasing "172 of the old 18" cannot be read literally), because `box-sizing: border-box` (`02-generic/reset.css`:73) makes a dropped border change used `width`/`height`, both of which were already in the set. **The extension is still right, on the three things that genuinely are invisible to the old 18** — same test, same page: `border-radius: 0` → 0 deltas, `box-shadow: none` → 0, `cursor: default` → 0, and `library.css`:76/:86 carry them **between them**: :76 `.btn-primary` a box-shadow and a `var(--radius-btn)` radius, :86 `.btn-ghost` a 9px radius and a `cursor` — neither rule carries all three, and an earlier draft of this row said it did. The set is now 44. **No bare `.btn { }` rule, deliberately**: `slo.html` has `class="btn"` ×2 from `99-legacy/slo.css`:50 in `layer(legacy)`, and `layer(components)` outranks it — the skeleton sits on the modifier list instead, API `class="btn btn--primary"`. Colour from Tier 2, geometry measured from `bank.css`:139/:149, every scale divergence recorded in the file header. **Released no held page and never could**: `taqseem` is the only one whose buttons this unblocks and it also needs UI-040; **`index` is NOT unblocked** — its buttons are `.gen-btn`/`.ghost-btn` from its own legacy file, and its real blocker is the reset D22 parks. Four shapes still uncovered (secondary, danger, accent/gold, on-dark) and the size grid misses `library`'s 40px and `index`'s 48px — **accent/gold was covered by UI-041b on 2026-08-11, so three remain** |
| UI-041b | `.btn--accent` — the gold fill, and D7 | **done** | *(this commit)* | **PREPARED, NOT LIVE.** `.btn--` is in zero markup; **0 element × property deltas on all five live pages**, drift 0. **Inert rather than unreachable, and this time that was measured rather than argued**: `css_page_rule_probe.mjs` gained an optional selector argument and reports `.btn--accent` present in the CSSOM on `bank` and `slo`, arriving in **`layer=components`**, matching **0 elements** — the check UI-041's review had to run by hand. **It is not the two-declaration port the board scoped, and the reason is a measured accessibility failure**: `theme.css`:120's `.btn.gold` puts white on `--accent`, which is `--teal-500`, at **3.03:1**. The button is 15px/700 — under WCAG's large-text threshold of 18.66px bold — so it needs **4.5:1** and the legacy button fails it on `taqseem` today. Not a defect this tree introduced; a defect the port would have carried. **Irfan's call (C): darken the fill, not the text**, so both filled variants keep white text. New Tier 1 `--teal-600` at **6.07:1**, chosen to sit beside `.btn--primary`'s **6.29:1** rather than scrape past 4.5 — the D31 lesson from three days earlier, where a token picked with 0.26 to spare failed on three surfaces. New Tier 2 roles `--color-accent-strong` and `--color-on-accent`; `--color-accent` keeps `--teal-500` for the focus ring and soft states, where nothing sits on top of it. The filled geometry was split out of `.btn--primary` so the two variants differ in **exactly two declarations**. **No hover rule, deliberately**: `theme.css`:119's generic `.btn:hover` and `:120`'s `.btn.gold` have equal specificity (0,2,0) so the later wins and a gold button does not change on hover today; matching that beats inventing a `--color-accent-hover`. **The ratchet fired for the sixth time on this epic, and for the sixth time through a comment** — two hex literals quoted in the new block, caught at 429 → 431 and removed before commit. `shared_css_lines` 2263 → **2322**, `unsanctioned_hex` back to **429**, `token_hex` 19 → 20 (the sanctioned primitive). pytest 906, ruff clean |

---

## Live metrics — these may only go DOWN

Verified at `ui-baseline`, real app pages only (`mockup-modern.html` is a reference, not a page):

**Enforced since UI-002.** `python scripts/css_baseline.py --check` fails on any increase,
and `tests/test_css_architecture.py` fails the suite. Numbers below are no longer maintained
by hand — run the script.

| metric | key | `ui-baseline` | now (UI-031b, `library`) | target |
|---|---|---:|---:|---:|
| `<style>` blocks in HTML | `style_blocks` | 9 | **0** ✅ | 0 |
| CSS lines in HTML | `css_lines_in_html` | 2133 | **0** ✅ | 0 |
| page CSS + `99-legacy/` | `total_css_lines` | 2133 | **2115** | 0 |
| inline `style=""` attrs | `inline_style_attrs` | 466 | 466 | ~171 (one-offs only) |
| ⤷ excluding `display:` toggles | `inline_style_non_display` | 385 | 385 | ~171 — **this is the one to drive down** |
| hardcoded hex in `<style>` | `hardcoded_hex` | 324 | **0** ✅ | 0 — *but see below, this one lies* |
| hardcoded hex in `style=""` | `hardcoded_hex_inline` | 76 | 76 | 0 |
| **hex outside `tokens.css`** | `unsanctioned_hex` | 429 | **429** | 0 — **the honest one** |
| `99-legacy/` lines | `legacy_css_lines` | 0 | **2115** | *informational* — peaks ~2133 after Sprint 1 |
| hex in every `.css` | `stylesheet_hex` | 29 | **372** | *informational* |
| hex in `01-settings/tokens.css` | `token_hex` | 0 | **19** | *informational* — the sanctioned palette |
| hex anywhere | `total_hardcoded_hex` | 429 | **448** | *informational* since UI-020a |
| `app.css` + `theme.css` + new tree | `shared_css_lines` | 269 | **1616** | *informational* — grows through Sprints 2–4 |

**Five are deliberately NOT ratcheted** (`legacy_css_lines`, `stylesheet_hex`, `token_hex`,
`total_hardcoded_hex`, `shared_css_lines`). `99-legacy/` climbs to ~2133 during Sprint 1 and
the new tree grows in Sprint 2, so a downward ratchet on any of them would fail its own
migration.

**`unsanctioned_hex` is the ratcheted hex metric, not `total_hardcoded_hex`** — changed in
UI-020a. This table used to give `total_hardcoded_hex` a target of **0** and call it "the
honest one". That target was never reachable: ADR-001 and `CLAUDE.md` §11 both state the
invariant as *"a raw hex outside `01-settings/tokens.css` is a CI failure"*, so the end state
has hex **inside** that one file, legitimately — Tier 1 primitives are raw values by
definition. Ratcheting a metric that counted them made UI-020 literally unwritable: authoring
the palette at all pushed the number up and failed the suite. So `token_hex` counts that one
file, `unsanctioned_hex` is everything else and is the ratcheted one, and it **baselines at
429** — the same figure `total_hardcoded_hex` carried through all nine Sprint 1 tasks, because
`tokens.css` did not exist yet. It is a continuation, not a reset. `total_hardcoded_hex` keeps
its exact definition and is still reported every run, so every number in the task log below
stays comparable.

**The new hiding place, stated plainly.** Hex laundered *into* `tokens.css` leaves
`unsanctioned_hex` while nothing was repaid. *Authoring* new primitives is ratchet-neutral
(`total_hardcoded_hex` and `token_hex` rise together, `unsanctioned_hex` flat) — that is the
point of the exemption. *Relocating* existing hex into `tokens.css` drops `unsanctioned_hex`
with nothing deleted from the tree, and that is arithmetically identical to the legitimate
Sprint 5–6 burn-down, so no automated check can separate them. `test_tokens_file_holds_only_token_hex`
narrows it — every hex in that file must sit on a custom-property declaration — but the check
is **line-based**, so a one-line or minified rule defeats it (D17), and it cannot judge whether
a primitive is needed. Like `shared_css_lines`, this one is on the reviewer: **watch `token_hex`
move; a large jump wants a reason.**

**`hardcoded_hex` falling is NOT progress during Sprint 1.** It counts only `<style>` blocks
in HTML, so extraction moves hex out of it and into `stylesheet_hex` untouched — UI-010..016
took it 324 → 298 → 273 → 268 → 254 → 211 → 210 → 148 → 87 → **0** without removing one colour. It reaches 0 when the last page is
extracted, with
all 324 still in `99-legacy/`. **`unsanctioned_hex` is the number that has to reach 0**;
it is flat at 429 through extraction and only moves when a hex is genuinely deleted.

**`total_css_lines` drops exactly 2 per page extracted, not 0.** `css_lines_in_html` counts
the `<style>` and `</style>` lines; a `.css` file has neither. Expect **2133 → 2115** across
Sprint 1. A drop larger than 2 on an extraction task means CSS was deleted rather than moved.

**Watch `shared_css_lines` when reviewing.** `total_css_lines` covers page CSS + `99-legacy/`
only, so moving a page's `<style>` block into `app.css` instead of `99-legacy/` passes the
ratchet with three metrics falling and nothing removed. A page shrinking while
`shared_css_lines` jumps by the same amount is debt relocated, not repaid — no automated
check can tell the difference, so that one is on the reviewer.

**Green baseline at `ui-baseline`:** `pytest -q` = 874 passed · `ruff check .` clean.
**Green at UI-002:** `pytest -q` = 900 passed (874 + 26) · `ruff check .` clean ·
`css_baseline.py --check` exit 0.
**Green at UI-011:** `pytest -q` = **902 passed** · `ruff check .` clean ·
`css_baseline.py --check` exit 0.
**Green at UI-012:** `pytest -q` = **902 passed** · `ruff check .` clean ·
`css_baseline.py --check` exit 0. Gates run twice — by the implementing session and
independently by the review agent.
**Green at UI-013:** `pytest -q` = **902 passed** · `ruff check .` clean ·
`css_baseline.py --check` exit 0. Both runs independent (implementer + review agent).
Note `ruff` is not on PATH in this environment — use `python -m ruff check .`.
**Green at UI-014:** `pytest -q` = **902 passed** · `python -m ruff check .` clean ·
`css_baseline.py --check` exit 0. Both runs independent.
**Green at UI-015:** `pytest -q` = **902 passed** · `python -m ruff check .` clean ·
`css_baseline.py --check` exit 0. Both runs independent (implementer + review agent).
**Green at UI-016:** `pytest -q` = **902 passed** · `python -m ruff check .` clean ·
`css_baseline.py --check` exit 0. Both runs independent; the reviewer also served the app
and confirmed the new stylesheet returns 200, not 404.
**Green at UI-017a / UI-017:** `pytest -q` = **902 passed** · `python -m ruff check .` clean ·
`css_baseline.py --check` exit 0, both gates run at each of the two commits. UI-017a was
built and verified on a clean `HEAD` (extraction stashed) so its own commit is green in
isolation, not only in combination.
**Green at UI-018a / UI-018:** `pytest -q` = **902 passed** · `python -m ruff check .` clean ·
`css_baseline.py --check` exit 0. Same clean-`HEAD` treatment for UI-018a. Reviewer served the
app: `/print.html` 200 with 0 `<style>` blocks, 2 stylesheets, no `theme.css`, and
`print.css` 200 at 20209 bytes.
**Green at UI-020a:** `pytest -q` = **905 passed, 1 skipped** · `python -m ruff check .` clean ·
`black --check` clean on both changed files · `css_baseline.py --check` exit 0. Gates run three
times: implementer, plus two independent review agents (the first FAILED the task). The single
skip is `test_tokens_file_holds_only_token_hex`, vacuous only until `tokens.css` exists — it
un-skips in UI-020. Project-wide `black --check .` reports ~95 unformatted files, but that is
**pre-existing at clean `HEAD`** (verified by stashing: identical count), not introduced here.
**Green at UI-020:** `pytest -q` = **906 passed, 0 skipped** · `python -m ruff check .` clean ·
`css_baseline.py --check` exit 0. The skip is gone because `test_tokens_file_holds_only_token_hex`
un-skips once `tokens.css` exists — expect 906/0 from here, not 905/1. Gates run three times
(implementer + two independent review agents; the first FAILED the task). **Not verified: `@layer`
parsing in a real browser** — the Chrome extension was not connected for the implementer or either
reviewer, and all three said so rather than claiming it. No risk today (`main.css` is linked
nowhere); close it in the pre-Sprint-3 browser session.
**Green at UI-021:** `pytest -q` = **906 passed, 0 skipped** · `python -m ruff check .` clean ·
`css_baseline.py --check` exit 0, with `shared_css_lines` re-pinned to **1178** in-task. Gates
run three times (implementer + two independent review agents; the first FAILED the task on
`font: inherit`). **`@layer` is still unparsed by any browser** — the Chrome extension was
connected for none of the five agents across UI-020 and UI-021, all five said so rather than
claiming it, and the browser session did not close it either: no page loads `main.css`, so
there was nothing to parse. Retired instead by version (Edge/Chrome 150 vs ADR-001's floor of
99) and finally by UI-031. See the browser-session block above.
**Green at UI-030:** `pytest -q` = **906 passed, 0 skipped** · `python -m ruff check .` clean ·
`css_baseline.py --check` exit 0 · `unsanctioned_hex` flat at **429** · `shared_css_lines`
1178 → **1351**, re-pinned in-task. One full-suite run reported `test_upload_replaces_previous_data`
failing on `sqlite3.OperationalError: disk I/O error`; re-run in isolation it passes 15/15, and
the final full run is clean — a flake, recorded rather than quietly dropped. Gates run five
times (implementer three, review agent twice
— it **FAILED the task twice**, and both times the second round of numbers was checkable in one
grep). No `.html` modified, so the frozen inventory diff is empty by construction. Still no
browser: `@layer` remains unparsed by anything, harmless here because no page links `main.css`,
and the `height:100vh` / independent-scroll reasoning is specification-level, not observed.
**UI-031 is the first task that can see any of it.**
**Green at UI-031a:** `pytest -q` = **906 passed, 0 skipped** · `python -m ruff check .` clean ·
`css_baseline.py --check` exit 0 · **all eight ratcheted metrics flat**, `unsanctioned_hex`
**429** · `shared_css_lines` 1351 → **1527**, the only mover, re-pinned in-task. Gates run
**nine times** (implementer four, review agent five — it **FAILED the task four times**).
**`@layer` is no longer unverified**: parsed in headless Edge 150 through CDP, layer statement
and per-file layer assignment both read off the live document. The Chrome extension was not
connected — Edge headless plus Node's built-in `WebSocket` over CDP was used instead, and
screenshots came from `msedge --headless=new --screenshot`. The school PC remains unchecked
(blocked item 1). **Two process hazards recorded rather than dropped:** the review agent ran
`Get-Process msedge | Stop-Process -Force`, which kills *every* Edge on the machine including
Irfan's — scope cleanup to your own `--user-data-dir` or PIDs. And `C:` reached **226 MB free**
during this task, causing a real `OSError: [Errno 28] No space left on device` mid-`pytest`;
**UI-030's recorded `sqlite3.OperationalError: disk I/O error` "flake" was almost certainly
this, not a flake.** Freeing headless-browser profiles recovered ~2.3 GB.
**Green at UI-031b:** `pytest -q` = **906 passed, 0 skipped** · `python -m ruff check .` clean ·
`css_baseline.py --check` exit 0 · **all eight ratcheted metrics flat**, `unsanctioned_hex`
**429** · `shared_css_lines` 1527 → **1576** (the 49-line entry file), the only mover, re-pinned
in-task and **only after `--check` passed against HEAD's baseline** — the ordering UI-031a had
to learn the hard way; the re-pin diff touches that one key and nothing else. All nine pages
still return 200, with `slo` and `slo-health` now on two `<link>`s. **Gates run once, by the
implementer only — the independent review agent did NOT run on this task**, so unlike every
task above it these numbers have not been reproduced by a second party. Headless Edge 150 was
driven through CDP on its own `--user-data-dir`, and the processes were checked as gone by
matching that directory rather than by killing every `msedge` on the machine (the UI-031a
hazard). Disk stayed at ~11 GB free, so UI-031a's `Errno 28` conditions did not recur.
**Green at UI-031b (`library`):** `pytest -q` = **906 passed, 0 skipped** · `python -m ruff
check .` clean · `css_baseline.py --check` exit 0 · **all eight ratcheted metrics flat**,
`unsanctioned_hex` **429** · `shared_css_lines` 1576 → **1616** (the 40-line entry file), the
only mover, re-pinned in-task after `--check` passed against HEAD's baseline. Gates run
**eight times** — implementer four, review agent four, and **the review agent FAILED this task
three times**. It also mutation-tested the hex ratchet (a colour literal in the comment →
429 → 430, exit 1, then restored byte-identical). `landing` is not in these numbers: it was
built and green, then held, and its entry file was moved to `docs/ui/parked-landing.css` so
that 55 lines of CSS no page loads could not be absorbed into this task's re-pin.
**Green after `taqseem` was held and reverted:** `pytest -q` = **906 passed, 0 skipped** ·
`python -m ruff check .` clean · `css_baseline.py --check` exit 0 · **all eight ratcheted
metrics flat**, `unsanctioned_hex` **429**, `shared_css_lines` **flat at 1616** — the entry
file is parked in `docs/`, which the metric does not count, so nothing unlinked is hiding in
it. **BASELINE.json was deliberately NOT re-pinned**: nothing shipped, and pinning lines of
CSS that no page loads is exactly the laundering this board warns about. `taqseem.html` is byte-identical to HEAD. Headless Edge 150 was driven on
its own `--user-data-dir` (the UI-031a hazard), and the dev server was a local
`uvicorn app.main:app` on `127.0.0.1:8000`.
**Re-pin `BASELINE.json` (`css_baseline.py --write`) as part of every extraction task** —
UI-010..012 did, UI-013 missed it and had to fix it in the close commit; UI-014 and UI-015
did it in-task. Skipping it leaves the next task comparing against numbers two tasks stale.

---

## Decisions locked (do not relitigate)

| Decision | Choice | When |
|---|---|---|
| Palette | **Modern** — indigo `#4f46e5` + teal `#0ea5a4` | 2026-07-28 |
| Design target | `static/mockup-modern.html` | 2026-07-28 |
| Shell fidelity | **Full mockup shell** — `.app` grid + topbar + grouped nav | 2026-07-28 |
| Architecture | ITCSS order + BEM naming + small utility layer | ADR-001 |
| Load mechanism | one `<link>` → `main.css`, `@import` inside | ADR-001 |
| `@layer` | **adopted** — floor is Edge/Chrome 99 (Mar 2022), Edge auto-updates | 2026-07-28 |
| Review gate | every task passes an **independent review agent** before Irfan sees it | 2026-07-28 |
| Dirty tree | committed as-is, tagged `ui-baseline` | 2026-07-28 |
| Branching | one epic branch, one commit per task | 2026-07-28 |
| Push | **never by Claude** — Irfan, via GitHub Desktop | standing |

---

## Blocked / needs Irfan

| # | Item | Needed for |
|---|---|---|
| 1 | **School PC's Edge version** (`edge://version`, needs ≥ 99). Dev PC is 150, but ADR-001 accepts `@layer`'s hard-fail risk purely on Edge auto-updating and the school machines have never been checked. Irfan said 2026-07-31 he would do it later | **UI-031** — the first task that puts `main.css` on a page. Not blocking UI-030, which touches no page |
| 2 | **`--font-mono` names "IBM Plex Mono" and no such font exists in the repo** (D23). Either commit the two woff2 (~80KB, licence-checked) or drop the family and let `ui-monospace` be the declared intent. Font-asset call, not CSS | a small asset task, or **UI-064** with D13. Nothing is blocked meanwhile — it has silently fallen back since before this epic |

---

## How to start a session

1. Read this file. Take **only** the task named under NEXT TASK.
2. Read `CLAUDE.md` §11–12 (rules) and the one page/file that task owns. Nothing else.
3. State a 2-line plan. Wait for go-ahead.
4. Implement — anchored `Edit`s only, inside the declared scope.
5. Self-check all gates, then **spawn the independent review agent**. It can FAIL you;
   on FAIL, fix and re-review. Never hand over a failed or unreviewed task.
6. On PASS, hand to Irfan with a **specific click-list** for his browser check.
7. Only after Irfan says OK: update this file (task log, metrics, NEXT TASK), then commit.
   Never push.
8. Emit a copy-pasteable prompt for the next task's fresh session.
