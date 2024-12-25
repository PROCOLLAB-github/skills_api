from django.utils import timezone
from django.db.models import Manager, QuerySet


class WebinarManager(Manager):

    def get_actual_webinars(self) -> QuerySet:
        return super().get_queryset().filter(
            datetime_end__gte=timezone.now()
        )

    def get_records_webinars(self) -> QuerySet:
        return super().get_queryset().filter(
            datetime_end__lte=timezone.localtime()
        )
