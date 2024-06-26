# Generated by Django 5.0.3 on 2024-06-06 15:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("courses", "0005_task_ordinal_number"),
    ]

    operations = [
        migrations.AddField(
            model_name="skill",
            name="status",
            field=models.CharField(
                choices=[("draft", "Черновик"), ("published", "Опубликован")],
                default="draft",
                max_length=15,
                verbose_name="Статус",
            ),
        ),
    ]
