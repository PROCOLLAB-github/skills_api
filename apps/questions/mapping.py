from enum import Enum
from typing import Union

from questions.models import QuestionSingleAnswer, InfoSlide, QuestionConnect, QuestionWrite


class TypeQuestionPoints(Enum):
    INFO_SLIDE = 5
    QUESTION_SINGLE_ANSWER = 5
    QUESTION_WRITE = 5
    QUESTION_CONNECT = 5
    QUESTION_EXCLUDE = 5


TaskObjs = Union[
    TypeQuestionPoints.INFO_SLIDE,
    TypeQuestionPoints.QUESTION_SINGLE_ANSWER,
    TypeQuestionPoints.QUESTION_CONNECT,
    TypeQuestionPoints.QUESTION_EXCLUDE,
]


def get_fields_for_answer_type(view_class) -> list[str]:
    """Получение списка всех необходимых связанных объктов и полей для prefetch_related."""
    field_for_prefetch = {
        QuestionSingleAnswer: ["content_object", "content_object__single_answers"],
        QuestionConnect: ["content_object", "content_object__connect_answers"],
        QuestionWrite: ["content_object"],
        InfoSlide: ["content_object"],
    }
    question_field: list[str] = field_for_prefetch.get(view_class.expected_question_model)
    return question_field


def wrong_endpoint_text(request_question, view) -> tuple[str, str]:
    needed: str = view.expected_question_model._meta.verbose_name
    gotten: str = request_question._meta.verbose_name

    view_name = view.__class__.__name__.lower()
    if isinstance(request_question, QuestionSingleAnswer):
        gotten = "Вопрос на исключение" if request_question.is_exclude else "Вопрос с одним правильным ответом"
    if view.expected_question_model == QuestionSingleAnswer:
        if "exclude" in view_name:
            needed = "Вопрос на исключение"
        elif "single" in view_name:
            needed = "Вопрос с одним правильным ответом"

    return needed, gotten
