from django.db import models

from progress.models import UserProfile
from questions.models.questions import QuestionConnect, QuestionSingleAnswer, QuestionWrite


class AnswerSingle(models.Model):
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


class AnswerConnect(models.Model):
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


class AnswerUserWrite(models.Model):
    text = models.TextField(null=False)
    write_question = models.ForeignKey(
        QuestionWrite,
        on_delete=models.CASCADE,
        related_name="write_answers",
    )
    user_profile = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        related_name="write_answer_results",
        verbose_name="Профиль пользователя",
    )

    class Meta:
        verbose_name = "Ответ пользователя для вопроса с текстом"
        verbose_name_plural = "Ответы пользователя для вопросы с текстом"
        unique_together = ("write_question", "user_profile")
