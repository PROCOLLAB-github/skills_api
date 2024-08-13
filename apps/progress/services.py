import datetime
import math
from decimal import Decimal, ROUND_HALF_UP

from django.db.models import Count, Q, QuerySet, Sum
from django.utils import timezone

from progress.mapping import MonthMapping
from courses.models import Skill
from progress.typing import (
    UserProfileDataDict,
    UserSkillsProgressDict,
    UserMonthsProgressDict,
    PreparatoryUserMonthsProgressDict,
)
from progress.models import (
    UserMonthStat,
    UserProfile,
    UserWeekStat,
    UserSkillDone,
    TaskObjUserResult,
)


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


def get_user_profile_skills_progress(user_profile_id: int) -> list[UserSkillsProgressDict]:
    """
    Статистика по навыкам пользователя с % прогресса для профиля. 
    """
    # TODO Fix учесть, когда будет выбор только 5 навыков для юзера.
    _, user_skills_ids = get_user_skills(user_profile_id)
    skills_stats: QuerySet[Skill] = (
        Skill.published
        .filter(id__in=user_skills_ids)
        .annotate(
                # Общее кол-во опубликованных вопросов навыка.
                total_num_questions=Count("tasks__task_objects", filter=Q(tasks__status="published")),
                # Общее кол-во ответов юзера на опубликованные вопросы в рамках навыка.
                total_user_answers=Count(
                    "tasks__task_objects__user_results",
                    filter=(Q(tasks__task_objects__user_results__user_profile_id=user_profile_id)
                            & Q(tasks__status="published")),
                ),
            )
    )
    stats_data: list[UserSkillsProgressDict] = [
        {
            "skill_id": skill.id,
            "skill_name": skill.name,
            "skill_level": 1,  # TODO Fix захардкоженный уровень, пока не понятно что за уровни навыка.
            "skill_progress": get_rounded_percentage(skill.total_user_answers, skill.total_num_questions)
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
    user_skills: QuerySet[Skill] = Skill.published.filter(
        Q(intermediateuserskills__user_profile__id=user_profile_id)
        | Q(tasks__task_objects__user_results__user_profile__id=user_profile_id),
    ).distinct()
    user_skills_ids: QuerySet = user_skills.values_list("id", flat=True)
    return user_skills, user_skills_ids


def get_user_available_week(profile_id: int) -> int:
    """
    Получение доступных пользователю недель, все что <= `available_week` доступно.
    Если подписка вообще не оформлена, то -> 0, соотв. ничего не доступно.
    Пример запроса для Task:
        `Q(week__lte=available_week)`
    """
    subscription_date: datetime = UserProfile.objects.get(pk=profile_id).last_subscription_date

    if subscription_date:
        current_date: datetime = timezone.now().date()
        # Если подписка была сегодня то прошло дней 0, сооотв -> 1.
        days_since_subscription: datetime.timedelta = (current_date - subscription_date).days or 1
        # Дробный результат преобразуется в бОльшую часть, пример: 2.1 -> 3
        # (т.е. как началась 3 неделя, чтобы она была включительно)
        available_week: int = math.ceil(days_since_subscription / 7)
        return available_week
    return 0


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
