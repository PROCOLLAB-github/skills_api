from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied

from courses.models import TaskObject


class CheckQuestionTypePermission(permissions.BasePermission):
    """
    Проверка типа вопроса для GET эндпоинта вопросов, если запрос прилетел не туда,
    то резится PermissionDenied пояснением, что необходимо было дернуть.
    """

    def has_permission(self, request, view):
        task_object_id = view.kwargs.get("task_obj_id")
        try:
            request_task_object: TaskObject = TaskObject.objects.prefetch_related(
                "content_object",
                "content_object__files",
            ).get(id=task_object_id)

        except TaskObject.DoesNotExist:
            raise PermissionDenied({"error": 'You tried to summon taskobject with a wrong id.'})
        else:
            request_question = request_task_object.content_object
            if isinstance(request_question, view.expected_question_model):
                # Установка атрибутов класса представления, чтобы повторно не дергать БД с запросом.
                view.task_object_id = task_object_id
                view.request_question = request_question
                return True
            raise PermissionDenied(
                {
                    "error": (f"You tried to summon taskobject with a wrong endpoint. "
                              f"Instead of using '{view.expected_question_model._meta.verbose_name}' endpoint, "
                              f"try using '{request_question._meta.verbose_name}' endpoint.")
                }
            )
