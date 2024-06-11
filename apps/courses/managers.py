from django.db import models
from django.db.models.query import QuerySet


class SkillPublishedManager(models.Manager):
    """Модельный менеджер навыков - только опубликованные навыки."""

    def get_queryset(self) -> QuerySet:
        return super().get_queryset().filter(status='published')
