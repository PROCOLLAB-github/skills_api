from django.urls import path

from webinars.views import (WebinarActualView, WebinarRecordsLinkView,
                            WebinarRecordsView, WebinarRegistrationView)

urlpatterns = [
    path(
        "actual/",
        WebinarActualView.as_view(),
        name="webinar-actual",
    ),
    path(
        "actual/<int:webinar_id>/",
        WebinarRegistrationView.as_view(),
        name="webinar-registration",
    ),
    path(
        "records/",
        WebinarRecordsView.as_view(),
        name="webinar-records",
    ),
    path(
        "records/<int:webinar_id>/link/",
        WebinarRecordsLinkView.as_view(),
        name="webinar-record-link",
    ),
]
