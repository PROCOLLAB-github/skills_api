from procollab_skills.celery import app
from progress.constants import MONTHS_CACHING_TIMEOUT
from progress.models import UserProfile
from progress.services import last_two_months_stats
from django.core.cache import cache


# @app.task
# def nullify_skills_for_all_users():
#     all_instances = UserProfile.objects.all()
#     for instance in all_instances:
#         instance.chosen_skills.clear()


@app.task
def profile_month_recache():
    user_profiles = UserProfile.objects.values_list("id", flat=True)
    # TODO сделать чтобы у "неактивных" пользователей кэш не обновлялся
    for profile_id in user_profiles:
        months_stats = last_two_months_stats(profile_id)
        cache.set(f"months_data_{profile_id}", months_stats, MONTHS_CACHING_TIMEOUT)
