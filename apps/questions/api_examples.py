from drf_spectacular.utils import OpenApiExample


SUCCESS_RESPONSE = OpenApiExample(
    "Success Response",
    value={"text": "success"},
    status_codes=["201"],
    response_only=True,
)

QUERY_DOES_NOT_EXISTS = OpenApiExample(
    "Query does not exist",
    value={"error": "'Answer' matching query does not exist."},
    status_codes=["400"],
    response_only=True,
)

WRONG_TASKOBJECT = OpenApiExample(
    "Wrong Taskobject",
    value={
        "error": ("You tried to summon taskobject with a wrong endpoint. "
                  "Instead of using 'This' endpoint, try using 'Somebody else' endpoint.")
    },
    status_codes=["403"],
    response_only=True,
)

USER_ALREADY_DONE_TASK = OpenApiExample(
    "Already done",
    value={"error": "User has already done this 'task'!"},
    status_codes=["400"],
    response_only=True,
)

NEED_MORE_QUESTION_EXCLUDE_RESPONSE = OpenApiExample(
    "Need More Response",
    value={"text": "need more..."},
    status_codes=["400"],
    response_only=True,
)

WRONG_ANSWERS_QUESTION_EXCLUDE_RESPONSE = OpenApiExample(
    "Wrong Answers",
    value={"is_correct": False, "wrong_answers": [0]},
    status_codes=["400"],
    response_only=True,
)

WRONG_ANSWERS_QUESTION_CONNECT_RESPONSE = OpenApiExample(
    "Wrong Answers",
    value=[
        {"left_id": 1, "right_id": 2, "is_correct": False},
        {"left_id": 2, "right_id": 1, "is_correct": False},
    ],
    status_codes=["400"],
    response_only=True,
)

WRONG_SINGLE_CORECT_QUESTION_RESPONSE = OpenApiExample(
    "Wrong Answer",
    value={"is_correct": False, "correct_answer": 1},
    status_codes=["400"],
    response_only=True,
)
