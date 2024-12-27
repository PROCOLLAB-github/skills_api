from django.shortcuts import get_object_or_404

from django.db.models import (
    Sum, Q,
    BooleanField,
    Case,
    Count,
    Exists,
    OuterRef,
    Prefetch,
    QuerySet,
    Value,
    Subquery,
    When,
)
from rest_framework import generics, status
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated

from progress.models import TaskObjUserResult, UserSkillDone
from progress.services import (
    DBObjectStatusFilters,
    get_user_available_week,
    get_rounded_percentage,
)
from subscription.permissions import (
    SubscriptionObjectPermission,
    SubscriptionSectionPermission,
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
    permission_classes = [IsAuthenticated, SubscriptionObjectPermission]

    @extend_schema(
        summary="Выводит информацию о задаче",
        tags=["Навыки и задачи"],
        responses={200: CoursesResponseSerializer},
    )
    def get(self, request, *args, **kwargs):

        task_id = self.kwargs.get("task_id")
        available_week, _ = get_user_available_week(self.profile_id)
        task: Task = self.get_object(task_id, available_week)

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
            "free_access": task.free_access,
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
            skill_data = get_stats(task.skill, self.profile_id, self.request.user)
            return Response(skill_data | data, status=status.HTTP_200_OK)
        else:
            return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def get_object(self, task_id: int, available_week: int) -> Task:
        task: Task = get_object_or_404(
            Task.published.for_user(self.request.user),
            id=int(task_id),
        )
        self.check_object_permissions(request=self.request, obj=task)
        return get_object_or_404(
            Task.available
            .only_awailable_weeks(available_week, self.request.user)
            .select_related("skill__skill_preview", "skill__skill_point_logo"),
            id=int(task_id),
        )


# TODO добавить поля для количества навыков
@extend_schema(
    summary="Выводит все навыки на платформе",
    tags=["Навыки и задачи"],
)
class SkillsList(generics.ListAPIView):
    # TODO FIX: В сериализаторе указан статичный уровень 1 для всех навыков
    serializer_class = SkillsBasicSerializer
    pagination_class = DefaultPagination

    def get_queryset(self):
        return Skill.published.for_user(self.request.user)


@extend_schema(
    summary="Выводит все навыки на платформе, помечает использованные",
    tags=["Навыки и задачи"],
)
class DoneSkillsList(generics.ListAPIView):
    serializer_class = SkillsDoneSerializer
    pagination_class = DefaultPagination
    permission_classes = [IsAuthenticated, SubscriptionSectionPermission]

    # TODO FIX: В сериализаторе указан статичный уровень 1 для всех навыков
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
    permission_classes = [IsAuthenticated, SubscriptionObjectPermission]
    lookup_url_kwarg = "skill_id"

    def get_queryset(self):
        return Skill.published.for_user(self.request.user)


@extend_schema(
    summary="""Вывод задач для навыков""",
    responses={200: TaskOfSkillProgressSerializer},
    tags=["Навыки и задачи"],
)
class TasksOfSkill(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated, SubscriptionObjectPermission]
    serializer_class = TaskOfSkillProgressSerializer

    def get(self, request, *args, **kwargs):
        skill: Skill = get_object_or_404(
            Skill.published.for_user(self.request.user),
            id=self.kwargs.get("skill_id"),
        )
        self.check_object_permissions(request=request, obj=skill)

        return Response(
            get_stats(skill, self.profile_id, self.request.user),
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
    permission_classes = [IsAuthenticated, SubscriptionObjectPermission]

    def get(self, request, *args, **kwargs) -> Response:
        task_id: int = self.kwargs.get("task_id")
        # TODO Optimize
        task, available_week = self.get_object(task_id)

        skill_status_filter = DBObjectStatusFilters().get_skill_status_for_user(self.request.user)

        tasks_of_skill: QuerySet[Task] = (
            Task.available
            .only_awailable_weeks(available_week, self.request.user)
            .prefetch_related(
                Prefetch(
                    "task_objects__user_results",
                    queryset=TaskObjUserResult.objects.filter(user_profile_id=self.profile_id),
                    to_attr="filtered_user_results",
                )
            ).prefetch_related("task_objects")
            .annotate(task_objects_count=Count("task_objects"))
            .filter(skill_id=task.skill.id)
            .filter(skill_status_filter)
        )

        user_done_task_objects: list[int] = []
        all_task_objects: list[int] = []
        for task_on_skill in tasks_of_skill:
            user_results_count = sum(1 for obj in task_on_skill.task_objects.all() if obj.filtered_user_results)
            user_done_task_objects.append(user_results_count)
            all_task_objects.append(task_on_skill.task_objects_count)

        progress = get_rounded_percentage(sum(user_done_task_objects), sum(all_task_objects))

        data = TaskResultData(
            points_gained=task.points_gained if task.points_gained else 0,
            quantity_done_correct=task.total_correct_answers,
            quantity_done=task.total_answers,
            quantity_all=task.total_questions,
            level=task.level,
            progress=progress,
            skill_name=task.skill.name,
            next_task_id=task.next_task_id if task.next_task_id else None,
        )

        serializer = self.get_serializer(data)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def get_object(self, task_id: int) -> tuple[Task, int]:
        task: Task = get_object_or_404(
            Task.published.for_user(self.request.user),
            id=task_id,
        )
        self.check_object_permissions(request=self.request, obj=task)
        available_week, _ = get_user_available_week(self.profile_id)
        available_week = available_week if not task.free_access else 4
        task = get_object_or_404(
            (
                Task.available
                .only_awailable_weeks(available_week, self.request.user)  # Только доступыне недели.
                .annotate(
                    total_questions=Count("task_objects", distinct=True),  # Всего вопросов в задании.
                    total_answers=Count(  # Всего ответов пользователя в задании.
                        "task_objects__user_results",
                        filter=Q(task_objects__user_results__user_profile_id=self.profile_id),
                        distinct=True,
                    ),
                    total_correct_answers=Count(  # Всего ответов пользователя в задании.
                        "task_objects__user_results",
                        filter=(
                            Q(task_objects__user_results__user_profile_id=self.profile_id)
                            & Q(task_objects__user_results__correct_answer=True)
                        ),
                        distinct=True,
                    ),
                    points_gained=Sum(  # Кол-во полученных поинтов юзером в рамках задания.
                        "task_objects__user_results__points_gained",
                        filter=Q(task_objects__user_results__user_profile_id=self.profile_id),
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
        return task, available_week
