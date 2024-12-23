import pytest
from django.test import override_settings
from rest_framework.test import APIClient

from . import constants


@pytest.mark.usefixtures("info_question_data")
def test_infoslide_not_answered(api_auth_with_sub_client: APIClient):
    response = api_auth_with_sub_client.get(constants.INFO_SLIDE_GET)
    response_data = response.json()

    assert response.status_code == 200
    assert response_data["text"] == "123", "Текст вопроса не соотв. фикстуре"
    assert response_data["is_done"] is False, "Задание должно быть не решенным"


@pytest.mark.usefixtures("free_info_question_data")
def test_free_infoslide_not_answered(api_auth_with_sub_client: APIClient):
    response = api_auth_with_sub_client.get(constants.INFO_SLIDE_GET)
    response_data = response.json()

    assert response.status_code == 200, "(Бесплтано) Почему-то недоступен вопрос"
    assert response_data["text"] == "123", "(Бесплтано) Текст вопроса не соотв. фикстуре"
    assert response_data["is_done"] is False, "(Бесплтано) Задание должно быть не решенным"


@pytest.mark.usefixtures("info_question_answered_data")
def test_infoslide_answered(api_auth_with_sub_client: APIClient):
    response = api_auth_with_sub_client.get(constants.INFO_SLIDE_GET)
    response_data = response.json()

    assert response.status_code == 200
    assert response_data["text"] == "123", "Текст вопроса не соотв. фикстуре"
    assert response_data["is_done"] is True, "Задание должно быть решено"


@pytest.mark.usefixtures("info_question_data")
@override_settings(task_always_eager=True)
def test_infoslide_not_answered_post(api_auth_with_sub_client: APIClient):
    response = api_auth_with_sub_client.post(constants.INFO_SLIDE_POST)
    assert response.status_code == 201, "Задание (инфо слайд) не принимается к ответу"


@pytest.mark.usefixtures("free_info_question_data")
@override_settings(task_always_eager=True)
def test_free_infoslide_not_answered_post(api_auth_with_sub_client: APIClient):
    response = api_auth_with_sub_client.post(constants.INFO_SLIDE_POST)
    assert response.status_code == 201, "(Бесплтано) Задание (инфо слайд) не принимается к ответу"


@pytest.mark.usefixtures("free_info_question_data")
@override_settings(task_always_eager=True)
def test_free_infoslide_not_answered_post_wo_sub(api_auth_without_sub_client: APIClient):
    response = api_auth_without_sub_client.post(constants.INFO_SLIDE_POST)
    assert response.status_code == 201, "(Бесплтано)(Без подп.) Задание (инфо слайд) не принимается к ответу"
