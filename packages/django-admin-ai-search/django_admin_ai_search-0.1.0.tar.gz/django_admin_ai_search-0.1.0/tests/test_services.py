"""Tests for the services module."""

import pytest
from django.core.exceptions import ImproperlyConfigured

from django_admin_ai_search.protocols import QueryGenerator
from django_admin_ai_search.schema import get_model_schema
from django_admin_ai_search.services import execute_search, get_generator


class TestGetModelSchema:
    """Tests for get_model_schema."""

    def test_returns_list(self):
        """Schema should be a list."""
        schema = get_model_schema()
        assert isinstance(schema, list)

    def test_includes_auth_models(self):
        """Should include Django auth models."""
        schema = get_model_schema()
        app_labels = {m["app"] for m in schema}
        assert "auth" in app_labels


class TestGetGenerator:
    """Tests for get_generator."""

    def test_returns_generator(self):
        """Should return configured generator."""
        generator = get_generator()
        assert isinstance(generator, QueryGenerator)


class TestExecuteSearch:
    """Tests for execute_search."""

    def test_returns_success_dict(self):
        """Should return success dict with expected keys."""
        result = execute_search("test query")
        assert result["success"] is True
        assert "results" in result
        assert "code" in result
        assert "explanation" in result


class TestQueryGeneratorProtocol:
    """Tests for QueryGenerator protocol."""

    def test_mock_generator_matches_protocol(self):
        """Mock generator should match protocol."""

        class TestGenerator:
            def generate(self, user_query: str, model_schema: list[dict]) -> dict:
                return {
                    "code": "list([])",
                    "explanation": "test",
                    "app_label": "auth",
                    "model_name": "User",
                }

        gen = TestGenerator()
        assert isinstance(gen, QueryGenerator)
