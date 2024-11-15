import pytest
from django.urls import reverse

get_url = reverse("write-question-get", kwargs={"task_obj_id": 1})


@pytest.mark.usefixtures("write_question_data", "user_with_trial_sub_token")
def test_write_not_answered_should_succeed(client, user_with_trial_sub_token: str, write_question_data) -> None:
    headers = {"Authorization": f"Bearer {user_with_trial_sub_token}"}

    response = client.get(get_url, headers=headers)
    response_data = response.json()

    assert response.status_code == 200
    assert response_data["text"] == "123", "почему-то текст не такой, какой задан в текстуре"
    assert response_data["answer"] is None, "почему-то ответ уже есть, быть не должен"


@pytest.mark.usefixtures("write_question_data_answered")
def test_write_answered_should_succeed(client, write_question_data_answered: str) -> None:
    headers = {"Authorization": f"Bearer {write_question_data_answered}"}

    response = client.get(get_url, headers=headers)
    response_data = response.json()

    assert response.status_code == 200
    assert response_data["text"] == "123", "почему-то текст не такой, какой задан в текстуре"
    assert response_data["answer"]["text"] == "sigma", "почему-то задание не сделано"
