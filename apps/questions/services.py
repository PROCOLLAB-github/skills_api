from typing import Iterable, Optional

from rest_framework.response import Response
from rest_framework import status
from rest_framework.utils.serializer_helpers import ReturnDict

from questions.mapping import TypeQuestionPoints
from courses.models import TaskObject
from progress.models import TaskObjUserResult


def get_error_message_for_permissions(needed_model_class: str, gotten_model_class: str) -> dict[str: str]:
    """
    Получаем: наименование ожидаемой и полученной модели.
    Возвращаем: Словарь ключ-ошибка, значение-текст ошибки.
    """
    return {
            "error": (
                f"You tried to summon taskobject with a wrong endpoint. "
                f"Instead of using '{needed_model_class}' endpoint, "
                f"try using '{gotten_model_class}' endpoint."
            )
    }


def add_popup_data(data: ReturnDict | dict, task_object: TaskObject) -> ReturnDict | dict:
    """Корректировки response для вопросов, добавляем информацию по поп-апам."""
    data["popups"] = []
    for popup in task_object.popup.all():
        data["popups"].append({
            "title": popup.title,
            "text": popup.text if popup.text else None,
            "file_link": popup.file.link if popup.file else None,
            "ordinal_number": popup.ordinal_number,
        })
    return data


def handle_no_validation_required(
    task_object_id: int,
    profile_id: int,
    point_type: TypeQuestionPoints,
    request_data: Iterable,
    response_data: dict,
    required_data: Optional[Iterable] = None,
) -> Response:
    """
    Если у TaskObject отключена проверка.
    Проверка лишь на наличие ответа, а в случае с вопросом на соотношение, что все блоки сопоставлены.
    """
    if (required_data and len(request_data) < len(required_data)) or not request_data:
        return Response({"text": "need more..."}, status=status.HTTP_400_BAD_REQUEST)

    TaskObjUserResult.objects.create_user_result(task_object_id, profile_id, point_type)
    return Response(response_data, status=status.HTTP_201_CREATED)
