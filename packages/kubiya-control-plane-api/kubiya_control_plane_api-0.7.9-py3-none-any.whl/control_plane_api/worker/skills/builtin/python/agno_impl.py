"""Python skill implementation for agno runtime."""
import inspect
from typing import get_type_hints, get_origin, get_args
from agno.tools.python import PythonTools as AgnoPythonTools
from agno.tools.function import Function


class PythonTools(AgnoPythonTools):
    """
    Python code execution using agno PythonTools.

    Wraps agno's PythonTools to provide Python execution with proper parameter schemas.
    """

    def __init__(self, **kwargs):
        """
        Initialize Python tools.

        Args:
            **kwargs: Configuration (enable_code_execution, blocked_imports, etc.)
        """
        super().__init__()
        self.config = kwargs

        # Fix: Rebuild function schemas with proper parameters
        self._rebuild_function_schemas()

    def _rebuild_function_schemas(self):
        """Rebuild function schemas to include proper parameter definitions."""
        if not hasattr(self, 'functions') or not self.functions:
            return

        # Rebuild each function with proper parameter schema
        for func_name, func_obj in list(self.functions.items()):
            try:
                # Get the actual method
                method = getattr(self, func_name, None)
                if not method or not callable(method):
                    continue

                # Extract parameter schema from function signature
                sig = inspect.signature(method)
                type_hints = get_type_hints(method)

                properties = {}
                required = []

                for param_name, param in sig.parameters.items():
                    # Skip 'self'
                    if param_name == 'self':
                        continue

                    # Get type hint
                    param_type = type_hints.get(param_name, str)

                    # Determine JSON schema type
                    json_type = self._python_type_to_json_type(param_type)

                    # Build parameter schema
                    param_schema = {"type": json_type}

                    # Add description from docstring if available
                    if method.__doc__:
                        # Try to extract parameter description from docstring
                        desc = self._extract_param_description(method.__doc__, param_name)
                        if desc:
                            param_schema["description"] = desc

                    properties[param_name] = param_schema

                    # Mark as required if no default value
                    if param.default == inspect.Parameter.empty:
                        required.append(param_name)

                # Update function parameters
                if properties:
                    func_obj.parameters = {
                        "type": "object",
                        "properties": properties,
                        "required": required
                    }

            except Exception as e:
                # Log but don't fail
                print(f"Warning: Could not rebuild schema for {func_name}: {e}")

    @staticmethod
    def _python_type_to_json_type(python_type):
        """Convert Python type hint to JSON schema type."""
        # Handle Optional types
        origin = get_origin(python_type)
        if origin is not None:
            # For Optional, Union, etc., get the non-None type
            args = get_args(python_type)
            if args:
                for arg in args:
                    if arg is not type(None):
                        python_type = arg
                        break

        # Map Python types to JSON schema types
        if python_type == str or python_type == 'str':
            return "string"
        elif python_type == int or python_type == 'int':
            return "integer"
        elif python_type == float or python_type == 'float':
            return "number"
        elif python_type == bool or python_type == 'bool':
            return "boolean"
        elif python_type == list or python_type == 'list':
            return "array"
        elif python_type == dict or python_type == 'dict':
            return "object"
        else:
            return "string"  # Default to string

    @staticmethod
    def _extract_param_description(docstring: str, param_name: str) -> str:
        """Extract parameter description from docstring."""
        if not docstring:
            return ""

        lines = docstring.split('\n')
        for line in lines:
            if f":param {param_name}:" in line:
                # Extract description after ":param param_name:"
                parts = line.split(f":param {param_name}:")
                if len(parts) > 1:
                    return parts[1].strip()

        return ""
