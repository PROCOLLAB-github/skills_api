from django.core.exceptions import ObjectDoesNotExist
from django.db.models import QuerySet
from drf_spectacular.utils import extend_schema
from rest_framework import generics, serializers, status
from rest_framework.response import Response

from progress.models import UserProfile
from progress.services import create_user_result
from questions.exceptions import UserAlreadyAnsweredException
from questions.mapping import TypeQuestionPoints
from questions.permissions import CheckQuestionTypePermission, SimpleCheckQuestionTypePermission
from questions.models import (
    QuestionSingleAnswer,
    QuestionConnect,
    QuestionWrite,
    InfoSlide,
    AnswerSingle,
    AnswerConnect,
)
from questions.serializers import (
    ConnectQuestionPostResponseSerializer,
    CustomTextSerializer,
    CustomTextSucessSerializer,
    SimpleNumberListSerializer,
    SingleCorrectPostSerializer,
    WriteAnswerSerializer,
    WriteAnswerTextSerializer,
    QuestionTextSerializer,
    ConnectAnswerSerializer,
)


# TODO сделать, чтобы если юзер прошёл задание идеально правильно ранее (есть сохраненный результат),
#  то выводился ещё и он,
# а не только вопрос
# https://www.figma.com/file/cZKZgA3ZywZykhZuHn1OQk/ProCollab?type=design&node-id=377-634&mode=design&t=Pxo1vEpfsWDnicoF-0


@extend_schema(
    summary="Проверяет прохождение вопроса c одним правильным ответом.",
    tags=["Вопросы и инфо-слайд"],
    description="""Помимо этого создаёт результат прохождения пользователем вопроса.""",
    request=QuestionTextSerializer(),
    responses={201: SingleCorrectPostSerializer},
)
class SingleCorrectPost(generics.CreateAPIView):
    serializer_class = SingleCorrectPostSerializer
    permission_classes = [CheckQuestionTypePermission]
    expected_question_model = QuestionSingleAnswer

    def create(self, request, *args, **kwargs) -> Response:
        try:
            # profile_id = UserProfile.objects.get(user_id=self.request.user.id).id
            profile_id = UserProfile.objects.get(user_id=1).id

            question_answers: QuerySet[AnswerSingle] = self.request_question.single_answers.all()
            given_answer: AnswerSingle = question_answers.get(id=request.data.get("answer_id"))
            is_correct_answer: bool = given_answer.is_correct
            data = {"is_correct": is_correct_answer}

            if is_correct_answer:
                create_user_result(self.task_object_id, profile_id, TypeQuestionPoints.QUESTION_SINGLE_ANSWER)
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
    request=serializers.ListSerializer(child=ConnectAnswerSerializer()),
    responses={201: ConnectQuestionPostResponseSerializer},
)
class ConnectQuestionPost(generics.CreateAPIView):
    serializer_class = ConnectQuestionPostResponseSerializer
    permission_classes = [CheckQuestionTypePermission]
    expected_question_model = QuestionConnect

    def create(self, request, *args, **kwargs) -> Response:
        try:
            user_answers = request.data
            # profile_id = UserProfile.objects.get(user_id=self.request.user.id).id
            profile_id = UserProfile.objects.get(user_id=1).id
            question: QuestionConnect = self.request_question
            all_answer_options: QuerySet[AnswerConnect] = question.connect_answers.all()
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
                create_user_result(self.task_object_id, profile_id, TypeQuestionPoints.QUESTION_CONNECT)
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
    request=serializers.ListSerializer(child=serializers.IntegerField()),
    responses={
        200: CustomTextSucessSerializer,
        204: CustomTextSerializer,
        400: serializers.ListSerializer(child=serializers.IntegerField()),
    },
)
class QuestionExcludePost(generics.CreateAPIView):
    serializer_class = SimpleNumberListSerializer
    permission_classes = [CheckQuestionTypePermission]
    expected_question_model = QuestionSingleAnswer

    def create(self, request, *args, **kwargs) -> Response:
        try:
            # profile_id = UserProfile.objects.get(user_id=self.request.user.id).id
            profile_id = UserProfile.objects.get(user_id=1).id
            given_answer_ids: list[int] = request.data
            answers_of_question: QuerySet[AnswerSingle] = self.request_question.single_answers.all()
            given_answers: QuerySet[AnswerSingle] = answers_of_question.filter(id__in=given_answer_ids)
            quantity_needed_answers: int = answers_of_question.filter(is_correct=False).count()
            data = given_answers.filter(id__in=given_answer_ids, is_correct=True).values_list("id", flat=True)

            if len(data):
                return Response({"is_correct": False, "wrong_answers": data}, status=status.HTTP_400_BAD_REQUEST)
            elif quantity_needed_answers != given_answers.count():
                return Response({"text": "need more..."}, status=status.HTTP_400_BAD_REQUEST)
            else:
                create_user_result(self.task_object_id, profile_id, TypeQuestionPoints.QUESTION_EXCLUDE)
                return Response({"text": "success"}, status=status.HTTP_201_CREATED)
        except UserAlreadyAnsweredException as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# POST ответить на вопрос для текста


@extend_schema(
    summary="Сохранение ответа пользователя на ответ, требующий ввод текста",
    tags=["Вопросы и инфо-слайд"],
    request=WriteAnswerTextSerializer(),
    responses={
        200: WriteAnswerSerializer,
        201: WriteAnswerSerializer,
        400: {"error": "You can't save an empty answer!"},
    },
)
class QuestionWritePost(generics.CreateAPIView):
    serializer_class = WriteAnswerSerializer
    permission_classes = [SimpleCheckQuestionTypePermission]
    expected_question_model = QuestionWrite

    def create(self, request, *args, **kwargs) -> Response:
        try:
            # profile_id = UserProfile.objects.get(user_id=self.request.user.id).id
            profile_id = 1

            user_answer: str = request.data["text"]
            if len(user_answer):
                create_user_result(self.task_object_id, profile_id, TypeQuestionPoints.QUESTION_WRITE)
                # serializer = self.serializer_class(query)
                return Response({"text": "success"}, status=status.HTTP_201_CREATED)

            return Response({"error": "You can't save an empty answer!"}, status=status.HTTP_400_BAD_REQUEST)
        except UserAlreadyAnsweredException as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    summary="Пометить InfoSlide как сделанный",
    tags=["Вопросы и инфо-слайд"],
)
class InfoSlidePost(generics.CreateAPIView):
    permission_classes = [SimpleCheckQuestionTypePermission]
    expected_question_model = InfoSlide

    def create(self, request, *args, **kwargs) -> Response:
        try:
            user_profile_id = 1
            create_user_result(self.task_object_id, user_profile_id, TypeQuestionPoints.INFO_SLIDE)
            return Response("successful", status=status.HTTP_204_NO_CONTENT)
        except UserAlreadyAnsweredException as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
