"""FastAPI main application."""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.database import init_db, close_db
from app.api.routes import api_router

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    await init_db()
    print("Database initialized")

    # Initialize RAG vector store with ontology
    try:
        from app.services.rag.vector_store import get_vector_store
        from pathlib import Path

        vector_store = get_vector_store()
        ontology_path = Path(__file__).parent / "data" / "ontology.json"
        if ontology_path.exists():
            vector_store.load_ontology(str(ontology_path))
            print("Ontology loaded into vector store")
    except Exception as e:
        print(f"Warning: Could not initialize vector store: {e}")

    yield

    # Shutdown
    await close_db()
    print("Database connections closed")


app = FastAPI(
    title="AI Pathway Tool",
    description="Multi-agent AI system for generating personalized AI learning paths",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins_list(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
