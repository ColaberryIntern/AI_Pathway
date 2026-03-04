"""Curiosity Feed API routes — discovery feed for next skills to learn."""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_database, get_ontology, get_rag
from app.services.ontology import OntologyService
from app.services.rag.retriever import RAGRetriever
from app.services.curiosity_feed import CuriosityFeedService
from app.schemas.curiosity_feed import CuriosityFeedResponse

router = APIRouter()
feed_svc = CuriosityFeedService()


@router.get("/{user_id}/curiosity-feed", response_model=CuriosityFeedResponse)
async def get_curiosity_feed(
    user_id: str,
    limit: int = 10,
    db: AsyncSession = Depends(get_database),
    ontology_svc: OntologyService = Depends(get_ontology),
    rag: RAGRetriever = Depends(get_rag),
):
    """Get a discovery feed of skills the user can explore next."""
    items = await feed_svc.generate_feed(
        db=db,
        user_id=user_id,
        ontology_svc=ontology_svc,
        rag=rag,
        limit=limit,
    )
    return CuriosityFeedResponse(
        user_id=user_id,
        items=items,
        total_items=len(items),
    )
