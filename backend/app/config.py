"""Application configuration settings."""
from functools import lru_cache
from typing import Literal
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # LLM Provider
    llm_provider: Literal["claude", "openai", "vertex"] = "vertex"
    anthropic_api_key: str = ""
    openai_api_key: str = ""

    # Model Configuration
    claude_model: str = "claude-sonnet-4-20250514"
    openai_model: str = "gpt-4-turbo-preview"

    # GCP / Vertex AI Configuration
    gcp_project_id: str = "ai-pathway-486221"
    gcp_region: str = "us-central1"
    vertex_model: str = "gemini-2.0-flash-exp"

    # Database
    database_url: str = "sqlite+aiosqlite:///./ai_pathway.db"

    # ChromaDB
    chroma_persist_directory: str = "./chroma_db"

    # Embedding Model (unused - using Vertex AI embeddings)
    embedding_model: str = "text-embedding-004"

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True

    # CORS - comma-separated string (parsed by main.py)
    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    def get_cors_origins_list(self) -> list[str]:
        """Get CORS origins as a list."""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
