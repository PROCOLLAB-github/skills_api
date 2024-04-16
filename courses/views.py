from django.db.models import Count, Q, F, Case, When, BooleanField
from drf_spectacular.utils import extend_schema
from rest_framework import generics, status
from rest_framework.response import Response

from courses.mapping import TYPE_TASK_OBJECT
from courses.models import Task, Skill
from courses.serializers import TaskSerializer, SkillsBasicSerializer
from progress.pagination import DefaultPagination
from progress.serializers import ResponseSerializer


class TaskList(generics.ListAPIView):
    serializer_class = TaskSerializer

    @extend_schema(
        summary="Выводит информацию о задаче",
        tags=["Навыки и задачи"],
        responses={200: TaskSerializer},
    )
    def get(self, request, *args, **kwargs):
        task_id = self.kwargs.get("task_id")

        profile_id = 1

        task = Task.objects.prefetch_related("task_objects").get(id=int(task_id))

        task_objects = task.task_objects.annotate(
            has_user_results=Case(
                When(user_results__user_profile__id=profile_id, then=True),
                default=False,
                output_field=BooleanField(),
            )
        ).order_by("ordinal_number")

        data = {"count": task_objects.count(), "step_data": []}
        for task_object in task_objects:
            data["step_data"].append(
                {
                    "id": task_object.id,
                    "type": TYPE_TASK_OBJECT[task_object.content_type.model],
                    "is_done": task_object.has_user_results,
                }
            )

        serializer = self.serializer_class(data=data)
        if serializer.is_valid():
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


# TODO добавить поля для количества навыков
@extend_schema(
    summary="Выводит все навыки на платформе",
    description="""Пока эндпоинт немного пустой, потом будут добавлены поля: who_made, file, 
    description, quantity_of_levels""",
    tags=["Навыки и задачи"],
)
class SkillsList(generics.ListAPIView):
    serializer_class = SkillsBasicSerializer
    pagination_class = DefaultPagination
    queryset = Skill.objects.all()


@extend_schema(
    summary="Выводит подробую информацию о навыке",
    description="""Выводит только тот уровень, который юзер может пройти. Остальные для прохождения закрыты""",
    tags=["Навыки и задачи"],
)
class SkillDetails(generics.ListAPIView):
    serializer_class = ResponseSerializer

    def get(self, request, *args, **kwargs):
        skill_id = self.kwargs.get("skill_id")

        skill = (  # получаем все скиллы у юзера. те, которые он выбрал, и те, которые он пытался решать
            Skill.objects.prefetch_related("profile_skills")
            .filter(id=skill_id)
            .annotate(total_tasks=Count("tasks"))
            .distinct()
            .first()
        )

        tasks = (  # получаем все задачи у скиллов с количеством вопросов и ответов
            Task.objects.select_related("skill")
            .filter(skill=skill)
            .annotate(
                num_questions=Count("task_objects"),
                num_answers=Count("task_objects__user_results"),
            )
            .distinct()
        )

        skill_data = {skill.id: {"skill_name": skill.name}}

        # скилла, для каждого уровня, для каждого уровня, если все задачи решены, то накидываем уровень для скилла

        levels_of_skill = tasks.values_list("level", flat=True).distinct()
        for level in levels_of_skill:
            if "level" not in skill_data[skill.id].keys():
                skill_data[skill.id]["level"] = 1
            # quantity_tasks_of_skill = tasks.filter(level=level, skill=skill).count()
            # quantity_of_done_tasks  = tasks.filter(level=level,skill=skill, num_questions=F("num_answers")).count()

            task_statistics = tasks.filter(level=level, skill=skill).aggregate(
                quantity_tasks_of_skill=Count("id"),
                quantity_of_done_tasks=Count("id", filter=F("num_questions") == F("num_answers")),
            )

            # Извлекаем значение quantity_tasks_of_skill и quantity_of_done_tasks из результата
            total_tasks = task_statistics.get("quantity_tasks_of_skill", 0)
            total_done_tasks = task_statistics.get("quantity_of_done_tasks", 0)

            if total_tasks == total_done_tasks:
                skill_data[skill.id]["level"] += 1

            # if quantity_of_done_tasks == quantity_tasks_of_skill:
            #     skills_data[skill.id]["level"] += 1

        user_skills_ids = [skill.id]

        # проверка прогресса недопройденных навыков
        undone_tasks = tasks.filter(
            ~Q(num_questions=F("num_answers")),
            level=skill_data[skill_id]["level"],
            skill__id=skill_id,
        )
        if skill_id in user_skills_ids:
            quantity_tasks_undone = undone_tasks.count()
            if quantity_tasks_undone:
                progress = (
                    sum(undone_task.num_answers / undone_task.num_questions for undone_task in undone_tasks)
                    / quantity_tasks_undone
                )
                skill_data[skill_id]["progress"] = progress * 100

        data = {"skills": skill_data}
        return Response(data, status=200)
