from django.db import models
from django.db.models import Q
from django.db.models.query import QuerySet

from progress.models import CustomUser


class PublishedManager(models.Manager):
    """Только опубликованные сущности: `status=published`."""

    def get_queryset(self) -> QuerySet:
        return super().get_queryset().filter(status="published")

    def for_user(self, user: CustomUser = None) -> QuerySet:
        """
        Возвращает:
            - Все объекты для `superuser`,
            - Объекты со статусом `published` и `stuff_only` для `staff`,
            - Только опубликованные объекты для остальных.
        """
        base_queryset = super().get_queryset()
        if user and user.is_superuser:
            return base_queryset
        if user and user.is_staff:
            return base_queryset.filter(Q(status="published") | Q(status="stuff_only"))
        return self.get_queryset()


class AvailableForUser(PublishedManager):
    """
    Доступные пользователю `Task` исходя из недель через метод `only_awailable_weeks`.
    """

    def only_awailable_weeks(self, available_week: int, user: CustomUser = None) -> QuerySet:
        """Фильтрация по доступным для пользователя неделям."""
        if user and (user.is_superuser or user.is_staff):
            return super().for_user(user)
        if available_week == 0:
            return super().for_user(user).filter(free_access=True)
        return super().for_user(user).filter(Q(week__lte=available_week))
