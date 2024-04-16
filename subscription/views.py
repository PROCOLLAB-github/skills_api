from dataclasses import asdict

from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.response import Response

from subscription.mapping import (
    CreatePaymentData,
    AmountData,
    ConfirmationRequestData,
    CreatePaymentViewRequestData,
    CreatePaymentResponseData,
)
from subscription.models import SubscriptionType
from subscription.serializers import CreatePaymentResponseSerializer, SubscriptionSerializer
from subscription.utils.create_payment import create_payment


@extend_schema(
    summary="Создаёт объект оплаты в ЮКассе",
    description="""Выводит только тот уровень, который юзер может пройти. Остальные для прохождения закрыты""",
    tags=["Подписка"],
    parameters=[OpenApiParameter(name="subscription_id", description="ID типа подписки", type=int)],
    responses={201: CreatePaymentResponseSerializer},
)
class CreatePayment(CreateAPIView):
    def get_request_data(self) -> CreatePaymentViewRequestData:
        return CreatePaymentViewRequestData(
            subscription_id=int(self.request.query_params.get("subscription_id")),
            confirmation=ConfirmationRequestData(type="redirect"),  # на будущее, при добавлении новых способов оплаты
            user_profile_id=1,  # TODO заменить при добавлении авторизации
        )

    def create(self, request, *args, **kwargs) -> Response:
        request_data = self.get_request_data()
        subscription = get_object_or_404(SubscriptionType, id=1)

        payload = CreatePaymentData(
            amount=AmountData(value=subscription.price),
            confirmation=request_data.confirmation,
            metadata={"user_profile_id": request_data.user_profile_id},
        )

        payment: CreatePaymentResponseData = create_payment(payload)
        return Response(asdict(payment), status=200)


@extend_schema(
    summary="Вывод доступных подписок",
    tags=["Подписка"],
)
class ViewSubscriptions(ListAPIView):
    queryset = SubscriptionType.objects.all()
    serializer_class = SubscriptionSerializer

    def list(self, request, *args, **kwargs) -> Response:
        queryset = self.get_queryset()

        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data, status=200)


# TODO получение информации о платеже

# TODO запрос на создание возврата

# TODO зап
