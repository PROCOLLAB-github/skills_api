from django.db.models import QuerySet
from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied

from courses.models import Task
from courses.services import get_user_available_tasks


class CheckUserHasWeekPermission(permissions.BasePermission):
    """
    Проверка наличия доступа к заданию исходя из недели(зависит от даты оформления подписки).
    В запросе должен быть либо `task_obj_id`либо `task_id`
    """

    def has_permission(self, request, view):
        task_object_id: int = view.kwargs.get("task_obj_id")
        task_id: int = view.kwargs.get("task_id")
        if task_object_id:
            current_task: Task = Task.objects.get(task_objects__id=task_object_id)
        elif task_id:
            current_task: Task = Task.objects.get(pk=task_id)
        user_tasks: QuerySet[Task] = get_user_available_tasks(request.user.profiles.id, current_task.skill.id)
        if user_tasks and (current_task in user_tasks):
            return True
        raise PermissionDenied("The task is not active yet, you need to wait for the corresponding week.")
