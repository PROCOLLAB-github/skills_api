from django.urls import path

from courses.views import (DoneSkillsList, SkillDetails, SkillsList,
                           TaskDetail, TasksOfSkill, TaskStatsGet)

urlpatterns = [
    path("<int:task_id>", TaskDetail.as_view(), name="task_detail"),
    path("all-skills/", SkillsList.as_view(), name="all-skills"),
    path("choose-skills/", DoneSkillsList.as_view(), name="choose-skills"),
    path("skill-details/<int:skill_id>", SkillDetails.as_view(), name="skill-details"),
    path("tasks-of-skill/<int:skill_id>", TasksOfSkill.as_view(), name="tasks-of-skill"),
    path("task-result/<int:task_id>", TaskStatsGet.as_view(), name="task-result"),
]
