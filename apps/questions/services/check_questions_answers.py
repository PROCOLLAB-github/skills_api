from abc import ABC, abstractmethod
from copy import deepcopy
from typing import Any, Iterable, Optional, Union

from django.db import transaction
from django.db.models import QuerySet
from rest_framework import status

from courses.models import TaskObject
from progress.models import TaskObjUserResult, UserAnswersAttemptCounter
from questions.exceptions import (QustionConnectException,
                                  UserAlreadyAnsweredException)
from questions.mapping import TypeQuestionPoints
from questions.models.answers import AnswerConnect, AnswerSingle
from questions.models.questions import (InfoSlide, QuestionConnect,
                                        QuestionSingleAnswer, QuestionWrite)


class AbstractAnswersService(ABC):
    _WRONG_ANSWER_WO_VALIDATION = {
        "detail": "need more...",
        "is_correct": False,
    }
    _SUCCESS_RESPONSE_BODY: dict = {"is_correct": True}
    _UNSUCCESS_RESPONSE_BODY: dict = {"is_correct": False}

    def __init__(
        self,
        request_profile_id: int,
        request_question: Union[InfoSlide, QuestionWrite, QuestionConnect, QuestionSingleAnswer],
        request_task_object: TaskObject,
        request_data: dict,
    ) -> None:
        self.request_profile_id = request_profile_id
        self.request_question = request_question
        self.request_task_object = request_task_object
        self.request_data = request_data

    @transaction.atomic
    def create_answer(self) -> tuple[dict[str, Any], int]:
        """
        Основной энетрипоинт в интерфейс.
        Ожидаемый результат:
            - body для response: dict
            - status для response: int
        """
        # Проверка, что ответ еще не давался:
        existing_task_obj_result = TaskObjUserResult.objects.filter(
            task_object=self.request_task_object,
            user_profile_id=self.request_profile_id,
        )
        if existing_task_obj_result.exists():
            raise UserAlreadyAnsweredException()

        # Для вопросов без проверки ответа(`validate_answer`):
        if not self.request_task_object.validate_answer:
            return self._handle_no_question_validation(point_type=self._QUSTION_POINTS)

        return self._check_correct_answer()

    @abstractmethod
    def _check_correct_answer(self) -> tuple[dict[str, Any], int]:
        """Проверка на корректность ответа + формирование процесса с `couter` (если это предполагается)."""
        raise NotImplementedError

    @abstractmethod
    def _create_answer_response_body(self) -> dict[str, Any]:
        raise NotImplementedError

    def _process_answer_attempt_counter(self, question_answers: Any):
        """
        Если у вопроса указан `attempts_before_hint` формируется counter по ответам.
        После `attempts_before_hint` max значения в reponse появляется подсказка.
        После `attempts_after_hint` max значения, ответ принимается без баллов, response с ответом.
        """
        counter = UserAnswersAttemptCounter.objects.filter(
            user_profile_id=self.request_profile_id,
            task_object=self.request_task_object,
        ).first()

        if not counter:
            counter = UserAnswersAttemptCounter.objects.create(
                user_profile_id=self.request_profile_id,
                task_object=self.request_task_object,
            )
        else:
            if counter.is_take_hint:
                counter.attempts_made_after += 1
            else:
                counter.attempts_made_before += 1

        # Проверка после подсказки, если counter `after` max, то сохранение без баллов:
        if counter.is_take_hint and counter.attempts_made_after >= self.request_question.attempts_after_hint:
            counter.delete()
            self._create_tast_obj_result(TypeQuestionPoints.QUESTION_WO_POINTS, correct_answer=False)
            question_answer_body = self._create_answer_response_body(question_answers)
            question_answer_body["hint"] = self.request_question.hint_text
            return question_answer_body, status.HTTP_201_CREATED

        # Проверка до подсказки:
        #   - если counter `before` max, то в response будет подсказка.
        #   - если `after` нет, то засчитывается неверный ответ.
        if counter.attempts_made_before >= self.request_question.attempts_before_hint:
            counter.is_take_hint = True
            counter.save()
            response_body = deepcopy(self._UNSUCCESS_RESPONSE_BODY)

            if self.request_question.attempts_after_hint and self.request_question.hint_text:
                response_body["hint"] = self.request_question.hint_text
                return response_body, status.HTTP_400_BAD_REQUEST
            else:
                counter.delete()
                self._create_tast_obj_result(TypeQuestionPoints.QUESTION_WO_POINTS, correct_answer=False)
                question_answer_body = self._create_answer_response_body(question_answers)
                if self.request_question.hint_text:
                    question_answer_body["hint"] = self.request_question.hint_text
                return question_answer_body, status.HTTP_201_CREATED

        counter.save()
        return self._UNSUCCESS_RESPONSE_BODY, status.HTTP_400_BAD_REQUEST

    def _handle_no_question_validation(
        self,
        point_type: TypeQuestionPoints,
        required_data: Optional[Iterable] = None,
    ) -> tuple[dict, int]:
        """Если у TaskObject отключена проверка (необходимо ответить хоть что-то/сопоставить все даже неправильно)."""
        if (required_data and len(self.request_data) < len(required_data)) or not self.request_data:
            return self._WRONG_ANSWER_WO_VALIDATION, status.HTTP_400_BAD_REQUEST
        self._create_tast_obj_result(point_type)
        return self._SUCCESS_RESPONSE_BODY, status.HTTP_201_CREATED

    def _create_tast_obj_result(
        self,
        point_type: TypeQuestionPoints,
        text: str = "",
        correct_answer: bool = True,
    ):
        """
        Формирование результата выполнения задачи:
        - 80 / количество задач в навыке
        - 0 баллов, если задача бесплатная
        """
        if self.request_task_object.task.free_access:
            points = 0
        else:
            skill = self.request_task_object.task.skill
            tasks_count = skill.tasks.count() or 1  # защита от деления на 0
            points = round(80 / tasks_count)

        TaskObjUserResult.objects.create(
            task_object=self.request_task_object,
            user_profile_id=self.request_profile_id,
            text=text,
            correct_answer=correct_answer,
            points_gained=points,
        )

    def _delete_self_counter(self):
        """Удаление `UserAnswersAttemptCounter` сущности."""
        counter = UserAnswersAttemptCounter.objects.filter(
            user_profile_id=self.request_profile_id,
            task_object=self.request_task_object,
        ).first()
        if counter:
            counter.delete()


class SingleCorrectAnswerService(AbstractAnswersService):
    """Проверка ответа пользователя на вопрос с 1 правильным ответом."""

    _QUSTION_POINTS: TypeQuestionPoints = TypeQuestionPoints.QUESTION_SINGLE_ANSWER

    def _check_correct_answer(self) -> tuple[dict[str, Any], int]:
        """Проверка на корректность ответа + формирование процесса с `couter` (если вопросом это предполагается)."""
        question_answer: QuerySet[AnswerSingle] = (
            self.request_question
            .single_answers
            .filter(is_correct=True)
            .first()
        )

        if self.request_data.get("answer_id") == question_answer.id:
            self._create_tast_obj_result(self._QUSTION_POINTS)
            self._delete_self_counter()
            return self._SUCCESS_RESPONSE_BODY, status.HTTP_201_CREATED

        if self.request_question.attempts_before_hint:
            return self._process_answer_attempt_counter(question_answer)
        return self._UNSUCCESS_RESPONSE_BODY, status.HTTP_400_BAD_REQUEST

    def _create_answer_response_body(self, question_answer: AnswerSingle):
        response_body = deepcopy(self._UNSUCCESS_RESPONSE_BODY)
        response_body["answer_ids"] = question_answer.id
        return response_body


class QuestionExcludeAnswerService(AbstractAnswersService):
    """Проверка ответа пользователя на вопрос на исключение."""

    _QUSTION_POINTS: TypeQuestionPoints = TypeQuestionPoints.QUESTION_EXCLUDE

    def _check_correct_answer(self) -> tuple[dict[str, Any], int]:
        correct_answers_ids: set[int] = set(
            self.request_question.single_answers.filter(is_correct=False).values_list("id", flat=True)
        )
        given_answer_ids: set[int] = set(self.request_data)

        if correct_answers_ids == given_answer_ids:
            self._create_tast_obj_result(self._QUSTION_POINTS)
            self._delete_self_counter()
            return self._SUCCESS_RESPONSE_BODY, status.HTTP_201_CREATED

        if self.request_question.attempts_before_hint:
            return self._process_answer_attempt_counter(correct_answers_ids)

        return self._UNSUCCESS_RESPONSE_BODY, status.HTTP_400_BAD_REQUEST

    def _create_answer_response_body(self, question_answer: AnswerSingle):
        response_body = deepcopy(self._UNSUCCESS_RESPONSE_BODY)
        response_body["answer_ids"] = list(question_answer)
        return response_body


class QuestionConnectAnswerService(AbstractAnswersService):
    """Проверка ответа пользователя на вопрос-соотношение."""

    _QUSTION_POINTS: TypeQuestionPoints = TypeQuestionPoints.QUESTION_CONNECT

    def _check_correct_answer(self) -> tuple[dict[str, Any], int]:
        all_answer_options: QuerySet[AnswerConnect] = self.request_question.connect_answers.all()

        answers_ids: list[int] = set(all_answer_options.values_list("id", flat=True))
        user_answer_ids: set[int] = (
            {answer["right_id"] for answer in self.request_data}
            | {answer["left_id"] for answer in self.request_data}
        )

        if answers_ids != user_answer_ids:
            raise QustionConnectException("Wrong ids or need more answers.")

        answer_is_correct: bool = all([answer["right_id"] == answer["left_id"] for answer in self.request_data])
        if answer_is_correct:
            self._create_tast_obj_result(self._QUSTION_POINTS)
            self._delete_self_counter()
            return self._SUCCESS_RESPONSE_BODY, status.HTTP_201_CREATED

        if self.request_question.attempts_before_hint:
            return self._process_answer_attempt_counter(all_answer_options)

        return self._UNSUCCESS_RESPONSE_BODY, status.HTTP_400_BAD_REQUEST

    def _create_answer_response_body(self, question_answer: AnswerSingle):
        response_body = deepcopy(self._UNSUCCESS_RESPONSE_BODY)
        response_body["answer_ids"] = [
            {
                "left_id": answer.id,
                "right_id": answer.id
            }
            for answer in question_answer
        ]
        return response_body


class QuestionWriteAnswerService(AbstractAnswersService):
    """Проверка (запись) ответа пользователя на вопрос с вводом ответа."""
    _QUSTION_POINTS: TypeQuestionPoints = TypeQuestionPoints.QUESTION_WRITE

    def create_answer(self) -> tuple[dict[str, Any], int]:
        if user_answer := self.request_data.get("text"):
            self._create_tast_obj_result(self._QUSTION_POINTS, text=user_answer)
            return self._SUCCESS_RESPONSE_BODY, status.HTTP_201_CREATED

        return self._UNSUCCESS_RESPONSE_BODY, status.HTTP_400_BAD_REQUEST

    def _check_correct_answer(self) -> tuple[dict[str, Any], int]:
        raise NotImplementedError

    def _create_answer_response_body(self) -> dict[str, Any]:
        raise NotImplementedError


class InfoSlideAnswerService(AbstractAnswersService):
    """Проверка (запись) ответа пользователя инфо слайд."""
    _QUSTION_POINTS: TypeQuestionPoints = TypeQuestionPoints.INFO_SLIDE

    def create_answer(self) -> tuple[dict[str, Any], int]:
        self._create_tast_obj_result(self._QUSTION_POINTS)
        return self._SUCCESS_RESPONSE_BODY, status.HTTP_201_CREATED

    def _check_correct_answer(self) -> tuple[dict[str, Any], int]:
        raise NotImplementedError

    def _create_answer_response_body(self) -> dict[str, Any]:
        raise NotImplementedError
