from django.db import IntegrityError


class UserAlreadyAnsweredException(IntegrityError):
    message = "User has already done this slide!"

    def __str__(self):
        return f"{self.message}"
