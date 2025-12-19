"""Protocol definitions for LLM query generators."""

from typing import Mapping, Protocol, runtime_checkable


@runtime_checkable
class QueryGenerator(Protocol):
    """
    Protocol for LLM query generators.

    Implement this with ANY LLM client - OpenAI, Anthropic, Bedrock,
    LangChain, Pydantic-AI, etc. We don't care how you get the result.

    Example implementation with OpenAI:

        class OpenAIGenerator:
            def __init__(self, api_key: str):
                from openai import OpenAI
                self.client = OpenAI(api_key=api_key)

            def generate(self, user_query: str, model_schema: list[dict]) -> dict:
                from django_admin_ai_search import get_system_prompt
                response = self.client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": get_system_prompt(model_schema)},
                        {"role": "user", "content": user_query},
                    ]
                )
                return json.loads(response.choices[0].message.content)
    """

    def generate(self, user_query: str, model_schema: list[dict]) -> Mapping[str, str]:
        """
        Generate ORM query from natural language.

        Args:
            user_query: User's natural language query
            model_schema: Output from get_model_schema() - list of model definitions

        Returns:
            Mapping with required keys:
                - code: Valid Python/Django ORM code
                - explanation: Brief explanation
                - app_label: App label (lowercase)
                - model_name: Model class name (PascalCase)
        """
        ...
