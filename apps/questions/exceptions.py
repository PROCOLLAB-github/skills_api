from django.db import IntegrityError
from rest_framework.exceptions import PermissionDenied

PermissionDenied


class UserAlreadyAnsweredException(IntegrityError):
    message = "User has already done this slide!"

    def __str__(self):
        return f"{self.message}"
