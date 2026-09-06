"""`scripts/seed_bank.py` ka per-grade marks paimana.

KYUN YE TESTS MOJOOD HAIN. AI har sawal ke apne marks tajweez karta hai aur wo kuch
grades ke liye ghalat hote hain. Pre Year 1 par ye TEEN dafa hua (PROGRESS.md 2026-09-04
aur 09-06): aakhri run mein 24 ke 24 sawal 3/4/6/7 marks par aaye jab ke us grade ka har
sawal 1 mark ka hai. Har dafa hal ek `UPDATE ... SET marks = 1` tha jo kisi INSAAN ko
yaad rakhna parta tha -- aur teesri dafa bhi yaad us waqt aayi jab check chalaya gaya.

Ye tests us qaide ko yaad-dasht se nikaal kar gate par le aate hain.

⚠ YE TESTS AI KO NAHI BULATE. `apply_marks_scale` jaan-boojh kar ek khalis function hai
jo dicts par chalta hai, is liye ise bina kharch, bina network ke naapa ja sakta hai --
aur yehi wajah hai ke wo `persist_batch` se pehle alag rakha gaya.
"""

import pytest

from scripts.seed_bank import GRADE_MARKS, apply_marks_scale, resolve_marks_target


def q(marks):
    """Ek AI dict jaisa, sirf utna hi jitna is qaide ko chahiye."""
    return {"question_en": "x", "marks": marks}


class TestResolveMarksTarget:
    @pytest.mark.parametrize("grade", ["Pre Year 1", "Pre Year 2", "Pre Year 3"])
    def test_auto_teenon_pre_year_ek_mark_dete_hain(self, grade):
        """Irfan ka faisla 2026-09-06 (D67): teenon Pre Year grades 1-mark par."""
        assert resolve_marks_target(grade, "auto") == 1

    def test_auto_us_grade_par_None_jis_ka_qaida_nahi(self):
        # Grade 4 school-age hai aur us ka paimana naapa nahi gaya (43 sawal, marks
        # 1..8). None ka matlab "haath mat lagao", 0 ka nahi.
        for grade in ("Grade 4", "Grade 9", "Pre Year 4"):
            assert resolve_marks_target(grade, "auto") is None

    def test_keep_hamesha_None(self):
        assert resolve_marks_target("Pre Year 1", "keep") is None

    def test_adad_override_map_ko_harata_hai(self):
        assert resolve_marks_target("Pre Year 1", "3") == 3
        assert resolve_marks_target("Grade 4", "2") == 2


class TestApplyMarksScale:
    def test_ghalat_marks_theek_hote_hain_aur_ginti_lautti_hai(self):
        qs = [q(3), q(4), q(6), q(7)]
        assert apply_marks_scale(qs, 1) == 4
        assert [x["marks"] for x in qs] == [1, 1, 1, 1]

    def test_jo_pehle_se_theek_hain_wo_ginti_mein_nahi_aate(self):
        qs = [q(1), q(5), q(1)]
        assert apply_marks_scale(qs, 1) == 1
        assert [x["marks"] for x in qs] == [1, 1, 1]

    def test_target_None_kuch_nahi_chhoota(self):
        """Ye sab se ahem test hai: jis grade ka qaida naapa nahi gaya, us ke sawal
        waise hi rehne chahiyen. Warna ye script PY2/PY3 ke 696 sawal chup-chaap
        badal degi. D67 par ye faisla ho chuka (teenon PY 1-mark), magar Grade 4 ab
        bhi bahar hai -- aur us par yehi hifazat lagti hai."""
        qs = [q(3), q(4), q(6)]
        assert resolve_marks_target("Grade 4", "auto") is None
        assert apply_marks_scale(qs, None) == 0
        assert [x["marks"] for x in qs] == [3, 4, 6]

    def test_khali_list_par_nahi_girta(self):
        assert apply_marks_scale([], 1) == 0

    def test_marks_ki_ghair_mojoodgi_bhi_theek_hoti_hai(self):
        """AI dict mein `marks` na ho to bhi qaida lagna chahiye -- `.get()` None deta
        hai aur wo target ke barabar kabhi nahi hoga."""
        qs = [{"question_en": "x"}]
        assert apply_marks_scale(qs, 1) == 1
        assert qs[0]["marks"] == 1


class TestGradeMarksMap:
    def test_sirf_naapey_hue_grades_map_mein_hain(self):
        """Map ka apna contract: sirf wo grade jis ka paimana DB se naapa gaya.
        Koi is mein andaze se grade daale to ye test us se sawal karega."""
        assert GRADE_MARKS == {"Pre Year 1": 1, "Pre Year 2": 1, "Pre Year 3": 1}

    @pytest.mark.parametrize("marks", list(GRADE_MARKS.values()))
    def test_har_qadr_musbat_adad_hai(self, marks):
        assert isinstance(marks, int) and marks > 0
