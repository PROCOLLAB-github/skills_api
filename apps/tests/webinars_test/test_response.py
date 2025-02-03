import pytest
from rest_framework.test import APIClient

from . import constants


@pytest.mark.usefixtures("actual_webinar", "record_webinar")
def test_actual_webinars(api_auth_with_sub_client: APIClient):
    response = api_auth_with_sub_client.get(constants.ACTUAL_WEBINARS_PATH)
    response_dct = response.json()

    assert response_dct["count"] == 1, "Актуальный только 1 вебинар"
    assert response_dct["results"][0]["title"] == "Акутальный", (
        "Неверный response, либо данные, либо доступен неактуальный"
    )
    assert response_dct["results"][0]["duration"] == 60, (
        "Неверный response, либо данные, либо доступен неактуальный"
    )


@pytest.mark.usefixtures("actual_webinar", "record_webinar")
def test_record_webinars(api_auth_with_sub_client: APIClient):
    response = api_auth_with_sub_client.get(constants.RECORD_WEBINARS_PATH)
    response_dct = response.json()

    assert response_dct["count"] == 1, "В записи только 1 вебинар"
    assert response_dct["results"][0]["title"] == "Запись", (
        "Неверный response, либо данные, либо доступен актуальный"
    )
    assert response_dct["results"][0]["duration"] == 60, (
        "Неверный response, либо данные, либо доступен актуальный"
    )


@pytest.mark.usefixtures("record_webinar", "actual_webinar")
def test_record_webinars_get_link(api_auth_with_sub_client: APIClient):
    response = api_auth_with_sub_client.get(constants.RECORD_LINK_PATH)
    response_dct = response.json()

    assert response_dct["recording_link"] == "https://example4.com", "Неверная ссылка на запись вебинара"
