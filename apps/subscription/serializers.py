from rest_framework import serializers
from rest_framework_dataclasses.serializers import DataclassSerializer

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
