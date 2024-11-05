import pytest

from subscription.models import SubscriptionType


@pytest.fixture
def trying_sub() -> SubscriptionType:
    return SubscriptionType.objects.create(
        name="Пробная",
        price=1,
        features=(
            "Задания от практикующих специалистов, Нативные задания, "
            "Карьерные знания дешевле стакана кофе, Общество единомышленников"
        ),
    )


@pytest.fixture
def optimum_sub():
    return SubscriptionType.objects.create(
        name="Оптимум",
        price=120,
        features=(
            "Задания от практикующих специалистов, Нативные задания, "
            "Карьерные знания дешевле стакана кофе, Общество единомышленников"
        ),
    )
