from datetime import date

from django.utils import timezone
from rest_framework import serializers

from courses.models import Skill
from courses.serializers import (SkillDetailsSerializer,
                                 SkillNameAndLogoSerializer)
from progress.models import UserSkillDone

from .models import Month, Trajectory, UserTrajectory


class TrajectoryIdSerializer(serializers.Serializer):
    user_trajectory_id = serializers.IntegerField(source="id")


class TrajectoryStudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trajectory
        fields = ["id", "name", "avatar"]


class TrajectorySerializer(serializers.ModelSerializer):
    is_active_for_user = serializers.SerializerMethodField()
    skills = serializers.SerializerMethodField()
    company = serializers.CharField(read_only=True)
    background_color = serializers.CharField(read_only=True)
    button_color = serializers.CharField(read_only=True)
    select_button_color = serializers.CharField(read_only=True)
    text_color = serializers.CharField(read_only=True)

    class Meta:
        model = Trajectory
        fields = [
            "id",
            "name",
            "description",
            "is_active_for_user",
            "avatar",
            "mentors",
            "skills",
            "company",
            "background_color",
            "button_color",
            "select_button_color",
            "text_color",
        ]

    def get_is_active_for_user(self, obj):
        """
        Проверка, активна ли траектория для текущего пользователя.
        """
        user = self.context["request"].user
        active_trajectory = UserTrajectory.objects.filter(user=user, trajectory=obj, is_active=True).exists()
        return active_trajectory

    def get_skills(self, obj):
        """
        Получение первых 5 уникальных навыков для траектории из всех месяцев.
        """
        skills = Skill.objects.filter(month__trajectory=obj).distinct()[:5]
        return SkillNameAndLogoSerializer(skills, many=True).data


class MonthSerializer(serializers.ModelSerializer):
    skills = serializers.SerializerMethodField()

    class Meta:
        model = Month
        fields = ["order", "skills"]

    def get_skills(self, obj):
        """Сериализует список навыков для месяца."""
        return [skill.name for skill in obj.skills.all()]


class UserTrajectorySerializer(serializers.ModelSerializer):
    trajectory_id = serializers.IntegerField(source="trajectory.id")
    mentor_avatar = serializers.SerializerMethodField()
    mentor_first_name = serializers.CharField(source="mentor.first_name", allow_null=True)
    mentor_last_name = serializers.CharField(source="mentor.last_name", allow_null=True)
    mentor_id = serializers.IntegerField(source="mentor.id", allow_null=True)
    first_meeting_done = serializers.SerializerMethodField()
    final_meeting_done = serializers.SerializerMethodField()
    available_skills = serializers.SerializerMethodField()
    unavailable_skills = serializers.SerializerMethodField()
    completed_skills = serializers.SerializerMethodField()
    active_month = serializers.SerializerMethodField()
    end_date = serializers.SerializerMethodField()
    company = serializers.CharField(source="trajectory.company")
    duration_months = serializers.IntegerField(source="trajectory.duration_months")
    background_color = serializers.CharField(source="trajectory.background_color")
    button_color = serializers.CharField(source="trajectory.button_color")
    select_button_color = serializers.CharField(source="trajectory.select_button_color")
    text_color = serializers.CharField(source="trajectory.text_color")

    class Meta:
        model = UserTrajectory
        fields = [
            "trajectory_id",
            "start_date",
            "end_date",
            "is_active",
            "mentor_first_name",
            "mentor_last_name",
            "mentor_id",
            "mentor_avatar",
            "first_meeting_done",
            "final_meeting_done",
            "available_skills",
            "unavailable_skills",
            "completed_skills",
            "active_month",
            "company",
            "duration_months",
            "background_color",
            "button_color",
            "select_button_color",
            "text_color",
        ]

    def get_mentor_avatar(self, obj):
        profile = getattr(obj.mentor, "profiles", None)
        return profile.file.url if profile and profile.file else None

    def get_first_meeting_done(self, obj):
        return any(meeting.initial_meeting for meeting in obj.meetings.all())

    def get_final_meeting_done(self, obj):
        return obj.meetings.filter(final_meeting=True).exists()

    def get_active_month(self, obj):
        current_date = timezone.now().date()
        return (current_date - obj.start_date).days // 30 + 1

    def get_skills_breakdown(self, obj):
        user = self.context["request"].user
        current_date = timezone.now().date()
        months_passed = (current_date - obj.start_date).days // 30
        completed_skills_ids = set(
            UserSkillDone.objects.filter(user_profile=user.profiles).values_list("skill_id", flat=True)
        )
        available_skills = []
        unavailable_skills = []
        completed_skills_list = []
        for month in obj.trajectory.months.all():
            is_accessible = month.order <= months_passed + 1
            for skill in month.skills.all():
                if skill.id in completed_skills_ids:
                    completed_skills_list.append(skill)
                elif is_accessible:
                    available_skills.append({"skill": skill, "overdue": month.order < months_passed + 1})
                else:
                    unavailable_skills.append(skill)
        return {
            "available_skills": available_skills,
            "unavailable_skills": unavailable_skills,
            "completed_skills": completed_skills_list,
        }

    def get_available_skills(self, obj):
        breakdown = self.get_skills_breakdown(obj)
        return [
            {**SkillDetailsSerializer(item["skill"]).data, "overdue": item["overdue"]}
            for item in breakdown["available_skills"]
        ]

    def get_unavailable_skills(self, obj):
        breakdown = self.get_skills_breakdown(obj)
        return SkillDetailsSerializer(breakdown["unavailable_skills"], many=True).data

    def get_completed_skills(self, obj):
        breakdown = self.get_skills_breakdown(obj)
        return SkillDetailsSerializer(breakdown["completed_skills"], many=True).data

    def get_end_date(self, obj):
        months_count = obj.trajectory.months.count()
        if months_count == 0:
            return None
        return obj.start_date + timezone.timedelta(days=months_count * 30)


class StudentSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    age = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()
    specialization = serializers.CharField()

    def get_age(self, obj):
        if obj.age:
            today = date.today()
            age = today.year - obj.age.year - ((today.month, today.day) < (obj.age.month, obj.age.day))
            return age
        return None

    def get_avatar(self, obj):
        if file := obj.profiles.file:
            return file.link


class MentorStudentSerializer(serializers.ModelSerializer):
    student = StudentSerializer(source="user")
    initial_meeting = serializers.SerializerMethodField()
    final_meeting = serializers.SerializerMethodField()
    remaining_days = serializers.SerializerMethodField()
    trajectory = TrajectoryStudentSerializer()
    user_trajectory_id = serializers.IntegerField(source="id")
    mentor_id = serializers.IntegerField(source="mentor.id", allow_null=True)

    class Meta:
        model = UserTrajectory
        fields = [
            "student",
            "initial_meeting",
            "final_meeting",
            "remaining_days",
            "trajectory",
            "user_trajectory_id",
            "mentor_id",
        ]

    def get_initial_meeting(self, obj):
        return obj.meetings.filter(initial_meeting=True).exists()

    def get_final_meeting(self, obj):
        return obj.meetings.filter(final_meeting=True).exists()

    def get_remaining_days(self, obj):
        return obj.get_remaining_days()
