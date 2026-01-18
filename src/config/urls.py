from django.contrib import admin
from django.urls import path, include
from twitter.api import health
from rest_framework_simplejwt.views import TokenRefreshView


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/health/", health),
    path("api/accounts/", include("accounts.urls")),
    path("api/token/refresh/", TokenRefreshView.as_view()),

]

