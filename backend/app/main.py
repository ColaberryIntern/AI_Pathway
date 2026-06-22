"""FastAPI main application."""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.database import init_db, close_db
from app.api.routes import api_router
from app.observability import CorrelationIdMiddleware, configure_logging

settings = get_settings()
configure_logging(logging.DEBUG if settings.debug else logging.INFO)
logger = logging.getLogger("app.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    await init_db()
    logger.info("database_initialized")

    # Initialize RAG vector store with ontology — skip if GCP credentials
    # are not available (avoids blocking startup with network timeouts)
    import os
    gcp_creds = (
        os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
        or os.environ.get("GOOGLE_CLOUD_PROJECT")
    )
    if gcp_creds:
        try:
            from app.services.rag.vector_store import get_vector_store
            from pathlib import Path

            vector_store = get_vector_store()
            ontology_path = Path(__file__).parent / "data" / "ontology.json"
            if ontology_path.exists():
                vector_store.load_ontology(str(ontology_path))
                logger.info("ontology_loaded_into_vector_store")
        except Exception as e:
            logger.warning("vector_store_init_failed", extra={"error": str(e)})
    else:
        logger.info("vector_store_init_skipped", extra={"reason": "no GCP credentials"})

    yield

    # Shutdown
    await close_db()
    logger.info("database_connections_closed")


app = FastAPI(
    title="AI Pathway Tool",
    description="Multi-agent AI system for generating personalized AI learning paths",
    version="0.1.0",
    lifespan=lifespan,
)

# Correlation id + request telemetry (added before CORS so it wraps every request
# and the correlation id is bound for the whole request lifecycle).
app.add_middleware(CorrelationIdMiddleware)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins_list(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Correlation-ID"],
)

# Include API routes
app.include_router(api_router, prefix="/api")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "AI Pathway Tool",
        "version": "0.1.0",
        "description": "Multi-agent AI system for generating personalized AI learning paths",
        "docs": "/docs",
        "api": "/api",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )
