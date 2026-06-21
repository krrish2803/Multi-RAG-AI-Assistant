"""Centralized application configuration using Pydantic Settings."""

from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # MongoDB
    mongo_user: str = "app_user"
    mongo_password: str = "change_me_in_production"
    mongo_host: str = "mongodb"
    mongo_port: int = 27017
    mongo_db: str = "knowledge_assistant"
    mongo_uri: str = "mongodb://app_user:change_me_in_production@mongodb:27017/knowledge_assistant?authSource=admin"

    # Qdrant
    qdrant_url: Optional[str] = None  # e.g. https://xxxxx.cloud.qdrant.io:6333 (for Qdrant Cloud)
    qdrant_host: str = "qdrant"
    qdrant_port: int = 6333
    qdrant_api_key: Optional[str] = None
    qdrant_collection: str = "knowledge_base"
    qdrant_vector_size: int = 1024

    # NVIDIA NIM
    nvidia_api_key: str = "nvapi-xxxx"
    nvidia_chat_model: str = "meta/llama-3.1-70b-instruct"
    nvidia_embed_model: str = "nvidia/nv-embedqa-e5-v5"
    nvidia_base_url: str = "https://integrate.api.nvidia.com/v1"

    # JWT Authentication
    jwt_secret_key: str = "change_me_to_random_64_char_string"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7

    # Application
    app_env: str = "development"
    app_debug: bool = True
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    log_level: str = "INFO"

    # Frontend
    frontend_url: str = "http://localhost:3000"

    @property
    def is_development(self) -> bool:
        return self.app_env == "development"

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    def get_qdrant_client_kwargs(self) -> dict:
        """Return kwargs for AsyncQdrantClient based on config."""
        if self.qdrant_url:
            return {"url": self.qdrant_url, "api_key": self.qdrant_api_key}
        return {
            "host": self.qdrant_host,
            "port": self.qdrant_port,
            "api_key": self.qdrant_api_key,
        }


@lru_cache()
def get_settings() -> Settings:
    """Cached settings instance."""
    return Settings()
