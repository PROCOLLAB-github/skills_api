from datetime import datetime, timedelta
from typing import Union

from rest_framework import serializers
from rest_framework_dataclasses.serializers import DataclassSerializer

from progress.models import UserProfile
from subscription.models import SubscriptionType
from subscription.services import user_sub_is_active
from subscription.typing import (CreatePaymentResponseData, SubIdSerializer,
                                 WebHookRequest)


class CreatePaymentResponseSerializer(DataclassSerializer):
    class Meta:
        dataclass = CreatePaymentResponseData


class SubscriptionSerializer(serializers.ModelSerializer):
    features_list = serializers.SerializerMethodField()
    active = serializers.SerializerMethodField()
    available = serializers.SerializerMethodField()

    class Meta:
        model = SubscriptionType
        fields = ["id", "name", "price", "features_list", "active", "available"]

    def get_features_list(self, obj) -> list[str]:
        return obj.features.split(", ")

    def get_active(self, obj: SubscriptionType) -> bool | None:
        """Активна ли запрашиваемая подписка."""
        request = self.context["request"]
        if request.user and not request.user.is_authenticated:
            return None
        user_profile: UserProfile = request.user.profiles
        if user_sub_is_active(request.user) and user_profile.last_subscription_type == obj:
            return True
        return False

    # TODO FIX как появятся несколько видов подписок (не включая пробную)
    # необходимо добавить возможность перехода.
    def get_available(self, obj: SubscriptionType) -> bool | None:
        """
        Доступна ли подписка к покупке:
        - `Пробная` - можно приобрести только 1 раз.
        - Прочие - доступны к покупке, если не активна какая-либо сейчас.
        """
        request = self.context["request"]
        user_profile: UserProfile = request.user.profiles
        if request.user and not request.user.is_authenticated:
            return None
        if obj.name == "Пробная" and obj.price == 1:
            return not user_profile.bought_trial_subscription
        return not user_sub_is_active(request.user)


class RenewSubDateSerializer(DataclassSerializer):
    class Meta:
        dataclass = WebHookRequest


class BuySubSerializer(DataclassSerializer):
    class Meta:
        dataclass = SubIdSerializer


class UserSubscriptionDataSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    subscription_date_over = serializers.SerializerMethodField(allow_null=True)
    last_subscription_type = SubscriptionSerializer(allow_null=True)

    class Meta:
        model = UserProfile
        fields = [
            "is_subscribed",
            "last_subscription_type",
            "last_subscription_date",
            "subscription_date_over",
            "is_autopay_allowed",
        ]

    def get_is_subscribed(self, obj: UserProfile) -> bool:
        if obj.user.is_superuser or obj.user.is_staff:
            return True
        return user_sub_is_active(obj.user)

    def get_subscription_date_over(self, obj: UserProfile) -> Union[datetime.date, None]:
        if not obj.last_subscription_date:
            return None
        return obj.last_subscription_date + timedelta(days=30)
