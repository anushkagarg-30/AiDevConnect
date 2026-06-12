from typing import Literal, Self

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

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
    mock_embeddings: bool = True
    access_token_expire_minutes: int = 30
    embedding_model: str = "text-embedding-3-small"
    embedding_dimensions: int = 1536
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    @field_validator("database_url", mode="before")
    @classmethod
    def normalize_database_url(cls, value: str) -> str:
        if isinstance(value, str) and value.startswith("postgresql://") and "+asyncpg" not in value:
            return value.replace("postgresql://", "postgresql+asyncpg://", 1)
        return value

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @model_validator(mode="after")
    def validate_production(self) -> Self:
        if self.environment != "production":
            return self

        if self.secret_key in INSECURE_SECRET_KEYS or len(self.secret_key) < 32:
            raise ValueError("SECRET_KEY must be a random string of at least 32 characters in production")

        if not self.mock_embeddings and not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required when MOCK_EMBEDDINGS=false in production")

        if not self.cors_origins_list:
            raise ValueError("CORS_ORIGINS must list at least one allowed origin in production")

        return self


settings = Settings()
