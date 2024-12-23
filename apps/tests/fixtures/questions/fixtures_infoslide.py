import pytest
from django.test import override_settings
from django.contrib.contenttypes.models import ContentType

from courses.models import TaskObject
from progress.models import TaskObjUserResult
from questions.mapping import TypeQuestionPoints
from questions.models import InfoSlide


@pytest.fixture
def info_question_data(task_wo_questions) -> TaskObject:
    """Вопрос из ПЛАТНОГО навыка."""
    slide = InfoSlide(text="123")
    slide.save()

    task_obj = TaskObject(
        task=task_wo_questions,
        content_type=ContentType.objects.get_for_model(InfoSlide),
        object_id=1,
    )
    task_obj.save()
    return task_obj


@pytest.fixture
def free_info_question_data(free_task_wo_questions) -> TaskObject:
    """Вопрос из БЕСПЛАТНОГО навыка."""
    slide = InfoSlide(text="123")
    slide.save()

    task_obj = TaskObject(
        task=free_task_wo_questions,
        content_type=ContentType.objects.get_for_model(InfoSlide),
        object_id=1,
    )
    task_obj.save()
    return task_obj


@pytest.fixture
@override_settings(task_always_eager=True)
def info_question_answered_data(info_question_data, user):
    TaskObjUserResult.objects.create_user_result(
        task_obj_id=info_question_data.id,
        user_profile_id=user.profiles.id,
        type_task_obj=TypeQuestionPoints.INFO_SLIDE,
    )
