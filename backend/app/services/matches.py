from app.models.match_request import MatchRequest
from app.models.user import User
from app.schemas.match_request import MatchRequestResponse
from app.schemas.project import ProjectResponse


def build_match_response(
    match: MatchRequest,
    requester: User,
    recipient: User,
) -> MatchRequestResponse:
    requester_project = None
    if match.requester_project is not None:
        requester_project = ProjectResponse.model_validate(match.requester_project)

    return MatchRequestResponse(
        id=match.id,
        requester_id=match.requester_id,
        recipient_id=match.recipient_id,
        project_id=match.project_id,
        requester_project_id=match.requester_project_id,
        status=match.status,
        created_at=match.created_at,
        updated_at=match.updated_at,
        requester_username=requester.username,
        recipient_username=recipient.username,
        project=ProjectResponse.model_validate(match.project),
        requester_project=requester_project,
    )
