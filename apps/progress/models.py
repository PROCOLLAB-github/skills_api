from django.contrib.auth.models import AbstractUser
from django.db import models

from django.utils import timezone

from progress.manager import CustomUserManager
from progress.managers import TaskObjUserResultManager, UserProfileManager

from progress.validators import user_name_validator
from subscription.models import SubscriptionType


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
    age = models.DateField(null=True, blank=False)
    specialization = models.CharField(max_length=40, verbose_name="Специальность пользователя", null=True)

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
        "progress.CustomUser",
        on_delete=models.CASCADE,
        related_name="profiles",
        verbose_name="Пользователь",
    )
    chosen_skills = models.ManyToManyField(
        "courses.Skill",
        related_name="profile_skills",
        verbose_name="Выбранные навыки",
        through="IntermediateUserSkills",
    )
    file = models.ForeignKey(
        "files.FileModel",
        on_delete=models.SET_NULL,
        related_name="profiles",
        verbose_name="Картинка",
        null=True,
        blank=True,
    )

    is_autopay_allowed = models.BooleanField(default=False)
    last_subscription_type = models.ForeignKey(SubscriptionType, on_delete=models.SET_NULL, null=True, blank=True)
    last_subscription_date = models.DateField(null=True, verbose_name="Последний раз когда юзер оформилял подписку")

    objects = UserProfileManager()

    # TODO перенести некоторую логику оценок в профиль пользователя, чтобы уменьшить нагрузку на БД

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"

    class Meta:
        verbose_name = "Профиль пользователя"
        verbose_name_plural = "Профили пользователей"


class IntermediateUserSkills(models.Model):
    user_profile = models.ForeignKey("progress.UserProfile", on_delete=models.CASCADE)
    skill = models.ForeignKey("courses.Skill", on_delete=models.CASCADE)
    date_chosen = models.DateField(default=timezone.now)

    class Meta:
        unique_together = ("user_profile", "date_chosen")

    def __str__(self):
        return (
            f"<SkillUserRelation> "
            f"<User:{self.user_profile.user.first_name + self.user_profile.user.last_name}> <Skill:{self.skill.name}>"
        )


class TaskObjUserResult(models.Model):
    task_object = models.ForeignKey(
        "courses.TaskObject",
        on_delete=models.CASCADE,
        related_name="user_results",
        verbose_name="Объект задачи",
    )
    user_profile = models.ForeignKey(
        "progress.UserProfile",
        on_delete=models.CASCADE,
        related_name="task_obj_results",
        verbose_name="Профиль пользователя",
    )

    text = models.TextField(null=False, help_text="Для ответов юзера, которые связаны с вопросами по вводу ответа")
    points_gained = models.PositiveIntegerField(verbose_name="Набранные баллы")

    datetime_created = models.DateTimeField(verbose_name="Дата создания", null=False, default=timezone.now)

    objects = TaskObjUserResultManager()

    def __str__(self):
        return f"{self.task_object.task.name} {self.task_object.ordinal_number} {self.user_profile.user.first_name}"

    class Meta:
        verbose_name = "Ответ пользователя на единицу задания"
        verbose_name_plural = "Ответы пользователя на единицу задания"
        unique_together = ("task_object", "user_profile")
