from django.db.models import Sum, Q
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status
from rest_framework.response import Response

from courses.models import Skill
from progress.models import UserProfile
from progress.pagination import DefaultPagination
from progress.serializers import SkillScoreSerializer, UserScoreSerializer
from progress.filters import UserScoreRatingFilter


@extend_schema(
    tags=["Рейтинг"],
    summary="Топ юзеров по количеству очков.",
    parameters=[
        OpenApiParameter(
            name="skills",
            description="Фильтр по выбранным навыкам",
            required=False,
            type=OpenApiTypes.STR,
            style="form",
            explode=True,
        ),
        OpenApiParameter(
            name="time_frame",
            description="Фильтр по временным рамкам (last_day, last_month, last_year)",
            required=True,
            type=OpenApiTypes.STR,
            style="form",
            explode=True,
        ),
    ],
)
class UserScoreRating(generics.ListAPIView):
    serializer_class = UserScoreSerializer
    pagination_class = DefaultPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = UserScoreRatingFilter
    queryset = UserProfile.objects.select_related("user", "file")


class UserSkillsRating(generics.ListAPIView):
    serializer_class = SkillScoreSerializer
    pagination_class = DefaultPagination

    @extend_schema(
        summary="Топ навыков юзера по количеству очков",
        description="""Пока не выводит уровень. Этим я потом займусь.""",
        tags=["Рейтинг"],
    )
    def get(self, request, *args, **kwargs):
        # TODO добавить отображение уровней у навыков
        user_skills = (
            Skill.published.filter(intermediateuserskills__user_profile__id=self.profile_id)
            .annotate(
                score_count=Sum(
                    "tasks__task_objects__user_results__points_gained",
                    filter=Q(tasks__task_objects__user_results__user_profile_id=self.profile_id),
                )
            )
            .distinct()
            .order_by("-score_count")
        )

        paginated_data = self.pagination_class().paginate_queryset(user_skills, self.request)

        data = [
            {
                "skill_name": skill.name,
                "score_count": skill.score_count,
                "file": skill.file.link,
            }
            for skill in paginated_data
        ]
        return Response(data, status=status.HTTP_200_OK)
