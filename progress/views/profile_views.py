from django.db.models import QuerySet


# GET профиль юзера
# /progress/profile/{user_id}
# response
from drf_spectacular.utils import extend_schema
from rest_framework import generics, status
from rest_framework.response import Response

from courses.models import Skill
from courses.serializers import IntegerListSerializer
from progress.models import UserTest, UserProfile
from progress.serializers import ResponseSerializer, HollowSerializer
from progress.services import get_user_data, get_current_level
# TODO разобраться с выводом очков
a = {
    "user_data": {
        "first_name": str,
        "last_name": str,
        "age": int,
        "specialization": str,
        "geo_position": str
    },
    "skills": {
        int: {  # ключ - это id навыка
            "skill_name": str,
            "level": int
        }
    },
    "months": [
        {
            "month": str, #  название месяца
            "is_passed": bool
        }
    ]
}

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


# PATCH выбор навыков из уже прокаченных на 1 лвл хотя бы
# /progress/choose-skills
# request body:
c = [int]
# response
"204"


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