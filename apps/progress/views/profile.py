import json
import requests

from django.core.exceptions import ValidationError
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView, ListAPIView, UpdateAPIView, get_object_or_404
from drf_spectacular.utils import extend_schema

from courses.models import Skill
from procollab_skills import settings
from progress.models import CustomUser
from progress.services import get_user_data, get_user_profile_skills_progress, get_user_profile_months_stats
from progress.typing import UserProfileDataDict, UserSkillsProgressDict, UserMonthsProgressDict
from progress.serializers import (
    ProfileResponseSerializer,
    HollowSerializer,
    IntegerListSerializer,
    UserSerializer,
    SubProclong,
    CustomUserSerializer,
)
from procollab_skills.permissions import IfSubscriptionOutdatedPermission
from subscription.serializers import UserSubscriptionDataSerializer


class UserProfile(generics.RetrieveAPIView):
    serializer_class = ProfileResponseSerializer
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        summary="""Выводит все данные для страницы профиля пользователя""",
        tags=["Профиль"],
    )
    def get(self, request, *args, **kwargs):
        # TODO подумать над кэшированием.
        user_data: UserProfileDataDict = get_user_data(self.user_profile.id)
        skills_stats: list[UserSkillsProgressDict] = get_user_profile_skills_progress(self.user_profile.id)
        months_stats: list[UserMonthsProgressDict] = get_user_profile_months_stats(self.user_profile.id)
        data = {"user_data": user_data} | {"skills": skills_stats} | {"months": months_stats}
        return Response(data, status=status.HTTP_200_OK)


@extend_schema(
    summary="""Выбор навыков из тех, которые юзерв  прошлом трогал""",
    request=IntegerListSerializer,
    responses={204: HollowSerializer},
    tags=["Профиль"],
)
class UserChooseSkills(generics.UpdateAPIView):
    serializer_class = ...
    permission_classes = [IfSubscriptionOutdatedPermission, permissions.AllowAny]

    def update(self, request, *args, **kwargs):
        try:
            skills = Skill.published.filter(id__in=request.data)

            self.user_profile.chosen_skills.add(*skills)
            return Response("success", status=status.HTTP_204_NO_CONTENT)
        except ValidationError as e:  # для случая, если юзер выбрал больше 5-ти
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    summary="""Регистрация пользователя""",
    tags=["api"],
    request=UserSerializer,
)
class CreateUserView(CreateAPIView):
    model = CustomUser
    permission_classes = [permissions.AllowAny]
    serializer_class = UserSerializer
    authentication_classes = []


@extend_schema(
    summary="""Данные о статусе подписки залогиненного пользователя""",
    tags=["Профиль"],
)
class SubscriptionUserData(ListAPIView):
    serializer_class = UserSubscriptionDataSerializer
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        serializer = self.serializer_class(self.user_profile)
        return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(
    summary="""Изменить статус авто-продления подписки""",
    tags=["Профиль"],
)
class UpdateAutoRenewal(UpdateAPIView):
    serializer_class = SubProclong
    permission_classes = [permissions.AllowAny]

    def patch(self, request, *args, **kwargs):
        new_status = request.data.get("is_autopay_allowed")

        self.user_profile.is_autopay_allowed = new_status
        self.user_profile.save()

        return Response(status=204)


@extend_schema(
    summary="""Получить данные о юзере""",
    tags=["Профиль"],
)
class GetUserProfileData(ListAPIView):
    serializer_class = CustomUserSerializer

    def _get_date_verificated(self) -> str:
        url_name = "dev" if settings.DEBUG else "api"
        data = requests.get(
            f"https://{url_name}.procollab.ru/auth/users/clone-data", data={"email": self.request.user.email}
        )

        return json.loads(data.content)[0]["verification_date"]

    def get(self, request, *args, **kwargs) -> Response:
        user = get_object_or_404(CustomUser.objects.select_related("profiles__file").all(), pk=self.request.user.id)
        serialized_data = self.serializer_class(user).data

        serialized_data["verification_date"] = self._get_date_verificated()

        return Response(serialized_data, status=status.HTTP_200_OK)
