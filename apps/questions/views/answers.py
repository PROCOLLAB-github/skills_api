from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import generics, status, serializers
from rest_framework.response import Response

from courses.models import TaskObject

from progress.models import UserProfile
from progress.services import create_user_result

from questions.mapping import TypeQuestionPoints
from questions.serializers import (
    SingleCorrectPostSerializer,
    ConnectQuestionPostResponseSerializer,
    SimpleNumberListSerializer,
    ConnectAnswerSerializer,
    CustomTextSucessSerializer,
    CustomTextSerializer,
)
from questions.models import AnswerSingle

# TODO сделать, чтобы если юзер прошёл задание идеально правильно ранее (есть сохраненный результат),
#  то выводился ещё и он,
# а не только вопрос
# https://www.figma.com/file/cZKZgA3ZywZykhZuHn1OQk/ProCollab?type=design&node-id=377-634&mode=design&t=Pxo1vEpfsWDnicoF-0


@extend_schema(
    summary="Проверяет прохождение вопроса c одним правильным ответов. ",
    tags=["Вопросы и инфо-слайд"],
    description="""Помимо этого создаёт результат прохождения пользователем вопроса.""",
    request=None,
    responses={201: SingleCorrectPostSerializer},
    parameters=[
        OpenApiParameter(name="task_obj_id", required=True, type=int),
    ],
)
class SingleCorrectPost(generics.CreateAPIView):
    serializer_class = SingleCorrectPostSerializer

    def create(self, request, *args, **kwargs) -> Response:
        task_obj_id = self.request.query_params.get("task_obj_id")
        # profile_id = UserProfile.objects.get(user_id=self.request.user.id).id
        profile_id = UserProfile.objects.get(user_id=1).id

        given_answer = AnswerSingle.objects.select_related("question").get(id=self.kwargs.get("answer_id"))
        serializer_context = {"given_answer": given_answer}
        if not given_answer.is_correct:
            correct_answer = AnswerSingle.objects.filter(question=given_answer.question, is_correct=True).first()
            serializer_context["correct_answer"] = correct_answer
        else:
            create_user_result(task_obj_id, profile_id, TypeQuestionPoints.QUESTION_SINGLE_ANSWER)

        data = {"is_correct": serializer_context["given_answer"].is_correct}
        if not data["is_correct"]:
            data["correct_answer"] = serializer_context["correct_answer"].id

        serializer = self.serializer_class(data=data)
        if serializer.is_valid():
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    summary="Проверить вопрос на соотношение",
    tags=["Вопросы и инфо-слайд"],
    request=ConnectAnswerSerializer,
    responses={201: ConnectQuestionPostResponseSerializer},
)
class ConnectQuestionPost(generics.CreateAPIView):
    serializer_class = ConnectQuestionPostResponseSerializer

    def create(self, request, *args, **kwargs):
        task_obj_id = self.kwargs.get("task_obj_id")
        user_answers = request.data
        # profile_id = UserProfile.objects.get(user_id=self.request.user.id).id
        profile_id = UserProfile.objects.get(user_id=1).id

        question = TaskObject.objects.prefetch_related("content_object__connect_answers").get(id=task_obj_id)

        all_answer_options = question.content_object.connect_answers.all()

        scored_answers = []
        for user_answer in user_answers:
            check_answer = all_answer_options.get(id=user_answer["left_id"])
            user_answer["is_correct"] = check_answer.connect_right == user_answer["right_text"]
            scored_answers.append(user_answer)

        if not sum(1 for user_answer in user_answers if user_answer["is_correct"] is False):
            create_user_result(task_obj_id, profile_id, TypeQuestionPoints.QUESTION_CONNECT)

        serializer = self.serializer_class(data=scored_answers)

        if serializer.is_valid():
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


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

    def create(self, request, *args, **kwargs):
        task_obj_id = self.kwargs.get("task_obj_id")
        # profile_id = UserProfile.objects.get(user_id=self.request.user.id).id
        profile_id = UserProfile.objects.get(user_id=1).id
        given_answer_ids = request.data

        task_obj = TaskObject.objects.prefetch_related("content_object").get(id=task_obj_id)
        answers_of_question = AnswerSingle.objects.filter(question=task_obj.content_object)

        given_answers = answers_of_question.filter(id__in=given_answer_ids)
        quantity_needed_answers = answers_of_question.filter(is_correct=False).count()
        data = given_answers.filter(id__in=given_answer_ids, is_correct=True).values_list("id", flat=True)

        if len(data):
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
        elif quantity_needed_answers != given_answers.count():
            return Response({"text": "need more..."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            create_user_result(task_obj_id, profile_id, TypeQuestionPoints.QUESTION_EXCLUDE)
            return Response({"text": "success"}, status=status.HTTP_201_CREATED)


# POST ответить на вопрос для текста
