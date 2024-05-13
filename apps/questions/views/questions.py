import random
from dataclasses import asdict

from django.db.models import QuerySet
from drf_spectacular.utils import extend_schema
from rest_framework import generics, status
from rest_framework.response import Response

from courses.mapping import ModelNameEnum
from courses.models import TaskObject
from progress.models import UserProfile
from questions.mapping import TypeQuestionPoints
from questions.serializers import (
    SingleQuestionAnswerSerializer,
    ConnectQuestionSerializer,
    WriteQuestionSerializer,
)
from progress.services import check_if_answered_get

from questions.models import (
    QuestionSingleAnswer,
    AnswerConnect,
    InfoSlide,
)

# TODO сделать, чтобы если юзер прошёл задание идеально правильно ранее (есть сохраненный результат),
#  то выводился ещё и он,
# а не только вопрос
# https://www.figma.com/file/cZKZgA3ZywZykhZuHn1OQk/ProCollab?type=design&node-id=377-634&mode=design&t=Pxo1vEpfsWDnicoF-0
from questions.serializers import InfoSlideSerializer
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
        answers = [SingleAnswerData(id=answer.id, text=answer.text) for answer in all_answers]

        user_result = check_if_answered_get(task_object_id, profile_id, TypeQuestionPoints.QUESTION_SINGLE_ANSWER)
        correct_answer = [
            SingleAnswerData(id=all_answers.get(is_correct=True).id, text=all_answers.get(is_correct=True).text)
        ]
        random.shuffle(answers)

        serializer = self.serializer_class(
            QuestionSerializerData(
                id=needed_task_object.id,
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
        if check_if_answered_get(task_object_id, profile_id, TypeQuestionPoints.QUESTION_CONNECT):
            question_data.is_answered = True
        else:
            random.shuffle(target_right)
            random.shuffle(target_left)

        serializer = self.serializer_class(question_data)
        return Response(serializer.data, status=status.HTTP_200_OK)


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
        answers = [SingleAnswerData(id=answer.id, text=answer.text) for answer in all_answers]
        answers_to_exclude = [
            SingleAnswerData(id=answer.id, text=answer.text) for answer in all_answers if answer.is_correct
        ]

        data_to_serialize = QuestionSerializerData(
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
                "is_done": bool(check_if_answered_get(task_object_id, user_profile_id, TypeQuestionPoints.INFO_SLIDE)),
            }
        )
        if serializer.is_valid():
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


# GET вопрос для текста
class QuestionWriteAnswer(generics.ListAPIView):
    serializer_class = WriteQuestionSerializer

    @extend_schema(
        summary="Выводит информацию для слайда с вопросом, для которого надо будет написать ответ",
        tags=["Вопросы и инфо-слайд"],
    )
    def get(self, request, *args, **kwargs):
        task_object_id = self.kwargs.get("task_obj_id")
        user_profile_id = 1

        question = TaskObject.objects.prefetch_related("content_object").get(id=task_object_id).content_object
        write_question = QuestionWriteSerializerData(
            id=question.id,
            text=question.text,
            description=question.description,
            files=[file.link for file in question.files.all()],
        )

        if user_answer := check_if_answered_get(task_object_id, user_profile_id, TypeQuestionPoints.QUESTION_WRITE):
            write_question.answer = AnswerUserWriteData(id=user_answer.id, text=user_answer.text)

        return Response(asdict(write_question), status=status.HTTP_200_OK)
