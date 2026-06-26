"""API dependencies."""
from fastapi import Depends, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services.llm import get_llm_provider, BaseLLMProvider
from app.services.rag.retriever import get_retriever, RAGRetriever
from app.services.ontology import get_ontology_service, OntologyService
from app.agents.orchestrator import get_orchestrator, Orchestrator


async def get_database() -> AsyncSession:
    """Dependency for database session."""
    async for db in get_db():
        yield db


async def get_optional_user(request: Request, db: AsyncSession = Depends(get_database)):
    """Resolve the current User from the session cookie, or None.

    NON-ENFORCING by design (SSO increment 1): routes are NOT gated on this yet,
    so the current open flow + demo are unaffected. The next increment will add a
    `require_user` that 401s, once SSO is actually turned on. Returns None when
    auth is off, no cookie, or the token is invalid/expired.
    """
    from app.config import get_settings
    from app.models.user import User
    from app.services.auth.tokens import verify_session

    token = request.cookies.get("ai_pathway_session")
    secret = get_settings().session_secret
    claims = verify_session(token, secret) if token else None
    if not claims:
        return None
    return (await db.execute(select(User).where(User.id == claims["sub"]))).scalars().first()


def get_llm() -> BaseLLMProvider:
    """Dependency for LLM provider."""
    return get_llm_provider()


def get_rag() -> RAGRetriever:
    """Dependency for RAG retriever."""
    return get_retriever()


def get_ontology() -> OntologyService:
    """Dependency for ontology service."""
    return get_ontology_service()


def get_agent_orchestrator() -> Orchestrator:
    """Dependency for orchestrator."""
    return get_orchestrator()
