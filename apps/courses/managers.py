from django.db import models
from django.db.models import Q
from django.db.models.query import QuerySet


class PublishedManager(models.Manager):
    """Только опубликованные сущности: `status=published`."""

    def get_queryset(self) -> QuerySet:
        return super().get_queryset().filter(status="published")


class AvailableForUser(PublishedManager):
    """
    Только опубликованные сущности: `status=published`.
    Доступные пользователю `Task` исходя из недель через метод `only_awailable_weeks`.
    """

    def only_awailable_weeks(self, available_week: int) -> QuerySet:
        """Фильтрация по доступным для пользователя неделям."""
        return super().get_queryset().filter(Q(week__lte=available_week))
