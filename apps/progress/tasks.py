from datetime import timedelta

from django.core.cache import cache
from django.db.models import Count, Q, QuerySet

from procollab_skills.celery import app
from courses.models import Skill, Task
from courses.services import get_user_available_week
from progress.constants import MONTHS_CACHING_TIMEOUT
from progress.models import UserProfile, TaskObjUserResult, UserWeekStat, UserSkillDone
from progress.mapping import AdditionalPoints
from progress.services import last_two_months_stats


@app.task
def profile_month_recache():
    user_profiles = UserProfile.objects.values_list("id", flat=True)
    # TODO сделать чтобы у "неактивных" пользователей кэш не обновлялся
    for profile_id in user_profiles:
        months_stats = last_two_months_stats(profile_id)
        cache.set(f"months_data_{profile_id}", months_stats, MONTHS_CACHING_TIMEOUT)


@app.task
def check_week_stat(task_obj_id: int) -> None:
    """Celery Task:
        После сохранения `TaskObjUserResult`, начинается проверка все ли выполнено в рамках недели.
        В результате создается/обновляется запись в `UserWeekStat`.
        Дополнительные баллы начилсяются если все было сделано в срок.
    """
    instance: TaskObjUserResult = TaskObjUserResult.objects.get_wiht_related_fields(task_obj_id)

    task: Task = instance.task_object.task
    skill: Skill = task.skill
    week: int = task.week
    user_profile: UserProfile = instance.user_profile

    available_week: int = get_user_available_week(user_profile.pk)

    tasks_by_week: QuerySet[Task] = (
        Task.published
        .filter(skill__pk=skill.pk, week=week)
        .annotate(
            task_objects_count=Count("task_objects"),  # Общее кол-во вопросов.
            task_objects_done=Count(  # Общее кол-во ответов.
                "task_objects__user_results",
                filter=Q(task_objects__user_results__user_profile_id=user_profile.id),
            ),

        )
    )
    # Проверка, что все задачи каждой Task сделаны.
    all_done: bool = all([task.task_objects_count == task.task_objects_done for task in tasks_by_week])

    # Баллы начисляются только при условии, что все сделано
    # и сделано вовремя (текущая доступная неделя == неделя задания).
    additional_points: int = AdditionalPoints.MONTH.value if (all_done and week == available_week) else 0

    # Создание/Получение записи результата недели.
    obj, created = UserWeekStat.objects.get_or_create(
        user_profile=user_profile,
        skill=skill,
        week=week,
        defaults={"is_done": all_done, "additional_points": additional_points},
    )
    # Если объект ранее был создан.
    if not created:
        obj.additional_points = additional_points
        obj.is_done = all_done
        obj.save()


@app.task
def check_skill_done(task_obj_id: int) -> None:
    """Celery Task:
        После сохранения `TaskObjUserResult`, начинается проверка все ли выполнено в рамках навыка.
        Если выполнено все, то создается запись `UserSkillDone`.
        Дополнительные баллы начилсяются если все было сделано в срок (Ответы в рамках 30 дней подписки).
    """
    instance: TaskObjUserResult = TaskObjUserResult.objects.get_wiht_related_fields(task_obj_id)

    task: Task = instance.task_object.task
    skill: Skill = task.skill
    user_profile: UserProfile = instance.user_profile
    # Данные для проверки ответа вовремя от даты начала подписки, до + 30 дней.
    subscription_date = user_profile.last_subscription_date
    deadline = subscription_date + timedelta(days=30)

    skill: Skill = (
        Skill.published
        .annotate(
            total_num_questions=Count(  # Общее количество заданий.
                "tasks__task_objects",
                filter=(Q(tasks__status="published")),
            ),
            total_user_answers=Count(  # Общее количество ответов.
                "tasks__task_objects__user_results",
                filter=(
                    Q(tasks__task_objects__user_results__user_profile_id=user_profile.id)
                    & Q(tasks__status="published")
                ),
            ),
            timely_responses=Count(  # Количество ответов вовремя.
                "tasks__task_objects__user_results",
                filter=(
                    Q(tasks__task_objects__user_results__user_profile_id=user_profile.id)
                    & Q(tasks__status="published")
                    & Q(tasks__task_objects__user_results__datetime_created__gte=subscription_date)
                    & Q(tasks__task_objects__user_results__datetime_created__lte=deadline)
                ),
            ),
        )
        .get(pk=skill.pk)
    )
    # Навык считается пройденным если сделаны все части задачи, доп. баллы - если сделан вовремя.
    if skill.total_user_answers == skill.total_num_questions:
        additional_points = AdditionalPoints.SKILL.value if skill.total_num_questions == skill.timely_responses else 0
        UserSkillDone.objects.create(
            user_profile=user_profile,
            skill=skill,
            additional_points=additional_points,
        )
