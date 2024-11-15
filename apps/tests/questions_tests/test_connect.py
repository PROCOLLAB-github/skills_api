import pytest
from django.urls import reverse

get_url = reverse("connect-question-get", kwargs={"task_obj_id": 1})


@pytest.mark.usefixtures("connect_question_data", "user_with_trial_sub_token")
def test_connect_not_answered_should_succeed(client, connect_question_data, user_with_trial_sub_token: str) -> None:
    headers = {"Authorization": f"Bearer {user_with_trial_sub_token}"}

    response = client.get(get_url, headers=headers)
    response_data = response.json()

    assert response.status_code == 200

    assert len(response_data["connect_left"]) == 2
    assert response_data["is_answered"] is False


@pytest.mark.usefixtures("connect_question_data_answered")
def test_connect_answered_should_succeed(client, connect_question_data_answered: str) -> None:
    headers = {"Authorization": f"Bearer {connect_question_data_answered}"}

    response = client.get(get_url, headers=headers)
    response_data = response.json()

    assert response.status_code == 200
    assert len(response_data["connect_left"]) == 2
    assert response_data["is_answered"] is True

    for left, right in zip(response_data["connect_left"], response_data["connect_right"]):
        assert left["id"] == right["id"], "порядок вопросов нарушен"
