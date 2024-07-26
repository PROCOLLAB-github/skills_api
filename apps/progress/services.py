import datetime

from django.db.models import Q, Count, QuerySet

from courses.models import Skill, Task
from progress.mapping import MonthMapping
from progress.models import UserProfile, IntermediateUserSkills
from progress.typing import SkillIdType, SkillProgressType, SkillMonthProgressType


def months_passed_data() -> tuple[datetime.date, datetime.date]:
    """Последние 2 месяца не включая текущий."""
    today = datetime.date.today()
    first = today.replace(day=1)
    last_month = first - datetime.timedelta(days=1)

    sec = last_month.replace(day=1)
    last_last_month = sec - datetime.timedelta(days=1)

    return last_last_month, last_month


def get_user_data(profile_id: int) -> dict:
    user_profile = UserProfile.objects.select_related("user", "file").get(id=profile_id)
    # TODO добавить сериалайзер
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
    }


def get_current_level(user_profile_id: int) -> dict[SkillIdType, SkillProgressType]:
    """Выдаёт наиболее маленький непройденный уровень у всех скиллов пользователя"""

    # Навыки и id навыков пользователя.
    user_skills, user_skills_ids = get_user_skills(user_profile_id)

    # Получение значений для всех задач, связанных с навыками пользователя.
    tasks: QuerySet = (
        # TODO Fix как утвердится инфа для профиля, надо учесть недели.
        Task.published.filter(skill__in=user_skills_ids)
        .annotate(
            num_questions=Count("task_objects"),
            num_answers=Count(
                "task_objects__user_results", filter=Q(task_objects__user_results__user_profile__id=user_profile_id)
            ),
        )
        .values("skill_id", "level", "num_questions", "num_answers")
    )

    # Подготовительный словарь для хранения данных о навыках.
    skills_data: dict[SkillIdType, SkillProgressType] = {
        skill.id: {"skill_name": skill.name, "level": 1} for skill in user_skills
    }

    # Определение текущего уровня навыка на основе задач.
    for task in tasks:
        skill_id = task["skill_id"]
        level = task["level"]
        num_questions = task["num_questions"]
        num_answers = task["num_answers"]

        if skills_data[skill_id]["level"] == level:
            if num_questions == num_answers:
                skills_data[skill_id]["level"] += 1
            else:
                skills_data[skill_id]["progress"] = round((num_answers / num_questions) * 100)
    return skills_data


def last_two_months_stats(user_profile_id: int) -> list[SkillMonthProgressType]:
    """
    Получение информации по навыкам за 2 последних месяца не включая текущий.
    Если в течении месяца было закомпличено хотя бы по 1 уровню у ВСЕХ навыков, то True.
    """
    two_months_ago, last_months = months_passed_data()
    user_skills_ids: QuerySet = get_user_skills_data(user_profile_id, (two_months_ago, last_months))

    # Получение значений для всех уровней за 2 месяца, связанных с навыками пользователя.
    tasks: QuerySet = (
        Task.published.filter(skill_id__in=user_skills_ids)
        .annotate(
            num_questions=Count("task_objects"),
            num_answers_last_months=Count(
                "task_objects__user_results",
                filter=Q(
                    task_objects__user_results__user_profile__id=user_profile_id,
                    task_objects__user_results__datetime_created__month=last_months.month,
                    task_objects__user_results__datetime_created__year=last_months.year,
                ),
            ),
            num_answers_two_months_ago=Count(
                "task_objects__user_results",
                filter=Q(
                    task_objects__user_results__user_profile__id=user_profile_id,
                    task_objects__user_results__datetime_created__month=two_months_ago.month,
                    task_objects__user_results__datetime_created__year=two_months_ago.year,
                ),
            ),
        )
        .values("skill_id", "level", "num_questions", "num_answers_last_months", "num_answers_two_months_ago")
    )

    # Подготовительный словарь с данными по навыку и комплиту хотя бы 1 уровня за 2 месяца.
    stats: dict[SkillIdType, SkillMonthProgressType] = {}
    for task in tasks:
        skill_id = task["skill_id"]
        num_questions = task["num_questions"]
        if skill_id not in stats:
            stats[skill_id] = {"last_months": False, "two_months_ago": False}
        if num_questions == task["num_answers_last_months"]:
            stats[skill_id]["last_months"] = True
        if num_questions == task["num_answers_two_months_ago"]:
            stats[skill_id]["two_months_ago"] = True

    # Результирующий список словарей.
    months_data: list[SkillMonthProgressType] = [
        {
            "month": MonthMapping[last_months.month],
            "is_passed": all(task["last_months"] for task in stats.values()) if stats else False,
        },
        {
            "month": MonthMapping[two_months_ago.month],
            "is_passed": all(task["two_months_ago"] for task in stats.values()) if stats else False,
        },
    ]
    return months_data


def get_user_skills(user_profile_id: int) -> tuple[QuerySet[Skill], QuerySet]:
    """Получение всех навыков и их id для конкретного пользователя."""
    user_skills: QuerySet[Skill] = Skill.published.filter(
        Q(intermediateuserskills__user_profile__id=user_profile_id)
        | Q(tasks__task_objects__user_results__user_profile__id=user_profile_id),
    ).distinct()
    user_skills_ids: QuerySet = user_skills.values_list("id", flat=True)
    return user_skills, user_skills_ids


def get_user_skills_data(user_profile_id: int, dates: tuple[datetime.date, datetime.date]) -> QuerySet:
    """Получение всех навыков и их id для конкретного пользователя."""
    user_skills_ids = (
        IntermediateUserSkills.objects.select_related("skill")
        .filter(
            user_profile_id=user_profile_id,
            date_chosen__year__in=[date.year for date in dates],
            date_chosen__month__in=[date.month for date in dates],
        )
        .values_list("id", flat=True)
    )
    return user_skills_ids
