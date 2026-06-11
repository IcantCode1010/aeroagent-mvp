from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ToolDefinition:
    name: str
    description: str
    category: str
    read_only: bool
    permission_level: str
    input_schema: dict[str, Any]
    output_schema: dict[str, Any]


@dataclass(frozen=True)
class ToolContext:
    session_id: str


class BaseTool(ABC):
    definition: ToolDefinition

    @abstractmethod
    def run(self, input_data: dict[str, Any], context: ToolContext) -> dict[str, Any]:
        raise NotImplementedError
