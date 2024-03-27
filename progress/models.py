from django.utils import timezone

from django.db import models
from courses.models import TaskObject, Skill
from progress.validators import CORRECTNESS_VALUE_VALIDATOR


class UserTest(models.Model):
    first_name = models.CharField(max_length=30, verbose_name="Имя пользователя")
    last_name = models.CharField(max_length=30, verbose_name="Фамилия пользователя")
    age = models.IntegerField(verbose_name="Возраст пользователя")
    specialization = models.CharField(max_length=40, verbose_name="Специальность пользователя")
    geo_position = models.CharField(max_length=50)

    class Meta:
        verbose_name = "Пользователь (тестовая модель)"
        verbose_name_plural = "Пользователи (тестовая модель)"


class UserProfile(models.Model):
    user = models.ForeignKey(
        UserTest, on_delete=models.CASCADE, related_name="profiles", verbose_name="Пользователь"
    )
    chosen_skills = models.ManyToManyField(Skill, related_name="profile_skills", verbose_name="Выбранные навыки")

    # TODO перенести некоторую логику оценок в профиль пользователя, чтобы уменьшить нагрузку на БД

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"

    class Meta:
        verbose_name = "Профиль пользователя"
        verbose_name_plural = "Профили пользователей"


class TaskObjUserResult(models.Model):
    task_object = models.OneToOneField(
        TaskObject,
        on_delete=models.CASCADE,
        related_name="user_results",
        verbose_name="Объект задачи"
    )
    user_profile = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        related_name="task_obj_results",
        verbose_name="Профиль пользователя"
    )

    points_gained = models.PositiveIntegerField(
        verbose_name="Набранные баллы"
    )

    datetime_created = models.DateTimeField(
        verbose_name="Дата создания",
        null=False,
        default=timezone.now
    )

    def __str__(self):
        return f"{self.task_object.task.name} {self.task_object.ordinal_number} {self.user_profile.user.first_name}"

    class Meta:
        verbose_name = "Ответ пользователя на единицу задания"
        verbose_name_plural = "Ответы пользователя на единицу задания"
        unique_together = ("task_object", "user_profile")

