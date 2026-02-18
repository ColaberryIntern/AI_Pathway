"""API dependencies."""
from fastapi import Depends
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
