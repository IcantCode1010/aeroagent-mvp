# AeroAgent MVP

AeroAgent is a bare-bones proof of concept for a notebook-connected aviation agent. This first version proves the agent shell: typed streaming responses, multimodal image cards, a center source viewer, and a read-only plug-and-play tool registry backed by mock data.

## Architecture

```mermaid
flowchart LR
  Browser[Next.js web UI] -->|POST /api/agent/stream| API[FastAPI API]
  API --> Runtime[AgentRuntime]
  Runtime --> Planner[Planner]
  Runtime --> Registry[ToolRegistry]
  Registry --> Topics[list_topics]
  Registry --> Markdown[search_markdown]
  Registry --> Images[search_images]
  Browser -->|GET /api/images/:id| API
```

## How To Run

```bash
docker compose up --build
```

Open `http://localhost:3000`.

The API runs on `http://localhost:8000`.

## Test Curl Command

```bash
curl -N -X POST http://localhost:8000/api/agent/stream \
  -H "Content-Type: application/json" \
  -d "{\"message\":\"show me apu images\",\"sessionId\":\"demo\"}"
```

## What Is Included

- FastAPI endpoints for health, typed agent streaming, images, and thumbnails.
- Custom Python `AgentRuntime`, `Planner`, and read-only `ToolRegistry`.
- Mock tools: `list_topics`, `search_markdown`, and `search_images`.
- Next.js three-pane UI with topic placeholder, source viewer, streaming chat, and image cards.
- Docker Compose services for `api` on port `8000` and `web` on port `3000`.

## What Is Intentionally Excluded

- Real auth, database, vector DB, object storage, OCR, indexing, or LLM provider.
- Agent file writes, uploads, terminal commands, or indexing actions.
- Binary image assets; SVG images are generated in memory by the API.

## Local Checks

```bash
python -m pytest apps/api/tests/test_agent_runtime.py -q
cd apps/web && npm test && npm run build
```

## Next Step

Replace the mock tools with a read-only filesystem notebook adapter for Markdown files and image metadata under `/data/notebooks`.
