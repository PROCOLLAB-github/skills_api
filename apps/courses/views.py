from decimal import Decimal, ROUND_HALF_UP

from django.db.models import Count, F, Sum, Q, Exists, OuterRef

from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework import permissions

from progress.models import TaskObjUserResult
from .mapping import TYPE_TASK_OBJECT
from .models import Task, Skill, TaskObject
from .services import get_stats, get_skills_details
from .typing import TaskResultData
from .serializers import (
    TaskSerializer,
    SkillSerializer,
    SkillsBasicSerializer,
    TasksOfSkillSerializer,
    TaskResult,
    CoursesResponseSerializer,
)


# from procollab_skills.decorators import (
#  exclude_sub_check_perm
# )

from progress.pagination import DefaultPagination
from progress.serializers import ResponseSerializer
from .serializers import IntegerListSerializer


class TaskList(generics.RetrieveAPIView):
    serializer_class = TaskSerializer

    @extend_schema(
        summary="Выводит информацию о задаче",
        tags=["Навыки и задачи"],
        responses={200: CoursesResponseSerializer},
    )
    def get(self, request, *args, **kwargs):

        task_id = self.kwargs.get("task_id")

        task = (
            Task.objects
            .select_related("skill__skill_preview", "skill__skill_point_logo")
            .get(id=int(task_id))
        )

        task_objects = (
            TaskObject.objects.filter(task=task)
            .annotate(
                has_user_results=Exists(
                    TaskObjUserResult.objects.filter(task_object=OuterRef("pk"), user_profile_id=self.profile_id)
                )
            )
            .distinct()
            .order_by("ordinal_number")
        )

        data = {
            "skill_name": task.skill.name,
            "skill_preview": task.skill.skill_preview.link if task.skill.skill_preview else None,
            "skill_point_logo": task.skill.skill_point_logo.link if task.skill.skill_point_logo else None,
            "count": task_objects.count(),
            "step_data": [],
        }
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
            skill_data = get_stats(task.skill.id, self.profile_id)
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
    queryset = Skill.published.all()
    permission_classes = [permissions.AllowAny]
    authentication_classes = []


@extend_schema(
    summary="Выводит подробную информацию о навыке",
    description="""Выводит только тот уровень, который юзер может пройти. Остальные для прохождения закрыты""",
    tags=["Навыки и задачи"],
    responses={200: SkillSerializer},
)
class SkillDetails(generics.RetrieveAPIView):
    serializer_class = ResponseSerializer

    def get(self, request, *args, **kwargs):
        # TODO FIX this
        # Временно статично "1 уровень" для навыков
        skill_detail = get_skills_details(self.kwargs.get("skill_id"), self.profile_id)
        skill_detail["level"] = 1
        return Response(skill_detail, status=200)


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
    responses={200: TaskResult},
    tags=["Навыки и задачи"],
)
class TaskStatsGet(generics.RetrieveAPIView):
    serializer_class = TaskResult

    def get(self, request, *args, **kwargs) -> Response:
        task_id: int = self.kwargs.get("task_id")

        task: Task = get_object_or_404(
            Task.objects.annotate(
                total_questions=Count("task_objects", distinct=True),  # Всего вопросов в задании.
                total_answers=Count(  # Всего ответов пользователя в задании.
                    "task_objects__user_results",
                    filter=Q(task_objects__user_results__user_profile_id=self.profile_id),
                    distinct=True,
                ),
                points_gained=Sum(  # Кол-во полученных поинтов юзером в рамках задания.
                    "task_objects__user_results__points_gained",
                    filter=Q(task_objects__user_results__user_profile_id=self.profile_id),
                    distinct=True,
                ),
            ),
            id=task_id,
        )

        skill: Skill = get_object_or_404(
            Skill.published.annotate(
                num_levels=F("quantity_of_levels"),  # Общее кол-во заданий навыка.
                total_num_questions=Count("tasks__task_objects"),  # Общее кол-во вопросов навыка.
                total_user_answers=Count(  # Общее кол-во ответов юзера в рамках навыка.
                    "tasks__task_objects__user_results",
                    filter=Q(tasks__task_objects__user_results__user_profile_id=self.profile_id),
                ),
            ),
            id=task.skill.id,
        )

        progress: int = 0
        if skill.total_user_answers and skill.total_num_questions:
            # Округление до %, round() работает некорректно, поэтому взят Decimal
            decimal_progress: Decimal = Decimal(str((skill.total_user_answers / skill.total_num_questions) * 100))
            progress: int = int(decimal_progress.quantize(Decimal("1"), rounding=ROUND_HALF_UP))

        data = TaskResultData(
            points_gained=task.points_gained if task.points_gained else 0,
            quantity_done_correct=task.total_answers,
            quantity_all=task.total_questions,
            level=task.level,
            progress=progress,
            skill_name=skill.name,
            next_task_id=task.level + 1 if task.level + 1 < skill.num_levels else None,
        )
        serializer = self.get_serializer(data)
        return Response(serializer.data, status=status.HTTP_200_OK)
