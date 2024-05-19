from dataclasses import asdict
from datetime import datetime, timedelta

from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_spectacular.utils import extend_schema, OpenApiParameter

from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.response import Response

from procollab_skills.decorators import exclude_auth_perm  # , exclude_sub_check_perm
from progress.models import UserProfile
from subscription.mapping import (
    CreatePaymentData,
    AmountData,
    ConfirmationRequestData,
    CreatePaymentViewRequestData,
    CreatePaymentResponseData,
    WebHookRequest,
)
from subscription.models import SubscriptionType
from subscription.serializers import CreatePaymentResponseSerializer, SubscriptionSerializer, RenewSubDateSerializer
from subscription.utils.create_payment import create_payment


@extend_schema(
    summary="Создаёт объект оплаты в ЮКассе",
    description="""Выводит только тот уровень, который юзер может пройти. Остальные для прохождения закрыты""",
    tags=["Подписка"],
    parameters=[OpenApiParameter(name="subscription_id", description="ID типа подписки", type=int)],
    responses={201: CreatePaymentResponseSerializer},
)
# @exclude_sub_check_perm
class CreatePayment(CreateAPIView):
    @staticmethod
    def check_subscription(user_sub_date):
        thirty_days_ago = datetime.now().date() - timedelta(days=30)
        if user_sub_date >= thirty_days_ago:
            raise PermissionDenied("Подписка уже оформлена.")

    def get_request_data(self, user_profile_id: int) -> CreatePaymentViewRequestData:
        return CreatePaymentViewRequestData(
            subscription_id=int(self.request.query_params.get("subscription_id")),
            confirmation=ConfirmationRequestData(type="redirect"),  # на будущее, при добавлении новых способов оплаты
            user_profile_id=user_profile_id,
        )

    def create(self, request, *args, **kwargs) -> Response:
        # user_profile = UserProfile.objects.select_related("user").get(user_id=self.request.user.id)
        user_profile = UserProfile.objects.select_related("user").get(user_id=1)

        try:
            self.check_subscription(user_profile.last_subscription_date)
        except PermissionDenied as e:
            return Response({"error": str(e)}, status=403)

        request_data = self.get_request_data(user_profile.id)
        subscription = get_object_or_404(SubscriptionType, id=self.request.query_params.get("subscription_id"))

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
@exclude_auth_perm
class ViewSubscriptions(ListAPIView):
    queryset = SubscriptionType.objects.all()
    serializer_class = SubscriptionSerializer

    def list(self, request, *args, **kwargs) -> Response:
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data, status=200)


@extend_schema(summary="Обновление дат подписки для юзеров", tags=["Подписка"])
class ServeWebHook(CreateAPIView):
    serializer_class = RenewSubDateSerializer

    def get_request_data(self) -> WebHookRequest:
        return WebHookRequest(event=self.request.data["event"], object=self.request.data["object"])

    def create(self, request, *args, **kwargs) -> Response:
        notification_data = self.get_request_data()

        if notification_data.event == "payment.succeeded" and notification_data.object["status"] == "succeeded":
            profile_to_update = UserProfile.objects.select_related("user").get(
                id=notification_data.object["metadata"]["user_profile_id"]
            )

            profile_to_update.last_subscription_date = timezone.now()
            profile_to_update.save()

            return Response(
                f"subscription date renewed for {profile_to_update.user.first_name} {profile_to_update.user.last_name}"
            )

        return Response({"error": "event is not yet succeeded"}, status=400)


# TODO получение информации о платеже

# TODO запрос на создание возврата
