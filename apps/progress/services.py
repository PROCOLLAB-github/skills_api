import datetime
import math
from decimal import Decimal, ROUND_HALF_UP

from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db.models import Count, Q, QuerySet, Sum

from progress.mapping import MonthMapping
from courses.models import Skill
from progress.typing import (
    UserProfileDataDict,
    UserSkillsProgressDict,
    UserMonthsProgressDict,
    PreparatoryUserMonthsProgressDict,
)
from progress.models import (
    CustomUser,
    UserMonthStat,
    UserProfile,
    UserWeekStat,
    UserSkillDone,
    TaskObjUserResult,
)

User = get_user_model()


def get_user_data(profile_id: int) -> UserProfileDataDict:
    """
    Информация о юзере для профиля:
        Общие перснальные данные.
        Баллы (`points`).
    """
    user_profile = UserProfile.objects.select_related("user", "file").get(id=profile_id)
    user = user_profile.user

    years_passed = None
    if user.age:
        current_date = datetime.datetime.now()
        time_difference = current_date.date() - user.age
        years_passed = time_difference.days // 365

    return {
        "first_name": user.first_name,
        "last_name": user.last_name,
        "file_link": user_profile.file.link if user_profile.file else None,
        "specialization": user.specialization,
        "age": years_passed,
        "geo_position": user.city,
        "points": get_user_points(profile_id),
    }


def get_user_profile_skills_progress(
    user_profile_id: int,
    request_user: CustomUser | None = None,
) -> list[UserSkillsProgressDict]:
    """
    Статистика по навыкам пользователя с % прогресса для профиля. 
    """
    # TODO Fix учесть, когда будет выбор только 5 навыков для юзера.
    _, user_skills_ids = get_user_skills(user_profile_id)
    task_status_filter = DBObjectStatusFilters().get_many_tasks_status_filter_for_user(request_user)
    skills_stats: QuerySet[Skill] = (
        Skill.published
        .for_user(request_user)
        .filter(id__in=user_skills_ids)
        .annotate(
                # Общее кол-во опубликованных вопросов навыка.
                total_num_questions=Count("tasks__task_objects", filter=task_status_filter),
                # Общее кол-во ответов юзера на опубликованные вопросы в рамках навыка.
                total_user_answers=Count(
                    "tasks__task_objects__user_results",
                    filter=(Q(tasks__task_objects__user_results__user_profile_id=user_profile_id)
                            & task_status_filter),
                ),
            )
    )
    stats_data: list[UserSkillsProgressDict] = [
        {
            "skill_id": skill.id,
            "skill_name": skill.name,
            "skill_level": 1,  # TODO Fix захардкоженный уровень, пока не понятно что за уровни навыка.
            "skill_progress": get_rounded_percentage(skill.total_user_answers, skill.total_num_questions),
            "file_link": skill.file.link if skill.file else None,
        }
        for skill in skills_stats
    ]
    return stats_data


def get_user_profile_months_stats(user_profile_id: int) -> list[UserMonthsProgressDict]:
    """Статистика по месяцам для пользователя для текущего года."""
    now_year: int = timezone.now().year
    months_data: list[PreparatoryUserMonthsProgressDict] = (
        UserMonthStat.objects
        .filter(user_profile__id=user_profile_id, year=now_year)
        .values("month", "year", "successfully_done")
    )
    # Словари пересобирается через маппинг, чтобы вернуть `str` месяц.
    months_stats: list[UserMonthsProgressDict] = [
        {
            "month": MonthMapping.get(stat["month"]),
            "year": stat["year"],
            "successfully_done": stat["successfully_done"]
        }
        for stat in months_data
    ]
    return months_stats


def get_user_skills(user_profile_id: int) -> tuple[QuerySet[Skill], QuerySet]:
    """Получение всех навыков и их id для конкретного пользователя."""
    user = UserProfile.objects.get(id=user_profile_id).user
    user_skills: QuerySet[Skill] = (
        Skill.published
        .for_user(user)
        .filter(
            Q(intermediateuserskills__user_profile__id=user_profile_id)
            | Q(tasks__task_objects__user_results__user_profile__id=user_profile_id),
        )
        .distinct()
    )
    user_skills_ids: QuerySet = user_skills.values_list("id", flat=True)
    return user_skills, user_skills_ids


def get_user_available_week(profile_id: int) -> tuple[int, CustomUser]:
    """
    Получение доступных пользователю недель, все что <= `available_week` доступно.
    Если подписка вообще не оформлена, то -> 0, соотв. ничего не доступно.
    Для `superuser` и `staff` доступно все (4 недели).
    Пример запроса для Task:
        `Q(week__lte=available_week)`
    """
    user_profile = UserProfile.objects.select_related("user").get(pk=profile_id)

    if user_profile.user.is_superuser or user_profile.user.is_staff:
        return 4, user_profile.user

    subscription_date: datetime = user_profile.last_subscription_date

    if subscription_date:
        current_date: datetime = timezone.now().date()
        # Если подписка была сегодня то прошло дней 0, сооотв -> 1.
        days_since_subscription: datetime.timedelta = (current_date - subscription_date).days or 1
        # Дробный результат преобразуется в бОльшую часть, пример: 2.1 -> 3
        # (т.е. как началась 3 неделя, чтобы она была включительно)
        available_week: int = math.ceil(days_since_subscription / 7)
        return available_week, user_profile.user
    return 0, user_profile.user


def get_user_points(profile_id: int) -> int:
    """Собирает поинты пользователя по всем сущностям."""

    # TODO подумать можно ли это упростить, обратный вызов через `related_name`, distinct, annotate и Sum
    # дублирует строки и стата перемножается.
    skill_done_points: int = (
        UserSkillDone.objects
        .filter(user_profile__id=profile_id)
        .aggregate(points=Sum("additional_points"))
    )["points"] or 0

    week_done_points: int = (
        UserWeekStat.objects
        .filter(user_profile__id=profile_id)
        .aggregate(points=Sum("additional_points"))
    )["points"] or 0

    task_objects_pounts: int = (
        TaskObjUserResult.objects
        .filter(user_profile__id=profile_id)
        .aggregate(points=Sum("points_gained"))
    )["points"] or 0

    return skill_done_points + week_done_points + task_objects_pounts


def get_rounded_percentage(dividend: int, divisor: int) -> int:
    """
    Принимает делитель и делимое, возврщает округленное процентное соотношение.
    Если делитель/делимое == `0` -> вернет просто `0` без выброса исключения.
    """
    if divisor == 0 or dividend == 0:
        return 0
    percentage: Decimal = Decimal(str((dividend / divisor) * 100))
    rounded_percentage: int = int(percentage.quantize(Decimal("1"), rounding=ROUND_HALF_UP))
    return rounded_percentage


class DBObjectStatusFilters:
    """
    Икапсуляция логики получения фильтра для подзапросов, отображение определенным ролям:
        - Все объекты для `superuser`,
        - Объекты со статусом `published` и `stuff_only` для `staff`,
        - Только опубликованные объекты для остальных.
    Инстансы для фильтрации:
        - Skill
        - Task
    """

    @staticmethod
    def get_many_tasks_status_filter_for_user(user: CustomUser):
        task_filter = Q(tasks__status="published")
        if user and user.is_superuser:
            task_filter = Q()
        elif user and user.is_staff:
            task_filter = Q(tasks__status="published") | Q(tasks__status="stuff_only")
        return task_filter

    @staticmethod
    def get_task_status_filter_for_user(user: CustomUser):
        task_filter = Q(task__status="published")
        if user and user.is_superuser:
            task_filter = Q()
        elif user and user.is_staff:
            task_filter = Q(task__status="published") | Q(task__status="stuff_only")
        return task_filter

    @staticmethod
    def get_task_skill_status_for_for_user(user: CustomUser):
        skill_status = Q(task__skill__status="published")
        if user and user.is_superuser:
            skill_status = Q()
        elif user and user.is_staff:
            skill_status = Q(task__skill__status="published") | Q(task__skill__status="stuff_only")
        return skill_status

    @staticmethod
    def get_skill_status_for_user(user: CustomUser):
        skill_status = Q(skill__status="published")
        if user and user.is_superuser:
            skill_status = Q()
        elif user and user.is_staff:
            skill_status = Q(skill__status="published") | Q(skill__status="stuff_only")
        return skill_status
