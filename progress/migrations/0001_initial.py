# Generated by Django 5.0.3 on 2024-04-25 11:40

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("courses", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="UserTest",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("first_name", models.CharField(max_length=30, verbose_name="Имя пользователя")),
                ("last_name", models.CharField(max_length=30, verbose_name="Фамилия пользователя")),
                ("age", models.IntegerField(verbose_name="Возраст пользователя")),
                ("specialization", models.CharField(max_length=40, verbose_name="Специальность пользователя")),
                ("geo_position", models.CharField(max_length=50)),
            ],
            options={
                "verbose_name": "Пользователь (тестовая модель)",
                "verbose_name_plural": "Пользователи (тестовая модель)",
            },
        ),
        migrations.CreateModel(
            name="UserProfile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("is_autopay_allowed", models.BooleanField(default=True)),
                (
                    "last_subscription_date",
                    models.DateField(
                        default=django.utils.timezone.now, verbose_name="Последний раз когда юзер оформилял подписку"
                    ),
                ),
                (
                    "chosen_skills",
                    models.ManyToManyField(
                        related_name="profile_skills", to="courses.skill", verbose_name="Выбранные навыки"
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="profiles",
                        to="progress.usertest",
                        verbose_name="Пользователь",
                    ),
                ),
            ],
            options={
                "verbose_name": "Профиль пользователя",
                "verbose_name_plural": "Профили пользователей",
            },
        ),
        migrations.CreateModel(
            name="TaskObjUserResult",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("points_gained", models.PositiveIntegerField(verbose_name="Набранные баллы")),
                (
                    "datetime_created",
                    models.DateTimeField(default=django.utils.timezone.now, verbose_name="Дата создания"),
                ),
                (
                    "task_object",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="user_results",
                        to="courses.taskobject",
                        verbose_name="Объект задачи",
                    ),
                ),
                (
                    "user_profile",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="task_obj_results",
                        to="progress.userprofile",
                        verbose_name="Профиль пользователя",
                    ),
                ),
            ],
            options={
                "verbose_name": "Ответ пользователя на единицу задания",
                "verbose_name_plural": "Ответы пользователя на единицу задания",
                "unique_together": {("task_object", "user_profile")},
            },
        ),
    ]
