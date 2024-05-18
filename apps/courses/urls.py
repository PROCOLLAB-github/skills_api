from django.urls import path

from courses.views import SkillsList, SkillDetails, TaskList, TasksOfSkill, TaskStatsGet

urlpatterns = [
    path("<int:task_id>", TaskList.as_view(), name="task_list"),
    path("all-skills/", SkillsList.as_view()),
    path("skill-details/<int:skill_id>", SkillDetails.as_view()),
    path("tasks-of-skill/<int:skill_id>", TasksOfSkill.as_view()),
    path("task-result/<int:task_id>", TaskStatsGet.as_view()),
]
