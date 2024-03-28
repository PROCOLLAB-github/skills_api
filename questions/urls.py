from django.urls import path

from questions.views import (
    InfoSlideDetails,
    QuestionSingleAnswerGet,
    SingleCorrectPost,
    QuestionConnectGet,
    ConnectQuestionPost,
    QuestionExcludePost,
    QuestionExcludeAnswerGet,
)

urlpatterns = [
    path(
        "info-slide/<int:task_obj_id>",
        InfoSlideDetails.as_view(),
        name="infoslide_details",
    ),
    path(
        "single-correct/<int:task_obj_id>",
        QuestionSingleAnswerGet.as_view(),
        name="single_answer",
    ),
    path(
        "single-correct/check/<int:answer_id>",
        SingleCorrectPost.as_view(),
        name="single_answer",
    ),
    path(
        "connect/<int:task_obj_id>",
        QuestionConnectGet.as_view(),
        name="single_answer",
    ),
    path(
        "connect/check/<int:task_obj_id>",
        ConnectQuestionPost.as_view(),
        name="single_answer",
    ),
    path(
        "exclude-correct/<int:task_obj_id>",
        QuestionExcludeAnswerGet.as_view(),
        name="single_answer",
    ),
    path(
        "exclude/check/<int:task_obj_id>",
        QuestionExcludePost.as_view(),
        name="single_answer",
    ),
]
