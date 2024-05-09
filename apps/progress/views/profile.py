from django.core.exceptions import ValidationError
from drf_spectacular.utils import extend_schema
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView
from rest_framework import permissions


from courses.models import Skill
from procollab_skills.decorators import exclude_auth_perm, exclude_sub_check_perm

from progress.models import UserProfile, CustomUser
from progress.serializers import (
    ResponseSerializer,
    HollowSerializer,
    IntegerListSerializer,
    UserSerializer,
)
from progress.services import get_user_data, get_current_level, last_two_months_stats


# TODO разобраться с выводом очков


@exclude_sub_check_perm
class UserProfileList(generics.ListAPIView):
    serializer_class = ResponseSerializer
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        summary="""Выводит все данные для страницы профиля пользователя""",
        tags=["Профиль"],
    )
    def get(self, request, *args, **kwargs):
        # profile_id = UserProfile.objects.get(user_id=self.request.user.id).id
        profile_id = 1

        user_data = get_user_data(profile_id)

        skills_and_levels = get_current_level(profile_id)

        # months_stats = cache.get(f"months_data_{profile_id}", None)
        # if months_stats is None:
        months_stats = last_two_months_stats(profile_id)
        # cache.set(f"months_data_{profile_id}", months_stats, MONTHS_CACHING_TIMEOUT)

        data = {"user_data": user_data} | {"skills": skills_and_levels} | {"months": months_stats}
        return Response(data, status=200)


@extend_schema(
    summary="""Выбор навыков из тех, которые юзерв  прошлом трогал""",
    request=IntegerListSerializer,
    responses={204: HollowSerializer},
    tags=["Профиль"],
)
class UserChooseSkills(generics.UpdateAPIView):
    serializer_class = ...
    permission_classes = [permissions.AllowAny]

    def update(self, request, *args, **kwargs):
        try:
            # user_profile = UserProfile.objects.get(user_id=self.request.user.id)
            user_profile = UserProfile.objects.get(user_id=1)

            skills = Skill.objects.filter(id__in=request.data)

            user_profile.chosen_skills.add(*skills)
            return Response("success", status=status.HTTP_204_NO_CONTENT)
        except ValidationError as e:  # для случая, если юзер выбрал больше 5-ти
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    summary="""Регистрация пользователя""",
    tags=["api"],
    request=UserSerializer,
)
@exclude_auth_perm
class CreateUserView(CreateAPIView):
    model = CustomUser
    permission_classes = [permissions.AllowAny]
    serializer_class = UserSerializer
