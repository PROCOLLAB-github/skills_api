from datetime import datetime, timedelta

from rest_framework import serializers
from rest_framework_dataclasses.serializers import DataclassSerializer

from progress.models import UserProfile
from subscription.typing import CreatePaymentResponseData, WebHookRequest, SubIdSerializer
from subscription.models import SubscriptionType


class CreatePaymentResponseSerializer(DataclassSerializer):
    class Meta:
        dataclass = CreatePaymentResponseData


class SubscriptionSerializer(serializers.ModelSerializer):
    features_list = serializers.SerializerMethodField()

    def get_features_list(self, obj) -> list[str]:
        return obj.features.split(",")

    class Meta:
        model = SubscriptionType
        fields = ["id", "name", "price", "features_list"]


class RenewSubDateSerializer(DataclassSerializer):
    class Meta:
        dataclass = WebHookRequest


class BuySubSerializer(DataclassSerializer):
    class Meta:
        dataclass = SubIdSerializer


class UserSubscriptionDataSerializer(serializers.ModelSerializer):
    is_subscribed: bool = serializers.SerializerMethodField()
    subscription_date_over = serializers.SerializerMethodField()
    last_subscription_type = SubscriptionSerializer()

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
        user_sub_date = obj.last_subscription_date
        thirty_days_ago = datetime.now().date() - timedelta(days=30)

        if not obj.last_subscription_date:
            return False

        if user_sub_date <= thirty_days_ago:
            return False

        return True

    def get_subscription_date_over(self, obj: UserProfile):
        return obj.last_subscription_date + timedelta(days=30)
