# Стандартные библиотеки
import json
import requests

# Django
from django.core.exceptions import ValidationError
from files.models import FileModel
from django.http import HttpRequest
from courses.models import Skill
from progress.models import CustomUser, IntermediateUserSkills
from procollab_skills import settings

# Django REST Framework
from rest_framework import (
    generics,
    status,
    permissions,
)
from rest_framework.generics import (
    CreateAPIView,
    ListAPIView,
    UpdateAPIView,
    get_object_or_404,
)
from rest_framework.response import Response

# drf_spectacular
from drf_spectacular.utils import extend_schema, OpenApiResponse

# Локальные приложения
from progress.services import (
    get_user_data,
    get_user_profile_skills_progress,
    get_user_profile_months_stats,
)
from progress.typing import (
    UserProfileDataDict,
    UserSkillsProgressDict,
    UserMonthsProgressDict,
)
from progress.serializers import (
    ProfileResponseSerializer,
    HollowSerializer,
    IntegerListSerializer,
    UserSerializer,
    SubProclong,
    CustomUserSerializer,
)
from subscription.serializers import UserSubscriptionDataSerializer


class UserProfile(generics.RetrieveAPIView):
    serializer_class = ProfileResponseSerializer

    @extend_schema(
        summary="""Выводит все данные для страницы профиля пользователя""",
        tags=["Профиль"],
    )
    def get(self, request, *args, **kwargs):
        # TODO подумать над кэшированием.
        user_data: UserProfileDataDict = get_user_data(self.user_profile.id)
        skills_stats: list[UserSkillsProgressDict] = get_user_profile_skills_progress(
            self.user_profile.id,
            self.request.user,
        )
        months_stats: list[UserMonthsProgressDict] = get_user_profile_months_stats(self.user_profile.id)
        data = {"user_data": user_data} | {"skills": skills_stats} | {"months": months_stats}
        return Response(data, status=status.HTTP_200_OK)


@extend_schema(
    summary="""Выбор навыков из тех, которые юзер в прошлом трогал""",
    request=IntegerListSerializer,
    responses={204: HollowSerializer},
    tags=["Профиль"],
)
class UserChooseSkills(generics.UpdateAPIView):
    serializer_class = ...

    def update(self, request, *args, **kwargs):
        try:
            skills = Skill.published.for_user(self.request.user).filter(id__in=request.data)

            IntermediateUserSkills.objects.bulk_create(
                [IntermediateUserSkills(user_profile=self.user_profile, skill=skill) for skill in skills]
            )
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

    def get(self, request, *args, **kwargs):
        serializer = self.serializer_class(self.user_profile, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(
    summary="""Изменить статус авто-продления подписки""",
    tags=["Профиль"],
)
class UpdateAutoRenewal(UpdateAPIView):
    serializer_class = SubProclong

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
        serialized_data["is_mentor"] = user.mentored_trajectories.exists()

        return Response(serialized_data, status=status.HTTP_200_OK)


class SyncUserProfile(generics.GenericAPIView):
    """
    API-эндпоинт для синхронизации данных пользователя между сервисами Skills и Procollab.
    """

    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="Синхронизация данных профиля skills с сервисом procollab",
        responses={
            status.HTTP_200_OK: OpenApiResponse(
                description="Данные успешно синхронизированы",
                examples={"application/json": {"message": "Данные успешно синхронизированы"}},
            ),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                description="Ошибка при получении данных",
                examples={"application/json": {"error": "Ошибка получения данных от procollab"}},
            ),
            status.HTTP_401_UNAUTHORIZED: OpenApiResponse(
                description="Неавторизованный доступ",
                examples={"application/json": {"error": "Неавторизованный доступ"}},
            ),
        },
        tags=["Профиль"],
    )
    def post(self, request: HttpRequest, *args, **kwargs) -> Response:
        """
        Обработчик POST-запроса для синхронизации профиля.

        Процесс синхронизации включает:
        1. Получение данных пользователя из Procollab
        2. Обновление информации в профиле Skills
        3. Обработку ошибок и возвращение соответствующего ответа
        """
        try:
            procollab_data = self._fetch_procollab_data(request.user.email)
            self._update_user_profile(request.user, procollab_data)
            return Response("Данные успешно синхронизированы")
        except Exception as e:
            return self._handle_error(e)

    def _fetch_procollab_data(self, email: str) -> dict:
        """
        Получение данных пользователя из сервиса Procollab.

        Args:
            email (str): Email пользователя для поиска в Procollab
        """
        url_name = "dev" if settings.DEBUG else "api"
        response = requests.get(f"https://{url_name}.procollab.ru/auth/users/clone-data", data={"email": email})

        if response.status_code != status.HTTP_200_OK:
            raise ValueError("Ошибка получения данных от procollab")

        return json.loads(response.content)[0]

    def _update_user_profile(self, user: CustomUser, data: dict) -> None:
        """
        Обновление данных профиля пользователя в сервисе Skills.

        Args:
            user (CustomUser): Объект пользователя для обновления
            data (dict): Данные из Procollab для обновления профиля

        Updates:
            - Личные данные пользователя (имя, фамилия, отчество)
            - Информацию о городе и специализации
            - Дату рождения
            - Аватар профиля (если предоставлен)
        """
        user_fields = {
            "first_name": data["first_name"],
            "last_name": data["last_name"],
            "patronymic": data["patronymic"],
            "city": data["city"],
            "age": data["birthday"],
            "specialization": data["speciality"],
        }
        for field, value in user_fields.items():
            setattr(user, field, value)
        user.save()

        user_profile = self.user_profile
        if avatar_url := data.get("avatar"):
            file_instance, _ = FileModel.objects.get_or_create(
                link=avatar_url,
                defaults={
                    "user": user,
                    "name": "avatar",
                    "extension": avatar_url.split(".")[-1],
                },
            )
            user_profile.file = file_instance
        user_profile.save()

    def _handle_error(self, error: Exception) -> Response:
        """
        Обработчик ошибок для эндпоинта синхронизации.
        """
        return Response({"error": str(error)}, status=status.HTTP_400_BAD_REQUEST)
