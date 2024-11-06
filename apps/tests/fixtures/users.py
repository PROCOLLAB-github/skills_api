from datetime import timedelta
from unittest.mock import patch

import pytest
from model_bakery import baker
from django.utils import timezone
from rest_framework.test import APIClient

from progress.models import UserProfile
from progress.serializers import CustomObtainPairSerializer


@pytest.fixture
def user():
    return baker.make("progress.CustomUser")


@pytest.fixture
def user_with_trial_sub(user):
    """Пользователь с активной НЕ просроченной подпиской."""
    with patch("progress.tasks.create_user_monts_target.delay"):
        profile: UserProfile = user.profiles
        profile.bought_trial_subscription = True
        profile.last_subscription_date = timezone.now().date()
        profile.save()
    return user


# @pytest.fixture
# def user_with_trial_sub_token():
#     with patch("progress.tasks.create_user_monts_target.delay"):
#         user = baker.make("progress.CustomUser")
#         profile: UserProfile = user.profiles
#
#         profile.bought_trial_subscription = True
#         profile.last_subscription_date = datetime.now().date()
#         profile.save()
#
#         return str(CustomObtainPairSerializer.get_token(user))


@pytest.fixture
def user_with_overdue_trial_sub(user):
    """Пользователь с активной ПРОСРОЧЕННОЙ подпиской."""
    with patch("progress.tasks.create_user_monts_target.delay"):
        profile: UserProfile = user.profiles
        profile.bought_trial_subscription = True
        profile.last_subscription_date = timezone.now().date() - timedelta(days=31)
        profile.save()
    return user


@pytest.fixture
def user_with_old_sub(user):
    """Пользователь с активной подпиской (более 22 дня назад)."""
    with patch("progress.tasks.create_user_monts_target.delay"):
        profile: UserProfile = user.profiles
        profile.bought_trial_subscription = True
        profile.last_subscription_date = timezone.now().date() - timedelta(days=22)
        profile.save()
    return user


@pytest.fixture
def api_auth_with_sub_client(user_with_trial_sub):
    """Клиент с активной НЕ просроченной подпиской."""
    client = APIClient()
    token = CustomObtainPairSerializer.get_token(user_with_trial_sub)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    return client


@pytest.fixture
def api_auth_with_overdue_sub_client(user_with_overdue_trial_sub):
    """Клиент с активной ПРОСРОЧЕННОЙ подпиской."""
    client = APIClient()
    token = CustomObtainPairSerializer.get_token(user_with_overdue_trial_sub)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    return client


@pytest.fixture
def api_auth_without_sub_client(user):
    """Клиент БЕЗ подписки."""
    client = APIClient()
    token = CustomObtainPairSerializer.get_token(user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    return client


@pytest.fixture
def api_auth_with_old_sub_client(user_with_old_sub):
    """Клиент БЕЗ подписки."""
    client = APIClient()
    token = CustomObtainPairSerializer.get_token(user_with_old_sub)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    return client


@pytest.fixture
def api_anonymous_client():
    """Анонимный клинет."""
    return APIClient()
