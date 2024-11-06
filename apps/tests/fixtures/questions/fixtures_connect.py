from unittest.mock import patch

import pytest
from django.contrib.contenttypes.models import ContentType

from courses.models import Skill, Task, TaskObject
from progress.models import TaskObjUserResult
from questions.mapping import TypeQuestionPoints
from questions.models import QuestionConnect, AnswerConnect


@pytest.fixture
def connect_question_data() -> None:
    skill = Skill(name="asd", who_created="123", status="published")
    skill.save()

    task = Task(name="asd", skill=skill, status="published")
    task.save()

    question = QuestionConnect(
        text="123",
    )
    question.save()

    answer1 = AnswerConnect(
        connect_left="left1", connect_right="right1", question=question
    )
    answer2 = AnswerConnect(
        connect_left="left2", connect_right="right2", question=question
    )
    answer1.save()
    answer2.save()

    task_obj = TaskObject(
        task=task,
        content_type=ContentType.objects.get_for_model(QuestionConnect),
        object_id=1,
    )
    task_obj.save()


@pytest.fixture
def connect_question_data_answered(connect_question_data, user_with_trial_sub_token):
    with patch("progress.tasks.check_skill_done.delay"):
        with patch("progress.tasks.check_week_stat.delay"):
            TaskObjUserResult.objects.create_user_result(
                task_obj_id=1,
                user_profile_id=1,
                type_task_obj=TypeQuestionPoints.QUESTION_CONNECT,
            )

            return user_with_trial_sub_token
