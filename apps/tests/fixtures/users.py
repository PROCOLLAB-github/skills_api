from datetime import timedelta
from unittest.mock import patch

import pytest
from model_bakery import baker
from django.utils import timezone

from progress.models import (
    UserProfile,
    CustomUser,
)


@pytest.fixture
def user():
    return baker.make("progress.CustomUser")


@pytest.fixture
def user_admin():
    return baker.make("progress.CustomUser", is_superuser=True)


@pytest.fixture
def user_staff():
    return baker.make("progress.CustomUser", is_staff=True)


@pytest.fixture
def user_with_trial_sub(user: CustomUser):
    """Пользователь с активной НЕ просроченной подпиской."""
    with patch("progress.tasks.create_user_monts_target.delay"):
        profile: UserProfile = user.profiles
        profile.bought_trial_subscription = True
        profile.last_subscription_date = timezone.now().date()
        profile.save()
    return user


@pytest.fixture
def user_with_overdue_trial_sub(user: CustomUser):
    """Пользователь с активной ПРОСРОЧЕННОЙ подпиской."""
    with patch("progress.tasks.create_user_monts_target.delay"):
        profile: UserProfile = user.profiles
        profile.bought_trial_subscription = True
        profile.last_subscription_date = timezone.now().date() - timedelta(days=31)
        profile.save()
    return user


@pytest.fixture
def user_with_old_sub(user: CustomUser):
    """Пользователь с активной подпиской (более 22 дня назад)."""
    with patch("progress.tasks.create_user_monts_target.delay"):
        profile: UserProfile = user.profiles
        profile.bought_trial_subscription = True
        profile.last_subscription_date = timezone.now().date() - timedelta(days=22)
        profile.save()
    return user


@pytest.fixture
def user_admin_with_trial_sub(user_admin: CustomUser):
    """Админ с активной НЕ просроченной подпиской."""
    with patch("progress.tasks.create_user_monts_target.delay"):
        profile: UserProfile = user_admin.profiles
        profile.bought_trial_subscription = True
        profile.last_subscription_date = timezone.now().date()
        profile.save()
    return user_admin


@pytest.fixture
def user_staff_with_trial_sub(user_staff: CustomUser):
    """Персонал с активной НЕ просроченной подпиской."""
    with patch("progress.tasks.create_user_monts_target.delay"):
        profile: UserProfile = user_staff.profiles
        profile.bought_trial_subscription = True
        profile.last_subscription_date = timezone.now().date()
        profile.save()
    return user_staff
