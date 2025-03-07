from django.urls import path

from progress.views.profile import (CreateUserView, GetUserProfileData,
                                    SubscriptionUserData, SyncUserProfile,
                                    UpdateAutoRenewal, UserChooseSkills,
                                    UserProfile)
from progress.views.rating import UserScoreRating, UserSkillsRating

urlpatterns = [
    path(
        "profile/",
        UserProfile.as_view(),
        name="user-profile",
    ),
    path(
        "subscription-data/",
        SubscriptionUserData.as_view(),
        name="subscribtion-user-data",
    ),
    path(
        "add-skills/",
        UserChooseSkills.as_view(),
        name="add-skills",
    ),
    path(
        "user-rating/",
        UserScoreRating.as_view(),
        name="user-score-rating",
    ),
    path(
        "skill-rating/",
        UserSkillsRating.as_view(),
        name="skill-rating",
    ),
    path(
        "registration/",
        CreateUserView.as_view(),
        name="registration",
    ),
    path(
        "update-auto-renewal/",
        UpdateAutoRenewal.as_view(),
        name="update-auto-renewal",
    ),
    path(
        "user-data/",
        GetUserProfileData.as_view(),
        name="user-data",
    ),
    path(
        'sync-profile/', 
        SyncUserProfile.as_view()),
]
