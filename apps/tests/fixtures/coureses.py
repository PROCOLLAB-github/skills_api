import pytest
from model_bakery import baker
from django.contrib.contenttypes.models import ContentType

from courses.models import (
    Task,
    TaskObject,
    Skill,
)
from questions.models.questions import InfoSlide


@pytest.fixture
def skill_wo_tasks(random_file_intance):
    """Просто навык без задач."""
    return baker.make(
        Skill,
        status="published",
        file=random_file_intance,
        skill_preview=random_file_intance,
        skill_point_logo=random_file_intance,
    )


@pytest.fixture
def task_wo_questions(skill_wo_tasks):
    """Задача привязанная к навыку, без заданий."""
    return baker.make(
        Task,
        skill=skill_wo_tasks,
        status="published",
    )


def create_full_skill(random_file_intance, status="published"):
    """
    Полный курс:
        - 4 недели (4 `Task`)
        - 8 задач (по 2 на каждую неделю `TaskObject`)
        - 8 заданий (`InfoSlide` по 1й на каждую задачу)
    """
    skill = Skill(
        name="Навык 1",
        status=status,
        description="Описание",
        who_created="Создатель",
        file=random_file_intance,
        skill_preview=random_file_intance,
        skill_point_logo=random_file_intance,
        quantity_of_levels=4,
    )
    skill.save()

    InfoSlide.objects.bulk_create([
        InfoSlide(
            text=f"Заголовок {idx}",
            description=f"Текст {idx}",
        )
        for idx in range(1, 9)
    ])

    info_slide_content_type = ContentType.objects.get_for_model(InfoSlide)
    tasks_list = []
    task_objects_list = []
    object_id_counter = 1
    for task_idx in range(1, 5):
        task = Task(
            week=task_idx,
            level=task_idx,
            skill=skill,
            status=status,
            ordinal_number=task_idx,
            name=f"Задача {task_idx}",
        )
        tasks_list.append(task)
        for obj_idx in range(1, 3):
            task_object = TaskObject(
                ordinal_number=obj_idx,
                task=task,
                content_type=info_slide_content_type,
                object_id=object_id_counter,
            )
            task_objects_list.append(task_object)
            object_id_counter += 1

    Task.objects.bulk_create(tasks_list)
    TaskObject.objects.bulk_create(task_objects_list)
    return skill


@pytest.fixture
def full_filled_published_skill(random_file_intance):
    skill = create_full_skill(random_file_intance)
    return skill


@pytest.fixture
def full_filled_only_stuff_skill(random_file_intance):
    return create_full_skill(random_file_intance, "stuff_only")


@pytest.fixture
def full_filled_draft_skill(random_file_intance):
    return create_full_skill(random_file_intance, "draft")
