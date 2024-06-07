from django.db.models import Case, When, BooleanField

from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework import permissions

from .mapping import TYPE_TASK_OBJECT, check_if_task_correct
from .models import Task, Skill, TaskObject
from .serializers import TaskSerializer, SkillsBasicSerializer, TasksOfSkillSerializer
from .services import get_stats, get_skills_details


# from procollab_skills.decorators import (
#  exclude_sub_check_perm
# )

from progress.models import TaskObjUserResult
from progress.pagination import DefaultPagination
from progress.serializers import ResponseSerializer
from .serializers import IntegerListSerializer


class TaskList(generics.ListAPIView):
    serializer_class = TaskSerializer

    @extend_schema(summary="Выводит информацию о задаче", tags=["Навыки и задачи"], responses={200: TaskSerializer})
    def get(self, request, *args, **kwargs):
        task_id = self.kwargs.get("task_id")

        task = Task.objects.prefetch_related("task_objects", "task_objects__content_object").get(id=int(task_id))

        task_objects = (
            task.task_objects.annotate(
                has_user_results=Case(
                    When(user_results__user_profile__id=self.profile_id, then=True),
                    default=False,
                    output_field=BooleanField(),
                )
            )
            .distinct()
            .order_by("ordinal_number")
        )

        data = {"count": task_objects.count(), "step_data": []}
        for task_object in task_objects:
            type_task = TYPE_TASK_OBJECT[task_object.content_type.model]
            # TODO вместо словаря сделать Enum
            if type_task == "question_single_answer" and task_object.content_object.is_exclude:
                type_task = "exclude_question"
            data["step_data"].append(
                {
                    "id": task_object.id,
                    "type": type_task,
                    "is_done": task_object.has_user_results,
                    "ordinal_number": task_object.ordinal_number,
                }
            )

        serializer = self.serializer_class(data=data)
        if serializer.is_valid():
            skill_data = get_skills_details(task.skill.id, user_profile_id=1)
            return Response(skill_data | data, status=status.HTTP_200_OK)
        else:
            return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


# TODO добавить поля для количества навыков
@extend_schema(
    summary="Выводит все навыки на платформе",
    tags=["Навыки и задачи"],
)
class SkillsList(generics.ListAPIView):
    serializer_class = SkillsBasicSerializer
    pagination_class = DefaultPagination
    queryset = Skill.objects.filter(status="published")
    permission_classes = [permissions.AllowAny]
    authentication_classes = []


@extend_schema(
    summary="Выводит подробную информацию о навыке",
    description="""Выводит только тот уровень, который юзер может пройти. Остальные для прохождения закрыты""",
    tags=["Навыки и задачи"],
)
class SkillDetails(generics.ListAPIView):
    serializer_class = ResponseSerializer

    def get(self, request, *args, **kwargs):
        return Response(get_skills_details(self.kwargs.get("skill_id"), self.profile_id), status=200)


@extend_schema(
    summary="""Вывод задач для навыков""",
    request=IntegerListSerializer,
    responses={200: TasksOfSkillSerializer(many=True)},
    tags=["Навыки и задачи"],
)
class TasksOfSkill(generics.ListAPIView):
    serializer_class = TasksOfSkillSerializer

    def get(self, request, *args, **kwargs):
        return Response(get_stats(self.kwargs.get("skill_id"), self.profile_id), status=200)


@extend_schema(
    summary="""Инфа о новом уровне""",
    request=IntegerListSerializer,
    # responses={200: TasksOfSkillSerializer(many=True)},
    tags=["Навыки и задачи"],
)
class TaskStatsGet(generics.ListAPIView):
    serializer_class = ...

    def list(self, request, *args, **kwargs):
        task_id = self.kwargs.get("task_id")

        task = get_object_or_404(Task.objects.values("skill_id", "id", "ordinal_number"), id=task_id)

        next_task = (
            Task.objects.filter(skill_id=task["skill_id"], ordinal_number=task["ordinal_number"] + 1)
            .values("id")
            .first()
        )

        task["next_task_id"] = next_task["id"] if next_task else None

        skill_data = get_skills_details(
            skill_id=task["skill_id"],
            user_profile_id=self.profile_id,
        )
        needed_skill_data = {
            "level": skill_data["level"],
            "progress": skill_data.get("progress", 0),
            "skill_name": skill_data.get("skill_name"),
        }
        task_objs = TaskObject.objects.filter(task_id=task["id"]).values_list("id", flat=True)
        task_results = TaskObjUserResult.objects.select_related("task_object", "task_object__content_type").filter(
            user_profile_id=self.profile_id,
            task_object_id__in=task_objs,
        )

        done_correct_tasks = 0
        total_points = 0
        for result in task_results:
            if points := check_if_task_correct(result):
                total_points += points
                done_correct_tasks += 1
        data = {
            "points_gained": total_points,
            "quantity_done_correct": done_correct_tasks,
            "quantity_all": task_objs.count(),
            **needed_skill_data,
            "next_task_id": task["next_task_id"],
        }
        return Response(data, status=200)
