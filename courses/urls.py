from django.urls import path

from courses.views import *
from courses.views.task_skill_infoslide_views import SkillsList, SkillDetails

urlpatterns = [
    path("<int:task_id>", TaskList.as_view(), name="task_list"),
    path(
        "info-slide/<int:infoslide_id>",
        InfoSlideDetails.as_view(),
        name="infoslide_details",
    ),
    path(
        "single-correct/<int:question_single_answer_id>",
        QuestionSingleAnswerGet.as_view(),
        name="single_answer",
    ),
    path(
        "single-correct/check/<int:answer_id>",
        SingleCorrectPost.as_view(),
        name="single_answer",
    ),
    path(
        "connect/<int:question_connection_id>",
        QuestionConnectGet.as_view(),
        name="single_answer",
    ),
    path(
        "connect/check/<int:question_connection_id>",
        ConnectQuestionPost.as_view(),
        name="single_answer",
    ),
    path(
        "exclude/check/<int:exclude_question_id>",
        QuestionExcludePost.as_view(),
        name="single_answer",
    ),
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


