from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.match_request import MatchStatus
from app.schemas.project import ProjectResponse


class MatchRequestCreate(BaseModel):
    project_id: int = Field(description="The recipient's project you want to collaborate on")
    requester_project_id: int | None = Field(
        default=None,
        description="Your project that matched semantically (optional context)",
    )


class MatchRequestResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    requester_id: int
    recipient_id: int
    project_id: int
    requester_project_id: int | None
    status: MatchStatus
    created_at: datetime
    updated_at: datetime
    requester_username: str
    recipient_username: str
    project: ProjectResponse
    requester_project: ProjectResponse | None = None
