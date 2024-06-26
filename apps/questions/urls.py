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
from questions.views.answers import QuestionWritePost, InfoSlidePost
from questions.views.questions import QuestionWriteAnswer

urlpatterns = [
    path(
        "info-slide/<int:task_obj_id>",
        InfoSlideDetails.as_view(),
    ),
    path(
        "info-slide/check/<int:task_obj_id>",
        InfoSlidePost.as_view(),
    ),
    path(
        "single-correct/<int:task_obj_id>",
        QuestionSingleAnswerGet.as_view(),
    ),
    path(
        "single-correct/check/<int:task_obj_id>",
        SingleCorrectPost.as_view(),
    ),
    path(
        "connect/<int:task_obj_id>",
        QuestionConnectGet.as_view(),
    ),
    path(
        "connect/check/<int:task_obj_id>",
        ConnectQuestionPost.as_view(),
    ),
    path(
        "exclude/<int:task_obj_id>",
        QuestionExcludeAnswerGet.as_view(),
    ),
    path(
        "exclude/check/<int:task_obj_id>",
        QuestionExcludePost.as_view(),
    ),
    path(
        "write/<int:task_obj_id>",
        QuestionWriteAnswer.as_view(),
    ),
    path(
        "write/check/<int:task_obj_id>",
        QuestionWritePost.as_view(),
    ),
]
