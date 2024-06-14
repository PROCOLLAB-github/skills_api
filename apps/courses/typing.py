from dataclasses import dataclass


@dataclass
class TaskResultData:
    points_gained: int
    quantity_done_correct: int
    quantity_all: int
    level: int
    progress: int
    skill_name: str
    next_task_id: int | None


@dataclass
class TaskResponseSerializerData:
    id: int
    name: str
    level: int
    status: bool
