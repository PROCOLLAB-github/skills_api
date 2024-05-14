from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django import forms
from django.db.models import Q

from courses.models import Skill, Task, TaskObject
from questions.models import QuestionSingleAnswer


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    pass


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    pass


class TaskObjectForm(forms.ModelForm):
    content_type = forms.ModelChoiceField(
        queryset=ContentType.objects.filter(
            Q(app_label="questions", model="infoslide")
            | Q(app_label="questions", model="questionconnect")
            | Q(app_label="questions", model="questionsingleanswer")
            | Q(app_label="questions", model="questionwrite")
            | Q(app_label="questions", model="writequestion")
        ),
        label="Content Type",
    )

    class Meta:
        model = TaskObject
        fields = "__all__"


@admin.register(TaskObject)
class TaskObjectAdmin(admin.ModelAdmin):
    form = TaskObjectForm
    ordering = ("-task__id", "ordinal_number")
    list_display = (
        "id",
        "task_name",
        "question_type",
        "ordinal_number",
    )
    list_filter = ["task__name"]

    def task_name(self, obj):
        return obj.task.name

    def question_type(self, obj):
        if isinstance(obj.content_object, QuestionSingleAnswer) and obj.content_object.is_exclude:
            return f"{obj.content_type} (Исключающий)"
        else:
            return obj.content_type

    question_type.short_description = "тип единицы задачи"
    task_name.short_description = "наименование задачи"
