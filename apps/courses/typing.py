from dataclasses import dataclass
from typing import TypedDict


@dataclass
class TaskResultData:
    points_gained: int
    quantity_done_correct: int
    quantity_done: int
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
    week: int
    status: bool
    free_access: bool


@dataclass
class PopupSerializerData:
    title: str | None
    text: str | None
    file_link: str | None
    ordinal_number: int


@dataclass
class StatsOfWeeksData:
    week: int
    is_done: bool
    done_on_time: bool | None


@dataclass
class TaskOfSkillProgressSerializerData:
    progress: int
    tasks: list[TaskResponseSerializerData]
    stats_of_weeks: list[StatsOfWeeksData]


class WeekStatsDict(TypedDict):
    week: int
    is_done: bool
    done_on_time: bool | None


class GetStatsDict(TypedDict):
    progress: int
    tasks: list[list | None]
    stats_of_weeks: list[WeekStatsDict | None]
