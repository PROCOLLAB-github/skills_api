from dataclasses import dataclass


@dataclass
class SingleAnswerData:
    id: int
    text: str


@dataclass
class QuestionSerializerData:
    id: int
    question_text: str | None
    description: str
    files: list[str]
    answers: list[SingleAnswerData]
    is_answered: bool | None = False


@dataclass
class AnswerUserWriteData:
    id: int
    text: int


@dataclass
class QuestionWriteSerializerData:
    id: int
    text: str
    description: str
    files: list[str]
    answer: AnswerUserWriteData | None = None


@dataclass
class QuestionСonnectSerializerData:
    id: int
    text: str
    description: str
    connect_left: list[SingleAnswerData]
    connect_right: list[SingleAnswerData]
    files: list[str]
    is_answered: bool | None = False
