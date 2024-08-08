from progress.models import UserProfile


SkillProgressType = dict[str, object]
SkillIdType = int
SkillMonthProgressType = dict[str, bool]
UserSkillsProgress = dict[UserProfile, list[bool]]
