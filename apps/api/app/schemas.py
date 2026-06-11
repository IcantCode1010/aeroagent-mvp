from pydantic import BaseModel, Field


class AgentStreamRequest(BaseModel):
    message: str = Field(min_length=1)
    sessionId: str = Field(default="demo", min_length=1)


class HealthResponse(BaseModel):
    status: str
    service: str
