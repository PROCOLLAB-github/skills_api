from django.db import models


class SubscriptionType(models.Model):
    name = models.CharField(null=False, blank=False, verbose_name="Название подписки", max_length=30)
    price = models.IntegerField(null=False, blank=False, verbose_name="Стоимость подписки")
    features = models.TextField(
        null=True, verbose_name="Что юзер получает за подписку", help_text="Каждый пункт писать через запятую"
    )

    class Meta:
        verbose_name = "Тип подписки"
        verbose_name_plural = "Типы подписки"
