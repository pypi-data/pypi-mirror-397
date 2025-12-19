"""Schema generation utilities for actions."""

import inspect
import json
from typing import Callable


def generate_schema_from_signature(func: Callable) -> str:
    """Generate a JSON schema from a function's type hints.

    Args:
        func: The function to generate schema from

    Returns:
        JSON string representing the input schema
    """
    sig = inspect.signature(func)
    properties = {}
    required = []

    type_map = {
        str: "string",
        int: "integer",
        float: "number",
        bool: "boolean",
        list: "array",
        dict: "object",
    }

    for name, param in sig.parameters.items():
        if name == "self":
            continue

        param_type = "string"  # Default to string
        if param.annotation != inspect.Parameter.empty:
            if param.annotation in type_map:
                param_type = type_map[param.annotation]
            # Handle Optional, List, etc. later if needed

        properties[name] = {"type": param_type}

        if param.default == inspect.Parameter.empty:
            required.append(name)

    schema = {
        "type": "object",
        "properties": properties,
    }
    if required:
        schema["required"] = required

    return json.dumps(schema)
