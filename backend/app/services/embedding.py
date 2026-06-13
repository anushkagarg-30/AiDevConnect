import asyncio
import hashlib
import math

from google import genai
from google.genai import types
from openai import AsyncOpenAI

from app.config import settings


def _mock_embedding(text: str) -> list[float]:
    """Deterministic pseudo-embedding for local dev without an API key."""
    digest = hashlib.sha256(text.encode()).digest()
    values: list[float] = []
    while len(values) < settings.embedding_dimensions:
        for byte in digest:
            values.append((byte / 255.0) * 2 - 1)
            if len(values) == settings.embedding_dimensions:
                break
        digest = hashlib.sha256(digest).digest()

    magnitude = sum(v * v for v in values) ** 0.5
    return [v / magnitude for v in values]


def _normalize_embedding(values: list[float]) -> list[float]:
    magnitude = math.sqrt(sum(v * v for v in values))
    if magnitude == 0:
        return values
    return [v / magnitude for v in values]


def build_embedding_text(title: str, description: str, skills_needed: str | None = None) -> str:
    parts = [title.strip(), description.strip()]
    if skills_needed:
        parts.append(f"Skills needed: {skills_needed.strip()}")
    return "\n".join(parts)


def get_embedding_mode() -> str:
    if settings.mock_embeddings:
        return "mock"
    if settings.embedding_provider == "gemini" and settings.google_api_key:
        return "gemini"
    if settings.embedding_provider == "openai" and settings.openai_api_key:
        return "openai"
    return "mock"


def _gemini_embedding_sync(text: str) -> list[float]:
    client = genai.Client(api_key=settings.google_api_key)
    response = client.models.embed_content(
        model=settings.embedding_model,
        contents=text,
        config=types.EmbedContentConfig(
            output_dimensionality=settings.embedding_dimensions,
            task_type="RETRIEVAL_DOCUMENT",
        ),
    )
    values = list(response.embeddings[0].values)
    # gemini-embedding-001 requires manual normalization below 3072 dims
    if settings.embedding_dimensions != 3072:
        values = _normalize_embedding(values)
    return values


async def _openai_embedding(text: str) -> list[float]:
    client = AsyncOpenAI(api_key=settings.openai_api_key)
    response = await client.embeddings.create(
        model=settings.embedding_model,
        input=text,
        dimensions=settings.embedding_dimensions,
    )
    return response.data[0].embedding


async def generate_embedding(text: str) -> list[float]:
    if settings.mock_embeddings:
        return _mock_embedding(text)

    if settings.embedding_provider == "gemini":
        if not settings.google_api_key:
            return _mock_embedding(text)
        return await asyncio.to_thread(_gemini_embedding_sync, text)

    if not settings.openai_api_key:
        return _mock_embedding(text)
    return await _openai_embedding(text)
