from django.contrib import admin

from .models import TaskObjUserResult, CustomUser, UserProfile, IntermediateUserSkills


@admin.register(TaskObjUserResult)
class TaskAdmin(admin.ModelAdmin):
    ordering = ("-datetime_created",)


@admin.register(CustomUser)
class UserAdmin(admin.ModelAdmin):
    pass


class IntermediateUserSkillsInline(admin.TabularInline):
    model = IntermediateUserSkills
    extra = 0


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    inlines = [IntermediateUserSkillsInline]
    list_display = ("id",)  # Замените "some_other_field" на реальные поля UserProfile
