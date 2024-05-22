from django.apps import AppConfig


class ProgressConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "progress"
    verbose_name = "Результаты прохождения заданий"

    def ready(self):
        from progress.signals import skills_changed
        from progress.models import UserProfile
        from django.db.models.signals import m2m_changed
        from procollab_skills.schema import MyAuthenticationScheme  # noqa: F401

        m2m_changed.connect(skills_changed, sender=UserProfile.chosen_skills.through)
