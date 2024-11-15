import pytest
from django.urls import reverse

get_url = reverse("exclude-question-get", kwargs={"task_obj_id": 1})


@pytest.mark.usefixtures("user_with_trial_sub_token", "exclude_question_data")
def test_exclude_not_answered_should_succeed(client, user_with_trial_sub_token, exclude_question_data) -> None:
    headers = {"Authorization": f"Bearer {user_with_trial_sub_token}"}

    response = client.get(get_url, headers=headers)
    response_data = response.json()

    assert response.status_code == 200
    assert response_data["is_answered"] is False, "Почему-то на вопрос уже ответили, странно, такого быть не должно"
    assert len(response_data["answers"]) > 1, "Почему-то выдало всего один ответ. Должно больше"


@pytest.mark.usefixtures("exclude_question_data_answered")
def test_exclude_answered_should_succeed(client, exclude_question_data_answered) -> None:
    headers = {"Authorization": f"Bearer {exclude_question_data_answered}"}

    response = client.get(get_url, headers=headers)
    response_data = response.json()

    assert response.status_code == 200
    assert response_data["is_answered"] is True, "Почему-то вопрос не помечен как отвеченый"
    assert len(response_data["answers"]) == 1, "Почему-то выдало больше одного ответа"
