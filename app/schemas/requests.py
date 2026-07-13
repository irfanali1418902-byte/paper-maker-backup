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


class GeneratePaperRequest(BaseModel):
    subject: str
    class_name: Optional[str] = None
    total_questions: int = 10
    bloom_distribution: str = "balanced"
    difficulty: Optional[str] = None
    paper_type: str = "mixed"  # mcq | mixed | subjective | custom-ratio
    # Sirf paper_type == "custom-ratio" par relevant. MCQ group ka %; subjective
    # group = 100 - mcq_percent. Range Pydantic level par enforce (0-100).
    mcq_percent: Optional[int] = Field(default=None, ge=0, le=100)
    paper_title: Optional[str] = None


class AdaptivePaperRequest(BaseModel):
    """Phase 3: build a paper weighted toward a class's weak Bloom levels,
    learned from source_paper_id's latest results upload. Subject is taken from
    the source paper, so it can't drift from the weakness signal."""

    source_paper_id: str
    class_name: Optional[str] = None
    total_questions: int = 10
    difficulty: Optional[str] = None
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
    options_en: Optional[str] = None   # JSON-encoded list, e.g. '["a","b","c","d"]'
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
                self.question_en, self.question_ur,
                self.options_en, self.options_ur,
                self.correct_answer_en, self.correct_answer_ur,
                self.marks, self.answer_lines, self.image_size,
                self.learning_outcome, self.estimated_time, self.keywords,
                self.source_book, self.page_number, self.status,
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
            raise ValueError("Kam az kam ek field (keywords, category, ya question_types) dena zaroori hai.")
        return self


_BULK_Q_META_FIELDS = {"keywords", "source_book", "page_number", "status", "learning_outcome", "estimated_time"}


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


_SMART_FIELDS = {"name", "syllabus_topic_id", "keywords", "question_types", "category", "source_book", "page_number"}


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
    paper_title: Optional[str] = None
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
                self.question_text, self.is_urdu, self.options, self.correct_answer,
                self.marks, self.answer_lines, self.learning_outcome, self.estimated_time,
                self.keywords, self.source_book, self.page_number, self.status,
            )
        ):
            raise ValueError("Kam az kam ek field dena zaroori hai.")
        return self


class BlueprintSection(BaseModel):
    """One section in a blueprint — e.g. 'Section A — MCQ'."""

    heading: str
    question_types: List[str]
    topic_ids: List[str] = []
    count: int = Field(ge=1)
    marks_each: int = Field(default=1, ge=1)
    source_filter: str = "manual"

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
    paper_title: Optional[str] = None

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
