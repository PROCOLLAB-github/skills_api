from django.db import IntegrityError
from django.db.models import Manager

from progress.models import TaskObjUserResult
from questions.exceptions import UserAlreadyAnsweredException
from questions.mapping import TaskObjs


class TaskObjUserResultManager(Manager):
    def get_answered(self, task_obj_id: int, user_profile_id: int, type_task_obj: TaskObjs) -> TaskObjUserResult | None:
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
            TaskObjUserResult.objects.create(
                task_object_id=task_obj_id,
                user_profile_id=user_profile_id,
                points_gained=type_task_obj.value,
            )
        except IntegrityError as e:
            if "unique constraint" in str(e.args).lower():
                raise UserAlreadyAnsweredException
            else:
                raise IntegrityError(str(e))
