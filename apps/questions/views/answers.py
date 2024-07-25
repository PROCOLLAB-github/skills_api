from django.core.exceptions import ObjectDoesNotExist
from django.db.models import QuerySet
from drf_spectacular.utils import extend_schema
from rest_framework import generics, status
from rest_framework.response import Response

from courses.serializers import IntegerListSerializer
from procollab_skills.permissions import IfSubscriptionOutdatedPermission
from progress.models import TaskObjUserResult

from questions import serializers
from questions import api_examples
from questions.exceptions import UserAlreadyAnsweredException
from questions.mapping import TypeQuestionPoints
from courses.permissions import CheckUserHasWeekPermission
from questions.permissions import CheckQuestionTypePermission, SimpleCheckQuestionTypePermission
from questions.services import handle_no_validation_required
from questions.models import (
    QuestionSingleAnswer,
    QuestionConnect,
    QuestionWrite,
    InfoSlide,
    AnswerSingle,
    AnswerConnect,
)


@extend_schema(
    summary="Проверяет прохождение вопроса c одним правильным ответом.",
    tags=["Вопросы и инфо-слайд"],
    description="""Помимо этого создаёт результат прохождения пользователем вопроса.""",
    request=serializers.QuestionTextSerializer(),
    responses={
        201: serializers.SingleCorrectPostSuccessResponseSerializer,
        400: serializers.SingleCorrectPostErrorResponseSerializer,
        403: serializers.CustomTextErrorSerializer,
    },
    examples=[
        api_examples.WRONG_SINGLE_CORECT_QUESTION_RESPONSE,
        api_examples.QUERY_DOES_NOT_EXISTS,
        api_examples.WRONG_TASKOBJECT,
        api_examples.USER_ALREADY_DONE_TASK,
    ],
)
class SingleCorrectPost(generics.CreateAPIView):
    serializer_class = serializers.SingleCorrectPostSerializer
    expected_question_model = QuestionSingleAnswer
    permission_classes = [
        IfSubscriptionOutdatedPermission,
        CheckQuestionTypePermission,
        CheckUserHasWeekPermission,
    ]

    def create(self, request, *args, **kwargs) -> Response:
        try:

            # Если у TaskObject отключена проверка ответа, то дальнешие действия не нужны.
            if not self.request_task_object.validate_answer:
                return handle_no_validation_required(
                    self.task_object_id,
                    self.profile_id,
                    TypeQuestionPoints.QUESTION_SINGLE_ANSWER,
                    request.data.get("answer_id"),
                    {"is_correct": True},
                )

            question_answers: QuerySet[AnswerSingle] = self.request_question.single_answers.all()
            given_answer: AnswerSingle = question_answers.get(id=request.data.get("answer_id"))
            is_correct_answer: bool = given_answer.is_correct
            data = {"is_correct": is_correct_answer}

            if is_correct_answer:
                TaskObjUserResult.objects.create_user_result(
                    self.task_object_id, self.profile_id, TypeQuestionPoints.QUESTION_SINGLE_ANSWER
                )
            else:
                correct_answer: AnswerSingle = question_answers.get(is_correct=True)
                data["correct_answer"] = correct_answer.id

            serializer = self.serializer_class(data=data)
            if serializer.is_valid():
                response_status = status.HTTP_201_CREATED if is_correct_answer else status.HTTP_400_BAD_REQUEST
                return Response(data, status=response_status)
            else:
                return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except (UserAlreadyAnsweredException, ObjectDoesNotExist) as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    summary="Проверить вопрос на соотношение",
    tags=["Вопросы и инфо-слайд"],
    request=serializers.ConnectQuestionPostRequestSerializer,
    responses={
        201: serializers.CustomTextSucessSerializer,
        400: serializers.ConnectQuestionPostResponseSerializer,
        403: serializers.CustomTextErrorSerializer,
    },
    examples=[
        api_examples.SUCCESS_RESPONSE,
        api_examples.WRONG_ANSWERS_QUESTION_CONNECT_RESPONSE,
        api_examples.QUERY_DOES_NOT_EXISTS,
        api_examples.WRONG_TASKOBJECT,
        api_examples.USER_ALREADY_DONE_TASK,
    ],
)
class ConnectQuestionPost(generics.CreateAPIView):
    serializer_class = serializers.ConnectQuestionPostResponseSerializer
    permission_classes = [
        IfSubscriptionOutdatedPermission,
        CheckQuestionTypePermission,
        CheckUserHasWeekPermission,
    ]
    expected_question_model = QuestionConnect

    def create(self, request, *args, **kwargs) -> Response:
        try:
            question: QuestionConnect = self.request_question
            all_answer_options: QuerySet[AnswerConnect] = question.connect_answers.all()

            # Если у TaskObject отключена проверка ответа, то дальнешие действия не нужны.
            if not self.request_task_object.validate_answer:
                return handle_no_validation_required(
                    self.task_object_id,
                    self.profile_id,
                    TypeQuestionPoints.QUESTION_CONNECT,
                    request.data,
                    {"text": "success"},
                    required_data=all_answer_options,
                )

            user_answers = request.data
            answers_left_to_check: list[int] = list(all_answer_options.values_list("id", flat=True))
            # all_answers_count = all_answer_options.count()

            scored_answers = []
            for user_answer in user_answers:
                check_answer = all_answer_options.get(id=user_answer["left_id"])
                user_answer["is_correct"] = check_answer.id == user_answer["right_id"]
                scored_answers.append(user_answer)
                if user_answer["is_correct"]:
                    if (
                        user_answer["left_id"] in answers_left_to_check
                    ):  # КОСТЫЛЬ УБРАТЬ КОГДА РАЗЮБЬЁМ ОТВЕТЫ НА РАЗНЫЕ МОДЕЛИ
                        answers_left_to_check.remove(user_answer["left_id"])
                    if user_answer["right_id"] in answers_left_to_check:
                        answers_left_to_check.remove(user_answer["right_id"])

            if_false_answers = not all(user_answer["is_correct"] for user_answer in user_answers)
            if_unchecked_answers = bool(len(answers_left_to_check))

            serializer = self.serializer_class(data=scored_answers)

            if serializer.is_valid() and not if_false_answers and not if_unchecked_answers:
                TaskObjUserResult.objects.create_user_result(
                    self.task_object_id, self.profile_id, TypeQuestionPoints.QUESTION_CONNECT
                )
                return Response({"text": "success"}, status=status.HTTP_201_CREATED)
            elif not serializer.is_valid():
                return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

            if if_false_answers or if_unchecked_answers:
                return Response(scored_answers, status.HTTP_400_BAD_REQUEST)

        except (UserAlreadyAnsweredException, ObjectDoesNotExist) as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# TODO сделать возможным для прохождения только прохождаемый пользователем навык
@extend_schema(
    summary="Проверка вопроса на исключение",
    tags=["Вопросы и инфо-слайд"],
    description="В request - список ответов, которые пользователь исключает\n В response - количество отв",
    request=IntegerListSerializer,
    responses={
        201: serializers.CustomTextSucessSerializer,
        400: serializers.QuestionExcludePostResponseSerializer,
        403: serializers.CustomTextErrorSerializer,
    },
    examples=[
        api_examples.SUCCESS_RESPONSE,
        api_examples.WRONG_ANSWERS_QUESTION_EXCLUDE_RESPONSE,
        api_examples.NEED_MORE_QUESTION_EXCLUDE_RESPONSE,
        api_examples.QUERY_DOES_NOT_EXISTS,
        api_examples.WRONG_TASKOBJECT,
        api_examples.USER_ALREADY_DONE_TASK,
    ],
)
class QuestionExcludePost(generics.CreateAPIView):
    serializer_class = serializers.SimpleNumberListSerializer
    permission_classes = [
        IfSubscriptionOutdatedPermission,
        CheckQuestionTypePermission,
        CheckUserHasWeekPermission,
    ]
    expected_question_model = QuestionSingleAnswer

    def create(self, request, *args, **kwargs) -> Response:
        try:
            given_answer_ids: list[int] = request.data

            # Если у TaskObject отключена проверка ответа, то дальнешие действия не нужны.
            if not self.request_task_object.validate_answer:
                return handle_no_validation_required(
                    self.task_object_id,
                    self.profile_id,
                    TypeQuestionPoints.QUESTION_EXCLUDE,
                    given_answer_ids,
                    {"text": "success"},
                )

            # Все правильные ответы (в рамках исключения).
            set_correct_answer_ids: set[int] = set(
                self.request_question.single_answers.filter(is_correct=False).values_list("id", flat=True)
            )
            set_given_answer_ids: set[int] = set(given_answer_ids)

            # Проверка - все правильные ответы были даны.
            if set_given_answer_ids == set_correct_answer_ids:
                TaskObjUserResult.objects.create_user_result(
                    self.task_object_id, self.profile_id, TypeQuestionPoints.QUESTION_EXCLUDE
                )
                return Response({"text": "success"}, status=status.HTTP_201_CREATED)
            # Проверка - даны правильные ответы, но часть правильных отсутствует.
            elif set_given_answer_ids.issubset(set_correct_answer_ids):
                return Response({"text": "need more..."}, status=status.HTTP_400_BAD_REQUEST)
            # Иначе, если есть неправильные ответы/сторонние id.
            else:
                wrong_answers: list[int] = list(set_given_answer_ids - set_correct_answer_ids)
                return Response(
                    {"is_correct": False, "wrong_answers": wrong_answers}, status=status.HTTP_400_BAD_REQUEST
                )
        except UserAlreadyAnsweredException as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# POST ответить на вопрос для текста


@extend_schema(
    summary="Сохранение ответа пользователя на ответ, требующий ввод текста",
    tags=["Вопросы и инфо-слайд"],
    request=serializers.WriteAnswerTextSerializer(),
    responses={
        201: serializers.CustomTextSucessSerializer,
        400: serializers.CustomTextErrorSerializer,
        403: serializers.CustomTextErrorSerializer,
    },
    examples=[api_examples.SUCCESS_RESPONSE, api_examples.USER_ALREADY_DONE_TASK, api_examples.WRONG_TASKOBJECT],
)
class QuestionWritePost(generics.CreateAPIView):
    serializer_class = serializers.WriteAnswerTextSerializer
    expected_question_model = QuestionWrite
    permission_classes = [
        IfSubscriptionOutdatedPermission,
        SimpleCheckQuestionTypePermission,
        CheckUserHasWeekPermission,
    ]

    def create(self, request, *args, **kwargs) -> Response:
        try:
            user_answer: str = request.data["text"]
            if len(user_answer):
                TaskObjUserResult.objects.create_user_result(
                    self.task_object_id, self.profile_id, TypeQuestionPoints.QUESTION_WRITE
                )
                return Response({"text": "success"}, status=status.HTTP_201_CREATED)

            return Response({"error": "You can't save an empty answer!"}, status=status.HTTP_400_BAD_REQUEST)
        except UserAlreadyAnsweredException as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    summary="Пометить InfoSlide как сделанный",
    tags=["Вопросы и инфо-слайд"],
    responses={
        204: None,
        400: serializers.CustomTextErrorSerializer,
        403: serializers.CustomTextErrorSerializer,
    },
    examples=[api_examples.USER_ALREADY_DONE_TASK, api_examples.WRONG_TASKOBJECT],
)
class InfoSlidePost(generics.CreateAPIView):
    expected_question_model = InfoSlide
    permission_classes = [
        IfSubscriptionOutdatedPermission,
        SimpleCheckQuestionTypePermission,
        CheckUserHasWeekPermission,
    ]

    def create(self, request, *args, **kwargs) -> Response:
        try:
            TaskObjUserResult.objects.create_user_result(
                self.task_object_id, self.profile_id, TypeQuestionPoints.INFO_SLIDE
            )
            return Response("successful", status=status.HTTP_204_NO_CONTENT)
        except UserAlreadyAnsweredException as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
