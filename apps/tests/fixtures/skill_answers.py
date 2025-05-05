from datetime import timedelta
from unittest.mock import patch

import pytest
from django.test import override_settings
from django.utils import timezone

from courses.models import Skill
from progress.models import CustomUser, TaskObjUserResult


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
    Замоканы доп баллы за месяц.
    """
    with patch("progress.tasks.check_week_stat.delay"):
        for task_obj_idx in range(1, 4):
            TaskObjUserResult.objects.create(
                task_object_id=task_obj_idx,
                user_profile=user_admin_with_trial_sub.profiles,
                points_gained=20
            )
        for task_obj_idx in range(1, 3):
            TaskObjUserResult.objects.create(
                task_object_id=task_obj_idx,
                user_profile=user_staff_with_trial_sub.profiles,
                points_gained=20
            )

        TaskObjUserResult.objects.create(
            task_object_id=1,
            user_profile=user_with_trial_sub.profiles,
            points_gained=20
        )


@pytest.fixture
@override_settings(task_always_eager=True)
def skill_three_users_some_old_answers(
    full_filled_published_skill: Skill,
    three_random_user_with_sub: list[CustomUser, CustomUser, CustomUser],
):
    """
    Для рейтинга (разные таймлайн), где 3 пользователя ответили на соотв. TaskObj
    - Юзер1: делал задания более месяца назад (но в этом году) 
    - Юзер2: делал в прошлом месяце
    - Юзер3: делал день в день
    Замоканы доп баллы за месяц.
    """
    user1, user2, user3 = three_random_user_with_sub

    with patch("progress.tasks.check_week_stat.delay"):
        for task_obj_idx in range(1, 4):
            TaskObjUserResult.objects.create(
                task_object_id=task_obj_idx,
                user_profile=user1.profiles,
                points_gained=5,
                datetime_created=timezone.now() - timedelta(days=32)

            )
        for task_obj_idx in range(1, 3):
            TaskObjUserResult.objects.create(
                task_object_id=task_obj_idx,
                user_profile=user2.profiles,
                points_gained=5,
                datetime_created=timezone.now() - timedelta(days=2)
            )

        TaskObjUserResult.objects.create(
            task_object_id=1,
            user_profile=user3.profiles,
            points_gained=5
        )
