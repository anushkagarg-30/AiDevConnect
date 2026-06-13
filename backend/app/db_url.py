"""Normalize Postgres URLs for SQLAlchemy + asyncpg (Neon, Render, etc.)."""

import ssl
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

# libpq query params that must not be passed to asyncpg.connect()
_ASYNCPG_STRIP_QUERY_KEYS = frozenset({"sslmode", "channel_binding", "options"})


def normalize_database_url(url: str) -> str:
    if url.startswith("postgresql://") and "+asyncpg" not in url:
        return url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return url


def clean_database_url_for_asyncpg(url: str) -> str:
    parsed = urlparse(url)
    query = parse_qs(parsed.query, keep_blank_values=True)
    filtered = {key: values for key, values in query.items() if key not in _ASYNCPG_STRIP_QUERY_KEYS}
    flat_query = urlencode({key: values[0] if values else "" for key, values in filtered.items()})
    return urlunparse(parsed._replace(query=flat_query))


def asyncpg_connect_args(url: str) -> dict:
    query = parse_qs(urlparse(url).query, keep_blank_values=True)
    sslmode = query.get("sslmode", [""])[0].lower()
    if sslmode in {"require", "verify-ca", "verify-full"}:
        return {"ssl": ssl.create_default_context()}
    return {}
