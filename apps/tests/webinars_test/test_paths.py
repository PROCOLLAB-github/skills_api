from unittest.mock import patch

import pytest
from rest_framework.test import APIClient

from . import constants


@pytest.mark.parametrize(
    "path",
    constants.ALL_GET_PATHS,
)
def test_all_get_paths_by_anon(path: str, api_anonymous_client: APIClient):
    response = api_anonymous_client.get(path)

    assert response.status_code == 403, f"Анониму должен быть недоступен {path}"


@pytest.mark.parametrize(
    "path",
    constants.ALL_GET_PATHS,
)
@pytest.mark.usefixtures("record_webinar")
def test_all_paths_with_sub(path: str, api_auth_with_sub_client: APIClient):
    response = api_auth_with_sub_client.get(path)

    assert response.status_code == 200, f"С подпиской должно быть доступно {path}"


@pytest.mark.parametrize(
    "path",
    constants.GET_PATHS_WO_SUB,
)
@pytest.mark.usefixtures("record_webinar")
def test_available_paths_wo_sub(path: str, api_auth_without_sub_client: APIClient):
    response = api_auth_without_sub_client.get(path)

    assert response.status_code == 200, f"Без подписки должно быть доступно {path}"


@pytest.mark.usefixtures("record_webinar")
def test_unavailable_paths_wo_sub(api_auth_without_sub_client: APIClient):
    response = api_auth_without_sub_client.get(constants.RECORD_LINK_PATH)

    assert response.status_code == 403, f"Без подписки должно быть НЕ доступно {constants.RECORD_LINK_PATH}"


@pytest.mark.usefixtures("actual_webinar")
def test_webinar_registration_by_anon(api_anonymous_client: APIClient):
    with patch("webinars.tasks.send_webinar_oline_link_email.delay"):
        response = api_anonymous_client.post(constants.RECORD_LINK_PATH)

    assert response.status_code == 403, "Анониму нельзя регистрироваться на вебинар"


@pytest.mark.usefixtures("actual_webinar")
def test_webinar_registration_with_sub(api_auth_with_sub_client: APIClient):
    with patch("webinars.tasks.send_webinar_oline_link_email.delay"):
        response = api_auth_with_sub_client.post(constants.WEBINAR_REGISTRATION_PATH)
    assert response.status_code == 201, "С подпиской дожна быть доступна регистрация"

    response = api_auth_with_sub_client.post(constants.WEBINAR_REGISTRATION_PATH)
    assert response.status_code == 400, "Повторный запрос на регистрацию должен вернуть 400"


@pytest.mark.usefixtures("actual_webinar")
def test_webinar_registration_wo_sub(api_auth_without_sub_client: APIClient):
    with patch("webinars.tasks.send_webinar_oline_link_email.delay"):
        response = api_auth_without_sub_client.post(constants.WEBINAR_REGISTRATION_PATH)
    assert response.status_code == 201, "Без подписки дожна быть доступна регистрация"

    response = api_auth_without_sub_client.post(constants.WEBINAR_REGISTRATION_PATH)
    assert response.status_code == 400, "Повторный запрос на регистрацию должен вернуть 400"
