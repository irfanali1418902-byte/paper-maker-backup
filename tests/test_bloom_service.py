"""Unit tests for bloom_service — pure functions, no DB needed.

The rounding-overflow case is the historically important one: `ceil` on
each bucket can push the sum above `total_questions`. The trim loop must
bring it back. We sweep small totals exhaustively because that's where the
bug originally surfaced.
"""

import pytest

from app.services.bloom_service import calculate_bloom_distribution, calculate_marks

# ---- calculate_bloom_distribution -------------------------------------------


class TestCalculateBloomDistribution:

    def test_balanced_distribution_sum_equals_total(self):
        dist = calculate_bloom_distribution("balanced", 10)
        assert sum(dist.values()) == 10

    def test_all_six_bloom_levels_present(self):
        """All six keys must always exist, even when count is 0 — callers
        iterate `dist.items()` and expect every level."""
        dist = calculate_bloom_distribution("balanced", 10)
        assert set(dist.keys()) == {
            "REMEMBER",
            "UNDERSTAND",
            "APPLY",
            "ANALYZE",
            "EVALUATE",
            "CREATE",
        }

    def test_balanced_total_one_handles_rounding_overflow(self):
        """The classic bug: for total=1, ceil on each of 6 buckets yielded
        1*6=6. The trim loop must reduce it back to 1."""
        dist = calculate_bloom_distribution("balanced", 1)
        assert sum(dist.values()) == 1

    def test_balanced_small_totals_never_overflow(self):
        """Sweep small N exhaustively — overflow only surfaces at low counts."""
        for n in range(0, 25):
            dist = calculate_bloom_distribution("balanced", n)
            assert sum(dist.values()) == n, f"overflow at n={n}: got {dist}"

    def test_foundational_keeps_evaluate_and_create_at_zero(self):
        """Foundational is for young learners — EVALUATE/CREATE never asked."""
        dist = calculate_bloom_distribution("foundational", 30)
        assert dist["EVALUATE"] == 0
        assert dist["CREATE"] == 0

    # ---- WHICH level got the questions, not just how many --------------------
    #
    # Har upar wala test sirf JORH dekhta hai, aur isi khali jagah mein ek bug
    # barson chhupa raha: trim loop `max(result, key=result.get)` istemal karta
    # tha, jo barabar qeematon mein PEHLI key deti hai, aur dict REMEMBER se
    # shuru hota hai. Chhoti ginti par har level `ceil` se 1 hota hai, to katai
    # hamesha neeche wale levels kha jaati thi. Naapa gaya 2026-08-21, fix se
    # pehle: balanced/3 = ANALYZE 1, EVALUATE 1, CREATE 1 — yani ek chhote
    # paper mein sirf sab se mushkil sawal. Jorh phir bhi 3 tha, isliye poora
    # suite hara rehta tha.

    @pytest.mark.parametrize("n", [1, 2, 3, 4, 5])
    def test_small_balanced_papers_start_from_the_bottom(self, n):
        """Chhota balanced paper foundational levels se bharta hai, CREATE se
        nahi. Ek bacche ko teen CREATE-level sawal dena "balanced" nahi hai."""
        dist = calculate_bloom_distribution("balanced", n)
        assert dist["REMEMBER"] >= 1
        assert dist["CREATE"] == 0

    def test_balanced_never_leaves_the_low_levels_empty_while_high_ones_fill(self):
        """Koi bhi n par: agar kisi ooncha level ko sawal mila hai to us se
        neeche wale khaali nahi ho sakte."""
        order = ["REMEMBER", "UNDERSTAND", "APPLY", "ANALYZE", "EVALUATE", "CREATE"]
        for n in range(1, 40):
            dist = calculate_bloom_distribution("balanced", n)
            for i, lvl in enumerate(order):
                if dist[lvl] == 0:
                    assert all(dist[higher] == 0 for higher in order[i + 1 :]), (
                        f"n={n}: {lvl} khaali hai magar upar wale bhare hain — {dist}"
                    )

    @pytest.mark.parametrize("n", [3, 5, 10, 30])
    def test_foundational_always_keeps_remember(self, n):
        """REMEMBER foundational ka 40% hai — us ka sab se bara hissa. Purana
        trim `min(surplus, bucket)` se poori bucket ek saath kha jaata tha, aur
        sab se bari bucket wahi hoti thi jis ki distribution ko sab se zyada
        zaroorat hai; foundational/3 REMEMBER ke baghair wapas aata tha."""
        dist = calculate_bloom_distribution("foundational", n)
        assert dist["REMEMBER"] >= 1

    def test_foundational_weights_hold_at_a_round_number(self):
        """10 par hissa saaf naapa ja sakta hai: 40/30/20/10."""
        dist = calculate_bloom_distribution("foundational", 10)
        assert dist == {
            "REMEMBER": 4,
            "UNDERSTAND": 3,
            "APPLY": 2,
            "ANALYZE": 1,
            "EVALUATE": 0,
            "CREATE": 0,
        }

    @pytest.mark.parametrize("dist_type", ["balanced", "foundational", "advanced"])
    def test_sum_holds_for_every_distribution(self, dist_type):
        for n in range(0, 40):
            assert sum(calculate_bloom_distribution(dist_type, n).values()) == n

    def test_foundational_small_totals_never_overflow(self):
        for n in range(0, 25):
            dist = calculate_bloom_distribution("foundational", n)
            assert sum(dist.values()) == n, f"foundational overflow at n={n}: got {dist}"

    def test_advanced_small_totals_never_overflow(self):
        for n in range(0, 25):
            dist = calculate_bloom_distribution("advanced", n)
            assert sum(dist.values()) == n, f"advanced overflow at n={n}: got {dist}"

    def test_unknown_dist_type_falls_back_to_balanced(self):
        """Typo in dist_type shouldn't crash — fallback to balanced."""
        unknown = calculate_bloom_distribution("nonsense-mode", 10)
        balanced = calculate_bloom_distribution("balanced", 10)
        assert unknown == balanced

    def test_zero_total_returns_all_zeros(self):
        dist = calculate_bloom_distribution("balanced", 0)
        assert sum(dist.values()) == 0
        assert all(v == 0 for v in dist.values())

    def test_all_bucket_counts_are_non_negative(self):
        """The trim loop must not produce negative counts at any N or split."""
        for n in range(0, 50):
            for dist_type in ["balanced", "foundational", "advanced"]:
                dist = calculate_bloom_distribution(dist_type, n)
                for level, count in dist.items():
                    assert count >= 0, (
                        f"negative count at n={n}, dist={dist_type}, " f"level={level}: {count}"
                    )

    def test_large_total_balanced_proportions(self):
        """At large N, rounding error is negligible — proportions should be
        close to the documented 20/20/20/15/15/10 split."""
        dist = calculate_bloom_distribution("balanced", 100)
        assert sum(dist.values()) == 100
        # Pre-trim ceil ratios are close to the spec; post-trim values must
        # still sum exactly and stay within a couple of the targets.
        assert 18 <= dist["REMEMBER"] <= 22
        assert 18 <= dist["UNDERSTAND"] <= 22
        assert 8 <= dist["CREATE"] <= 12


# ---- calculate_marks --------------------------------------------------------


class TestCalculateMarks:

    def test_remember_easy_mcq_is_one(self):
        """REMEMBER (1) + multiple-choice (0) + easy (0) = 1."""
        assert calculate_marks("REMEMBER", "multiple-choice", "easy") == 1

    def test_analyze_hard_essay_is_nine(self):
        """ANALYZE (4) + essay (3) + hard (2) = 9."""
        assert calculate_marks("ANALYZE", "essay", "hard") == 9

    def test_create_hard_essay_is_highest(self):
        """CREATE (5) + essay (3) + hard (2) = 10 — highest documented combo."""
        assert calculate_marks("CREATE", "essay", "hard") == 10

    def test_unknown_bloom_level_falls_back_to_default_two(self):
        """Unknown level → base default 2."""
        assert calculate_marks("WHATEVER", "multiple-choice", "easy") == 2

    def test_unknown_question_type_gives_zero_bonus(self):
        assert calculate_marks("REMEMBER", "unknown-type", "easy") == 1

    def test_unknown_difficulty_falls_back_to_default_one(self):
        """Unknown difficulty defaults to bonus 1 (medium-equivalent)."""
        assert calculate_marks("REMEMBER", "multiple-choice", "unknown") == 2

    def test_short_answer_adds_one_mark(self):
        """UNDERSTAND (2) + short-answer (1) + medium (1) = 4."""
        assert calculate_marks("UNDERSTAND", "short-answer", "medium") == 4
