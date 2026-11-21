from typing import Any, Callable, Dict, List, Optional
from schema.tool import (
    Schema,
    Tool,
    ToolParameter,
    ToolSuccessResult,
    ToolType,
)
from utils.tools import wrap_tool_result


class ToolRegistry:
    def __init__(self) -> None:
        """
        Initialize the tool registry.
        """
        self._tools: Dict[str, Tool] = {}

    def register(
        self,
        *,
        description: Optional[str],
        tool_type: ToolType,
        parameters: Optional[list[ToolParameter]],
        return_type: Schema,
    ) -> None:
        """
        Register a tool with the tool registry.
        """

        def decorator(func: Callable) -> None:
            tool_name = func.__name__
            tool_description = description or func.__doc__
            tool_parameters = parameters or []

            if tool_name in self._tools:
                raise ValueError(
                    f"Tool {tool_name} already registered. Please use a different name."
                )

            tool = Tool(
                name=tool_name,
                description=tool_description,
                tool_type=tool_type,
                function=func,
                parameters=tool_parameters,
                success_output_schema=ToolSuccessResult(data=return_type),
            )

            self._tools[tool_name] = tool
            return wrap_tool_result(func)

        return decorator

    def get_all_tools(self) -> List[Tool]:
        """
        Get all tools from the tool registry.
        """
        return list[Tool](self._tools.values())

    def get_tool(self, name: str) -> Tool:
        """
        Get a tool from the tool registry.
        """
        if name not in self._tools:
            raise ValueError(
                f"Tool {name} not found. Please register the tool first or verify the tool name."
                f"For available tools, please use the get_all_tools method."
            )

        return self._tools[name]

    def call(self, name: str, **kwargs: Any) -> Any:
        """
        Call a tool from the tool registry.
        """
        tool = self.get_tool(name)
        return tool.function(**kwargs)
