from procollab_skills.celery import app
from progress.models import UserProfile
from datetime import timedelta
from django.utils import timezone
from yookassa import Payment

from subscription.models import SubscriptionType
from subscription.typing import AmountData, CreateRecurrentPaymentData
from subscription.utils.create_payment import create_payment


@app.task
def daily_resub_users() -> str:
    one_month_ago = timezone.now() - timedelta(days=30)
    user_profiles = UserProfile.objects.filter(
        last_subscription_date__lte=one_month_ago
    )

    autopay_on_profiles = user_profiles.filter(is_autopay_allowed=True)
    autopay_on_profiles_ids = list(autopay_on_profiles.values_list("id", flat=True))

    # для них же ищет данные о платежах
    payments = Payment.list({"created_at.lte": one_month_ago.isoformat()})

    subscriptions = SubscriptionType.objects.values("id", "price")
    subscriptions_prices: dict[int, str] = dict(
        (item["id"], item["name"]) for item in subscriptions
    )

    for payment in payments.items:
        if (
                payment.metadata.get("user_profile_id", None) is None
        ):  # если данных нет почему-то
            continue

        subscription_id = int(payment.metadata["subscription_id"])
        if (
                subscriptions_prices[subscription_id] == 1
        ):  # подписка была пробная - не продляем
            continue

        user_id = int(payment.metadata["user_profile_id"])
        if user_id not in autopay_on_profiles_ids:  # включено ли у юзера авто-продление
            continue

        payload = CreateRecurrentPaymentData(
            amount=AmountData(value=payment.amount.value),
            payment_method_id=payment.id,
            metadata={
                "user_profile_id": user_id,
                "subscription_id": subscription_id,
            },
        )

        create_payment(payload)

    return f"Users' skills nullified {user_profiles.count()}\n Quantity of resubbed users {len(autopay_on_profiles_ids)}"
