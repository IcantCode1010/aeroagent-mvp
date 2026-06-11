from collections.abc import Iterator

from app.agent.events import StreamEvent, make_event
from app.agent.planner import Planner
from app.agent.tool_registry import ToolRegistry, build_default_registry


class AgentRuntime:
    def __init__(self, registry: ToolRegistry | None = None, planner: Planner | None = None) -> None:
        self.registry = registry or build_default_registry()
        self.planner = planner or Planner()

    def stream(self, message: str, session_id: str) -> Iterator[StreamEvent]:
        yield make_event("status", {"message": "Planning request..."})

        plan = self.planner.plan(message)
        yield make_event("tool_start", {"tool": plan.tool_name})

        try:
            result = self.registry.run(plan.tool_name, plan.arguments, session_id=session_id)
        except Exception as exc:
            yield make_event("error", {"message": str(exc)})
            return

        yield make_event("tool_done", {"tool": plan.tool_name})

        if plan.tool_name == "search_images":
            images = result["images"]
            for image in images:
                yield make_event("image_result", image)
            if images:
                yield make_event("ui_action", {"type": "open_image", "payload": {"imageId": images[0]["imageId"]}})
            yield make_event("agent_token", {"text": f"I found {len(images)} mock image references for this notebook."})
        elif plan.tool_name == "list_topics":
            topics = result["topics"]
            yield make_event("agent_token", {"text": f"Available mock topics: {', '.join(topics)}."})
        else:
            yield make_event("agent_token", {"text": result["answer"]})

        yield make_event("done", {"messageId": "mock-msg-1"})
