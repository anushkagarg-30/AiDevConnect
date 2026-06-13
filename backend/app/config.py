from typing import Literal, Self

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.db_url import (
    asyncpg_connect_args,
    clean_database_url_for_asyncpg,
    normalize_database_url as normalize_db_driver_url,
)

INSECURE_SECRET_KEYS = {
    "dev-secret-key-change-in-production",
    "change-me-to-a-long-random-string",
    "ci-test-secret-key",
    "load-test-secret",
}


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    environment: Literal["development", "production", "test"] = "development"
    database_url: str = "postgresql+asyncpg://aidevconnect:aidevconnect@localhost:5432/aidevconnect"
    secret_key: str = "dev-secret-key-change-in-production"
    openai_api_key: str = ""
    google_api_key: str = ""
    mock_embeddings: bool = True
    access_token_expire_minutes: int = 30
    embedding_provider: Literal["gemini", "openai"] = "gemini"
    embedding_model: str = "gemini-embedding-001"
    embedding_dimensions: int = 1536
    match_min_similarity: float = 0.72
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    @field_validator("database_url", mode="before")
    @classmethod
    def validate_database_url(cls, value: str) -> str:
        if isinstance(value, str):
            return normalize_db_driver_url(value)
        return value

    @property
    def sqlalchemy_database_url(self) -> str:
        return clean_database_url_for_asyncpg(self.database_url)

    @property
    def database_connect_args(self) -> dict:
        return asyncpg_connect_args(self.database_url)

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @model_validator(mode="after")
    def validate_production(self) -> Self:
        if self.environment != "production":
            return self

        if self.secret_key in INSECURE_SECRET_KEYS or len(self.secret_key) < 32:
            raise ValueError("SECRET_KEY must be a random string of at least 32 characters in production")

        if not self.mock_embeddings:
            if self.embedding_provider == "gemini" and not self.google_api_key:
                raise ValueError(
                    "GOOGLE_API_KEY is required when EMBEDDING_PROVIDER=gemini and MOCK_EMBEDDINGS=false"
                )
            if self.embedding_provider == "openai" and not self.openai_api_key:
                raise ValueError(
                    "OPENAI_API_KEY is required when EMBEDDING_PROVIDER=openai and MOCK_EMBEDDINGS=false"
                )

        if not self.cors_origins_list:
            raise ValueError("CORS_ORIGINS must list at least one allowed origin in production")

        return self


settings = Settings()
