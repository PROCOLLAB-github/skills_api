import json

import pytest
from rest_framework.test import APIClient
from django.test import override_settings

from . import constants


@pytest.mark.usefixtures("write_question_data")
def test_write_not_answered(api_auth_with_sub_client: APIClient):
    response = api_auth_with_sub_client.get(constants.WRITE_QUESTION_GET)
    response_data = response.json()

    assert response.status_code == 200
    assert (
        response_data["text"] == "123"
    ), "почему-то текст не такой, какой задан в текстуре"
    assert response_data["answer"] is None, "почему-то ответ уже есть, быть не должен"


@pytest.mark.usefixtures("write_question_data_answered")
def test_write_answered(api_auth_with_sub_client: APIClient):
    response = api_auth_with_sub_client.get(constants.WRITE_QUESTION_GET)
    response_data = response.json()

    assert response.status_code == 200
    assert (
        response_data["text"] == "123"
    ), "почему-то текст не такой, какой задан в текстуре"
    assert response_data["answer"]["text"] == "sigma", "почему-то задание не сделано"


@pytest.mark.usefixtures("write_question_data")
@override_settings(task_always_eager=True)
def test_write_not_answered_post(api_auth_with_sub_client: APIClient):
    data = {"text": "some"}

    response = api_auth_with_sub_client.post(
        constants.WRITE_QUESTION_POST,
        data=json.dumps(data),
        content_type="application/json"
    )
    response_data = response.json()

    assert response.status_code == 201, "Задание (write) не принимается к ответу"
    assert response_data["is_correct"] is True, "Задание (write) решено верно, но response некорректный"
