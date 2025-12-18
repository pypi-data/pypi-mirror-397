"""YAML export functions for Django model structure."""

from typing import Any, Dict
import yaml


def normalize_value(value: Any) -> Any:
    """Convert values to proper Python types for YAML export.

    Handles both string representations from AST and already-inferred
    literal values (lists, dicts, etc.).

    Args:
        value: Value to normalize (string or already-inferred type)

    Returns:
        Normalized Python value (bool, int, None, string, list, dict, etc.)

    Example:
        >>> normalize_value("True")
        True
        >>> normalize_value(["active", "Active"])
        ["active", "Active"]
        >>> normalize_value({"key": "value"})
        {"key": "value"}
    """
    # If already a list, recursively normalize elements
    if isinstance(value, list):
        return [normalize_value(item) for item in value]

    # If already a dict, recursively normalize values
    if isinstance(value, dict):
        return {k: normalize_value(v) for k, v in value.items()}

    # If already a primitive type, return as-is
    if isinstance(value, (bool, int, float, type(None))):
        return value

    # Otherwise, treat as string and apply string normalization
    if not isinstance(value, str):
        return value

    value_str = value

    # Handle boolean values
    if value_str == "True":
        return True
    if value_str == "False":
        return False

    # Handle None
    if value_str == "None":
        return None

    # Handle numeric values
    if value_str.isdigit():
        return int(value_str)

    # Try to parse as float
    try:
        if "." in value_str and value_str.replace(".", "").replace("-", "").isdigit():
            return float(value_str)
    except (ValueError, AttributeError):
        pass

    # Strip quotes from strings
    if (value_str.startswith('"') and value_str.endswith('"')) or (
        value_str.startswith("'") and value_str.endswith("'")
    ):
        return value_str[1:-1]

    # Return as-is for complex expressions (e.g., models.CASCADE, timezone.now)
    return value_str


def format_field_options(options_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize field option values for YAML output.

    Args:
        options_dict: Dictionary of field options (strings or inferred values)

    Returns:
        Dictionary with normalized values

    Example:
        >>> format_field_options({'max_length': 100, 'null': False})
        {'max_length': 100, 'null': False}
        >>> format_field_options({'choices': [['a', 'A'], ['b', 'B']]})
        {'choices': [['a', 'A'], ['b', 'B']]}
    """
    normalized = {}
    for key, value in options_dict.items():
        normalized[key] = normalize_value(value)
    return normalized


def format_model_output(model_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Structure model data for YAML output.

    Args:
        model_dict: Raw model dictionary from parser

    Returns:
        Formatted dictionary ready for YAML export

    Example:
        >>> model = {
        ...     'module': 'app.models',
        ...     'abstract': False,
        ...     'table': 'app_user',
        ...     'fields': {'name': {'type': 'CharField', 'max_length': '100'}},
        ...     'relationships': {}
        ... }
        >>> formatted = format_model_output(model)
        >>> formatted['fields']['name']['max_length']
        100
    """
    output = {
        "module": model_dict["module"],
        "abstract": model_dict["abstract"],
    }

    # Add bases field (list of Django Model base classes)
    if "bases" in model_dict:
        output["bases"] = model_dict["bases"]

    # Only include table for concrete models
    if not model_dict["abstract"] and model_dict.get("table"):
        output["table"] = model_dict["table"]

    # Format fields with normalized values
    if model_dict.get("fields"):
        formatted_fields = {}
        for field_name, field_data in model_dict["fields"].items():
            formatted_field = {"type": field_data["type"]}

            # Normalize all options
            for key, value in field_data.items():
                if key != "type":
                    formatted_field[key] = normalize_value(value)

            formatted_fields[field_name] = formatted_field

        output["fields"] = formatted_fields

    # Format relationships with normalized values
    if model_dict.get("relationships"):
        formatted_rels = {}
        for rel_name, rel_data in model_dict["relationships"].items():
            formatted_rel = {}
            for key, value in rel_data.items():
                if isinstance(value, str):
                    formatted_rel[key] = normalize_value(value)
                else:
                    formatted_rel[key] = value
            formatted_rels[rel_name] = formatted_rel

        output["relationships"] = formatted_rels

    return output


def export_to_yaml(models_dict: Dict[str, Dict[str, Any]], output_path: str) -> None:
    """Write models dictionary to YAML file.

    Args:
        models_dict: Dictionary mapping model qualified names to model data
        output_path: Path to output YAML file

    Example:
        >>> models = {
        ...     'app.models.User': {
        ...         'module': 'app.models',
        ...         'abstract': False,
        ...         'fields': {...}
        ...     }
        ... }
        >>> export_to_yaml(models, 'django_models.yaml')
    """
    # Format all models
    formatted_models = {}
    for model_name, model_data in models_dict.items():
        # Skip internal tracking fields
        cleaned_model = {k: v for k, v in model_data.items() if k != "ancestors"}
        formatted_models[model_name] = format_model_output(cleaned_model)

    # Write to YAML with readable formatting
    with open(output_path, "w", encoding="utf-8") as f:
        yaml.safe_dump(
            formatted_models,
            f,
            sort_keys=False,  # Preserve insertion order
            default_flow_style=False,  # Use block style
            allow_unicode=True,
            indent=2,
        )


def export_to_yaml_string(models_dict: Dict[str, Dict[str, Any]]) -> str:
    """Convert models dictionary to YAML string.

    Args:
        models_dict: Dictionary mapping model qualified names to model data

    Returns:
        YAML string representation

    Example:
        >>> models = {'app.models.User': {...}}
        >>> yaml_str = export_to_yaml_string(models)
        >>> print(yaml_str)
        app.models.User:
          module: app.models
          ...
    """
    # Format all models
    formatted_models = {}
    for model_name, model_data in models_dict.items():
        cleaned_model = {k: v for k, v in model_data.items() if k != "ancestors"}
        formatted_models[model_name] = format_model_output(cleaned_model)

    return yaml.safe_dump(
        formatted_models,
        sort_keys=False,
        default_flow_style=False,
        allow_unicode=True,
        indent=2,
    )
