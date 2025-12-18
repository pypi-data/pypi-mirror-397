from enum import Enum
from typing import Any, Mapping, Self

import msgspec

from _typeshed import Incomplete

from svy.core.labels import Label as Label
from svy.core.labels import LabellingCatalog as LabellingCatalog
from svy.core.labels import MissingKind as MissingKind
from svy.core.types import Category as Category

log: Incomplete

class QuestionType(Enum):
    SINGLE = "single"
    MULTI = "multi"
    BOOLEAN = "boolean"
    NUMERIC = "numeric"
    TEXT = "text"
    DATE = "date"

class Op(Enum):
    EQ = "=="
    NE = "!="
    IN = "in"
    NOT_IN = "not_in"
    GT = ">"
    GE = ">="
    LT = "<"
    LE = "<="
    IS_MISSING = "is_missing"
    NOT_MISSING = "not_missing"

class EnableWhen(msgspec.Struct, frozen=True):
    """Minimal, serializable condition for routing/enablement."""

    question_id: str
    op: Op
    value: Category | list[Category] | None = ...

class Choices(msgspec.Struct, frozen=True):
    """
    Choices can come from:
      - inline mapping (mapping=...)
      - a catalog concept (concept=..., locale=...)
    Provide exactly one of (mapping, concept).
    """

    mapping: dict[Category, str] | None = ...
    concept: str | None = ...
    locale: str | None = ...
    title: str | None = ...
    randomize: bool = ...
    allow_other: bool = ...
    def resolve_mapping(self, catalog: LabellingCatalog | None) -> dict[Category, str]: ...

class Question(msgspec.Struct, frozen=True):
    """
    A single question. 'name' is the variable name/column id (stable).
    """

    name: str
    text: str
    qtype: QuestionType
    choices: Choices | None = ...
    required: bool = ...
    min_value: float | None = ...
    max_value: float | None = ...
    min_length: int | None = ...
    max_length: int | None = ...
    enable_when_all: list[EnableWhen] | None = ...
    allow_missing_kinds: set[MissingKind] | None = ...
    def validate(self) -> None: ...
    def is_enabled(self, answers: Mapping[str, Any]) -> bool:
        """Check skip logic against already-collected answers."""
    def resolved_choices(self, catalog: LabellingCatalog | None) -> dict[Category, str]: ...

class Questionnaire(msgspec.Struct):
    """
    Minimal questionnaire container.
    - Store metadata
    - Hold questions (ordered)
    - Provide resolution/validation helpers
    """

    title: str
    locale: str | None = ...
    version: str | None = ...
    questions: list[Question] = msgspec.field(default_factory=list)
    def add(self, *qs: Question) -> Self: ...
    def add_question(self, **kwargs: Any) -> Self:
        """
        Build-and-append from kwargs:
        Questionnaire().add_question(
            name="consent",
            text="Do you agree to participate?",
            qtype=QuestionType.SINGLE,
            choices=Choices(concept="yes_no"),
            required=True,
        )
        """
    def add_questions(self, *items: dict[str, Any]) -> Self:
        """Batch add from kwargs dicts."""
    def find(self, name: str) -> Question: ...
    def validate(self) -> None: ...
    def choice_map(self, name: str, catalog: LabellingCatalog | None) -> dict[Category, str]: ...
    def to_codebook(self, catalog: LabellingCatalog | None) -> list[dict[str, Any]]:
        """
        Produce a simple codebook for UI/exports.
        """
    def apply_skip_logic(self, answers: Mapping[str, Any]) -> set[str]:
        """
        Return the set of question names that are enabled given current answers.
        """
    def validate_answer(
        self, name: str, value: Any, catalog: LabellingCatalog | None = None
    ) -> None: ...
    def to_row(self, answers: Mapping[str, Any]) -> dict[str, Any]:
        """
        Convert validated answers to a row (dict). For MULTI, store as a list (up to caller to expand).
        This function assumes `validate_answer` has been called per item.
        """
