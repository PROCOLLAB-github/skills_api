from dataclasses import dataclass


@dataclass
class SingleAnswerData:
    id: int
    answer_text: str


@dataclass
class QuestionExcludeSerializerData:
    id: int
    question_text: str | None
    description: str
    files: list[str]
    answers: list[SingleAnswerData]
    is_answered: bool | None = False
