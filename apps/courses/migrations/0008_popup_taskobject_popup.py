# Generated by Django 5.0.3 on 2024-06-21 16:09

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("courses", "0007_skill_skill_point_logo_skill_skill_preview_and_more"),
        ("files", "0002_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Popup",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(blank=True, max_length=150, null=True, verbose_name="Заголовок")),
                ("text", models.TextField(blank=True, null=True, verbose_name="Содержимое")),
                (
                    "ordinal_number",
                    models.PositiveSmallIntegerField(blank=True, null=True, verbose_name="Порядковый номер"),
                ),
                (
                    "file",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="popups",
                        to="files.filemodel",
                        verbose_name="Изображение",
                    ),
                ),
            ],
            options={
                "verbose_name": "Поп-ап",
                "verbose_name_plural": "Поп-апы",
            },
        ),
        migrations.AddField(
            model_name="taskobject",
            name="popup",
            field=models.ManyToManyField(
                blank=True, related_name="task_objects", to="courses.popup", verbose_name="Поп-ап"
            ),
        ),
    ]
