from django.contrib import admin

from .models import TaskObjUserResult, UserTest, UserProfile


@admin.register(TaskObjUserResult)
class TaskAdmin(admin.ModelAdmin):
    ordering = ("-datetime_created",)


@admin.register(UserTest)
class UserTestAdmin(admin.ModelAdmin):
    pass


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    pass
