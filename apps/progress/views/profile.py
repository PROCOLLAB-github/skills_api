from django.core.exceptions import ValidationError
from drf_spectacular.utils import extend_schema
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView, ListAPIView, UpdateAPIView
from rest_framework import permissions

from courses.models import Skill


from procollab_skills.permissions import IfSubscriptionOutdatedPermission

from progress.models import CustomUser
from progress.serializers import (
    ResponseSerializer,
    HollowSerializer,
    IntegerListSerializer,
    UserSerializer,
    SubProclong,
)
from subscription.serializers import UserSubscriptionDataSerializer
from progress.services import get_user_data, get_current_level, last_two_months_stats


# TODO разобраться с выводом очков


class UserProfileList(generics.ListAPIView):
    serializer_class = ResponseSerializer
    permission_classes = [AllowAny]

    @extend_schema(
        summary="""Выводит все данные для страницы профиля пользователя""",
        tags=["Профиль"],
    )
    def get(self, request, *args, **kwargs):
        user_data = get_user_data(self.user_profile.id)

        skills_and_levels = get_current_level(self.user_profile.id)

        # months_stats = cache.get(f"months_data_{profile_id}", None)
        # if months_stats is None:
        months_stats = last_two_months_stats(self.user_profile.id)
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
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        serializer = self.serializer_class(self.user_profile)
        return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(
    summary="""Изменить статус авто-продления подписки""",
    tags=["Профиль"],
)
class UpdateAutoRenewal(UpdateAPIView):
    serializer_class = SubProclong
    permission_classes = [AllowAny]

    def patch(self, request, *args, **kwargs):
        new_status = request.data.get("is_autopay_allowed")

        self.user_profile.is_autopay_allowed = new_status
        self.user_profile.save()

        return Response(status=204)
