from django.urls import path

from courses.views import SkillsList, SkillDetails, TaskList

urlpatterns = [
    path("<int:task_id>", TaskList.as_view(), name="task_list"),
    path(
        "all-skills/",
        SkillsList.as_view(),
        name="single_answer",
    ),
    path(
        "skill-details/<int:skill_id>",
        SkillDetails.as_view(),
        name="single_answer",
    ),
]
