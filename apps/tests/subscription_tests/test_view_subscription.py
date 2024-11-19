import pytest
from django.urls import reverse
from rest_framework.test import APIClient


@pytest.mark.usefixtures("trying_sub")
def test_get_trying_subscription_should_succeed(api_auth_without_sub_client: APIClient):
    get_url = reverse("view-subscriptions")

    response = api_auth_without_sub_client.get(get_url)
    response_data: dict = response.json()

    assert response.status_code == 200, "Ошибка при получении подписки"
    assert response_data.get("name") == "Пробная", "Выдаётся не тот тип подписки"
    assert response_data.get("price") == 1, "Выдаётся не тот тип подписки"


@pytest.mark.usefixtures("optimum_sub")
def test_get_optimum_subscription_should_succeed(api_auth_with_sub_client: APIClient):
    get_url = reverse("view-subscriptions")
    response = api_auth_with_sub_client.get(get_url)
    response_data: dict = response.json()

    assert response.status_code == 200, "Ошибка при получении подписки"
    assert response_data.get("name") == "Оптимум", "Ошибка при получении подписки"
    assert response_data.get("price") == 120, "Выдаётся не тот тип подписки"
