import calendar
import datetime
from abc import ABC, abstractmethod

from typing import Annotated

from django.core.cache import cache
from django.db.models import Prefetch, F, QuerySet

from courses.models import Task
from progress.models import IntermediateUserSkills, TaskObjUserResult
from questions.mapping import UserSkillProgressDict, MONTH_IN_SECONDS, UserTaskProgressDict
from questions.utils.additional_points.typing_and_constants import (
    AdditionalPointsTypes,
    TaskDates,
    WEEK_BEGIN_DAYS,
)


class TaskStatusAbstractChecker(ABC):
    """
    Абстрактный класс для начисления доп.
    очков юзеру при прохождении заданий в нужный промежуток времени.
    """
    _quantity_of_additional_points: int

    def __init__(
            self,
            task: Task,
            user_profile_id: int,
    ):
        self.task_id = task.id
        self.skill_id = task.skill.id
        self.user_profile_id = user_profile_id

        self.user_skill_progress: UserSkillProgressDict = self._get_user_skill_progress()

    @abstractmethod
    def check_needed_tasks_done(self) -> Annotated[int, "_quantity_of_additional_points or 0"]:
        """
        Проверяет, соблюдены ли нужные условия для начисления баллов.
        Возвращает число добавляемых очков, когда выполняется условие:
        'все задачи в категории (в нужной неделе / месяце, и т.д.)
        выполнены кроме задачи с id = self.task_id'.

        В ином случае возвращает 0.
        """

    @property
    def date_today(self) -> Annotated[str, "example: '%Y-%m-%d' or '%Y-%m'"]:
        """Сделано, чтоб можно было менять формат времени в зависимости от класса"""
        return datetime.datetime.now().date().strftime('%Y-%m-%d')

    @staticmethod
    def _map_week_number(week_number: int) -> TaskDates:
        today = datetime.date.today()

        # последнее число месяца скачет
        last_day_of_month: 28 | 29 | 30 | 31 = calendar.monthrange(today.year, today.month)[1]
        week_end_days: list[int] = [7, 14, 21, last_day_of_month]

        return TaskDates(
            begin_date=f"{today.year}-{today.month}-{WEEK_BEGIN_DAYS[week_number - 1]}",
            end_date=f"{today.year}-{today.month}-{week_end_days[week_number - 1]}"
        )

    @abstractmethod
    def _is_done_in_time_period(self, date_to_compare: str | None = None) -> bool:
        """
        Предварительная проверка перед исполнением.
        Если не проходит, дальнейший код не запускается.

        data_to_compare: какую дату сравниваем с датами из user_skill_progres["tasks"][self.task_id]
        """

    def _mark_current_task_id_as_done(self):
        self.user_skill_progress["tasks"][self.task_id]["is_done_in_time"] = True
        cache.set(f"{self.user_profile_id}_{self.skill_id}", self.user_skill_progress, timeout=MONTH_IN_SECONDS)

    def _date_status_check(self) -> bool:
        if not self._is_done_in_time_period():
            return False
        if self.user_skill_progress["tasks"][self.task_id]["is_done_in_time"]:
            """Если проверяемая задача уже сделана, то что-то не то, и смысла дальше проверять нет."""
            return False
        return True

    def _get_skill_date(self) -> datetime.date:
        skill_date = (
            IntermediateUserSkills.objects
            .filter(user_profile_id=self.user_profile_id, skill_id=self.skill_id)
            .order_by("-date_chosen")
            .only("date_chosen")
            .first()
        )
        return skill_date.date_chosen

    def _get_tasks_of_skill(self) -> QuerySet[Task]:
        return (
            Task.published
            .prefetch_related(
                Prefetch(
                    "task_objects__user_results",
                    queryset=TaskObjUserResult.objects.filter(
                        user_profile_id=self.user_profile_id,
                        datetime_created__gte=F("week_begin"),
                        datetime_created__lte=F("week_end"),
                    ),
                    to_attr="filtered_user_results",
                )
            )
            .prefetch_related("task_objects")
            .filter(skill_id=self.skill_id, skill__status="published")
            .order_by("ordinal_number")
        )

    @staticmethod
    def _get_user_tasks_progress(
            tasks_of_skill: QuerySet[Task],
            skill_date: datetime.date
    ) -> UserSkillProgressDict:
        tasks: dict[int, UserTaskProgressDict] = {}

        for task in tasks_of_skill:
            is_task_done = all(obj.filtered_user_results for obj in task.task_objects.all())
            tasks[task.id] = UserTaskProgressDict(
                begin_date=task.begin_date,
                end_date=task.end_date,
                is_done_in_time=is_task_done
            )

        return UserSkillProgressDict(
            tasks=tasks,
            skill_date=datetime.datetime.strftime(skill_date, '%Y-%m')
        )

    def _set_user_skill_progress(self) -> UserSkillProgressDict:
        skill_date: datetime.date = self._get_skill_date()
        tasks_of_skill: QuerySet[Task] = self._get_tasks_of_skill()

        user_skill_progress: UserSkillProgressDict = self._get_user_tasks_progress(
            tasks_of_skill,
            skill_date
        )

        cache.set(
            f"{self.user_profile_id}_{self.skill_id}",
            user_skill_progress,
            timeout=MONTH_IN_SECONDS
        )

        return user_skill_progress

        # TODO добавить в модели
        # TODO перенести в отдельный файл в utils

    def _get_user_skill_progress(self) -> UserSkillProgressDict:
        user_skill_progress = cache.get(f"{self.user_profile_id}_{self.skill_id}")
        if not user_skill_progress:
            user_skill_progress = self._set_user_skill_progress()
        return user_skill_progress


class TaskStatusWeekChecker(TaskStatusAbstractChecker):
    _quantity_of_additional_points: int = AdditionalPointsTypes.WEEK_DONE.value

    def _is_done_in_time_period(self, date_to_compare: str | None = None) -> bool:
        """Проверяет, попадает ли date_to_compare в промежуток задачи"""
        if date_to_compare is None:
            date_to_compare = datetime.datetime.strptime(self.date_today, "%Y-%m-%d")
        date_begin = datetime.datetime.strptime(
            self.user_skill_progress["tasks"][self.task_id]["begin_date"], "%Y-%m-%d"
        )
        date_end = datetime.datetime.strptime(
            self.user_skill_progress["tasks"][self.task_id]["end_date"], "%Y-%m-%d"
        )
        return date_begin <= date_to_compare <= date_end

    def check_needed_tasks_done(self) -> int:
        if self._date_status_check():
            return 0

        # если все на нужной неделе сделано кроме задачи с self.task_id
        is_done_needed_but_not_task_id = True
        for task_id, task_data in self.user_skill_progress["tasks"].values():
            begin_day_is_similar = self._is_done_in_time_period(
                task_data["begin_date"]
            )
            end_day_is_similar = self._is_done_in_time_period(
                task_data["end_date"]
            )
            if not (begin_day_is_similar and end_day_is_similar):
                """Отсекаем задания по промежуткам времени"""
                continue
            if task_id == self.task_id:
                continue
            elif self.user_skill_progress["tasks"][task_id]["is_done_in_time"] is False:
                is_done_needed_but_not_task_id = False
                break

        self._mark_current_task_id_as_done()
        if is_done_needed_but_not_task_id:
            return self._quantity_of_additional_points
        return 0


class TaskStatusMonthChecker(TaskStatusAbstractChecker):
    _quantity_of_additional_points: int = AdditionalPointsTypes.MONTH_DONE.value

    @property
    def date_today(self) -> Annotated[str, "date '%Y-%m'"]:
        return datetime.datetime.now().date().strftime('%Y-%m')

    def _is_done_in_time_period(self, date_to_compare: str | None = None) -> bool:
        if date_to_compare is None:
            date_to_compare: str = self.user_skill_progress.get("skill_date")
        return self.date_today == date_to_compare

    def check_needed_tasks_done(self) -> int:
        if self._date_status_check():
            return 0

        # если все сделано кроме задачи с self.task_id
        is_done_needed_but_not_task_id = True
        for task_id, task_data in self.user_skill_progress["tasks"].values():
            if task_id == self.task_id:
                continue
            elif task_data["is_done_in_time"] is False:
                is_done_needed_but_not_task_id = False
                break

        self._mark_current_task_id_as_done()
        if is_done_needed_but_not_task_id:
            return self._quantity_of_additional_points
        return 0
