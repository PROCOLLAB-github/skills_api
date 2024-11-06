import pytest
from django.urls import reverse

get_url = reverse("info-slide-get", kwargs={'task_obj_id': 1})


@pytest.mark.usefixtures("user_with_trial_sub_token", "info_question_data")
def test_infoslide_not_answered_should_succeed(client, user_with_trial_sub_token, info_question_data) -> None:
    headers = {"Authorization": f"Bearer {user_with_trial_sub_token}"}

    response = client.get(get_url, headers=headers)
    response_data = response.json()

    assert response.status_code == 200
    assert response_data["text"] == "123", "почему-то текст не такой, какой задан в текстуре"
    assert response_data["is_done"] is False, "почему-то задание сделано"


@pytest.mark.usefixtures("info_question_answered_data")
def test_infoslide_answered_should_succeed(client, info_question_answered_data: str) -> None:
    headers = {"Authorization": f"Bearer {info_question_answered_data}"}

    response = client.get(get_url, headers=headers)
    response_data = response.json()

    assert response.status_code == 200
    assert response_data["text"] == "123", "почему-то текст не такой, какой задан в текстуре"
    assert response_data["is_done"] is True, "почему-то задание не сделано"
