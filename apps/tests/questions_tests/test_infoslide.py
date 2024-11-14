import pytest
from django.test import override_settings
from rest_framework.test import APIClient

from . import constants


@pytest.mark.usefixtures("info_question_data")
def test_infoslide_not_answered(api_auth_with_sub_client: APIClient):
    response = api_auth_with_sub_client.get(constants.INFO_SLIDE_GET)
    response_data = response.json()

    assert response.status_code == 200
    assert (
        response_data["text"] == "123"
    ), "почему-то текст не такой, какой задан в текстуре"
    assert response_data["is_done"] is False, "почему-то задание сделано"


@pytest.mark.usefixtures("info_question_answered_data")
def test_infoslide_answered(api_auth_with_sub_client: APIClient):
    response = api_auth_with_sub_client.get(constants.INFO_SLIDE_GET)
    response_data = response.json()

    assert response.status_code == 200
    assert (
        response_data["text"] == "123"
    ), "почему-то текст не такой, какой задан в текстуре"
    assert response_data["is_done"] is True, "почему-то задание не сделано"


@pytest.mark.usefixtures("info_question_data")
@override_settings(task_always_eager=True)
def test_infoslide_not_answered_post(api_auth_with_sub_client: APIClient):
    response = api_auth_with_sub_client.post(constants.INFO_SLIDE_POST)
    assert response.status_code == 204, "Задание (инфо слайд) не принимается к ответу"
