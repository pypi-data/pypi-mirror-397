"""Tests for the prompt module."""

from django_admin_ai_search.prompt import get_system_prompt


class TestGetSystemPrompt:
    """Tests for get_system_prompt."""

    def test_returns_string(self):
        """Should return a string."""
        schema = [{"app": "auth", "model_class": "User", "fields": ["id", "email"]}]
        prompt = get_system_prompt(schema)
        assert isinstance(prompt, str)

    def test_contains_schema(self):
        """Should contain the provided schema."""
        schema = [{"app": "auth", "model_class": "User", "fields": ["id", "email"]}]
        prompt = get_system_prompt(schema)
        # The schema should be JSON-encoded in the prompt
        assert '"app": "auth"' in prompt
        assert '"model_class": "User"' in prompt

    def test_contains_safety_rules(self):
        """Should contain safety rules about read-only queries."""
        schema = [{"app": "auth", "model_class": "User", "fields": ["id"]}]
        prompt = get_system_prompt(schema)
        assert "READ-ONLY" in prompt
        assert ".update()" in prompt
        assert ".delete()" in prompt
        assert ".create()" in prompt
        assert ".save()" in prompt

    def test_contains_limit_rule(self):
        """Should contain rule about 50 item limit."""
        schema = []
        prompt = get_system_prompt(schema)
        assert "50" in prompt

    def test_contains_apps_get_model_instruction(self):
        """Should instruct to use apps.get_model."""
        schema = []
        prompt = get_system_prompt(schema)
        assert "apps.get_model" in prompt

    def test_contains_json_response_format(self):
        """Should specify JSON response format."""
        schema = []
        prompt = get_system_prompt(schema)
        assert '"code"' in prompt
        assert '"explanation"' in prompt
        assert '"app_label"' in prompt
        assert '"model_name"' in prompt

    def test_with_empty_schema(self):
        """Should work with an empty schema."""
        prompt = get_system_prompt([])
        assert isinstance(prompt, str)
        assert "[]" in prompt

    def test_with_multiple_models(self):
        """Should include all models in schema."""
        schema = [
            {"app": "auth", "model_class": "User", "fields": ["id", "email"]},
            {"app": "auth", "model_class": "Group", "fields": ["id", "name"]},
        ]
        prompt = get_system_prompt(schema)
        assert "User" in prompt
        assert "Group" in prompt
