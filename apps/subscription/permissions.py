from django.utils import timezone
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import BasePermission

from progress.services import get_user_available_week
from subscription.services import user_sub_is_active
from subscription.utils.has_active_subscription import \
    user_has_active_subscription
from trajectories.models import Month, UserIndividualSkill


class SubscriptionSectionPermission(BasePermission):
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


class SubscriptionTaskObjectPermission(BasePermission):
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


class SubscriptionObjectPermission(BasePermission):
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


class HasActiveSubscription(BasePermission):
    """
    Разрешает доступ только пользователям с активной подпиской.
    """

    message = "У вас нет активной подписки."

    def has_permission(self, request, view):
        return user_has_active_subscription(request.user)


class SkillAccessPermission(BasePermission):
    """
    Разрешает доступ к навыкам пользователям, которые:
    1. Имеют активную подписку,
    2. Или находятся в активной траектории,
    3. Или навык имеет бесплатный доступ.
    """

    def has_permission(self, request, view):
        skill = view.get_object()
        return self.is_skill_accessible_for_user(request, skill)

    def is_skill_accessible_for_user(self, request, skill):
        user = request.user

        if skill.free_access:
            return True

        if request.user.is_superuser or request.user.is_staff:
            return True

        if skill.requires_subscription and user_has_active_subscription(user):
            return True

        if skill.is_from_trajectory and self.is_skill_accessible_via_trajectory(
            user, skill
        ):
            return True

        return False

    def user_has_active_subscription(self, user):
        return user_has_active_subscription(user)

    def is_skill_accessible_via_trajectory(self, user, skill):
        """
        Проверяет, доступен ли навык через активную траекторию или индивидуальные навыки пользователя,
        и является ли навык доступным по времени в рамках траектории.
        """
        user_trajectory = user.user_trajectories.filter(is_active=True).first()
        if not user_trajectory:
            return False

        month_with_skill = Month.objects.filter(
            trajectory=user_trajectory.trajectory, skills=skill
        ).first()

        if month_with_skill:
            current_date = timezone.now().date()
            if month_with_skill.is_accessible_for_user(user, current_date):
                return True
            return False

        if UserIndividualSkill.objects.filter(
            user=user, skills=skill, user_trajectory=user_trajectory
        ).exists():
            return True

        return False
