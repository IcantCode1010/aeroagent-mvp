import json
import os
from dataclasses import dataclass
from typing import Any, Protocol


class ModelClient(Protocol):
    def generate(self, message: str, tool_name: str, tool_result: dict[str, Any]) -> str | None:
        ...


@dataclass(frozen=True)
class ModelConfig:
    api_key: str | None = None
    model: str = "gpt-5.5"
    base_url: str | None = None

    @classmethod
    def from_env(cls) -> "ModelConfig":
        return cls(
            api_key=os.environ.get("OPENAI_API_KEY") or None,
            model=os.environ.get("OPENAI_MODEL") or "gpt-5.5",
            base_url=os.environ.get("OPENAI_BASE_URL") or None,
        )

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key)


class OpenAIModelClient:
    SYSTEM_INSTRUCTIONS = (
        "You are AeroAgent, a read-only aviation notebook assistant. "
        "Answer from the provided notebook context only. "
        "If the context is insufficient, say what notebook source is missing. "
        "Do not invent maintenance procedures, regulatory guidance, or safety steps."
    )

    def __init__(self, config: ModelConfig | None = None, openai_client: Any | None = None) -> None:
        self.config = config or ModelConfig.from_env()
        self._openai_client = openai_client

    def generate(self, message: str, tool_name: str, tool_result: dict[str, Any]) -> str | None:
        if not self.config.is_configured:
            return None

        client = self._openai_client or self._build_client()
        response = client.responses.create(
            model=self.config.model,
            instructions=self.SYSTEM_INSTRUCTIONS,
            input=self._build_input(message, tool_name, tool_result),
        )
        return str(response.output_text).strip()

    def _build_client(self) -> Any:
        from openai import OpenAI

        kwargs: dict[str, str] = {"api_key": self.config.api_key or ""}
        if self.config.base_url:
            kwargs["base_url"] = self.config.base_url
        return OpenAI(**kwargs)

    def _build_input(self, message: str, tool_name: str, tool_result: dict[str, Any]) -> str:
        context = json.dumps(tool_result, ensure_ascii=False)
        return (
            f"User request: {message}\n\n"
            f"Tool used: {tool_name}\n\n"
            "Read-only notebook context:\n"
            f"{context}"
        )
