import pytest
from rest_framework.test import APIClient

from . import constants


@pytest.mark.parametrize("path", constants.PROGRESS_NO_ACCESS_PATHS)
def test_progress_path_by_anonymous(path, api_anonymous_client: APIClient):
    response = api_anonymous_client.get(path)
    assert response.status_code == 403, f"Аноним получил не тот статус тут: {path}"


def test_anonymous_registarion_correct_data(api_anonymous_client: APIClient):
    response = api_anonymous_client.post(
        path=constants.REGISTRATION_PATH,
        data=constants.CORRECT_REGISTRATION_DATA,
    )
    assert response.status_code == 201, "Аноним не может зарегистрироваться."


def test_anonymous_registarion_incorrect_data(api_anonymous_client: APIClient):
    response = api_anonymous_client.post(
        path=constants.REGISTRATION_PATH,
        data=constants.INCORRECT_REGISTRATION_DATA,
    )
    assert response.status_code == 400, "Некорректные данные прошли регистрацию."


@pytest.mark.usefixtures("user")
def test_registration_with_existing_email(api_anonymous_client: APIClient):
    response = api_anonymous_client.post(
        path=constants.REGISTRATION_PATH,
        data=constants.CORRECT_REGISTRATION_DATA,
    )
    assert response.status_code == 400, "Существующий email прошел регистацию."


@pytest.mark.parametrize("path", (constants.USER_PROFILE_PATH, constants.SUBSCRIBTION_USER_DATA_PATH))
def test_auth_client_wo_sub_available(path, api_auth_without_sub_client: APIClient):
    response = api_auth_without_sub_client.get(path)
    assert response.status_code == 200, f"Auth пользователь без подписки, не получил доступа к {path}"


@pytest.mark.parametrize(
    "path",
    (
        constants.USER_SCORE_RATING_PATH,
        constants.SKILL_RATING_PATH,
        constants.ADD_SKILLS_PATH,
        constants.SKILL_RATING_PATH,
    )
)
def test_auth_client_wo_sub_forbidden(path, api_auth_without_sub_client: APIClient):
    response = api_auth_without_sub_client.get(path)
    assert response.status_code == 403, f"Auth пользователь без подписки, получил доступ к {path}"


@pytest.mark.parametrize("path", constants.PROGRESS_NO_ACCESS_GET_PATHS)
def test_auth_client_with_sub_all_path(path, api_auth_with_sub_client: APIClient):
    response = api_auth_with_sub_client.get(path)
    assert response.status_code == 200, f"Пользователь с подпиской не получил доступа к {path}"


# TODO Тесты:
#   - /progress/add-skills/
#   - /progress/update-auto-renewal/
# Они пока в принципе не работают/работают некорректно.
