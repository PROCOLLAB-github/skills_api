import calendar
from datetime import timedelta

from django.db import transaction
from django.utils import timezone
from django.db.models import Count, Q, QuerySet

from procollab_skills.celery import app
from courses.models import Skill, Task
from progress.mapping import AdditionalPoints
from progress.typing import UserSkillsProgress
from progress.services import (
    DBObjectStatusFilters,
    get_user_available_week,
)
from progress.models import (
    UserProfile,
    TaskObjUserResult,
    UserWeekStat,
    UserSkillDone,
    UserMonthTarget,
    UserMonthStat,
)


@app.task
def check_week_stat(task_obj_id: int) -> None:
    """Celery Task:
        После сохранения `TaskObjUserResult`, начинается проверка все ли выполнено в рамках недели.
        В результате создается/обновляется запись в `UserWeekStat`.
        Дополнительные баллы начилсяются если все было сделано в срок.
        Бесплатные Task не дают баллы.
    """
    instance: TaskObjUserResult = TaskObjUserResult.objects.get_with_related_fields(task_obj_id)

    task: Task = instance.task_object.task
    skill: Skill = task.skill
    week: int = task.week
    user_profile: UserProfile = instance.user_profile

    available_week, _ = get_user_available_week(user_profile.pk)

    tasks_by_week: QuerySet[Task] = (
        Task.objects
        .filter(skill__pk=skill.pk, week=week)
        .annotate(
            task_objects_count=Count("task_objects", distinct=True),  # Общее кол-во вопросов.
            task_objects_done=Count(  # Общее кол-во ответов.
                "task_objects__user_results",
                filter=Q(task_objects__user_results__user_profile_id=user_profile.id),
            ),

        )
    )
    # Проверка, что все задачи каждой Task сделаны.
    all_done: bool = all((task.task_objects_count == task.task_objects_done for task in tasks_by_week))

    # Баллы начисляются только при условии, что все сделано
    # и сделано вовремя (текущая доступная неделя == неделя задания).
    if user_profile.user.is_superuser or user_profile.user.is_staff:
        additional_points: int = AdditionalPoints.MONTH.value
    elif task.free_access:
        additional_points: int = 0
    else:
        additional_points: int = AdditionalPoints.MONTH.value if (all_done and week == available_week) else 0

    # Создание/Обновление записи результата недели.
    UserWeekStat.objects.update_or_create(
        user_profile=user_profile,
        skill=skill,
        week=week,
        defaults={"is_done": all_done, "additional_points": additional_points},
    )


@app.task
def check_skill_done(task_obj_id: int) -> None:
    """Celery Task:
        После сохранения `TaskObjUserResult`, начинается проверка все ли выполнено в рамках навыка.
        Если выполнено все, то создается запись `UserSkillDone`.
        Дополнительные баллы начилсяются если все было сделано в срок (Ответы в рамках 30 дней подписки).
        Бесплатные Skill не дают баллы.
    """
    instance: TaskObjUserResult = TaskObjUserResult.objects.get_with_related_fields(task_obj_id)

    task: Task = instance.task_object.task
    skill: Skill = task.skill
    user_profile: UserProfile = instance.user_profile
    # Данные для проверки ответа вовремя от даты начала подписки, до + 30 дней.
    subscription_date = user_profile.last_subscription_date if user_profile.last_subscription_date else timezone.now()
    deadline = subscription_date + timedelta(days=30) if subscription_date else timezone.now()

    task_status_filter = DBObjectStatusFilters().get_many_tasks_status_filter_for_user(user_profile.user)

    skill: Skill = (
        Skill.published
        .for_user(user_profile.user)
        .annotate(
            total_num_questions=Count(  # Общее количество заданий.
                "tasks__task_objects",
                filter=task_status_filter,
                distinct=True,
            ),
            total_user_answers=Count(  # Общее количество ответов.
                "tasks__task_objects__user_results",
                filter=(
                    task_status_filter
                    & Q(tasks__task_objects__user_results__user_profile_id=user_profile.id)
                ),
            ),
            timely_responses=Count(  # Количество ответов вовремя.
                "tasks__task_objects__user_results",
                filter=(
                    task_status_filter
                    & Q(tasks__task_objects__user_results__user_profile_id=user_profile.id)
                    & Q(tasks__task_objects__user_results__datetime_created__gte=subscription_date)
                    & Q(tasks__task_objects__user_results__datetime_created__lte=deadline)
                ),
            ),
        )
        .get(pk=skill.pk)
    )
    # Навык считается пройденным если сделаны все части задачи, доп. баллы - если сделан вовремя.
    # Для `superuser` и `staff` таймлайн не учитывается.
    if skill.total_user_answers == skill.total_num_questions:
        if user_profile.user.is_superuser or user_profile.user.is_staff:
            additional_points = AdditionalPoints.SKILL.value
        elif skill.free_access:
            additional_points: int = 0
        else:
            additional_points = (
                AdditionalPoints.SKILL.value if skill.total_num_questions == skill.timely_responses else 0
            )
        UserSkillDone.objects.update_or_create(
            user_profile=user_profile,
            skill=skill,
            defaults={"additional_points": additional_points},
        )


@app.task
@transaction.atomic
def create_user_monts_target(user_profile_id: int) -> None:
    """Celery Task:
        После сохранения `UserProfile` если дата подписки изменилась (т.е. пользователь подписался или переподписался),
        формируются цели на текущий месяц, если конец подписки уходит на след. месяц то и на след. месяц.
        Цели формируются исходя из кол-ва дней до конца текущего месяца:
            - Если до конца месяца(30 дней) 10 дней, то цель == 33% к концу месяца.
            - Если пользователь в предыдущем месяце выбрал и не завершил навык, но при этом в текущем месяце взял его 
              вновь, то его цель обновляется, до актуальной для текущего месяца. 
    """
    user_profile = UserProfile.objects.get(pk=user_profile_id)
    # Если у пользователя просто слетела подписка или ее не было, дальше ехать нет смысла.
    if not user_profile.last_subscription_date:
        return

    deadline = user_profile.last_subscription_date + timedelta(days=30)
    current_year: int = user_profile.last_subscription_date.year
    current_month: int = user_profile.last_subscription_date.month
    current_day: int = user_profile.last_subscription_date.day
    next_month: int = 1 if current_month == 12 else current_month + 1
    next_month_year: int = current_year + 1 if current_month == 12 else current_year
    _, last_day = calendar.monthrange(current_year, current_month)
    days_until_end_month = (last_day - current_day) + 1  # Дней до конца месяца (включая текущий).

    percentag_complete: int = int((days_until_end_month / last_day) * 100)  # Остаток отбрасывается.

    # user_skills = user_profile.chosen_skills.all()
    # TODO: ↑ вариант, когда будут скиллы только по выбору, логика ↓ будет не нужна.
    user_skills = Skill.published.for_user(user_profile.user)
    user_done_skills = UserSkillDone.objects.filter(user_profile=user_profile).values("skill__id")
    user_skills = user_skills.exclude(id__in=user_done_skills)  # Исключение тех навыков, которые завершены.

    for skill in user_skills:
        # Если пользователь выбирает один и тот же навык, и ранее он его не завершил,
        # то его цель на текущий месяц обновляется, если подобной цели не было -> создается.
        UserMonthTarget.objects.update_or_create(
            user_profile=user_profile,
            month=current_month,
            year=current_year,
            skill=skill,
            defaults={"percentage_of_completion": percentag_complete},
        )
        # Если подписка выходит за рамки текущего месяца, то формируется еще 1 запись на след. месяц.
        # цель на след. месяц == полный комплит навыка (100%).
        if deadline.month != current_month:
            UserMonthTarget.objects.update_or_create(
                user_profile=user_profile,
                month=next_month,
                year=next_month_year,
                skill=skill,
                defaults={"percentage_of_completion": 100},
            )


@app.task
@transaction.atomic
def monthly_check_user_goals() -> None:
    """Celery-beat Task:
        Задача заведена на 1 день месяца. Проверяются цели за предыдущий месяц `UserMonthTarget` 
        и записывается статистика за месяц `UserMonthStat`.
        Булевый флаг `successfully_done` для `UserMonthStat` завсит от выполнения цели в %.
    """
    now = timezone.now()
    previous_month: int = now.month - 1 if now.month > 1 else 12  # Предыдущий месяц.
    previous_year: int = now.year if now.month > 1 else now.year - 1  # Предыдущий год (если мы проверям в янв.).

    # Цели пользователей за прошлый месяц.
    users_targets: QuerySet[UserMonthTarget] = (
        UserMonthTarget.objects
        .select_related("user_profile", "skill")
        .filter(month=previous_month, year=previous_year)
    )
    user_skills_data: UserSkillsProgress = {}
    # Перебор целей для формирования словаря с информацией по комплиту запланированных навыков.
    for user_target in users_targets:
        task_status_filter = (
            DBObjectStatusFilters()
            .get_many_tasks_status_filter_for_user(user_target.user_profile.user)
        )
        try:
            skill: Skill = (
                Skill.published
                .for_user(user_target.user_profile.user)
                .annotate(
                    total_num_questions=Count("tasks__task_objects", filter=task_status_filter),
                    total_user_answers=Count(
                        "tasks__task_objects__user_results",
                        filter=(
                            task_status_filter
                            & Q(tasks__task_objects__user_results__user_profile_id=user_target.user_profile.id)
                        ),
                    ),
                )
                .get(id=user_target.skill.id)
            )
            skill_percentage = (  # На всякий случай проверка, чтобы все не упало при кривом заполнении навыков.
                int((skill.total_user_answers / skill.total_num_questions) * 100)
                if skill.total_num_questions > 0 else 100
            )
            # Ключом словаря является профиль, значение - список с булевыми значениями выполнена цель/нет.
            (user_skills_data.setdefault(user_target.user_profile, [])
             .append(skill_percentage >= user_target.percentage_of_completion))
        except Skill.DoesNotExist:
            # Ситуация, когда удалили/скрыли навык, а цель была сформирована.
            pass

    # Перебор профилей и результата по скиллам, формируются статистика за предыдущий месяц.
    # В идеале bulk_create, но мы на проде шаффлим подписки, транзакция может не пройти.
    for user_profile, skills_results in user_skills_data.items():
        UserMonthStat.objects.update_or_create(
            year=previous_year,
            month=previous_month,
            user_profile=user_profile,
            defaults={'successfully_done': all(skills_results)},
        )
    # Ранее отфильтрованные цели за прошлый месяц удаляются (больше не нужны).
    users_targets.delete()
