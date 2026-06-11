from dataclasses import dataclass


@dataclass(frozen=True)
class Plan:
    tool_name: str
    arguments: dict[str, str]


class Planner:
    def plan(self, message: str) -> Plan:
        normalized = message.lower()

        if any(keyword in normalized for keyword in ("image", "picture", "diagram", "show")):
            return Plan(tool_name="search_images", arguments={"query": message})

        if "list" in normalized or "topics" in normalized:
            return Plan(tool_name="list_topics", arguments={"query": message})

        return Plan(tool_name="search_markdown", arguments={"query": message})
