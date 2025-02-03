import pytest
from django.urls import reverse
from rest_framework.test import APIClient

import constants


@pytest.mark.usefixtures("trying_sub", "optimum_sub")
def test_get_all_sub_types_wo_sub(api_auth_without_sub_client: APIClient):
    get_url = reverse("view-subscriptions")
    response = api_auth_without_sub_client.get(get_url)
    response_data: list[dict] = response.json()

    assert response.status_code == 200, "Ошибка при получении подписок"
    assert response_data == constants.SUB_RESPONSE, "Не соотв. ответ по подпискам"


@pytest.mark.usefixtures("trying_sub", "optimum_sub")
def test_check_active_available_sub_with_trial_sub(api_auth_with_sub_client: APIClient):
    """Активна пробная, НЕ просрочена."""
    get_url = reverse("view-subscriptions")
    response = api_auth_with_sub_client.get(get_url)
    response_data: list[dict] = response.json()
    trial = [sub for sub in response_data if sub["name"] == "Пробная"][0]
    optimum = [sub for sub in response_data if sub["name"] == "Оптимум"][0]

    assert response.status_code == 200, "Ошибка при получении подписок"
    assert trial["active"] is True, "Пробная должна быть активной"
    assert trial["available"] is False, "Пробная должна быть недоступной"
    assert optimum["active"] is False, "Оптимум должна быть неактивной"
    assert optimum["available"] is False, "Оптимум должна быть недоступной"


@pytest.mark.usefixtures("trying_sub", "optimum_sub")
def test_check_active_available_sub_with_overdue_trial_sub(api_auth_with_overdue_sub_client: APIClient):
    """Активна пробная, просрочена."""
    get_url = reverse("view-subscriptions")
    response = api_auth_with_overdue_sub_client.get(get_url)
    response_data: list[dict] = response.json()
    trial = [sub for sub in response_data if sub["name"] == "Пробная"][0]
    optimum = [sub for sub in response_data if sub["name"] == "Оптимум"][0]

    assert response.status_code == 200, "Ошибка при получении подписок"
    assert trial["active"] is False, "Пробная должна быть  неактивной"
    assert trial["available"] is False, "Пробная должна быть недоступной"
    assert optimum["active"] is False, "Оптимум должна быть неактивной"
    assert optimum["available"] is True, "Оптимум должна быть доступной"


@pytest.mark.usefixtures("trying_sub", "optimum_sub")
def test_check_active_available_sub_with_optimum_sub(api_auth_with_optimum_sub_client: APIClient):
    """Активна оптимум, НЕ просрочена (пробная покупалась)."""
    get_url = reverse("view-subscriptions")
    response = api_auth_with_optimum_sub_client.get(get_url)
    response_data: list[dict] = response.json()
    trial = [sub for sub in response_data if sub["name"] == "Пробная"][0]
    optimum = [sub for sub in response_data if sub["name"] == "Оптимум"][0]

    assert response.status_code == 200, "Ошибка при получении подписок"
    assert trial["active"] is False, "Пробная должна быть  неактивной"
    assert trial["available"] is False, "Пробная должна быть недоступной"
    assert optimum["active"] is True, "Оптимум должна быть активной"
    assert optimum["available"] is False, "Оптимум должна быть недоступной"


@pytest.mark.usefixtures("trying_sub", "optimum_sub")
def test_check_active_available_sub_with_overdue_optimum_sub(api_auth_with_overdue_optimum_sub_client: APIClient):
    """Активна оптимум, просрочена (пробная покупалась)."""
    get_url = reverse("view-subscriptions")
    response = api_auth_with_overdue_optimum_sub_client.get(get_url)
    response_data: list[dict] = response.json()
    trial = [sub for sub in response_data if sub["name"] == "Пробная"][0]
    optimum = [sub for sub in response_data if sub["name"] == "Оптимум"][0]

    assert response.status_code == 200, "Ошибка при получении подписок"
    assert trial["active"] is False, "Пробная должна быть неактивной"
    assert trial["available"] is False, "Пробная должна быть недоступной"
    assert optimum["active"] is False, "Оптимум должна быть неактивной"
    assert optimum["available"] is True, "Оптимум должна быть доступной"
