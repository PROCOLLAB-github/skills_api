from django.urls import path

from progress.views.profile import UserProfileList, UserChooseSkills, CreateUserView
from progress.views.rating import UserScoreRating, UserSkillsRating

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
    path(
        "registration/",
        CreateUserView.as_view(),
    ),
]
