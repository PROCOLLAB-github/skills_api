from django.contrib import admin

from courses.models import Skill, Task, TaskObject


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    pass


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    pass


@admin.register(TaskObject)
class TaskObjectAdmin(admin.ModelAdmin):
    ordering = ("-task__id", "ordinal_number")
    list_display = (
        "id",
        "task_name",
        "ordinal_number",
    )

    def task_name(self, obj):
        return obj.task.name
