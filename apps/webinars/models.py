from django.db import models

from files.models import FileModel
from progress.models import CustomUser
from webinars.managers import WebinarManager


class Webinar(models.Model):
    title = models.CharField(
        max_length=255,
        verbose_name="Заголовок",
    )
    description = models.TextField(
        verbose_name="Описание",
    )
    datetime_start = models.DateTimeField(
        verbose_name="Дата и время начала",
    )
    datetime_end = models.DateTimeField(
        verbose_name="Дата и время конца",
    )
    online_link = models.URLField(
        null=True,
        blank=True,
        verbose_name="Ссылка для подключения",
    )
    recording_link = models.URLField(
        null=True,
        blank=True,
        verbose_name="Ссылка на запись",
    )
    speaker = models.ForeignKey(
        to="Speaker",
        related_name="webinars",
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        verbose_name="Спикер",
    )

    objects = WebinarManager()

    class Meta:
        verbose_name = "Вебинар"
        verbose_name_plural = "Вебинары"
        ordering = ["datetime_start"]

    def __str__(self):
        return f"{self.id}: {self.title}"


class Speaker(models.Model):
    full_name = models.CharField(
        max_length=255,
        verbose_name="Имя и фамилия спикера",
    )
    photo = models.ForeignKey(
        to=FileModel,
        related_name="webinars",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    position = models.CharField(
        max_length=255,
        verbose_name="Должность",
    )

    class Meta:
        verbose_name = "Спикер"
        verbose_name_plural = "Спикеры"

    def __str__(self):
        return f"{self.id}: {self.full_name}"


class WebinarRegistration(models.Model):
    user = models.ForeignKey(
        to=CustomUser,
        related_name="webinar_registrations",
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
    )
    webinar = models.ForeignKey(
        to=Webinar,
        related_name="webinar_registrations",
        on_delete=models.CASCADE,
        verbose_name="Вебинар",
    )
    datetime_created = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата регистрации",
    )

    class Meta:
        verbose_name = "Регистрация на вебинар"
        verbose_name_plural = "Регистрации на вебинар"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "webinar"],
                name="unique_user_registration",
            ),
        ]

    def __str__(self):
        return f"{self.id}: {self.webinar} - {self.user}"
