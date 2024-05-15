from enum import Enum
from typing import Union

from questions.models import QuestionSingleAnswer


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


def get_answer_type(view_class) -> str:
    view_name = view_class.__class__.__name__.lower()
    answer_field = "content_object__"

    if "exclude" in view_name or "single" in view_name:
        answer_field += "single_answers"
    elif "connect" in view_name:
        answer_field += "connect_answers"

    return answer_field


def wrong_endpoint_text(request_question, view) -> tuple[str, str]:
    needed = view.expected_question_model._meta.verbose_name
    gotten = request_question._meta.verbose_name

    view_name = view.__class__.__name__.lower()
    if isinstance(request_question, QuestionSingleAnswer):
        gotten = "Вопрос на исключение" if request_question.is_exclude else "Вопрос с одним правильным ответом"
        if "exclude" in view_name:
            needed = "Вопрос на исключение"
        elif "single" in view_name:
            needed = "Вопрос с одним правильным ответом"

    return needed, gotten
