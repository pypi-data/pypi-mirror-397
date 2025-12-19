"""Core search execution service."""

import hashlib
import logging
import traceback

from django.apps import apps
from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ImproperlyConfigured
from django.utils.module_loading import import_string

from django_admin_ai_search.protocols import QueryGenerator
from django_admin_ai_search.schema import get_model_schema

logger = logging.getLogger(__name__)

REQUIRED_KEYS = ("code", "explanation", "app_label", "model_name")


def get_config(key: str, default=None):
    """Get configuration value from Django settings."""
    config = getattr(settings, "DJANGO_ADMIN_AI_SEARCH", {})
    return config.get(key, default)


def get_generator() -> QueryGenerator:
    """
    Get the configured query generator.

    The generator must be configured in Django settings:

        DJANGO_ADMIN_AI_SEARCH = {
            'GENERATOR': 'myapp.generators.MyGenerator',
            # or an instance:
            'GENERATOR': MyGeneratorInstance,
        }

    Raises:
        ImproperlyConfigured: If GENERATOR is not configured
    """
    generator = get_config("GENERATOR")

    if generator is None:
        raise ImproperlyConfigured(
            "DJANGO_ADMIN_AI_SEARCH['GENERATOR'] must be configured. "
            "Provide a QueryGenerator implementation."
        )

    if isinstance(generator, str):
        generator_class = import_string(generator)
        # If it's a class, instantiate it
        if isinstance(generator_class, type):
            generator = generator_class()
        else:
            generator = generator_class

    return generator


def get_cache_key(query: str) -> str:
    """Generate a cache key for a search query."""
    query_hash = hashlib.md5(query.lower().strip().encode()).hexdigest()
    prefix = get_config("CACHE_PREFIX", "django_admin_ai_search")
    return f"{prefix}:{query_hash}"


def execute_search(user_query: str, use_cache: bool = True) -> dict:
    """
    Execute AI-powered search and return results.

    Args:
        user_query: Natural language search query
        use_cache: Whether to use cached results (default: True)

    Returns:
        Dict with keys:
            - success: bool
            - query: Original query
            - code: Generated ORM code
            - explanation: What the query does
            - results: Query results as list of dicts
            - columns: Column names for display
            - count: Number of results
            - app_label: App label of queried model
            - model_name: Model class name
            - from_cache: Whether result was from cache
            - error: Error message (if success=False)
    """
    cache_timeout = get_config("CACHE_TIMEOUT", 3600)
    cache_key = get_cache_key(user_query)

    # Check cache first
    if use_cache:
        cached_result = cache.get(cache_key)
        if cached_result:
            cached_result["from_cache"] = True
            return cached_result

    try:
        generator = get_generator()
        schema = get_model_schema()

        # Generate ORM query using the configured generator
        result = generator.generate(user_query, schema)

        # Validate required keys
        missing = [k for k in REQUIRED_KEYS if k not in result]
        if missing:
            raise ValueError(f"Generator response missing required keys: {missing}")

        code = result["code"]

        # Execute the generated code
        local_vars = {"apps": apps}
        exec(code, {"apps": apps, "__builtins__": __builtins__}, local_vars)

        # Get the result from the last expression
        lines = [line for line in code.strip().split("\n") if line.strip()]
        last_line = lines[-1] if lines else ""

        exec(
            f"__result__ = {last_line}",
            {"apps": apps, "__builtins__": __builtins__, **local_vars},
            local_vars,
        )

        results = local_vars.get("__result__", [])

        if hasattr(results, "__iter__") and not isinstance(results, (list, dict)):
            results = list(results)

        # Extract columns from results
        columns = []
        if results and isinstance(results, list) and len(results) > 0:
            first_result = results[0]
            if isinstance(first_result, dict):
                # Ensure 'id' is first if present
                keys = list(first_result.keys())
                if "id" in keys:
                    keys.remove("id")
                    columns = ["id"] + keys
                else:
                    columns = keys

        response = {
            "success": True,
            "query": user_query,
            "code": code,
            "explanation": result["explanation"],
            "results": results,
            "columns": columns,
            "count": len(results) if isinstance(results, list) else 1,
            "app_label": result["app_label"],
            "model_name": result["model_name"],
            "from_cache": False,
        }

        # Cache the successful result
        if use_cache and cache_timeout > 0:
            cache.set(cache_key, response, timeout=cache_timeout)

        return response

    except Exception as e:
        logger.exception(f"Error executing AI search: {e}")
        return {
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc(),
            "results": [],
            "from_cache": False,
        }
