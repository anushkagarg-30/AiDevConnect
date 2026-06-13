import os
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import NullPool

from app.config import settings


def _use_null_pool() -> bool:
    return os.getenv("USE_NULL_POOL", "").lower() in ("1", "true", "yes")


_engine_kwargs: dict = {
    "echo": False,
    "connect_args": settings.database_connect_args,
}
if _use_null_pool():
    _engine_kwargs["poolclass"] = NullPool
else:
    _engine_kwargs["pool_size"] = 20
    _engine_kwargs["max_overflow"] = 30

engine = create_async_engine(settings.sqlalchemy_database_url, **_engine_kwargs)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session
