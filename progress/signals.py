from django.core.exceptions import ValidationError


def skills_changed(sender, instance, action, **kwargs):
    if instance.chosen_skills.count() > 5:
        raise ValidationError("User has already chosen 5 skills")
