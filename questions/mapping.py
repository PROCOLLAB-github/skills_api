from typing import Union, Literal

POINTS_MAPPING: dict[str, int] = {
    "info_slide": 10,
    "question_single_answer": 25,
    "question_connect": 50,
    "question_exclude": 60,
}

TaskObjs = Union[
    Literal["info_slide"],
    Literal["question_single_answer"],
    Literal["question_connect"],
    Literal["question_exclude"],
]
