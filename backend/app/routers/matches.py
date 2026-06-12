from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.deps import get_current_user
from app.models.match_request import MatchRequest, MatchStatus
from app.models.project import Project
from app.models.user import User
from app.schemas.match_request import MatchRequestCreate, MatchRequestResponse
from app.services.matches import build_match_response
from app.services.websocket import manager

router = APIRouter(prefix="/matches", tags=["matches"])

MATCH_LOAD_OPTIONS = (
    selectinload(MatchRequest.project),
    selectinload(MatchRequest.requester_project),
    selectinload(MatchRequest.requester),
    selectinload(MatchRequest.recipient),
)


async def _get_match_or_404(db: AsyncSession, match_id: int) -> MatchRequest:
    result = await db.execute(
        select(MatchRequest).options(*MATCH_LOAD_OPTIONS).where(MatchRequest.id == match_id)
    )
    match = result.scalar_one_or_none()
    if match is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Match request not found")
    return match


@router.post("", response_model=MatchRequestResponse, status_code=status.HTTP_201_CREATED)
async def create_match_request(
    payload: MatchRequestCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MatchRequestResponse:
    project = await db.get(Project, payload.project_id)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    if project.user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot send a match request for your own project",
        )

    if payload.requester_project_id is not None:
        requester_project = await db.get(Project, payload.requester_project_id)
        if requester_project is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Requester project not found")
        if requester_project.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Requester project must belong to you",
            )

    duplicate_filters = [
        MatchRequest.requester_id == current_user.id,
        MatchRequest.project_id == payload.project_id,
    ]
    if payload.requester_project_id is not None:
        duplicate_filters.append(MatchRequest.requester_project_id == payload.requester_project_id)

    existing = await db.execute(select(MatchRequest).where(*duplicate_filters))
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already sent a match request for this project",
        )

    match = MatchRequest(
        requester_id=current_user.id,
        recipient_id=project.user_id,
        project_id=project.id,
        requester_project_id=payload.requester_project_id,
    )
    db.add(match)
    await db.commit()
    await db.refresh(match)

    loaded = await _get_match_or_404(db, match.id)

    await manager.send_to_user(
        loaded.recipient_id,
        {
            "type": "match_request",
            "match_request_id": loaded.id,
            "requester_id": current_user.id,
            "requester_username": current_user.username,
            "project_id": project.id,
            "project_title": project.title,
            "requester_project_id": payload.requester_project_id,
        },
    )

    return build_match_response(loaded, loaded.requester, loaded.recipient)


@router.get("/sent", response_model=list[MatchRequestResponse])
async def list_sent_match_requests(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[MatchRequestResponse]:
    result = await db.execute(
        select(MatchRequest)
        .options(*MATCH_LOAD_OPTIONS)
        .where(MatchRequest.requester_id == current_user.id)
        .order_by(MatchRequest.created_at.desc())
    )
    matches = result.scalars().all()
    return [build_match_response(m, m.requester, m.recipient) for m in matches]


@router.get("/received", response_model=list[MatchRequestResponse])
async def list_received_match_requests(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[MatchRequestResponse]:
    result = await db.execute(
        select(MatchRequest)
        .options(*MATCH_LOAD_OPTIONS)
        .where(MatchRequest.recipient_id == current_user.id)
        .order_by(MatchRequest.created_at.desc())
    )
    matches = result.scalars().all()
    return [build_match_response(m, m.requester, m.recipient) for m in matches]


@router.get("/{match_id}", response_model=MatchRequestResponse)
async def get_match_request(
    match_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MatchRequestResponse:
    match = await _get_match_or_404(db, match_id)

    if current_user.id not in (match.requester_id, match.recipient_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this match request")

    return build_match_response(match, match.requester, match.recipient)


@router.post("/{match_id}/accept", response_model=MatchRequestResponse)
async def accept_match_request(
    match_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MatchRequestResponse:
    match = await _get_match_or_404(db, match_id)

    if match.recipient_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the recipient can accept")

    if match.status != MatchStatus.PENDING:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Match request is no longer pending")

    match.status = MatchStatus.ACCEPTED
    await db.commit()
    await db.refresh(match)
    match = await _get_match_or_404(db, match.id)

    await manager.send_to_user(
        match.requester_id,
        {
            "type": "match_accepted",
            "match_request_id": match.id,
            "recipient_id": current_user.id,
            "recipient_username": current_user.username,
            "project_id": match.project_id,
            "project_title": match.project.title,
        },
    )

    return build_match_response(match, match.requester, match.recipient)


@router.post("/{match_id}/reject", response_model=MatchRequestResponse)
async def reject_match_request(
    match_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MatchRequestResponse:
    match = await _get_match_or_404(db, match_id)

    if match.recipient_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the recipient can reject")

    if match.status != MatchStatus.PENDING:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Match request is no longer pending")

    match.status = MatchStatus.REJECTED
    await db.commit()
    await db.refresh(match)
    match = await _get_match_or_404(db, match.id)

    await manager.send_to_user(
        match.requester_id,
        {
            "type": "match_rejected",
            "match_request_id": match.id,
            "recipient_id": current_user.id,
            "recipient_username": current_user.username,
            "project_id": match.project_id,
            "project_title": match.project.title,
        },
    )

    return build_match_response(match, match.requester, match.recipient)
