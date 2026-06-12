import hashlib

from openai import AsyncOpenAI

from app.config import settings


def _mock_embedding(text: str) -> list[float]:
    """Deterministic pseudo-embedding for local dev without an OpenAI key."""
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


def build_embedding_text(title: str, description: str, skills_needed: str | None = None) -> str:
    parts = [title.strip(), description.strip()]
    if skills_needed:
        parts.append(f"Skills needed: {skills_needed.strip()}")
    return "\n".join(parts)


async def generate_embedding(text: str) -> list[float]:
    if settings.mock_embeddings or not settings.openai_api_key:
        return _mock_embedding(text)

    client = AsyncOpenAI(api_key=settings.openai_api_key)
    response = await client.embeddings.create(
        model=settings.embedding_model,
        input=text,
        dimensions=settings.embedding_dimensions,
    )
    return response.data[0].embedding
