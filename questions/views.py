from django.db.models import QuerySet
from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework import generics, status, serializers

from .models import (
    QuestionSingleAnswer,
    SingleAnswer,
    QuestionConnect,
    ConnectAnswer, InfoSlide,
)
from courses.models import TaskObject
from courses.serializers import (
    SingleQuestionAnswerSerializer,
    SingleCorrectPostSerializer,
    ConnectQuestionSerializer,
    ConnectQuestionPostResponseSerializer,
    SimpleNumberListSerializer,
    ConnectAnswerSerializer,
    CustomTextSucessSerializer,
    CustomTextSerializer,
)

import random


# TODO сделать, чтобы если юзер прошёл задание идеально правильно ранее (есть сохраненный результат), то выводился ещё и он,
# а не только вопросhttps://www.figma.com/file/cZKZgA3ZywZykhZuHn1OQk/ProCollab?type=design&node-id=377-634&mode=design&t=Pxo1vEpfsWDnicoF-0
from .serializers import InfoSlideSerializer


class QuestionSingleAnswerGet(generics.ListAPIView):
    serializer_class = SingleQuestionAnswerSerializer

    @extend_schema(
        summary="Выводит данные для трёх видов вопросов (см. описание)",
        tags=["Вопросы и инфо-слайд"],
        description="""для: вопроса с одним правильным ответом, вопроса на исключение, вопроса на выбор нескольких правильных
        ответов (возможно пока его нет, но в будущем может появится).""",
    )
    def get(self, request, *args, **kwargs):
        task_object_id = self.kwargs.get("question_single_answer_id")

        needed_task_object = TaskObject.objects.prefetch_related(
            "content_object",
            "content_object__single_answers",
            "content_object__files",
        ).get(id=task_object_id)

        question: QuestionSingleAnswer = needed_task_object.content_object

        answers = [
            {"id": answer.id, "answer_text": answer.text}
            for answer in question.single_answers.all()
        ]
        random.shuffle(answers)

        serializer = self.serializer_class(
            data={
                "question_text": question.text,
                "description": question.description,
                "files": [file.link for file in question.files.all()],
                "answers": answers,
            }
        )
        if serializer.is_valid():
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(
                {"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
            )


@extend_schema(
    summary="Проверяет прохождение вопроса c одним правильным ответов",
    tags=["Вопросы и инфо-слайд"],
    description="""Помимо этого создаёт результат прохождения пользователем вопроса.""",
    request=None,
    responses={201: SingleCorrectPostSerializer}
)
class SingleCorrectPost(generics.CreateAPIView):
    serializer_class = SingleCorrectPostSerializer

    def create(self, request, *args, **kwargs):
        given_answer = SingleAnswer.objects.select_related("question").get(
            id=self.kwargs.get("answer_id")
        )
        serializer_context = {"given_answer": given_answer}
        if not given_answer.is_correct:
            correct_answer = SingleAnswer.objects.filter(
                question=given_answer.question, is_correct=True
            ).first()
            serializer_context["correct_answer"] = correct_answer

        # TODO добавить сохранение результата

        data = {"is_correct": serializer_context["given_answer"].is_correct}
        if not data["is_correct"]:
            data["correct_answer"] = serializer_context["correct_answer"].id

        serializer = self.serializer_class(data=data)
        if serializer.is_valid():
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(
                {"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
            )


class QuestionConnectGet(generics.ListAPIView):
    serializer_class = ConnectQuestionSerializer

    @extend_schema(
        summary="Получить данные для вопроса на соотношение",
        tags=["Вопросы и инфо-слайд"],
    )
    def get(self, request, *args, **kwargs):
        task_object_id = self.kwargs.get("question_connection_id")
        # TODO добавить возможность размещения файлов вместо текста справа. сделать тип вопроса
        needed_task_object = TaskObject.objects.prefetch_related(
            "content_object",
            "content_object__connect_answers",
            "content_object__files",
        ).get(id=task_object_id)

        question: QuestionConnect = needed_task_object.content_object

        all_connect_answers: QuerySet[ConnectAnswer] = question.connect_answers.all()
        connect_right = [
            {"string": answer.connect_right} for answer in all_connect_answers
        ]
        random.shuffle(connect_right)
        connect_left = [
            {"id": answer.id, "answer_text": answer.connect_left}
            for answer in all_connect_answers
        ]
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
            return Response(
                {"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
            )



@extend_schema(
    summary="Проверить вопрос на соотношение",
    tags=["Вопросы и инфо-слайд"],
    request=ConnectAnswerSerializer(many=True),
    responses={201: ConnectQuestionPostResponseSerializer}
)
class ConnectQuestionPost(generics.CreateAPIView):
    serializer_class = ConnectQuestionPostResponseSerializer

    def create(self, request, *args, **kwargs):
        question_id = self.kwargs.get("question_connection_id")
        user_answers = request.data

        question = QuestionConnect.objects.prefetch_related("connect_answers").get(
            id=question_id
        )

        all_answer_options = question.connect_answers.all()

        scored_answers = []
        for user_answer in user_answers:
            check_answer = all_answer_options.get(id=user_answer["left_id"])
            user_answer["is_correct"] = (
                    check_answer.connect_right == user_answer["right_text"]
            )
            scored_answers.append(user_answer)

        serializer = self.serializer_class(data={"answer": scored_answers})

        if serializer.is_valid():
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(
                {"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
            )


# GET вопроса на исключение
# request: /courses/exclude/{question_id}
# response:
i = {
    "question_text": str,
    "question_description": str or None,
    "options": [{"id": int, "text": str}],
}


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
    }
)
class QuestionExcludePost(generics.CreateAPIView):
    serializer_class = SimpleNumberListSerializer

    def create(self, request, *args, **kwargs):
        question_id = self.kwargs.get("exclude_question_id")
        given_answer_ids = request.data

        answers_of_question = SingleAnswer.objects.filter(question__id=question_id)
        given_answers = answers_of_question.filter(id__in=given_answer_ids)
        quantity_needed_answers = answers_of_question.filter(is_correct=False).count()
        data = given_answers.filter(
            id__in=given_answer_ids, is_correct=True
        ).values_list("id", flat=True)

        if len(data):
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
        elif quantity_needed_answers != given_answers.count():
            return Response({"text": "need more..."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"text": "success"}, status=status.HTTP_201_CREATED)




class InfoSlideDetails(generics.ListAPIView):
    serializer_class = InfoSlideSerializer

    @extend_schema(
        summary="Выводит информацию для информационного слайда",
        tags=["Навыки и задачи"],
    )
    def get(self, request, *args, **kwargs):
        task_object_id = self.kwargs.get("infoslide_id")

        needed_task_object = TaskObject.objects.prefetch_related("content_object").get(
            id=task_object_id
        )

        info_slide: InfoSlide = needed_task_object.content_object
        serializer = self.serializer_class(
            data={
                "text": info_slide.text,
                "files": [file.link for file in info_slide.files.all()],
            }
        )
        if serializer.is_valid():
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(
                {"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
            )