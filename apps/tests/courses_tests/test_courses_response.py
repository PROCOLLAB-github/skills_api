from django.test import override_settings
import pytest

from rest_framework.test import APIClient

from . import constants


@pytest.mark.usefixtures("full_filled_published_skill")
def test_task_response_info_with_new_sub(api_auth_with_sub_client: APIClient):
    """
    response проверяется на полное соответствие,
    далее в этом необходимости нет, можно проверять отдельные компоненты.
    """
    response = api_auth_with_sub_client.get("/courses/1")
    assert constants.FULL_FILLED_PUBLISHED_SKILL_RESPONSE == response.json()


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
    print(response.json())
    respose_dct = response.json()
    assert respose_dct["progress"] == 50, "Прогресс не соответствует."
    assert respose_dct["step_data"][0]["is_done"] is True, "Задание не отметилось как выполненное."
