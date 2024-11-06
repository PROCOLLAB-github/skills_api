import pytest
from django.urls import reverse

from courses.models import TaskObject, Task, Skill
from questions.tests.fixtures.fixtures_single import user_with_subscription_token, question_data,  question_data_answered
from questions.tests.fixtures.common import user_with_trial_sub


get_url = reverse("single-correct-get", kwargs={'task_obj_id': 1})




@pytest.mark.django_db
def test_single_not_answered_should_succeed(client, question_data, user_with_trial_sub: str) -> None:
    headers = {"Authorization": f"Bearer {user_with_trial_sub}"}

    response = client.get(get_url, headers=headers)
    response_data = response.json()

    assert response.status_code == 200
    assert response_data["is_answered"] is False, "Почему-то на вопрос уже ответили, странно, такого быть не должно"
    assert len(response_data["answers"]) > 1, "Почему-то выдало всего один правильный ответ. Должно больше"


@pytest.mark.django_db
def test_single_answered_should_succeed(client, question_data_answered: str) -> None:
    headers = {"Authorization": f"Bearer {question_data_answered}"}

    response = client.get(get_url, headers=headers)
    response_class = response.json()

    assert response.status_code == 200
    assert response_class["is_answered"] is True, "Почему-то на вопрос не ответили, странно, такого быть не должно"
    assert len(response_class["answers"]) == 1, "Почему-то выдало больше одного правильного ответа"
