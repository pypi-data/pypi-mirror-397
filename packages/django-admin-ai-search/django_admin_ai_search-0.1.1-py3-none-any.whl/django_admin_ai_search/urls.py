"""URL configuration for Django Admin AI Search."""

from django.urls import path

from django_admin_ai_search.views import ai_search_page_view, ai_search_view


def get_urlpatterns():
    """
    Get URL patterns for the AI search feature.

    Add these to your project's urls.py:

        from django_admin_ai_search.urls import get_urlpatterns as get_ai_search_urls

        urlpatterns = [
            path("admin/ai-search/", include("django_admin_ai_search.urls")),
            path("admin/search/", ai_search_page_view, name="admin_ai_search_page_empty"),
            path("admin/search/<path:query>", ai_search_page_view, name="admin_ai_search_page"),
            path("admin/", admin.site.urls),
            # ... other urls
        ]
        urlpatterns += get_ai_search_urls()
    """
    return [
        path(
            "admin/search/",
            ai_search_page_view,
            name="admin_ai_search_page_empty",
        ),
        path(
            "admin/search/<path:query>",
            ai_search_page_view,
            name="admin_ai_search_page",
        ),
    ]


urlpatterns = [
    path("search/", ai_search_view, name="admin_ai_search"),
]
