import datetime
from datetime import timedelta

from django_filters import rest_framework as filters
from django.contrib import admin
from django.utils import timezone
from django.db.models import Sum, Q, QuerySet, F

from progress.models import UserProfile


class UserScoreRatingFilter(filters.FilterSet):
    """Фильтр по указанным навыкам и дню/месяцу/году."""

    time_frame = filters.CharFilter(method="filter_by_time_frame")

    class Meta:
        model = UserProfile
        fields = []

    def filter_by_time_frame(self, queryset, name, value) -> QuerySet[UserProfile]:
        """Фильтрует пользователей на основе временного промежутка."""
        values: dict[str, datetime.datetime] = {
            "last_day": timezone.now() - datetime.timedelta(days=1),
            "last_month": timezone.now() - datetime.timedelta(days=30),
            "last_year": timezone.now() - datetime.timedelta(days=365),
        }

        time_frame_param: str = self.request.query_params.get("time_frame", None)
        skill_names_param: str = self.request.query_params.get("skills", None)

        filter_time_frame = (
            Q(task_obj_results__datetime_created__gte=values[time_frame_param])
            if time_frame_param
            else Q()  # If time_frame_param is None, an empty Q object is used
        )
        filter_skills = (
            Q(chosen_skills__name__in=[skill.strip() for skill in skill_names_param.split(",")])
            if skill_names_param
            else Q()  # If time_frame_param is None, an empty Q object is used
        )

        done_user_queryset = queryset.annotate(
            score_count=Sum(
                "task_obj_results__points_gained",
                filter=filter_skills & filter_time_frame,
            )
        ).distinct()

        return done_user_queryset.exclude(score_count__isnull=True).order_by("-score_count")


class AdminUserSubscriptionFilter(admin.SimpleListFilter):
    title = ("Подписка")
    parameter_name = "subscribtion"

    def lookups(self, request, model_admin):
        return [
            ("all_subscribers", "Все кто имел подписку"),
            ("only_active", "Только активные подписки"),
        ]

    def queryset(self, request, queryset):
        if self.value() == "all_subscribers":
            return queryset.exclude(last_subscription_date=None)
        if self.value() == "only_active":
            date = timezone.now() - timedelta(days=30)
            print(date)
            return (
                queryset
                .exclude(last_subscription_date=None)
                .exclude(last_subscription_date__lte=date)
            )
