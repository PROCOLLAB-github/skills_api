# Generated by Django 5.0.3 on 2024-09-30 20:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("courses", "0013_alter_task_managers"),
        ("progress", "0015_usermonthstat_usermonthtarget_and_more"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="intermediateuserskills",
            unique_together={("user_profile", "date_chosen", "skill")},
        ),
    ]
