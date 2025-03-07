from drf_spectacular.utils import OpenApiExample

SUCCESS_RESPONSE = OpenApiExample(
    "Success Response",
    value={"is_correct": True},
    status_codes=["201"],
    response_only=True,
)


SUCCESS_RESPONSE_WO_POINTS = OpenApiExample(
    "Success Response wo points",
    value={"is_correct": False},
    status_codes=["201"],
    response_only=True,
)

WRONG_ANSWER_RESPONSE = OpenApiExample(
    "Wrong Answer",
    value={"is_correct": False},
    status_codes=["400"],
    response_only=True,
)


WRONG_ANSWER_RESPONSE_WITH_HINT = OpenApiExample(
    "Wrong Answer with hint",
    value={"is_correct": False, "hint": "Some text"},
    status_codes=["400"],
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


SINGLE_RESPONSE_WITH_ANSWER = OpenApiExample(
    "Wrong with answer",
    value={"is_correct": False, "answer_ids": 1},
    status_codes=["201"],
    response_only=True,
)

EXCLUDE_RESPONSE_WITH_ANSWER = OpenApiExample(
    "Wrong with answer",
    value={"is_correct": False, "answer_ids": [1, 2, 3]},
    status_codes=["201"],
    response_only=True,
)

CONNECT_RESPONSE_WITH_ANSWER = OpenApiExample(
    "Wrong with answer",
    value={"is_correct": False, "answer_ids": [{"left_id": 1, "right_id": 1}]},
    status_codes=["201"],
    response_only=True,
)
