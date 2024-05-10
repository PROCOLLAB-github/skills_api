from django.contrib import admin

from .models import TaskObjUserResult, CustomUser, UserProfile


@admin.register(TaskObjUserResult)
class TaskAdmin(admin.ModelAdmin):
    ordering = ("-datetime_created",)


@admin.register(CustomUser)
class UserAdmin(admin.ModelAdmin):
    pass


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("id",)
