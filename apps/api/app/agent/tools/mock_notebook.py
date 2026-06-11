from typing import Any

from app.agent.tools.base import BaseTool, ToolContext, ToolDefinition


TOPICS = ["APU", "Hydraulics", "Electrical"]


class ListTopicsTool(BaseTool):
    definition = ToolDefinition(
        name="list_topics",
        description="List mock notebook topics.",
        category="notebook",
        read_only=True,
        permission_level="public_mock",
        input_schema={"type": "object", "properties": {"query": {"type": "string"}}},
        output_schema={"type": "object", "properties": {"topics": {"type": "array"}}},
    )

    def run(self, input_data: dict[str, Any], context: ToolContext) -> dict[str, Any]:
        return {"topics": TOPICS}


class SearchMarkdownTool(BaseTool):
    definition = ToolDefinition(
        name="search_markdown",
        description="Search mock notebook Markdown text.",
        category="notebook",
        read_only=True,
        permission_level="public_mock",
        input_schema={"type": "object", "properties": {"query": {"type": "string"}}},
        output_schema={
            "type": "object",
            "properties": {
                "answer": {"type": "string"},
                "source": {"type": "string"},
            },
        },
    )

    def run(self, input_data: dict[str, Any], context: ToolContext) -> dict[str, Any]:
        query = str(input_data.get("query", "")).strip() or "your request"
        return {
            "answer": (
                "Mock notebook search found a starter APU note. "
                f"This placeholder response is grounded in mock data for: {query}."
            ),
            "source": "mock://notebooks/aircraft-systems/topics/apu/apu.md",
        }
