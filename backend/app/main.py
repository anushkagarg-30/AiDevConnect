from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import get_db
from app.routers import auth, matches, projects, ws


@asynccontextmanager
async def lifespan(_app: FastAPI):
    yield


app = FastAPI(
    title="AI DevConnect API",
    description="Developer networking platform with semantic project matching via pgvector",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1")
app.include_router(projects.router, prefix="/api/v1")
app.include_router(matches.router, prefix="/api/v1")
app.include_router(ws.router, prefix="/api/v1")


@app.get("/health")
async def health(db: AsyncSession = Depends(get_db)) -> dict[str, str]:
    try:
        await db.execute(text("SELECT 1"))
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database unavailable",
        ) from exc

    embedding_mode = "mock" if settings.mock_embeddings or not settings.openai_api_key else "openai"
    return {
        "status": "ok",
        "database": "connected",
        "embedding_mode": embedding_mode,
    }
