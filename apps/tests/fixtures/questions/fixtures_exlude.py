import pytest
from django.test import override_settings
from django.contrib.contenttypes.models import ContentType

from courses.models import TaskObject
from progress.models import TaskObjUserResult
from questions.mapping import TypeQuestionPoints
from questions.models import QuestionSingleAnswer, AnswerSingle


@pytest.fixture
def exclude_question_data(task_wo_questions) -> TaskObject:
    question = QuestionSingleAnswer(text="123", is_exclude=True)
    question.save()

    answer = AnswerSingle(text="asd", is_correct=True, question=question)
    answer.save()

    answer1 = AnswerSingle(text="asd2", is_correct=False, question=question)
    answer1.save()

    answer2 = AnswerSingle(text="asd1", is_correct=False, question=question)
    answer2.save()

    task_obj = TaskObject(
        task=task_wo_questions,
        content_type=ContentType.objects.get_for_model(QuestionSingleAnswer),
        object_id=1,
    )
    task_obj.save()
    return task_obj


@pytest.fixture
@override_settings(task_always_eager=True)
def exclude_question_data_answered(exclude_question_data, user):
    TaskObjUserResult.objects.create_user_result(
        task_obj_id=exclude_question_data.id,
        user_profile_id=user.id,
        type_task_obj=TypeQuestionPoints.QUESTION_EXCLUDE,
    )
