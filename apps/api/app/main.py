from collections.abc import Iterator

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, StreamingResponse

from app.agent.events import format_sse
from app.agent.model_client import ModelClient
from app.agent.notebook_repository import NotebookRepository
from app.agent.runtime import AgentRuntime
from app.agent.tool_registry import build_default_registry
from app.schemas import AgentStreamRequest, HealthResponse


def create_app(
    notebook_root: str | None = None,
    model_client: ModelClient | None = None,
    load_env: bool = True,
) -> FastAPI:
    if load_env:
        load_dotenv()

    app = FastAPI(title="AeroAgent API", version="0.1.0")
    repository = NotebookRepository(notebook_root)
    runtime = AgentRuntime(registry=build_default_registry(str(repository.root)), model_client=model_client)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health", response_model=HealthResponse)
    def health() -> HealthResponse:
        return HealthResponse(status="ok", service="aeroagent-api")

    @app.post("/api/agent/stream")
    def stream_agent(request: AgentStreamRequest) -> StreamingResponse:
        def event_iterator() -> Iterator[str]:
            for event in runtime.stream(request.message, session_id=request.sessionId):
                yield format_sse(event)

        return StreamingResponse(event_iterator(), media_type="text/event-stream")

    @app.get("/api/images/{image_id}")
    def image(image_id: str) -> Response:
        image_content = repository.get_image_content(image_id)
        if image_content is None:
            raise HTTPException(status_code=404, detail="Image not found")
        return Response(content=image_content.content, media_type=image_content.media_type)

    @app.get("/api/images/{image_id}/thumbnail")
    def image_thumbnail(image_id: str) -> Response:
        image_content = repository.get_image_content(image_id, thumbnail=True)
        if image_content is None:
            raise HTTPException(status_code=404, detail="Image not found")
        return Response(content=image_content.content, media_type=image_content.media_type)

    return app


app = create_app()
