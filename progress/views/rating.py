# GET топ юзеров по очкам (фильтр по году месяцу дню)
from django.db.models import Sum, Q
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status
from rest_framework.response import Response

from courses.models import Skill
from progress.models import UserProfile
from progress.pagination import DefaultPagination
from progress.serializers import SkillScoreSerializer, UserScoreSerializer
from progress.services import UserScoreRatingFilter


@extend_schema(
    tags=["Рейтинг"],
    summary="Топ юзеров по количеству очков.",
    parameters=[
        OpenApiParameter(
            name="chosen_skills",
            description="Фильтр по выбранным навыкам",
            required=False,
            type=OpenApiTypes.STR,
            style='form',
            explode=True,
        ),
        OpenApiParameter(
            name="time_frame",
            description="Фильтр по временным рамкам (last_day, last_month, last_year)",
            required=False,
            type=OpenApiTypes.STR,
            style='form',
            explode=True,
        )
    ]
)
class UserScoreRating(generics.ListAPIView):
    serializer_class = UserScoreSerializer
    pagination_class = DefaultPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = UserScoreRatingFilter

    def get_queryset(self):
        user_queries = (
            UserProfile.objects.select_related("user")
            .annotate(score_count=Sum("chosen_skills__tasks__task_objects__user_results__points_gained"))
            .order_by("-score_count")
        )
        return user_queries


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
        # TODO добавить авторизацию
        profile_id = self.kwargs.get("profile_id")
        profile_id = 1

        user_skills = (
            Skill.objects.prefetch_related("profile_skills")
            .filter(
                Q(profile_skills__id=profile_id) | Q(tasks__task_objects__user_results__user_profile__id=profile_id)
            )
            .annotate(score_count=Sum("tasks__task_objects__user_results__points_gained"))
            .order_by("-score_count")
            .distinct()
        )

        paginator = self.pagination_class()
        paginated_data = paginator.paginate_queryset(user_skills, self.request)

        data = [{"skill_name": skill.name, "score_count": skill.score_count} for skill in paginated_data]
        return Response(data, status=status.HTTP_200_OK)