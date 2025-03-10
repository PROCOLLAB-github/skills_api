# Generated by Django 5.0.3 on 2024-12-26 09:34

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("questions", "0013_rename_title_infoslide_text"),
    ]

    operations = [
        migrations.AlterField(
            model_name="questionconnect",
            name="attempts_after_hint",
            field=models.SmallIntegerField(
                blank=True,
                null=True,
                validators=[django.core.validators.MinValueValidator(1)],
                verbose_name="Попытки после подсказки",
            ),
        ),
        migrations.AlterField(
            model_name="questionconnect",
            name="attempts_before_hint",
            field=models.SmallIntegerField(
                blank=True,
                null=True,
                validators=[django.core.validators.MinValueValidator(1)],
                verbose_name="Попытки до подсказки",
            ),
        ),
        migrations.AlterField(
            model_name="questionsingleanswer",
            name="attempts_after_hint",
            field=models.SmallIntegerField(
                blank=True,
                null=True,
                validators=[django.core.validators.MinValueValidator(1)],
                verbose_name="Попытки после подсказки",
            ),
        ),
        migrations.AlterField(
            model_name="questionsingleanswer",
            name="attempts_before_hint",
            field=models.SmallIntegerField(
                blank=True,
                null=True,
                validators=[django.core.validators.MinValueValidator(1)],
                verbose_name="Попытки до подсказки",
            ),
        ),
    ]
