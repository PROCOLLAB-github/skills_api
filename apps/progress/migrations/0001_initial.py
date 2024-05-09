# Generated by Django 5.0.3 on 2024-05-06 10:04

import django.db.models.deletion
import django.utils.timezone
import progress.manager
import progress.validators
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
        ("courses", "0002_initial"),
        ("files", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="CustomUser",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("last_login", models.DateTimeField(blank=True, null=True, verbose_name="last login")),
                (
                    "is_superuser",
                    models.BooleanField(
                        default=False,
                        help_text="Designates that this user has all permissions without explicitly assigning them.",
                        verbose_name="superuser status",
                    ),
                ),
                (
                    "is_staff",
                    models.BooleanField(
                        default=False,
                        help_text="Designates whether the user can log into this admin site.",
                        verbose_name="staff status",
                    ),
                ),
                ("date_joined", models.DateTimeField(default=django.utils.timezone.now, verbose_name="date joined")),
                ("email", models.EmailField(max_length=254, unique=True)),
                ("first_name", models.CharField(max_length=255, validators=[progress.validators.user_name_validator])),
                ("last_name", models.CharField(max_length=255, validators=[progress.validators.user_name_validator])),
                (
                    "patronymic",
                    models.CharField(
                        blank=True, max_length=255, null=True, validators=[progress.validators.user_name_validator]
                    ),
                ),
                ("password", models.CharField(max_length=255)),
                ("is_active", models.BooleanField(default=True, editable=False)),
                ("city", models.CharField(blank=True, max_length=255, null=True)),
                ("organization", models.CharField(blank=True, max_length=255, null=True)),
                ("age", models.DateTimeField(null=True)),
                (
                    "specialization",
                    models.CharField(max_length=40, null=True, verbose_name="Специальность пользователя"),
                ),
                ("geo_position", models.CharField(max_length=50, null=True)),
                ("speciality", models.CharField(blank=True, max_length=255, null=True)),
                ("datetime_updated", models.DateTimeField(auto_now=True)),
                ("datetime_created", models.DateTimeField(auto_now_add=True)),
                (
                    "groups",
                    models.ManyToManyField(
                        blank=True,
                        help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.group",
                        verbose_name="groups",
                    ),
                ),
                (
                    "user_permissions",
                    models.ManyToManyField(
                        blank=True,
                        help_text="Specific permissions for this user.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.permission",
                        verbose_name="user permissions",
                    ),
                ),
            ],
            options={
                "verbose_name": "Пользователь",
                "verbose_name_plural": "Пользователи",
            },
            managers=[
                ("objects", progress.manager.CustomUserManager()),
            ],
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
                    "file",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="profiles",
                        to="files.filemodel",
                        verbose_name="Картинка",
                    ),
                ),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="profiles",
                        to=settings.AUTH_USER_MODEL,
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
