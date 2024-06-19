from django.urls import path

from subscription.views import CreatePayment, ViewSubscriptions, ServeWebHook, CreateRefund

urlpatterns = [
    path("buy/", CreatePayment.as_view()),
    path("", ViewSubscriptions.as_view()),
    path("renew-sub-date", ServeWebHook.as_view()),
    path("refund", CreateRefund.as_view()),
]
