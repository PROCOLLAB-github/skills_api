from django.shortcuts import get_object_or_404

from django.db.models import Count, Sum, Q, Exists, OuterRef, Subquery, Case, When, Value, BooleanField

from rest_framework import generics, status
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from drf_spectacular.utils import extend_schema


from procollab_skills.auth import CustomAuth
from progress.models import TaskObjUserResult, UserSkillDone

from progress.services import (
    DBSubQuryFiltersForUser,
    get_user_available_week,
    get_rounded_percentage,
)
from .mapping import TYPE_TASK_OBJECT
from .models import Task, Skill, TaskObject
from .services import get_stats
from .typing import TaskResultData
from .serializers import (
    TaskSerializer,
    SkillsBasicSerializer,
    TaskOfSkillProgressSerializer,
    TaskResult,
    CoursesResponseSerializer,
    SkillDetailsSerializer,
    SkillsDoneSerializer,
)


from progress.pagination import DefaultPagination
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
        available_week, _ = get_user_available_week(self.profile_id)
        task = get_object_or_404(
            Task.available
            .only_awailable_weeks(available_week, self.request.user)
            .select_related("skill__skill_preview", "skill__skill_point_logo"),
            id=int(task_id),
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
            "current_level": task.level,
            "next_level": task.level + 1 if task.level + 1 < task.skill.quantity_of_levels else None,
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
            skill_data = get_stats(task.skill.id, self.profile_id, self.request.user)
            return Response(skill_data | data, status=status.HTTP_200_OK)
        else:
            return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


# TODO добавить поля для количества навыков
@extend_schema(
    summary="Выводит все навыки на платформе",
    tags=["Навыки и задачи"],
)
class SkillsList(generics.ListAPIView):
    # TODO FIX: В сериализаторе указан статичный уровень 1 для всех навыков
    serializer_class = SkillsBasicSerializer
    pagination_class = DefaultPagination
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def get_queryset(self):
        """
        Появилась необходимость получить юзера, обход кастомной атентификации.
        Через Swagger не сработает (дока токен не шлет из-за `authentication_classes=[]`),
        только фронт | Postman (отправлен/не отправлен токен).
        """
        try:
            user = CustomAuth().authenticate(self.request)[0]
        except PermissionDenied as e:
            if "User credentials are not given" not in str(e):
                raise
            user = None
        return Skill.published.for_user(user)


@extend_schema(
    summary="Выводит все навыки на платформе, помечает использованные",
    tags=["Навыки и задачи"],
)
class DoneSkillsList(generics.ListAPIView):
    # TODO FIX: В сериализаторе указан статичный уровень 1 для всех навыков
    serializer_class = SkillsDoneSerializer
    pagination_class = DefaultPagination

    def get_queryset(self) -> Skill:
        return Skill.published.for_user(self.request.user).annotate(
            has_user_done_skills=Exists(
                UserSkillDone.objects.filter(user_profile=self.user_profile, skill_id=OuterRef("id"))
            )
        ).annotate(
            is_done=Case(
                When(has_user_done_skills=True, then=Value(True)), default=Value(False), output_field=BooleanField()
            )
        )


@extend_schema(
    summary="Выводит подробную информацию о навыке",
    description="""Выводит только тот уровень, который юзер может пройти. Остальные для прохождения закрыты""",
    tags=["Навыки и задачи"],
    responses={200: SkillDetailsSerializer},
)
class SkillDetails(generics.RetrieveAPIView):
    serializer_class = SkillDetailsSerializer
    lookup_url_kwarg = "skill_id"

    def get_queryset(self):
        return Skill.published.for_user(self.request.user)


@extend_schema(
    summary="""Вывод задач для навыков""",
    responses={200: TaskOfSkillProgressSerializer},
    tags=["Навыки и задачи"],
)
class TasksOfSkill(generics.RetrieveAPIView):
    serializer_class = TaskOfSkillProgressSerializer

    def get(self, request, *args, **kwargs):
        skill = get_object_or_404(Skill.published.for_user(self.request.user), id=self.kwargs.get("skill_id"))
        return Response(
            get_stats(skill.id, self.profile_id, self.request.user),
            status=status.HTTP_200_OK,
        )


@extend_schema(
    summary="Инфа о новом уровне",
    request=IntegerListSerializer,
    responses={200: TaskResult},
    tags=["Навыки и задачи"],
)
class TaskStatsGet(generics.RetrieveAPIView):
    serializer_class = TaskResult

    def get(self, request, *args, **kwargs) -> Response:
        task_id: int = self.kwargs.get("task_id")
        available_week, _ = get_user_available_week(self.profile_id)
        task: Task = get_object_or_404(
            (
                Task.available.only_awailable_weeks(available_week, self.request.user)
                .annotate(  # Только доступыне недели.
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
                    next_task_id=Subquery(  # ID следующего задания.
                        Task.available.only_awailable_weeks(available_week, self.request.user)
                        .filter(skill=OuterRef("skill"), ordinal_number=OuterRef("ordinal_number") + 1)
                        .values("id")[:1]
                    ),
                )
            ),
            id=task_id,
        )
        task_status_filter = DBSubQuryFiltersForUser().get_many_tasks_status_filter_for_user(self.request.user)
        skill: Skill = get_object_or_404(
            Skill.published.for_user(self.request.user).annotate(
                # Общее кол-во опубликованных вопросов навыка.
                total_num_questions=Count(
                    "tasks__task_objects", filter=(task_status_filter & Q(tasks__week__lte=available_week))
                ),
                # Общее кол-во ответов юзера на опубликованные вопросы в рамках навыка.
                total_user_answers=Count(
                    "tasks__task_objects__user_results",
                    filter=(
                        task_status_filter
                        & Q(tasks__task_objects__user_results__user_profile_id=self.profile_id)
                        & Q(tasks__week__lte=available_week)  # Только доступыне недели.
                    ),
                ),
            ),
            id=task.skill.id,
        )
        progress: int = get_rounded_percentage(skill.total_user_answers, skill.total_num_questions)
        data = TaskResultData(
            points_gained=task.points_gained if task.points_gained else 0,
            quantity_done_correct=task.total_answers,
            quantity_all=task.total_questions,
            level=task.level,
            progress=progress,
            skill_name=skill.name,
            next_task_id=task.next_task_id if task.next_task_id else None,
        )

        serializer = self.get_serializer(data)
        return Response(serializer.data, status=status.HTTP_200_OK)
