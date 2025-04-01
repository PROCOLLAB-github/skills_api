from django.urls import path

from .views import (MeetingUpdateView, MentorStudentsView,
                    TrajectoryDetailView, TrajectoryListView,
                    UserIndividualSkillListView, UserTrajectoryCreateView,
                    UserTrajectoryView)

urlpatterns = [
    path("", TrajectoryListView.as_view(), name="trajectory_list"),
    path("<int:id>/", TrajectoryDetailView.as_view(), name="trajectory-detail"),
    path("user-trajectory/", UserTrajectoryView.as_view(), name="user-trajectory"),
    path("user-trajectory/create/", UserTrajectoryCreateView.as_view(), name="user-trajectory-create"),
    path('individual-skills/', UserIndividualSkillListView.as_view(), name='individual-skill-list'),
    path("mentor/students/", MentorStudentsView.as_view(), name="mentor-students"),
    path("meetings/update/", MeetingUpdateView.as_view(), name="meeting-update"),
]
