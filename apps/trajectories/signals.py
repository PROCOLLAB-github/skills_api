from django.db.models.signals import post_save
from django.dispatch import receiver

from trajectories.models import Meeting, UserTrajectory


@receiver(post_save, sender=UserTrajectory)
def create_meeting_for_new_trajectory(sender, instance, created, **kwargs):
    if created:
        Meeting.objects.create(user_trajectory=instance)
