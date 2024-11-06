import pytest
from django.urls import reverse

from questions.tests.fixtures.common import user_with_trial_sub
from questions.tests.fixtures.fixtures_exlude import exclude_question_data, exclude_question_data_answered
get_url = reverse("exclude-question-get", kwargs={'task_obj_id': 1})

@pytest.mark.django_db
def test_exclude_not_answered_should_succeed(client, user_with_trial_sub, exclude_question_data) -> None:
    headers = {"Authorization": f"Bearer {user_with_trial_sub}"}

    response = client.get(get_url, headers=headers)
    response_data = response.json()

    assert response.status_code == 200
    assert response_data["is_answered"] is False, "Почему-то на вопрос уже ответили, странно, такого быть не должно"
    assert len(response_data["answers"]) > 1, "Почему-то выдало всего один ответ. Должно больше"

@pytest.mark.django_db
def test_exclude_answered_should_succeed(client, exclude_question_data_answered) -> None:
    headers = {"Authorization": f"Bearer {exclude_question_data_answered}"}

    response = client.get(get_url, headers=headers)
    response_data = response.json()

    assert response.status_code == 200
    assert response_data["is_answered"] is True, "Почему-то вопрос не помечен как отвеченый"
    assert len(response_data["answers"]) == 1, "Почему-то выдало больше одного ответа"








