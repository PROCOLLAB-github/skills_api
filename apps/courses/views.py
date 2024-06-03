from django.db.models import OuterRef, Exists

from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework import permissions

from .mapping import TYPE_TASK_OBJECT, check_if_task_correct
from .models import Task, Skill, TaskObject
from .serializers import TaskSerializer, SkillsBasicSerializer, TasksOfSkillSerializer
from .services import get_stats, get_skills_details


from procollab_skills.decorators import (
    exclude_auth_perm,
    #  exclude_sub_check_perm
)

from progress.models import TaskObjUserResult
from progress.pagination import DefaultPagination
from progress.serializers import ResponseSerializer
from questions.serializers import IntegerListSerializer


class TaskList(generics.ListAPIView):
    serializer_class = TaskSerializer

    @extend_schema(summary="Выводит информацию о задаче", tags=["Навыки и задачи"], responses={200: TaskSerializer})
    def get(self, request, *args, **kwargs):
        try:
            task_id = self.kwargs.get("task_id")

            task = Task.objects.prefetch_related("task_objects", "task_objects__content_object").get(id=int(task_id))

            task_objects = task.task_objects.annotate(
                has_user_results=Exists(
                    TaskObjUserResult.objects.filter(task_object=OuterRef("pk"), user_profile_id=self.profile_id)
                )
            ).order_by("ordinal_number")

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
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_200_OK)


# TODO добавить поля для количества навыков
@extend_schema(
    summary="Выводит все навыки на платформе",
    tags=["Навыки и задачи"],
)
@exclude_auth_perm
class SkillsList(generics.ListAPIView):
    serializer_class = SkillsBasicSerializer
    pagination_class = DefaultPagination
    queryset = Skill.objects.all()
    permission_classes = [permissions.AllowAny]


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
        # TODO переписать эндпоинт, какой-то то непонятный
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
        needed_skill_data = {"level": skill_data["level"], "progress": skill_data.get("progress", 0)}

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


# @extend_schema(
#     summary="""Статус задач для навыка""",
#     request=IntegerListSerializer,
#     # responses={200: TasksOfSkillSerializer(many=True)},
#     tags=["Навыки и задачи"],
# )
# class SkillTaskStatus(generics.ListAPIView):
#
#     def get(self, request, *args, **kwargs):
#         skill_id = self.kwargs.get("skill_id")
#         profile_id = 1
#
#         tasks_of_skill = (
#             Task.objects
#             .prefetch_related(
#                 Prefetch(
#                     'task_objects__user_results',
#                     queryset=TaskObjUserResult.objects.filter(user_profile_id=profile_id),
#                     to_attr='filtered_user_results'  # этот атрибут будет недоступен напрямую через объект Task
#                 )
#             )
#             .prefetch_related("task_objects")
#             .filter(skill_id=skill_id)
#         )
#
#
#         data = []
#
#         for task in tasks_of_skill:
#             user_results_count = sum(1 for obj in task.task_objects.all() if obj.filtered_user_results)
#             data.append({
#                 "task_id": task.id,
#                 "status": user_results_count == task.task_objects.all().count()
#             })
#
#         statuses = (sum(1 for obj in data if obj["status"]) / tasks_of_skill.count()) * 100
#         new_data = [{"progress": int(statuses)}] + data
#
#         return Response(new_data, status=200)
