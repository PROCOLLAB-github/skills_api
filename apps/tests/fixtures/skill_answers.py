from datetime import timedelta

import pytest
from unittest.mock import patch
from django.test import override_settings
from django.utils import timezone

from courses.models import Skill
from progress.models import (
    TaskObjUserResult,
    CustomUser,
)


@pytest.fixture
@override_settings(task_always_eager=True)
def skill_three_users_answers(
    full_filled_published_skill: Skill,
    user_with_trial_sub: CustomUser,
    user_staff_with_trial_sub: CustomUser,
    user_admin_with_trial_sub: CustomUser,
):
    """
    Для рейтинга, где 3 пользователя ответили на соотв. TaskObj
    - Дефолт юзер: 1 задание -> 5 баллов
    - Стафф: 2 задания -> 10 баллов
    - Админ: 3 задания -> 15 баллов 
    Функционал аналогичен для каждого типа пользователей, просто, чтбы не плодить 
    сущности, взяты готовые стафф и админ.
    Замоканы доп баллы за месяц.
    """
    with patch("progress.tasks.check_week_stat.delay"):
        for task_obj_idx in range(1, 4):
            TaskObjUserResult.objects.create(
                task_object_id=task_obj_idx,
                user_profile=user_admin_with_trial_sub.profiles,
                points_gained=5
            )
        for task_obj_idx in range(1, 3):
            TaskObjUserResult.objects.create(
                task_object_id=task_obj_idx,
                user_profile=user_staff_with_trial_sub.profiles,
                points_gained=5
            )

        TaskObjUserResult.objects.create(
            task_object_id=1,
            user_profile=user_with_trial_sub.profiles,
            points_gained=5
        )


@pytest.fixture
@override_settings(task_always_eager=True)
def skill_three_users_some_old_answers(
    full_filled_published_skill: Skill,
    user_with_trial_sub: CustomUser,
    user_staff_with_trial_sub: CustomUser,
    user_admin_with_trial_sub: CustomUser,
):
    """
    Для рейтинга (разные таймлайн), где 3 пользователя ответили на соотв. TaskObj
    - Админ: делал задания более месяца назад (но в этом году) 
    - Стафф: делал в прошлом месяце
    - Юзер: делал день в день
    Функционал аналогичен для каждого типа пользователей, просто, чтобы не плодить 
    сущности, взяты готовые стафф и админ.
    Замоканы доп баллы за месяц.
    """
    with patch("progress.tasks.check_week_stat.delay"):
        for task_obj_idx in range(1, 4):
            TaskObjUserResult.objects.create(
                task_object_id=task_obj_idx,
                user_profile=user_admin_with_trial_sub.profiles,
                points_gained=5,
                datetime_created=timezone.now() - timedelta(days=32)

            )
        for task_obj_idx in range(1, 3):
            TaskObjUserResult.objects.create(
                task_object_id=task_obj_idx,
                user_profile=user_staff_with_trial_sub.profiles,
                points_gained=5,
                datetime_created=timezone.now() - timedelta(days=2)
            )

        TaskObjUserResult.objects.create(
            task_object_id=1,
            user_profile=user_with_trial_sub.profiles,
            points_gained=5
        )
