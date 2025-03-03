import re

from django.core.exceptions import ValidationError


def validate_hex_color(value):
    """
    Проверяет, что значение является корректным HEX-кодом цвета (#RRGGBB).
    """
    if not re.fullmatch(r"^#[0-9A-Fa-f]{6}$", value):
        raise ValidationError("Цвет должен быть в формате HEX (#RRGGBB).")


def validate_positive(value):
    """
    Проверяет, что значение является положительным числом.
    """
    if value <= 0:
        raise ValidationError("Значение должно быть положительным числом.")
