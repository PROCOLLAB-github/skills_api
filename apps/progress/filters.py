import datetime

from django.contrib import admin
from django.db.models import (F, IntegerField, OuterRef, Q, QuerySet, Subquery,
                              Sum, Value)
from django.db.models.functions import Coalesce
from django.utils import timezone
from django_filters import rest_framework as filters

from progress.models import (TaskObjUserResult, UserProfile, UserSkillDone,
                             UserWeekStat)


class UserScoreRatingFilter(filters.FilterSet):
    """Фильтр по указанным навыкам и дню/месяцу/году."""

    time_frame = filters.CharFilter(method="filter_by_time_frame")

    class Meta:
        model = UserProfile
        fields = []

    def filter_by_time_frame(self, queryset: QuerySet[UserProfile], name, value) -> QuerySet[UserProfile]:
        """Фильтрует пользователей на основе временного промежутка | скиллов."""
        time_frame_param: str | None = self.request.query_params.get("time_frame", None)
        skill_names_param: str | None = self.request.query_params.get("skills", None)

        filter_time_frame: Q = self.__get_filter_time_frame(time_frame_param)
        filter_skills: Q = (
            Q(skill__name__in=[skill.strip() for skill in skill_names_param.split(",")])
            if skill_names_param
            else Q()
        )
        filter_related_skills: Q = (
            Q(task_object__task__skill__name__in=[skill.strip() for skill in skill_names_param.split(",")])
            if skill_names_param
            else Q()
        )

        done_user_queryset = (
            queryset
            .annotate(
                skill_done_points=Coalesce(
                    Subquery(
                        self.__get_skill_done_points_subquery(filter_time_frame, filter_skills),
                        output_field=IntegerField()
                    ),
                    Value(0),
                    output_field=IntegerField(),
                ),
                week_done_points=Coalesce(
                    Subquery(
                        self.__get_week_done_points_subquery(filter_time_frame, filter_skills),
                        output_field=IntegerField()
                    ),
                    Value(0),
                    output_field=IntegerField(),
                ),
                task_objects_points=Coalesce(
                    Subquery(
                        self.__get_task_objects_points_subquery(filter_time_frame, filter_related_skills),
                        output_field=IntegerField()
                    ),
                    Value(0),
                    output_field=IntegerField(),
                ),
            )
            .annotate(score_count=F("skill_done_points") + F("week_done_points") + F("task_objects_points"))
            .exclude(score_count=0).order_by("-score_count")
        )
        return done_user_queryset

    def __get_filter_time_frame(self, time_frame_param: str) -> Q:
        timestamps: dict[str, datetime.datetime] = {
            "last_day": timezone.now() - datetime.timedelta(days=1),
            "last_month": timezone.now() - datetime.timedelta(days=30),
            "last_year": timezone.now() - datetime.timedelta(days=365),
        }
        filter_time_frame = (
            Q(datetime_created__gte=timestamps[time_frame_param])
            if time_frame_param in timestamps
            else Q()
        )
        return filter_time_frame

    def __get_skill_done_points_subquery(self, filter_time_frame: Q, filter_skills: Q) -> QuerySet:
        skill_done_points_subquery = (
            UserSkillDone.objects
            .filter(user_profile_id=OuterRef("id"))
            .filter(filter_time_frame & filter_skills)
            .values("user_profile_id")
            .annotate(total_points=Sum("additional_points"))
            .values("total_points")
        )
        return skill_done_points_subquery

    def __get_week_done_points_subquery(self, filter_time_frame: Q, filter_skills: Q) -> QuerySet:
        week_done_points_subquery = (
            UserWeekStat.objects
            .filter(user_profile_id=OuterRef("id"))
            .filter(filter_time_frame & filter_skills)
            .values("user_profile_id")
            .annotate(total_points=Sum("additional_points"))
            .values("total_points")
        )
        return week_done_points_subquery

    def __get_task_objects_points_subquery(self, filter_time_frame: Q, filter_related_skills: Q) -> QuerySet:
        task_objects_points_subquery = (
            TaskObjUserResult.objects
            .filter(user_profile_id=OuterRef("id"))
            .filter(filter_time_frame & filter_related_skills)
            .values("user_profile_id")
            .annotate(total_points=Sum("points_gained"))
            .values("total_points")
        )
        return task_objects_points_subquery


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
            date = timezone.now() - datetime.timedelta(days=30)
            return (
                queryset
                .exclude(last_subscription_date=None)
                .exclude(last_subscription_date__lte=date)
            )
