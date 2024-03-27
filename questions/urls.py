from django.urls import path

from questions.views import InfoSlideDetails, QuestionSingleAnswerGet, SingleCorrectPost, QuestionConnectGet, \
    ConnectQuestionPost, QuestionExcludePost

urlpatterns = [
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

]


