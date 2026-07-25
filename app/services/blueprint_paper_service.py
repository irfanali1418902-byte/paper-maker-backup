"""Assembles a paper from a Blueprint — section by section, partial-friendly.

Design rules:
- Har section ke liye available questions fetch karo; jitne hain utne use karo.
- Shortfall (maange zyada, mile kam) note karo — poora paper nahi rokta.
- Error sirf tab jab poore paper mein zero questions mile (sab sections khaali).
- sections_meta JSON paper row mein store hoti hai (print.html ke liye).
- Questions ki image_path automatic saath aati hai — koi extra step nahi.
- Naye filters: status (default published), difficulty, bloom_level.
- difficulty_distribution: per-difficulty separate fetch, per-difficulty shortfall.
"""

from __future__ import annotations

import uuid
from datetime import date
from typing import Optional

from app.repositories import papers_repository, questions_repository
from app.services import blueprint_bloom_guidance_service, item_analysis_service


def assemble_blueprint_paper(
    blueprint_id: Optional[str],
    sections_input: list[dict],
    subject: Optional[str],
    class_name: Optional[str],
    paper_title: Optional[str],
    class_tier: Optional[str] = None,
    exam_no: Optional[int] = None,
) -> dict | None:
    """Core assembly — called by route with either a saved blueprint_id
    (sections_input ignored) or inline sections_input list.

    Returns assembled paper dict, or None if every section yielded zero
    questions (caller maps to 404).

    sections_input element shape (all new fields optional for backward compat):
        heading, question_types (list), topic_ids (list), count,
        marks_each, source_filter,
        status_filter (default 'published'), difficulty_filter,
        bloom_filter, difficulty_distribution
    """
    all_question_ids: list[str] = []
    all_questions: list[dict] = []
    sections_meta: list[dict] = []
    shortfall_notes: list[str] = []
    shortfall_details: list[dict] = []

    for sec in sections_input:
        heading       = sec.get("heading", "Section")
        qtypes        = sec.get("question_types") or []
        topic_ids     = sec.get("topic_ids") or []
        wanted        = int(sec.get("count", 1))
        marks_each    = int(sec.get("marks_each", 1))
        source_filter = sec.get("source_filter", "manual")
        source_arg    = None if source_filter == "all" else source_filter

        # New filter fields — safe defaults for backward compat with old blueprints
        status_filter = sec.get("status_filter", "published")
        difficulty_filter = sec.get("difficulty_filter")
        bloom_filter  = sec.get("bloom_filter")
        distribution  = sec.get("difficulty_distribution")
        language_filter = sec.get("language_filter")

        if distribution:
            picked, sec_shortfall_notes = _fetch_with_distribution(
                subject=subject,
                topic_ids=topic_ids,
                question_types=qtypes,
                source=source_arg,
                status=status_filter,
                bloom_level=bloom_filter,
                distribution=distribution,
                wanted=wanted,
                heading=heading,
                language_filter=language_filter,
            )
        else:
            picked, sec_shortfall_notes = _fetch_simple(
                subject=subject,
                topic_ids=topic_ids,
                question_types=qtypes,
                source=source_arg,
                status=status_filter,
                difficulty=difficulty_filter,
                bloom_level=bloom_filter,
                wanted=wanted,
                heading=heading,
                language_filter=language_filter,
            )

        # Hissa 4-C: teacher ke pin kiye questions must-include. Pinned pehle (dedup,
        # order-preserve), filter-natija baqi jagah bhare; count ke andar; pinned > count
        # to count inhi tak barh jaata (`wanted` update). Non-existent id chup-chaap skip.
        pinned_ids = sec.get("include_question_ids") or []
        picked, wanted, pin_added = _apply_pinned(picked, pinned_ids, wanted)

        # Pins sirf questions ADD karte (shortfall ghata sakte). Fetch ka note original
        # wanted par bana tha — pins ki soorat mein gumraah-kun, is liye final got par
        # recompute (bina pins purana rawaiyya bilkul waisa hi).
        if pin_added:
            got_after = len(picked)
            sec_shortfall_notes = (
                [f"{heading}: {wanted} maange, {got_after} mile"] if got_after < wanted else []
            )
        shortfall_notes.extend(sec_shortfall_notes)

        # Shortfall ki soorat mein hi diagnostic — normal generation par ek bhi
        # faltu query nahi. Reason + actionable options deta hai (UI nahi chherta).
        got = len(picked)
        diag = None
        if got < wanted:
            diag = _diagnose_shortfall(
                subject,
                topic_ids=topic_ids,
                question_types=qtypes,
                source=source_arg,
                status=status_filter,
                difficulty=difficulty_filter,
                bloom_level=bloom_filter,
                distribution=distribution,
                language_filter=language_filter,
                wanted=wanted,
                got=got,
                heading=heading,
            )
            shortfall_details.append(diag)

        for q in picked:
            questions_repository.increment_usage_count(q["id"])

        sec_qids  = [q["id"] for q in picked]
        sec_marks = sum(marks_each for _ in picked)

        # reason + options ko sections_meta mein bhi rakho — paper insert ke baad
        # shortfall_details discard ho jaati hai; print.html isi persisted copy se
        # panel banata hai (blueprint jaisa). Legacy papers mein yeh keys nahi hotin.
        section_meta = {
            "heading":      heading,
            "question_ids": sec_qids,
            "marks":        sec_marks,
            "shortfall":    wanted - len(picked),
        }
        if diag:
            section_meta["shortfall_reason"]  = diag["reason"]
            section_meta["shortfall_options"] = diag["options"]
        sections_meta.append(section_meta)

        all_question_ids.extend(sec_qids)
        all_questions.extend(picked)

    if not all_questions:
        return None

    _annotate_expected_difficulty(all_questions)

    total_marks   = sum(q["marks"] for q in all_questions)
    resolved_title = _resolve_title(paper_title, subject or "", class_name)

    paper_id = str(uuid.uuid4())
    papers_repository.insert(
        paper_id=paper_id,
        subject=subject or "",
        class_name=class_name,
        total_marks=total_marks,
        question_ids=all_question_ids,
        paper_title=resolved_title,
        sections_meta=sections_meta,
        exam_no=exam_no,
    )

    return {
        "paper_id":        paper_id,
        "total_marks":     total_marks,
        "questions":       all_questions,
        "sections_meta":   sections_meta,
        "shortfall_notes": shortfall_notes,
        "shortfall_details": shortfall_details,
        "balance_summary": item_analysis_service.summarize_paper_balance(all_questions),
        "bloom_guidance": blueprint_bloom_guidance_service.compute_bloom_guidance(
            all_questions, class_tier, subject=subject,
        ),
    }


# ── private helpers ───────────────────────────────────────────────────────────

def _apply_pinned(
    picked: list[dict],
    include_question_ids: list[str],
    wanted: int,
) -> tuple[list[dict], int, bool]:
    """Teacher ke pin kiye questions (must-include) ko section mein guarantee karo.

    - Pinned PEHLE (diye gaye order mein, dedup), filter-natija (`picked`) baqi jagah.
    - Effective count = max(wanted, #valid-pins) — pinned > count to count barh jaata.
    - Pinned jo pehle se `picked` mein ho, filler se hata (double-count nahi).
    - Non-existent question_id chup-chaap skip (find_by_id None).

    Returns (merged_picked, effective_count, any_pin_added). Koi valid pin na ho to
    (picked, wanted, False) — bilkul purana rawaiyya (backward-compat)."""
    if not include_question_ids:
        return picked, wanted, False

    seen: set[str] = set()
    pinned_rows: list[dict] = []
    for qid in include_question_ids:
        if qid in seen:
            continue
        seen.add(qid)
        row = questions_repository.find_by_id(qid)
        if row is not None:
            pinned_rows.append(row)

    if not pinned_rows:
        return picked, wanted, False

    pinned_id_set = {r["id"] for r in pinned_rows}
    filler = [q for q in picked if q["id"] not in pinned_id_set]
    effective = max(wanted, len(pinned_rows))
    merged = pinned_rows + filler[: effective - len(pinned_rows)]
    return merged, effective, True


def _fetch_simple(
    subject: Optional[str],
    topic_ids: list,
    question_types: list,
    source: Optional[str],
    status: str,
    difficulty: Optional[str],
    bloom_level: Optional[str],
    wanted: int,
    heading: str,
    language_filter: Optional[str] = None,
) -> tuple[list[dict], list[str]]:
    """Single query fetch — no distribution. Returns (picked, shortfall_notes)."""
    candidates = questions_repository.find_for_blueprint_section(
        subject=subject,
        topic_ids=topic_ids,
        question_types=question_types,
        source=source,
        status=status,
        difficulty=difficulty,
        bloom_level=bloom_level,
        language_filter=language_filter,
    )
    picked = candidates[:wanted]
    notes = []
    if len(picked) < wanted:
        lang_label = {"en": " (English only)", "ur": " (Urdu only)"}.get(language_filter or "", "")
        notes.append(f"{heading}: {wanted} maange{lang_label}, {len(picked)} mile")
    return picked, notes


def _fetch_with_distribution(
    subject: Optional[str],
    topic_ids: list,
    question_types: list,
    source: Optional[str],
    status: str,
    bloom_level: Optional[str],
    distribution: dict,
    wanted: int,
    heading: str,
    language_filter: Optional[str] = None,
) -> tuple[list[dict], list[str]]:
    """Per-difficulty fetch. Returns (picked, shortfall_notes).

    distribution = {"easy": 3, "medium": 5, "hard": 2}
    sum(distribution.values()) <= wanted  (validated by Pydantic already).
    Remaining slots (wanted - sum) filled from any-difficulty pool,
    excluding already-picked ids.
    """
    picked: list[dict] = []
    notes: list[str] = []
    used_ids: set[str] = set()
    lang_label = {"en": " (English only)", "ur": " (Urdu only)"}.get(language_filter or "", "")

    for diff, need in distribution.items():
        if need <= 0:
            continue
        candidates = questions_repository.find_for_blueprint_section(
            subject=subject,
            topic_ids=topic_ids,
            question_types=question_types,
            source=source,
            status=status,
            difficulty=diff,
            bloom_level=bloom_level,
            language_filter=language_filter,
        )
        # Exclude already-picked ids (shouldn't overlap, but be safe)
        candidates = [q for q in candidates if q["id"] not in used_ids]
        slot = candidates[:need]
        found = len(slot)
        if found < need:
            notes.append(f"{heading}: {need} {diff} maange{lang_label}, {found} mile")
        picked.extend(slot)
        used_ids.update(q["id"] for q in slot)

    # Fill remaining slots (unspecified difficulty)
    distributed_sum = sum(distribution.values())
    remaining = wanted - distributed_sum
    if remaining > 0:
        extra_candidates = questions_repository.find_for_blueprint_section(
            subject=subject,
            topic_ids=topic_ids,
            question_types=question_types,
            source=source,
            status=status,
            difficulty=None,
            bloom_level=bloom_level,
            language_filter=language_filter,
        )
        extra_candidates = [q for q in extra_candidates if q["id"] not in used_ids]
        extra = extra_candidates[:remaining]
        if len(extra) < remaining:
            notes.append(f"{heading}: {remaining} remaining maange{lang_label}, {len(extra)} mile")
        picked.extend(extra)
        used_ids.update(q["id"] for q in extra)

    return picked, notes


def _diagnose_shortfall(
    subject: Optional[str],
    *,
    topic_ids: list,
    question_types: list,
    source: Optional[str],
    status: str,
    difficulty: Optional[str],
    bloom_level: Optional[str],
    distribution: Optional[dict],
    language_filter: Optional[str],
    wanted: int,
    got: int,
    heading: str,
) -> dict:
    """Shortfall ki WAJAH + actionable OPTIONS. SIRF got < wanted par call hota hai.

    Do alag ginti (sirf LAGI HUI shartein test hoti hain):
      - solo_count : sirf yeh shart, baqi sab (diagnosable) hata kar. REASON ke liye —
                     'tang' shart wohi jis ki APNI ginti sab se KAM ho.
      - would_give : sirf yeh shart hata kar, baqi waise. OPTIONS ke liye — un ka
                     tarteeb would_give ke desc order mein (sab se zyada faida pehle).

    Distribution wale section mein would_give _fetch_with_distribution se hoti hai
    taake used_ids/slice ka hisaab theek rahe (raw SQL count over-count karta).
    solo_count hamesha ek saada pool-count hai (koi distribution/cap nahi) — us shart
    ke apne questions kitne hain. would_give sirf ginti hai, koi paper assemble nahi.
    """
    lang_word = {"en": "English", "ur": "Urdu"}.get(language_filter or "", "")

    # (key, active?, would_give-override, option-label, reason-phrase(solo_count))
    specs = [
        ("bloom_level", bool(bloom_level), {"bloom_level": None},
         "Bloom shart hata dein",
         lambda n: f"Bloom '{bloom_level}' ke is subject mein sirf {n} questions hain"),
        ("difficulty", bool(difficulty), {"difficulty": None},
         "Difficulty shart hata dein",
         lambda n: f"Difficulty '{difficulty}' ke is subject mein sirf {n} questions hain"),
        ("question_types", bool(question_types), {"question_types": []},
         "Question type shart hata dein",
         lambda n: f"Is question type ke is subject mein sirf {n} questions hain"),
        ("topic_ids", bool(topic_ids), {"topic_ids": []},
         "Topic barha dein (poora subject)",
         lambda n: f"Chune gaye topics mein sirf {n} questions hain"),
        ("language_filter", bool(language_filter), {"language_filter": None},
         "Language shart hata dein (dono zabaan)",
         lambda n: f"{lang_word} mein is subject ke sirf {n} questions hain"),
        ("status", status != "all", {"status": "all"},
         "Draft/archived bhi shamil karein",
         lambda n: f"'{status}' status ke sirf {n} questions hain"),
    ]

    def _would_give(override: dict) -> int:
        if distribution:
            # Distribution mode: asal fill logic dobara chalao (used_ids + per-bucket
            # slice replicate hote hain). 'difficulty' yahan top-level shart nahi.
            kwargs = dict(
                subject=subject,
                topic_ids=topic_ids,
                question_types=question_types,
                source=source,
                status=status,
                bloom_level=bloom_level,
                distribution=distribution,
                wanted=wanted,
                heading=heading,
                language_filter=language_filter,
            )
            kwargs.update(override)
            picked, _ = _fetch_with_distribution(**kwargs)
            return len(picked)
        # Simple mode: raw available pool (uncapped) — teacher ko batata hai kitne
        # questions maujood hain (misaal: 8 -> 24).
        kwargs = dict(
            subject=subject,
            topic_ids=topic_ids,
            question_types=question_types,
            source=source,
            status=status,
            difficulty=difficulty,
            bloom_level=bloom_level,
            language_filter=language_filter,
        )
        kwargs.update(override)
        return len(questions_repository.find_for_blueprint_section(**kwargs))

    def _solo_count(key: str) -> int:
        # Sirf yeh ek shart; baqi diagnosable shartein neutral. subject + source
        # (jo diagnosable nahi) waise hi rehte. Koi distribution/cap nahi.
        kwargs = dict(
            subject=subject, source=source,
            topic_ids=[], question_types=[], status="all",
            difficulty=None, bloom_level=None, language_filter=None,
        )
        section_values = {
            "bloom_level": bloom_level,
            "difficulty": difficulty,
            "question_types": question_types,
            "topic_ids": topic_ids,
            "language_filter": language_filter,
            "status": status,
        }
        kwargs[key] = section_values[key]
        return len(questions_repository.find_for_blueprint_section(**kwargs))

    active = [(key, ov, label, reason_fn) for (key, act, ov, label, reason_fn) in specs if act]

    # REASON: tang shart = jis ki APNI ginti (solo_count) sab se KAM. Ties -> pehla.
    if active:
        solo = {key: _solo_count(key) for (key, _ov, _label, _rfn) in active}
        tight_key, _ov, _label, tight_rfn = min(active, key=lambda a: solo[a[0]])
        reason = tight_rfn(solo[tight_key])
    else:
        reason = f"Is subject mein sirf {got} questions maujood hain"

    # OPTIONS: sirf faida-mand (would_give > got), would_give ke desc order mein,
    # max 2 filter-options, phir hamesha aakhri "jitne mile utne par" option.
    scored = []
    for key, ov, label, _rfn in active:
        wg = _would_give(ov)
        if wg > got:
            scored.append((wg, key, label))
    scored.sort(key=lambda x: x[0], reverse=True)

    options = [
        {"filter": key, "label": label, "would_give": wg}
        for (wg, key, label) in scored[:2]
    ]
    options.append({"filter": None, "label": f"{got} par hi paper banayen", "would_give": got})

    return {
        "heading": heading,
        "wanted": wanted,
        "got": got,
        "reason": reason,
        "options": options,
    }


def _resolve_title(paper_title: Optional[str], subject: str, class_name: Optional[str]) -> str:
    if paper_title and paper_title.strip():
        return paper_title.strip()
    parts = [subject] if subject else []
    if class_name:
        parts.append(class_name)
    parts.append(date.today().strftime("%d %b %Y"))
    return " – ".join(parts) if parts else "Blueprint Paper"


def _annotate_expected_difficulty(questions: list[dict]) -> None:
    for q in questions:
        q["expected_difficulty"] = item_analysis_service.expected_difficulty(q["bloom_level"])
        q["difficulty_mismatch"] = item_analysis_service.is_difficulty_mismatch(
            q.get("difficulty"), q["bloom_level"]
        )
