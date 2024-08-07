from enum import Enum

from questions.mapping import TypeQuestionPoints

TYPE_TASK_OBJECT: dict[str, str] = {
    "infoslide": "info_slide",
    "questionconnect": "question_connect",
    "questionsingleanswer": "question_single_answer",
    "questionwrite": "question_write",
}
# TODO заменить на Enum


class ModelNameEnum(Enum):
    INFO_SLIDE = "info_slide"
    QUESTION_CONNECT = "question_connect"
    QUESTION_SINGLE_ANSWER = "question_single_answer"
    QUESTION_EXCLUDE = "question_exclude"


SWAGGER_API_HINTS: dict[str, str] = {
    "info_slide": "информационный слайд",
    "question_connect": "вопрос на сопоставление",
    "question_single_answer": "вопрос где надо выбрать 1 ответ",
    "exclude_question": "вопрос, где надо исключить неправильные ответы",
    "question_write": "вопрос, где надо написать ответ",
}


def check_if_task_correct(task_obj_result) -> int:
    """Проверяет, совпадает ли количество очков с максимально возможным кол-вом очков у типа задачи"""

    content_type = task_obj_result.task_object.content_type
    content_type_verbose = TYPE_TASK_OBJECT[
        content_type.model
    ].upper()  # приводим в читаемый вид и готовим к работе с классом Enum
    points_gained = task_obj_result.points_gained

    if points_gained == getattr(TypeQuestionPoints, content_type_verbose).value:
        return points_gained
    return 0
