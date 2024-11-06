import pytest
from django.urls import reverse


get_url = reverse("single-correct-get", kwargs={"task_obj_id": 1})


@pytest.mark.usefixtures("user_token")
def test_single_not_answered_should_succeed(client, user_token: str) -> None:
    headers = {"Authorization": f"Bearer {user_token}"}

    response = client.get(get_url, headers=headers)
    response_data = response.json()

    assert response.status_code == 403, "почему-то статус код не тот"
    assert (
        response_data["detail"] == "Подписка просрочена."
    ), "Почему-то на вопрос уже ответили, странно, такого быть не должно"
