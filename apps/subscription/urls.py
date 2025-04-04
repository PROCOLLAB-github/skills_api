from django.urls import path

from subscription.views import (CreatePayment, CreateRefund,
                                NotificationWebHook, ViewSubscriptions)

urlpatterns = [
    path("buy/", CreatePayment.as_view()),
    path("", ViewSubscriptions.as_view(), name="view-subscriptions"),
    path("notifications", NotificationWebHook.as_view()),
    path("refund", CreateRefund.as_view()),
]
