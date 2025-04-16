from django.core.exceptions import PermissionDenied
from django.db.models import QuerySet
from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from subscription.permissions import HasActiveSubscription
from trajectories.models import (Meeting, Trajectory, UserIndividualSkill,
                                 UserTrajectory)
from trajectories.serializers import (MeetingUpdateSerializer,
                                      MentorStudentSerializer,
                                      TrajectoryIdSerializer,
                                      TrajectorySerializer,
                                      UserIndividualSkillSerializer,
                                      UserTrajectorySerializer)


@extend_schema(
    summary="Выводит все траектории на платформе, помечает активные для пользователя",
    tags=["Траектории"],
)
class TrajectoryListView(generics.ListAPIView):
    serializer_class = TrajectorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self) -> QuerySet[Trajectory]:
        return Trajectory.objects.all()


@extend_schema(
    summary="Получает информацию о траектории по её ID",
    tags=["Траектории"],
)
class TrajectoryDetailView(generics.RetrieveAPIView):
    serializer_class = TrajectorySerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"

    def get_queryset(self) -> QuerySet[Trajectory]:
        return Trajectory.objects.all()


@extend_schema(
    summary="Получает детальную информацию о траектории пользователя",
    tags=["Траектории"],
)
class UserTrajectoryView(generics.RetrieveAPIView):
    serializer_class = UserTrajectorySerializer
    permission_classes = [IsAuthenticated, HasActiveSubscription]

    def get_object(self):
        user = self.request.user
        return (
            UserTrajectory.objects.prefetch_related(
                "meetings", "trajectory__months__skills"
            )
            .filter(user=user, is_active=True)
            .first()
        )

    def get(self, request, *args, **kwargs):
        user_trajectory = self.get_object()
        if not user_trajectory:
            return Response(
                {"error": "У пользователя нет активной траектории"},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = UserTrajectorySerializer(
            user_trajectory, context={"request": request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(
    summary="Активирует выбранную траекторию для пользователя",
    tags=["Траектории"],
)
class UserTrajectoryCreateView(generics.CreateAPIView):
    serializer_class = TrajectoryIdSerializer
    permission_classes = [IsAuthenticated, HasActiveSubscription]

    def create(self, request, *args, **kwargs):
        user = request.user
        trajectory_id = request.data.get("trajectory_id")

        if UserTrajectory.objects.filter(user=user, is_active=True).exists():
            return Response(
                {"error": "У вас уже есть активная траектория"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        trajectory = Trajectory.objects.filter(id=trajectory_id).first()
        if not trajectory:
            return Response(
                {"error": "Траектория не найдена"}, status=status.HTTP_404_NOT_FOUND
            )

        user_trajectory = UserTrajectory.objects.create(
            user=user,
            trajectory=trajectory,
            start_date=timezone.now().date(),
            is_active=True,
            mentor=None,
        )

        serializer = self.get_serializer(user_trajectory)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@extend_schema(
    summary="Получения списка индивидуальных навыков",
    tags=["Траектории"],
)
class UserIndividualSkillListView(generics.ListAPIView):
    serializer_class = UserIndividualSkillSerializer
    permission_classes = [IsAuthenticated, HasActiveSubscription]

    def get_queryset(self):
        return UserIndividualSkill.objects.filter(user=self.request.user)


@extend_schema(
    summary="Информация о студентах ментора",
    tags=["Траектории"],
)
class MentorStudentsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        mentor = request.user
        trajectories = UserTrajectory.objects.filter(
            mentor=mentor, is_active=True
        ).prefetch_related("meetings")

        serializer = MentorStudentSerializer(trajectories, many=True)

        return Response(serializer.data)


@extend_schema(
    summary="Обновление статуса встреч наставника с учеником",
    tags=["Траектории"],
)
class MeetingUpdateView(APIView):
    """
    API-вью для обновления статуса встреч.
    """

    serializer_class = MeetingUpdateSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = MeetingUpdateSerializer(data=request.data)
        if serializer.is_valid():
            meeting_id = serializer.validated_data["meeting_id"]
            meeting = get_object_or_404(Meeting, id=meeting_id)

            user_trajectory = meeting.user_trajectory

            if user_trajectory.mentor != request.user:
                raise PermissionDenied("У вас нет прав на изменение этой встречи.")

            meeting.initial_meeting = serializer.validated_data["initial_meeting"]
            meeting.final_meeting = serializer.validated_data["final_meeting"]
            meeting.save()

            return Response(
                MeetingUpdateSerializer(meeting).data, status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
