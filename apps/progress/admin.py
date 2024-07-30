from django import forms
from django.contrib import admin


from .models import (
    TaskObjUserResult,
    CustomUser,
    UserProfile,
    IntermediateUserSkills,
    UserSkillDone,
    UserWeekStat,
)


@admin.register(TaskObjUserResult)
class TaskAdmin(admin.ModelAdmin):
    ordering = ("-datetime_created",)
    list_display = ("id", "task_object", "user_profile", "datetime_created")


@admin.register(CustomUser)
class UserAdmin(admin.ModelAdmin):
    pass


class IntermediateUserSkillsInline(admin.TabularInline):
    model = IntermediateUserSkills
    extra = 0


class UserProfileForm(forms.ModelForm):
    avatar_url_custom = forms.CharField(
        label="Avatar URL", required=False, widget=forms.TextInput(attrs={"readonly": "readonly"})
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
