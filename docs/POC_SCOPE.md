# AeroAgent MVP Scope

## Included

- Dockerized FastAPI API and Next.js web app.
- Typed Server-Sent Events for agent responses.
- Custom Python agent runtime with a simple planner.
- Read-only plug-and-play tool registry.
- Mock tools for topic listing, Markdown search, and image search.
- In-memory SVG image and thumbnail endpoints.
- Three-pane web UI with topic placeholder, source viewer, and streaming chat.

## Intentionally Excluded

- Real authentication or authorization.
- Real LLM providers.
- Postgres, LanceDB, MinIO, or any other persistent storage.
- OCR, Pillow, OpenCV, image ingestion, or document upload.
- Filesystem notebook indexing.
- Agent file writes, terminal execution, upload actions, or indexing actions.

## Next Step

Replace the mock tools with a read-only filesystem notebook adapter that can load notebook metadata, Markdown topic files, and image metadata from a mounted `/data/notebooks` directory.
