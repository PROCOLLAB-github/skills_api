import pytest
from rest_framework.test import APIClient

from progress.models import CustomUser
from progress.serializers import CustomObtainPairSerializer


@pytest.fixture
def api_auth_with_sub_client(user_with_trial_sub: CustomUser):
    """Клиент с активной НЕ просроченной подпиской."""
    client = APIClient()
    token = CustomObtainPairSerializer.get_token(user_with_trial_sub)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    return client


@pytest.fixture
def api_auth_with_sub_client_admin(user_admin_with_trial_sub: CustomUser):
    """Клиент(Админ) с активной НЕ просроченной подпиской."""
    client = APIClient()
    token = CustomObtainPairSerializer.get_token(user_admin_with_trial_sub)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    return client


@pytest.fixture
def api_auth_with_sub_client_staff(user_staff_with_trial_sub: CustomUser):
    """Клиент(Админ) с активной НЕ просроченной подпиской."""
    client = APIClient()
    token = CustomObtainPairSerializer.get_token(user_staff_with_trial_sub)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    return client


@pytest.fixture
def api_auth_with_overdue_sub_client(user_with_overdue_trial_sub: CustomUser):
    """Клиент с активной ПРОСРОЧЕННОЙ подпиской."""
    client = APIClient()
    token = CustomObtainPairSerializer.get_token(user_with_overdue_trial_sub)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    return client


@pytest.fixture
def api_auth_without_sub_client(user: CustomUser):
    """Клиент БЕЗ подписки."""
    client = APIClient()
    token = CustomObtainPairSerializer.get_token(user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    return client


@pytest.fixture
def api_auth_with_old_sub_client(user_with_old_sub: CustomUser):
    """Клиент с активной подпиской (более 22 дней назад)."""
    client = APIClient()
    token = CustomObtainPairSerializer.get_token(user_with_old_sub)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    return client


@pytest.fixture
def api_anonymous_client():
    """Анонимный клинет."""
    return APIClient()
