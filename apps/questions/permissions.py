from django.shortcuts import get_object_or_404
from django.db.models import Q
from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied

from courses.models import TaskObject
from courses.services import get_user_available_week
from progress.services import DBObjectStatusFilters
from questions.mapping import get_fields_for_answer_type, wrong_endpoint_text
from questions.services import get_error_message_for_permissions


class CheckQuestionTypePermission(permissions.BasePermission):
    """
    Проверка типа вопроса для эндпоинтов вопросов, если запрос прилетел не в тот тип вопроса,
    то резится PermissionDenied пояснением, что необходимо было дернуть.
    """

    def has_permission(self, request, view):
        task_object_id = view.kwargs.get("task_obj_id")
        prefetch_fields_list: list[str] = get_fields_for_answer_type(view)
        available_week, _ = get_user_available_week(view.profile_id)
        # Для GET запроса необходимо подягивать файлы, для POST нет.
        if request.method == "GET":
            prefetch_fields_list.extend(["content_object__files", "popup", "popup__file"])

        task_status_filter = DBObjectStatusFilters().get_task_status_filter_for_user(request.user)
        task_skill_status = DBObjectStatusFilters().get_task_skill_status_for_for_user(request.user)

        try:
            request_task_object: TaskObject = get_object_or_404(
                (TaskObject.objects
                 .prefetch_related(*prefetch_fields_list)
                 .filter(Q(task__week__lte=available_week) & task_skill_status & task_status_filter)),
                id=task_object_id,
            )
        except AttributeError as e:
            error_message = str(e.args).lower()
            if "cannot find" in error_message and "is an invalid parameter to prefetch_related()" in error_message:
                request_question = (
                    TaskObject.objects.prefetch_related("content_object").get(id=task_object_id).content_object
                )
                needed_model_class, gotten_model_class = wrong_endpoint_text(request_question, view)
                error_message = get_error_message_for_permissions(needed_model_class, gotten_model_class)
                raise PermissionDenied(error_message)
            else:
                raise AttributeError(str(e))
        request_question = request_task_object.content_object
        needed_model_class, gotten_model_class = wrong_endpoint_text(request_question, view)
        if isinstance(request_question, view.expected_question_model) and needed_model_class == gotten_model_class:
            # Установка атрибутов класса представления, чтобы повторно не дергать БД с запросом.
            view.request_task_object = request_task_object
            view.task_object_id = task_object_id
            view.request_question = request_question
            return True
        error_message = get_error_message_for_permissions(needed_model_class, gotten_model_class)
        raise PermissionDenied(error_message)


class SimpleCheckQuestionTypePermission(permissions.BasePermission):
    """
    Упрощенная проверка(там где не требуются связанные объекты) типа вопроса для эндпоинтов вопросов, если запрос
    прилетел не в тот тип вопроса, то резится PermissionDenied пояснением, что необходимо было дернуть.
    """

    def has_permission(self, request, view):
        task_object_id = view.kwargs.get("task_obj_id")
        available_week, _ = get_user_available_week(view.profile_id)
        task_status_filter = DBObjectStatusFilters().get_task_status_filter_for_user(request.user)
        task_skill_status = DBObjectStatusFilters().get_task_skill_status_for_for_user(request.user)
        request_task_object: TaskObject = get_object_or_404(
            (TaskObject.objects
             .prefetch_related("content_object")
             .filter(Q(task__week__lte=available_week) & task_skill_status & task_status_filter)),
            id=task_object_id,
        )
        request_question = request_task_object.content_object
        needed_model_class, gotten_model_class = wrong_endpoint_text(request_question, view)
        if isinstance(request_question, view.expected_question_model) and needed_model_class == gotten_model_class:
            view.task_object_id = task_object_id
            return True
        error_message = get_error_message_for_permissions(needed_model_class, gotten_model_class)
        raise PermissionDenied(error_message)
