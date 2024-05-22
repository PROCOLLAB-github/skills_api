import random
from dataclasses import asdict

from django.db.models import QuerySet
from drf_spectacular.utils import extend_schema

from rest_framework import generics, status
from rest_framework.response import Response

from procollab_skills.permissions import AuthCheck
from questions.mapping import TypeQuestionPoints
from questions.serializers import (
    SingleQuestionAnswerSerializer,
    ConnectQuestionSerializer,
    WriteQuestionSerializer,
)
from progress.services import check_if_answered_get

from questions.models import (
    QuestionSingleAnswer,
    QuestionConnect,
    QuestionWrite,
    AnswerConnect,
    InfoSlide,
)
from questions.serializers import InfoSlideSerializer
from questions.permissions import CheckQuestionTypePermission
from questions.typing import (
    QuestionSerializerData,
    SingleAnswerData,
    QuestionWriteSerializerData,
    AnswerUserWriteData,
    QuestionСonnectSerializerData,
    SingleConnectedAnswerData,
)


class QuestionSingleAnswerGet(generics.ListAPIView):
    serializer_class = SingleQuestionAnswerSerializer
    permission_classes = [AuthCheck, CheckQuestionTypePermission]
    expected_question_model = QuestionSingleAnswer

    @extend_schema(
        summary="Выводит данные для трёх видов вопросов (см. описание)",
        tags=["Вопросы и инфо-слайд"],
        description="""для: вопроса с одним правильным ответом, вопроса на исключение,
         вопроса на выбор нескольких правильных
        ответов (возможно пока его нет, но в будущем может появится).""",
    )
    def get(self, request, *args, **kwargs) -> Response:
        question: QuestionSingleAnswer = self.request_question
        all_answers = question.single_answers.all()
        answers = [SingleAnswerData(id=answer.id, text=answer.text) for answer in all_answers]

        user_result = check_if_answered_get(
            self.task_object_id, self.profile_id, TypeQuestionPoints.QUESTION_SINGLE_ANSWER
        )
        correct_answer = [
            SingleAnswerData(id=all_answers.get(is_correct=True).id, text=all_answers.get(is_correct=True).text)
        ]
        random.shuffle(answers)

        serializer = self.serializer_class(
            QuestionSerializerData(
                id=self.task_object_id,
                question_text=question.text,
                description=question.description,
                files=[file.link for file in question.files.all()],
                answers=correct_answer if user_result else answers,
                is_answered=True if user_result else False,
            )
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class QuestionConnectGet(generics.ListAPIView):
    serializer_class = ConnectQuestionSerializer
    permission_classes = [AuthCheck, CheckQuestionTypePermission]
    expected_question_model = QuestionConnect

    @extend_schema(
        summary="Получить данные для вопроса на соотношение",
        tags=["Вопросы и инфо-слайд"],
    )
    def get(self, request, *args, **kwargs):
        question: QuestionConnect = self.request_question
        all_connect_answers: QuerySet[AnswerConnect] = question.connect_answers.all()

        target_left = [
            SingleConnectedAnswerData(id=answer.id, text=answer.connect_left)
            if answer.connect_left
            else SingleConnectedAnswerData(id=answer.id, file=answer.file_left.link)
            for answer in all_connect_answers
        ]
        target_right = [
            SingleConnectedAnswerData(id=answer.id, text=answer.connect_right)
            if answer.connect_right
            else SingleConnectedAnswerData(id=answer.id, file=answer.file_right.link)
            for answer in all_connect_answers
        ]

        # TODO переписать с датаклассами

        question_data = QuestionСonnectSerializerData(
            id=question.id,
            text=question.text,
            description=question.description,
            files=[file.link for file in question.files.all()],
            connect_left=target_left,
            connect_right=target_right,
        )
        if check_if_answered_get(self.task_object_id, self.profile_id, TypeQuestionPoints.QUESTION_CONNECT):
            question_data.is_answered = True
        else:
            random.shuffle(target_right)
            random.shuffle(target_left)

        serializer = self.serializer_class(question_data)
        return Response(serializer.data, status=status.HTTP_200_OK)


class QuestionExcludeAnswerGet(generics.ListAPIView):
    serializer_class = SingleQuestionAnswerSerializer
    permission_classes = [AuthCheck, CheckQuestionTypePermission]
    expected_question_model = QuestionSingleAnswer

    @extend_schema(
        summary="Выводит данные для трёх видов вопросов (см. описание)",
        tags=["Вопросы и инфо-слайд"],
        description="""для: вопроса с одним правильным ответом, вопроса на исключение, 
        вопроса на выбор нескольких правильных
        ответов (возможно пока его нет, но в будущем может появится).""",
    )
    def get(self, request, *args, **kwargs):
        question: QuestionSingleAnswer = self.request_question

        all_answers = question.single_answers.all()
        answers = [SingleAnswerData(id=answer.id, text=answer.text) for answer in all_answers]
        answers_to_exclude = [
            SingleAnswerData(id=answer.id, text=answer.text) for answer in all_answers if answer.is_correct
        ]

        data_to_serialize = QuestionSerializerData(
            id=self.task_object_id,
            question_text=question.text,
            description=question.description,
            files=[file.link for file in question.files.all()],
            answers=answers,
        )
        if check_if_answered_get(self.task_object_id, self.profile_id, TypeQuestionPoints.QUESTION_EXCLUDE):
            data_to_serialize.is_answered = True
            data_to_serialize.answers = answers_to_exclude

        random.shuffle(answers)

        serializer = self.serializer_class(data_to_serialize)
        return Response(serializer.data, status=status.HTTP_200_OK)


class InfoSlideDetails(generics.ListAPIView):
    serializer_class = InfoSlideSerializer
    permission_classes = [AuthCheck, CheckQuestionTypePermission]
    expected_question_model = InfoSlide

    @extend_schema(
        summary="Выводит информацию для информационного слайда",
        tags=["Вопросы и инфо-слайд"],
    )
    def get(self, request, *args, **kwargs):
        info_slide: InfoSlide = self.request_question

        serializer = self.serializer_class(
            data={
                "text": info_slide.text,
                "files": [file.link for file in info_slide.files.all()],
                "is_done": bool(
                    check_if_answered_get(self.task_object_id, self.profile_id, TypeQuestionPoints.INFO_SLIDE)
                ),
            }
        )
        if serializer.is_valid():
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


# GET вопрос для текста
class QuestionWriteAnswer(generics.ListAPIView):
    serializer_class = WriteQuestionSerializer
    permission_classes = [AuthCheck, CheckQuestionTypePermission]
    expected_question_model = QuestionWrite

    @extend_schema(
        summary="Выводит информацию для слайда с вопросом, для которого надо будет написать ответ",
        tags=["Вопросы и инфо-слайд"],
    )
    def get(self, request, *args, **kwargs):
        question: QuestionWrite = self.request_question

        write_question = QuestionWriteSerializerData(
            id=question.id,
            text=question.text,
            description=question.description,
            files=[file.link for file in question.files.all()],
        )

        if user_answer := check_if_answered_get(
            self.task_object_id, self.profile_id, TypeQuestionPoints.QUESTION_WRITE
        ):
            write_question.answer = AnswerUserWriteData(id=user_answer.id, text=user_answer.text)

        return Response(asdict(write_question), status=status.HTTP_200_OK)
