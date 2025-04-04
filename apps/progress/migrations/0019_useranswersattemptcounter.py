# Generated by Django 5.0.3 on 2024-11-25 16:07

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("courses", "0015_skill_subcription_type"),
        ("progress", "0018_remove_userweekstat_created_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="UserAnswersAttemptCounter",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "attempts_made_before",
                    models.SmallIntegerField(
                        default=1,
                        help_text="Количество попыток ответа до подсказки",
                        validators=[django.core.validators.MinValueValidator(0)],
                    ),
                ),
                ("is_take_hint", models.BooleanField(default=False, help_text="Получил ли подсказку")),
                (
                    "attempts_made_after",
                    models.SmallIntegerField(
                        default=0,
                        help_text="Количество попыток ответа после подсказки",
                        validators=[django.core.validators.MinValueValidator(0)],
                    ),
                ),
                (
                    "task_object",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="users_attempts",
                        to="courses.taskobject",
                        verbose_name="Объект задачи",
                    ),
                ),
                (
                    "user_profile",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="attemps_counter",
                        to="progress.userprofile",
                        verbose_name="Пользователь",
                    ),
                ),
            ],
            options={
                "verbose_name": "Попытки ответа пользователя",
                "verbose_name_plural": "Попытки ответа пользователя",
                "unique_together": {("user_profile", "task_object")},
            },
        ),
    ]
