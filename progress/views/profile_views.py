from drf_spectacular.utils import extend_schema
from rest_framework import generics, status
from rest_framework.response import Response

from courses.models import Skill
from progress.models import UserProfile
from progress.serializers import ResponseSerializer, HollowSerializer, IntegerListSerializer
from progress.services import get_user_data, get_current_level

# TODO разобраться с выводом очков


class UserProfileList(generics.ListAPIView):
    serializer_class = ResponseSerializer

    @extend_schema(
        summary="""Выводит все данные для страницы профиля пользователя""",
        tags=["Профиль"]
    )
    def get(self, request, *args, **kwargs):
        profile_id = self.kwargs.get("profile_id")
        profile_id = 1
        # TODO добавить авторизацию


        user_data = get_user_data(profile_id)
        skills_and_levels, months = get_current_level(profile_id)

        data = {"user_data" :user_data} | {"skills": skills_and_levels} | {"months": months}
        return Response(data, status=200)


@extend_schema(
    summary="""Выбор навыков из тех, которые юзерв  прошлом трогал""",
    request=IntegerListSerializer,
    responses={204: HollowSerializer},
    tags=["Профиль"]
)
class UserChooseSkills(generics.UpdateAPIView):
    serializer_class = ...

    def update(self, request, *args, **kwargs):
        profile_id = self.kwargs.get("profile_id")
        profile_id = 1
        # TODO добавить авторизацию
        user_profile = UserProfile.objects.get(id=profile_id)
        skills = Skill.objects.filter(id__in=request.data)

        user_profile.chosen_skills.add(*skills)
        return Response("success", status=status.HTTP_204_NO_CONTENT)