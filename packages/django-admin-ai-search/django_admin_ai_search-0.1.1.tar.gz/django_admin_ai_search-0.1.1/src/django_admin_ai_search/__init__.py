"""Django Admin AI Search - Natural language search for Django Admin."""

__version__ = "0.1.1"

from django_admin_ai_search.prompt import get_system_prompt
from django_admin_ai_search.protocols import QueryGenerator
from django_admin_ai_search.schema import get_model_schema

__all__ = [
    "QueryGenerator",
    "get_model_schema",
    "get_system_prompt",
]
