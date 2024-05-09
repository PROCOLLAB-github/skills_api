# GET топ юзеров по очкам (фильтр по году месяцу дню)
from django.db.models import Sum, Q
from drf_spectacular.utils import extend_schema
from rest_framework import generics, status
from rest_framework.response import Response

from courses.models import Skill
from procollab_skills.decorators import exclude_auth_perm
from progress.models import UserProfile
from progress.pagination import DefaultPagination
from progress.serializers import SkillScoreSerializer, UserScoreSerializer


@exclude_auth_perm
class UserScoreRating(generics.ListAPIView):
    serializer_class = UserScoreSerializer
    pagination_class = DefaultPagination

    @extend_schema(
        summary="Топ юзеров по количеству очков",
        description="""Пока что фильтры не реализованы, это позже""",
        tags=["Рейтинг"],
    )
    def get(self, request, *args, **kwargs):
        user_queries = (
            UserProfile.objects.select_related("user", "user__file")
            .annotate(score_count=Sum("chosen_skills__tasks__task_objects__user_results__points_gained"))
            .order_by("-score_count")
        )
        # TODO добавить фильтры день месяц год
        # TODO добавить фильтр по конкретным навыкам
        paginator = self.pagination_class()
        paginated_data = paginator.paginate_queryset(user_queries, self.request)

        data = [
            {
                "user_name": user_profile.user.first_name + " " + user_profile.user.last_name,
                "age": user_profile.user.age,
                "specializtion": user_profile.user.specialization,
                "geo_position": user_profile.user.geo_position,
                "score_count": user_profile.score_count,
                "file": user_profile.file.link,
            }
            for user_profile in paginated_data
        ]

        return Response(data, status=status.HTTP_200_OK)


@exclude_auth_perm
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
        profile_id = UserProfile.objects.get(user_id=self.request.user.id).id

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

        data = [
            {
                "skill_name": skill.name,
                "score_count": skill.score_count,
                "file": skill.file.link,
            }
            for skill in paginated_data
        ]
        return Response(data, status=status.HTTP_200_OK)
