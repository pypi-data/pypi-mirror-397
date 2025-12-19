"""Django settings for tests."""

SECRET_KEY = "test-secret-key-not-for-production"

INSTALLED_APPS = [
    "django_admin_ai_search",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

ROOT_URLCONF = "tests.urls"

USE_TZ = True

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}


class MockGenerator:
    """Mock generator for tests."""

    def generate(self, user_query: str, model_schema: list[dict]) -> dict:
        return {
            "code": "list([])",
            "explanation": "Mock query",
            "app_label": "auth",
            "model_name": "User",
        }


DJANGO_ADMIN_AI_SEARCH = {
    "GENERATOR": MockGenerator(),
}
