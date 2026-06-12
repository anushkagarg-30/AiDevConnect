from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.deps import get_current_user
from app.models.match_request import MatchRequest
from app.models.project import Project
from app.models.user import User, UserRole
from app.schemas.project import ProjectCreate, ProjectMatchResult, ProjectResponse, ProjectUpdate
from app.services.embedding import build_embedding_text, generate_embedding

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    payload: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Project:
    embedding_text = build_embedding_text(payload.title, payload.description, payload.skills_needed)
    embedding = await generate_embedding(embedding_text)

    project = Project(
        user_id=current_user.id,
        title=payload.title,
        description=payload.description,
        skills_needed=payload.skills_needed,
        embedding=embedding,
    )
    db.add(project)
    await db.commit()
    await db.refresh(project)
    return project


@router.get("", response_model=list[ProjectResponse])
async def list_projects(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[Project]:
    if current_user.role == UserRole.ADMIN:
        result = await db.execute(select(Project).order_by(Project.created_at.desc()))
    else:
        result = await db.execute(
            select(Project).where(Project.user_id == current_user.id).order_by(Project.created_at.desc())
        )
    return list(result.scalars().all())


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Project:
    project = await db.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    if current_user.role != UserRole.ADMIN and project.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this project")

    return project


@router.patch("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int,
    payload: ProjectUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Project:
    project = await db.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    if project.user_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this project")

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(project, field, value)

    if {"title", "description", "skills_needed"} & update_data.keys():
        embedding_text = build_embedding_text(project.title, project.description, project.skills_needed)
        project.embedding = await generate_embedding(embedding_text)

    await db.commit()
    await db.refresh(project)
    return project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    project = await db.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    if project.user_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this project")

    await db.delete(project)
    await db.commit()


@router.get("/{project_id}/matches", response_model=list[ProjectMatchResult])
async def find_matches(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = 10,
) -> list[ProjectMatchResult]:
    """
    Find semantically similar projects using pgvector cosine distance.

    The core query:
        SELECT *, 1 - (embedding <=> $1) AS similarity
        FROM projects
        WHERE user_id != $2
        ORDER BY embedding <=> $1
        LIMIT 10;
    """
    source = await db.get(Project, project_id)
    if source is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    if source.user_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to match on this project")

    distance = Project.embedding.cosine_distance(source.embedding)
    similarity = (1 - distance).label("similarity")

    already_requested = select(MatchRequest.project_id).where(
        MatchRequest.requester_id == current_user.id,
        or_(
            MatchRequest.requester_project_id == project_id,
            MatchRequest.requester_project_id.is_(None),
        ),
    )

    stmt = (
        select(Project, similarity, User.username)
        .join(User, Project.user_id == User.id)
        .where(Project.user_id != current_user.id)
        .where(Project.id != project_id)
        .where(Project.id.not_in(already_requested))
        .order_by(distance)
        .limit(limit)
    )

    result = await db.execute(stmt)
    rows = result.all()

    return [
        ProjectMatchResult(
            project=ProjectResponse.model_validate(project),
            similarity=round(float(sim_score), 4),
            owner_username=username,
        )
        for project, sim_score, username in rows
    ]
