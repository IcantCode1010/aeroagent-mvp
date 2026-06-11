import json
from typing import Any, Literal, TypedDict


StreamEventName = Literal[
    "status",
    "tool_start",
    "tool_done",
    "agent_token",
    "image_result",
    "ui_action",
    "warning",
    "done",
    "error",
]


class StreamEvent(TypedDict):
    event: StreamEventName
    data: dict[str, Any]


def make_event(event: StreamEventName, data: dict[str, Any]) -> StreamEvent:
    return {"event": event, "data": data}


def format_sse(event: StreamEvent) -> str:
    payload = json.dumps(event["data"], separators=(",", ":"))
    return f"event: {event['event']}\ndata: {payload}\n\n"
