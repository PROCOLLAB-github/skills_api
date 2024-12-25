from django.contrib import admin

from django_summernote.admin import SummernoteModelAdmin

from webinars.models import (
    Webinar,
    WebinarRegistration,
    Speaker,
)


@admin.register(Webinar)
class WebinarAdmin(SummernoteModelAdmin, admin.ModelAdmin):
    list_display = ["id", "title", "datetime_start"]


@admin.register(Speaker)
class SpeakerAdmin(admin.ModelAdmin):
    list_display = ["id", "full_name", "position"]


@admin.register(WebinarRegistration)
class WebinarRegistrationAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "webinar", "datetime_created"]
    list_filter = ["webinar"]
    search_fields = [
        "user__email",
        "user__first_name",
        "user__last_name",
    ]
