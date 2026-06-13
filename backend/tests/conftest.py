import os

# Must run before app.settings is loaded so tests use mock-friendly thresholds.
os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("MATCH_MIN_SIMILARITY", "0")
os.environ.setdefault("USE_NULL_POOL", "true")

import pytest
from httpx import ASGITransport, AsyncClient

from app.database import engine
from app.main import app


@pytest.fixture(scope="session")
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture(scope="session", autouse=True)
async def dispose_db_engine():
    yield
    await engine.dispose()
