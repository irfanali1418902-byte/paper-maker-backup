"""Tests for shortfall reason + options (feature/shortfall-reason).

Diagnostic sirf shortfall (got < wanted) par chale; reason + actionable options
de; would_give sach ho; purana shortfall_notes format bilkul waisa rahe;
bina shortfall ke shortfall_details khali ho. Distribution ke would_give mein
used_ids/slice ka hisaab (KHAAS MASLA) theek ho.
"""

from __future__ import annotations

import json
import uuid

import pytest
from fastapi.testclient import TestClient

from app.repositories import questions_repository


@pytest.fixture
def client(test_db):
    from app.main import app
    return TestClient(app)


def _insert_q(
    subject="Science",
    qtype="multiple-choice",
    topic_id=None,
    source="manual",
    difficulty="medium",
    bloom_level="UNDERSTAND",
    status="published",
):
    qid = str(uuid.uuid4())
    questions_repository.insert({
        "id": qid,
        "subject": subject,
        "topic": "Test Topic",
        "bloom_level": bloom_level,
        "difficulty": difficulty,
        "question_type": qtype,
        "marks": 1,
        "question_en": f"Q {qid[:6]}?",
        "question_ur": None,
        "options_en": json.dumps(["A", "B", "C", "D"]) if qtype == "multiple-choice" else "[]",
        "options_ur": "[]",
        "correct_answer_en": "A",
        "correct_answer_ur": None,
        "explanation_en": None,
        "explanation_ur": None,
        "visual_emoji": None,
        "visual_count": None,
        "syllabus_topic_id": topic_id,
        "source": source,
        "status": status,
    })
    return qid


def _section(heading="Sec A", count=5, **extra):
    sec = {
        "heading": heading,
        "question_types": ["multiple-choice"],
        "topic_ids": [],
        "count": count,
        "marks_each": 1,
        "source_filter": "manual",
        "status_filter": "published",
    }
    sec.update(extra)
    return sec


def _post(client, sections, subject="Science"):
    return client.post("/api/blueprint-paper", json={
        "sections_input": sections,
        "subject": subject,
    })


# ── no shortfall → koi details nahi ─────────────────────────────────────────────

class TestNoShortfall:
    def test_full_section_has_empty_shortfall_details(self, client):
        for _ in range(5):
            _insert_q()
        res = _post(client, [_section(count=3)])
        assert res.status_code == 200
        body = res.json()
        assert body["shortfall_details"] == []
        assert body["shortfall_notes"] == []

    def test_exact_fill_no_details(self, client):
        """got == wanted (bilkul poora) → koi shortfall detail nahi."""
        for _ in range(3):
            _insert_q()
        res = _post(client, [_section(count=3)])
        assert res.status_code == 200
        assert res.json()["shortfall_details"] == []


# ── old format untouched ────────────────────────────────────────────────────────

class TestOldNotesFormat:
    def test_shortfall_notes_string_unchanged(self, client):
        """Purana '<heading>: <wanted> maange, <got> mile' bilkul waisa rahe."""
        for _ in range(8):
            _insert_q(bloom_level="APPLY")
        res = _post(client, [_section(heading="Section A", count=20, bloom_filter="APPLY")])
        assert res.status_code == 200
        notes = res.json()["shortfall_notes"]
        assert "Section A: 20 maange, 8 mile" in notes


# ── simple shortfall: reason + options ──────────────────────────────────────────

class TestSimpleShortfall:
    def test_bloom_tight_reason_and_options(self, client):
        """8 APPLY + 16 UNDERSTAND; section 20 APPLY maange → 8 mile.
        Bloom hatane se 24 → reason bloom, option would_give=24."""
        for _ in range(8):
            _insert_q(bloom_level="APPLY")
        for _ in range(16):
            _insert_q(bloom_level="UNDERSTAND")
        res = _post(client, [_section(heading="Section A", count=20, bloom_filter="APPLY")])
        assert res.status_code == 200
        body = res.json()
        assert len(body["questions"]) == 8

        details = body["shortfall_details"]
        assert len(details) == 1
        d = details[0]
        assert d["heading"] == "Section A"
        assert d["wanted"] == 20
        assert d["got"] == 8
        # reason = tang shart ki APNI ginti (solo_count); yahan bloom solo == 8
        assert "Bloom" in d["reason"] and "APPLY" in d["reason"] and "8" in d["reason"]

        opts = d["options"]
        assert len(opts) <= 3
        bloom_opt = next(o for o in opts if o["filter"] == "bloom_level")
        assert bloom_opt["would_give"] == 24
        # aakhri option hamesha "jitne mile utne par"
        assert opts[-1]["filter"] is None
        assert opts[-1]["would_give"] == 8

    def test_would_give_is_truthful(self, client):
        """would_give=24 = bloom hata kar asal available count."""
        for _ in range(8):
            _insert_q(bloom_level="APPLY")
        for _ in range(16):
            _insert_q(bloom_level="UNDERSTAND")
        # bloom option would_give
        res = _post(client, [_section(count=20, bloom_filter="APPLY")])
        wg = next(o["would_give"] for o in res.json()["shortfall_details"][0]["options"]
                  if o["filter"] == "bloom_level")
        # bloom hata kar bara paper — utne hi asal mein milne chahiye
        res2 = _post(client, [_section(count=100)])
        assert len(res2.json()["questions"]) == wg == 24

    def test_only_helpful_filters_and_ordering(self, client):
        """Do filters faida dein (topic 30, bloom 15) → desc order, reason=max,
        max 3 options, aakhri 'make paper'."""
        for _ in range(5):
            _insert_q(topic_id="topic-1", bloom_level="APPLY")
        for _ in range(10):
            _insert_q(topic_id="topic-1", bloom_level="UNDERSTAND")
        for _ in range(25):
            _insert_q(topic_id=None, bloom_level="APPLY")
        res = _post(client, [_section(count=20, topic_ids=["topic-1"], bloom_filter="APPLY")])
        assert res.status_code == 200
        d = res.json()["shortfall_details"][0]
        assert d["got"] == 5
        # reason: topic ki APNI ginti (solo=15) sab se kam → reason topic, count 15
        assert "opic" in d["reason"] and "15" in d["reason"]
        opts = d["options"]
        assert len(opts) == 3
        assert opts[0]["filter"] == "topic_ids" and opts[0]["would_give"] == 30
        assert opts[1]["filter"] == "bloom_level" and opts[1]["would_give"] == 15
        assert opts[2]["filter"] is None and opts[2]["would_give"] == 5

    def test_no_helpful_filter_still_names_tightest(self, client):
        """Sirf 3 APPLY maujood; 10 maange. Koi filter hatane se faida nahi →
        options sirf 'make paper'. Lekin reason phir bhi tang shart (bloom, solo=3)
        naam le — generic nahi (kyunke bloom shart waqai lagi hui hai)."""
        for _ in range(3):
            _insert_q(bloom_level="APPLY")
        res = _post(client, [_section(count=10, bloom_filter="APPLY")])
        assert res.status_code == 200
        d = res.json()["shortfall_details"][0]
        assert d["got"] == 3
        assert d["options"] == [{"filter": None, "label": "3 par hi paper banayen", "would_give": 3}]
        assert "Bloom" in d["reason"] and "APPLY" in d["reason"] and "3" in d["reason"]


# ── distribution shortfall: KHAAS MASLA (would_give via fill logic) ──────────────

class TestDistributionShortfall:
    def test_distribution_would_give_uses_fill_logic_not_raw(self, client):
        """easy/medium APPLY x1 each, easy/medium UNDERSTAND x3 each.
        dist {easy:3, medium:3}, bloom APPLY → got=2.
        Bloom hatane par asal fill = 3+3 = 6 (distribution cap se). RAW count 8 hota
        — would_give 6 aana chahiye (used_ids/slice hisaab), 8 nahi."""
        _insert_q(difficulty="easy", bloom_level="APPLY")
        _insert_q(difficulty="medium", bloom_level="APPLY")
        for _ in range(3):
            _insert_q(difficulty="easy", bloom_level="UNDERSTAND")
        for _ in range(3):
            _insert_q(difficulty="medium", bloom_level="UNDERSTAND")
        res = _post(client, [_section(
            count=6,
            bloom_filter="APPLY",
            difficulty_distribution={"easy": 3, "medium": 3},
        )])
        assert res.status_code == 200
        body = res.json()
        assert len(body["questions"]) == 2  # got

        d = body["shortfall_details"][0]
        assert d["got"] == 2
        assert d["wanted"] == 6
        # reason: bloom ki apni ginti (solo=2 APPLY) sab se kam — solo raw hai (no dist)
        assert "Bloom" in d["reason"] and "APPLY" in d["reason"] and "2" in d["reason"]
        bloom_opt = next(o for o in d["options"] if o["filter"] == "bloom_level")
        assert bloom_opt["would_give"] == 6  # NOT 8 (raw) — fill logic
        assert d["options"][-1]["filter"] is None
        assert d["options"][-1]["would_give"] == 2


# ── REASON rule: min solo_count (options rule: max would_give) — divergence ──────

class TestReasonMinSoloRule:
    def test_reason_from_min_solo_not_max_would_give(self, client):
        """3 shartein aisi ke reason (min solo) aur option[0] (max would_give)
        ALAG filter par aayen — nayi rule ki asal jaanch.

        Cells (bloom, topic, type):  A=APPLY U=UNDERSTAND  E=essay M=multiple-choice
          A,T1,E=2 (got)  A,T1,M=6  A,T2,E=1  U,T1,E=3  U,T2,E=10  U,T2,M=10
        solo:      bloom=9(min)  topic=11  type=16
        would_give: type=8(max)  bloom=5   topic=3
        → reason = BLOOM (solo 9); option[0] = QUESTION_TYPES (would_give 8).
        """
        def q(topic, bloom, qtype, n):
            for _ in range(n):
                _insert_q(subject="DivTest", topic_id=topic, bloom_level=bloom, qtype=qtype)
        q("dt-t1", "APPLY", "essay", 2)          # got
        q("dt-t1", "APPLY", "multiple-choice", 6)
        q("dt-t2", "APPLY", "essay", 1)
        q("dt-t1", "UNDERSTAND", "essay", 3)
        q("dt-t2", "UNDERSTAND", "essay", 10)
        q("dt-t2", "UNDERSTAND", "multiple-choice", 10)

        sec = _section(
            count=20,
            question_types=["essay"],
            topic_ids=["dt-t1"],
            bloom_filter="APPLY",
            source_filter="all",
        )
        res = _post(client, [sec], subject="DivTest")
        assert res.status_code == 200
        d = res.json()["shortfall_details"][0]
        assert d["got"] == 2

        # REASON: bloom (solo 9) — got (2) ya would_give se nahi
        assert "Bloom" in d["reason"] and "APPLY" in d["reason"] and "9" in d["reason"]

        opts = d["options"]
        assert len(opts) == 3
        # OPTIONS: would_give desc — pehla question_types (8), phir bloom (5)
        assert opts[0]["filter"] == "question_types" and opts[0]["would_give"] == 8
        assert opts[1]["filter"] == "bloom_level" and opts[1]["would_give"] == 5
        assert opts[2]["filter"] is None and opts[2]["would_give"] == 2
        # reason-filter (bloom) != top-option-filter (question_types)
        assert opts[0]["filter"] != "bloom_level"


# ── sections_meta persistence: reason+options print.html ke liye store hon ──────

class TestSectionsMetaPersistence:
    def test_short_section_meta_carries_reason_and_options(self, client):
        """Short section ki sections_meta mein reason + options ho (print.html
        wahin se panel banata hai — shortfall_details insert ke baad discard hoti)."""
        for _ in range(8):
            _insert_q(bloom_level="APPLY")
        for _ in range(16):
            _insert_q(bloom_level="UNDERSTAND")
        res = _post(client, [_section(heading="Section A", count=20, bloom_filter="APPLY")])
        assert res.status_code == 200
        meta = res.json()["sections_meta"][0]
        assert meta["shortfall"] == 12
        assert "Bloom" in meta["shortfall_reason"] and "APPLY" in meta["shortfall_reason"]
        bloom_opt = next(o for o in meta["shortfall_options"] if o["filter"] == "bloom_level")
        assert bloom_opt["would_give"] == 24
        assert meta["shortfall_options"][-1]["filter"] is None

    def test_full_section_meta_has_no_shortfall_keys(self, client):
        """Poore section ki meta mein reason/options keys bilkul na hon."""
        for _ in range(5):
            _insert_q()
        res = _post(client, [_section(count=3)])
        assert res.status_code == 200
        meta = res.json()["sections_meta"][0]
        assert meta["shortfall"] == 0
        assert "shortfall_reason" not in meta
        assert "shortfall_options" not in meta


# ── multi-section: har shortfall section apna detail ────────────────────────────

class TestMultiSection:
    def test_one_detail_per_short_section_only(self, client):
        """Do sections: ek poora, ek short → sirf short wale ka detail."""
        for _ in range(10):
            _insert_q(bloom_level="UNDERSTAND")
        for _ in range(3):
            _insert_q(bloom_level="APPLY")
        full = _section(heading="Full", count=3)          # 3 of 10 UNDERSTAND
        short = _section(heading="Short", count=20, bloom_filter="APPLY")  # 3 of 3
        res = _post(client, [full, short])
        assert res.status_code == 200
        details = res.json()["shortfall_details"]
        assert len(details) == 1
        assert details[0]["heading"] == "Short"
