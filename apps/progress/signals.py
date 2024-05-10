from django.core.exceptions import ValidationError

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomUser, UserProfile


def skills_changed(sender, instance, action, **kwargs):
    if instance.chosen_skills.count() > 5:
        raise ValidationError("User has already chosen 5 skills")


@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
