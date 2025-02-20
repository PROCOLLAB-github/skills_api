from django.urls import path

from .views import (TrajectoryDetailView, TrajectoryListView,
                    TrajectorySkillsView)

urlpatterns = [
    path("", TrajectoryListView.as_view(), name="trajectory_list"),
    path("<int:id>/", TrajectoryDetailView.as_view(), name="trajectory-detail"),
    path("<int:id>/skills/", TrajectorySkillsView.as_view(), name="trajectory-skills"),
]
