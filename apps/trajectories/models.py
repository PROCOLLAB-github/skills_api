from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from files.models import FileModel

CustomUser = get_user_model()


class Trajectory(models.Model):
    """
    Модель для представления траектории.
    Связана с множеством менторов в виде пользователей.
    """

    name = models.CharField(max_length=50, verbose_name="Название траектории")
    description = models.TextField(verbose_name="Описание траектории")
    avatar = models.ForeignKey(
        FileModel,
        on_delete=models.SET_NULL,
        related_name="avatar",
        verbose_name="Аватар траектории",
        null=True,
        blank=True,
    )
    mentors = models.ManyToManyField(CustomUser, related_name="mentored_trajectories", verbose_name="Наставники")
    start_date = models.DateField(default=timezone.now, verbose_name="Дата начала")
    duration_months = models.IntegerField(verbose_name="Количество месяцев")
    company = models.CharField(max_length=255, verbose_name="Компания")
    background_color = models.CharField(max_length=7, default="#FFFFFF", verbose_name="Цвет заднего фона билета")
    button_color = models.CharField(max_length=7, default="#6c27ff", verbose_name="Цвет кнопки 'Подробнее'")
    select_button_color = models.CharField(max_length=7, default="#6c27ff", verbose_name="Цвет кнопки 'Выбрать'")
    text_color = models.CharField(max_length=7, default="#332e2d", verbose_name="Цвет текста на билете")

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = "Траектория"
        verbose_name_plural = "Траектории"


class Month(models.Model):
    """
    Модель для представления месяца в рамках траектории.
    Связана с траекторией и набором навыков.
    """

    trajectory = models.ForeignKey(Trajectory, on_delete=models.CASCADE, related_name="months")
    skills = models.ManyToManyField("courses.Skill", verbose_name="Навыки")

    def __str__(self):
        return f"Месяц в траектории '{self.trajectory.name}'"

    class Meta:
        verbose_name = "Месяц"
        verbose_name_plural = "Месяцы"


class UserTrajectory(models.Model):
    """
    Модель для связи пользователя с траекторией.
    Каждый пользователь может быть привязан только к одной активной траектории в любой момент времени.
    """

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="user_trajectories")
    trajectory = models.ForeignKey(Trajectory, on_delete=models.CASCADE)
    start_date = models.DateField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    mentor = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name="mentored_users"
    )

    def __str__(self):
        return f"{self.user.email} - {self.trajectory.name}"

    class Meta:
        verbose_name = "Пользовательская траектория"
        verbose_name_plural = "Пользовательские траектории"


class Meeting(models.Model):
    """
    Модель для отражения статуса встреч пользователя с наставником в рамках траектории.
    Могут быть начальные и финальные встречи.
    """

    user_trajectory = models.ForeignKey(UserTrajectory, on_delete=models.CASCADE, related_name="meetings")
    initial_meeting = models.BooleanField(default=False, verbose_name="Начальная встреча")
    final_meeting = models.BooleanField(default=False, verbose_name="Финальная встреча")

    def __str__(self):
        return f"Встречи для {self.user_trajectory.user.email}"

    class Meta:
        verbose_name = "Встреча"
        verbose_name_plural = "Встречи"
