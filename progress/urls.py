from django.urls import path

from progress.views.profile_views import UserProfileList, UserChooseSkills
from progress.views.rating_views import UserScoreRating, UserSkillsRating

urlpatterns = [
    path(
        "profile/",
        UserProfileList.as_view(),
        name="profile",
    ),
    path(
        "add-skills/",
        UserChooseSkills.as_view(),
        name="choose_skills",
    ),
    path(
        "user-rating/",
        UserScoreRating.as_view(),
        name="choose_skills",
    ),
    path(
        "skill-rating/",
        UserSkillsRating.as_view(),
        name="choose_skills",
    ),
]
