from typing import Any

from app.agent.tools.base import BaseTool, ToolContext, ToolDefinition
from app.agent.tools.mock_images import SearchImagesTool
from app.agent.tools.mock_notebook import ListTopicsTool, SearchMarkdownTool


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, BaseTool] = {}

    def register(self, tool: BaseTool) -> None:
        if not tool.definition.read_only:
            raise ValueError(f"Writable tools are not allowed in this MVP: {tool.definition.name}")
        self._tools[tool.definition.name] = tool

    def list_definitions(self) -> list[ToolDefinition]:
        return [tool.definition for tool in self._tools.values()]

    def run(self, name: str, input_data: dict[str, Any], session_id: str) -> dict[str, Any]:
        tool = self._tools.get(name)
        if not tool:
            raise KeyError(f"Tool not registered: {name}")
        return tool.run(input_data, ToolContext(session_id=session_id))


def build_default_registry() -> ToolRegistry:
    registry = ToolRegistry()
    registry.register(ListTopicsTool())
    registry.register(SearchMarkdownTool())
    registry.register(SearchImagesTool())
    return registry
