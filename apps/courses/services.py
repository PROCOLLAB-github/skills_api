from django.db.models import Prefetch, Count, F, Q
from django.shortcuts import get_object_or_404, get_list_or_404

from courses.models import Task, Skill
from progress.models import TaskObjUserResult


def get_stats(skill_id: int, profile_id: int) -> dict:
    tasks_of_skill = get_list_or_404(
        Task.objects.prefetch_related(
            Prefetch(
                "task_objects__user_results",
                queryset=TaskObjUserResult.objects.filter(user_profile_id=profile_id),
                to_attr="filtered_user_results",
            )
        ).prefetch_related("task_objects"),
        skill_id=skill_id,
        skill__status="published",
    )

    data = []

    for task in tasks_of_skill:
        user_results_count = sum(1 for obj in task.task_objects.all() if obj.filtered_user_results)
        data.append(
            {
                "id": task.id,
                "name": task.name,
                "level": task.level,
                "status": user_results_count == task.task_objects.all().count(),
            }
        )

    statuses = (sum(1 for obj in data if obj["status"]) / len(tasks_of_skill)) * 100
    new_data = {"progress": int(statuses), "tasks": data}
    return new_data


def get_skills_details(skill_id: int, user_profile_id: int) -> dict:
    # user_profile_id = UserProfile.objects.get(user_id=self.request.user.id).id

    skill = get_object_or_404(  # получаем все скиллы у юзера. те, которые он выбрал, и те, которые он пытался решать
        Skill.published.select_related("file", "skill_preview", "skill_point_logo")
        .annotate(total_tasks=Count("tasks"))
        .distinct()
        .filter(id=skill_id)
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

    skill_data = {
        skill.id: {
            "skill_name": skill.name,
            "file": skill.file.link if skill.file else None,
            "skill_preview": skill.skill_preview.link if skill.skill_preview else None,
            "skill_point_logo": skill.skill_point_logo.link if skill.skill_point_logo else None,
            "description": skill.description,
        }
    }

    # скилла, для каждого уровня, для каждого уровня, если все задачи решены, то накидываем уровень для скилла

    levels_of_skill = tasks.values_list("level", flat=True).distinct()
    for level in levels_of_skill:
        if "level" not in skill_data[skill.id].keys():
            skill_data[skill.id]["level"] = 0

        task_statistics = tasks.filter(level=level, skill=skill).aggregate(
            quantity_tasks_of_skill=Count("id"),
            quantity_of_done_tasks=Count("id", filter=F("num_questions") == F("num_answers")),
        )

        total_tasks = task_statistics.get("quantity_tasks_of_skill", 0)
        total_done_tasks = task_statistics.get("quantity_of_done_tasks", 0)

        if total_tasks == total_done_tasks:
            skill_data[skill.id]["level"] += 1

    user_skills_ids = [skill.id]

    # проверка прогресса недопройденных навыков
    undone_tasks = tasks.filter(
        ~Q(num_questions=F("num_answers")),
        level=skill_data[skill_id]["level"],
        skill__id=skill_id,
    )
    # raise ValueError(tasks, undone_tasks, skill_data[skill_id]["level"])
    if skill_id in user_skills_ids:
        quantity_tasks_undone = undone_tasks.count()
        if quantity_tasks_undone:
            progress = (
                sum(undone_task.num_answers / undone_task.num_questions for undone_task in undone_tasks)
                / quantity_tasks_undone
            )
            skill_data[skill_id]["progress"] = progress * 100

    first_key = list(skill_data.keys())[0]
    return skill_data[first_key]
