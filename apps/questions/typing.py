from dataclasses import dataclass


@dataclass
class SingleAnswerData:
    id: int
    text: str


@dataclass
class SingleConnectedAnswerData:
    id: int
    text: str | None = None
    file: str | None = None


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
    connect_left: list[SingleConnectedAnswerData]
    connect_right: list[SingleConnectedAnswerData]
    files: list[str]
    is_answered: bool | None = False


@dataclass
class ScoredConnectAnswerSerializerData:
    left_id: int
    right_id: int
    is_correct: bool


@dataclass
class ConnectAnswerSerializerData:
    left_id: int
    right_id: int


@dataclass
class WriteAnswerTextSerializerData:
    text: str


@dataclass
class CustomTextErrorSerializerData:
    error: str


@dataclass
class CustomTextSucessSerializerData:
    text: str


@dataclass
class QuestionExcludePostResponseSerializer:
    is_correct: bool
    wrong_answers: list[int]


@dataclass
class SingleCorrectPostSuccessResponseSerializerData:
    is_correct: bool


@dataclass
class SingleCorrectPostErrorResponseSerializerData:
    is_correct: bool
    correct_answer: int


@dataclass
class InfoSlideSerializerData:
    text: str
    files: list[str]
    is_done: bool
