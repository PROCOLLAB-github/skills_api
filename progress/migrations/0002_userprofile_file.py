# Generated by Django 5.0.3 on 2024-04-25 15:11

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("files", "0001_initial"),
        ("progress", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="userprofile",
            name="file",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="profiles",
                to="files.filemodel",
                verbose_name="Картинка",
            ),
        ),
    ]
