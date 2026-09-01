# Things only Irfan can settle — 2026-08-09, §5 added 2026-08-31

**Every number in §1–§4 is the board's own measured figure, copied with its source. None of it
was re-measured while writing this page. No review agent read it — Irfan reads it himself.**

**⚠ §5 is different and says so: its figures were re-measured on the day** (`css_baseline.py`
aur `css_duplication_audit.py` dobara chalayi gayin), kyunke sawal hi ye tha ke board ka
purana adad ab bhi sach hai ya nahi — aur nahi tha.

**Answer 1, 2 and 3 and three pages open with no new CSS.**

---

### 1. `landing` — the icons shrink when the page is layered · **ANSWERED: A, 2026-08-10**

**Irfan chose A — accept 17px.** No rule was written. `landing` migrated the same day (UI-047d)
and the 11 icons are 17px, matching the other eight pages.

**11 icons go 22px → 17px.** `99-legacy/landing.css`:26 (22px) wins today only by document order;
`static/app.css`:57 (17px) is unlayered, and unlayered beats every `@layer`. The other eight pages
already show 17px. *(measured 2026-08-07 · `main.css`:73-74)*

| | | |
|---|---|---|
| **A** | accept **17px** | zero work — matches every other page |
| **B** | keep **22px** | one unlayered rule in `landing`'s own entry file |

### 2. `bank` — two labels miss WCAG AA by 0.06 · **ANSWERED: B, 2026-08-10**

**Irfan delegated the call; B was taken on the measurement.** `--color-text-muted-strong`
(`--slate-600`) added and read by `forms.css`'s `label`. The two labels go **4.44 → 7.07**, and
103 labels across `bank` and `library` take the darker role. **`library` is a live page and this
changes it** — 44 labels, measured, nothing else. `slo`, `slo-health` and `landing`: 0 deltas.

**The option sheet understated the problem, and that is why B won.** slate-500 fails AA on three
Tier 2 surfaces at 12px/600, not one: tinted 4.44, **`--color-canvas` 4.48** and
`--color-surface-inset` 4.34. Canvas is the page background, so this was never only bank's two
labels. slate-600 clears all five surfaces at 6.92–7.58.

**D31 stays OPEN.** `small` and `.pagehead p` still read the weak role. See DEFERRED.md.

**2 of 59 labels land at 4.44:1 against AA's 4.5:1.** The other 57 sit on white at 4.76:1 and
pass. The two that fail are on `.urdu-toggle-row`'s tinted background. *(D31 · `bank.html`, Edge 151)*

| | | |
|---|---|---|
| **A** | accept **4.44:1** | zero work — `bank` migrates now |
| **B** | add `--color-text-muted-strong` | lifts all 59 at once — D31 calls this the one-line fix |

### 3. `print` — one real print, on a real printer · **DONE: PASSED, 2026-08-11**

**Irfan printed all three papers on real paper and passed them**: edges inside, slate ink reads
clean, pagination correct — **`0d04c750` came out at 2 pages, not 3**, so D36's fix works on a
physical printer and not only in `Page.printToPDF`. `print` migrated the same day (UI-047f).

**Not a decision, a check.** Margin is **52.9134px = exactly 14mm** on all four sides, before *and*
after migration (D35), and page counts are back to **2 / 6 / 7** (UI-044b). What is unproven is a
physical print. Ctrl+P these and look at the page edges:

```
http://127.0.0.1:8000/static/print.html?paper_id=0d04c750-ddaa-406a-a9bb-a154cf487c9d   2 pages
http://127.0.0.1:8000/static/print.html?paper_id=a5015cda-8269-4e96-8e87-82da9ccf091f   6 pages
http://127.0.0.1:8000/static/print.html?paper_id=9ade2655-21e6-449d-943a-ae875542012e   7 pages
```

Also say yes or no to one change: printed ink goes near-black → slate on 400+ elements (F1) — the
same change already live on the three migrated pages.

### 4. `index` — the Urdu toggle loses Nastaliq

**Correction: `index` was recorded as blocked on D22, and that was wrong. D22 is a technical
constraint, not your call** — the button reset can only land in the commit that re-classes the
markup, which is Sprint 6. The real blocker is narrower: **`index.html`:21's اردو button renders in
the Latin body sans**, because `03-elements/forms.css`:101's `button { font-family: inherit }`
outranks `99-legacy/index.css`:34 by layer order. *(measured UI-032, 2026-08-04)*

| | | |
|---|---|---|
| **A** | page-scoped rule in `index`'s entry file | small, contained, no other page touched |
| **B** | narrow `forms.css`'s `button` | edits a reviewed file live on all nine pages |

---

| # | answer |
|---|---|
| 1 `landing` icons | **A — 17px. Answered 2026-08-10, page migrated** ✅ |
| 2 `bank` labels | **B — darker role. Answered 2026-08-10, page migrated** ✅ |
| 3 `print` | **PASSED — edges OK, ink OK, 2/6/7 on paper. 2026-08-11** ✅ |
| 4 `index` toggle | **A — page-scoped in `index`'s entry file. Answered 2026-08-13** ✅ |

**Scope of 4, measured 2026-08-13 before it was answered:** exactly **2 elements**, both
`<button class="urdu">`. The `<input class="urdu">` at `index.html`:444 is safe — it carries an
inline `style` with the Nastaliq stack, and inline beats every layer. `bank` and `print` are
not affected: their `urdu-toggle-row`, `qtext-ur`, `school-ur` and `urdu-input` are different
class names that `.urdu` does not match. A first grep said otherwise and was wrong — ``
treats the hyphen as a word boundary, the same trap this epic hit on `app-nav` a day earlier.

---

### 5. Target — `legacy_css_lines` ka aakhri adad · **ANSWERED: ~1400, 2026-08-31**

**Irfan ne range khatam ki: ek adad, `~1400`.** Purana `1,200–1,400` mansookh.

Sawal kyun uthana para: **`1,200` riyazi taur par pohanch se bahar tha.** 2026-08-31 ko
`css_duplication_audit.py` dobara chali — `agree` **76** + `disagree` **232** = **308 lines
scope mein**, aur us waqt `legacy_css_lines` **1729** tha. Baqi 1,051 lines page-only hain,
jo 2026-08-19 ko jaan-boojh kar scope se bahar ki gayi thin.

| | | |
|---|---|---|
| **A** | target **~1400** | scope waise hi rahe; bacha kaam kar ke epic band |
| **B** | page-only ki 1,051 lines mein se kuch scope mein lao | sirf `99-legacy/<page>.css` → `pages/<page>.css` shift — na duplication ghatti hai, na CSS |

**A liya gaya.** Aaj ka faasla: **1707 − 1400 = 307 lines**, yani lag-bhag utna hi jitna
scope mein bacha hai — target pohanch mein hai magar har bacha hua tukda chahiye.

### 6. Item 8 ka tail — teen rules jo do-do files mein hain **aur aapas mein mel nahi khatin**

**Ye "chhe lines delete karo" wala kaam nahi nikla.** `STATUS.md` ka row in teen rules ko
6 lines kehta tha; 2026-09-01 ko grep aur probe se naapa gaya to **teenon ki do-do copies
hain aur har jodi mein qadrein alag hain.** Isi liye audit ne inhein `disagree` mein rakha
hai — `disagree` ka matlab hi yehi hai ke copies aapas mein ikhtilaf rakhti hain, is liye
**pehle faisla, phir component.**

**Naapa gaya (probe, 1280px):**

```
.options-grid   bank    gap=8px  margin-top=8px
                print   gap=6px  margin-top=0px
```

| rule | kahan | ikhtilaf |
|---|---|---|
| `.options-grid` | `bank.css:77`, `print.css:257` | gap **8px** banaam **6px**; bank par `margin-top: 8px`, print par nahi. Print ke paas `.options-grid input { width:100% }` bhi hai, bank ke paas nahi. Bank ke paas `@760` ka `1fr` override bhi hai. |
| `.strip-empty` | `bank.css:106`, `print.css:306` | sirf rang: `var(--muted2)` banaam **ek hardcoded hex**. Wo hex `unsanctioned_hex` mein ginta hai. |
| `.list-empty` | `bank.css:163`, `blueprint.css:117` | padding **40px 20px** banaam **30px**. Baqi teen declarations barabar. |

| | |
|---|---|
| **A** | **Component banao, farq page par chhoro** — mushtarka declarations `05-components/` mein, aur har page apna farq (`gap`, `margin-top`, `padding`) `pages/*.css` mein rakhe. Sab se zyada lines bachti hain, magar teen chhoti page-overrides banti hain. |
| **B** | **Ek qadar par muttafiq ho jao** — yani `gap` dono jagah 8px (ya 6px), `padding` dono jagah ek. Sab se saaf CSS, **magar ye dikhne wali tabdeeli hai** aur bank/print ka farq jaan-boojh kar bhi ho sakta hai (print ki jagah tang hoti hai). |
| **C** | **Haath na lagao** — page-only samjho, aur target ka faasla kahin aur se poora karo. |

**Do baatein jo faisle se pehle jaan lena zaroori hai:**

* **`.strip-empty` aur `.list-empty` dono JS se bante hain** (`innerHTML`, `bank.html:844`,
  `:1007`, `print.html:354`, `bank.html:1256`, `blueprint.html:1063`). **`css_type_probe`
  aur `css_state_probe` inhein sifar elements ginte hain, yani ghalat tabdeeli par bhi
  0 deltas denge** (D45 ki shakl, PROBES.md rule 10). `css_inject_probe.mjs` ke fixtures
  mein ye do abhi **nahi** hain — B ya A par jane se pehle **fixtures likhni parengi.**
* **B ka ek muft faida hai:** `.strip-empty` ka print wala hardcoded hex `var(--muted2)`
  ke haq mein khatam ho jayega, yani `unsanctioned_hex` ek aur ghatega.

| # | answer |
|---|---|
| 5 target | **A — ~1400. Answered 2026-08-31** ✅ |
| 6 item-8 tail | ⬜ **khula — 2026-09-01 ko naapa aur likha gaya** |
