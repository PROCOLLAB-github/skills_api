# Generated by Django 5.0.3 on 2024-10-31 11:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("questions", "0007_infoslide_title"),
    ]

    operations = [
        migrations.AlterField(
            model_name="infoslide",
            name="text",
            field=models.TextField(blank=True, null=True),
        ),
    ]