from django.contrib import admin

from courses.models import *


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    pass


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    pass


@admin.register(TaskObject)
class TaskObjectAdmin(admin.ModelAdmin):
    ordering = ("-task__id", "ordinal_number")
    list_display = ("id",  "task_object_text", "task_name", "ordinal_number", )

    def task_name(self, obj):
        return obj.task.name

    def task_object_text(self, obj):
        return f"{obj.content_object.text[:20]}..."


@admin.register(QuestionConnect)
class QuestionConnectAdmin(admin.ModelAdmin):
    pass


@admin.register(ConnectAnswer)
class ConnectAnswerAdmin(admin.ModelAdmin):
    pass


@admin.register(QuestionSingleAnswer)
class QuestionSingleAnswerAdmin(admin.ModelAdmin):
    pass


@admin.register(SingleAnswer)
class SingleAnswerAdmin(admin.ModelAdmin):
    pass


@admin.register(InfoSlide)
class InfoSlideAdmin(admin.ModelAdmin):
    pass
