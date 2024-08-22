# Generated by Django 5.0.3 on 2024-08-01 09:25

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("courses", "0011_task_week_alter_taskobject_validate_answer"),
        ("progress", "0014_userskilldone_userweekstat_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="UserMonthStat",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "month",
                    models.PositiveSmallIntegerField(
                        choices=[
                            (1, "Январь"),
                            (2, "Февраль"),
                            (3, "Март"),
                            (4, "Апрель"),
                            (5, "Май"),
                            (6, "Июнь"),
                            (7, "Июль"),
                            (8, "Август"),
                            (9, "Сентябрь"),
                            (10, "Октябрь"),
                            (11, "Ноябрь"),
                            (12, "Декабрь"),
                        ],
                        verbose_name="Месяц",
                    ),
                ),
                ("year", models.PositiveSmallIntegerField(verbose_name="Год")),
                ("successfully_done", models.BooleanField(verbose_name="Месяц успешно закрыт")),
                (
                    "user_profile",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="month_results",
                        to="progress.userprofile",
                        verbose_name="Пользователь",
                    ),
                ),
            ],
            options={
                "verbose_name": "Статистика по месяцу",
                "verbose_name_plural": "Статистика по месяцам",
            },
        ),
        migrations.CreateModel(
            name="UserMonthTarget",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "month",
                    models.PositiveSmallIntegerField(
                        choices=[
                            (1, "Январь"),
                            (2, "Февраль"),
                            (3, "Март"),
                            (4, "Апрель"),
                            (5, "Май"),
                            (6, "Июнь"),
                            (7, "Июль"),
                            (8, "Август"),
                            (9, "Сентябрь"),
                            (10, "Октябрь"),
                            (11, "Ноябрь"),
                            (12, "Декабрь"),
                        ],
                        verbose_name="Месяц",
                    ),
                ),
                ("year", models.PositiveSmallIntegerField(verbose_name="Год")),
                (
                    "percentage_of_completion",
                    models.PositiveSmallIntegerField(
                        help_text="Цель по навыку до конца текущего месяца", verbose_name="Необходимый % комплита"
                    ),
                ),
                (
                    "skill",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="months_result",
                        to="courses.skill",
                        verbose_name="Навык",
                    ),
                ),
                (
                    "user_profile",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="month_targets",
                        to="progress.userprofile",
                        verbose_name="Пользователь",
                    ),
                ),
            ],
            options={
                "verbose_name": "Месячная цель пользователя",
                "verbose_name_plural": "Месячные цели пользователей",
            },
        ),
        migrations.AddConstraint(
            model_name="usermonthstat",
            constraint=models.UniqueConstraint(fields=("user_profile", "month", "year"), name="unique_month_stat"),
        ),
        migrations.AddConstraint(
            model_name="usermonthtarget",
            constraint=models.UniqueConstraint(
                fields=("user_profile", "skill", "month", "year"), name="unique_month_target"
            ),
        ),
    ]
