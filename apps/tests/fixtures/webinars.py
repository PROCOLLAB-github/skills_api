from datetime import timedelta

import pytest
from django.utils import timezone

from webinars.models import (
    Webinar,
    Speaker,
)


@pytest.fixture
def webinar_speaker(random_file_intance):
    manager = Speaker.objects.create(
        full_name="Имя Фамилия",
        photo=random_file_intance,
        position="Должность",
    )
    return manager


@pytest.fixture
def actual_webinar(webinar_speaker):
    webinar = Webinar.objects.create(
        title="Акутальный",
        description="Описание",
        datetime_start=timezone.now() + timedelta(hours=1),
        datetime_end=timezone.now() + timedelta(hours=2),
        online_link="https://example1.com",
        recording_link="https://example2.com",
        speaker=webinar_speaker,
    )
    return webinar


@pytest.fixture
def record_webinar(webinar_speaker):
    webinar = Webinar.objects.create(
        title="Запись",
        description="Описание",
        datetime_start=timezone.now() - timedelta(days=1, hours=2),
        datetime_end=timezone.now() - timedelta(days=1, hours=1),
        online_link="https://example3.com",
        recording_link="https://example4.com",
        speaker=webinar_speaker,
    )
    return webinar
