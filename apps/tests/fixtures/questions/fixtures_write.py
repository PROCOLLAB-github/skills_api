import pytest
from django.test import override_settings
from django.contrib.contenttypes.models import ContentType

from courses.models import TaskObject
from progress.models import TaskObjUserResult
from questions.mapping import TypeQuestionPoints
from questions.models import QuestionWrite


@pytest.fixture
def write_question_data(task_wo_questions) -> TaskObject:
    question = QuestionWrite(
        text="123",
    )
    question.save()

    task_obj = TaskObject(
        task=task_wo_questions,
        content_type=ContentType.objects.get_for_model(QuestionWrite),
        object_id=1,
    )
    task_obj.save()
    return task_obj


@pytest.fixture
def write_question_data_answered(write_question_data: QuestionWrite, user_with_trial_sub_token):
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

            return user_with_trial_sub_token

