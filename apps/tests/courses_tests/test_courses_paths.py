import pytest

from rest_framework.test import APIClient

from . import constants


@pytest.mark.parametrize("path", constants.COURSES_NO_ACCESS_PATHS)
def test_anymous_user_no_access(path, api_anonymous_client: APIClient):
    response = api_anonymous_client.get(path)
    assert response.status_code == 403, f"Аноним НЕ должен иметь доступа к {path}"


@pytest.mark.parametrize("path", constants.COURSES_ACCESS_PATHS)
def test_anymous_user_have_access(path, api_anonymous_client: APIClient):
    response = api_anonymous_client.get(path)
    assert response.status_code == 200, f"Аноним ДОЛЖЕН иметь доступ к {path}"


@pytest.mark.parametrize("path", constants.COURSES_ALL_PATHS)
@pytest.mark.usefixtures("skill_wo_tasks", "task_wo_questions")
def test_auth_user_with_sub_have_access(path, api_auth_with_sub_client: APIClient):
    response = api_auth_with_sub_client.get(path)
    assert response.status_code == 200, f"Пользователь c подпиской должен иметь доступ к {path}"


@pytest.mark.parametrize("path", constants.COURSES_NO_ACCESS_PATHS)
@pytest.mark.usefixtures("skill_wo_tasks", "task_wo_questions")
def test_auth_user_wo_sub_no_access(path, api_auth_without_sub_client: APIClient):
    response = api_auth_without_sub_client.get(path)
    assert response.status_code == 403, f"Пользователь без подписки НЕ должен иметь доступ к {path}"


@pytest.mark.parametrize("path", constants.COURSES_NO_ACCESS_PATHS)
@pytest.mark.usefixtures("skill_wo_tasks", "task_wo_questions")
def test_auth_with_overdue_sub_no_access(path, api_auth_with_overdue_sub_client: APIClient):
    response = api_auth_with_overdue_sub_client.get(path)
    assert response.status_code == 403, f"Пользователь с просроченной подписокй НЕ должен иметь доступ к {path}"
