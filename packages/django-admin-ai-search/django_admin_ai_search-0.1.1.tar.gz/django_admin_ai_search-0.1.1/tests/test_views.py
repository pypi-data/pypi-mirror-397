"""Tests for the views module."""

import json

import pytest
from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse


@pytest.fixture
def staff_user(db):
    """Create a staff user for testing."""
    return User.objects.create_user(
        username="staffuser",
        password="testpass123",
        is_staff=True,
    )


@pytest.fixture
def regular_user(db):
    """Create a regular (non-staff) user for testing."""
    return User.objects.create_user(
        username="regularuser",
        password="testpass123",
        is_staff=False,
    )


@pytest.fixture
def authenticated_client(staff_user):
    """Return a client logged in as staff user."""
    client = Client()
    client.login(username="staffuser", password="testpass123")
    return client


@pytest.fixture
def unauthenticated_client():
    """Return an unauthenticated client."""
    return Client()


class TestAISearchView:
    """Tests for ai_search_view."""

    def test_successful_search(self, authenticated_client):
        """Should return success response for valid query."""
        response = authenticated_client.post(
            reverse("admin_ai_search"),
            data=json.dumps({"query": "find all users"}),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "results" in data

    def test_empty_query_returns_error(self, authenticated_client):
        """Should return error for empty query."""
        response = authenticated_client.post(
            reverse("admin_ai_search"),
            data=json.dumps({"query": ""}),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert data["error"] == "Query is required"

    def test_whitespace_query_returns_error(self, authenticated_client):
        """Should return error for whitespace-only query."""
        response = authenticated_client.post(
            reverse("admin_ai_search"),
            data=json.dumps({"query": "   "}),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert data["error"] == "Query is required"

    def test_missing_query_key_returns_error(self, authenticated_client):
        """Should return error when query key is missing."""
        response = authenticated_client.post(
            reverse("admin_ai_search"),
            data=json.dumps({}),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert data["error"] == "Query is required"

    def test_invalid_json_returns_error(self, authenticated_client):
        """Should return error for invalid JSON."""
        response = authenticated_client.post(
            reverse("admin_ai_search"),
            data="not valid json",
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert data["error"] == "Invalid JSON"

    def test_requires_staff_authentication(self, unauthenticated_client):
        """Should redirect unauthenticated users."""
        response = unauthenticated_client.post(
            reverse("admin_ai_search"),
            data=json.dumps({"query": "test"}),
            content_type="application/json",
        )
        # staff_member_required redirects to admin login
        assert response.status_code == 302

    def test_non_staff_user_redirected(self, regular_user):
        """Should redirect non-staff users."""
        client = Client()
        client.login(username="regularuser", password="testpass123")
        response = client.post(
            reverse("admin_ai_search"),
            data=json.dumps({"query": "test"}),
            content_type="application/json",
        )
        assert response.status_code == 302

    def test_get_method_not_allowed(self, authenticated_client):
        """Should reject GET requests."""
        response = authenticated_client.get(reverse("admin_ai_search"))
        assert response.status_code == 405

    def test_general_exception_returns_error(self, authenticated_client, monkeypatch):
        """Should return error for general exceptions."""
        from django_admin_ai_search import views

        def raise_error(query):
            raise RuntimeError("Unexpected error")

        monkeypatch.setattr(views, "execute_search", raise_error)
        response = authenticated_client.post(
            reverse("admin_ai_search"),
            data=json.dumps({"query": "test"}),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "Unexpected error" in data["error"]


class TestAISearchPageView:
    """Tests for ai_search_page_view."""

    def test_renders_page_without_query(self, authenticated_client):
        """Should render the admin index page without query."""
        response = authenticated_client.get(reverse("admin_ai_search_page_empty"))
        assert response.status_code == 200

    def test_renders_page_with_query(self, authenticated_client):
        """Should render the admin index page with query in URL."""
        response = authenticated_client.get("/admin/search/find%20users/")
        assert response.status_code == 200

    def test_requires_staff_authentication(self, unauthenticated_client):
        """Should redirect unauthenticated users."""
        response = unauthenticated_client.get(reverse("admin_ai_search_page_empty"))
        assert response.status_code == 302
