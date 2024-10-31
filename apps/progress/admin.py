from django import forms
from django.contrib import admin

from .filters import AdminUserSubscriptionFilter
from .models import (
    TaskObjUserResult,
    CustomUser,
    UserProfile,
    IntermediateUserSkills,
    UserSkillDone,
    UserWeekStat,
    UserMonthStat,
    UserMonthTarget,
)


@admin.register(TaskObjUserResult)
class TaskAdmin(admin.ModelAdmin):
    ordering = ("-datetime_created",)
    list_display = ("id", "task_object", "user_profile", "datetime_created")


@admin.register(CustomUser)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "email",
        "first_name",
        "last_name",
    )
    list_display_links = (
        "id",
        "email",
        "first_name",
        "last_name",
    )
    search_fields = (
        "email",
        "first_name",
        "last_name",
    )


class IntermediateUserSkillsInline(admin.TabularInline):
    model = IntermediateUserSkills
    extra = 0


class UserProfileForm(forms.ModelForm):
    avatar_url_custom = forms.CharField(
        label="Avatar URL",
        required=False,
        widget=forms.TextInput(attrs={"readonly": "readonly"}),
    )

    class Meta:
        model = UserProfile
        fields = "__all__"


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    form = UserProfileForm
    inlines = (IntermediateUserSkillsInline,)
    list_display = (
        "user",
        "last_subscription_date",
    )
    search_fields = (
        "user__email",
        "user__first_name",
        "user__last_name",
    )
    list_filter = [AdminUserSubscriptionFilter]

    def get_name(self):
        return f"{self.obj.first_name} {self.obj.last_name}"

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj and obj.file:
            form.base_fields["avatar_url_custom"].initial = obj.file.link
        return form


@admin.register(UserSkillDone)
class UserSkillDoneAdmin(admin.ModelAdmin):
    list_display = ("id", "user_profile", "skill", "additional_points")
    list_filter = ["skill"]


@admin.register(UserWeekStat)
class UserWeekStatAdmin(admin.ModelAdmin):
    list_display = ("id", "user_profile", "skill", "week", "is_done")
    list_filter = ["skill", "week"]


@admin.register(UserMonthStat)
class UserMonthStatAdmin(admin.ModelAdmin):
    list_display = ("id", "user_profile", "month", "year", "successfully_done")
    list_filter = ["month", "year"]


@admin.register(UserMonthTarget)
class UserMonthTargetAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user_profile",
        "skill",
        "month",
        "year",
        "percentage_of_completion",
    )
    list_filter = ["skill", "month", "year"]
