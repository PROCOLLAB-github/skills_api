import datetime

from django.db.models import Q, Count, F, Case, When, BooleanField

from courses.models import Skill, Task
from progress.mapping import MonthMapping
from progress.models import UserProfile, TaskObjUserResult
from questions.mapping import TaskObjs


def get_user_data(profile_id: int) -> dict:
    user_profile = (
        UserProfile.objects.select_related("user", "file").prefetch_related("chosen_skills").get(id=profile_id)
    )
    # TODO добавить сериалайзер
    user = user_profile.user

    years_passed = None
    if user.age:
        current_date = datetime.datetime.now()
        time_difference = current_date - user.age.replace(tzinfo=None)
        years_passed = time_difference.days // 365

    return {
        "first_name": user.first_name,
        "last_name": user.last_name,
        "file_link": user_profile.file.link if user_profile.file else None,
        "specialization": user.specialization,
        "age": years_passed,
        "geo_position": user.geo_position,
    }


def months_passed_data() -> tuple[datetime.date, datetime.date]:
    today = datetime.date.today()
    first = today.replace(day=1)
    last_month = first - datetime.timedelta(days=1)

    sec = last_month.replace(day=1)
    last_last_month = sec - datetime.timedelta(days=1)

    return last_last_month, last_month


def get_current_level(user_profile_id: int) -> dict:
    """Выдаёт наиболее маленький непройденный уровень у всех скиллов пользователя"""
    user_skills = (  # получаем все скиллы у юзера. те, которые он выбрал, и те, которые он пытался решать
        Skill.objects.prefetch_related("profile_skills")
        .filter(
            Q(profile_skills__id=user_profile_id)
            | Q(tasks__task_objects__user_results__user_profile__id=user_profile_id)
        )
        .annotate(total_tasks=Count("tasks"))
        .distinct()
    )

    tasks = (  # получаем все задачи у скиллов с количеством вопросов и ответов
        Task.objects.select_related("skill")
        .filter(skill__in=user_skills)
        .annotate(
            num_questions=Count("task_objects"),
            num_answers=Count(
                "task_objects__user_results", filter=Q(task_objects__user_results__user_profile__id=user_profile_id)
            ),
            is_done=Case(When(num_questions=F("num_answers"), then=True), default=False, output_field=BooleanField()),
        )
        .distinct()
    )

    skills_data = {skill.id: {"skill_name": skill.name} for skill in user_skills}

    # скилла, для каждого уровня, для каждого уровня, если все задачи решены, то накидываем уровень для скилла
    for skill in user_skills:
        levels_of_skill = tasks.values_list("level", flat=True).distinct()
        for level in levels_of_skill:
            if "level" not in skills_data[skill.id].keys():
                skills_data[skill.id]["level"] = 1

            task_statistics = tasks.filter(level=level, skill=skill).aggregate(
                quantity_tasks_of_skill=Count("id"),
                quantity_of_done_tasks=Count("id", filter=Q(is_done=True)),
            )

            # Извлекаем значение quantity_tasks_of_skill и quantity_of_done_tasks из результата
            total_tasks = task_statistics.get("quantity_tasks_of_skill", 0)
            total_done_tasks = task_statistics.get("quantity_of_done_tasks", 0)

            if total_tasks == total_done_tasks:
                skills_data[skill.id]["level"] += 1

    user_skills_ids = user_skills.filter(profile_skills__id=user_profile_id).values_list("id", flat=True)

    # проверка прогресса недопройденных навыков
    for skill_id, value in skills_data.items():
        undone_tasks = tasks.filter(~Q(num_questions=F("num_answers")), level=value["level"], skill__id=skill_id)
        if skill_id in user_skills_ids:
            quantity_tasks_undone = undone_tasks.count()
            if quantity_tasks_undone:
                progress = (
                    sum(undone_task.num_answers / undone_task.num_questions for undone_task in undone_tasks)
                    / quantity_tasks_undone
                )
                skills_data[skill_id]["progress"] = progress * 100

    return skills_data


def last_two_months_stats(user_profile_id: int) -> list[dict]:
    user_skills = (  # получаем все скиллы у юзера. те, которые он выбрал, и те, которые он пытался решать
        Skill.objects.prefetch_related("profile_skills")
        .filter(
            Q(profile_skills__id=user_profile_id)
            | Q(tasks__task_objects__user_results__user_profile__id=user_profile_id)
        )
        .annotate(total_tasks=Count("tasks"))
        .distinct()
    )
    # TODO do something with reused code
    tasks = (  # получаем все задачи у скиллов с количеством вопросов и ответов
        Task.objects.select_related("skill")
        .filter(skill__in=user_skills)
        .annotate(
            num_questions=Count("task_objects"),
            num_answers=Count("task_objects__user_results"),
            is_done=Case(When(num_questions=F("num_answers"), then=True), default=False, output_field=BooleanField()),
        )
        .distinct()
    )

    months = months_passed_data()  # получаем два предыдущих месяца
    if user_skills.count() == 0:
        data = [{"month": MonthMapping[month.month], "is_passed": False} for month in months]
        return data

    months_data = []

    # навыки, у которых пройден один уровень за месяц.
    for month in months:
        months_counter = 0
        for skill in user_skills:
            levels_of_skill = tasks.values_list("level", flat=True).distinct()
            for level in levels_of_skill:
                task_statistics = (
                    tasks.prefetch_related("task_objects")
                    .filter(level=level, skill=skill)
                    .aggregate(
                        num_questions=Count("task_objects"),
                        num_answers_of_month=Count(
                            "task_objects__user_results",
                            filter=Q(
                                task_objects__user_results__datetime_created__gte=month.replace(day=1),
                                task_objects__user_results__datetime_created__lte=month,
                            ),
                        ),
                    )
                )

                # Извлекаем значение quantity_tasks_of_skill и quantity_of_done_tasks из результата
                total_tasks = task_statistics.get("num_questions", 0)
                total_done_tasks = task_statistics.get("num_answers_of_month", 0)

                if total_tasks == total_done_tasks:
                    months_counter += 1

        months_data.append({"month": MonthMapping[month.month], "is_passed": months_counter == user_skills.count()})

    return months_data


def check_if_answered_get(task_obj_id: int, user_profile_id: int, type_task_obj: TaskObjs) -> TaskObjUserResult | None:
    return TaskObjUserResult.objects.filter(
        task_object_id=task_obj_id,
        user_profile_id=user_profile_id,
        points_gained=type_task_obj.value,
    ).first()


def create_user_result(task_obj_id: int, user_profile_id: int, type_task_obj: TaskObjs):
    TaskObjUserResult.objects.create(
        task_object_id=task_obj_id,
        user_profile_id=user_profile_id,
        points_gained=type_task_obj.value,
    )