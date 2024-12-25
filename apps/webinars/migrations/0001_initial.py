# Generated by Django 5.0.3 on 2024-12-24 09:47

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("files", "0002_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Speaker",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("full_name", models.CharField(max_length=255, verbose_name="Имя и фамилия спикера")),
                ("position", models.CharField(max_length=255, verbose_name="Должность")),
                (
                    "photo",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="webinars",
                        to="files.filemodel",
                    ),
                ),
            ],
            options={
                "verbose_name": "Спикер",
                "verbose_name_plural": "Спикеры",
            },
        ),
        migrations.CreateModel(
            name="Webinar",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=255, verbose_name="Заголовок")),
                ("description", models.TextField(verbose_name="Описание")),
                ("datetime_start", models.DateTimeField(verbose_name="Дата и время начала")),
                ("datetime_end", models.DateTimeField(verbose_name="Дата и время конца")),
                ("online_link", models.URLField(blank=True, null=True, verbose_name="Ссылка для подключения")),
                ("recording_link", models.URLField(blank=True, null=True, verbose_name="Ссылка на запись")),
                (
                    "speaker",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="webinars",
                        to="webinars.speaker",
                        verbose_name="Спикер",
                    ),
                ),
            ],
            options={
                "verbose_name": "Вебинар",
                "verbose_name_plural": "Вебинары",
                "ordering": ["datetime_start"],
            },
        ),
        migrations.CreateModel(
            name="WebinarRegistration",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("datetime_created", models.DateTimeField(auto_now_add=True, verbose_name="Дата регистрации")),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="webinar_registrations",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Пользователь",
                    ),
                ),
                (
                    "webinar",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="webinar_registrations",
                        to="webinars.webinar",
                        verbose_name="Вебинар",
                    ),
                ),
            ],
            options={
                "verbose_name": "Регистрация на вебинар",
                "verbose_name_plural": "Регистрации на вебинар",
            },
        ),
        migrations.AddConstraint(
            model_name="webinarregistration",
            constraint=models.UniqueConstraint(fields=("user", "webinar"), name="unique_user_registration"),
        ),
    ]