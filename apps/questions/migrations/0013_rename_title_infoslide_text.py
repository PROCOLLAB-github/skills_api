# Generated by Django 5.0.3 on 2024-12-11 10:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("questions", "0012_rename_text_infoslide_description"),
    ]

    operations = [
        migrations.RenameField(
            model_name="infoslide",
            old_name="title",
            new_name="text",
        ),
    ]
