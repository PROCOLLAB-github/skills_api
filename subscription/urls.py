from django.urls import path

from subscription.views import CreatePayment, ViewSubscriptions

urlpatterns = [path("buy", CreatePayment.as_view()), path("", ViewSubscriptions.as_view())]
