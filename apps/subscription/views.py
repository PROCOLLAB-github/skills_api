from dataclasses import asdict
from datetime import datetime, timedelta

from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_spectacular.utils import extend_schema

from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

# from procollab_skills.decorators import exclude_auth_perm  # , exclude_sub_check_perm
from yookassa import Payment, Refund

from progress.models import UserProfile
from subscription.typing import (
    CreatePaymentData,
    AmountData,
    ConfirmationRequestData,
    CreatePaymentViewRequestData,
    CreatePaymentResponseData,
    WebHookRequest,
)
from subscription.models import SubscriptionType
from subscription.serializers import (
    CreatePaymentResponseSerializer,
    SubscriptionSerializer,
    RenewSubDateSerializer,
    BuySubSerializer,
)
from subscription.utils.create_payment import create_payment
import logging


@extend_schema(
    summary="Создаёт объект оплаты в ЮКассе",
    description="""Выводит только тот уровень, который юзер может пройти. Остальные для прохождения закрыты""",
    tags=["Подписка"],
    request=BuySubSerializer,
    parameters=[],
    responses={201: CreatePaymentResponseSerializer},
)
class CreatePayment(CreateAPIView):
    permission_classes = [AllowAny]

    @staticmethod
    def check_subscription(user_sub_date):
        try:
            thirty_days_ago = datetime.now().date() - timedelta(days=30)
            if user_sub_date and user_sub_date >= thirty_days_ago:
                raise PermissionDenied("Подписка уже оформлена.")

        except PermissionDenied as e:
            return Response({"error": str(e)}, status=403)

    def get_request_data(self, user_profile_id: int) -> CreatePaymentViewRequestData:
        self.subscription_id = self.request.data.get("subscription_id")
        return CreatePaymentViewRequestData(
            subscription_id=self.subscription_id,
            confirmation=ConfirmationRequestData(
                type="redirect", return_url=self.request.data.get("redirect_url")
            ),  # на будущее, при добавлении новых способов оплаты
            user_profile_id=user_profile_id,
        )

    def create(self, request, *args, **kwargs) -> Response:
        try:
            self.check_subscription(self.user_profile.last_subscription_date)

            request_data = self.get_request_data(self.profile_id)
            subscription = get_object_or_404(SubscriptionType, id=self.subscription_id)

            payload = CreatePaymentData(
                amount=AmountData(value=subscription.price),
                confirmation=request_data.confirmation,
                metadata={"user_profile_id": self.profile_id, "subscription_id": subscription.id},
            )
            payment: CreatePaymentResponseData = create_payment(payload)
            return Response(asdict(payment), status=200)
        except Exception as e:
            return Response({"error": str(e)}, status=400)


@extend_schema(
    summary="Вывод доступных подписок",
    tags=["Подписка"],
)
class ViewSubscriptions(ListAPIView):
    queryset = SubscriptionType.objects.all()
    permission_classes = [AllowAny]
    serializer_class = SubscriptionSerializer
    authentication_classes = []

    def list(self, request, *args, **kwargs) -> Response:
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data, status=200)


@extend_schema(summary="НЕ ДЛЯ ФРОНТА. Обновление дат подписки для юзеров.", tags=["Подписка"])
class NotificationWebHook(CreateAPIView):
    serializer_class = RenewSubDateSerializer
    permission_classes = [AllowAny]
    authentication_classes = []

    def get_request_data(self) -> WebHookRequest:
        return WebHookRequest(event=self.request.data["event"], object=self.request.data["object"])

    def create(self, request, *args, **kwargs) -> Response:
        # try:
        notification_data = self.get_request_data()

        profile_to_update = UserProfile.objects.select_related("user", "last_subscription_type").filter(
            id=notification_data.object["metadata"]["user_profile_id"]
        )

        if notification_data.event == "payment.succeeded" and notification_data.object["status"] == "succeeded":

            params_to_update = {"last_subscription_date": timezone.now()}
            if sub_id := notification_data.object["metadata"].get(
                "subscription_id"
            ):  # если совершается впервые (не продливается)
                params_to_update["last_subscription_type_id"] = sub_id

            profile_to_update.update(**params_to_update)

            logging.info(
                f"subscription date renewed for {profile_to_update[0].user.first_name} "
                f"{profile_to_update[0].user.last_name}"
            )
            return Response(
                f"subscription date renewed for {profile_to_update[0].user.first_name} "
                f"{profile_to_update[0].user.last_name}"
            )
        elif notification_data.event == "refund.succeeded" and notification_data.object["status"] == "succeeded":
            (
                profile_to_update.update(
                    last_subscription_date=None, is_autopay_allowed=False, last_subscription_type=None
                )
            )

            logging.info(
                f"subscription canceled for {profile_to_update[0].user.first_name} "
                f"{profile_to_update[0].user.last_name}"
            )
            return Response(
                f"subscription canceled for {profile_to_update[0].user.first_name} "
                f"{profile_to_update[0].user.last_name}"
            )

        return Response({"error": "event is not yet succeeded"}, status=400)

    # except Exception as e:
    #     return Response({"error": str(e)}, status=400)


@extend_schema(summary="Запрос возврата", tags=["Подписка"])
class CreateRefund(CreateAPIView):
    def create(self, request, *args, **kwargs):
        one_month_ago = timezone.now() - timedelta(days=30)
        payments = Payment.list(
            {
                "created_at.lte": one_month_ago.isoformat(),
                "metadata": {"user_profile_id": self.profile_id},
                "status": "succeeded",
            }
        )
        last_payment = payments.items[0]
        if self.user_profile.last_subscription_date >= timezone.now().date() - timedelta(days=15):

            Refund.create(
                {
                    "payment_id": last_payment.id,
                    "amount": {"value": last_payment.amount.value, "currency": "RUB"},
                }
            )

        else:
            return Response({"error": "Вы не можете отменить подписку после 15 дней пользования, извините"}, status=400)
        return Response(status=202)
