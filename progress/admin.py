from django.contrib import admin
from .models import *


@admin.register(TaskObjUserResult)
class TaskAdmin(admin.ModelAdmin):
    ordering = ("-datetime_created",)


@admin.register(UserTest)
class TaskAdmin(admin.ModelAdmin):
    pass


@admin.register(UserProfile)
class TaskAdmin(admin.ModelAdmin):
    pass
