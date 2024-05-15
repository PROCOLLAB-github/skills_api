from django.shortcuts import get_object_or_404
from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied

from courses.models import TaskObject
from questions.mapping import get_answer_type, wrong_endpoint_text


class CheckQuestionTypePermission(permissions.BasePermission):
    """
    Проверка типа вопроса для GET эндпоинта вопросов, если запрос прилетел не туда,
    то резится PermissionDenied пояснением, что необходимо было дернуть.
    """

    def has_permission(self, request, view):
        task_object_id = view.kwargs.get("task_obj_id")
        try:
            request_task_object: TaskObject = get_object_or_404(
                TaskObject.objects.prefetch_related(
                    "content_object",
                    get_answer_type(view),
                    "content_object__files",
                ),
                id=task_object_id,
            )
        except AttributeError as e:
            error_message = str(e.args).lower()
            if "cannot find" in error_message and "is an invalid parameter to prefetch_related()" in error_message:
                request_question = (
                    TaskObject.objects.prefetch_related(
                        "content_object",
                    )
                    .get(id=task_object_id)
                    .content_object
                )

                needed_model_class, gotten_model_class = wrong_endpoint_text(request_question, view)
                raise PermissionDenied(
                    {
                        "error": (
                            f"You tried to summon taskobject with a wrong endpoint. "
                            f"Instead of using '{needed_model_class}' endpoint, "
                            f"try using '{gotten_model_class}' endpoint."
                        )
                    }
                )
            else:
                raise AttributeError(str(e))

        request_question = request_task_object.content_object
        needed_model_class, gotten_model_class = wrong_endpoint_text(request_question, view)
        if isinstance(request_question, view.expected_question_model) and needed_model_class == gotten_model_class:
            # Установка атрибутов класса представления, чтобы повторно не дергать БД с запросом.
            view.task_object_id = task_object_id
            view.request_question = request_question
            return True
        raise PermissionDenied(
            {
                "error": (
                    f"You tried to summon taskobject with a wrong endpoint. "
                    f"Instead of using '{needed_model_class}' endpoint, "
                    f"try using '{gotten_model_class}' endpoint."
                )
            }
        )
