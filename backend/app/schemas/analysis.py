"""Analysis schemas for full workflow."""
from pydantic import BaseModel
from app.schemas.profile import ProfileResponse
from app.schemas.goal import GoalResponse
from app.schemas.assessment import AssessmentResponse
from app.schemas.skill_gap import SkillGapResponse
from app.schemas.learning_path import LearningPathResponse


class JDParseRequest(BaseModel):
    """Schema for JD parsing request."""

    jd_text: str
    target_role: str | None = None


class JDParseResponse(BaseModel):
    """Schema for JD parsing response."""

    target_role: str
    extracted_skills: list[dict]  # [{skill_id, skill_name, required_level, importance}]
    industry: str | None = None
    experience_level: str | None = None


class JDSkillsRequest(BaseModel):
    """Schema for JD skills parsing request (JD-first flow).

    When learner_profile is provided, runs a 3-step chain:
    1. Analyze JD against ontology -> extract 10 skills
    2. Re-rank against learner's background -> identify true gaps
    3. Apply scoring rubric -> produce final ranked top 5
    """

    jd_text: str
    target_role: str | None = None
    learner_profile: dict | None = None  # Full profile for 3-step chain


class FullAnalysisRequest(BaseModel):
    """Schema for full analysis request (StateA → StateB → Gap → Path)."""

    profile_id: str | None = None  # Use existing profile
    custom_profile: dict | None = None  # Or provide custom profile data
    target_jd_text: str
    target_role: str | None = None
    skip_assessment: bool = False  # Skip quiz and use profile-based assessment
    self_assessed_skills: dict | None = None  # {skill_id: level} from self-assessment UI


class FullAnalysisResponse(BaseModel):
    """Schema for full analysis response."""

    user_id: str
    profile: ProfileResponse
    goal: GoalResponse
    assessment: AssessmentResponse | None
    skill_gap: SkillGapResponse
    learning_path: LearningPathResponse
    summary: dict  # High-level summary for UI


class PathGenerateRequest(BaseModel):
    """Schema for generating a learning path."""

    gap_id: str
    num_chapters: int = 5
    focus_skills: list[str] | None = None  # Specific skills to prioritize
