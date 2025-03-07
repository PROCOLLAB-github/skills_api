import os

import django
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "procollab_skills.settings")
django.setup()

app = Celery("procollab_skills")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()

app.conf.task_serializer = "json"

# Расписание задач
app.conf.beat_schedule = {
    "daily_resub_users": {
        "task": "subscription.tasks.daily_resub_users",
        "schedule": crontab(minute=0, hour=0),
    },
    "user_month_stat": {
        "task": "progress.tasks.monthly_check_user_goals",
        "schedule": crontab(0, 0, day_of_month="1"),
    },
}

if __name__ == "__main__":
    app.start()
