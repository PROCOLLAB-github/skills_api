from django.db.models import Prefetch, QuerySet
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from courses.models import Skill
from courses.serializers import SkillDetailsSerializer
from progress.models import UserSkillDone
from subscription.permissions import SubscriptionSectionPermission

from .models import Trajectory
from .serializers import TrajectorySerializer


@extend_schema(
    summary="Выводит все траектории на платформе, помечает активные для пользователя",
    tags=["Траектории"],
)
class TrajectoryListView(generics.ListAPIView):
    serializer_class = TrajectorySerializer
    permission_classes = [IsAuthenticated, SubscriptionSectionPermission]

    def get_queryset(self) -> QuerySet[Trajectory]:
        """
        Возвращает все траектории. Для каждой траектории будет помечено, активна ли она для текущего пользователя.
        """
        return Trajectory.objects.all()


@extend_schema(
    summary="Получает информацию о траектории по её ID",
    tags=["Траектории"],
)
class TrajectoryDetailView(generics.RetrieveAPIView):
    serializer_class = TrajectorySerializer
    permission_classes = [IsAuthenticated, SubscriptionSectionPermission]
    lookup_field = "id"

    def get_queryset(self) -> QuerySet[Trajectory]:
        """
        Возвращает траекторию по её ID.
        """
        return Trajectory.objects.all()


@extend_schema(
    summary="Получает три набора навыков: доступные, выполненные, будущие",
    tags=["Траектории"],
)
class TrajectorySkillsView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    lookup_field = "id"

    def get_queryset(self):
        """Предзагружаем траектории с месяцами и навыками."""
        return Trajectory.objects.prefetch_related(Prefetch("months__skills", queryset=Skill.objects.all()))

    def retrieve(self, request, *args, **kwargs):
        """Разделяет навыки на доступные, недоступные и выполненные."""
        trajectory = self.get_object()
        user = request.user
        current_date = timezone.now().date()

        # Получаем список выполненных навыков
        completed_skills = set(
            UserSkillDone.objects.filter(user_profile=user.profiles).values_list("skill_id", flat=True)
        )

        # Определяем текущий месяц пользователя
        active_trajectory = user.user_trajectories.filter(is_active=True).first()
        if not active_trajectory:
            return Response(
                {"error": "У пользователя нет активной траектории"},
                status=400,
            )

        trajectory_start_date = active_trajectory.start_date
        months_passed = (current_date - trajectory_start_date).days // 30

        available_skills = []
        unavailable_skills = []
        completed_skills_list = []

        for month in trajectory.months.all():
            is_accessible = month.order <= months_passed + 1

            for skill in month.skills.all():
                if skill.id in completed_skills:
                    completed_skills_list.append(skill)
                elif is_accessible:
                    available_skills.append(
                        {
                            "skill": skill,
                            "overdue": month.order < months_passed + 1,
                        }
                    )
                else:
                    unavailable_skills.append(skill)

        return Response(
            {
                "available_skills": [
                    {**SkillDetailsSerializer(skill_data["skill"]).data, "overdue": skill_data["overdue"]}
                    for skill_data in available_skills
                ],
                "unavailable_skills": SkillDetailsSerializer(unavailable_skills, many=True).data,
                "completed_skills": SkillDetailsSerializer(completed_skills_list, many=True).data,
            }
        )
