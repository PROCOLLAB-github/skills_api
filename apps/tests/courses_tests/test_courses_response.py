import pytest
from django.test import override_settings

from rest_framework.test import APIClient

from . import constants


@pytest.mark.usefixtures("full_filled_published_skill")
def test_task_response_info_with_new_sub(api_auth_with_sub_client: APIClient):
    """
    response проверяется на полное соответствие,
    далее в этом необходимости нет, можно проверять отдельные компоненты.
    """
    response = api_auth_with_sub_client.get("/courses/1")
    assert constants.FULL_FILLED_PUBLISHED_SKILL_RESPONSE_NEW_SUB == response.json()


@pytest.mark.usefixtures("full_filled_published_skill")
def test_task_response_info_with_old_sub(api_auth_with_old_sub_client: APIClient):
    response = api_auth_with_old_sub_client.get("/courses/1")
    respose_dct = response.json()
    assert len(respose_dct["stats_of_weeks"]) == 4, "Кол-во доступных недель должно быть = 4"
    assert len(respose_dct["tasks"]) == 4, "Кол-во доступных задач должно быть = 4"


@pytest.mark.usefixtures("full_filled_published_skill")
@override_settings(task_always_eager=True)
def test_task_response_info_with_new_sub_progress(api_auth_with_sub_client: APIClient):
    api_auth_with_sub_client.post("/questions/info-slide/check/1")
    response = api_auth_with_sub_client.get("/courses/1")
    respose_dct = response.json()
    assert respose_dct["progress"] == 50, "Прогресс не соответствует."
    assert respose_dct["step_data"][0]["is_done"] is True, "Задание не отметилось как выполненное."


@pytest.mark.usefixtures("full_filled_published_skill")
@override_settings(task_always_eager=True)
def test_task_response_info_with_old_sub_progress(api_auth_with_old_sub_client: APIClient):
    api_auth_with_old_sub_client.post("/questions/info-slide/check/1")
    response = api_auth_with_old_sub_client.get("/courses/1")
    respose_dct = response.json()
    assert respose_dct["progress"] == 13, "Прогресс не соответствует."
    assert respose_dct["step_data"][0]["is_done"] is True, "Задание не отметилось как выполненное."


@pytest.mark.usefixtures(
    "full_filled_published_skill",
    "full_filled_only_stuff_skill",
    "full_filled_draft_skill",
)
@pytest.mark.parametrize("path", ("/courses/all-skills/", "/courses/choose-skills/"))
def test_all_skill_response_by_user(path, api_auth_with_sub_client: APIClient):
    response = api_auth_with_sub_client.get(path)
    respose_dct = response.json()
    assert respose_dct["count"] == 1, "Пользователь видит скрытые навыки."


@pytest.mark.usefixtures(
    "full_filled_published_skill",
    "full_filled_only_stuff_skill",
    "full_filled_draft_skill",
)
@pytest.mark.parametrize("path", ("/courses/all-skills/", "/courses/choose-skills/"))
def test_all_skill_response_by_staff(path, api_auth_with_sub_client_staff: APIClient):
    response = api_auth_with_sub_client_staff.get(path)
    respose_dct = response.json()
    assert respose_dct["count"] == 2, "Стафф видит/не видит навыки."


@pytest.mark.usefixtures(
    "full_filled_published_skill",
    "full_filled_only_stuff_skill",
    "full_filled_draft_skill",
)
@pytest.mark.parametrize("path", ("/courses/all-skills/", "/courses/choose-skills/"))
def test_all_skill_response_by_admin(path, api_auth_with_sub_client_admin: APIClient):
    response = api_auth_with_sub_client_admin.get(path)
    respose_dct = response.json()
    assert respose_dct["count"] == 3, "Админ не видит скрытые навыки (а должен)."
