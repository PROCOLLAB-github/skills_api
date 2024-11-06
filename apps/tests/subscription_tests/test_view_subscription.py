import pytest
from django.urls import reverse

from progress.serializers import CustomObtainPairSerializer


@pytest.mark.usefixtures("trying_sub")
def test_get_trying_subscription_should_succeed(client, user) -> None:
    get_url = reverse("view-subscriptions")
    token = CustomObtainPairSerializer.get_token(user)
    headers = {"Authorization": f"Bearer {str(token)}"}
    response = client.get(
        get_url,
        headers=headers
    )
    response_data: dict = response.json()

    assert response.status_code == 200, "Ошибка при получении подписки"
    assert response_data.get("name") == "Пробная", "Выдаётся не тот тип подписки"
    assert response_data.get("price") == 1, "Выдаётся не тот тип подписки"


@pytest.mark.skip("TODO надо поправить, теперь другой тип подписки какой-то")
@pytest.mark.usefixtures("optimum_sub")
def test_get_optimum_subscription_should_succeed(client, user_with_trial_sub, optimum_sub) -> None:
    get_url = reverse("view-subscriptions")
    token = CustomObtainPairSerializer.get_token(user_with_trial_sub)
    headers = {"Authorization": f"Bearer {str(token)}"}
    response = client.get(
        get_url,
        headers=headers
    )
    response_data: dict = response.json()

    assert response.status_code == 200, "Ошибка при получении подписки"
    assert response_data.get("name") == "Оптимум", "Ошибка при получении подписки"
    assert response_data.get("price") == 120, "Выдаётся не тот тип подписки"
