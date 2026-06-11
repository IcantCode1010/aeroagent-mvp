from collections.abc import Iterator

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, StreamingResponse

from app.agent.events import format_sse
from app.agent.runtime import AgentRuntime
from app.agent.tools.mock_images import get_svg_image, get_svg_thumbnail
from app.schemas import AgentStreamRequest, HealthResponse


def create_app() -> FastAPI:
    app = FastAPI(title="AeroAgent API", version="0.1.0")
    runtime = AgentRuntime()

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
        svg = get_svg_image(image_id)
        if svg is None:
            raise HTTPException(status_code=404, detail="Image not found")
        return Response(content=svg, media_type="image/svg+xml")

    @app.get("/api/images/{image_id}/thumbnail")
    def image_thumbnail(image_id: str) -> Response:
        svg = get_svg_thumbnail(image_id)
        if svg is None:
            raise HTTPException(status_code=404, detail="Image not found")
        return Response(content=svg, media_type="image/svg+xml")

    return app


app = create_app()
