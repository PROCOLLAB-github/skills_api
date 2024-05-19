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
