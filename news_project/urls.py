"""Define project-level routes for admin, API, and newsroom pages."""

from django.contrib import admin
from django.urls import include, path
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/token/', obtain_auth_token, name='api-token'),
    path('api/', include('news.api_urls')),
    path('', include('news.urls')),
]
