"""Tests for Neon/asyncpg database URL normalization."""

from app.db_url import asyncpg_connect_args, clean_database_url_for_asyncpg, normalize_database_url


def test_normalize_adds_asyncpg_driver():
    url = "postgresql://user:pass@host/db"
    assert normalize_database_url(url) == "postgresql+asyncpg://user:pass@host/db"


def test_clean_strips_sslmode_for_asyncpg():
    url = (
        "postgresql+asyncpg://user:pass@ep-test.neon.tech/neondb"
        "?sslmode=require&channel_binding=require"
    )
    cleaned = clean_database_url_for_asyncpg(url)
    assert "sslmode" not in cleaned
    assert "channel_binding" not in cleaned
    assert cleaned.endswith("/neondb")


def test_asyncpg_connect_args_ssl_for_neon():
    url = "postgresql+asyncpg://user:pass@ep-test.neon.tech/neondb?sslmode=require"
    args = asyncpg_connect_args(url)
    assert "ssl" in args


def test_asyncpg_connect_args_empty_for_local():
    url = "postgresql+asyncpg://user:pass@localhost:5432/db"
    assert asyncpg_connect_args(url) == {}
