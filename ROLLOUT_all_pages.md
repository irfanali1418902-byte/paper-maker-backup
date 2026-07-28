# PaperMaker — Poore App par Theme Rollout (CLI Spec)

**Maqsad:** Sirf blueprint nahi — **saare pages** (My Papers, Analytics, Question Bank, Image Library, SLO Health, Blueprint, Exam Taqseem, Coverage, More/Settings) ek-jaisa mockup-Classic look mein. Micro-steps ke bajaye ek `theme.css` + har page par ek `<link>` line.

**File:** naya `static/theme.css` (is spec ke saath diya hua — replace existing) is source of truth.

---

## 0. Pehle (safety)
1. `backup.bat` chalao (E: connected).
2. Working tree clean karo ya note karo — Round 1 commit `6d4123c` already hai; yeh rollout uske upar.

---

## 1. theme.css install
- Diya hua `theme.css` `static/` mein rakho (agar purana chhota hai to isse replace — yeh superset hai, saare component classes + tokens).
- Verify: `curl -sI localhost:8000/static/theme.css` → 200, text/css.

## 2. Har page par ek line add (sirf link — logic zero)
Har HTML page ke `<head>` mein, `app.css` ke baad:
```html
<link rel="stylesheet" href="/static/theme.css">
```
Pages (jo mojood hain, verify karo): `index.html` (My Papers/Generator), `blueprint.html`, `bank.html` (Question Bank), `taqseem.html`, `analytics.html`, `library`/image pages, `slo`/SLO Health page, settings page. **Sirf jo exist karein.** Ek `grep -L "theme.css" static/*.html` se pata karo kaunse baaki hain.

> blueprint.html mein link already hai (Round 1) — dobara mat daalo.

## 3. Token reconcile (har page — CSS only, koi markup/JS nahi)
Har page ke apne `<style>` `:root` mein jo local hex hain, unhe theme tokens par re-point karo (jaise blueprint mein kiya). Pattern:
```
--primary: var(--brand);   --primary-hover: var(--brand-2);
--surface: var(--panel);   --bg: var(--app-bg);
--border:  var(--line);    --ink: var(--fg);
--ok-*: green tokens; --warn-*: yellow; --err-*: red;
```
Sirf color literals → tokens. **Koi id/onclick/handler/DB/route nahi.**

## 4. Markup map (per page — visual layout, sirf wrapper divs)
Yeh sirf presentational wrappers hain — har `id`/`onclick`/`label`/`name` andar waise ke waise:
- Har "section box" → `.card.has-ch > .ch(<h3>Title</h3>) + .cb(body)`.
- Page title → `.pagehead > h1 + p` (subtitle **neeche**, saath nahi).
- SLO code → `.tag`; status → `.badge.g/.y/.r` (green>=100 / yellow 60-99 / red<60; Unassigned=null).
- Buttons → `.btn / .btn.gold / .btn.ghost`.
- Tables → `.tbl`.
- Toggles → `.switch(+.on)`.
- Shortfall/soft guidance → `.panel-soft` ("tajweez — hukm nahi").
- Section builder rows (blueprint) → `.sec/.sh/.body/.qrow/.pin`.

**Copy-paste mockup se NAHI** — sirf visual language map karo apne markup par.

## 5. Guardrails (non-negotiable — har page)
- Koi `id`/`onclick`/`name`/`data-*` NAHI badlega. JS `getElementById`/`querySelector`/handler targets intact.
- Koi naya route/DB column NAHI.
- Colors sirf theme.css tokens; fonts offline (koi CDN).
- Draft questions paper mein nahi; coverage query, `_apply_pinned`, taqseem validation byte-identical.
- Har page se pehle: `grep -n "getElementById\|querySelector\|onclick=\|id=" <page>` → lock-list; un elements ke id/handler lock.

## 6. Order (ek page = ek commit; push NAHI)
1. blueprint.html poora khatam (baaki cards: Preset, Sections, Saved) — Steps jo chal rahe.
2. index.html (My Papers / Generator).
3. bank.html (Question Bank).
4. taqseem.html (Exam Taqseem).
5. Coverage / SLO Health page.
6. analytics.html.
7. Image Library page.
8. Settings / More.

Har page ke baad: incognito hard-refresh (Ctrl+Shift+R) screenshot → Irfan ko dikhao → approve → commit (Summary bharo) → **push Irfan GitHub Desktop se**.

## 7. Har page ki "done" checklist
- [ ] theme.css linked; `git diff` mein koi id/onclick/label change nahi.
- [ ] Cards `.card.has-ch`, page header `.pagehead`, badges/chips/tags/buttons/tables theme classes par.
- [ ] Traffic-light + Unassigned=null sahi.
- [ ] JS chalti hai (incognito test): dropdowns, pins, coverage, generate, save.
- [ ] `pytest` + `ruff` + `node --check` pass.
- [ ] Commit + Summary. Push NAHI.

---

## 8. CLI prompt (copy-paste)
```
Read ROLLOUT_all_pages.md fully. theme.css (diya hua) static/ mein install/replace karo — yeh saare component classes + Classic tokens ka source of truth hai. papermaker-mockup sirf visual reference (copy-paste NAHI).

Maqsad: saare pages ek-jaisa mockup-Classic look. Section 6 order.

Ab shuru: (a) theme.css install + verify 200. (b) grep -L se pata karo kaunse pages mein theme.css link nahi — un sab ke <head> mein link line add karo (sirf link, koi logic nahi). Yeh ek commit ("theme: link theme.css across all pages"). Diff dikha kar ruko.

Uske baad ek-ek page: token reconcile + markup map (Section 4). Har page se pehle grep se JS-touched lock-list banao. Har page ke baad ruko, git diff (sirf class/CSS/wrapper) + pytest+ruff+node --check dikhao, incognito screenshot ke liye ruko. Commit karo par PUSH mat karo.

Non-negotiable: koi id/onclick/handler/name/data-attr/route/DB NAHI badlega; colors sirf tokens; fonts offline. Har page se pehle 2-line plan; approve ke baad likho.
```
