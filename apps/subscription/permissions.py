from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied

from progress.services import get_user_available_week
from subscription.services import user_sub_is_active


class SubscriptionSectionPermission(permissions.BasePermission):
    """
    Проверка пользователя на то, есть ли у него подписка, подразумевается доступ к разделу.
    Персоналу (`is_staff`, `is_superuser` доступ без подписки).
    """

    def has_permission(self, request, view) -> bool:
        if not request.user:
            return False
        if request.user.is_superuser or request.user.is_staff:
            return True
        if not user_sub_is_active(request.user):
            raise PermissionDenied("Для доступа необходимо приобрести подписку.")
        return True


class SubscriptionTaskObjectPermission(permissions.BasePermission):
    """
    Без подписки доступ только к бесплатным сущностям (
        Контекст предполгает именно view c аттрибутом `view.task`
    ).
    Персоналу (`is_staff`, `is_superuser` полный доступ без подписки).
    Платное задание доступно только если неделя от начала подписки >= неделе задания.
    """

    def has_permission(self, request, view) -> bool:
        if not request.user:
            return False

        if request.user.is_superuser or request.user.is_staff or view.task.free_access:
            return True

        if not user_sub_is_active(request.user):
            raise PermissionDenied("Для доступа необходимо приобрести подписку.")

        awailable_week, _ = get_user_available_week(request.user.profiles.id)
        if user_sub_is_active(request.user) and awailable_week < view.task.week:
            raise PermissionDenied(f"Доступ к {view.task.week} неделе откроется позже.")

        return True


class SubscriptionObjectPermission(permissions.BasePermission):
    """
    Без подписки доступ только к бесплатным сущностям.
    Персоналу (`is_staff`, `is_superuser` доступ без подписки).
    Данная проверка подразумевает явный/неявный вызов у view класса метода `check_object_permissions`
    """

    def has_object_permission(self, request, view, obj) -> bool:
        if not request.user:
            return False
        if request.user.is_superuser or request.user.is_staff:
            return True
        if obj.free_access is False and not user_sub_is_active(request.user):
            raise PermissionDenied("Для доступа необходимо приобрести подписку.")
        return True
