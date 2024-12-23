from datetime import timedelta, datetime

import pytest
from model_bakery import baker
from django.utils import timezone
from django.test import override_settings

from progress.models import (
    UserProfile,
    CustomUser,
)
from subscription.models import SubscriptionType


@pytest.fixture
def user(random_file_intance):
    user = baker.make(
        "progress.CustomUser",
        email="user@example.com",
        first_name="Юзер",
        last_name="Юзер",
        specialization="Специальность",
        age=datetime(year=2000, month=12, day=31, hour=23, minute=23, second=59),
        city="Москва",
    )
    user.profiles.file = random_file_intance
    user.profiles.save()
    return user


@pytest.fixture
@override_settings(task_always_eager=True)
def three_random_user_with_sub():
    users = []
    for _ in range(3):
        user = baker.make("progress.CustomUser")
        profile: UserProfile = user.profiles
        profile.bought_trial_subscription = True
        profile.last_subscription_date = timezone.now().date()
        profile.save()
        users.append(user)
    return users


@pytest.fixture
def user_admin():
    return baker.make(
        "progress.CustomUser",
        is_superuser=True,
        first_name="Админ",
        last_name="Админ",
    )


@pytest.fixture
def user_staff():
    return baker.make(
        "progress.CustomUser",
        is_staff=True,
        first_name="Стафф",
        last_name="Стафф",
    )


@pytest.fixture
@override_settings(task_always_eager=True)
def user_with_trial_sub(user: CustomUser, trying_sub: SubscriptionType):
    """Пользователь с активной пробной НЕ просроченной подпиской."""
    profile: UserProfile = user.profiles
    profile.bought_trial_subscription = True
    profile.last_subscription_type = trying_sub
    profile.last_subscription_date = timezone.now().date()
    profile.save()
    return user


@pytest.fixture
@override_settings(task_always_eager=True)
def user_with_optimum_sub(user: CustomUser, optimum_sub: SubscriptionType):
    """Пользователь с активной оптимум НЕ просроченной подпиской (покупавший пробную)."""
    profile: UserProfile = user.profiles
    profile.bought_trial_subscription = True
    profile.last_subscription_type = optimum_sub
    profile.last_subscription_date = timezone.now().date()
    profile.save()
    return user


@pytest.fixture
@override_settings(task_always_eager=True)
def user_with_overdue_optimum_sub(user: CustomUser, optimum_sub: SubscriptionType):
    """Пользователь с активной оптимум просроченной подпиской (покупавший пробную)."""
    profile: UserProfile = user.profiles
    profile.bought_trial_subscription = True
    profile.last_subscription_type = optimum_sub
    profile.last_subscription_date = timezone.now().date() - timedelta(days=31)
    profile.save()
    return user


@pytest.fixture
@override_settings(task_always_eager=True)
def user_with_overdue_trial_sub(user: CustomUser, trying_sub: SubscriptionType):
    """Пользователь с активной пробной ПРОСРОЧЕННОЙ подпиской."""
    profile: UserProfile = user.profiles
    profile.bought_trial_subscription = True
    profile.last_subscription_type = trying_sub
    profile.last_subscription_date = timezone.now().date() - timedelta(days=31)
    profile.save()
    return user


@pytest.fixture
@override_settings(task_always_eager=True)
def user_with_old_sub(user: CustomUser):
    """Пользователь с активной подпиской (более 22 дня назад)."""
    profile: UserProfile = user.profiles
    profile.bought_trial_subscription = True
    profile.last_subscription_date = timezone.now().date() - timedelta(days=22)
    profile.save()
    return user


@pytest.fixture
@override_settings(task_always_eager=True)
def user_admin_with_trial_sub(user_admin: CustomUser):
    """Админ с активной НЕ просроченной подпиской."""
    profile: UserProfile = user_admin.profiles
    profile.bought_trial_subscription = True
    profile.last_subscription_date = timezone.now().date()
    profile.save()
    return user_admin


@pytest.fixture
@override_settings(task_always_eager=True)
def user_staff_with_trial_sub(user_staff: CustomUser):
    """Персонал с активной НЕ просроченной подпиской."""
    profile: UserProfile = user_staff.profiles
    profile.bought_trial_subscription = True
    profile.last_subscription_date = timezone.now().date()
    profile.save()
    return user_staff


@pytest.fixture
@override_settings(task_always_eager=True)
def user_staff_with_overdue_sub(user_staff: CustomUser):
    """Персонал с активной НЕ просроченной подпиской."""
    profile: UserProfile = user_staff.profiles
    profile.bought_trial_subscription = True
    profile.last_subscription_date = timezone.now().date() - timedelta(days=31)
    profile.save()
    return user_staff
