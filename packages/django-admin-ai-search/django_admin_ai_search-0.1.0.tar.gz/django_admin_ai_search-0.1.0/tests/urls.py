"""URL configuration for tests."""

from django.contrib import admin
from django.urls import include, path

from django_admin_ai_search.urls import get_urlpatterns as get_ai_search_urls

urlpatterns = [
    path("admin/ai-search/", include("django_admin_ai_search.urls")),
    path("admin/", admin.site.urls),
]

urlpatterns += get_ai_search_urls()
