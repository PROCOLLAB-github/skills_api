from django.urls import reverse

# All `courses` url paths:
TASK_LIST_PATH: str = reverse("task_list", kwargs={"task_id": 1})
ALL_SKILLS_PATH: str = reverse("all-skills")
CHOOSE_SKILLS_PATH: str = reverse("choose-skills")
SKILL_DETAILS_PATH: str = reverse("skill-details", kwargs={"skill_id": 1})
TASK_RESULT: str = reverse("task-result", kwargs={"task_id": 1})
TASKS_OF_SKILL: str = reverse("tasks-of-skill", kwargs={"skill_id": 1})


COURSES_ALL_PATHS: list[str] = [
    TASK_LIST_PATH,
    ALL_SKILLS_PATH,
    CHOOSE_SKILLS_PATH,
    SKILL_DETAILS_PATH,
    TASKS_OF_SKILL,
    TASK_RESULT,
]


COURSES_NO_ACCESS_PATHS: list[str] = [
    TASK_LIST_PATH,
    CHOOSE_SKILLS_PATH,
    SKILL_DETAILS_PATH,
    TASKS_OF_SKILL,
    TASK_RESULT,
]


COURSES_ACCESS_PATHS: list[str] = [
    ALL_SKILLS_PATH,
]


# Tasks только для stuff(в фикстуре статус должен быть указан)
TASKS_PATH_STUFF_ONLY = [
    TASK_LIST_PATH,
    TASK_RESULT,
]


# Response по /courses/1:
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


# Response по /courses/all-skills/:
ALL_SKILLS_RESPONSE_NEW_SUB = {
    "count": 1,
    "next": None,
    "previous": None,
    "results": [
        {
            "id": 1,
            "name": "Навык 1",
            "who_created": "Создатель",
            "file_link": "http://some.com/",
            "quantity_of_levels": 1,
            "description": "Описание"
        }
    ]
}


# Response по /courses/choose-skills/:
CHOOSE_SKILLS_RESPONSE_NEW_SUB = {
    "count": 1,
    "next": None,
    "previous": None,
    "results": [
        {
            "id": 1,
            "name": "Навык 1",
            "who_created": "Создатель",
            "file_link": "http://some.com/",
            "quantity_of_levels": 1,
            "description": "Описание",
            "is_done": False
        }
    ]
}


# Response по /courses/skill-details/1:
SKILL_DETAILS_RESPONSE_NEW_SUB = {
    "skill_name": "Навык 1",
    "file": "http://some.com/",
    "skill_preview": "http://some.com/",
    "skill_point_logo": "http://some.com/",
    "description": "Описание",
    "level": 1
}


# Response по /courses/task-result/1:
TASK_RESULT_RESPONSE_NEW_SUB = {
  "points_gained": 0,
  "quantity_done_correct": 0,
  "quantity_all": 2,
  "level": 1,
  "progress": 0,
  "skill_name": "Навык 1",
  "next_task_id": None
}


# Response по /courses/tasks-of-skill/1:
TASKS_OF_SKILL_RESPONSE_NEW_SUB = {
  "progress": 0,
  "tasks": [
    {
      "id": 1,
      "name": "Задача 1",
      "level": 1,
      "week": 1,
      "status": False
    }
  ],
  "stats_of_weeks": [
    {
      "week": 1,
      "is_done": False,
      "done_on_time": None
    }
  ]
}
