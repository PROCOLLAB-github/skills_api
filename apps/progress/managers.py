from typing import TypeVar

from django.db import IntegrityError
from django.db.models import Manager, Prefetch

from questions.exceptions import UserAlreadyAnsweredException

# from questions.mapping import TaskObjs
TaskObjs = TypeVar("TaskObjs")  # не смог тайпхинты нормально сделать из-за ошибки circular import(((
ModelInstance = TypeVar("ModelInstance")


class TaskObjUserResultManager(Manager):
    def get_answered(self, task_obj_id: int, user_profile_id: int, type_task_obj: TaskObjs) -> ModelInstance | None:
        return (
            self.get_queryset()
            .filter(
                task_object_id=task_obj_id,
                user_profile_id=user_profile_id,
                points_gained=type_task_obj.value,
            )
            .first()
        )

    def create_user_result(self, task_obj_id: int, user_profile_id: int, type_task_obj: TaskObjs):
        try:
            self.get_queryset().create(
                task_object_id=task_obj_id,
                user_profile_id=user_profile_id,
                points_gained=type_task_obj.value,
            )
        except IntegrityError as e:
            if "unique constraint" in str(e.args).lower():
                raise UserAlreadyAnsweredException
            else:
                raise IntegrityError(str(e))

    def get_wiht_related_fields(self, task_obj_id: int):
        return self.get_queryset().select_related(
            "user_profile",
            "task_object",
            "task_object__task",
            "task_object__task__skill",
        ).get(pk=task_obj_id)


class UserProfileManager(Manager):
    def prefetch_current_skills(self):
        from progress.models import IntermediateUserSkills
        from progress.services import months_passed_data

        dates = months_passed_data()
        return self.get_queryset().prefetch_related(
            Prefetch(
                "chosen_skills",
                queryset=IntermediateUserSkills.objects.filter(
                    date_chosen__year__in=[date.year for date in dates],
                    date_chosen__month__in=[date.month for date in dates],
                ),
            )
        )
