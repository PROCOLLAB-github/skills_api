from django.contrib import admin
from django.contrib.contenttypes.models import ContentType

from questions.models import (
    QuestionSingleAnswer,
    AnswerSingle,
    InfoSlide,
    QuestionConnect,
    AnswerConnect,
    QuestionWrite,
)

from courses.models import TaskObject, Skill, Task


class AbstractQuestionShowcase(admin.ModelAdmin):
    """Абстарктная модель для вопросов."""

    list_display = ("id", "short_description", "related_task_object", "related_skill")

    def short_description(self, obj) -> str:
        """Сокращенное описание вопроса."""
        return (
            obj.description[:50] + "..."
            if len(obj.description) > 50
            else obj.description
        )

    short_description.short_description = "Описание"

    def related_task_object(self, obj) -> int | None:
        """ID части задачи, если вопрос уже привязан."""
        content_type: ContentType = ContentType.objects.get_for_model(obj)
        try:
            task_object: TaskObject = TaskObject.objects.get(
                content_type=content_type, object_id=obj.id
            )
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


class ConnectAnswersInline(
    admin.StackedInline
):  # Или TabularInline для другого стиля отображения
    model = AnswerConnect
    extra = 0
    fieldsets = (
        (
            None,
            {
                "fields": (
                    ("connect_left", "file_left"),
                    ("connect_right", "file_right"),
                ),
                "classes": ("wide",),
            },
        ),
    )



class TextEditorMixin:
    formfield_overrides = {
        models.CharField: {"widget": SummernoteWidget},
    }




@admin.register(QuestionConnect)
class QuestionConnectAdmin(AbstractQuestionShowcase):
    inlines = [ConnectAnswersInline]


    formfield_overrides = {
        models.CharField: {"widget": SummernoteWidget},
    }



class SingleAnswersInline(admin.StackedInline):
    model = AnswerSingle
    extra = 0


@admin.register(QuestionSingleAnswer)
class QuestionSingleAnswerAdmin(AbstractQuestionShowcase):
    inlines = [SingleAnswersInline]


@admin.register(InfoSlide)
class InfoSlideAdmin(AbstractQuestionShowcase, TextEditorMixin):

    def short_description(self, obj) -> str:
        """Сокращенное описание вопроса."""
        return obj.text[:50] + "..." if len(obj.text) > 50 else obj.text

    short_description.short_description = "Описание"


@admin.register(QuestionWrite)
class QuestionWriteAdmin(AbstractQuestionShowcase):
    pass
