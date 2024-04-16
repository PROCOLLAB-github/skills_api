# Generated by Django 5.0.3 on 2024-04-13 12:36

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="SubscriptionType",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=30, verbose_name="Название подписки")),
                ("price", models.IntegerField(verbose_name="Стоимость подписки")),
                (
                    "features",
                    models.TextField(
                        help_text="Каждый пункт писать через запятую",
                        null=True,
                        verbose_name="Что юзер получает за подписку",
                    ),
                ),
            ],
            options={
                "verbose_name": "Тип подписки",
                "verbose_name_plural": "Типы подписки",
            },
        ),
    ]
