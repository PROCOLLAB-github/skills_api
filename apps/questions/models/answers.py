from django.db import models
from django.core.exceptions import ValidationError

from files.models import FileModel
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
    connect_left = models.CharField(max_length=50, null=True, blank=True, verbose_name="Вопрос (текст)")
    connect_right = models.CharField(max_length=50, null=True, blank=True, verbose_name="Ответ (текст)")
    file_left = models.ForeignKey(
        FileModel,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="connect_answers_withimages_left",
        verbose_name="Вопрос (Картинка)",
    )
    file_right = models.ForeignKey(
        FileModel,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="connect_answers_withimages_right",
        verbose_name="Ответ (Картинка)",
    )
    question = models.ForeignKey(
        QuestionConnect,
        on_delete=models.CASCADE,
        related_name="connect_answers",
    )

    class Meta:
        verbose_name = "Ответ для вопроса на соотношение"
        verbose_name_plural = "Ответы для вопроса на соотношение"

    def clean(self):
        """Проверка на заполненность полей."""
        if not (self.connect_left or self.file_left):
            raise ValidationError("Необходимо заполнить хотя бы одно из полей 'Вопрос'.")
        if not (self.connect_right or self.file_right):
            raise ValidationError("Необходимо заполнить хотя бы одно из полей 'Ответ'.")
        if (self.connect_left and self.file_left) or (self.connect_right and self.file_right):
            raise ValidationError("Заполните только одно из полей 'Вопрос' или 'Ответ'.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


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
