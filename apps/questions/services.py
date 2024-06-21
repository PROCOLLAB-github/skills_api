from rest_framework.utils.serializer_helpers import ReturnDict

from courses.models import TaskObject


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
            "title": popup.title if popup.title else None,
            "text": popup.text if popup.text else None,
            "file_link": popup.file.link if popup.file else None,
            "ordinal_number": popup.ordinal_number,
        })
    return data
