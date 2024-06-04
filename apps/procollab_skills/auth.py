import json

import jwt
import requests
from jwt import ExpiredSignatureError, InvalidSignatureError
from django.db import transaction
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import PermissionDenied, NotAuthenticated

from files.models import FileModel
from procollab_skills import settings
from progress.exceptions import UserDoesNotExistException
from progress.models import UserProfile, CustomUser


class CustomAuth(TokenAuthentication):
    # TODO переписать, и сделать так, чтобы в jwt хранился только email, а не id и email
    @staticmethod
    def _check_exists_skills(view, email: str) -> CustomUser | None:
        if user := CustomUser.objects.filter(email=email).first():
            view.user = user
            view.user_profile = UserProfile.objects.get(user=user)
            view.profile_id = view.user_profile.id
            return user

    @staticmethod
    def _check_exists_procollab(view, email: str) -> CustomUser | None:
        url_name = "dev" if settings.DEBUG else "api"
        user_procollab_response = requests.get(
            f"https://{url_name}.procollab.ru/auth/users/clone-data", data={"email": email}
        )
        if user_procollab_response.status_code == status.HTTP_200_OK:
            data = json.loads(user_procollab_response.content)[0]
            user, user_profile = __class__._create_user_instance_from_data(data)
            view.user = user
            view.user_profile = user_profile
            view.profile_id = view.user_profile.id
            return user

    @staticmethod
    @transaction.atomic
    def _create_user_instance_from_data(data) -> tuple[CustomUser, UserProfile]:
        user: CustomUser = CustomUser.objects.create(
            email=data["email"],
            is_superuser=data["is_superuser"],
            first_name=data["first_name"],
            last_name=data["last_name"],
            password=data["password"],
        )
        user_profile: UserProfile = UserProfile.objects.get(user=user)
        url_procollab_avatar: str = data.get("avatar")
        if url_procollab_avatar:
            file_instanse: FileModel
            created: bool
            file_instanse, created = FileModel.objects.get_or_create(
                link=url_procollab_avatar,
                defaults={
                    "user": user,
                    "name": "avatar",
                    "extension": url_procollab_avatar.split('.')[-1],
                }
            )
            user_profile.file = file_instanse
            user_profile.save()
        return user, user_profile

    def authenticate(self, request) -> tuple[CustomUser, None]:
        view = request.parser_context["view"]

        token: str = request.META.get("HTTP_AUTHORIZATION")

        if not token:
            raise PermissionDenied({"error": "User credentials are not given"})

        try:
            decoded_token: dict = jwt.decode(token[7:], settings.SECRET_KEY, algorithms=["HS256"])
        except ExpiredSignatureError:
            raise NotAuthenticated({"error": "Token is expired"})
        except InvalidSignatureError:
            raise PermissionDenied({"error": "Couldn't decode JWT. Check secret key variable"})

        email = decoded_token.get("email")

        user = self._check_exists_skills(view, email) or self._check_exists_procollab(view, email)
        if user is None:
            raise UserDoesNotExistException()

        return user, None
