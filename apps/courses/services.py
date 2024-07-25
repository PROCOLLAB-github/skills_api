import datetime
import math

from django.db.models import Prefetch, Q, QuerySet
from django.utils import timezone

from courses.models import Task
from progress.models import TaskObjUserResult, UserProfile


def get_stats(skill_id: int, profile_id: int) -> dict:
    available_user_tasks: QuerySet[Task] | None = get_user_available_tasks(profile_id, skill_id)
    if available_user_tasks:
        tasks_of_skill = (
            available_user_tasks.prefetch_related(
                Prefetch(
                    "task_objects__user_results",
                    queryset=TaskObjUserResult.objects.filter(user_profile_id=profile_id),
                    to_attr="filtered_user_results",
                )
            ).prefetch_related("task_objects")
            .filter(
                skill_id=skill_id,
                skill__status="published",
                id__in=available_user_tasks.values('id')
            )
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
                    "status": user_results_count == task.task_objects.all().count(),
                }
            )

        statuses = ((sum(1 for obj in data if obj["status"])
                     / tasks_of_skill.count()) * 100 if tasks_of_skill.count() else 0)
        new_data = {"progress": int(statuses), "tasks": data}
    else:
        new_data = {"progress": 0, "tasks": []}
    return new_data


def get_user_available_tasks(profile_id: int, skill_id: int) -> QuerySet[Task] | None:
    """
    Основной интерфейс ограничения заданий для пользователя по неделям.
    Если подписка вообще не оформлена, то -> `None`.
    """
    subscription_date: datetime = UserProfile.objects.get(pk=profile_id).last_subscription_date

    if subscription_date:
        current_date: datetime = timezone.now().date()
        # Если подписка была сегодня то прошло дней 0, сооотв -> 1.
        days_since_subscription: datetime.timedelta = (current_date - subscription_date).days or 1
        # Дробный результат преобразуется в бОльшую часть, пример: 2.1 -> 3
        # (т.е. как началась 3 неделя, чтобы она была включительно)
        current_week: int = math.ceil(days_since_subscription / 7)
        tasks: QuerySet[Task] = Task.published.filter(
            (Q(week__lte=current_week) | Q(week=current_week)) & Q(skill__id=skill_id)
        )
        return tasks
