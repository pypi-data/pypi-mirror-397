"""Tests for the urls module."""

from django.urls import resolve, reverse

from django_admin_ai_search.urls import get_urlpatterns, urlpatterns
from django_admin_ai_search.views import ai_search_page_view, ai_search_view


class TestUrlPatterns:
    """Tests for urlpatterns."""

    def test_urlpatterns_contains_search(self):
        """Should contain the search endpoint."""
        paths = [p.pattern.regex.pattern for p in urlpatterns]
        assert any("search" in p for p in paths)

    def test_search_url_resolves_to_ai_search_view(self):
        """search/ should resolve to ai_search_view."""
        # urlpatterns are used with include("django_admin_ai_search.urls")
        # at admin/ai-search/ prefix, so the full path is admin/ai-search/search/
        resolved = resolve("/admin/ai-search/search/")
        assert resolved.func == ai_search_view


class TestGetUrlPatterns:
    """Tests for get_urlpatterns function."""

    def test_returns_list(self):
        """Should return a list of URL patterns."""
        patterns = get_urlpatterns()
        assert isinstance(patterns, list)

    def test_contains_two_patterns(self):
        """Should contain two patterns (with and without query)."""
        patterns = get_urlpatterns()
        assert len(patterns) == 2

    def test_page_empty_url_resolves(self):
        """admin/search/ should resolve to ai_search_page_view."""
        resolved = resolve("/admin/search/")
        assert resolved.func == ai_search_page_view

    def test_page_with_query_url_resolves(self):
        """admin/search/<query> should resolve to ai_search_page_view."""
        resolved = resolve("/admin/search/find%20users/")
        assert resolved.func == ai_search_page_view

    def test_pattern_names(self):
        """URL patterns should have expected names."""
        patterns = get_urlpatterns()
        names = [p.name for p in patterns]
        assert "admin_ai_search_page_empty" in names
        assert "admin_ai_search_page" in names

    def test_reverse_admin_ai_search_page_empty(self):
        """Should reverse admin_ai_search_page_empty."""
        url = reverse("admin_ai_search_page_empty")
        assert url == "/admin/search/"

    def test_reverse_admin_ai_search_page_with_query(self):
        """Should reverse admin_ai_search_page with query."""
        url = reverse("admin_ai_search_page", kwargs={"query": "find users"})
        assert url == "/admin/search/find%20users"
