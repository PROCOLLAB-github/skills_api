from django.db import transaction

from procollab_skills.celery import app
from progress.models import UserProfile
from datetime import timedelta
from django.utils import timezone
from yookassa import Payment

from subscription.mapping import AmountData, CreateRecurrentPaymentData
from subscription.utils.create_payment import create_payment


@app.task
def daily_resub_users() -> str:
    # сначала удаляет все скиллы у тех юзеров, которые покупали подписку >= 1 месяц назад
    one_month_ago = timezone.now() - timedelta(days=30)
    user_profiles = UserProfile.objects.filter(last_subscription_date__lte=one_month_ago)

    autopay_on_profiles = user_profiles.filter(is_autopay_allowed=True)
    autopay_on_profiles_ids = list(autopay_on_profiles.values_list("id", flat=True))

    user_profile_chosen_skils = UserProfile.chosen_skills.through
    user_profile_chosen_skils.objects.filter(userprofile__in=user_profiles).delete()

    # для них же ищет данные о платежах
    payments = Payment.list({"created_at.lte": one_month_ago.isoformat()})

    # для платежей. если у юзера в настройках разрешена отмена периодических платежей, то повторяет их
    with transaction.atomic():
        for payment in payments.items:
            if not payment.metadata["user_profile_id"] in autopay_on_profiles_ids:
                continue

            payload = CreateRecurrentPaymentData(
                amount=AmountData(value=payment.amount.value),
                payment_method_id=payment.id,
                metadata={"user_profile_id": payment.metadata["user_profile_id"]},
            )

            # TODO настроить веб-хук, чтобы
            #  при уведомлениях об успешных платежах, у нужных юзеров бы обновлялась подписка
            new_payment = create_payment(payload)
            if new_payment.status == "succeeded":
                autopay_on_profiles.get(id=new_payment.metadata["user_profile_id"])

    return (
        f"Users' skills nullified {user_profiles.count()}\n Quantity of resubbed users {len(autopay_on_profiles_ids)}"
    )
