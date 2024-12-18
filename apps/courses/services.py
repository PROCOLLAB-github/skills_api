from django.db.models import Prefetch, Count, QuerySet, Max

from courses.models import Task
from courses.typing import GetStatsDict, WeekStatsDict
from progress.services import (
    DBObjectStatusFilters,
    get_user_available_week,
)
from progress.models import (
    CustomUser,
    TaskObjUserResult,
    UserWeekStat,
)
from progress.services import get_rounded_percentage


def get_stats(skill_id: int, profile_id: int, request_user: CustomUser | None = None) -> GetStatsDict:
    available_week, user = get_user_available_week(profile_id)
    skill_status_filter = DBObjectStatusFilters().get_skill_status_for_user(request_user)

    tasks_of_skill: QuerySet[Task] = (
        Task.available
        .only_awailable_weeks(available_week, user)
        .prefetch_related(
            Prefetch(
                "task_objects__user_results",
                queryset=TaskObjUserResult.objects.filter(user_profile_id=profile_id),
                to_attr="filtered_user_results",
            )
        ).prefetch_related("task_objects")
        .annotate(task_objects_count=Count("task_objects"))
        .filter(skill_id=skill_id)
        .filter(skill_status_filter)
    )

    data = []
    user_done_task_objects: list[int] = []
    all_task_objects: list[int] = []
    for task in tasks_of_skill:
        user_results_count = sum(1 for obj in task.task_objects.all() if obj.filtered_user_results)
        user_done_task_objects.append(user_results_count)
        all_task_objects.append(task.task_objects_count)
        data.append(
            {
                "id": task.id,
                "name": task.name,
                "level": task.level,
                "week": task.week,
                "status": user_results_count == task.task_objects_count,
            }
        )
    statuses = get_rounded_percentage(sum(user_done_task_objects), sum(all_task_objects))

    stats_of_weeks: list[WeekStatsDict] = get_stats_of_weeks(skill_id, profile_id, available_week, request_user)

    new_data = {"progress": statuses, "tasks": data, "stats_of_weeks": stats_of_weeks}
    return new_data


def get_stats_of_weeks(
    skill_id: int,
    profile_id: int,
    available_week: int,
    request_user: CustomUser | None = None,
) -> list[WeekStatsDict]:
    """
    Список статистики по неделям `done_on_time` имеет 3 состояния:
        `True`: Задания в неделе сделаны вовремя.
        `False`: Задания в неделе сделаны не вовремя (в случае если неделя завершена).
        `None`: Неделя не завершена.
    """
    stats_of_weeks: list[WeekStatsDict] = [
        {
            "week": week.week,
            "is_done": week.is_done,
            "done_on_time": bool(week.additional_points) if week.is_done else None,
        }
        for week in UserWeekStat.objects.filter(user_profile__id=profile_id, skill__id=skill_id)
    ]

    # TODO Временная мера(2 строчки ниже), как будет нормальное деление по неделям, необходимо убрать.
    # Выбор из минимально доступной недели и максимальной имеющейся у навыка (сейчас на проде все задания - 1неделя)
    # Если не убрать ничего не сломается, но лишний запрос.
    max_skill_week: dict[str:int] = (
        Task.published
        .for_user(request_user)
        .filter(skill__id=skill_id)
        .aggregate(Max("week"))
    )
    available_week = min(available_week, max_skill_week["week__max"])

    # Запись в `UserWeekStat` формируется при прохождении, но если юзер вообще не проходил,
    # необходимо дополнить список недостающими неделями (доступными ему сейчас).
    if len(stats_of_weeks) != available_week:
        existing_weeks: set[int] = {week["week"] for week in stats_of_weeks}
        for week in range(1, available_week+1):
            if week not in existing_weeks:
                stats_of_weeks.append(
                    {
                        "week": week,
                        "is_done": False,
                        "done_on_time": None,
                    }
                )
    return stats_of_weeks
