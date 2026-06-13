from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import NullPool

from app.config import settings

_engine_kwargs: dict = {
    "echo": False,
    "connect_args": settings.database_connect_args,
}
if settings.environment == "test":
    _engine_kwargs["poolclass"] = NullPool

engine = create_async_engine(settings.sqlalchemy_database_url, **_engine_kwargs)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session
