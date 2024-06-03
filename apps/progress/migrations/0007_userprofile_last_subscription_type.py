# Generated by Django 5.0.3 on 2024-05-28 10:49

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("progress", "0006_alter_taskobjuserresult_task_object"),
        ("subscription", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="userprofile",
            name="last_subscription_type",
            field=models.ForeignKey(
                null=True, on_delete=django.db.models.deletion.SET_NULL, to="subscription.subscriptiontype"
            ),
        ),
    ]