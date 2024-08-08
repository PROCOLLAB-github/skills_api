from django.core.exceptions import ValidationError

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomUser, UserProfile, TaskObjUserResult


def skills_changed(sender, instance, action, **kwargs):
    if instance.chosen_skills.count() > 5:
        raise ValidationError("User has already chosen 5 skills")


@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=TaskObjUserResult)
def recalculation_user_statistics(sender, instance, created, **kwargs) -> None:
    """При созданиии записи `TaskObjUserResult` формирует 2 Celery таски."""
    # Циклический импорт.
    from progress.tasks import check_skill_done, check_week_stat
    if created:
        check_skill_done.delay(instance.pk)
        check_week_stat.delay(instance.pk)
