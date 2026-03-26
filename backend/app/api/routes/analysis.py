"""Analysis API routes - main workflow endpoints."""
import json
import logging
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse
from pydantic import BaseModel as _BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_database, get_agent_orchestrator
from app.agents.orchestrator import Orchestrator
from app.agents.jd_parser import JDParserAgent
from app.agents.base import BaseAgent
from app.models.user import User
from app.models.goal import Goal
from app.models.skill_gap import SkillGap
from app.models.learning_path import LearningPath
from app.services.ontology import get_ontology_service
from app.services.llm import get_llm_provider
from app.schemas.analysis import (
    FullAnalysisRequest,
    FullAnalysisResponse,
    JDParseRequest,
    JDParseResponse,
    JDSkillsRequest,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/full")
async def run_full_analysis(
    request: FullAnalysisRequest,
    db: AsyncSession = Depends(get_database),
    orchestrator: Orchestrator = Depends(get_agent_orchestrator),
):
    """Run full analysis: Profile -> JD -> Gap -> Path generation.

    Accepts either a profile_id (DB profile) or custom_profile (inline dict).
    When profile_id is provided, links the analysis results to that profile.
    """
    from app.models.profile import Profile as ProfileModel

    db_profile = None
    user_id = None

    if request.profile_id:
        # Load profile from database
        db_profile = await db.get(ProfileModel, request.profile_id)
        if not db_profile:
            raise HTTPException(status_code=404, detail="Profile not found")

        # Build profile dict from DB record for orchestrator
        pd = db_profile.profile_data or {}
        profile = {
            "id": db_profile.id,
            "name": db_profile.name,
            "current_role": db_profile.current_role,
            "target_role": db_profile.target_role,
            "industry": db_profile.industry,
            "experience_years": db_profile.experience_years,
            "ai_exposure_level": db_profile.ai_exposure_level,
            "learning_intent": db_profile.learning_intent,
            "tools_used": pd.get("tools_used", []),
            "technical_background": pd.get("technical_background", ""),
            "current_profile": pd.get("current_profile"),
            "archetype": pd.get("archetype"),
            "target_jd": pd.get("target_jd"),
            "estimated_current_skills": pd.get("estimated_current_skills"),
            "expected_skill_gaps": pd.get("expected_skill_gaps"),
        }
        user_id = db_profile.user_id
    elif request.custom_profile:
        profile = request.custom_profile
    else:
        raise HTTPException(
            status_code=400,
            detail="Either profile_id or custom_profile must be provided"
        )

    # Run orchestrator OUTSIDE DB transaction (20-40s of LLM calls, no DB lock)
    try:
        result = await orchestrator.execute({
            "profile": profile,
            "jd_text": request.target_jd_text,
            "target_role": request.target_role,
            "skip_assessment": request.skip_assessment,
            "self_assessed_skills": request.self_assessed_skills,
            "include_resources": True,
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

    # Quick DB save
    if not user_id:
        user = User(name=profile.get("name", "Anonymous"))
        db.add(user)
        await db.flush()
        user_id = user.id

    goal = Goal(
        user_id=user_id,
        profile_id=db_profile.id if db_profile else None,
        target_role=request.target_role or profile.get("target_role", ""),
        target_jd_text=request.target_jd_text,
        learning_intent=profile.get("learning_intent", ""),
        state_b_skills=result.get("jd_parsing", {}).get("state_b_skills", {}),
    )
    db.add(goal)
    await db.flush()

    skill_gap = SkillGap(
        user_id=user_id,
        goal_id=goal.id,
        state_a_skills=result.get("profile_analysis", {}).get("state_a_skills", {}),
        state_b_skills=result.get("jd_parsing", {}).get("state_b_skills", {}),
        gaps=result.get("gap_analysis", {}).get("gaps", []),
    )
    db.add(skill_gap)
    await db.flush()

    learning_path = LearningPath(
        user_id=user_id,
        goal_id=goal.id,
        gap_id=skill_gap.id,
        title=result.get("learning_path", {}).get("title", ""),
        description=result.get("learning_path", {}).get("description", ""),
        chapters=result.get("learning_path", {}).get("chapters", []),
        total_chapters=len(result.get("learning_path", {}).get("chapters", [])),
    )
    db.add(learning_path)
    await db.commit()

    return {
        "user_id": user_id,
        "goal_id": goal.id,
        "skill_gap_id": skill_gap.id,
        "learning_path_id": learning_path.id,
        "result": result,
    }


@router.post("/parse-jd", response_model=dict)
async def parse_job_description(request: JDParseRequest):
    """Parse a job description to extract required skills."""
    jd_parser = JDParserAgent()

    try:
        result = await jd_parser.execute({
            "jd_text": request.jd_text,
            "target_role": request.target_role,
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"JD parsing failed: {str(e)}")

    return {
        "target_role": request.target_role or result.get("role_analysis", {}).get("primary_function", ""),
        "extracted_skills": result.get("extracted_requirements", []),
        "state_b_skills": result.get("state_b_skills", {}),
        "industry": result.get("industry"),
        "experience_level": result.get("experience_level"),
        "role_analysis": result.get("role_analysis", {}),
    }


_RERANK_SYSTEM_PROMPT = """You are an expert AI skills prioritization advisor.

You will receive:
1. A list of 10 skills extracted from a job description
2. The learner's background (LinkedIn profile summary, current skills, tools used)
3. A scoring rubric

Your job: re-rank the 10 skills into a final TOP 5 for THIS specific learner using the rubric.

SCORING RUBRIC - Score each factor 1-3:
Priority Score = (Importance x 4) + (Breadth x 3) + (Momentum x 3) + (Connectivity x 2) + (Career Signal x 2)

1. IMPORTANCE (x4): How critical for the target role?
   3 = Core deliverable; can't succeed without it
   2 = Important supporting skill
   1 = Nice to have; peripheral

2. BREADTH (x3): How many scenarios does this skill apply to?
   3 = Used across most daily tasks
   2 = Used in specific but recurring situations
   1 = Narrow/niche application

3. MOMENTUM (x3): How much existing foundation does THIS LEARNER have?
   3 = Strong transferable skills from their background; quick to build on
   2 = Some related experience; moderate ramp-up
   1 = Starting from scratch; long ramp-up

4. CONNECTIVITY (x2): How much does this skill enable other skills?
   3 = Prerequisite for or amplifies 3+ other skills
   2 = Connects to 1-2 other skills
   1 = Standalone skill

5. CAREER SIGNAL (x2): How visible is this skill to hiring managers?
   3 = Directly mentioned in JD; easy to demonstrate
   2 = Implied by JD; can be shown in portfolio
   1 = Background skill; hard to demonstrate

DIVERSITY RULE: No more than 2 skills from the same domain in the final top 5.

CRITICAL: Consider what the learner ALREADY knows from their background.
Skills they already have strong transferable experience in should be DEPRIORITIZED
(low Momentum potential = low learning ROI). Focus on genuine gaps where
training creates the most value.

Return a JSON object with:
{
  "top_5": [
    {
      "rank": 1,
      "skill_id": "SK.XXX.XXX",
      "skill_name": "...",
      "domain": "D.XXX",
      "domain_label": "...",
      "required_level": 3,
      "importance": "high",
      "rationale": "Why this skill was selected for THIS learner specifically",
      "scores": {
        "importance": 3,
        "breadth": 3,
        "momentum": 3,
        "connectivity": 2,
        "career_signal": 3
      },
      "total_score": 42
    }
  ],
  "deprioritized": [
    {
      "skill_id": "SK.XXX.XXX",
      "skill_name": "...",
      "reason": "Why this was dropped for THIS learner"
    }
  ]
}"""


@router.post("/parse-jd-skills")
async def parse_jd_skills(request: JDSkillsRequest):
    """Parse a JD and return skills with proficiency descriptions.

    When learner_profile is provided, runs a 3-step chain:
    1. Analyze JD against ontology -> extract 10 skills
    2. Re-rank against learner's background using 5-factor rubric
    3. Return final ranked skills (top 5 pre-selected)

    Without learner_profile, returns JD-only analysis (original behavior).
    """
    # ── Step 1: Extract skills from JD ──────────────────────────────
    jd_parser = JDParserAgent()

    try:
        result = await jd_parser.execute({
            "jd_text": request.jd_text,
            "target_role": request.target_role,
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"JD parsing failed: {str(e)}")

    ontology = get_ontology_service()
    top_skills = result.get("top_10_target_skills", [])

    # Filter out low-importance padding
    high_medium = [s for s in top_skills if s.get("importance") in ("high", "medium", "critical")]
    if len(high_medium) >= 3:
        top_skills = high_medium

    # ── Step 2: Re-rank with learner profile (3-step chain) ─────────
    reranked_top5 = None
    if request.learner_profile and top_skills:
        try:
            reranked_top5 = await _rerank_skills_for_learner(
                top_skills, request.learner_profile, result.get("role_analysis", {}),
            )
        except Exception as e:
            logger.warning("Re-ranking failed, falling back to JD-only: %s", e)

    # ── Step 3: Enrich with ontology metadata ───────────────────────
    # If re-ranking succeeded, use its ordering; otherwise use JD order
    if reranked_top5:
        # Merge re-ranked top 5 back with remaining skills
        top5_ids = {s["skill_id"] for s in reranked_top5}
        remaining = [s for s in top_skills if s["skill_id"] not in top5_ids]
        # Re-ranked top 5 first, then remaining skills
        ordered_skills = reranked_top5 + remaining
    else:
        ordered_skills = top_skills

    enriched = []
    for skill in ordered_skills:
        skill_obj = ontology.get_skill(skill.get("skill_id", ""))
        enriched.append({
            **skill,
            "skill_description": skill_obj.get("description", "") if skill_obj else "",
            "proficiency_descriptions": ontology.get_proficiency_descriptions(skill.get("skill_id", "")),
        })

    return {
        "target_role": result.get("role_analysis", {}).get("primary_function", request.target_role or ""),
        "top_10_skills": enriched,
        "role_analysis": result.get("role_analysis", {}),
        "reranked": reranked_top5 is not None,
    }


async def _rerank_skills_for_learner(
    skills: list[dict],
    learner_profile: dict,
    role_analysis: dict,
) -> list[dict]:
    """Step 2+3 of the chain: re-rank skills using learner context + rubric.

    Makes a single LLM call with the 10 skills, learner background, and
    scoring rubric. Returns the top 5 in priority order.
    """
    # Build learner background summary
    cp = learner_profile.get("current_profile", {})
    bg_parts = []
    if cp.get("summary"):
        bg_parts.append(f"Background: {cp['summary']}")
    if cp.get("ai_experience"):
        bg_parts.append(f"AI Experience: {cp['ai_experience']}")
    if learner_profile.get("technical_background"):
        bg_parts.append(f"Technical Background: {learner_profile['technical_background']}")
    if learner_profile.get("tools_used"):
        tools = learner_profile["tools_used"]
        if isinstance(tools, list):
            tools = ", ".join(tools)
        bg_parts.append(f"AI Tools Used: {tools}")
    if learner_profile.get("learning_intent"):
        bg_parts.append(f"Learning Intent: {learner_profile['learning_intent']}")
    if learner_profile.get("experience_years"):
        bg_parts.append(f"Years of Experience: {learner_profile['experience_years']}")
    if learner_profile.get("ai_exposure_level"):
        bg_parts.append(f"AI Knowledge Level: {learner_profile['ai_exposure_level']}")

    learner_bg = "\n".join(bg_parts) if bg_parts else "No background provided"

    # Format the 10 skills
    skills_text = ""
    for s in skills:
        skills_text += (
            f"#{s.get('rank', '?')} {s.get('skill_name', '?')} "
            f"({s.get('domain_label', s.get('domain', '?'))}) "
            f"- Importance: {s.get('importance', '?')} "
            f"- Required Level: {s.get('required_level', '?')}\n"
            f"   Rationale: {s.get('rationale', 'N/A')}\n\n"
        )

    prompt = f"""Here are {len(skills)} skills extracted from the job description for the role of "{role_analysis.get('primary_function', 'Unknown')}":

{skills_text}

Here is the learner's background:
{learner_bg}

Using the scoring rubric in your system prompt, score each of the {len(skills)} skills
for THIS SPECIFIC LEARNER and return the top 5 with score breakdowns.

Remember: skills the learner already has strong transferable experience in should be
DEPRIORITIZED. Focus on genuine gaps where training creates the most value for
this person transitioning to this role."""

    llm = get_llm_provider()
    response = await llm.generate(
        prompt=prompt,
        system_prompt=_RERANK_SYSTEM_PROMPT,
        max_tokens=2048,
        temperature=0.3,
        json_mode=True,
    )

    reranked = json.loads(response.content)
    top5 = reranked.get("top_5", [])

    # Validate skill IDs exist in the original list
    valid_ids = {s["skill_id"] for s in skills}
    validated = []
    for i, s in enumerate(top5[:5], 1):
        sid = s.get("skill_id", "")
        if sid in valid_ids:
            # Merge with original skill data (preserve domain_label etc.)
            original = next((o for o in skills if o["skill_id"] == sid), {})
            merged = {**original, **s, "rank": i}
            validated.append(merged)

    if len(validated) < 3:
        raise ValueError(f"Re-ranking returned too few valid skills ({len(validated)})")

    return validated


@router.get("/gap/{user_id}")
async def get_skill_gap(
    user_id: str,
    db: AsyncSession = Depends(get_database),
):
    """Get skill gap analysis for a user."""
    from sqlalchemy import select

    result = await db.execute(
        select(SkillGap)
        .where(SkillGap.user_id == user_id)
        .order_by(SkillGap.created_at.desc())
    )
    skill_gap = result.scalars().first()

    if not skill_gap:
        raise HTTPException(status_code=404, detail="No skill gap found for user")

    return {
        "id": skill_gap.id,
        "state_a_skills": skill_gap.state_a_skills,
        "state_b_skills": skill_gap.state_b_skills,
        "gaps": skill_gap.gaps,
        "created_at": skill_gap.created_at.isoformat(),
    }


class VisualizationRequest(_BaseModel):
    """Accept the analysis result dict for visualization."""

    analysis_result: dict


@router.post("/visualization", response_class=HTMLResponse)
async def generate_visualization(request: VisualizationRequest):
    """Generate a standalone HTML ontology path visualization.

    Accepts the ``result`` field from a completed analysis and returns
    a self-contained HTML page with D3.js interactive graph.
    """
    from app.services.path_visualizer import PathVisualizer

    try:
        visualizer = PathVisualizer()
        html_content = visualizer.generate_html(request.analysis_result)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Visualization generation failed: {str(e)}",
        )

    return HTMLResponse(content=html_content)
