import json
from datetime import datetime, timedelta

import jwt
import requests
from jwt import ExpiredSignatureError

from rest_framework import permissions, status
from rest_framework.exceptions import PermissionDenied

from procollab_skills import settings
from progress.exceptions import UserDoesNotExistException
from progress.models import UserProfile, CustomUser


class IfSubscriptionOutdatedAndAuthenticated(permissions.BasePermission):
    """
    Два пермишена были объеденины в один, чтобы сэкономить на запросе получения пользователя
    """

    @staticmethod
    def _is_authenticated(user) -> bool:
        if not bool(user and user.is_authenticated):
            raise PermissionDenied("Учетные данные не были предоставлены.")
        return True

    @staticmethod
    def _is_subscription_valid(view, user) -> bool:
        skip_middleware = getattr(view, "_skip_check_sub", False)
        if skip_middleware:
            return True

        user_sub_date = UserProfile.objects.only("last_subscription_date").get(user=user).last_subscription_date
        thirty_days_ago = datetime.now().date() - timedelta(days=30)
        if user_sub_date <= thirty_days_ago:
            raise PermissionDenied("Подписка просрочена.")
        return True

    def has_permission(self, request, view):
        user = request.user

        skip_auth_middleware = getattr(view, "_skip_auth", False)
        if skip_auth_middleware:
            return True
        return self._is_authenticated(user) and self._is_subscription_valid(view, user)


class AuthCheck(permissions.BasePermission):
    """
    Проверка JWT юзера через основной Procollab
    """

    # TODO переписать, и сделать так, чтобы в jwt хранился только email, а не id и email
    @staticmethod
    def _check_exists_skills(view, email: str) -> bool:
        if user := CustomUser.objects.filter(email=email).first():
            view.user = user
            view.user_profile = UserProfile.objects.get(user=user)
            view.profile_id = view.user_profile.id
            return True
        return False

    @staticmethod
    def _check_exists_procollab(view, email: str) -> bool:
        user_procollab_response = requests.get("https://dev.procollab.ru/auth/users/clone-data", data={"email": email})
        if user_procollab_response.status_code == status.HTTP_200_OK:
            data = json.loads(user_procollab_response.content)[0]
            user = CustomUser.objects.create(
                email=data["email"],
                is_superuser=data["is_superuser"],
                first_name=data["first_name"],
                last_name=data["last_name"],
                password=data["password"],
            )
            view.user = user
            view.user_profile = UserProfile.objects.get(user=user)
            view.profile_id = view.user_profile.id
            return True
        raise UserDoesNotExistException()

    def has_permission(self, request, view):
        token: str = request.META.get("HTTP_AUTHORIZATION")

        if not token:
            raise PermissionDenied({"error": "User credentials are not given"})

        try:
            decoded_token: dict = jwt.decode(token[7:], settings.SECRET_KEY, algorithms=["HS256"])
        except ExpiredSignatureError:
            raise PermissionDenied("Token is expired")
        email = decoded_token.get("email")

        return self._check_exists_skills(view, email) or self._check_exists_procollab(view, email)
