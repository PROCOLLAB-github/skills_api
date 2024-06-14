from django.urls import path

from progress.views.profile import (
    UserProfileList,
    UserChooseSkills,
    CreateUserView,
    SubscriptionUserData,
    UpdateAutoRenewal,
)
from progress.views.rating import UserScoreRating, UserSkillsRating


urlpatterns = [
    path(
        "profile/",
        UserProfileList.as_view(),
    ),
    path(
        "subscription-data/",
        SubscriptionUserData.as_view(),
    ),
    path(
        "add-skills/",
        UserChooseSkills.as_view(),
        name="choose_skills",
    ),
    path(
        "user-rating/",
        UserScoreRating.as_view(),
    ),
    path(
        "skill-rating/",
        UserSkillsRating.as_view(),
    ),
    path(
        "registration/",
        CreateUserView.as_view(),
    ),
    path(
        "update-auto-renewal/",
        UpdateAutoRenewal.as_view(),
    ),
]
