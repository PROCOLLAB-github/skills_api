from unittest.mock import patch

import pytest
from django.contrib.contenttypes.models import ContentType

from courses.models import Skill, Task, TaskObject
from progress.models import TaskObjUserResult
from questions.mapping import TypeQuestionPoints
from questions.models import QuestionWrite, AnswerUserWrite
from questions.typing import AnswerUserWriteData


@pytest.fixture
def write_question_data() -> QuestionWrite:
    skill = Skill(
        name="asd",
        who_created="123",
        status="published"
    )
    skill.save()

    task = Task(
        name="asd",
        skill=skill,
        status="published"

    )
    task.save()

    question = QuestionWrite(
        text="123",

    )
    question.save()

    task_obj = TaskObject(
        task=task,
        content_type=ContentType.objects.get_for_model(QuestionWrite),
        object_id=1,

    )
    task_obj.save()
    return question


@pytest.fixture
def write_question_data_answered(write_question_data: QuestionWrite, user_with_trial_sub):
    with patch("progress.tasks.check_skill_done.delay"):
        with patch("progress.tasks.check_week_stat.delay"):

            TaskObjUserResult.objects.create_user_result(
                task_obj_id=1,
                user_profile_id=1,
                type_task_obj=TypeQuestionPoints.QUESTION_WRITE,
            )
            a = TaskObjUserResult.objects.get(id=1)
            a.text = "sigma"
            a.save()

            return user_with_trial_sub