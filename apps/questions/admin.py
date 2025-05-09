from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django_summernote.admin import SummernoteModelAdmin

from courses.models import Skill, Task, TaskObject
from questions.models import (AnswerConnect, AnswerSingle, InfoSlide,
                              QuestionConnect, QuestionSingleAnswer,
                              QuestionWrite)


class AbstractQuestionShowcase(admin.ModelAdmin):
    """Абстарктная модель для вопросов."""

    list_display = ("id", "short_description", "related_task_object", "related_skill")

    def short_description(self, obj) -> str:
        """Сокращенное описание вопроса."""
        return obj.description[:50] + "..." if len(obj.description) > 50 else obj.description
    short_description.short_description = "Описание"

    def related_task_object(self, obj) -> int | None:
        """ID части задачи, если вопрос уже привязан."""
        content_type: ContentType = ContentType.objects.get_for_model(obj)
        try:
            task_object: TaskObject = TaskObject.objects.get(content_type=content_type, object_id=obj.id)
            return task_object.id
        except TaskObject.DoesNotExist:
            return None
        except TaskObject.MultipleObjectsReturned:
            return "Ошибка заполнения, 1 вопрос указан у двух разных TaskObject"
    related_task_object.short_description = "ID части задачи"

    def related_skill(self, obj) -> Skill | None:
        """Навык к которому относится вопрос, если он привязан."""
        task_object_id: int = self.related_task_object(obj)
        if task_object_id and isinstance(task_object_id, int):
            task: Task = TaskObject.objects.get(id=task_object_id).task
            return task.skill if task else None
    related_skill.short_description = "Навык"


class ConnectAnswersInline(admin.StackedInline):  # Или TabularInline для другого стиля отображения
    model = AnswerConnect
    extra = 0
    fieldsets = (
        (None, {
            "fields": (("connect_left", "file_left"), ("connect_right", "file_right")),
            "classes": ("wide",),
        }),
    )


@admin.register(QuestionConnect)
class QuestionConnectAdmin(AbstractQuestionShowcase, SummernoteModelAdmin):
    inlines = [ConnectAnswersInline]
    fieldsets = (
        (
            "Вопрос",
            {
                "fields": (
                    "text",
                    "description",
                    "video_url",
                    "files",
                )
            },
        ),
        (
            (
                "Подсказка: 1) Без подсказки - оставить все пустым; "
                "2) Без подсказки, но с попытками к ответу: `Попытки до подсказки`; "
                "3) С подсказкой в конце, но без попыток после подсказки: оставить пустым `Попытки после подсказки`;."

            ),
            {
                "fields": (
                    "hint_text",
                    "attempts_before_hint",
                    "attempts_after_hint",
                )
            }
        ),
    )


class SingleAnswersInline(admin.StackedInline):
    model = AnswerSingle
    extra = 0


@admin.register(QuestionSingleAnswer)
class QuestionSingleAnswerAdmin(AbstractQuestionShowcase, SummernoteModelAdmin):
    inlines = [SingleAnswersInline]
    fieldsets = (
        (
            "Вопрос",
            {
                "fields": (
                    "text",
                    "description",
                    "video_url",
                    "files",
                    "is_exclude",
                )
            },
        ),
        (
            "Подсказка (если не требуется, необходимо `Attempts before hint` оставить пустым)",
            {
                "fields": (
                    "hint_text",
                    "attempts_before_hint",
                    "attempts_after_hint",
                )
            }
        ),
    )


@admin.register(InfoSlide)
class InfoSlideAdmin(AbstractQuestionShowcase, SummernoteModelAdmin):

    def short_description(self, obj) -> str:
        """Сокращенное описание вопроса."""
        return obj.description[:50] + "..." if len(obj.description) > 50 else obj.description
    short_description.short_description = "Описание"


@admin.register(QuestionWrite)
class QuestionWriteAdmin(AbstractQuestionShowcase, SummernoteModelAdmin):
    pass
