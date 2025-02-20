from rest_framework import serializers

from .models import Trajectory, UserTrajectory


class TrajectorySerializer(serializers.ModelSerializer):
    is_active_for_user = serializers.SerializerMethodField()

    class Meta:
        model = Trajectory
        fields = ["id", "name", "description", "is_active_for_user", "avatar", "mentors"]

    def get_is_active_for_user(self, obj):
        """
        Проверка, активна ли траектория для текущего пользователя
        """
        user = self.context["request"].user
        active_trajectory = UserTrajectory.objects.filter(user=user, trajectory=obj, is_active=True).exists()
        return active_trajectory
