import json

import pytest
from django.test import override_settings
from rest_framework.test import APIClient

from . import constants


@pytest.mark.usefixtures("exclude_question_data")
def test_exclude_not_answered(api_auth_with_sub_client: APIClient):
    response = api_auth_with_sub_client.get(constants.EXCLUDE_QUESTION_GET)
    response_data = response.json()

    assert response.status_code == 200
    assert response_data["is_answered"] is False, "Неотвеченный вопрос пометился некорректно"
    assert len(response_data["answers"]) > 1, "Должно быть больше 1 варианта ответов"


@pytest.mark.usefixtures("free_exclude_free_question_data")
def test_free_exclude_not_answered(api_auth_with_sub_client: APIClient):
    response = api_auth_with_sub_client.get(constants.EXCLUDE_QUESTION_GET)
    response_data = response.json()

    assert response.status_code == 200
    assert response_data["is_answered"] is False, "(Бесплатно) Неотвеченный вопрос пометился некорректно"
    assert len(response_data["answers"]) > 1, "(Бесплатно) Должно быть больше 1 варианта ответов"


@pytest.mark.usefixtures("free_exclude_free_question_data")
def test_free_exclude_not_answered_wo_sub(api_auth_without_sub_client: APIClient):
    response = api_auth_without_sub_client.get(constants.EXCLUDE_QUESTION_GET)
    response_data = response.json()

    assert response.status_code == 200
    assert response_data["is_answered"] is False, "(Бесплатно)(Без подп.) Неотвеченный вопрос пометился некорректно"
    assert len(response_data["answers"]) > 1, "(Бесплатно)(Без подп.) Должно быть больше 1 варианта ответов"


@pytest.mark.usefixtures("exclude_question_data_answered")
def test_exclude_answered(api_auth_with_sub_client: APIClient):
    response = api_auth_with_sub_client.get(constants.EXCLUDE_QUESTION_GET)
    response_data = response.json()

    assert response.status_code == 200
    assert response_data["is_answered"] is True, "Почему-то вопрос не помечен как отвеченый"
    assert len(response_data["answers"]) == 1, "Почему-то выдало больше одного ответа"


@pytest.mark.usefixtures("exclude_question_data")
@override_settings(task_always_eager=True)
def test_exclude_not_answered_post(api_auth_with_sub_client: APIClient):
    data = [2, 3]

    response = api_auth_with_sub_client.post(
        constants.EXCLUDE_QUESTION_POST,
        data=json.dumps(data),
        content_type="application/json"
    )
    response_data = response.json()

    assert response.status_code == 201, "Задание (исключ) не принимается к ответу"
    assert response_data["is_correct"] is True, "Задание (исключ) решено верно, но response некорректный"


@pytest.mark.usefixtures("free_exclude_free_question_data")
@override_settings(task_always_eager=True)
def test_free_exclude_not_answered_post(api_auth_with_sub_client: APIClient):
    data = [2, 3]

    response = api_auth_with_sub_client.post(
        constants.EXCLUDE_QUESTION_POST,
        data=json.dumps(data),
        content_type="application/json"
    )
    response_data = response.json()

    assert response.status_code == 201, "(Бесплтано) Задание (исключ) не принимается к ответу"
    assert response_data["is_correct"] is True, "(Бесплатно) Задание (исключ) решено верно, но response некорректный"


@pytest.mark.usefixtures("free_exclude_free_question_data")
@override_settings(task_always_eager=True)
def test_free_exclude_not_answered_post_wo_sub(api_auth_without_sub_client: APIClient):
    data = [2, 3]

    response = api_auth_without_sub_client.post(
        constants.EXCLUDE_QUESTION_POST,
        data=json.dumps(data),
        content_type="application/json"
    )
    response_data = response.json()

    assert response.status_code == 201, (
        "(Бесплтано)(Без подп.) Задание (исключ) не принимается к ответу"
    )
    assert response_data["is_correct"] is True, (
        "(Бесплатно)(Без подп.) Задание (исключ) решено верно, но response некорректный"
    )


@pytest.mark.usefixtures("exclude_question_data_with_hint")
@override_settings(task_always_eager=True)
def test_exclude_wrong_answers_with_hint(api_auth_with_sub_client: APIClient):
    data = [1, 2]

    for answer_try in range(1, 5):
        response = api_auth_with_sub_client.post(
            constants.EXCLUDE_QUESTION_POST,
            data=json.dumps(data),
            content_type="application/json"
        )
        response_data = response.json()

        assert response_data == constants.EXCLUDE_WRONG_ANSWER_RESPONSE[answer_try], (
            "Запрос с неправильным ответом на вопрос вернул неверный reponse. "
            "Возможно отсутствует подсказка или ответ в конце."
        )
