from datetime import datetime
from unittest.mock import patch

import pytest
from model_bakery import baker

from progress.models import UserProfile
from progress.serializers import CustomObtainPairSerializer


@pytest.fixture
def user_with_trial_sub_token():
    with patch("progress.tasks.create_user_monts_target.delay"):
        user = baker.make("progress.CustomUser")
        profile: UserProfile = user.profiles

        profile.bought_trial_subscription = True
        profile.last_subscription_date = datetime.now().date()
        profile.save()

        return str(CustomObtainPairSerializer.get_token(user))





@pytest.fixture
def user_token():
    with patch("progress.tasks.create_user_monts_target.delay"):
        user = baker.make("progress.CustomUser")

        return str(CustomObtainPairSerializer.get_token(user))