from datetime import date

from dateutil.relativedelta import relativedelta
from rest_framework.permissions import BasePermission


class HasActiveSubscription(BasePermission):
    """
    Разрешает доступ только пользователям с активной подпиской.
    """

    message = "У вас нет активной подписки, оформите её, чтобы активировать траекторию."

    def has_permission(self, request, view):
        user = request.user

        if not hasattr(user, "profiles"):
            return False

        user_profile = user.profiles

        if not user_profile.last_subscription_type or not user_profile.last_subscription_date:
            return False

        subscription_valid_until = user_profile.last_subscription_date + relativedelta(months=1)
        return date.today() < subscription_valid_until
