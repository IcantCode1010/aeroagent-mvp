# AeroAgent MVP Scope

## Included

- Dockerized FastAPI API and Next.js web app.
- Typed Server-Sent Events for agent responses.
- Custom Python agent runtime with a simple planner.
- Read-only plug-and-play tool registry.
- File-backed read-only tools for topic listing, Markdown search, and image search.
- In-memory SVG image and thumbnail endpoints.
- Three-pane web UI with topic placeholder, source viewer, and streaming chat.

## Intentionally Excluded

- Real authentication or authorization.
- Real LLM providers.
- Postgres, LanceDB, MinIO, or any other persistent storage.
- OCR, Pillow, OpenCV, image ingestion, or document upload.
- Notebook indexing or writes.
- Agent file writes, terminal execution, upload actions, or indexing actions.

## Next Step

Connect the read-only filesystem notebook adapter to a maintained notebook corpus mounted through `AEROAGENT_NOTEBOOK_ROOT`.
