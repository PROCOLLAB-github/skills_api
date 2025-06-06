from django.apps import AppConfig


class ProgressConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "progress"
    verbose_name = "Результаты прохождения заданий"

    def ready(self):
        from django.db.models.signals import m2m_changed

        from progress.models import UserProfile
        from progress.signals import skills_changed

        m2m_changed.connect(skills_changed, sender=UserProfile.chosen_skills.through)
