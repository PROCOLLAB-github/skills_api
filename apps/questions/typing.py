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
    text: str | None
    video_url: str | None
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
    video_url: str | None
    files: list[str]
    answer: AnswerUserWriteData | None = None


@dataclass
class QuestionСonnectSerializerData:
    id: int
    text: str
    description: str
    video_url: str | None
    connect_left: list[SingleConnectedAnswerData]
    connect_right: list[SingleConnectedAnswerData]
    files: list[str]
    is_answered: bool | None = False


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
class InfoSlideSerializerData:
    text: str | None
    description: str | None
    files: list[str]
    is_done: bool
    video_url: str | None
