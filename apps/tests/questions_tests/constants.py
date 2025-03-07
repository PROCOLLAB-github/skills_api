from typing import Any

from django.urls import reverse

# All get `questions` url paths:
CONNECT_QUESTION_GET: str = reverse("connect-question-get", kwargs={"task_obj_id": 1})
EXCLUDE_QUESTION_GET: str = reverse("exclude-question-get", kwargs={"task_obj_id": 1})
INFO_SLIDE_GET: str = reverse("info-slide-get", kwargs={"task_obj_id": 1})
SINGLE_CORRECT_GET: str = reverse("single-correct-get", kwargs={"task_obj_id": 1})
WRITE_QUESTION_GET: str = reverse("write-question-get", kwargs={"task_obj_id": 1})

# All post `questions` url paths:
CONNECT_QUESTION_POST: str = reverse("connect-question-post", kwargs={"task_obj_id": 1})
EXCLUDE_QUESTION_POST: str = reverse("exclude-question-post", kwargs={"task_obj_id": 1})
INFO_SLIDE_POST: str = reverse("info-slide-post", kwargs={"task_obj_id": 1})
SINGLE_CORRECT_POST: str = reverse("single-correct-post", kwargs={"task_obj_id": 1})
WRITE_QUESTION_POST: str = reverse("write-question-post", kwargs={"task_obj_id": 1})


ALL_GET_PATHS: list[str] = [
    CONNECT_QUESTION_GET,
    EXCLUDE_QUESTION_GET,
    INFO_SLIDE_GET,
    SINGLE_CORRECT_GET,
    WRITE_QUESTION_GET,
]


ALL_POST_PATHS: list[str] = [
    CONNECT_QUESTION_POST,
    EXCLUDE_QUESTION_POST,
    INFO_SLIDE_POST,
    SINGLE_CORRECT_POST,
    WRITE_QUESTION_POST,
]


INCORRECT_ANSWER_RESPONSE = {"is_correct": False}
INCORRECT_ANSWER_RESPONSE_HINT = {
    "is_correct": False,
    "hint": "Подсказка",
}


# где key - № попытки, value - response при неверных ответах
CONNECT_WRONG_ANSWER_RESPONSE: dict[int, Any] = {
    1: INCORRECT_ANSWER_RESPONSE,
    2: INCORRECT_ANSWER_RESPONSE_HINT,
    3: INCORRECT_ANSWER_RESPONSE_HINT,
    4: {
        "is_correct": False,
        "answer_ids": [
            {"left_id": 1, "right_id": 1},
            {"left_id": 2, "right_id": 2}
        ],
        "hint": "Подсказка",
    },
}

# где key - № попытки, value - response при неверных ответах
EXCLUDE_WRONG_ANSWER_RESPONSE: dict[int, Any] = {
    1: INCORRECT_ANSWER_RESPONSE,
    2: INCORRECT_ANSWER_RESPONSE_HINT,
    3: INCORRECT_ANSWER_RESPONSE_HINT,
    4: {
        "is_correct": False,
        "answer_ids": [2, 3],
        "hint": "Подсказка",
    },
}

# где key - № попытки, value - response при неверных ответах
SINGLE_WRONG_ANSWER_RESPONSE: dict[int, Any] = {
    1: INCORRECT_ANSWER_RESPONSE,
    2: INCORRECT_ANSWER_RESPONSE_HINT,
    3: INCORRECT_ANSWER_RESPONSE_HINT,
    4: {
        "is_correct": False,
        "answer_ids": 1,
        "hint": "Подсказка",
    },
}
