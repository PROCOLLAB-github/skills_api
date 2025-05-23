# Generated by Django 5.0.3 on 2024-10-29 21:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("courses", "0013_alter_task_managers"),
    ]

    operations = [
        migrations.AlterField(
            model_name="skill",
            name="status",
            field=models.CharField(
                choices=[
                    ("draft", "Черновик"),
                    ("published", "Опубликован"),
                    ("stuff_only", "Доступ только у персонала"),
                ],
                default="draft",
                max_length=15,
                verbose_name="Статус",
            ),
        ),
        migrations.AlterField(
            model_name="task",
            name="status",
            field=models.CharField(
                choices=[
                    ("draft", "Черновик"),
                    ("published", "Опубликован"),
                    ("stuff_only", "Доступ только у персонала"),
                ],
                default="draft",
                max_length=15,
                verbose_name="Статус",
            ),
        ),
    ]
