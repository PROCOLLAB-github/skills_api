from django.urls import reverse

ACTUAL_WEBINARS_PATH: str = reverse("webinar-actual")
WEBINAR_REGISTRATION_PATH: str = reverse("webinar-registration", kwargs={"webinar_id": 1})
RECORD_WEBINARS_PATH: str = reverse("webinar-records")
RECORD_LINK_PATH: str = reverse("webinar-record-link", kwargs={"webinar_id": 1})


ALL_GET_PATHS: list[str] = [
    ACTUAL_WEBINARS_PATH,
    RECORD_WEBINARS_PATH,
    RECORD_LINK_PATH,
]

GET_PATHS_WO_SUB: list[str] = [
    ACTUAL_WEBINARS_PATH,
    RECORD_WEBINARS_PATH,
]
