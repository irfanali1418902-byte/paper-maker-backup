# Hafta-war Plan + Coverage — Spec (R7)

**Banaya:** 2026-08-22 · **Haalat:** Marhala 1 zer-e-kaam
**PRD:** R7 — *"create/store lesson plans linked to topics; report showing
paper-vs-plan coverage"* · **ROADMAP:** feature order 4

---

## 0. Faisle jo Irfan ne kiye (2026-08-22)

| sawal | jawab |
|---|---|
| "Lesson plan" ka daira | **Taqseem-e-auqat + coverage** — kaunsa topic kis hafte, aur paper ne us ke muqable kya cover kiya. Sabaq ka mazmoon (maqasid/sargarmiyan/materials) is module mein **NAHI** |
| Data kaise bharega | **Excel upload** — SLO tagging jaisa. Manual form sirf fallback |

Ye faisle dobara na kholein bina ye tay kiye ke kya badla.

---

## 1. Naam: "Lesson Plan" kyun nahi

Repo mein **taqseem** pehle se SLO → exam ke liye hai (`slo_exam_plan`,
`taqseem_service`, `taqseem.html`). Ye module topic → hafta hai. Dono ko ek naam
dena baad mein mehnga parega — code mein `topic_week_plan`, UI mein "Hafta-war
Plan".

---

## 2. Ye naya module nahi — aadhi machinery mojood hai

"Planned vs actual" ki shakal is repo mein pehle se do dafa bani hui hai:

| mojooda cheez | planned | actual |
|---|---|---|
| Taqseem | kaunsa SLO kis exam mein (`slo_exam_plan`) | `papers.exam_no` + `question_slo` |
| `coverage_service` | dono ko milata hai, **live compute** | — |

**Jo waqai naya hai wo sirf waqt ka dimension hai** — kaunsa topic kab.

⚠ **Ek daawa jo naapne par poora sach nahi nikla:** `coverage_service` ka docstring
kehta hai `_assemble_coverage` "DB-FREE hai taake dobara istemal ho". Wo waada
**SLO ke daire ke andar** tha (draft question_ids). Function khud **SLO-keyed** hai —
`s["slo_id"]` aur `strand` par chalta hai. Topic ke liye us ki key parameterize karni
paregi. Chhota refactor hai, magar hai, aur ye Marhala 3 ka kaam hai.

---

## 3. Data model

```
topic_week_plan
  syllabus_topic_id   TEXT/INTEGER  PK, FK -> syllabus_topics.id
  week_no             INTEGER
  position            INTEGER NULL
  updated_at          TIMESTAMP
```

`slo_exam_plan` (`slo_id, exam_no, position, updated_at`) ka **hu-ba-hu aaina** —
jaan-boojh kar. Us ka repository, service, aur "unassigned bucket" ka rule pehle se
aazmaya hua hai.

**Unassigned bucket:** `week_no` 0 / NULL / `>N` = un-assigned. Yehi
`taqseem_service` ka rule hai; dono ek jaise rahein.

**`week_count`** `school_settings` mein jayega, `exam_count` ki tarah, aur
`_week_count()` bilkul `_exam_count()` ke usool par: `int()` na bane to default,
`>= 1` warna default. **Default 36.**

**"Hafta" = ginti (1..N), tareekh NAHI.** Tareekh se timezone, chhuttiyan, aur "saal
kab shuru hua" ke sawal aate hain. `exam_no` bhi ginti hi hai. Tareekh baad mein is
ke oopar lag sakti hai.

---

## 4. Files — layering (`api -> services -> repositories -> core`)

| file | kaam | kis ka aaina |
|---|---|---|
| `app/repositories/topic_week_plan_repository.py` | sirf SQL | `slo_exam_plan_repository` |
| `app/services/topic_week_service.py` | assign / move / list | `taqseem_service` |
| `app/services/topic_week_import_service.py` | Excel | `slo_import_service` |
| `app/services/topic_coverage_service.py` | planned vs covered | `coverage_service` |
| `app/api/topic_plan.py` | routes | `app/api/taqseem.py` |
| `static/plan.html` + `static/css/pages/plan.css` | UI | `taqseem.html` |

---

## 5. Coverage ka hisaab

* **planned** = us hafte ke topics (`topic_week_plan`)
* **covered** = wo topics jo kisi paper mein aaye
  `papers.question_ids` -> `questions.syllabus_topic_id`
* **Live compute, koi stored snapshot nahi** — `coverage_service` ka mojooda usool
  (plan ya paper baad mein badle to report khud sahi rahe)

**Naapa gaya 2026-08-22:** 30/30 papers is raaste se topics tak jurte hain, aur 594
mein se **464** sawalon par `syllabus_topic_id` hai. Yani ye module **pehle din se
asal data dikhayega** — Hissa B wali soorat nahi hogi jahan SLO tagging tak sab
khali raha.

---

## 6. Endpoints

```
GET    /api/topic-plan?subject=&grade=              topics + week_no
GET    /api/topic-plan/template                     Excel template download
POST   /api/topic-plan/assign-import                bhari hui Excel upload
PATCH  /api/topic-plan/{topic_id}                   ek topic ka hafta badlo
GET    /api/topic-plan/coverage?subject=&grade=     planned vs covered
```

---

## 7. Excel ka raasta

Teen column:

| column | kaam |
|---|---|
| `syllabus_topic_id` | **mat chhuo** — matching isi se hoti hai, title se nahi |
| `subtopic_title` | sirf parhne ke liye, taake pata chale kaunsi row hai |
| `week_no` | Irfan bharega |

**Replace-set semantics**, SLO tagging jaisi: khali cell = us topic ka hafta
**clear**. Dobara upload mehfooz (idempotent). Ghalat `syllabus_topic_id` par saaf
error — chup-chaap nazar-andaaz **nahi**.

---

## 8. Marhale

| # | kaam | tests (andaza) | haalat |
|---|---|---|---|
| 1 | table + repository + service + assign/list API | ~18 | **✅ 2026-08-22** (50 tests) |
| 2 | Excel import + template | ~12 | **✅ 2026-08-22** (29 tests) |
| 3 | coverage service + endpoint (`_assemble_coverage` key parameterize) | ~15 | — |
| 4 | UI page | ~5 | **✅ 2026-08-23** — neeche §8.1 |

### 8.1 Marhala 4 — jo bana, aur jo tarteeb se hat kar bana

**Marhala 4 ko Marhala 3 se PEHLE kiya gaya, aur ye Irfan ka faisla tha.** Wajah
naapi hui thi: `topic_week_plan` mein **0 rows** thin. Coverage report ("planned vs
covered") ka koi matlab nahi jab plan mein data hi na ho — pehle bharne ka zariya,
phir report. Marhala 3 ab bhi baqi hai aur page us ke liye khula hai.

**Kanban board NAHI banaya gaya, table banayi gayi — aur ye §4 se hatna hai.** §4
kehta hai UI `taqseem.html` ka aaina ho. Naapne par wo shakal yahan tootti hai:
`exam_count` **8** hai, `week_count` **36**. taqseem ka board 9 columns ka hai; yahan
wohi shakal **37 columns × 87 topics** deti — na screen par aati, na us mein "hafta 7
khali hai" dikhta. To page ek table hai (Unit / Topic / Page / Hafta-dropdown) plus
upar har hafte ki ginti ka strip. Move ka raasta wohi hai jo taqseem par hai — ek
`<select>`, drag nahi.

**Teen cheezein jo `taqseem.html` se jaan-boojh kar mukhtalif hain:**

1. **Template `apiFetch` se aati hai, `window.location` se nahi.** `slo.html` seedha
   `href` istemal karti hai; wo `x-api-key` header nahi bhejta, to jis deployment par
   key set hai wahan wo download **401** ho jata. Yahan blob bana kar diya jata hai,
   aur filename server ke `Content-Disposition` se — naam wahan pehle se banta hai
   (`template_filename`), dobara banane ki zaroorat nahi.
2. **Grade ki list subject par munhasir hai.** `/api/syllabus-grades` jode deta hai;
   Mathematics ke paas Pre Year 1..3 hain aur Geography ke paas sirf Grade 8. Do
   azaad dropdown aise jode bana dete jin ka koi topic nahi.
3. **Khali hafte dikhte hain, gayab nahi hote** (strip mein dabe hue). "Hafta 7 khali
   hai" wohi maloomat hai jo teacher dhoondh raha hai.

**Page ka koi 99-legacy file nahi — pehla aisa page.** Tafseel
`static/css/pages/plan.css` ke header mein. Naapa gaya nateeja: `legacy_css_lines`
is page ke aane se **+0**, aur har ratcheted metric bhi **+0**.

**Kul ~50 nayi tests. Andaza: ~2 hafte** — ROADMAP ka "size L" naapne par zyada
lagta hai, kyunke machinery mojood hai. Ye andaza Marhala 1 ke baad durust hoga.

**Marhala 1–3 UI ke baghair kaam ke hain:** Excel se plan bhar kar coverage `curl`
se dekhi ja sakti hai. Waqt kam ho to Marhala 4 rok kar bhi faida milta hai.

---

## 9. Chaar baatein jo pehle se saaf hain

1. **`_assemble_coverage` ko chherna** ek aazmayi hui function ko chherna hai. Us ke
   mojooda tests hi gate hain — **SLO coverage tootni nahi chahiye.**
2. **130 sawal (English) topic se nahi jure** — un ka syllabus hai hi nahi, to wo
   kabhi coverage mein nahi aayenge. Ye module ki kami nahi, data ki soorat hai.
3. **`plan.html` daswan page hoga** — ITCSS tree mein naya entry file aur
   `BASELINE.json` mein entry chahiye hogi. Ye qeemat Marhala 4 mein shamil hai.
4. **Chaar jaali syllabi** (Math G5/G6, Science G7, Geography G8) — un ke topics par
   plan banana be-maani hai jab tak asal syllabus import na ho. UI un ko dikhaye to
   dikhaye, magar in par waqt zaya na kiya jaye.
