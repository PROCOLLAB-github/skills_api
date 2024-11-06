from datetime import datetime, timedelta
from unittest.mock import patch

import pytest
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q, Count
from django.utils import timezone
from model_bakery import baker

from courses.models import TaskObject, Skill, Task
from progress.mapping import AdditionalPoints
from progress.models import CustomUser, UserProfile, TaskObjUserResult, UserSkillDone
from progress.serializers import CustomObtainPairSerializer
from questions.mapping import TypeQuestionPoints
from questions.models import AnswerSingle, QuestionSingleAnswer


@pytest.fixture
def user_with_subscription_token() -> str:
    user = baker.make("progress.CustomUser")

    profile = user.profiles
    profile.last_subscription_date = timezone.now()
    profile.save()

    return str(CustomObtainPairSerializer.get_token(user))







@pytest.fixture
def question_data() -> None:
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
def question_data_answered(question_data, user_with_trial_sub_token):
    with patch("progress.tasks.check_skill_done.delay"):
        with patch("progress.tasks.check_week_stat.delay"):
            TaskObjUserResult.objects.create_user_result(
                task_obj_id=1,
                user_profile_id=1,
                type_task_obj=TypeQuestionPoints.QUESTION_SINGLE_ANSWER,
            )

            return user_with_trial_sub_token
