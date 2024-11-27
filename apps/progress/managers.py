from typing import TypeVar

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import UserManager

from django.db import IntegrityError
from django.db.models import Manager

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

    def create_user_result(
        self,
        task_obj_id: int,
        user_profile_id: int,
        type_task_obj: TaskObjs,
        text: str = "",
    ):
        try:
            self.get_queryset().create(
                task_object_id=task_obj_id,
                user_profile_id=user_profile_id,
                points_gained=type_task_obj.value,
                text=text
            )
        except IntegrityError as e:
            if "unique constraint" in str(e.args).lower():
                raise UserAlreadyAnsweredException
            else:
                raise IntegrityError(str(e))

    def get_with_related_fields(self, task_obj_id: int):
        return self.get_queryset().select_related(
            "user_profile",
            "task_object",
            "task_object__task",
            "task_object__task__skill",
        ).get(pk=task_obj_id)


class CustomUserManager(UserManager):
    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)

        return self._create_user(email, password, **extra_fields)

    def get_active(self):
        return self.get_queryset().filter(is_active=True).prefetch_related("member")

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        assert extra_fields.get("is_staff"), "Superuser must be assigned to is_staff=True"
        assert extra_fields.get("is_superuser"), "Superuser must be assigned to is_superuser=True"
        assert extra_fields.get("is_active"), "Superuser must be assigned to is_active=True"

        return self._create_user(email, password, **extra_fields)

    def _create_user(self, email, password, **extra_fields):
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.password = make_password(password)
        user.save()
        return user
