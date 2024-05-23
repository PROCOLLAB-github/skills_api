from datetime import datetime, timedelta


from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied


from progress.models import UserProfile


class IfSubscriptionOutdatedAndAuthenticated(permissions.BasePermission):
    """
    Два пермишена были объеденины в один, чтобы сэкономить на запросе получения пользователя
    """

    @staticmethod
    def _is_authenticated(user) -> bool:
        if not bool(user and user.is_authenticated):
            raise PermissionDenied("Учетные данные не были предоставлены.")
        return True

    @staticmethod
    def _is_subscription_valid(view, user) -> bool:
        skip_middleware = getattr(view, "_skip_check_sub", False)
        if skip_middleware:
            return True

        user_sub_date = UserProfile.objects.only("last_subscription_date").get(user=user).last_subscription_date
        thirty_days_ago = datetime.now().date() - timedelta(days=30)
        if user_sub_date <= thirty_days_ago:
            raise PermissionDenied("Подписка просрочена.")
        return True

    def has_permission(self, request, view):
        user = request.user

        skip_auth_middleware = getattr(view, "_skip_auth", False)
        if skip_auth_middleware:
            return True
        return self._is_authenticated(user) and self._is_subscription_valid(view, user)
