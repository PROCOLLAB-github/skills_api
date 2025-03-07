from django.urls import path

from questions.views import (ConnectQuestionPost, InfoSlideDetails,
                             QuestionConnectGet, QuestionExcludeAnswerGet,
                             QuestionExcludePost, QuestionSingleAnswerGet,
                             SingleCorrectPost)
from questions.views.answers import InfoSlidePost, QuestionWritePost
from questions.views.questions_views import QuestionWriteAnswer

urlpatterns = [
    path(
        "info-slide/<int:task_obj_id>",
        InfoSlideDetails.as_view(),
        name="info-slide-get",
    ),
    path(
        "info-slide/check/<int:task_obj_id>",
        InfoSlidePost.as_view(),
        name="info-slide-post",
    ),
    path(
        "single-correct/<int:task_obj_id>",
        QuestionSingleAnswerGet.as_view(),
        name="single-correct-get",
    ),
    path(
        "single-correct/check/<int:task_obj_id>",
        SingleCorrectPost.as_view(),
        name="single-correct-post",
    ),
    path(
        "connect/<int:task_obj_id>",
        QuestionConnectGet.as_view(),
        name="connect-question-get",
    ),
    path(
        "connect/check/<int:task_obj_id>",
        ConnectQuestionPost.as_view(),
        name="connect-question-post",
    ),
    path(
        "exclude/<int:task_obj_id>",
        QuestionExcludeAnswerGet.as_view(),
        name="exclude-question-get",
    ),
    path(
        "exclude/check/<int:task_obj_id>",
        QuestionExcludePost.as_view(),
        name="exclude-question-post",
    ),
    path(
        "write/<int:task_obj_id>",
        QuestionWriteAnswer.as_view(),
        name="write-question-get",
    ),
    path(
        "write/check/<int:task_obj_id>",
        QuestionWritePost.as_view(),
        name="write-question-post",
    ),
]
