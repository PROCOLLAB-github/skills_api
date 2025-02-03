from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from webinars.models import Webinar, WebinarRegistration
from webinars.tasks import send_webinar_oline_link_email
from webinars.pagination import DefaultPagination
from webinars.serializers import (
    WebinarActualSerializer,
    WebinarRecordsSerializer,
    WebinarRecordsLinkSerializer,
)
from subscription.permissions import SubscriptionSectionPermission


@extend_schema(
    tags=["Вебинары"],
    summary="Актуальные вебинары",
)
class WebinarActualView(generics.ListAPIView):
    serializer_class = WebinarActualSerializer
    queryset = Webinar.objects.get_actual_webinars()
    pagination_class = DefaultPagination


@extend_schema(
    tags=["Вебинары"],
    summary="Регистрация на вебинар",
    description="При регистрации, ссылка направляется на почту",
)
class WebinarRegistrationView(generics.CreateAPIView):

    def create(self, request, *args, **kwargs):
        webinar: Webinar = self.get_object()
        registration, created = WebinarRegistration.objects.get_or_create(
            user=request.user,
            webinar=webinar,
        )
        if not created:
            return Response(
                {"detail": "Вы уже регистрировались, проверьте почту, там ссылка на вебинар"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        send_webinar_oline_link_email.delay(
            user_email=request.user.email,
            webinar_online_link=webinar.online_link,
            webinar_title=webinar.title,
            webinar_description=webinar.description,
            webinar_datetime=webinar.datetime_start,
        )
        return Response(
            {
                "detail": "Успешная регистрация, письмо с ссылкой отправлено на почту",
            },
            status=status.HTTP_201_CREATED,
        )

    def get_object(self):
        return get_object_or_404(
            Webinar.objects.get_actual_webinars(),
            id=self.kwargs.get("webinar_id"),
        )


@extend_schema(
    tags=["Вебинары"],
    summary="Записи вебинаров",
)
class WebinarRecordsView(generics.ListAPIView):
    serializer_class = WebinarRecordsSerializer
    queryset = Webinar.objects.get_records_webinars()
    pagination_class = DefaultPagination


@extend_schema(
    tags=["Вебинары"],
    summary="Получить ссылку на запись вебинара",
    description="Доступно только с подпиской",
)
class WebinarRecordsLinkView(generics.RetrieveAPIView):
    serializer_class = WebinarRecordsLinkSerializer
    queryset = Webinar.objects.get_records_webinars()
    permission_classes = [IsAuthenticated, SubscriptionSectionPermission]
    lookup_url_kwarg = "webinar_id"
