import pytest
from django.contrib.contenttypes.models import ContentType
from django.test import override_settings

from courses.models import TaskObject
from progress.models import TaskObjUserResult
from questions.mapping import TypeQuestionPoints
from questions.models import AnswerConnect, QuestionConnect


@pytest.fixture
def connect_question_data(task_wo_questions) -> TaskObject:
    """Вопрос из ПЛАТНОГО навыка."""
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
        task=task_wo_questions,
        content_type=ContentType.objects.get_for_model(QuestionConnect),
        object_id=1,
    )
    task_obj.save()
    return task_obj


@pytest.fixture
def free_connect_question_data(free_task_wo_questions) -> TaskObject:
    """Вопрос из БЕСПЛАТНОГО навыка."""
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
        task=free_task_wo_questions,
        content_type=ContentType.objects.get_for_model(QuestionConnect),
        object_id=1,
    )
    task_obj.save()
    return task_obj


@pytest.fixture
def connect_question_data_with_hint(task_wo_questions) -> TaskObject:
    """Вопрос из ПЛАТНОГО навыка с подсказкой."""
    question = QuestionConnect(
        text="123",
        hint_text="Подсказка",
        attempts_before_hint=2,
        attempts_after_hint=2,
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
        task=task_wo_questions,
        content_type=ContentType.objects.get_for_model(QuestionConnect),
        object_id=1,
    )
    task_obj.save()
    return task_obj


@pytest.fixture
@override_settings(task_always_eager=True)
def connect_question_data_answered(connect_question_data, user):
    TaskObjUserResult.objects.create_user_result(
        task_obj_id=connect_question_data.id,
        user_profile_id=user.profiles.id,
        type_task_obj=TypeQuestionPoints.QUESTION_CONNECT,
    )
