from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator
from django.contrib.auth.models import AbstractUser

from progress.managers import TaskObjUserResultManager, CustomUserManager

from progress.validators import user_name_validator
from subscription.models import SubscriptionType


class CustomUser(AbstractUser):
    username = None
    email = models.EmailField(unique=True)

    first_name = models.CharField(max_length=255, validators=[user_name_validator])
    last_name = models.CharField(max_length=255, validators=[user_name_validator])
    patronymic = models.CharField(
        max_length=255, validators=[user_name_validator], null=True, blank=True
    )
    password = models.CharField(max_length=255)

    is_active = models.BooleanField(default=True, editable=False)

    city = models.CharField(max_length=255, null=True, blank=True)
    organization = models.CharField(max_length=255, null=True, blank=True)
    age = models.DateField(null=True, blank=False)
    specialization = models.CharField(
        max_length=40, verbose_name="Специальность пользователя", null=True
    )

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

    last_subscription_type = models.ForeignKey(
        SubscriptionType, on_delete=models.SET_NULL, null=True, blank=True
    )
    bought_trial_subscription = models.BooleanField(
        default=False, help_text="Покупал ли пользователь пробную подписку до этого"
    )
    last_subscription_date = models.DateField(
        null=True, verbose_name="Последний раз когда юзер оформилял подписку"
    )

    # TODO перенести некоторую логику оценок в профиль пользователя, чтобы уменьшить нагрузку на БД

    class Meta:
        verbose_name = "Профиль пользователя"
        verbose_name_plural = "Профили пользователей"

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"

    def save(self, *args, **kwargs):
        """
        Проверка на подписку, если пользователь подписался,
        формируется Celery таска на месячные цели.
        """
        if self.pk:
            old_instance = UserProfile.objects.get(pk=self.pk)
            if old_instance.last_subscription_date != self.last_subscription_date:
                from progress.tasks import create_user_monts_target

                create_user_monts_target.delay(old_instance.pk)
        super().save(*args, **kwargs)


class IntermediateUserSkills(models.Model):
    user_profile = models.ForeignKey("progress.UserProfile", on_delete=models.CASCADE)
    skill = models.ForeignKey("courses.Skill", on_delete=models.CASCADE)
    date_chosen = models.DateField(default=timezone.now)

    class Meta:
        unique_together = ("user_profile", "date_chosen", "skill")

    def __str__(self):
        return (
            f"<SkillUserRelation> "
            f"<User:{self.user_profile.user.first_name + self.user_profile.user.last_name}> <Skill:{self.skill.name}>"
        )


class AbstractDateTimeCreated(models.Model):
    datetime_created = models.DateTimeField(
        verbose_name="Дата создания",
        null=False,
        default=timezone.now,
    )

    class Meta:
        abstract = True


class TaskObjUserResult(AbstractDateTimeCreated):
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
    text = models.TextField(
        null=False,
        help_text="Для ответов юзера, которые связаны с вопросами по вводу ответа",
    )
    correct_answer = models.BooleanField(
        default=True,
        null=False,
        blank=False,
        verbose_name="Правильный ответ",
        help_text="Дан верный/не верный ответ на задание",
    )
    points_gained = models.PositiveIntegerField(verbose_name="Набранные баллы")
    datetime_created = models.DateTimeField(
        verbose_name="Дата создания", null=False, default=timezone.now
    )

    objects = TaskObjUserResultManager()

    def __str__(self):
        return f"{self.task_object.task.name} {self.task_object.ordinal_number} {self.user_profile.user.first_name}"

    class Meta:
        verbose_name = "Ответ пользователя на единицу задания"
        verbose_name_plural = "Ответы пользователя на единицу задания"
        unique_together = ("task_object", "user_profile")


class UserSkillDone(AbstractDateTimeCreated):
    """
    Завершенные навыки пользователя.
    Запись создается сигналом от `TaskObjUserResult` через Celery task.
    """

    user_profile = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        related_name="done_skills",
        verbose_name="Пользователь",
    )
    skill = models.ForeignKey(
        "courses.Skill",
        on_delete=models.CASCADE,
        related_name="done_skills",
        verbose_name="Навык",
    )
    additional_points = models.PositiveSmallIntegerField(
        default=0,
        verbose_name="Дополнительные баллы",
        help_text="Начисляются за прохождение месяца вовремя.",
    )

    def __str__(self):
        return f"{self.user_profile.user.first_name} {self.user_profile.user.last_name}: {self.skill.name}"

    class Meta:
        verbose_name = "Завершенный навык"
        verbose_name_plural = "Завершенные навыки"
        constraints = [
            models.UniqueConstraint(
                fields=["user_profile", "skill"], name="unique_skill_in_profile"
            )
        ]


class UserWeekStat(AbstractDateTimeCreated):
    """
    Завершенные недели пользователя.
    Запись создается сигналом от `TaskObjUserResult` через Celery task.
    """

    WEEK_CHOICES = [
        (1, "1 Неделя"),
        (2, "2 Неделя"),
        (3, "3 Неделя"),
        (4, "4 Неделя"),
    ]
    user_profile = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        related_name="weeks_result",
        verbose_name="Пользователь",
    )
    skill = models.ForeignKey(
        "courses.Skill",
        on_delete=models.CASCADE,
        related_name="weeks_result",
        verbose_name="Навык",
    )
    additional_points = models.PositiveSmallIntegerField(
        default=0,
        verbose_name="Дополнительные баллы",
        help_text="Начисляются за прохождение недели вовремя.",
    )
    week = models.PositiveSmallIntegerField(choices=WEEK_CHOICES, verbose_name="Неделя")
    is_done = models.BooleanField(verbose_name="Неделя завершена")

    class Meta:
        verbose_name = "Завершенная неделя"
        verbose_name_plural = "Завершенные недели"
        constraints = [
            models.UniqueConstraint(
                fields=["user_profile", "skill", "week"], name="unique_week_stat"
            )
        ]

    def __str__(self):

        return f"{self.user_profile.user.first_name}: {self.skill.name} - week {self.week}"


class AbstractMonthFields(models.Model):
    """Абстрактная модель с полями для таблиц месяцев."""

    class Month(models.IntegerChoices):
        JAN = 1, "Январь"
        FEB = 2, "Февраль"
        MAR = 3, "Март"
        APR = 4, "Апрель"
        MAY = 5, "Май"
        JUN = 6, "Июнь"
        JUL = 7, "Июль"
        AUG = 8, "Август"
        SEP = 9, "Сентябрь"
        OCT = 10, "Октябрь"
        NOV = 11, "Ноябрь"
        DEC = 12, "Декабрь"

    month = models.PositiveSmallIntegerField(
        choices=Month.choices, verbose_name="Месяц"
    )

    year = models.PositiveSmallIntegerField(verbose_name="Год")

    class Meta:
        abstract = True


class UserMonthStat(AbstractMonthFields):
    """Месячная статистика пользователя. Запись создается через Celery-beat task."""

    user_profile = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        related_name="month_results",
        verbose_name="Пользователь",
    )

    successfully_done = models.BooleanField(verbose_name="Месяц успешно закрыт")

    class Meta:
        verbose_name = "Статистика по месяцу"
        verbose_name_plural = "Статистика по месяцам"
        constraints = [
            models.UniqueConstraint(
                fields=["user_profile", "month", "year"],
                name="unique_month_stat"
            )
        ]

    def __str__(self):
        return f"{self.user_profile.user.first_name}: {self.month}.{self.year} - {self.successfully_done}"


class UserMonthTarget(AbstractMonthFields):
    """Цель по % комплиту навыка для пользователя. Цель формируется при переподписке пользователя."""

    user_profile = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        related_name="month_targets",
        verbose_name="Пользователь",
    )

    skill = models.ForeignKey(
        "courses.Skill",
        on_delete=models.CASCADE,
        related_name="months_result",
        verbose_name="Навык",
    )
    percentage_of_completion = models.PositiveSmallIntegerField(
        verbose_name="Необходимый % комплита",
        help_text="Цель по навыку до конца текущего месяца",
    )

    class Meta:
        verbose_name = "Месячная цель пользователя"
        verbose_name_plural = "Месячные цели пользователей"
        constraints = [
            models.UniqueConstraint(
                fields=["user_profile", "skill", "month", "year"],
                name="unique_month_target",
            )
        ]

    def __str__(self):
        return f"{self.user_profile.user.first_name}: {self.month}.{self.year} - {self.percentage_of_completion}"


class UserAnswersAttemptCounter(models.Model):
    user_profile = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        related_name="attemps_counter",
        verbose_name="Пользователь",
    )
    task_object = models.ForeignKey(
        "courses.TaskObject",
        on_delete=models.CASCADE,
        related_name="users_attempts",
        verbose_name="Объект задачи",
    )
    attempts_made_before = models.SmallIntegerField(
        default=1,
        validators=[MinValueValidator(0)],
        help_text="Количество попыток ответа до подсказки",
    )
    is_take_hint = models.BooleanField(
        default=False,
        help_text="Получил ли подсказку",
    )
    attempts_made_after = models.SmallIntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Количество попыток ответа после подсказки",
    )

    class Meta:
        verbose_name = "Попытки ответа пользователя"
        verbose_name_plural = "Попытки ответа пользователя"
        unique_together = ("user_profile", "task_object")
