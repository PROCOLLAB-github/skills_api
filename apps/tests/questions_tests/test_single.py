import json

import pytest
from rest_framework.test import APIClient
from django.test import override_settings

from . import constants


@pytest.mark.usefixtures("question_data")
def test_single_not_answered(api_auth_with_sub_client: APIClient):
    response = api_auth_with_sub_client.get(constants.SINGLE_CORRECT_GET)
    response_data = response.json()

    assert response.status_code == 200
    assert (
        response_data["is_answered"] is False
    ), "Почему-то на вопрос уже ответили, странно, такого быть не должно"
    assert (
        len(response_data["answers"]) > 1
    ), "Почему-то выдало всего один правильный ответ. Должно больше"


@pytest.mark.usefixtures("question_data_answered")
def test_single_answered(api_auth_with_sub_client: APIClient):
    response = api_auth_with_sub_client.get(constants.SINGLE_CORRECT_GET)
    response_class = response.json()

    assert response.status_code == 200
    assert (
        response_class["is_answered"] is True
    ), "Почему-то на вопрос не ответили, странно, такого быть не должно"
    assert (
        len(response_class["answers"]) == 1
    ), "Почему-то выдало больше одного правильного ответа"


@pytest.mark.usefixtures("question_data")
@override_settings(task_always_eager=True)
def test_single_not_answered_post(api_auth_with_sub_client: APIClient):
    data = {"answer_id": 1}

    response = api_auth_with_sub_client.post(
        constants.SINGLE_CORRECT_POST,
        data=json.dumps(data),
        content_type="application/json"
    )
    response_data = response.json()

    assert response.status_code == 201, "Задание (1 правильный) не принимается к ответу"
    assert response_data["is_correct"] is True, "Задание (1 правильный) решено верно, но response некорректный"


@pytest.mark.usefixtures("single_question_data_with_hint")
@override_settings(task_always_eager=True)
def test_single_wrong_answers_with_hint(api_auth_with_sub_client: APIClient):
    data = {"answer_id": 2}

    for answer_try in range(1, 5):
        response = api_auth_with_sub_client.post(
            constants.SINGLE_CORRECT_POST,
            data=json.dumps(data),
            content_type="application/json"
        )
        response_data = response.json()

        assert response_data == constants.SINGLE_WRONG_ANSWER_RESPONSE[answer_try], (
            "Запрос с неправильным ответом на вопрос вернул неверный reponse. "
            "Возможно отсутствует подсказка или ответ в конце."
        )
