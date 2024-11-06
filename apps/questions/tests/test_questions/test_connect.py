import pytest
from django.urls import reverse

from courses.models import TaskObject, Task, Skill
from questions.tests.fixtures.fixture_connect import connect_question_data,  connect_question_data_answered
from questions.tests.fixtures.common import user_with_trial_sub


get_url = reverse("connect-question-get", kwargs={'task_obj_id': 1})




@pytest.mark.django_db
def test_connect_not_answered_should_succeed(client, connect_question_data, user_with_trial_sub: str) -> None:
    headers = {"Authorization": f"Bearer {user_with_trial_sub}"}

    response = client.get(get_url, headers=headers)
    response_data = response.json()

    assert response.status_code == 200

    assert len(response_data["connect_left"]) == 2
    assert response_data["is_answered"] is False

@pytest.mark.django_db
def test_connect_answered_should_succeed(client, connect_question_data_answered: str) -> None:
    headers = {"Authorization": f"Bearer {connect_question_data_answered}"}

    response = client.get(get_url, headers=headers)
    response_data = response.json()

    assert response.status_code == 200
    assert len(response_data["connect_left"]) == 2
    assert response_data["is_answered"] is True

    for left, right in zip(response_data["connect_left"], response_data["connect_right"]):
        assert left["id"] == right["id"], "порядок вопросов нарушен"
