from dataclasses import dataclass
from enum import Enum
from typing import Annotated

WEEK_BEGIN_DAYS: tuple[int, int, int, int] = (1, 7, 14, 21)
StrDateType = Annotated[str, "date in format of '%Y-%m-%d'"]


class AdditionalPointsTypes(Enum):
    WEEK_DONE = 10
    MONTH_DONE = 30


@dataclass(frozen=True)
class TaskDates:
    begin_date: StrDateType
    end_date: StrDateType


@dataclass(frozen=True)
class AdditionalPointsParams:
    points_added_to: int
    task_obj_id: int
    user_profile_id: int
