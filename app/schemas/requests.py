"""Pydantic request shapes used by the API layer."""

from typing import List, Literal, Optional

from pydantic import BaseModel, Field, field_validator, model_validator


class GenerateQuestionsRequest(BaseModel):
    subject: str = ""
    topic: str = ""
    syllabus_topic_id: Optional[str] = None
    total_questions: int = 10
    bloom_distribution: str = "balanced"  # balanced | foundational | advanced
    question_types: List[str] = ["multiple-choice"]
    difficulty: str = "medium"
    learning_outcome: Optional[str] = None


#: Har wo question type jo app mein waqai mojood hai. paper_service.py ke
#: _PAPER_TYPE_FILTERS / _RATIO_* groups isi set se bante hain.
#: NOTE: ManualQuestionRequest ka apna Literal is se CHHOTA hai — us mein "essay"
#: nahi hai, yani teacher haath se essay nahi likh sakta jabke baqi app use poori
#: tarah support karti hai. Wo alag masla hai, yahan theek nahi kiya ja raha.
QuestionType = Literal[
    "multiple-choice",
    "true-false",
    "short-answer",
    "fill-blank",
    "essay",
]


class SectionTypeCount(BaseModel):
    """Ek qism aur us ki theek ginti — "3 MCQ", "4 short-answer"."""

    question_type: QuestionType
    count: int = Field(ge=1)


class PaperSectionSpec(BaseModel):
    """Ek section: uska heading, kaunsi qism ke sawal, aur kitne.

    Sawal QISM se section mein jaate hain (Irfan ka faisla, 2026-08-20) — yani
    do sections ek hi qism nahi le sakte, aur yeh us hardcoded do-hisse wale
    split ka seedha barha hua roop hai jo print.html abhi karta hai.

    DO SOORATEIN, aur EK HI dena hai:

      question_types + count   "7 sawal, MCQ ya short-answer mein se"
      type_counts              "theek 3 MCQ aur 4 short-answer"

    Doosri soorat Ratio Phase 2 hai (PRD R5). Pehli soorat ek se zyada qismein
    de kar bhi ANDAR ka mix tay nahi kar sakti — repository ka SQL
    `WHERE question_type IN (...) ORDER BY usage_count ASC LIMIT n` hai, yani
    mix usage counts par chhora hua hai. `type_counts` wahi khala bharta hai.

    `type_counts` LIST hai, dict nahi, kyunke TARTEEB ma'ni rakhti hai: sawal
    kaghaz par isi tarteeb mein chhapte hain, to teacher tay karta hai ke pehle
    MCQ aayen ya short-answer.
    """

    heading: str = Field(min_length=1, max_length=120)
    question_types: Optional[List[QuestionType]] = None
    count: Optional[int] = Field(default=None, ge=1)
    type_counts: Optional[List[SectionTypeCount]] = Field(default=None, min_length=1)

    @model_validator(mode="after")
    def _one_shape_only(self) -> "PaperSectionSpec":
        simple = self.question_types is not None or self.count is not None
        if simple and self.type_counts:
            raise ValueError(
                "section mein ya to question_types+count dein ya type_counts — dono nahi"
            )
        if self.type_counts:
            seen = [tc.question_type for tc in self.type_counts]
            if len(set(seen)) != len(seen):
                # Ek hi qism do dafa: kaun si ginti sahi hai, is ka jawab nahi.
                raise ValueError("type_counts mein ek qism do dafa nahi aa sakti")
            return self
        if not self.question_types or self.count is None:
            raise ValueError("section ko question_types+count chahiye, ya type_counts")
        return self

    @property
    def wanted(self) -> int:
        """Is section se kitne sawal maange gaye — dono shaklon ke liye ek jawab."""
        if self.type_counts:
            return sum(tc.count for tc in self.type_counts)
        return self.count or 0

    @field_validator("heading")
    @classmethod
    def _strip_heading(cls, v: str) -> str:
        # Kaghaz par chhapta hai — trailing spaces heading ko tirha dikhate hain.
        v = v.strip()
        if not v:
            raise ValueError("heading khaali nahi ho sakta")
        return v

    @field_validator("question_types")
    @classmethod
    def _dedupe_types(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        # None tab aata hai jab section type_counts wali shakl mein hai.
        if v is None:
            return v
        if not v:
            raise ValueError("question_types khaali nahi ho sakti")
        # Ek hi type do dafa dene se pick badalti nahi, sirf meta ganda hota hai.
        seen: list[str] = []
        for t in v:
            if t not in seen:
                seen.append(t)
        return seen


class GeneratePaperRequest(BaseModel):
    subject: str
    class_name: Optional[str] = None
    # grade = syllabus class string (e.g. "Grade 4", "Pre Year 1") — questions isi
    # se filter hote hain, `syllabus_topics.grade` par JOIN kar ke. class_name
    # free-text hai aur sirf paper ke title/row mein jata hai, filter ke liye
    # bharosay ke laiq nahi — wahi taqseem jo BlueprintPaperRequest pehle se
    # karti hai.
    #
    # None = koi grade filter nahi (purana behaviour). Ye OPT-IN isi liye hai ke
    # jin questions ka syllabus_topic_id NULL hai wo grade dene par bahar ho jate
    # hain (2026-08-21: English ke saare 130 sawal aise hi hain).
    grade: Optional[str] = None
    total_questions: int = 10
    bloom_distribution: str = "balanced"
    difficulty: Optional[str] = None
    paper_type: str = "mixed"  # mcq | mixed | subjective | custom-ratio
    # Sirf paper_type == "custom-ratio" par relevant. MCQ group ka %; subjective
    # group = 100 - mcq_percent. Range Pydantic level par enforce (0-100).
    mcq_percent: Optional[int] = Field(default=None, ge=0, le=100)
    paper_title: Optional[str] = None
    language_filter: Optional[Literal["en", "ur"]] = None
    # Paper kis exam se tag ho (coverage ke liye). None = Unassigned. UI dropdown
    # bhejta hai (Marhala 6). ge=0 — 0 bhi Unassigned; upar N ki hadd taqseem/global.
    exam_no: Optional[int] = Field(default=None, ge=0)
    # Sections mode. None ya khaali = purana behaviour bilkul waisa ka waisa
    # (sections_meta NULL, aur print.html apne hardcoded A/B split par girta hai).
    # Diya jaye to har section apni qism ke sawal khud uthata hai aur sections_meta
    # paper row mein likha jata hai, jise print.html pehle se render karta hai.
    #
    # sections ke saath total_questions/paper_type NAZAR-ANDAZ hote hain — ginti
    # sections se aati hai. Neeche wala validator custom-ratio ke saath saaf mana
    # karta hai, bajaye khamoshi se ek ko doosre par tarjeeh dene ke.
    sections: Optional[List[PaperSectionSpec]] = None

    @model_validator(mode="after")
    def _sections_rules(self) -> "GeneratePaperRequest":
        if self.sections:
            if self.paper_type == "custom-ratio":
                raise ValueError(
                    "sections aur custom-ratio ek saath nahi — dono ginti tay karte hain. "
                    "Sections chahiyen to paper_type custom-ratio mat bhejein."
                )
            headings = [s.heading.casefold() for s in self.sections]
            if len(set(headings)) != len(headings):
                # Do sections ka ek naam kaghaz par teacher ko dhoka deta hai.
                raise ValueError("do sections ka heading ek jaisa nahi ho sakta")
        return self


class AdaptivePaperRequest(BaseModel):
    """Phase 3: build a paper weighted toward a class's weak Bloom levels,
    learned from source_paper_id's latest results upload. Subject is taken from
    the source paper, so it can't drift from the weakness signal."""

    source_paper_id: str
    class_name: Optional[str] = None
    total_questions: int = 10
    difficulty: Optional[str] = None
    # Paper kis exam se tag ho (coverage). None = Unassigned.
    exam_no: Optional[int] = Field(default=None, ge=0)
    # Weakness signal (Bloom) aur format choice (type) alag cheezein hain — teacher
    # adaptive follow-up ka format chun sake. custom-ratio jaan-boojh kar allowed
    # nahi: weakness-distribution × ratio-split ka combo abhi scope se bahar hai.
    paper_type: str = "mixed"  # mcq | mixed | subjective

    @field_validator("paper_type")
    @classmethod
    def _reject_ratio_for_adaptive(cls, v: str) -> str:
        allowed = {"mcq", "mixed", "subjective"}
        if v not in allowed:
            raise ValueError(
                "Adaptive paper ke liye paper_type sirf mcq, mixed, ya subjective ho sakta hai "
                "(custom-ratio adaptive mein support nahi)."
            )
        return v


class ReplaceQuestionRequest(BaseModel):
    """Manual question swap in a built paper — replace old_question_id with
    new_question_id (both must already exist in the bank/paper)."""

    old_question_id: str
    new_question_id: str


class UpdateQuestionRequest(BaseModel):
    """PATCH /api/questions/{id} — saare fields optional, jo diya jaye wahi update ho."""

    question_en: Optional[str] = None
    question_ur: Optional[str] = None
    options_en: Optional[str] = None  # JSON-encoded list, e.g. '["a","b","c","d"]'
    options_ur: Optional[str] = None
    correct_answer_en: Optional[str] = None
    correct_answer_ur: Optional[str] = None
    marks: Optional[int] = Field(default=None, ge=1)
    answer_lines: Optional[int] = Field(default=None, ge=0, le=20)
    image_size: Optional[str] = None
    learning_outcome: Optional[str] = None
    estimated_time: Optional[int] = Field(default=None, ge=1)
    keywords: Optional[str] = None
    source_book: Optional[str] = None
    page_number: Optional[int] = Field(default=None, ge=1)
    status: Optional[Literal["published", "draft", "archived"]] = None

    @field_validator("image_size")
    @classmethod
    def _valid_image_size(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in ("small", "medium", "large"):
            raise ValueError("image_size sirf 'small', 'medium', ya 'large' ho sakta hai.")
        return v

    @field_validator("question_en", "question_ur")
    @classmethod
    def _not_blank(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError("Sawal khali nahi ho sakta.")
        return v

    @field_validator("options_en", "options_ur")
    @classmethod
    def _valid_json_list(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        try:
            parsed = __import__("json").loads(v)
        except Exception as exc:
            raise ValueError("options valid JSON list honi chahiye.") from exc
        if not isinstance(parsed, list):
            raise ValueError("options JSON array hona chahiye.")
        return v

    @model_validator(mode="after")
    def _at_least_one_field(self) -> "UpdateQuestionRequest":
        if all(
            v is None
            for v in (
                self.question_en,
                self.question_ur,
                self.options_en,
                self.options_ur,
                self.correct_answer_en,
                self.correct_answer_ur,
                self.marks,
                self.answer_lines,
                self.image_size,
                self.learning_outcome,
                self.estimated_time,
                self.keywords,
                self.source_book,
                self.page_number,
                self.status,
            )
        ):
            raise ValueError("Kam az kam ek field dena zaroori hai.")
        return self


class BulkUpdateTopicRequest(BaseModel):
    """PATCH /api/library/bulk-topic — kai images ka topic ek saath badlo."""

    image_ids: List[str]
    syllabus_topic_id: Optional[str] = None  # None = sab unlink

    @field_validator("image_ids")
    @classmethod
    def _non_empty_ids(cls, v: List[str]) -> List[str]:
        if not v:
            raise ValueError("image_ids khaali nahi ho sakti.")
        return v


_BULK_META_FIELDS = {"keywords", "category", "question_types"}


class BulkUpdateMetaRequest(BaseModel):
    """PATCH /api/library/bulk-meta — kai images ke smart tags ek saath badlo."""

    image_ids: List[str]
    keywords: Optional[str] = None
    category: Optional[str] = None
    question_types: Optional[str] = None
    keywords_mode: Literal["append", "replace"] = "replace"

    @field_validator("image_ids")
    @classmethod
    def _non_empty_ids(cls, v: List[str]) -> List[str]:
        if not v:
            raise ValueError("image_ids khaali nahi ho sakti.")
        return v

    @model_validator(mode="after")
    def _at_least_one_meta(self) -> "BulkUpdateMetaRequest":
        if not (self.model_fields_set & _BULK_META_FIELDS):
            raise ValueError(
                "Kam az kam ek field (keywords, category, ya question_types) dena zaroori hai."
            )
        return self


_BULK_Q_META_FIELDS = {
    "keywords",
    "source_book",
    "page_number",
    "status",
    "learning_outcome",
    "estimated_time",
}


class BulkUpdateQuestionMetaRequest(BaseModel):
    """PATCH /api/questions/bulk-meta — kai questions ke smart fields ek saath badlo."""

    question_ids: List[str]
    keywords: Optional[str] = None
    source_book: Optional[str] = None
    page_number: Optional[int] = Field(default=None, ge=1)
    status: Optional[Literal["published", "draft", "archived"]] = None
    learning_outcome: Optional[str] = None
    estimated_time: Optional[int] = Field(default=None, ge=1)
    keywords_mode: Literal["append", "replace"] = "replace"

    @field_validator("question_ids")
    @classmethod
    def _non_empty_ids(cls, v: List[str]) -> List[str]:
        if not v:
            raise ValueError("question_ids khaali nahi ho sakti.")
        return v

    @model_validator(mode="after")
    def _at_least_one_meta(self) -> "BulkUpdateQuestionMetaRequest":
        if not (self.model_fields_set & _BULK_Q_META_FIELDS):
            raise ValueError("Kam az kam ek field dena zaroori hai.")
        return self


_SMART_FIELDS = {
    "name",
    "syllabus_topic_id",
    "keywords",
    "question_types",
    "category",
    "source_book",
    "page_number",
}


class UpdateLibraryImageRequest(BaseModel):
    """PATCH /api/library/{id} — image ka naam, topic, ya smart fields (ya koi bhi) badlo."""

    name: Optional[str] = None
    syllabus_topic_id: Optional[str] = None  # None = topic unlink; absent = koi tabdeeli nahi
    keywords: Optional[str] = None
    question_types: Optional[str] = None
    category: Optional[str] = None
    source_book: Optional[str] = None
    page_number: Optional[int] = None

    @field_validator("name")
    @classmethod
    def _name_not_blank(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError("Naam khaali nahi ho sakta.")
        return v

    @model_validator(mode="after")
    def _at_least_one(self) -> "UpdateLibraryImageRequest":
        if not (self.model_fields_set & _SMART_FIELDS):
            raise ValueError("Kam az kam ek field dena zaroori hai.")
        return self


class CopyFromLibraryRequest(BaseModel):
    """POST /api/questions/{id}/image-from-library — library image ko question par apply karo."""

    image_id: str
    image_size: Optional[str] = "medium"

    @field_validator("image_size")
    @classmethod
    def _valid_image_size(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in ("small", "medium", "large"):
            raise ValueError("image_size sirf 'small', 'medium', ya 'large' ho sakta hai.")
        return v


class BankPaperRequest(BaseModel):
    """POST /api/bank-paper — teacher ke manual questions se paper banao, bina Gemini.
    syllabus_topic_id diya jaye to sirf us topic ke questions; warna subject ke sab."""

    subject: Optional[str] = None
    syllabus_topic_id: Optional[str] = None
    question_types: Optional[List[str]] = None
    total_questions: Optional[int] = Field(default=None, ge=1)
    class_name: Optional[str] = None
    # grade = syllabus class string; questions isi se filter hote hain. class_name
    # yahan free-text input hai (bank.html:305 ka placeholder hi "Class 7A" hai),
    # to filter ke liye wo istemal nahi ho sakta — wahi taqseem jo
    # GeneratePaperRequest aur BlueprintPaperRequest karti hain.
    #
    # None = koi grade filter nahi (purana behaviour). syllabus_topic_id is se
    # zyada baareek hai; dono bheje ja sakte hain.
    grade: Optional[str] = None
    paper_title: Optional[str] = None
    # Paper kis exam se tag ho (coverage). None = Unassigned.
    exam_no: Optional[int] = Field(default=None, ge=0)
    # 'manual' = sirf teacher-written (bina Gemini); 'all' = manual + gemini dono
    source_filter: str = "manual"

    @field_validator("source_filter")
    @classmethod
    def _valid_source(cls, v: str) -> str:
        if v not in ("manual", "all"):
            raise ValueError("source_filter sirf 'manual' ya 'all' ho sakta hai.")
        return v

    @model_validator(mode="after")
    def _subject_or_topic(self) -> "BankPaperRequest":
        if not self.subject and not self.syllabus_topic_id:
            raise ValueError("subject ya syllabus_topic_id mein se ek zaroori hai.")
        return self


class ManualQuestionRequest(BaseModel):
    """POST /api/bank/questions — teacher khud question likhta hai."""

    question_text: str
    is_urdu: bool = False  # True → question_ur field mein save, False → question_en
    question_type: Literal["multiple-choice", "fill-blank", "true-false", "short-answer"]
    options: Optional[List[str]] = None  # sirf MCQ ke liye, 2-4 items
    correct_answer: Optional[str] = None
    marks: int = Field(default=1, ge=1)
    difficulty: str = "medium"
    bloom_level: str = "REMEMBER"
    syllabus_topic_id: Optional[str] = None
    subject: Optional[str] = None
    topic: Optional[str] = None
    answer_lines: Optional[int] = Field(default=None, ge=0, le=20)
    learning_outcome: Optional[str] = None
    estimated_time: Optional[int] = Field(default=None, ge=1)
    keywords: Optional[str] = None
    source_book: Optional[str] = None
    page_number: Optional[int] = Field(default=None, ge=1)
    status: Literal["published", "draft", "archived"] = "published"
    slo_ids: Optional[List[str]] = None  # optional — kai SLO se link (khali/None = koi link nahi)

    @model_validator(mode="after")
    def _validate(self) -> "ManualQuestionRequest":
        if not self.question_text.strip():
            raise ValueError("Question khali nahi ho sakta.")
        if self.question_type == "multiple-choice":
            if not self.options or len(self.options) < 2:
                raise ValueError("MCQ ke liye kam az kam 2 options zaroori hain.")
            if len(self.options) > 4:
                raise ValueError("MCQ mein zyada se zyada 4 options ho sakte hain.")
            if self.correct_answer and self.correct_answer not in self.options:
                raise ValueError("correct_answer options mein se hona chahiye.")
        if not self.syllabus_topic_id and not (self.subject and self.topic):
            raise ValueError("syllabus_topic_id ya phir subject aur topic dono dene zaroori hain.")
        return self


class ManualQuestionUpdateRequest(BaseModel):
    """PATCH /api/bank/questions/{id} — sirf manual questions ke liye."""

    question_text: Optional[str] = None
    is_urdu: Optional[bool] = None  # explicitly dena zaroori nahi — existing row se infer hoga
    options: Optional[List[str]] = None
    correct_answer: Optional[str] = None
    marks: Optional[int] = Field(default=None, ge=1)
    answer_lines: Optional[int] = Field(default=None, ge=0, le=20)
    learning_outcome: Optional[str] = None
    estimated_time: Optional[int] = Field(default=None, ge=1)
    keywords: Optional[str] = None
    source_book: Optional[str] = None
    page_number: Optional[int] = Field(default=None, ge=1)
    status: Optional[Literal["published", "draft", "archived"]] = None
    slo_ids: Optional[List[str]] = None  # diya jaye to replace-set; None = link chheda na jaye

    @field_validator("options")
    @classmethod
    def _validate_options(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        if v is not None and (len(v) < 2 or len(v) > 4):
            raise ValueError("Options 2 se 4 ke beech hone chahiye.")
        return v

    @model_validator(mode="after")
    def _at_least_one(self) -> "ManualQuestionUpdateRequest":
        if all(
            v is None
            for v in (
                self.question_text,
                self.is_urdu,
                self.options,
                self.correct_answer,
                self.marks,
                self.answer_lines,
                self.learning_outcome,
                self.estimated_time,
                self.keywords,
                self.source_book,
                self.page_number,
                self.status,
                self.slo_ids,
            )
        ):
            raise ValueError("Kam az kam ek field dena zaroori hai.")
        return self


class SetQuestionSloRequest(BaseModel):
    """PUT /api/questions/{id}/slo — is question ke SLO links poori tarah set (replace).
    Khali list = saare link hata do. Kisi bhi source (manual/gemini) par chalta hai."""

    slo_ids: List[str] = []


_VALID_DIFFICULTIES = {"easy", "medium", "hard"}
_VALID_BLOOM_LEVELS = {
    "REMEMBER",
    "UNDERSTAND",
    "APPLY",
    "ANALYZE",
    "EVALUATE",
    "CREATE",
}


class BlueprintSection(BaseModel):
    """One section in a blueprint — e.g. 'Section A — MCQ'."""

    heading: str
    question_types: List[str]
    topic_ids: List[str] = []
    count: int = Field(ge=1)
    marks_each: int = Field(default=1, ge=1)
    source_filter: str = "manual"
    # Hissa 4-C: teacher ke KHUD pin kiye question_ids (must-include). Filter-natije se
    # pehle guarantee hote (dedup); agar count se zyada to count inhi tak barh jaata.
    # Khali = koi pin nahi (purana rawaiyya). Teacher pin karta — app khud nahi.
    include_question_ids: List[str] = []

    # --- New filter fields (all optional; absent = no filter / safe default) ---
    status_filter: Literal["published", "draft", "archived", "all"] = "published"
    difficulty_filter: Optional[Literal["easy", "medium", "hard"]] = None
    bloom_filter: Optional[str] = None
    # difficulty_distribution: {"easy": 3, "medium": 5, "hard": 2}
    # Sum must be ≤ count. Mutually exclusive with difficulty_filter.
    difficulty_distribution: Optional[dict] = None
    language_filter: Optional[Literal["en", "ur"]] = None

    @field_validator("question_types")
    @classmethod
    def _non_empty_types(cls, v: List[str]) -> List[str]:
        if not v:
            raise ValueError("question_types khaali nahi ho sakti.")
        return v

    @field_validator("source_filter")
    @classmethod
    def _valid_source(cls, v: str) -> str:
        if v not in ("manual", "all"):
            raise ValueError("source_filter sirf 'manual' ya 'all' ho sakta hai.")
        return v

    @field_validator("bloom_filter")
    @classmethod
    def _valid_bloom(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v.upper() not in _VALID_BLOOM_LEVELS:
            raise ValueError(
                f"bloom_filter sirf {sorted(_VALID_BLOOM_LEVELS)} mein se ek ho sakta hai."
            )
        return v.upper() if v else v

    @field_validator("difficulty_distribution")
    @classmethod
    def _valid_distribution(cls, v: Optional[dict]) -> Optional[dict]:
        if v is None:
            return v
        for key, val in v.items():
            if key not in _VALID_DIFFICULTIES:
                raise ValueError(
                    f"difficulty_distribution key '{key}' galat hai — sirf easy/medium/hard."
                )
            if not isinstance(val, int) or val < 0:
                raise ValueError(
                    f"difficulty_distribution['{key}'] ek non-negative integer hona chahiye."
                )
        return v

    @model_validator(mode="after")
    def _distribution_vs_filter(self) -> "BlueprintSection":
        if self.difficulty_filter is not None and self.difficulty_distribution is not None:
            raise ValueError(
                "difficulty_filter aur difficulty_distribution dono ek saath nahi diye ja sakte."
            )
        if self.difficulty_distribution is not None:
            total = sum(self.difficulty_distribution.values())
            if total > self.count:
                raise ValueError(
                    f"difficulty_distribution ka sum ({total}) section count ({self.count}) se zyada hai."
                )
        return self


class SaveBlueprintRequest(BaseModel):
    """POST /api/blueprints — blueprint save karo."""

    name: str
    subject: Optional[str] = None
    grade: Optional[str] = None
    sections: List[BlueprintSection]

    @field_validator("name")
    @classmethod
    def _non_empty_name(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Blueprint name khaali nahi ho sakta.")
        return v.strip()

    @field_validator("sections")
    @classmethod
    def _non_empty_sections(cls, v: List[BlueprintSection]) -> List[BlueprintSection]:
        if not v:
            raise ValueError("Blueprint mein kam az kam ek section hona chahiye.")
        return v


class BlueprintPaperRequest(BaseModel):
    """POST /api/blueprint-paper — blueprint se paper banao.
    blueprint_id diya jaye to saved blueprint use hoga;
    warna inline sections_input se paper bane ga (builder preview ke liye)."""

    blueprint_id: Optional[str] = None
    sections_input: Optional[List[BlueprintSection]] = None
    subject: Optional[str] = None
    class_name: Optional[str] = None
    # grade = syllabus class string (e.g. "Class 8") — Bloom-standard tier isse map hota
    # hai. class_name free-text hota hai (e.g. "Class 8A"), tier ke liye reliable nahi.
    grade: Optional[str] = None
    paper_title: Optional[str] = None
    # Paper kis exam se tag ho (coverage ke liye). None = Unassigned. UI dropdown
    # bhejta hai (Marhala 6). ge=0 — 0 bhi Unassigned; upar N ki hadd taqseem/global.
    exam_no: Optional[int] = Field(default=None, ge=0)

    @model_validator(mode="after")
    def _blueprint_or_sections(self) -> "BlueprintPaperRequest":
        if not self.blueprint_id and not self.sections_input:
            raise ValueError("blueprint_id ya sections_input mein se ek zaroori hai.")
        return self


class SchoolSettings(BaseModel):
    """Used for both the POST body and the GET response (singleton id=1)."""

    id: Optional[int] = None
    school_name: str = ""
    school_name_ur: str = ""
    address: str = ""
    address_ur: str = ""
    logo_base64: Optional[str] = None
    accent_color: str = "#0e4d3c"
    # School identity — phone/email letterhead par, principal_name sirf record.
    phone: str = ""
    email: str = ""
    principal_name: str = ""
    # Academic session — session_start_month 1-12 (default March=3), exam_count N
    # (default 8; taqseem se wiring Hissa 2 mein).
    session_start_month: int = 3
    exam_count: int = 8
    class_size: int = 25
    min_analysis_percent: int = 60
    weak_topic_threshold: int = 60
    # Marhala 4A — global print defaults (per-class na ho to yehi lagte hain).
    print_font_size: int = 14
    print_q_gap: int = 14
    print_page_margin: int = 14


class TaqseemGenerateRequest(BaseModel):
    """POST /api/taqseem/generate — ek (class, subject) ka auto exam plan banao.
    N (exam count) global hai (school_settings.exam_count), is liye body mein nahi
    aata. class_name/subject blank par route 400 deta hai (GET /api/taqseem jaisa)."""

    class_name: str
    subject: str


class TaqseemMoveRequest(BaseModel):
    """POST /api/taqseem/move — ek SLO ka assignment badlo (drag/drop).
    exam_no 0 = Unassigned. Range (0..N) check route/service karta hai (N global).
    position optional (exam ke andar tarteeb)."""

    slo_id: str
    exam_no: int
    position: Optional[int] = None


class ClassPrintSettingsSave(BaseModel):
    """POST /api/print-settings — ek class ke print knobs mehfooz karna (Marhala 4B).
    Bounds UI ki hadd ka mirror hain: out-of-range value 422 de deti hai, DB tak
    nahi pahunchti. class_name blank ho to route 400 (per-class ke liye laazmi)."""

    class_name: str
    font_size: int = Field(ge=11, le=20)
    q_gap: int = Field(ge=6, le=30)
    page_margin: int = Field(ge=10, le=25)
