from django.urls import path

from subscription.views import CreatePayment, ViewSubscriptions, NotificationWebHook, CreateRefund

urlpatterns = [
    path("buy/", CreatePayment.as_view()),
    path("", ViewSubscriptions.as_view()),
    path("notifications", NotificationWebHook.as_view()),
    path("refund", CreateRefund.as_view()),
]
