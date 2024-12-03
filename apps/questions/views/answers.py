from django.core.exceptions import ObjectDoesNotExist
from drf_spectacular.utils import extend_schema
from rest_framework import generics, status
from rest_framework.response import Response

from questions.services.check_questions_answers import (
    InfoSlideAnswerService,
    QuestionConnectAnswerService,
    QuestionExcludeAnswerService,
    QuestionWriteAnswerService,
    SingleCorrectAnswerService,
)
from courses.serializers import IntegerListSerializer
from procollab_skills.permissions import IfSubscriptionOutdatedPermission

from questions import serializers
from questions import api_examples
from questions.exceptions import (
    QustionConnectException,
    UserAlreadyAnsweredException,
)
from questions.permissions import (
    CheckQuestionTypePermission,
    SimpleCheckQuestionTypePermission,
)
from questions.models import (
    QuestionSingleAnswer,
    QuestionConnect,
    QuestionWrite,
    InfoSlide,
)


@extend_schema(
    summary="Проверяет прохождение вопроса c одним правильным ответом.",
    tags=["Вопросы и инфо-слайд"],
    description="""Помимо этого создаёт результат прохождения пользователем вопроса.""",
    request=serializers.QuestionTextSerializer(),
    responses={
        201: serializers.CorrectAnswerResponse,
        400: serializers.IncorrectAnswerResponse,
        403: serializers.CustomTextErrorSerializer,
    },
    examples=[
        api_examples.WRONG_ANSWER_RESPONSE,
        api_examples.SINGLE_RESPONSE_WITH_ANSWER,
        api_examples.SUCCESS_RESPONSE,
        api_examples.QUERY_DOES_NOT_EXISTS,
        api_examples.WRONG_TASKOBJECT,
        api_examples.USER_ALREADY_DONE_TASK,
        api_examples.WRONG_ANSWER_RESPONSE_WITH_HINT,
    ],
)
class SingleCorrectPost(generics.CreateAPIView):
    expected_question_model = QuestionSingleAnswer
    permission_classes = [IfSubscriptionOutdatedPermission, CheckQuestionTypePermission]

    def create(self, request, *args, **kwargs) -> Response:
        try:
            service = SingleCorrectAnswerService(
                request_profile_id=self.profile_id,
                request_question=self.request_question,
                request_task_object=self.request_task_object,
                request_data=self.request.data,
            )
            response_body, response_status = service.create_answer()
            return Response(response_body, status=response_status)
        except (UserAlreadyAnsweredException, ObjectDoesNotExist) as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    summary="Проверить вопрос на соотношение",
    tags=["Вопросы и инфо-слайд"],
    request=serializers.ConnectQuestionPostRequestSerializer,
    responses={
        201: serializers.CorrectAnswerResponse,
        400: serializers.IncorrectAnswerResponse,
        403: serializers.CustomTextErrorSerializer,
    },
    examples=[
        api_examples.WRONG_ANSWER_RESPONSE,
        api_examples.SUCCESS_RESPONSE,
        api_examples.CONNECT_RESPONSE_WITH_ANSWER,
        api_examples.QUERY_DOES_NOT_EXISTS,
        api_examples.WRONG_TASKOBJECT,
        api_examples.USER_ALREADY_DONE_TASK,
        api_examples.WRONG_ANSWER_RESPONSE_WITH_HINT,
    ],
)
class ConnectQuestionPost(generics.CreateAPIView):
    permission_classes = [IfSubscriptionOutdatedPermission, CheckQuestionTypePermission]
    expected_question_model = QuestionConnect

    def create(self, request, *args, **kwargs) -> Response:
        try:
            service = QuestionConnectAnswerService(
                request_profile_id=self.profile_id,
                request_question=self.request_question,
                request_task_object=self.request_task_object,
                request_data=self.request.data,
            )
            response_body, response_status = service.create_answer()
            return Response(response_body, status=response_status)
        except (UserAlreadyAnsweredException, ObjectDoesNotExist, QustionConnectException) as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    summary="Проверка вопроса на исключение",
    tags=["Вопросы и инфо-слайд"],
    description="В request - список ответов, которые пользователь исключает\n В response - количество отв",
    request=IntegerListSerializer,
    responses={
        201: serializers.CorrectAnswerResponse,
        400: serializers.IncorrectAnswerResponse,
        403: serializers.CustomTextErrorSerializer,
    },
    examples=[
        api_examples.SUCCESS_RESPONSE,
        api_examples.EXCLUDE_RESPONSE_WITH_ANSWER,
        api_examples.WRONG_ANSWER_RESPONSE,
        api_examples.QUERY_DOES_NOT_EXISTS,
        api_examples.WRONG_TASKOBJECT,
        api_examples.USER_ALREADY_DONE_TASK,
        api_examples.WRONG_ANSWER_RESPONSE_WITH_HINT,
    ],
)
class QuestionExcludePost(generics.CreateAPIView):
    permission_classes = [IfSubscriptionOutdatedPermission, CheckQuestionTypePermission]
    expected_question_model = QuestionSingleAnswer

    def create(self, request, *args, **kwargs) -> Response:
        try:
            service = QuestionExcludeAnswerService(
                request_profile_id=self.profile_id,
                request_question=self.request_question,
                request_task_object=self.request_task_object,
                request_data=self.request.data,
            )
            response_body, response_status = service.create_answer()
            return Response(response_body, status=response_status)
        except UserAlreadyAnsweredException as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    summary="Сохранение ответа пользователя на ответ, требующий ввод текста",
    tags=["Вопросы и инфо-слайд"],
    request=serializers.WriteAnswerTextSerializer(),
    responses={
        201: serializers.CorrectAnswerResponse,
        400: serializers.IncorrectAnswerResponse,
        403: serializers.CustomTextErrorSerializer,
    },
    examples=[
        api_examples.SUCCESS_RESPONSE,
        api_examples.WRONG_ANSWER_RESPONSE,
        api_examples.USER_ALREADY_DONE_TASK,
        api_examples.WRONG_TASKOBJECT,
    ],
)
class QuestionWritePost(generics.CreateAPIView):
    serializer_class = serializers.WriteAnswerTextSerializer
    expected_question_model = QuestionWrite
    permission_classes = [IfSubscriptionOutdatedPermission, SimpleCheckQuestionTypePermission]

    def create(self, request, *args, **kwargs) -> Response:
        try:
            service = QuestionWriteAnswerService(
                request_profile_id=self.profile_id,
                request_question=self.request_question,
                request_task_object=self.request_task_object,
                request_data=self.request.data,
            )
            response_body, response_status = service.create_answer()
            return Response(response_body, status=response_status)
        except UserAlreadyAnsweredException as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    summary="Пометить InfoSlide как сделанный",
    request=serializers.EmptySerializer(),
    tags=["Вопросы и инфо-слайд"],
    responses={
        201: serializers.CorrectAnswerResponse,
        400: serializers.IncorrectAnswerResponse,
        403: serializers.CustomTextErrorSerializer,
    },
    examples=[
        api_examples.SUCCESS_RESPONSE,
        api_examples.WRONG_ANSWER_RESPONSE,
        api_examples.USER_ALREADY_DONE_TASK,
        api_examples.WRONG_TASKOBJECT,
    ],
)
class InfoSlidePost(generics.CreateAPIView):
    expected_question_model = InfoSlide
    permission_classes = [IfSubscriptionOutdatedPermission, SimpleCheckQuestionTypePermission]

    def create(self, request, *args, **kwargs) -> Response:
        try:
            service = InfoSlideAnswerService(
                request_profile_id=self.profile_id,
                request_question=self.request_question,
                request_task_object=self.request_task_object,
                request_data=self.request.data,
            )
            response_body, response_status = service.create_answer()
            return Response(response_body, status=response_status)
        except UserAlreadyAnsweredException as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
