# ROADMAP & AUDIT FINDINGS — July 2026
**Basis (as written):** fresh audit of repo @ commit f6bed81 (ratio merge) · 242 tests passing · prod live & verified

> **⚠ 2026-08-25 — us pehli line ke teenon hisse ab ghalat hain.** Naapa gaya:
> **1,075 tests** (242 nahi) · HEAD `ebfc0f6`, `f6bed81` nahi · **aur "prod live" ka
> koi wujood nahi** — repo mein ek hi remote hai (`backup`), koi hosting remote nahi,
> aur Irfan GitHub Desktop se push karta hai (§B ki O1 row dekhein). Ye file **July ka
> audit** hai jise uske baad patch kiya jata raha; us ka عنوان aur buniyad purani hai,
> us ke andar ke chand hissay naye. **Har adad par shak karo aur khud naapo.**

---

## A. Audit Snapshot — What's HEALTHY ✅

- **Tests:** ~~242~~ **1,075 passing** (naapa 2026-08-25); services, repositories, and routes all covered; guard paths tested. `ruff` saaf.
- **Security:** git history clean of secrets (`.env*`, `*.db`, `*.zip` ignored); auth fail-closed in prod; timing-safe key compare; Gemini key in header not URL; app key already rotated once successfully.
- **Architecture:** clean layering (api → services → repositories → core) consistently followed; env reads at module boundary.
- **Process:** last three releases followed branch → plan-first → verify → PR → deploy — keep this.
- **Docs:** README, ARCHITECTURE, PROJECT, USER_STORIES exist and are substantial.

## B. Audit Findings — What NEEDS FIXING ⚠️ (with priority)

### P0 — Hygiene & risk ✅ BAND (naapa gaya 2026-08-21)

> **Ye rows mahinon se ghalat khuli pari thin.** 2026-08-21 ko file-by-file naapa
> gaya: H1–H4 aur H6 kab ke ho chuke the, sirf yahan kaati nahi gayin. Isi wajah
> se us din ki ginti bhi ghalat di gayi thi ("7 rows khuli"). **Row par bharosa
> mat karo — repo mein naapo.**

| # | Finding | Haalat (2026-08-21 ko naapi hui) |
|---|---------|--------|
| ~~H1~~ ✅ | ~~`.env.txt` (318 B) on disk~~ | **File mojood nahi.** Gemini key rotation ab bhi multawi hai (§E dekhein) |
| ~~H2~~ ✅ | ~~`maker.zip` (1.4 MB) in repo root~~ | **Mojood nahi** |
| ~~H3~~ ✅ | ~~Loose root scripts~~ | **`scripts/` mein hain** — `scripts/import_syllabus.py`, `scripts/seed_large_class.py` |
| ~~H4~~ ✅ | ~~Fixture CSVs in root~~ | **`tests/fixtures/` mein hain** — `happy_birds_pre_year_{1,2,3}.csv`, `syllabus_topics_unit1_sample.csv`; double extension bhi theek |
| **H5** ⛔ | `master` not protected on GitHub | **Ho hi nahi sakta, aur zaroorat bhi nahi.** GitHub API 403: *"Upgrade to GitHub Pro or make this repository public"* — private repo par branch protection paid feature hai. Aur ye Irfan ke asal tareeqe se takrata bhi hai: wo khud GitHub Desktop se `backup` remote par push karta hai, PR flow use nahi karta. **Row band — isay "baqi kaam" mat ginno** |
| ~~H6~~ ✅ | ~~`API_VERSIONING.md` (8 KB) over-long~~ | **File mojood nahi.** `DECISIONS.md` bhi nahi bana — us ki jagah `docs/ui/DECISIONS-FOR-IRFAN.md` aur `DEFERRED.md` ye kaam kar rahe hain |

### P1 — Product robustness (next 1–2 sessions)
| # | Finding | Action |
|---|---------|--------|
| ~~R1~~ ⚠ | ~~Prod question bank thin on subjective types~~ | **AUZAAR BAN GAYA 2026-08-21** (`scripts/seed_bank.py`), kaam **abhi adhoora**. Naapa gaya **2026-08-23** (`syllabus_topics` LEFT JOIN `questions`, na ke row ke bharose): <br><br>`Math Grade 4` 11/11 (43 sawal) · `Math Pre Year 1` 71/81 (329) · `Math Pre Year 2` 23/87 (92) · `Math Pre Year 3` **23/87 (92, 2026-08-23)** · **khali:** `Math G5` 0/11, `Math G6` 0/11, `Science G7` 0/11, `Geography G8` 0/11. Bank kul **686**. <br><br>⚠ **Purani row ne "5 khali" kaha aur 6 ginwaye** — ye wahi bimari hai jis se P0 rows mahinon jhooti khuli rahin. Adad DB se naapein. <br><br>**Chaar khali jode (`G5`, `G6`, `Science G7`, `Geography G8`) JAALI duplicate rows hain** — paanchon mein wohi 11 Grade-4 maths topics hain (dekhein PROGRESS.md 2026-08-21). **Un ko seed karna mana hai jab tak asal syllabus import na ho** — Geography par yehi ho chuka aur 44 sawal delete karne pare. **Ye code ka masla nahi, data ka hai:** in chaar ka asal syllabus (PDF/Excel) chahiye, import ka raasta pehle se mojood hai. <br><br>**RUKAWAT KA ASAL PAIMANA (naapa 2026-08-23):** PY2 aur PY3 dono theek **23/87** par ruke, dono dafa musalsal 3 dafa HTTP 429 par. Yani rozana quota lag-bhag **23–26 AI calls**. **128 topics baqi** (PY3 64 + PY2 64) = **~6 aur din ke run**. Ye "chhota tukda" nahi — ek hafte ka rozana kaam hai, aur row ka purana lehja ise chhota dikhata tha. <br><br>Row tab band karein jab PY2 + PY3 mukammal hon **aur** chaar jaali syllabi asal data se badal jayen. <br><br>~~**2026-08-25 ko dobara naapa — har adad wohi hai, kuch nahi badla** (bank 686; G4 11/11, PY1 71/81, PY2 23/87, PY3 23/87, chaaron jaali 0/11).~~ <br><br>**2026-08-26 ko run hua — pehli dafa ye adad hile:** bank **766**, PY3 **43/87 (172 sawal)**. PY1 71/81 (329), PY2 23/87 (92), chaaron jaali 0/11 — sab waise hi. Quota **20 topics** ke baad lagi (andaza 23–26 tha, to paimana durust hai). **Baqi 108 topics = PY3 ke 44 + PY2 ke 64, yani ~5–6 aur din.** Ye row aaj sach hai; agar aap ise kisi aur din parh rahe hain to dobara naap lein. |
| ~~R2~~ ✅ | ~~Export tests don't assert content (Urdu text, marks, sections)~~ | **DONE (PR #6):** docx content assertions for EN/UR question text, options, total-marks value. Sections deferred — feature not built yet. **⚠ YEH ROW AB TAAREEKH HAI, ZINDA TESTS NAHI:** DOCX/PDF export `e2bdcc4` mein delete ho chuka aur uske saath ye assertions bhi. Aaj paper ka output browser print hai (`static/print.html`), aur sections 2026-08-20 ko ban chuke (order 1 dekhein). |
| ~~R3~~ ✅ | ~~Adaptive papers ignore paper_type/ratio — undefined interaction~~ | **DONE (PR #8):** adaptive now honors `paper_type` (mcq/mixed/subjective) via the shared `_PAPER_TYPE_FILTERS`; `custom-ratio` deliberately rejected for adaptive (422 via `_reject_ratio_for_adaptive` validator) — weakness-distribution × ratio-split combo left out of scope. Tested: type filter + custom-ratio rejection. |
| ~~R4~~ ✅ | ~~Provider fallback (Gemini→Anthropic) untested~~ | **DONE (PR #6):** locked actual behavior — selection-by-priority (no runtime fallback exists); mocked-HTTP error-wrapping + no-key-leak tests. |

### P2 — Ops decision (before Railway day ~28)
| # | Finding | Action |
|---|---------|--------|
| O1 ⏸ | Railway credit expires; card not added (correct) | **Plan likha ja chuka: `docs/MIGRATION.md`** (Railway → Northflank, decisions locked, "awaiting implement karo"). Magar amal ruka hua hai aur shayad hona bhi nahi chahiye — **repo mein sirf EK remote hai (`backup`), koi hosting remote nahi**, aur Irfan ka asal tareeqa GitHub Desktop se backup push hai, cloud deploy nahi. Roadmap ki simt bhi ab school PC / Docker package hai. **`docs/MIGRATION.md` ka status line is se purana hai — usay parhne se pehle ye row parhein.** Faisla Irfan ka: plan zinda rakhna hai ya band karna |

## C. Feature Roadmap (after P0/P1)

| Order | Feature | Why | Size |
|-------|---------|-----|------|
| ~~1~~ ✅ | ~~**Sections mode (A/B/C)** — headings + per-section marks in UI/print/Word~~ | **DONE 2026-08-20** (`e2e517a`). Teacher generate screen par apne sections banata hai (naam, qismein, ginti); `sections_meta` paper ke saath store hoti hai aur `print.html` use pehle se render karta hai. **"Word" is row ka stale hissa tha** — DOCX/PDF export `e2bdcc4` mein jaan-boojh kar delete hua ("621 lines nothing calls, and a LibreOffice dependency") aur Irfan browser se print karta hai, to daira UI + print raha. Kami par paper fail nahi hota, shortfall report hota hai. Tafseel PROGRESS.md 2026-08-20 | M–L |
| 2 | **Ratio Phase 2** — exact counts per type (3/4/3) | Finer control; builds on ratio v1 | S–M |
| ~~3~~ ✅ | ~~**Prod seeding tool** — one-click "build starter bank" per class~~ | **DONE 2026-08-21** as `scripts/seed_bank.py` (CLI, dry-run by default), NOT a UI button — "one-click" jaan-boojh kar multawi, taake pehle naapa ja sake ke sawal kaam ke aate hain. Bank 459 → 502; Math Grade 4 ab 11/11 topics. Is ne do asal bug bhi benaqab kiye, dono fix ho chuke: (a) AI maangne par bhi `essay` nahi banata tha kyunke prompt ke JSON namoone mein sirf mcq/short-answer thay; (b) `advanced` Bloom taqseem chhote papers par ULTI chalti thi. Tafseel PROGRESS.md 2026-08-21 | S |
| ~~4~~ ✅ | ~~**Lesson Plan module** — plans linked to topics + coverage report~~ | **DONE 2026-08-22/23 — AND IT SHIPPED UNDER ANOTHER NAME, WHICH IS WHY THIS ROW STAYED OPEN FOR DAYS AFTER IT WAS FINISHED.** It is `R7 — Hafta-war Plan + Coverage`, spec `docs/TOPIC_WEEK_PLAN.md`, and its §1 records the naming decision: "Lesson Plan" was rejected because the module does not hold lesson content, it maps **topics to weeks**. All four marhale are done — table + repository + service + API (50 tests), Excel import + template (29), coverage service + `GET /api/topic-plan/coverage` (20), and `plan.html` with the week-strip coverage badges. **It was not the "new module, size L" this row assumed**: §2 measured that half the machinery already existed, and the whole thing landed in four days. <br><br>⚠ **Built ≠ adopted.** `topic_week_plan` holds **4 rows** (measured 2026-08-25), of which three are Irfan's own browser test from 2026-08-22. `Pre Year 1` alone has 81 topics. So `plan.html` renders, the coverage endpoint returns real data (49/81 topics covered, 60%), and the board is **empty in practice**. The remaining work is not code — it is one teacher filling in one Excel plan. | L |
| 5 | Per-student adaptive papers | Extends F10; still open after R3 (adaptive is whole-class only) | M |
| 6 | Syllabus PDF auto-extract | Convenience | M |
| 7 | Adaptive × custom-ratio | Deferred by R3 (currently 422-rejected); needs a weakness-distribution × ratio-split design before it's safe to allow | M |

## D. Suggested Session Plan (step-by-step)

```
Session 1  → P0 cleanup (H1–H6)                                   ✅ ho chuka
Session 2  → R2 + R4 tests; R3 (adaptive×type)                     ✅ PR #6/#8
Session 3  → R1 prod seeding + regression checklist                ✅ auzaar bana
Session 4  → O1 migration dry-run (MIGRATION.md)                   ⏸ plan likha, amal ruka
Session 5+ → order 1 (Sections mode)                               ✅ 2026-08-20
Aage      → order 2 (Ratio Phase 2). Sections ke qareeb hai: dono ginti tay
             karte hain, aur GeneratePaperRequest un dono ko ek saath lene se
             saaf inkaar karta hai (422) — us faisle ko dobara mat kholo bina
             yeh tay kiye ke teacher ko kaunsa jeetna chahiye.   ✅ 2026-08-21
             → order 3 (seeding tool)                            ✅ 2026-08-21
Aage      → order 4 (Lesson Plan)                                  ✅ 2026-08-23
             R7 ke naam se aaya, is naam se nahi — order 4 ki row parho.

Aage      → R1: bank bharna. Rozana ka kaam hai, ek session ka nahi:
             128 topics baqi, quota ~23–26 calls/din = ~6 din.
             "Sirf chalana hai" NAHI hai — defaults pre-school par ghalat hain
             (fill-blank + essay + balanced). Yehi command dobara chalani hai,
             seeded topics khud chhut jate hain:

             python -m scripts.seed_bank --subject Mathematics \
               --grade "Pre Year 3" \
               --types "multiple-choice,short-answer,true-false" \
               --bloom foundational --max-topics 87 --write

             Phir wohi Pre Year 2 ke liye. Grade 4+ par defaults theek hain.
             R1 row pehle parho: paanch khali joron mein se chaar JAALI
             syllabi hain, un ko seed mat karna.

ASAL AGLA  → CSS epic — docs/ui/STATUS.md. Ab sab se bara bacha hua kaam
             yehi hai aur is file mein us ka koi task nahi. Us ka apna
             NEXT: DEFERRED D45 (state probe), phir D44 (button task).
```

> **⚠ Is block ki har ✅ row kabhi khuli pari thi.** Order 1 ki row "Word export"
> kehti rahi jab wo mahine pehle delete ho chuka tha; order 4 do din band nahi hui
> kyunke kaam doosre naam se aaya; P0 ki H1–H4/H6 rows **mahinon** jhooti khuli
> rahin. **Row par bharosa mat karo — repo mein naapo**, aur kaam ke usi din row
> kaato.

> **2026-08-25 — ab sirf EK bara kaam bacha hai, do nahi.**
>
> 2026-08-21 wale note ne do ginwaye the: CSS epic, aur feature order 4. **Order 4 ho
> chuka** — R7 ke naam se, 22–23 August ko (upar us ki row dekhein). To bacha:
>
> * **CSS epic (`docs/ui/`)** — apna alag plan, apni `STATUS.md`, apni `ROADMAP.md`.
>   **Sab se bara bacha hua kaam yehi hai**, aur ye is roadmap mein ab bhi kahin
>   task ki soorat mein darj nahi. Haalat 2026-08-25: `legacy_css_lines` **1,842**,
>   hadaf ~1,200–1,400. UI-061 aur UI-062 is hafte gaye.
>
> Baqi sab chhote tukde hain, magar **do ka size ghalat samjha jata raha hai**:
>
> * **Bank bharna (R1)** — "quota par ruka" kehna is ko chhota dikhata hai. Naapa gaya:
>   **128 topics baqi**, rozana quota ~23–26 calls, yani **~6 din ka rozana kaam**.
> * **R7 ka istemaal** — module ban chuka aur **khali khada hai** (`topic_week_plan`
>   mein 4 rows). Ye code ka kaam nahi, Irfan ka ek Excel bharne ka kaam hai.
>
> Aur `docs/ui/DEFERRED.md` ki khuli rows — un mein **D44/D45/D46** naye hain (2026-08-25)
> aur teenon ek hi jagah ishara karte hain: buttons ka ek task. **D45 pehle** — is repo
> mein hover/focus/disabled naapne ka koi auzaar nahi hai, aur button ka kaam poora ka
> poora unhi surfaces par hai.
>
> **Ek aur baat jo darj honi chahiye:** 2026-08-21 ka kaam is plan ke bahar tha —
> seeding karte hue teen bug nikle (AI essay banata hi nahi tha, `advanced` bloom
> ulta chalta tha, aur grade kahin filter hi nahi karta tha). Un ke baghair seeding
> ka koi faida na hota: bhara hua bank teacher tak pohanchta hi nahi. Plan se hatna
> theek tha; **plan ki dastaveiz update na karna ghalat tha.**

> **2026-08-20 ka note — is list ke daawe naapne par ghalat nikalte hain.**
> Order 1 ki row kehti thi "UI/print/**Word**" jabke Word export mahine pehle
> delete ho chuka tha, aur uska aadha kaam (`sections_meta` column, print ka
> renderer, blueprint papers) **pehle se bana hua tha**. Kaam uthane se pehle
> repo mein naap lo ke kya mojood hai — row par bharosa mat karo.

## E. Standing Reminders

- Gemini key rotation still pending (aistudio access issue) — retry occasionally. **Khuli hai
  2026-08-25 tak.**
- Any future key that appears in chat/screenshot = rotate.
- Update this file at the end of every session (it is the living plan).

> **⚠ Aakhri qaida sab se zyada tori gayi hai, aur us ki qeemat is file mein har jagah
> nazar aati hai.** Naapa gaya 2026-08-25:
>
> | row | kitni der jhooti khuli rahi |
> |---|---|
> | P0 ki H1–H4, H6 | **mahinon** — kaam kab ka ho chuka tha, sirf yahan kaata nahi gaya |
> | order 1 ka "Word export" | mahina — feature delete ho chuka tha, row use maang rahi thi |
> | order 4 (Lesson Plan) | do din — kaam R7 ke naam se aaya, row pehchan hi na saki |
> | pehli line ke "242 tests / prod live" | hafte — asal mein 1,075 tests, aur prod hai hi nahi |
>
> **In mein se koi bhi ghalti kaam ki ghalti nahi thi — sab dastavez ki thin.** Nateeja ek
> hi hota hai: agla session ghalat row uthata hai, ya ho chuka kaam dobara plan karta hai.
>
> **Do amali baatein:**
> 1. **Row kaam ke usi din kaato**, "baad mein" nahi. Jo do din mein nahi kata, wo do mahine
>    nahi katta.
> 2. **Agar kaam kisi aur naam se aaya hai to dono naam row mein likho.** Order 4 isi ek
>    wajah se khuli rahi — "Lesson Plan" dhoondne wala "R7" ko pehchan nahi sakta.
