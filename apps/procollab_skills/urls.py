from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView


from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from django.conf.urls.static import static
from procollab_skills import settings

urlpatterns = [
    path("admin/", admin.site.urls),
    path('summernote/', include('django_summernote.urls')),
    path('editor/', include('django_summernote.urls')),
    # docs
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="docs"),
    # auth
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    # apps
    path("courses/", include("courses.urls")),
    path("questions/", include("questions.urls")),
    path("progress/", include("progress.urls")),
    path("subscription/", include("subscription.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
