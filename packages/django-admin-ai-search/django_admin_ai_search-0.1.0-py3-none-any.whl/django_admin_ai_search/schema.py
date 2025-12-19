"""Schema extraction from Django admin models."""

from django.contrib import admin


def get_model_schema() -> list[dict]:
    """
    Get schema of all registered admin models.

    Returns a list of model definitions with their fields, suitable for
    passing to an LLM for context about available models.

    Returns:
        List of dicts with keys:
            - app: App label (lowercase)
            - model: Model name (lowercase)
            - model_class: Model class name (PascalCase)
            - verbose_name: Human-readable model name
            - fields: List of field definitions
    """
    schema = []
    for model, _model_admin in admin.site._registry.items():
        model_info = {
            "app": model._meta.app_label,
            "model": model._meta.model_name,
            "model_class": model.__name__,
            "verbose_name": str(model._meta.verbose_name),
            "fields": [],
        }
        for field in model._meta.get_fields():
            field_info = {"name": field.name}
            if hasattr(field, "get_internal_type"):
                field_info["type"] = field.get_internal_type()
            if hasattr(field, "related_model") and field.related_model:
                field_info["related_to"] = (
                    f"{field.related_model._meta.app_label}."
                    f"{field.related_model._meta.model_name}"
                )
            model_info["fields"].append(field_info)
        schema.append(model_info)
    return schema
