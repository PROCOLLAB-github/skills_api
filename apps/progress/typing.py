from typing import TypedDict

from progress.models import UserProfile


UserSkillsProgress = dict[UserProfile, list[bool]]


class UserProfileDataDict(TypedDict):
    first_name: str
    last_name: str
    file_link: str | None
    specialization: str | None
    age: int | None
    geo_position: str | None
    points: int | None


class UserSkillsProgressDict(TypedDict):
    skill_id: int
    skill_name: str
    skill_level: int
    skill_progress: int


class UserMonthsProgressDict(TypedDict):
    month: str
    year: int
    successfully_done: bool


class PreparatoryUserMonthsProgressDict(UserMonthsProgressDict):
    month: int
