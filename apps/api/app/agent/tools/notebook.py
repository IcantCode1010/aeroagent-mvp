from typing import Any

from app.agent.notebook_repository import NotebookRepository
from app.agent.tools.base import BaseTool, ToolContext, ToolDefinition


class ListTopicsTool(BaseTool):
    def __init__(self, repository: NotebookRepository) -> None:
        self.repository = repository

    definition = ToolDefinition(
        name="list_topics",
        description="List notebook topics from the configured notebook directory.",
        category="notebook",
        read_only=True,
        permission_level="notebook_read",
        input_schema={"type": "object", "properties": {"query": {"type": "string"}}},
        output_schema={"type": "object", "properties": {"topics": {"type": "array"}}},
    )

    def run(self, input_data: dict[str, Any], context: ToolContext) -> dict[str, Any]:
        return {"topics": [topic.title for topic in self.repository.list_topics()]}


class SearchMarkdownTool(BaseTool):
    def __init__(self, repository: NotebookRepository) -> None:
        self.repository = repository

    definition = ToolDefinition(
        name="search_markdown",
        description="Search Markdown files from the configured notebook directory.",
        category="notebook",
        read_only=True,
        permission_level="notebook_read",
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
        return self.repository.search_markdown(str(input_data.get("query", "")))


class SearchImagesTool(BaseTool):
    def __init__(self, repository: NotebookRepository) -> None:
        self.repository = repository

    definition = ToolDefinition(
        name="search_images",
        description="Search image metadata from the configured notebook directory.",
        category="images",
        read_only=True,
        permission_level="notebook_read",
        input_schema={"type": "object", "properties": {"query": {"type": "string"}}},
        output_schema={"type": "object", "properties": {"images": {"type": "array"}}},
    )

    def run(self, input_data: dict[str, Any], context: ToolContext) -> dict[str, Any]:
        assets = self.repository.search_images(str(input_data.get("query", "")))
        return {"images": [self.repository.image_card(asset) for asset in assets]}
