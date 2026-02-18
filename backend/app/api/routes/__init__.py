"""API routes."""
from fastapi import APIRouter
from app.api.routes import profiles, analysis, assessment, paths, progress, ontology
from app.api.routes import deterministic_paths

api_router = APIRouter()

api_router.include_router(profiles.router, prefix="/profiles", tags=["profiles"])
api_router.include_router(analysis.router, prefix="/analysis", tags=["analysis"])
api_router.include_router(assessment.router, prefix="/assessment", tags=["assessment"])
api_router.include_router(paths.router, prefix="/paths", tags=["paths"])
api_router.include_router(progress.router, prefix="/progress", tags=["progress"])
api_router.include_router(ontology.router, prefix="/ontology", tags=["ontology"])
api_router.include_router(deterministic_paths.router, prefix="/deterministic-paths", tags=["deterministic-paths"])
