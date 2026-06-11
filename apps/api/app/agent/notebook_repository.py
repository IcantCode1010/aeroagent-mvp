import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


DEFAULT_NOTEBOOK_ROOT = Path(__file__).resolve().parents[1] / "data" / "notebooks"
STOP_WORDS = {
    "aircraft",
    "diagram",
    "diagrams",
    "image",
    "images",
    "list",
    "picture",
    "pictures",
    "show",
    "source",
    "topics",
}


@dataclass(frozen=True)
class Topic:
    slug: str
    title: str
    summary: str
    directory: Path


@dataclass(frozen=True)
class ImageAsset:
    image_id: str
    title: str
    caption: str
    image_file: Path
    thumbnail_file: Path
    sort_order: int


@dataclass(frozen=True)
class ImageContent:
    content: str
    media_type: str


class NotebookRepository:
    def __init__(self, root: Path | str | None = None) -> None:
        configured_root = root or os.environ.get("AEROAGENT_NOTEBOOK_ROOT") or DEFAULT_NOTEBOOK_ROOT
        self.root = Path(configured_root).resolve()

    def list_topics(self) -> list[Topic]:
        ordered_slugs = self._notebook_topic_order()
        topics_by_slug = {topic.slug: topic for topic in self._discover_topics()}
        ordered_topics = [topics_by_slug.pop(slug) for slug in ordered_slugs if slug in topics_by_slug]
        remaining_topics = sorted(topics_by_slug.values(), key=lambda topic: topic.title.lower())
        return ordered_topics + remaining_topics

    def search_markdown(self, query: str) -> dict[str, str]:
        terms = self._query_terms(query)
        best_match: tuple[int, Path, str] | None = None

        for markdown_file in self.root.rglob("*.md"):
            text = markdown_file.read_text(encoding="utf-8")
            normalized = text.lower()
            score = sum(1 for term in terms if term in normalized)
            if score == 0 and best_match is None:
                best_match = (0, markdown_file, self._excerpt(text, terms))
            elif score > 0 and (best_match is None or score > best_match[0]):
                best_match = (score, markdown_file, self._excerpt(text, terms))

        if best_match is None:
            return {
                "answer": "No Markdown notes are available in the configured notebook root.",
                "source": str(self.root),
            }

        _, source, excerpt = best_match
        return {
            "answer": excerpt,
            "source": source.as_posix(),
        }

    def search_images(self, query: str) -> list[ImageAsset]:
        terms = self._query_terms(query)
        assets = self._discover_images()
        matching = [
            asset
            for asset in assets
            if not terms or any(term in self._image_search_text(asset) for term in terms)
        ]
        return matching or assets

    def image_card(self, asset: ImageAsset) -> dict[str, str]:
        return {
            "imageId": asset.image_id,
            "title": asset.title,
            "thumbnailUrl": f"/api/images/{asset.image_id}/thumbnail",
            "imageUrl": f"/api/images/{asset.image_id}",
            "caption": asset.caption,
        }

    def get_image_content(self, image_id: str, *, thumbnail: bool = False) -> ImageContent | None:
        asset = next((candidate for candidate in self._discover_images() if candidate.image_id == image_id), None)
        if asset is None:
            return None

        image_file = asset.thumbnail_file if thumbnail else asset.image_file
        if not image_file.exists():
            image_file = asset.image_file

        return ImageContent(content=image_file.read_text(encoding="utf-8"), media_type="image/svg+xml")

    def _discover_topics(self) -> list[Topic]:
        topics: list[Topic] = []
        for metadata_path in self.root.rglob("topic.yaml"):
            metadata = self._read_yaml(metadata_path)
            topic_dir = metadata_path.parent
            topics.append(
                Topic(
                    slug=topic_dir.name,
                    title=str(metadata.get("title") or topic_dir.name.replace("-", " ").title()),
                    summary=str(metadata.get("summary") or ""),
                    directory=topic_dir,
                )
            )
        return topics

    def _discover_images(self) -> list[ImageAsset]:
        assets: list[ImageAsset] = []
        for metadata_path in self.root.rglob("images/*.yaml"):
            metadata = self._read_yaml(metadata_path)
            image_id = str(metadata.get("id") or metadata_path.stem)
            image_file = (metadata_path.parent / str(metadata["file"])).resolve()
            thumbnail_file = (metadata_path.parent / str(metadata.get("thumbnail") or metadata["file"])).resolve()
            self._assert_inside_root(image_file)
            self._assert_inside_root(thumbnail_file)
            assets.append(
                ImageAsset(
                    image_id=image_id,
                    title=str(metadata.get("title") or image_id.replace("_", " ").title()),
                    caption=str(metadata.get("caption") or ""),
                    image_file=image_file,
                    thumbnail_file=thumbnail_file,
                    sort_order=int(metadata.get("order") or 1000),
                )
            )
        return sorted(assets, key=lambda asset: (asset.sort_order, asset.title.lower()))

    def _notebook_topic_order(self) -> list[str]:
        slugs: list[str] = []
        for metadata_path in self.root.rglob("notebook.yaml"):
            metadata = self._read_yaml(metadata_path)
            for item in metadata.get("topics") or []:
                if isinstance(item, str):
                    slugs.append(item)
                elif isinstance(item, dict) and item.get("slug"):
                    slugs.append(str(item["slug"]))
        return slugs

    def _read_yaml(self, path: Path) -> dict[str, Any]:
        if not path.exists():
            return {}
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}

    def _query_terms(self, query: str) -> list[str]:
        terms = re.findall(r"[a-z0-9]+", query.lower())
        return [term for term in terms if len(term) > 2 and term not in STOP_WORDS]

    def _excerpt(self, text: str, terms: list[str]) -> str:
        sentences = re.split(r"(?<=[.!?])\s+", text.strip())
        for sentence in sentences:
            normalized = sentence.lower()
            if any(term in normalized for term in terms):
                return sentence
        return sentences[0] if sentences else "No matching notebook text found."

    def _image_search_text(self, asset: ImageAsset) -> str:
        return " ".join([asset.image_id, asset.title, asset.caption, asset.image_file.as_posix()]).lower()

    def _assert_inside_root(self, path: Path) -> None:
        path.relative_to(self.root)
