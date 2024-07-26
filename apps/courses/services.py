import datetime
import math

from django.db.models import Prefetch, Count, QuerySet
from django.utils import timezone

from courses.models import Task
from courses.typing import GetStatsDict
from progress.models import TaskObjUserResult, UserProfile


def get_stats(skill_id: int, profile_id: int) -> GetStatsDict:
    available_week: int = get_user_available_week(profile_id)
    tasks_of_skill: QuerySet[Task] = (
        Task.available
        .only_awailable_weeks(available_week)
        .prefetch_related(
            Prefetch(
                "task_objects__user_results",
                queryset=TaskObjUserResult.objects.filter(user_profile_id=profile_id),
                to_attr="filtered_user_results",
            )
        ).prefetch_related("task_objects")
        .annotate(task_objects_count=Count("task_objects"))
        .filter(skill_id=skill_id, skill__status="published")
    )

    data = []

    for task in tasks_of_skill:
        user_results_count = sum(1 for obj in task.task_objects.all() if obj.filtered_user_results)
        data.append(
            {
                "id": task.id,
                "name": task.name,
                "level": task.level,
                "week": task.week,
                "status": user_results_count == task.task_objects_count,
            }
        )
    count_task_of_skill: int = tasks_of_skill.count()
    statuses = ((sum(1 for obj in data if obj["status"]) / count_task_of_skill) * 100 if count_task_of_skill else 0)
    new_data = {"progress": int(statuses), "tasks": data}
    return new_data


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
