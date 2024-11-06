COURSES_ALL_PATHS: list[str] = [
    "/courses/1",
    "/courses/choose-skills/",
    "/courses/skill-details/1",
    "/courses/tasks-of-skill/1",
    "/courses/task-result/1",
    "/courses/all-skills/",
]

COURSES_NO_ACCESS_PATHS: list[str] = [
    "/courses/1",
    "/courses/choose-skills/",
    "/courses/skill-details/1",
    "/courses/tasks-of-skill/1",
    "/courses/task-result/1",
]

COURSES_ACCESS_PATHS: list[str] = [
    "/courses/all-skills/",
]

FULL_FILLED_PUBLISHED_SKILL_RESPONSE_NEW_SUB = {
    "count": 2,
    "current_level": 1,
    "next_level": None,
    "progress": 0,
    "skill_name": "Навык 1",
    "skill_point_logo": "http://some.com/",
    "skill_preview": "http://some.com/",
    "stats_of_weeks": [{"done_on_time": None, "is_done": False, "week": 1}],
    "step_data": [
        {
            "id": 1,
            "is_done": False,
            "ordinal_number": 1,
            "type": "info_slide"
        },
        {
            "id": 2,
            "is_done": False,
            "ordinal_number": 2,
            "type": "info_slide"
        }
    ],
    "tasks": [
        {
            "id": 1,
            "level": 1,
            "name": "Задача 1",
            "status": False,
            "week": 1
        }
    ]
 }
