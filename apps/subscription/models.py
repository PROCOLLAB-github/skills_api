from django.core.validators import MinValueValidator
from django.db import models


class SubscriptionType(models.Model):
    SUBSCRIPTION_CHOICES = [
        ("Start", "Start"),
        ("PRO", "PRO"),
        ("PRO+", "PRO+"),
    ]
    name = models.CharField(
        null=False, blank=False, verbose_name="Название подписки", max_length=30
    )
    subscription_level = models.CharField(
        choices=SUBSCRIPTION_CHOICES,
        unique=True,
        null=True,
        blank=False,
        verbose_name="Уровень подписки",
        max_length=30,
    )
    price = models.IntegerField(
        null=False,
        blank=False,
        verbose_name="Стоимость подписки",
        validators=[MinValueValidator(1)],
    )
    features = models.TextField(
        null=True,
        verbose_name="Что пользователь получит за подписку",
        help_text="Каждый пункт писать через запятую",
    )

    class Meta:
        verbose_name = "Тип подписки"
        verbose_name_plural = "Типы подписки"

    def __str__(self):
        return self.name
