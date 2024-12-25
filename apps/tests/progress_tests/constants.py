from django.urls import reverse
from django.utils import timezone

# All `progress` url paths:
REGISTRATION_PATH: str = reverse("registration")
USER_PROFILE_PATH: str = reverse("user-profile")
SUBSCRIBTION_USER_DATA_PATH: str = reverse("subscribtion-user-data")
ADD_SKILLS_PATH: str = reverse("add-skills")
USER_SCORE_RATING_PATH: str = reverse("user-score-rating")
SKILL_RATING_PATH: str = reverse("skill-rating")
UPDATE_AUTO_RENEWAL_PATH: str = reverse("update-auto-renewal")
# Не тестируется, запрос на внешний сервис:
USER_DATA_PATH: str = reverse("user-data")


PROGRESS_NO_ACCESS_PATHS: list[str] = [
    USER_PROFILE_PATH,
    SUBSCRIBTION_USER_DATA_PATH,
    ADD_SKILLS_PATH,
    USER_SCORE_RATING_PATH,
    SKILL_RATING_PATH,
    UPDATE_AUTO_RENEWAL_PATH,
]


PROGRESS_NO_ACCESS_GET_PATHS: list[str] = [
    USER_PROFILE_PATH,
    SUBSCRIBTION_USER_DATA_PATH,
    USER_SCORE_RATING_PATH,
    SKILL_RATING_PATH,
]


CORRECT_REGISTRATION_DATA = {
  "email": "user@example.com",
  "password": "password",
  "first_name": "Юзер",
  "last_name": "Юзер"
}


INCORRECT_REGISTRATION_DATA = {
  "email": "example.com",
  "password": "",
  "first_name": "User",
  "last_name": "User"
}


REGISTRATION_RESPONSE_DATA = {
  "id": 1,
  "email": "user@example.com",
  "first_name": "Юзер",
  "last_name": "Юзер"
}


PROGRESS_USER_PROFILE_RESPONSE = {
    "user_data": {
        "first_name": "Юзер",
        "last_name": "Юзер",
        "file_link": "http://some.com/",
        "specialization": "Специальность",
        "age": 24 + (timezone.now().year - 2024),
        "geo_position": "Москва",
        "points": 0
    },
    "skills": [],
    "months": []
}
