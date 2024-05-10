from django.urls import path

from courses.views import SkillsList, SkillDetails, TaskList, TasksOfSkill, NewLevel

urlpatterns = [
    path("<int:task_id>", TaskList.as_view(), name="task_list"),
    path("all-skills/", SkillsList.as_view()),
    path("skill-details/<int:skill_id>", SkillDetails.as_view()),
    path("tasks-of-skill/<int:skill_id>", TasksOfSkill.as_view()),
    path("new-level-stats/<int:task_id>", NewLevel.as_view()),
    # path("skill-task-status/<int:skill_id>", SkillTaskStatus.as_view()),
]
