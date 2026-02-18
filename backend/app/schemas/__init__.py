"""Pydantic schemas for API validation."""
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.schemas.profile import ProfileCreate, ProfileResponse, ProfileUpload
from app.schemas.goal import GoalCreate, GoalResponse
from app.schemas.assessment import (
    AssessmentCreate,
    AssessmentResponse,
    QuizQuestion,
    QuizResponse,
)
from app.schemas.skill_gap import SkillGapResponse, SkillGapCreate
from app.schemas.learning_path import (
    LearningPathCreate,
    LearningPathResponse,
    ChapterContent,
)
from app.schemas.progress import ProgressCreate, ProgressResponse, ProgressUpdate
from app.schemas.analysis import (
    FullAnalysisRequest,
    FullAnalysisResponse,
    JDParseRequest,
    JDParseResponse,
)

__all__ = [
    "UserCreate",
    "UserResponse",
    "UserUpdate",
    "ProfileCreate",
    "ProfileResponse",
    "ProfileUpload",
    "GoalCreate",
    "GoalResponse",
    "AssessmentCreate",
    "AssessmentResponse",
    "QuizQuestion",
    "QuizResponse",
    "SkillGapResponse",
    "SkillGapCreate",
    "LearningPathCreate",
    "LearningPathResponse",
    "ChapterContent",
    "ProgressCreate",
    "ProgressResponse",
    "ProgressUpdate",
    "FullAnalysisRequest",
    "FullAnalysisResponse",
    "JDParseRequest",
    "JDParseResponse",
]
