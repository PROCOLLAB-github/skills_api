from django.db import models

from files.models import FileModel


class AbstractQuestion(models.Model):
    text = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)

    class Meta:
        abstract = True


class QuestionSingleAnswer(AbstractQuestion):
    files = models.ManyToManyField(FileModel, related_name="single_questions", blank=True)
    is_exclude = models.BooleanField(
        help_text="Если этот вопрос является типом 'исключить неправильное', поставить на True", default=False
    )

    class Meta:
        verbose_name = "Вопрос с одним правильным ответов"
        verbose_name_plural = "Вопросы с одним правильным ответов"


class QuestionConnect(AbstractQuestion):
    files = models.ManyToManyField(FileModel, related_name="connect_questions", blank=True)

    class Meta:
        verbose_name = "Вопрос на соотношение"
        verbose_name_plural = "Вопросы на соотношение"


class InfoSlide(models.Model):
    text = models.TextField()
    files = models.ManyToManyField(FileModel, related_name="info_slides", blank=True)

    class Meta:
        verbose_name = "Информационный слайд"
        verbose_name_plural = "Информационные слайды"


class WriteQuestion(AbstractQuestion):
    class Meta:
        verbose_name = "Вопрос на ввод ответа"
        verbose_name_plural = "Вопросы на ввод ответа"
