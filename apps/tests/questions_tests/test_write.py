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
    assert response_data["text"] == "123", "Текст задания не соотв. фикстуре"
    assert response_data["answer"] is None, "Ответа в неотвеченном задании не должно быть"


@pytest.mark.usefixtures("free_write_question_data")
def test_free_write_not_answered(api_auth_with_sub_client: APIClient):
    response = api_auth_with_sub_client.get(constants.WRITE_QUESTION_GET)
    response_data = response.json()

    assert response.status_code == 200
    assert response_data["text"] == "123", "(Бесплатно) Текст задания не соотв. фикстуре"
    assert response_data["answer"] is None, "(Бесплтано) Ответа в неотвеченном задании не должно быть"


@pytest.mark.usefixtures("free_write_question_data")
def test_free_write_not_answered_wo_sub(api_auth_without_sub_client: APIClient):
    response = api_auth_without_sub_client.get(constants.WRITE_QUESTION_GET)
    response_data = response.json()

    assert response.status_code == 200
    assert response_data["text"] == "123", "(Бесплатно)(Без.подп) Текст задания не соотв. фикстуре"
    assert response_data["answer"] is None, "(Бесплтано)(Без.подп) Ответа в неотвеченном задании не должно быть"


@pytest.mark.usefixtures("write_question_data_answered")
def test_write_answered(api_auth_with_sub_client: APIClient):
    response = api_auth_with_sub_client.get(constants.WRITE_QUESTION_GET)
    response_data = response.json()

    assert response.status_code == 200
    assert response_data["text"] == "123", "Текст задания не соотв. фикстуре"
    assert response_data["answer"]["text"] == "sigma", "В отвеченном задании ответ не соотв."


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
    assert response_data["is_correct"] is True, "Задание (write) решено, но response некорректный"


@pytest.mark.usefixtures("free_write_question_data")
@override_settings(task_always_eager=True)
def test_free_write_not_answered_post(api_auth_with_sub_client: APIClient):
    data = {"text": "some"}

    response = api_auth_with_sub_client.post(
        constants.WRITE_QUESTION_POST,
        data=json.dumps(data),
        content_type="application/json"
    )
    response_data = response.json()

    assert response.status_code == 201, "(Бесплатно)Задание (write) не принимается к ответу"
    assert response_data["is_correct"] is True, "(Бесплатно)Задание (write) решено, но response некорректный"


@pytest.mark.usefixtures("free_write_question_data")
@override_settings(task_always_eager=True)
def test_free_write_not_answered_post_wo_sub(api_auth_without_sub_client: APIClient):
    data = {"text": "some"}

    response = api_auth_without_sub_client.post(
        constants.WRITE_QUESTION_POST,
        data=json.dumps(data),
        content_type="application/json"
    )
    response_data = response.json()

    assert response.status_code == 201, "(Бесплатно)(Без подп.) Задание (write) не принимается к ответу"
    assert response_data["is_correct"] is True, "(Бесплатно)(Без подп.)Задание (write) решено, но response некорректный"


@pytest.mark.usefixtures("write_question_data")
@override_settings(task_always_eager=True)
def test_write_empty_answer(api_auth_with_sub_client: APIClient):
    data = {"text": ""}

    response = api_auth_with_sub_client.post(
        constants.WRITE_QUESTION_POST,
        data=json.dumps(data),
        content_type="application/json"
    )
    response_data = response.json()

    assert response.status_code == 400, "Пустой ответ принялся"
    assert response_data["is_correct"] is False, "Неверный response для неверного ответа"
