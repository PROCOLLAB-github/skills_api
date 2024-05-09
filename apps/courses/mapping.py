from enum import Enum

TYPE_TASK_OBJECT: dict[str, str] = {
    "infoslide": "info_slide",
    "questionconnect": "question_connect",
    "questionsingleanswer": "question_single_answer",
}
# TODO заменить на Enum


class ModelNameEnum(Enum):
    INFO_SLIDE = "info_slide"
    QUESTION_CONNECT = "question_connect"
    QUESTION_SINGLE_ANSWER = "question_single_answer"
    QUESTION_EXCLUDE = "question_exlude"


SWAGGER_API_HINTS: dict[str, str] = {
    "info_slide": "информационный слайд",
    "question_connect": "вопрос на сопоставление",
    "question_single_answer": "вопрос где надо выбрать 1 ответ",
    "exclude_question": "вопрос, где надо исключить неправильные ответы",
}
