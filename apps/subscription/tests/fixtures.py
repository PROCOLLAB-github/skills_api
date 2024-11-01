import pytest

from model_bakery import baker

from progress.models import CustomUser
from subscription.models import SubscriptionType



@pytest.fixture
@pytest.mark.django_db
def trying_sub() -> None:
    return SubscriptionType.objects.create(
        name="Пробная",
        price=1,
        features="Задания от практикующих специалистов, Нативные задания, Карьерные знания дешевле стакана кофе, Общество единомышленников",
    )


@pytest.fixture
@pytest.mark.django_db
def optimum_sub():
    return SubscriptionType.objects.create(
    name="Оптимум",
    price=120,
    features="Задания от практикующих специалистов, Нативные задания, Карьерные знания дешевле стакана кофе, Общество единомышленников",
)


@pytest.fixture
@pytest.mark.django_db
def user() -> None:
    return baker.make('progress.CustomUser')


@pytest.fixture
@pytest.mark.django_db
def user_with_trial_sub() -> CustomUser:
    user = baker.make('progress.CustomUser')

    profile = user.profiles
    profile.bought_trial_subscription = True
    profile.save()

    return user





