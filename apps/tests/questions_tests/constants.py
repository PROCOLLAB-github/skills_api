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
