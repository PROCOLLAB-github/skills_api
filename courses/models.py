from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType


class Skill(models.Model):
    name = models.CharField(max_length=50, verbose_name="Название навыка")
    # who created
    # picture of who created
    # quantity of levels

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = "Навык"
        verbose_name_plural = "Навыки"


class Task(models.Model):
    name = models.CharField(max_length=50, verbose_name="Название")
    skill = models.ForeignKey(
        Skill,
        on_delete=models.CASCADE,
        related_name="tasks",
        verbose_name="Навык"
    )
    level = models.IntegerField(default=1, verbose_name="Уровень")

    def __str__(self):
        return f"{self.name} {self.skill.name} {self.level}"

    class Meta:
        verbose_name = "Задача"
        verbose_name_plural = "Задачи"


class TaskObject(models.Model):
    ordinal_number = models.PositiveSmallIntegerField(
        null=True,
        verbose_name="Порядковый номер"
    )
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name="task_objects",
        verbose_name="Задача"
    )

    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        related_name="task_objects_content",
        verbose_name="Тип единицы задачи"
    )
    object_id = models.PositiveIntegerField(verbose_name="ID единицы задачи")
    content_object = GenericForeignKey("content_type", "object_id")

    def __str__(self):
        return f"{self.task.name} {self.ordinal_number}"

    class Meta:
        verbose_name = "Часть задачи"
        verbose_name_plural = "Части задачи"

    # TODO сделать функцию, которая автоматически при методе
    #  save будет делать ordinal number больше самого последнего ordinal number на 1

    # TODO сделать валидацию и то, что выше
