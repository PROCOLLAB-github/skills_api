from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Max

from courses.managers import AvailableForUser, PublishedManager
from files.models import FileModel
from subscription.models import SubscriptionType


class AbstractStatusField(models.Model):
    STATUS_CHOICES = [
        ("draft", "Черновик"),
        ("published", "Опубликован"),
        ("stuff_only", "Доступ только у персонала"),
    ]

    status = models.CharField(
        choices=STATUS_CHOICES,
        max_length=15,
        default="draft",
        verbose_name="Статус",
    )
    free_access = models.BooleanField(
        default=False,
        null=False,
        blank=False,
        verbose_name="Доступ бесплатно",
        help_text="Возможность проходить без подписки.",
    )

    objects = models.Manager()
    published = PublishedManager()

    class Meta:
        abstract = True


class Skill(AbstractStatusField):
    is_from_trajectory = models.BooleanField(
        default=False,
        verbose_name="Из траектории",
        help_text="Указывает, что навык доступен только в рамках траектории.",
    )
    requires_subscription = models.BooleanField(
        default=False,
        verbose_name="Требует подписку",
        help_text="Определяет, необходима ли подписка для доступа к навыку.",
    )
    name = models.CharField(max_length=50, verbose_name="Название навыка")
    description = models.TextField(null=True)
    who_created = models.CharField(max_length=50, verbose_name="Кто создал")
    file = models.ForeignKey(
        FileModel,
        on_delete=models.SET_NULL,
        related_name="skill",
        verbose_name="Основоное лого",
        null=True,
        blank=True,
    )
    skill_preview = models.ForeignKey(
        FileModel,
        on_delete=models.SET_NULL,
        related_name="skill_preview",
        verbose_name="Лого навыка в уровне",
        null=True,
        blank=True,
    )
    skill_point_logo = models.ForeignKey(
        FileModel,
        on_delete=models.SET_NULL,
        related_name="skill_point_logo",
        verbose_name="Лого навыка в строке прогресса",
        null=True,
        blank=True,
    )
    quantity_of_levels = models.IntegerField(default=0)
    subcription_type = models.ForeignKey(
        SubscriptionType,
        blank=True,
        help_text="Минимальный тип подписки, с которой навык становится доступен",
        null=True,
        on_delete=models.SET_NULL,
        verbose_name="Тип подписки",
    )

    class Meta:
        verbose_name = "Навык"
        verbose_name_plural = "Навыки"

    def __str__(self):
        return f"{self.name}"

    def clean(self):
        from django.core.exceptions import ValidationError

        if self.free_access and (self.requires_subscription or self.is_from_trajectory):
            raise ValidationError(
                "Навык не может быть одновременно бесплатным и требовать подписку или принадлежать траектории."
            )

        super().clean()

    def save(self, *args, **kwargs):
        if self.pk is None:  # Проверка, сохранен ли объект в базе данных
            super().save(
                *args, **kwargs
            )  # Если объект еще не сохранен, сохраняем его сначала

        quantity_unique_levels = (
            Task.objects.filter(skill=self).values("level").distinct().count()
        )
        self.quantity_of_levels = quantity_unique_levels

        super().save(*args, **kwargs)


class Task(AbstractStatusField):
    WEEK_CHOICES = [
        (1, "1 Неделя"),
        (2, "2 Неделя"),
        (3, "3 Неделя"),
        (4, "4 Неделя (До конца месяца)"),
    ]
    ordinal_number = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name="Порядковый номер",
        help_text="Если не указать, то автоматически станет последним в порядке показа",
    )
    name = models.CharField(max_length=50, verbose_name="Название")
    skill = models.ForeignKey(
        Skill, on_delete=models.CASCADE, related_name="tasks", verbose_name="Навык"
    )
    level = models.IntegerField(default=1, verbose_name="Уровень")
    week = models.PositiveSmallIntegerField(
        choices=WEEK_CHOICES, default=1, verbose_name="Неделя"
    )

    objects = models.Manager()
    available = AvailableForUser()

    def __str__(self):
        return f"name:<{self.name}> skill:<{self.skill.name}> level:<{self.level}>"

    class Meta:
        verbose_name = "Задача"
        verbose_name_plural = "Задачи"

    def save(self, *args, **kwargs):
        """Автоматически устанавливает порядковый номер"""
        if self.ordinal_number is None:  # если порядковый номер слайда не введен
            last_task_obj = Task.objects.aggregate(Max("ordinal_number"))
            if not last_task_obj.get("ordinal_number__max", 0):
                last_task_obj["ordinal_number__max"] = 0
            self.ordinal_number = last_task_obj.get("ordinal_number__max", 0) + 1
        super().save(*args, **kwargs)


class TaskObject(models.Model):
    ordinal_number = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name="Порядковый номер",
        help_text="Если не указать, то автоматически станет последним в порядке показа",
    )
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name="task_objects",
        verbose_name="Задача",
    )
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        related_name="task_objects_content",
        verbose_name="Тип единицы задачи",
    )
    object_id = models.PositiveIntegerField(verbose_name="ID единицы задачи")
    popup = models.ManyToManyField(
        "Popup", blank=True, related_name="task_objects", verbose_name="Поп-ап"
    )
    content_object = GenericForeignKey("content_type", "object_id")
    validate_answer = models.BooleanField(
        default=True,
        verbose_name="Проверка ответа",
        help_text=(
            "Отключает проверку ответа.<br>"
            "(Только для 'Вопрос с одним правильным ответом', 'Вопрос с одним правильным ответом (Исключающий)' "
            "и 'Вопрос на соотношение', на остальных проверка не требуется)"
        ),
    )

    def __str__(self):
        return f"{self.task.name} {self.ordinal_number}"

    class Meta:
        verbose_name = "Часть задачи"
        verbose_name_plural = "Части задачи"
        unique_together = ("task", "ordinal_number")

    def save(self, *args, **kwargs):
        if self.ordinal_number is None:  # если порядковый номер слайда не введен
            last_task_obj = self.task.task_objects.aggregate(Max("ordinal_number"))
            if not last_task_obj.get("ordinal_number__max", 0):
                last_task_obj["ordinal_number__max"] = 0
            self.ordinal_number = last_task_obj.get("ordinal_number__max", 0) + 1
        super().save(*args, **kwargs)

    # TODO сделать валидацию и то, что выше


class Popup(models.Model):
    title = models.CharField(
        null=True, blank=True, max_length=150, verbose_name="Заголовок"
    )
    text = models.TextField(null=True, blank=True, verbose_name="Содержимое")
    file = models.ForeignKey(
        FileModel,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="popups",
        verbose_name="Изображение",
    )
    ordinal_number = models.PositiveSmallIntegerField(
        null=True, blank=True, verbose_name="Порядковый номер"
    )

    class Meta:
        verbose_name = "Поп-ап"
        verbose_name_plural = "Поп-апы"

    def __str__(self):
        return self.title or self.text or self.file.link

    def clean(self):
        if not self.title and not self.text and not self.file:
            raise ValidationError(
                "Должено быть заполнено хотя бы один из полей: "
                "'Заголовок', 'Содержимое' или 'Изображение'"
            )

    def save(self, *args, **kwargs):
        # TODO автоинкремен и валидация при добалении в TaskObject
        if self.ordinal_number is None:
            self.ordinal_number = 1
        super().save(*args, **kwargs)
