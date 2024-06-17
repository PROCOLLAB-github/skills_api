from datetime import datetime, timedelta

from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied


class IfSubscriptionOutdatedPermission(permissions.BasePermission):
    """
    Проверка пользователя на то, не просрочена ли у него подписка
    """

    def has_permission(self, request, view) -> bool:
        user_sub_date = view.user_profile.last_subscription_date
        if not user_sub_date:
            raise PermissionDenied("Подписка просрочена.")

        thirty_days_ago = datetime.now().date() - timedelta(days=30)
        if user_sub_date <= thirty_days_ago:
            raise PermissionDenied("Подписка просрочена.")
        return True
