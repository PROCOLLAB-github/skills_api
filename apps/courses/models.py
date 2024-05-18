from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Max

from files.models import FileModel


class Skill(models.Model):
    name = models.CharField(max_length=50, verbose_name="Название навыка")
    description = models.TextField(null=True)
    who_created = models.CharField(max_length=50, verbose_name="Кто создал")
    file = models.ForeignKey(
        FileModel, on_delete=models.SET_NULL, related_name="skill", verbose_name="Картинка", null=True, blank=True
    )
    quantity_of_levels = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = "Навык"
        verbose_name_plural = "Навыки"

    def save(self, *args, **kwargs):
        if self.pk is None:  # Проверка, сохранен ли объект в базе данных
            super().save(*args, **kwargs)  # Если объект еще не сохранен, сохраняем его сначала

        quantity_unique_levels = Task.objects.filter(skill=self).values("level").distinct().count()
        self.quantity_of_levels = quantity_unique_levels

        super().save(*args, **kwargs)


class Task(models.Model):
    ordinal_number = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name="Порядковый номер",
        help_text="Если не указать, то автоматически станет последним в порядке показа",
    )
    name = models.CharField(max_length=50, verbose_name="Название")
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name="tasks", verbose_name="Навык")
    level = models.IntegerField(default=1, verbose_name="Уровень")
    # TODO добавить порядковый номер для показа

    def __str__(self):
        return f"name:<{self.name}> skill:<{self.skill.name}> level:<{self.level}>"

    class Meta:
        verbose_name = "Задача"
        verbose_name_plural = "Задачи"


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
        ContentType, on_delete=models.CASCADE, related_name="task_objects_content", verbose_name="Тип единицы задачи"
    )
    object_id = models.PositiveIntegerField(verbose_name="ID единицы задачи")
    content_object = GenericForeignKey("content_type", "object_id")

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
