from datetime import timedelta

from django.utils import timezone

from progress.models import CustomUser


def user_sub_is_active(user: CustomUser) -> bool:
    """Проверяет есть и активна ли подписка у пользователя."""
    user_sub_date = user.profiles.last_subscription_date
    if not user_sub_date:
        return False

    one_month_ago = (timezone.now() - timedelta(days=30)).date()
    if user_sub_date <= one_month_ago:
        return False
    return True
