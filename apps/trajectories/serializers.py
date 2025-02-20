from rest_framework import serializers

from courses.serializers import SkillNameAndLogoSerializer

from .models import Trajectory, UserTrajectory
from courses.models import Skill


class TrajectorySerializer(serializers.ModelSerializer):
    is_active_for_user = serializers.SerializerMethodField()
    skills = serializers.SerializerMethodField()

    class Meta:
        model = Trajectory
        fields = ["id", "name", "description", "is_active_for_user", "avatar", "mentors", "skills"]

    def get_is_active_for_user(self, obj):
        """
        Проверка, активна ли траектория для текущего пользователя
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
