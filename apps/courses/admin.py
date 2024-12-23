from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django import forms
from django.db.models import Q
from django.utils.html import format_html

from courses.models import Skill, Task, TaskObject, Popup
from questions.models import QuestionSingleAnswer


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "quantity_of_levels",
        "status",
        "free_access",
    )


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "skill",
        "level",
        "status",
        "week",
        "free_access",
    )
    list_filter = ["week"]


class TaskObjectForm(forms.ModelForm):
    content_type = forms.ModelChoiceField(
        queryset=ContentType.objects.filter(
            Q(app_label="questions", model="infoslide")
            | Q(app_label="questions", model="questionconnect")
            | Q(app_label="questions", model="questionsingleanswer")
            | Q(app_label="questions", model="questionwrite")
        ),
        label="Content Type",
    )

    class Meta:
        model = TaskObject
        fields = "__all__"


@admin.register(TaskObject)
class TaskObjectAdmin(admin.ModelAdmin):
    form = TaskObjectForm
    ordering = ("-task__id",)
    filter_horizontal = ("popup",)
    list_display = (
        "id",
        "task_name",
        "question_type",
        "validate_answer",
        "has_popups",
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

    def has_popups(self, obj):
        return obj.popup.exists()
    has_popups.boolean = True


@admin.register(Popup)
class PopupAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "popup_title",
        "popup_text",
        "popup_file_link",
        "task_object_ids",
    )

    def popup_title(self, obj):
        return self.trim_text(obj.title)

    def popup_text(self, obj):
        return self.trim_text(obj.text)

    def popup_file_link(self, obj):
        if obj.file:
            return format_html(f'<a href="{obj.file.link}">{obj.file.link}</a>')
        return "-"

    def task_object_ids(self, obj):
        return list(obj.task_objects.values_list("id", flat=True)) or "-"

    def trim_text(self, text):
        return text[:30] if text else "-"
