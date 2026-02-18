"""Orchestrator Agent - Coordinates the multi-agent workflow."""
import asyncio
import json
from datetime import datetime
from typing import Any
import uuid
from app.agents.base import BaseAgent
from app.agents.profile_analyzer import ProfileAnalyzerAgent
from app.agents.jd_parser import JDParserAgent
from app.agents.assessment_agent import AssessmentAgent
from app.agents.gap_analyzer import GapAnalyzerAgent
from app.agents.path_generator import PathGeneratorAgent
from app.agents.content_curator import ContentCuratorAgent
from app.services.path_generator import LearningPathGenerator
from app.services.ontology import get_ontology_service


class Orchestrator(BaseAgent):
    """Main orchestrator that coordinates the full analysis workflow."""

    name = "Orchestrator"
    description = "Coordinates workflow between specialized agents"

    system_prompt = """You are the orchestrator for an AI learning path generation system.
Your role is to coordinate multiple specialized agents to analyze user profiles,
parse job descriptions, identify skill gaps, and generate personalized learning paths."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.profile_analyzer = ProfileAnalyzerAgent()
        self.jd_parser = JDParserAgent()
        self.assessment_agent = AssessmentAgent()
        self.gap_analyzer = GapAnalyzerAgent()
        self.path_generator = PathGeneratorAgent()
        self.content_curator = ContentCuratorAgent()

    async def execute(self, task: dict) -> dict:
        """Execute the full analysis workflow.

        Args:
            task: {
                "profile": dict - User profile data
                "jd_text": str - Target job description
                "target_role": str - Target role title (optional)
                "skip_assessment": bool - Skip quiz assessment
                "include_resources": bool - Include curated resources
            }

        Returns:
            Complete analysis including profile analysis, JD parsing,
            gap analysis, and generated learning path
        """
        self._start_execution()
        workflow_id = str(uuid.uuid4())

        results = {
            "workflow_id": workflow_id,
            "started_at": datetime.utcnow().isoformat(),
            "steps": [],
        }

        try:
            # Step 1 & 2: Analyze Profile and Parse JD in parallel (independent operations)
            profile_result, jd_result = await asyncio.gather(
                self._execute_step(
                    "profile_analysis",
                    self.profile_analyzer,
                    {"profile": task.get("profile", {})}
                ),
                self._execute_step(
                    "jd_parsing",
                    self.jd_parser,
                    {
                        "jd_text": task.get("jd_text", ""),
                        "target_role": task.get("target_role", ""),
                    }
                )
            )
            results["profile_analysis"] = profile_result
            results["steps"].append({"step": "profile_analysis", "status": "completed"})
            results["jd_parsing"] = jd_result
            results["steps"].append({"step": "jd_parsing", "status": "completed"})

            # Step 3: Optional Assessment
            state_a_skills = profile_result.get("state_a_skills", {})
            if not task.get("skip_assessment", True):
                # Generate and get assessment
                assessment_result = await self._execute_step(
                    "assessment",
                    self.assessment_agent,
                    {
                        "action": "generate",
                        "skill_ids": list(jd_result.get("state_b_skills", {}).keys())[:5],
                        "industry": task.get("profile", {}).get("industry", ""),
                    }
                )
                results["assessment"] = assessment_result
                results["steps"].append({"step": "assessment", "status": "completed"})
                # Note: In real flow, would wait for user responses and then score
            else:
                results["assessment"] = None
                results["steps"].append({"step": "assessment", "status": "skipped"})

            # Step 4: Gap Analysis
            gap_result = await self._execute_step(
                "gap_analysis",
                self.gap_analyzer,
                {
                    "state_a_skills": state_a_skills,
                    "state_b_skills": jd_result.get("state_b_skills", {}),
                    "learning_intent": task.get("profile", {}).get("learning_intent", ""),
                    "industry": task.get("profile", {}).get("industry", ""),
                    "jd_requirements": jd_result.get("extracted_requirements", []),
                }
            )
            results["gap_analysis"] = gap_result
            results["steps"].append({"step": "gap_analysis", "status": "completed"})

            # Step 4b: Build deterministic scaffold from state_a/state_b
            # This ensures chapter structure is gap-driven with prerequisite
            # ordering and domain diversity — not left to LLM discretion.
            #
            # LLM agents may return skill IDs not in the ontology (e.g.
            # "AI_Fundamentals" instead of "SK.FND.001").  The deterministic
            # gap engine validates IDs strictly, so we filter first.
            ontology = get_ontology_service()
            valid_state_a = {
                sid: lvl for sid, lvl in state_a_skills.items()
                if ontology.get_skill(sid) is not None
            }
            state_b_skills = jd_result.get("state_b_skills", {})
            valid_state_b = {
                sid: lvl for sid, lvl in state_b_skills.items()
                if ontology.get_skill(sid) is not None
            }

            # Fallback: when RAG is unavailable the JD parser may return
            # entirely invented skill IDs (e.g. "SKL001"), leaving
            # valid_state_b empty.  In that case, derive state_b from
            # the profile's expected_skill_gaps which contain curated
            # ontology IDs.
            profile_data = task.get("profile", {})
            if not valid_state_b and "expected_skill_gaps" in profile_data:
                for gap_group in profile_data["expected_skill_gaps"]:
                    for sid in gap_group.get("skills", []):
                        skill = ontology.get_skill(sid)
                        if skill:
                            valid_state_b[sid] = skill["level"]

            # Build role_context for better gap prioritization
            role_context = None
            if profile_data.get("target_role") or profile_data.get("expected_skill_gaps"):
                role_context = {
                    "target_role": profile_data.get("target_role", ""),
                    "target_domains": [
                        g["domain"]
                        for g in profile_data.get("expected_skill_gaps", [])
                        if "domain" in g
                    ],
                }

            deterministic = LearningPathGenerator(ontology_service=ontology)
            scaffold_result = deterministic.generate_path(
                valid_state_a, valid_state_b, role_context=role_context,
            )
            results["steps"].append({
                "step": "deterministic_scaffold", "status": "completed",
            })

            # Step 5: Generate Learning Path (scaffold-enrichment mode)
            path_result = await self._execute_step(
                "path_generation",
                self.path_generator,
                {
                    "chapter_scaffold": scaffold_result["chapters"],
                    "prioritized_gaps": gap_result.get("gaps", []),
                    "industry": task.get("profile", {}).get("industry", ""),
                    "learning_intent": task.get("profile", {}).get("learning_intent", ""),
                    "profile_summary": profile_result.get("profile_summary", ""),
                    "num_chapters": scaffold_result["total_chapters"],
                    "inferred_skill_count": scaffold_result.get("inferred_skill_count"),
                    "confidence_weighted": scaffold_result.get("confidence_weighted"),
                    "decay_applied": scaffold_result.get("decay_applied"),
                    "avg_decay_factor": scaffold_result.get("avg_decay_factor"),
                }
            )
            results["learning_path"] = path_result
            results["steps"].append({"step": "path_generation", "status": "completed"})

            # Step 6: Optional Content Curation
            if task.get("include_resources", True):
                resources_result = await self._execute_step(
                    "content_curation",
                    self.content_curator,
                    {
                        "chapters": path_result.get("chapters", []),
                        "industry": task.get("profile", {}).get("industry", ""),
                    }
                )
                # Merge resources into chapters
                for ch_resource in resources_result.get("chapter_resources", []):
                    ch_num = ch_resource.get("chapter_number")
                    for chapter in path_result.get("chapters", []):
                        if chapter.get("chapter_number") == ch_num:
                            chapter["resources"] = ch_resource.get("resources", [])
                results["steps"].append({"step": "content_curation", "status": "completed"})
            else:
                results["steps"].append({"step": "content_curation", "status": "skipped"})

            # Generate summary
            results["summary"] = self._generate_summary(results)
            results["status"] = "completed"

        except Exception as e:
            results["status"] = "error"
            results["error"] = str(e)
            raise

        finally:
            results["completed_at"] = datetime.utcnow().isoformat()
            results["duration_ms"] = self._end_execution()

        return results

    async def _execute_step(
        self,
        step_name: str,
        agent: BaseAgent,
        task: dict,
    ) -> dict:
        """Execute a single workflow step."""
        try:
            result = await agent.execute(task)
            return result
        except Exception as e:
            return {"error": str(e), "status": "failed"}

    def _generate_summary(self, results: dict) -> dict:
        """Generate a high-level summary of the analysis."""
        profile = results.get("profile_analysis", {})
        jd = results.get("jd_parsing", {})
        gaps = results.get("gap_analysis", {})
        path = results.get("learning_path", {})

        return {
            "profile_summary": profile.get("profile_summary", ""),
            "target_role": jd.get("role_analysis", {}).get("primary_function", ""),
            "total_gaps_identified": len(gaps.get("gaps", [])),
            "critical_gaps": gaps.get("summary", {}).get("critical_gaps", 0),
            "learning_path_title": path.get("title", ""),
            "total_chapters": len(path.get("chapters", [])),
            "estimated_learning_hours": path.get("total_estimated_hours", 0),
            "primary_domains": gaps.get("summary", {}).get("primary_domains", []),
            "recommendations": gaps.get("recommendations", [])[:3],
        }


# Singleton instance
_orchestrator_instance = None


def get_orchestrator() -> Orchestrator:
    """Get singleton orchestrator instance."""
    global _orchestrator_instance
    if _orchestrator_instance is None:
        _orchestrator_instance = Orchestrator()
    return _orchestrator_instance
