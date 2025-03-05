from django.apps import AppConfig


class TrajectoriesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "trajectories"
    verbose_name = "Траектории"

    def ready(self):
        import trajectories.signals  # noqa
