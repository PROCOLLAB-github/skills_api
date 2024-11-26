from abc import ABC, abstractmethod

from django.db import IntegrityError


class AbstractException(BaseException, ABC):

    def __init__(self, text_error: str | None = None, *args) -> None:
        super().__init__(*args)
        self.text_error = text_error

    @abstractmethod
    def __str__(self) -> str:
        raise NotImplementedError


class UserAlreadyAnsweredException(IntegrityError):
    message = "User has already done this slide!"

    def __str__(self):
        return f"{self.message}"


class QustionConnectException(AbstractException):

    def __str__(self) -> str:
        return self.text_error or "Ошибка в ответе"
