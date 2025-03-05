from django.contrib import admin

from .models import Meeting, Month, Trajectory, UserTrajectory


@admin.register(Trajectory)
class TrajectoryAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "company",
        "start_date",
        "duration_months",
    )
    list_filter = ("company", "start_date",)
    search_fields = ("name", "company",)
    autocomplete_fields = ("mentors",)

    def get_mentors(self, obj):
        return ", ".join([mentor.email for mentor in obj.mentors.all()])

    get_mentors.short_description = "Наставники"


@admin.register(Month)
class MonthAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "trajectory",
        "skills_list",
    )
    list_filter = ("trajectory",)
    search_fields = ("trajectory__name",)
    autocomplete_fields = ("skills",)

    def skills_list(self, obj):
        return ", ".join(skill.name for skill in obj.skills.all())

    skills_list.short_description = "Навыки"


@admin.register(UserTrajectory)
class UserTrajectoryAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "trajectory_name",
        "start_date",
        "is_active",
        "mentor",
    )
    list_filter = ("is_active", "trajectory",)
    search_fields = ("user__email", "trajectory__name",)
    autocomplete_fields = ("mentor",)

    def trajectory_name(self, obj):
        return obj.trajectory.name

    trajectory_name.short_description = "Траектория"


@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user_trajectory_user_email",
        "initial_meeting",
        "final_meeting",
    )
    readonly_fields = ("user_trajectory",)
    list_filter = ("initial_meeting", "final_meeting",)
    search_fields = ("user_trajectory__user__email",)

    def user_trajectory_user_email(self, obj):
        return obj.user_trajectory.user.email

    user_trajectory_user_email.short_description = "Пользователь"
