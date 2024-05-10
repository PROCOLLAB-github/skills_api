from enum import Enum
from typing import Union


class TypeQuestionPoints(Enum):
    INFO_SLIDE = 10
    QUESTION_SINGLE_ANSWER = 25
    QUESTION_WRITE = 40
    QUESTION_CONNECT = 50
    QUESTION_EXCLUDE = 60


TaskObjs = Union[
    TypeQuestionPoints.INFO_SLIDE,
    TypeQuestionPoints.QUESTION_SINGLE_ANSWER,
    TypeQuestionPoints.QUESTION_CONNECT,
    TypeQuestionPoints.QUESTION_EXCLUDE,
]
