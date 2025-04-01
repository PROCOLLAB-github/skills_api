from datetime import date, timedelta

from django.utils import timezone
from rest_framework import serializers

from courses.models import Skill
from courses.serializers import (SkillDetailsSerializer,
                                 SkillNameAndLogoSerializer)
from progress.models import UserSkillDone
from trajectories.models import (Meeting, Month, Trajectory,
                                 UserIndividualSkill, UserTrajectory)


class TrajectoryIdSerializer(serializers.Serializer):
    trajectory_id = serializers.IntegerField(source="trajectory.id", write_only=True)
    user_trajectory_id = serializers.IntegerField(source="id", read_only=True)

    class Meta:
        model = Trajectory
        fields = ["user_trajectory_id", "trajectory_id"]


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
    duration_months = serializers.IntegerField()

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
            "duration_months",
        ]

    def get_is_active_for_user(self, obj):
        """
        Проверка, активна ли траектория для текущего пользователя.
        """
        user = self.context["request"].user
        active_trajectory = UserTrajectory.objects.filter(
            user=user, trajectory=obj, is_active=True
        ).exists()
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
    mentor_first_name = serializers.CharField(
        source="mentor.first_name", allow_null=True
    )
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
            UserSkillDone.objects.filter(user_profile=user.profiles).values_list(
                "skill_id", flat=True
            )
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
                    available_skills.append(
                        {"skill": skill, "overdue": month.order < months_passed + 1}
                    )
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
            {
                **SkillDetailsSerializer(item["skill"]).data,
                "overdue": item["overdue"],
                "is_done": False,
            }
            for item in breakdown["available_skills"]
        ]

    def get_unavailable_skills(self, obj):
        breakdown = self.get_skills_breakdown(obj)
        return [
            {
                **SkillDetailsSerializer(skill).data,
                "is_done": False,
            }
            for skill in breakdown["unavailable_skills"]
        ]

    def get_completed_skills(self, obj):
        breakdown = self.get_skills_breakdown(obj)
        return [
            {**SkillDetailsSerializer(skill).data, "is_done": True}
            for skill in breakdown["completed_skills"]
        ]

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
            age = (
                today.year
                - obj.age.year
                - ((today.month, today.day) < (obj.age.month, obj.age.day))
            )
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
    meeting_id = serializers.SerializerMethodField()

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
            "meeting_id",
        ]

    def get_meeting_id(self, obj):
        meeting = obj.meetings.first()
        return meeting.id if meeting else None

    def get_initial_meeting(self, obj):
        return obj.meetings.filter(initial_meeting=True).exists()

    def get_final_meeting(self, obj):
        return obj.meetings.filter(final_meeting=True).exists()

    def get_remaining_days(self, obj):
        return obj.get_remaining_days()


class MeetingUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для обновления встречи"""

    meeting_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Meeting
        fields = [
            "meeting_id",
            "initial_meeting",
            "final_meeting",
        ]

    def validate_meeting_id(self, value):
        """Проверяем, существует ли встреча с таким ID"""
        if not Meeting.objects.filter(id=value).exists():
            raise serializers.ValidationError("Встреча с таким ID не найдена.")
        return value


class IndividualSkillStatusSerializer(SkillDetailsSerializer):
    is_done = serializers.SerializerMethodField()
    overdue = serializers.SerializerMethodField()

    class Meta:
        model = Skill
        fields = (
            "id",
            "name",
            "file_link",
            "skill_preview",
            "skill_point_logo",
            "description",
            "quantity_of_levels",
            "free_access",
            "is_done",
            "overdue",
        )

    def get_is_done(self, obj):
        if UserSkillDone.objects.filter(skill=obj):
            return True
        else:
            return False

    def get_overdue(self, obj):
        start_date = self.context.get("start_date")
        if start_date:
            if start_date + timedelta(days=30) < timezone.now():
                return True
            else:
                return False


class UserIndividualSkillSerializer(serializers.ModelSerializer):
    skills = serializers.SerializerMethodField()

    class Meta:
        model = UserIndividualSkill
        fields = ("skills",)

    def get_skills(self, obj):
        """Сериализует список навыков для месяца."""
        skills = obj.skills.all()
        serializer = IndividualSkillStatusSerializer(
            skills, many=True, context={"start_date": obj.start_date}
        )
        return serializer.data
