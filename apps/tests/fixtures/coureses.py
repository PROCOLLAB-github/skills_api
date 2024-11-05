import pytest
from model_bakery import baker

from courses.models import (
    Skill,
    Task,
)


@pytest.fixture
def skill_wo_tasks(random_file_intance):
    """Просто навык без задач."""
    return baker.make(
        Skill,
        id=1,
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
        id=1,
        skill=skill_wo_tasks,
        status="published",
    )
