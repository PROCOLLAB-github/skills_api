import json

import pytest
from rest_framework.test import APIClient
from django.test import override_settings

from . import constants


@pytest.mark.usefixtures("connect_question_data")
def test_connect_not_answered(api_auth_with_sub_client: APIClient):
    response = api_auth_with_sub_client.get(constants.CONNECT_QUESTION_GET)
    response_data = response.json()

    assert response.status_code == 200
    assert len(response_data["connect_left"]) == 2
    assert response_data["is_answered"] is False


@pytest.mark.usefixtures("connect_question_data_answered")
def test_connect_answered(api_auth_with_sub_client: APIClient):
    response = api_auth_with_sub_client.get(constants.CONNECT_QUESTION_GET)
    response_data = response.json()

    assert response.status_code == 200
    assert len(response_data["connect_left"]) == 2
    assert response_data["is_answered"] is True

    for left, right in zip(
        response_data["connect_left"], response_data["connect_right"]
    ):
        assert left["id"] == right["id"], "порядок вопросов нарушен"


@pytest.mark.usefixtures("connect_question_data")
@override_settings(task_always_eager=True)
def test_connect_not_answered_post(api_auth_with_sub_client: APIClient):
    data = [{"left_id": 1, "right_id": 1}, {"left_id": 2, "right_id": 2}]

    response = api_auth_with_sub_client.post(
        constants.CONNECT_QUESTION_POST,
        data=json.dumps(data),
        content_type="application/json"
    )
    response_data = response.json()

    assert response.status_code == 201, "Задание (соотношение) не принимается к ответу"
    assert response_data["is_correct"] is True, "Задание (соотношение) решено верно, но response некорректный"


@pytest.mark.usefixtures("connect_question_data_with_hint")
@override_settings(task_always_eager=True)
def test_connect_qustion_with_hint_wrong_answer(api_auth_with_sub_client: APIClient):
    data = [{"left_id": 2, "right_id": 1}, {"left_id": 1, "right_id": 2}]

    for answer_try in range(1, 5):
        response = api_auth_with_sub_client.post(
            constants.CONNECT_QUESTION_POST,
            data=json.dumps(data),
            content_type="application/json"
        )
        response_data = response.json()

        assert response_data == constants.CONNECT_WRONG_ANSWER_RESPONSE[answer_try], (
            "Запрос с неправильным ответом на вопрос вернул неверный reponse. "
            "Возможно отсутствует подсказка или ответ"
        )
