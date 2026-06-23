"""FastAPI main application."""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
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

    # Load the ontology into the vector store IFF RAG actually initialized. Keying
    # off real availability (get_rag_status) instead of an env-var heuristic makes
    # this turnkey: the moment GCP credentials are provided - by ANY ADC method
    # (service-account key OR workload identity, env var present or not) - RAG comes
    # up and the ontology auto-loads with zero further code change. When RAG is
    # unavailable we log the precise reason instead of a guessed one.
    from app.services.rag.retriever import get_rag_status
    rag_status = get_rag_status()
    if rag_status["available"]:
        try:
            from app.services.rag.vector_store import get_vector_store
            from pathlib import Path

            vector_store = get_vector_store()
            ontology_path = Path(__file__).parent / "data" / "ontology.json"
            if ontology_path.exists():
                vector_store.load_ontology(str(ontology_path))
                logger.info("ontology_loaded_into_vector_store")
        except Exception as e:
            logger.warning("ontology_load_failed", extra={"error": str(e)})
    else:
        logger.info("vector_store_init_skipped", extra={"reason": rag_status["reason"]})

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
    """Health check endpoint. Includes RAG availability so a degraded
    Semantic layer (no-op retriever) is visible, not silent."""
    try:
        from app.services.rag.retriever import get_rag_status
        rag = get_rag_status()
    except Exception as e:  # never let health-reporting break health
        rag = {"available": False, "retriever": "unknown", "reason": str(e)}
    return {"status": "healthy", "rag": rag}


@app.get("/metrics")
async def metrics_endpoint():
    """Rolling observability metrics (success/failure rates, error_class breakdown,
    retry counts, latency p50/p95/p99) aggregated from per-call/per-request telemetry."""
    from app.metrics import snapshot
    return {"window_hours": 24, "metrics": snapshot()}


# Both the root paths (internal / direct) and the /api/* aliases are registered:
# the prod frontend nginx only proxies /api/, so the /api/tbi/* aliases are what
# make the dashboard reachable externally (http://HOST/api/tbi/dashboard) with no
# nginx change.
@app.get("/tbi")
@app.get("/api/tbi")
async def tbi_status_endpoint():
    """Trust Before Intelligence status: INPACT scorecard, 7-layer health, and GOALS
    (governance/observability/availability/lexicon/solid), recorded + live signals."""
    from app.services.tbi import build_tbi_status
    return build_tbi_status()


@app.get("/tbi/dashboard", response_class=HTMLResponse)
@app.get("/api/tbi/dashboard", response_class=HTMLResponse)
async def tbi_dashboard_endpoint():
    """Self-contained TBI dashboard page (no external assets)."""
    from app.services.tbi import build_tbi_status, render_dashboard_html
    return HTMLResponse(render_dashboard_html(build_tbi_status()))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )
