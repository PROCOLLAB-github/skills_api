from django.db.models import Prefetch

from courses.models import Task
from progress.models import TaskObjUserResult
from questions.utils.additional_points.task_status_checker import TaskStatusWeekChecker, TaskStatusMonthChecker
from questions.utils.additional_points.typing_and_constants import AdditionalPointsTypes, AdditionalPointsParams


class PointsCalculator:

    def __init__(self, calculate_params: AdditionalPointsParams):
        self.task_obj: int = calculate_params.task_obj_id
        self.task: Task = self._get_task()
        self.user_profile_id: int = calculate_params.user_profile_id
        self.task_obj_id: int = calculate_params.task_obj_id
        self.points_added_to: int = calculate_params.points_added_to

    def calculate_points(self) -> int:
        is_task_done: bool = self._is_task_done()

        if is_task_done:
            self._add_points()
        return self.points_added_to

    def _get_task(self) -> Task:
        return (
            Task.published
            .prefetch_related(
                Prefetch(
                    "task_objects__user_results",
                    queryset=TaskObjUserResult.objects.filter(
                        user_profile_id=self.user_profile_id
                    ),
                    to_attr="filtered_user_results",
                )
            )
            .prefetch_related("task_objects")
            .filter(id=self.task.id)
        )

    def _is_task_done(self) -> bool:
        is_done_all_except_needed_task = True

        for task_obj in self.task.task_objects.all():
            if task_obj.id == self.task_obj_id and task_obj.filtered_user_results:
                is_done_all_except_needed_task = False
                break
            elif task_obj.id != self.task_obj_id and not task_obj.filtered_user_results:
                is_done_all_except_needed_task = False
                break
        return is_done_all_except_needed_task

    def _add_points(self):
        points_before_adding = self.points_added_to
        self.points_added_to += TaskStatusWeekChecker(
            self.task, self.user_profile_id
        ).check_needed_tasks_done()
        if self.points_added_to == points_before_adding + AdditionalPointsTypes.WEEK_DONE.value:
            self.points_added_to += TaskStatusMonthChecker(
                self.task, self.user_profile_id
            ).check_needed_tasks_done()
