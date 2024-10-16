# Generated by Django 5.0.3 on 2024-07-30 09:40

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("courses", "0011_task_week_alter_taskobject_validate_answer"),
        ("progress", "0013_remove_customuser_geo_position_alter_customuser_age"),
    ]

    operations = [
        migrations.CreateModel(
            name="UserSkillDone",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "additional_points",
                    models.PositiveSmallIntegerField(
                        default=0,
                        help_text="Начисляются за прохождение месяца вовремя.",
                        verbose_name="Дополнительные баллы",
                    ),
                ),
                (
                    "skill",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="done_skills",
                        to="courses.skill",
                        verbose_name="Навык",
                    ),
                ),
                (
                    "user_profile",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="done_skills",
                        to="progress.userprofile",
                        verbose_name="Пользователь",
                    ),
                ),
            ],
            options={
                "verbose_name": "Завершенный навык",
                "verbose_name_plural": "Завершенные навыки",
            },
        ),
        migrations.CreateModel(
            name="UserWeekStat",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "additional_points",
                    models.PositiveSmallIntegerField(
                        default=0,
                        help_text="Начисляются за прохождение недели вовремя.",
                        verbose_name="Дополнительные баллы",
                    ),
                ),
                (
                    "week",
                    models.PositiveSmallIntegerField(
                        choices=[(1, "1 Неделя"), (2, "2 Неделя"), (3, "3 Неделя"), (4, "4 Неделя")],
                        verbose_name="Неделя",
                    ),
                ),
                ("is_done", models.BooleanField(verbose_name="Неделя завершена")),
                ("created", models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")),
                (
                    "skill",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="weeks_result",
                        to="courses.skill",
                        verbose_name="Навык",
                    ),
                ),
                (
                    "user_profile",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="weeks_result",
                        to="progress.userprofile",
                        verbose_name="Пользователь",
                    ),
                ),
            ],
            options={
                "verbose_name": "Завершенная неделя",
                "verbose_name_plural": "Завершенные недели",
            },
        ),
        migrations.AddConstraint(
            model_name="userskilldone",
            constraint=models.UniqueConstraint(fields=("user_profile", "skill"), name="unique_skill_in_profile"),
        ),
        migrations.AddConstraint(
            model_name="userweekstat",
            constraint=models.UniqueConstraint(fields=("user_profile", "skill", "week"), name="unique_week_stat"),
        ),
    ]
