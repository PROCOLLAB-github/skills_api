from django.contrib.auth.models import AbstractUser
from django.db import models

from django.utils import timezone

from progress.manager import CustomUserManager

from progress.validators import user_name_validator


class CustomUser(AbstractUser):
    username = None
    email = models.EmailField(unique=True)

    first_name = models.CharField(max_length=255, validators=[user_name_validator])
    last_name = models.CharField(max_length=255, validators=[user_name_validator])
    patronymic = models.CharField(max_length=255, validators=[user_name_validator], null=True, blank=True)
    password = models.CharField(max_length=255)

    is_active = models.BooleanField(default=True, editable=False)

    city = models.CharField(max_length=255, null=True, blank=True)
    organization = models.CharField(max_length=255, null=True, blank=True)
    age = models.DateTimeField(null=True, blank=False)
    specialization = models.CharField(max_length=40, verbose_name="Специальность пользователя", null=True)
    geo_position = models.CharField(max_length=50, null=True)

    datetime_updated = models.DateTimeField(auto_now=True)
    datetime_created = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def get_full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def __str__(self) -> str:
        return f"User<{self.id}> - {self.first_name} {self.last_name}"

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"


class UserProfile(models.Model):
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="profiles",
        verbose_name="Пользователь",
    )
    chosen_skills = models.ManyToManyField(
        "courses.Skill", related_name="profile_skills", verbose_name="Выбранные навыки"
    )
    file = models.ForeignKey(
        "files.FileModel",
        on_delete=models.SET_NULL,
        related_name="profiles",
        verbose_name="Картинка",
        null=True,
        blank=True,
    )

    is_autopay_allowed = models.BooleanField(default=True)
    last_subscription_date = models.DateField(
        default=timezone.now, verbose_name="Последний раз когда юзер оформилял подписку"
    )

    # TODO перенести некоторую логику оценок в профиль пользователя, чтобы уменьшить нагрузку на БД

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"

    class Meta:
        verbose_name = "Профиль пользователя"
        verbose_name_plural = "Профили пользователей"


class TaskObjUserResult(models.Model):
    task_object = models.OneToOneField(
        "courses.TaskObject",
        on_delete=models.CASCADE,
        related_name="user_results",
        verbose_name="Объект задачи",
    )
    user_profile = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        related_name="task_obj_results",
        verbose_name="Профиль пользователя",
    )

    points_gained = models.PositiveIntegerField(verbose_name="Набранные баллы")

    datetime_created = models.DateTimeField(verbose_name="Дата создания", null=False, default=timezone.now)

    def __str__(self):
        return f"{self.task_object.task.name} {self.task_object.ordinal_number} {self.user_profile.user.first_name}"

    class Meta:
        verbose_name = "Ответ пользователя на единицу задания"
        verbose_name_plural = "Ответы пользователя на единицу задания"
        unique_together = ("task_object", "user_profile")
