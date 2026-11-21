from enum import Enum
from typing import Any, Callable, Optional, List
from dataclasses import dataclass


# JSON Schema type names stored on ToolParameter.type, mapped to Python types.
# bool is a subclass of int, so integer/number are checked separately.
_SCHEMA_TYPE_TO_PYTHON = {
    "string": (str,),
    "boolean": (bool,),
    "integer": (int,),
    "number": (int, float),
    "object": (dict,),
    "array": (list, tuple),
}


class ToolType(Enum):
    QUERY = "query"
    MUTATION = "mutation"
    ACTION = "action"


@dataclass
class ToolParameter:
    name: str
    description: str
    type: str
    required: bool


@dataclass
class ToolSuccessResult:
    data: Any
    success: bool = True


@dataclass
class Tool:
    name: str
    description: str
    tool_type: ToolType
    function: Callable
    parameters: list[ToolParameter]
    success_output_schema: ToolSuccessResult

    def get_parameters_json_schema(self) -> dict:
        """
        Get the JSON schema for the tool parameters.
        """
        return {
            "type": "object",
            "properties": {
                param.name: {
                    "type": param.type,
                    "description": param.description,
                }
                for param in self.parameters
            },
            "required": [param.name for param in self.parameters if param.required],
        }

    def validate_arguments(self, arguments: dict) -> None:
        """
        Validate the tool arguments.
        """

        def _value_matches_schema_type(value: Any, schema_type: str) -> bool:
            expected = _SCHEMA_TYPE_TO_PYTHON.get(schema_type)
            if expected is None:
                raise ValueError(f"Unsupported parameter type {schema_type}")
            # True/False must not count as integer or number.
            if schema_type in {"integer", "number"} and isinstance(value, bool):
                return False
            return isinstance(value, expected)

        for param in self.parameters:
            if param.name not in arguments:
                raise ValueError(f"Argument '{param.name}' is required")
            value = arguments[param.name]
            if not _value_matches_schema_type(value, param.type):
                raise TypeError(
                    f"Argument '{param.name}' must be of type '{param.type}', got '{type(value)}'"
                )


@dataclass
class Schema:
    type: str
    description: Optional[str] = None
    required: Optional[List[str]] = None
    properties: Optional[Schema] = None
