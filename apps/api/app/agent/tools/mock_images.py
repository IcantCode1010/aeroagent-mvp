from html import escape
from typing import Any

from app.agent.tools.base import BaseTool, ToolContext, ToolDefinition


IMAGE_RESULTS = {
    "apu_generator": {
        "imageId": "apu_generator",
        "title": "APU Generator Diagram",
        "thumbnailUrl": "/api/images/apu_generator/thumbnail",
        "imageUrl": "/api/images/apu_generator",
        "caption": "Mock APU generator diagram.",
    },
    "apu_bleed_air": {
        "imageId": "apu_bleed_air",
        "title": "APU Bleed Air Schematic",
        "thumbnailUrl": "/api/images/apu_bleed_air/thumbnail",
        "imageUrl": "/api/images/apu_bleed_air",
        "caption": "Mock APU bleed air schematic.",
    },
}


class SearchImagesTool(BaseTool):
    definition = ToolDefinition(
        name="search_images",
        description="Search mock notebook image cards.",
        category="images",
        read_only=True,
        permission_level="public_mock",
        input_schema={"type": "object", "properties": {"query": {"type": "string"}}},
        output_schema={"type": "object", "properties": {"images": {"type": "array"}}},
    )

    def run(self, input_data: dict[str, Any], context: ToolContext) -> dict[str, Any]:
        return {"images": list(IMAGE_RESULTS.values())}


def get_svg_image(image_id: str) -> str | None:
    image = IMAGE_RESULTS.get(image_id)
    if not image:
        return None

    title = escape(image["title"])
    caption = escape(image["caption"])
    accent = "#2563eb" if image_id == "apu_generator" else "#047857"
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="900" height="560" viewBox="0 0 900 560" role="img" aria-label="{title}">
  <rect width="900" height="560" fill="#f8fafc"/>
  <rect x="70" y="80" width="760" height="400" rx="18" fill="#ffffff" stroke="#0f172a" stroke-width="4"/>
  <text x="450" y="145" text-anchor="middle" font-family="Arial, sans-serif" font-size="34" font-weight="700" fill="#0f172a">{title}</text>
  <rect x="180" y="235" width="180" height="100" rx="16" fill="{accent}" opacity="0.92"/>
  <rect x="540" y="235" width="180" height="100" rx="16" fill="{accent}" opacity="0.72"/>
  <line x1="360" y1="285" x2="540" y2="285" stroke="#0f172a" stroke-width="8" stroke-linecap="round"/>
  <circle cx="450" cy="285" r="42" fill="#eab308" stroke="#0f172a" stroke-width="5"/>
  <text x="450" y="430" text-anchor="middle" font-family="Arial, sans-serif" font-size="24" fill="#334155">{caption}</text>
</svg>"""


def get_svg_thumbnail(image_id: str) -> str | None:
    image = IMAGE_RESULTS.get(image_id)
    if not image:
        return None

    title = escape(image["title"])
    accent = "#2563eb" if image_id == "apu_generator" else "#047857"
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="320" height="200" viewBox="0 0 320 200" role="img" aria-label="{title}">
  <rect width="320" height="200" fill="#eef2ff"/>
  <rect x="28" y="36" width="264" height="128" rx="10" fill="#ffffff" stroke="#1e293b" stroke-width="3"/>
  <rect x="72" y="88" width="60" height="34" rx="7" fill="{accent}"/>
  <rect x="188" y="88" width="60" height="34" rx="7" fill="{accent}" opacity="0.75"/>
  <line x1="132" y1="105" x2="188" y2="105" stroke="#1e293b" stroke-width="5"/>
  <text x="160" y="62" text-anchor="middle" font-family="Arial, sans-serif" font-size="18" font-weight="700" fill="#0f172a">{title}</text>
</svg>"""
