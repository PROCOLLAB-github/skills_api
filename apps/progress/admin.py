from django import forms
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

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj and obj.file:
            form.base_fields["avatar_url_custom"].initial = obj.file.link
        return form
