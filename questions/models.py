from django.db import models

from files.models import UserFile


class AbstractQuestion(models.Model):
    text = models.CharField(max_length=100)
    description = models.TextField(null=True)
    files = models.ManyToManyField(UserFile, related_name="question", blank=True)

    class Meta:
        abstract = True



class QuestionSingleAnswer(AbstractQuestion):
    files = models.ManyToManyField(
        UserFile, related_name="single_questions", blank=True
    )

    class Meta:
        verbose_name = "Вопрос с одним правильным ответов"
        verbose_name_plural = "Вопросы с одним правильным ответов"


class QuestionConnect(AbstractQuestion):
    files = models.ManyToManyField(
        UserFile, related_name="connect_questions", blank=True
    )

    class Meta:
        verbose_name = "Вопрос на соотношение"
        verbose_name_plural = "Вопросы на соотношение"



class SingleAnswer(models.Model):
    text = models.CharField(max_length=100, null=False)
    is_correct = models.BooleanField(default=False)
    question = models.ForeignKey(
        QuestionSingleAnswer,
        on_delete=models.CASCADE,
        related_name="single_answers",
    )

    class Meta:
        verbose_name = "Ответ для вопроса с одним правильным ответом"
        verbose_name_plural = "Ответы для вопроса с одним правильным ответом"


class ConnectAnswer(models.Model):
    connect_left = models.CharField(max_length=50, null=False)
    connect_right = models.CharField(max_length=50, null=False)
    question = models.ForeignKey(
        QuestionConnect,
        on_delete=models.CASCADE,
        related_name="connect_answers",
    )

    class Meta:
        verbose_name = "Ответ для вопроса на соотношение"
        verbose_name_plural = "Ответы для вопроса на соотношение"



class InfoSlide(models.Model):
    text = models.TextField()
    files = models.ManyToManyField(UserFile, related_name="info_slides", blank=True)

    class Meta:
        verbose_name = "Информационный слайд"
        verbose_name_plural = "Информационные слайды"
