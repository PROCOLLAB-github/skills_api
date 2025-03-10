import pytest
from django.contrib.contenttypes.models import ContentType
from django.test import override_settings

from courses.models import TaskObject
from progress.models import TaskObjUserResult
from questions.mapping import TypeQuestionPoints
from questions.models import QuestionWrite


@pytest.fixture
def write_question_data(task_wo_questions) -> TaskObject:
    """Вопрос из ПЛАТНОГО навыка."""
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
def free_write_question_data(free_task_wo_questions) -> TaskObject:
    """Вопрос из БЕСПЛАТНОГО навыка."""
    question = QuestionWrite(
        text="123",
    )
    question.save()

    task_obj = TaskObject(
        task=free_task_wo_questions,
        content_type=ContentType.objects.get_for_model(QuestionWrite),
        object_id=1,
    )
    task_obj.save()
    return task_obj


@pytest.fixture
@override_settings(task_always_eager=True)
def write_question_data_answered(write_question_data, user):
    TaskObjUserResult.objects.create_user_result(
        task_obj_id=write_question_data.id,
        user_profile_id=user.id,
        type_task_obj=TypeQuestionPoints.QUESTION_WRITE,
    )
    a = TaskObjUserResult.objects.get(id=1)
    a.text = "sigma"
    a.save()
