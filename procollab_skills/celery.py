import os

from celery import Celery
import django
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "procollab_skills.settings")
django.setup()

app = Celery("procollab_skills")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()

app.conf.task_serializer = "json"

# Расписание задач
app.conf.beat_schedule = {
    "nullify_skills_for_all_users": {
        "task": "progress.tasks.nullify_skills_for_all_users",
        "schedule": crontab(0, 0, day_of_month="1"),
    },
    "profile_month_recache": {
        "task": "progress.tasks.profile_month_recache",
        "schedule": crontab(0, 0, day_of_month="1"),
    },
}

if __name__ == "__main__":
    app.start()
