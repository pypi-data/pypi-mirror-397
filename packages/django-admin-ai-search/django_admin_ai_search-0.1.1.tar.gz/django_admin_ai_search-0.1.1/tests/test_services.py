"""Tests for the services module."""

import pytest
from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ImproperlyConfigured

from django_admin_ai_search.protocols import QueryGenerator
from django_admin_ai_search.schema import get_model_schema
from django_admin_ai_search.services import (
    execute_search,
    get_cache_key,
    get_config,
    get_generator,
)


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


class TestGetConfig:
    """Tests for get_config."""

    def test_returns_configured_value(self):
        """Should return configured value."""
        # GENERATOR is configured in test settings
        assert get_config("GENERATOR") is not None

    def test_returns_default_for_missing_key(self):
        """Should return default for missing key."""
        assert get_config("NONEXISTENT_KEY") is None
        assert get_config("NONEXISTENT_KEY", "default") == "default"

    def test_returns_default_cache_timeout(self):
        """Should return default cache timeout."""
        # CACHE_TIMEOUT is not configured, should use default
        timeout = get_config("CACHE_TIMEOUT", 3600)
        assert timeout == 3600


class TestGetGenerator:
    """Tests for get_generator."""

    def test_returns_generator(self):
        """Should return configured generator."""
        generator = get_generator()
        assert isinstance(generator, QueryGenerator)

    def test_raises_when_not_configured(self, monkeypatch):
        """Should raise ImproperlyConfigured when GENERATOR not set."""
        monkeypatch.setattr(settings, "DJANGO_ADMIN_AI_SEARCH", {})
        with pytest.raises(ImproperlyConfigured) as exc:
            get_generator()
        assert "GENERATOR" in str(exc.value)

    def test_imports_string_path_to_class(self, monkeypatch):
        """Should import and instantiate generator class from string path."""
        monkeypatch.setattr(
            settings,
            "DJANGO_ADMIN_AI_SEARCH",
            {"GENERATOR": "tests.settings.MockGenerator"},
        )
        generator = get_generator()
        assert isinstance(generator, QueryGenerator)

    def test_imports_string_path_to_instance(self, monkeypatch):
        """Should import generator instance from string path."""
        monkeypatch.setattr(
            settings,
            "DJANGO_ADMIN_AI_SEARCH",
            {"GENERATOR": "tests.settings.mock_generator_instance"},
        )
        generator = get_generator()
        assert isinstance(generator, QueryGenerator)


class TestGetCacheKey:
    """Tests for get_cache_key."""

    def test_returns_string(self):
        """Should return a string cache key."""
        key = get_cache_key("test query")
        assert isinstance(key, str)

    def test_includes_prefix(self):
        """Should include default prefix."""
        key = get_cache_key("test query")
        assert key.startswith("django_admin_ai_search:")

    def test_same_query_same_key(self):
        """Same query should produce same key."""
        key1 = get_cache_key("find users")
        key2 = get_cache_key("find users")
        assert key1 == key2

    def test_different_query_different_key(self):
        """Different queries should produce different keys."""
        key1 = get_cache_key("find users")
        key2 = get_cache_key("find groups")
        assert key1 != key2

    def test_case_insensitive(self):
        """Query should be case insensitive."""
        key1 = get_cache_key("Find Users")
        key2 = get_cache_key("find users")
        assert key1 == key2

    def test_strips_whitespace(self):
        """Should strip whitespace."""
        key1 = get_cache_key("  find users  ")
        key2 = get_cache_key("find users")
        assert key1 == key2


class TestExecuteSearch:
    """Tests for execute_search."""

    def setup_method(self):
        """Clear cache before each test."""
        cache.clear()

    def test_returns_success_dict(self):
        """Should return success dict with expected keys."""
        result = execute_search("test query")
        assert result["success"] is True
        assert "results" in result
        assert "code" in result
        assert "explanation" in result

    def test_returns_from_cache_true_when_not_cached(self):
        """Should return from_cache=False for fresh query."""
        result = execute_search("unique query 1")
        assert result["from_cache"] is False

    def test_returns_cached_result(self):
        """Should return cached result on second call."""
        query = "cached query test"
        # First call - not cached
        result1 = execute_search(query)
        assert result1["from_cache"] is False

        # Second call - should be cached
        result2 = execute_search(query)
        assert result2["from_cache"] is True

    def test_use_cache_false_skips_cache(self):
        """Should skip cache when use_cache=False."""
        query = "skip cache query"
        # First call
        execute_search(query)

        # Second call with cache disabled
        result = execute_search(query, use_cache=False)
        assert result["from_cache"] is False

    def test_handles_missing_required_keys(self, monkeypatch):
        """Should return error when generator response missing keys."""

        class BadGenerator:
            def generate(self, user_query, model_schema):
                return {
                    "code": "list([])"
                }  # Missing explanation, app_label, model_name

        monkeypatch.setattr(
            settings,
            "DJANGO_ADMIN_AI_SEARCH",
            {"GENERATOR": BadGenerator()},
        )
        result = execute_search("test query", use_cache=False)
        assert result["success"] is False
        assert "missing required keys" in result["error"]

    def test_handles_generator_exception(self, monkeypatch):
        """Should return error when generator raises exception."""

        class ErrorGenerator:
            def generate(self, user_query, model_schema):
                raise ValueError("Generator error")

        monkeypatch.setattr(
            settings,
            "DJANGO_ADMIN_AI_SEARCH",
            {"GENERATOR": ErrorGenerator()},
        )
        result = execute_search("test query", use_cache=False)
        assert result["success"] is False
        assert "Generator error" in result["error"]

    def test_handles_code_execution_error(self, monkeypatch):
        """Should return error when code execution fails."""

        class BadCodeGenerator:
            def generate(self, user_query, model_schema):
                return {
                    "code": "raise ValueError('bad code')",
                    "explanation": "test",
                    "app_label": "auth",
                    "model_name": "User",
                }

        monkeypatch.setattr(
            settings,
            "DJANGO_ADMIN_AI_SEARCH",
            {"GENERATOR": BadCodeGenerator()},
        )
        result = execute_search("test query", use_cache=False)
        assert result["success"] is False
        assert "bad code" in result["error"]

    def test_converts_iterator_to_list(self, monkeypatch):
        """Should convert iterator result to list."""

        class IteratorGenerator:
            def generate(self, user_query, model_schema):
                return {
                    "code": "(x for x in [1, 2, 3])",
                    "explanation": "test",
                    "app_label": "auth",
                    "model_name": "User",
                }

        monkeypatch.setattr(
            settings,
            "DJANGO_ADMIN_AI_SEARCH",
            {"GENERATOR": IteratorGenerator()},
        )
        result = execute_search("test query", use_cache=False)
        assert result["success"] is True
        assert result["results"] == [1, 2, 3]

    def test_extracts_columns_from_dict_results(self, monkeypatch):
        """Should extract columns from dict results with id first."""

        class DictGenerator:
            def generate(self, user_query, model_schema):
                return {
                    "code": "[{'name': 'Alice', 'id': 1, 'email': 'a@test.com'}]",
                    "explanation": "test",
                    "app_label": "auth",
                    "model_name": "User",
                }

        monkeypatch.setattr(
            settings,
            "DJANGO_ADMIN_AI_SEARCH",
            {"GENERATOR": DictGenerator()},
        )
        result = execute_search("test query", use_cache=False)
        assert result["success"] is True
        assert result["columns"][0] == "id"
        assert "name" in result["columns"]
        assert "email" in result["columns"]

    def test_extracts_columns_without_id(self, monkeypatch):
        """Should extract columns when no id field."""

        class NoIdGenerator:
            def generate(self, user_query, model_schema):
                return {
                    "code": "[{'name': 'Alice', 'email': 'a@test.com'}]",
                    "explanation": "test",
                    "app_label": "auth",
                    "model_name": "User",
                }

        monkeypatch.setattr(
            settings,
            "DJANGO_ADMIN_AI_SEARCH",
            {"GENERATOR": NoIdGenerator()},
        )
        result = execute_search("test query", use_cache=False)
        assert result["success"] is True
        assert result["columns"] == ["name", "email"]

    def test_returns_empty_columns_for_empty_results(self, monkeypatch):
        """Should return empty columns for empty results."""

        class EmptyGenerator:
            def generate(self, user_query, model_schema):
                return {
                    "code": "[]",
                    "explanation": "test",
                    "app_label": "auth",
                    "model_name": "User",
                }

        monkeypatch.setattr(
            settings,
            "DJANGO_ADMIN_AI_SEARCH",
            {"GENERATOR": EmptyGenerator()},
        )
        result = execute_search("test query", use_cache=False)
        assert result["success"] is True
        assert result["columns"] == []

    def test_returns_count(self):
        """Should return count of results."""
        result = execute_search("test query")
        assert "count" in result
        assert isinstance(result["count"], int)


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
