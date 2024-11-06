from unittest.mock import patch

import pytest
from django.contrib.contenttypes.models import ContentType

from courses.models import Skill, Task, TaskObject
from progress.models import TaskObjUserResult
from questions.mapping import TypeQuestionPoints
from questions.models import QuestionSingleAnswer, AnswerSingle


@pytest.fixture
def exclude_question_data() -> None:
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

    question = QuestionSingleAnswer(
        text="123",
        is_exclude=True
    )
    question.save()

    answer = AnswerSingle(
        text="asd",
        is_correct=True,
        question=question
    )
    answer.save()

    answer1 = AnswerSingle(
        text="asd2",
        is_correct=False,
        question=question
    )
    answer1.save()

    answer2 = AnswerSingle(
        text="asd1",
        is_correct=False,
        question=question
    )
    answer2.save()

    task_obj = TaskObject(
        task=task,
        content_type=ContentType.objects.get_for_model(QuestionSingleAnswer),
        object_id=1,

    )
    task_obj.save()


@pytest.fixture
def exclude_question_data_answered(exclude_question_data, user_with_trial_sub):
    with patch("progress.tasks.check_skill_done.delay"):
        with patch("progress.tasks.check_week_stat.delay"):
            TaskObjUserResult.objects.create_user_result(
                task_obj_id=1,
                user_profile_id=1,
                type_task_obj=TypeQuestionPoints.QUESTION_EXCLUDE,
            )

            return user_with_trial_sub
