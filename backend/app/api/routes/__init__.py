"""API routes."""
from fastapi import APIRouter
from app.api.routes import profiles, analysis, assessment, paths, progress, ontology
from app.api.routes import deterministic_paths, learning, prompt_lab, mentor
from app.api.routes import skill_genome, lesson_reactions, confusion_recovery
from app.api.routes import curiosity_feed, personalization

api_router = APIRouter()

api_router.include_router(profiles.router, prefix="/profiles", tags=["profiles"])
api_router.include_router(analysis.router, prefix="/analysis", tags=["analysis"])
api_router.include_router(assessment.router, prefix="/assessment", tags=["assessment"])
api_router.include_router(paths.router, prefix="/paths", tags=["paths"])
api_router.include_router(progress.router, prefix="/progress", tags=["progress"])
api_router.include_router(ontology.router, prefix="/ontology", tags=["ontology"])
api_router.include_router(deterministic_paths.router, prefix="/deterministic-paths", tags=["deterministic-paths"])
api_router.include_router(learning.router, prefix="/learning", tags=["learning"])
api_router.include_router(prompt_lab.router, prefix="/learning", tags=["prompt-lab"])
api_router.include_router(mentor.router, prefix="/learning", tags=["mentor"])
api_router.include_router(lesson_reactions.router, prefix="/learning", tags=["reactions"])
api_router.include_router(confusion_recovery.router, prefix="/learning", tags=["confusion"])
api_router.include_router(skill_genome.router, prefix="/genome", tags=["genome"])
api_router.include_router(curiosity_feed.router, prefix="/genome", tags=["curiosity"])
api_router.include_router(personalization.router, prefix="/personalization", tags=["personalization"])
