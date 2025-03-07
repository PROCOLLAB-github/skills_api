from django.db.models import Manager, QuerySet
from django.utils import timezone


class WebinarManager(Manager):

    def get_actual_webinars(self) -> QuerySet:
        return super().get_queryset().filter(
            datetime_end__gte=timezone.now()
        )

    def get_records_webinars(self) -> QuerySet:
        return super().get_queryset().filter(
            datetime_end__lte=timezone.localtime()
        )
