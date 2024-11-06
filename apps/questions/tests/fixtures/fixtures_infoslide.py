from unittest.mock import patch

import pytest
from django.contrib.contenttypes.models import ContentType

from courses.models import Task, Skill, TaskObject
from progress.models import TaskObjUserResult
from questions.mapping import TypeQuestionPoints
from questions.models import InfoSlide


@pytest.fixture
def info_question_data() -> None:
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

    slide = InfoSlide(text="123")
    slide.save()

    task_obj = TaskObject(
        task=task,
        content_type=ContentType.objects.get_for_model(InfoSlide),
        object_id=1,

    )
    task_obj.save()


@pytest.fixture
def info_question_answered_data(info_question_data, user_with_trial_sub):
    with patch("progress.tasks.check_skill_done.delay"):
        with patch("progress.tasks.check_week_stat.delay"):
            TaskObjUserResult.objects.create_user_result(
                task_obj_id=1,
                user_profile_id=1,
                type_task_obj=TypeQuestionPoints.INFO_SLIDE,
            )

            return user_with_trial_sub
