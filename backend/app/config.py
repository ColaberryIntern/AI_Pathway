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

    # Judge model (Trust Before Intelligence). The judge/evaluator runs on a
    # pinned, calibrated model independent of the generation provider. gpt-4.1 per
    # the Jun 2026 calibration (reproduces the expert reference; gpt-4o under-reads).
    judge_provider: Literal["claude", "openai", "vertex"] = "openai"
    judge_model: str = "gpt-4.1"
    # Governance gate: when true, the recommendation judge runs on the analysis
    # endpoint and records a verdict (shadow mode). Default off; flip on to test.
    judge_gate_enabled: bool = False
    # The judge LLM layer has run-to-run variance even at temperature 0.0 (a
    # borderline recommendation can flip ACCEPT<->REJECT between identical calls).
    # Per Trust Before Intelligence, the probabilistic judge is wrapped in an
    # ensemble: sample K times, aggregate each parameter by median, and refuse to
    # hard-act (accept/reject) when the K-run panel disagrees - route to human
    # review instead. K=1 reproduces the legacy single-shot behavior.
    judge_ensemble_k: int = 5

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
    cors_origins: str = "http://localhost:5173,http://localhost:3000,http://95.216.199.47,http://95.216.199.47:3000"

    # Communication Intelligence - Basecamp
    basecamp_token: str = ""
    basecamp_account_id: str = "3945211"
    basecamp_project_id: str = "46692302"

    # Communication Intelligence - Gmail
    gmail_credentials_path: str = "credentials/gmail_credentials.json"
    gmail_token_path: str = "credentials/gmail_token.json"

    def get_cors_origins_list(self) -> list[str]:
        """Get CORS origins as a list."""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        # 2026-06-03: allow extraneous env vars to be present without
        # rejection. Lets backend code run from contexts (e.g. the
        # rubric_compare_v3.py harness in the project root) that load
        # both backend/.env and project-root /.env which has unrelated
        # MSSQL_* / GMAIL_* keys for the Basecamp + send-* scripts.
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
