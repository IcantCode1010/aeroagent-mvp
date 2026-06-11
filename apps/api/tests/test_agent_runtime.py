import json
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

API_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(API_ROOT))

from app.agent.planner import Planner
from app.agent.runtime import AgentRuntime
from app.agent.tool_registry import ToolRegistry, build_default_registry
from app.main import create_app


def collect_events(lines: list[str]) -> list[tuple[str, dict]]:
    events: list[tuple[str, dict]] = []
    current_event: str | None = None

    for line in lines:
        if line.startswith("event: "):
            current_event = line.removeprefix("event: ").strip()
        elif line.startswith("data: ") and current_event:
            events.append((current_event, json.loads(line.removeprefix("data: "))))
            current_event = None

    return events


@pytest.mark.parametrize(
    ("message", "tool_name"),
    [
        ("show me apu images", "search_images"),
        ("do you have a picture of apu bleed air", "search_images"),
        ("list topics", "list_topics"),
        ("what does the apu do", "search_markdown"),
    ],
)
def test_planner_selects_expected_mock_tool(message: str, tool_name: str) -> None:
    assert Planner().plan(message).tool_name == tool_name


def test_default_registry_exposes_read_only_mock_tools() -> None:
    registry = build_default_registry()

    definitions = registry.list_definitions()
    assert {definition.name for definition in definitions} == {
        "list_topics",
        "search_markdown",
        "search_images",
    }
    assert all(definition.read_only for definition in definitions)

    topic_result = registry.run("list_topics", {"query": "list topics"}, session_id="demo")
    assert topic_result["topics"] == ["APU", "Hydraulics", "Electrical"]

    image_result = registry.run("search_images", {"query": "show me apu images"}, session_id="demo")
    assert [image["imageId"] for image in image_result["images"]] == [
        "apu_generator",
        "apu_bleed_air",
    ]


def test_registry_rejects_missing_tools() -> None:
    registry = ToolRegistry()

    with pytest.raises(KeyError, match="Tool not registered: missing_tool"):
        registry.run("missing_tool", {}, session_id="demo")


def test_agent_runtime_streams_typed_image_events() -> None:
    runtime = AgentRuntime(registry=build_default_registry(), planner=Planner())

    events = list(runtime.stream("show me apu images", session_id="demo"))
    event_names = [event["event"] for event in events]

    assert event_names == [
        "status",
        "tool_start",
        "tool_done",
        "image_result",
        "image_result",
        "ui_action",
        "agent_token",
        "done",
    ]
    assert events[3]["data"]["imageId"] == "apu_generator"
    assert events[5]["data"] == {
        "type": "open_image",
        "payload": {"imageId": "apu_generator"},
    }
    assert "I found 2 mock image references" in events[6]["data"]["text"]


def test_agent_stream_endpoint_returns_sse_events() -> None:
    client = TestClient(create_app())

    with client.stream(
        "POST",
        "/api/agent/stream",
        json={"message": "list topics", "sessionId": "demo"},
    ) as response:
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/event-stream")
        events = collect_events(list(response.iter_lines()))

    assert [event_name for event_name, _ in events] == [
        "status",
        "tool_start",
        "tool_done",
        "agent_token",
        "done",
    ]
    assert events[3][1]["text"] == "Available mock topics: APU, Hydraulics, Electrical."


def test_image_endpoints_return_svg_and_unknown_images_404() -> None:
    client = TestClient(create_app())

    image_response = client.get("/api/images/apu_generator")
    thumb_response = client.get("/api/images/apu_generator/thumbnail")
    missing_response = client.get("/api/images/not_real")

    assert image_response.status_code == 200
    assert image_response.headers["content-type"].startswith("image/svg+xml")
    assert "APU Generator Diagram" in image_response.text
    assert thumb_response.status_code == 200
    assert thumb_response.headers["content-type"].startswith("image/svg+xml")
    assert missing_response.status_code == 404
