import random

from django.db.models import QuerySet
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import generics, status, serializers
from rest_framework.response import Response

from courses.mapping import ModelNameEnum
from courses.models import TaskObject
from progress.models import UserProfile, TaskObjUserResult
from .mapping import TypeQuestionPoints
from .serializers import (
    SingleQuestionAnswerSerializer,
    SingleCorrectPostSerializer,
    ConnectQuestionSerializer,
    ConnectQuestionPostResponseSerializer,
    SimpleNumberListSerializer,
    ConnectAnswerSerializer,
    CustomTextSucessSerializer,
    CustomTextSerializer,
)
from progress.services import (
    create_user_result,
    check_if_answered_get,
)
from .models import (
    QuestionSingleAnswer,
    SingleAnswer,
    ConnectAnswer,
    InfoSlide,
)

# TODO сделать, чтобы если юзер прошёл задание идеально правильно ранее (есть сохраненный результат),
#  то выводился ещё и он,
# а не только вопрос
# https://www.figma.com/file/cZKZgA3ZywZykhZuHn1OQk/ProCollab?type=design&node-id=377-634&mode=design&t=Pxo1vEpfsWDnicoF-0
from .serializers import InfoSlideSerializer
from .typing import QuestionExcludeSerializerData, SingleAnswerData


class QuestionSingleAnswerGet(generics.ListAPIView):
    serializer_class = SingleQuestionAnswerSerializer

    @extend_schema(
        summary="Выводит данные для трёх видов вопросов (см. описание)",
        tags=["Вопросы и инфо-слайд"],
        description="""для: вопроса с одним правильным ответом, вопроса на исключение,
         вопроса на выбор нескольких правильных
        ответов (возможно пока его нет, но в будущем может появится).""",
    )
    def get(self, request, *args, **kwargs) -> Response:
        task_object_id = self.kwargs.get("task_obj_id")
        # profile_id = UserProfile.objects.get(user_id=self.request.user.id).id
        profile_id = UserProfile.objects.get(user_id=1).id

        needed_task_object = TaskObject.objects.prefetch_related(
            "content_object",
            "content_object__single_answers",
            "content_object__files",
        ).get(id=task_object_id)

        question: QuestionSingleAnswer = needed_task_object.content_object

        all_answers = question.single_answers.all()
        answers = [{"id": answer.id, "answer_text": answer.text} for answer in all_answers]

        user_result = check_if_answered_get(task_object_id, profile_id, TypeQuestionPoints.QUESTION_SINGLE_ANSWER)
        correct_answer = [
            {"id": all_answers.get(is_correct=True).id, "answer_text": all_answers.get(is_correct=True).text}
        ]
        random.shuffle(answers)

        serializer = self.serializer_class(
            data={
                "id": needed_task_object.id,
                "question_text": question.text,
                "description": question.description,
                "files": [file.link for file in question.files.all()],
                "is_answered": True if user_result else False,
                "answers": correct_answer if user_result else answers,
            }
        )
        if serializer.is_valid():
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


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

        given_answer = SingleAnswer.objects.select_related("question").get(id=self.kwargs.get("answer_id"))
        serializer_context = {"given_answer": given_answer}
        if not given_answer.is_correct:
            correct_answer = SingleAnswer.objects.filter(question=given_answer.question, is_correct=True).first()
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


class QuestionConnectGet(generics.ListAPIView):
    serializer_class = ConnectQuestionSerializer

    @extend_schema(
        summary="Получить данные для вопроса на соотношение",
        tags=["Вопросы и инфо-слайд"],
    )
    def get(self, request, *args, **kwargs):
        task_object_id = self.kwargs.get("task_obj_id")
        # profile_id = UserProfile.objects.get(user_id=self.request.user.id).id
        profile_id = UserProfile.objects.get(user_id=1).id
        # TODO добавить возможность размещения файлов вместо текста справа. сделать тип вопроса

        needed_task_object = TaskObject.objects.prefetch_related(
            "content_object",
            "content_object__connect_answers",
            "content_object__files",
        ).get(id=task_object_id)

        question = needed_task_object.content_object

        all_connect_answers: QuerySet[ConnectAnswer] = question.connect_answers.all()

        connect_right = [{"string": answer.connect_right} for answer in all_connect_answers]
        connect_left = [{"id": answer.id, "answer_text": answer.connect_left} for answer in all_connect_answers]
        # TODO переписать с датаклассами
        if check_if_answered_get(task_object_id, profile_id, TypeQuestionPoints.QUESTION_CONNECT):
            serializer = self.serializer_class(
                data={
                    "id": question.id,
                    "question_text": question.text,
                    "description": question.description,
                    "files": [file.link for file in question.files.all()],
                    "connect_left": connect_left,
                    "connect_right": connect_right,
                    "is_answered": True,
                }
            )
            serializer.is_valid()
            return Response(serializer.data, status=status.HTTP_200_OK)

        random.shuffle(connect_right)

        random.shuffle(connect_left)

        serializer = self.serializer_class(
            data={
                "id": question.id,
                "question_text": question.text,
                "description": question.description,
                "files": [file.link for file in question.files.all()],
                "connect_left": connect_left,
                "connect_right": connect_right,
            }
        )
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


class QuestionExcludeAnswerGet(generics.ListAPIView):
    serializer_class = SingleQuestionAnswerSerializer

    @extend_schema(
        summary="Выводит данные для трёх видов вопросов (см. описание)",
        tags=["Вопросы и инфо-слайд"],
        description="""для: вопроса с одним правильным ответом, вопроса на исключение, 
        вопроса на выбор нескольких правильных
        ответов (возможно пока его нет, но в будущем может появится).""",
    )
    def get(self, request, *args, **kwargs):
        task_object_id = self.kwargs.get("task_obj_id")
        # profile_id = UserProfile.objects.get(user_id=self.request.user.id).id
        profile_id = UserProfile.objects.get(user_id=1).id

        needed_task_object = TaskObject.objects.prefetch_related(
            "content_object",
            "content_object__single_answers",
            "content_object__files",
        ).get(id=task_object_id)
        if not isinstance(question := needed_task_object.content_object, QuestionSingleAnswer):
            return Response(
                {
                    "error": f"""
                    You tried to summon taskobject with a wrong endpoint. 
                    Instead of using {question._meta.model_name} endpoint, 
                    try using {ModelNameEnum.QUESTION_EXCLUDE.value} endpoint
                    """
                }
            )
        if not question.is_exclude:
            return Response(
                {"error": "You tried to summon question_single_answer question with question_exclude endpoint"}
            )

        all_answers = question.single_answers.all()
        answers = [SingleAnswerData(id=answer.id, answer_text=answer.text) for answer in all_answers]
        answers_to_exclude = [
            SingleAnswerData(id=answer.id, answer_text=answer.text) for answer in all_answers if answer.is_correct
        ]

        data_to_serialize = QuestionExcludeSerializerData(
            id=needed_task_object.id,
            question_text=question.text,
            description=question.description,
            files=[file.link for file in question.files.all()],
            answers=answers,
        )
        if check_if_answered_get(task_object_id, profile_id, TypeQuestionPoints.QUESTION_EXCLUDE):
            data_to_serialize.is_answered = True
            data_to_serialize.answers = answers_to_exclude

        random.shuffle(answers)

        serializer = self.serializer_class(data_to_serialize)
        return Response(serializer.data, status=status.HTTP_200_OK)


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
        answers_of_question = SingleAnswer.objects.filter(question=task_obj.content_object)

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


class InfoSlideDetails(generics.ListAPIView):
    serializer_class = InfoSlideSerializer

    @extend_schema(
        summary="Выводит информацию для информационного слайда",
        tags=["Вопросы и инфо-слайд"],
    )
    def get(self, request, *args, **kwargs):
        task_object_id = self.kwargs.get("task_obj_id")
        user_profile_id = 1

        needed_task_object = TaskObject.objects.prefetch_related("content_object").get(id=task_object_id)

        info_slide: InfoSlide = needed_task_object.content_object
        serializer = self.serializer_class(
            data={
                "text": info_slide.text,
                "files": [file.link for file in info_slide.files.all()],
            }
        )
        if serializer.is_valid():
            TaskObjUserResult.objects.get_or_create(
                task_object_id=task_object_id,
                user_profile_id=user_profile_id,
                points_gained=TypeQuestionPoints.INFO_SLIDE.value,
            )
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


# GET вопрос для текста
# POST ответить на вопрос для текста
