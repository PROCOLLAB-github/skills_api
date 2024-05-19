from django.db.models import Count, F, Q

from courses.models import Skill, Task


def get_skill_level(skill_id: int, user_profile_id: int) -> dict:
    skill = (  # получаем все скиллы у юзера. те, которые он выбрал, и те, которые он пытался решать
        Skill.objects.prefetch_related("profile_skills")
        .filter(
            Q(profile_skills__id=user_profile_id)
            | Q(tasks__task_objects__user_results__user_profile__id=user_profile_id)
            | Q(id=skill_id)
        )
        .annotate(total_tasks=Count("tasks"))
        .distinct()
        .first()
    )

    tasks = (  # получаем все задачи у скиллов с количеством вопросов и ответов
        Task.objects.select_related("skill")
        .filter(skill=skill)
        .annotate(
            num_questions=Count("task_objects"),
            num_answers=Count(
                "task_objects__user_results", filter=Q(task_objects__user_results__user_profile__id=user_profile_id)
            ),
        )
        .distinct()
    )

    skill_data = {skill.id: {"skill_name": skill.name}}

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

    return skill_data
