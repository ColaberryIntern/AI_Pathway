"""Gap Analyzer Agent - Calculates and prioritizes skill gaps."""
import asyncio
import json
from app.agents.base import BaseAgent
from app.services.ontology import get_ontology_service


class GapAnalyzerAgent(BaseAgent):
    """Agent for analyzing skill gaps between State A and State B."""

    name = "GapAnalyzerAgent"
    description = "Calculates skill deltas and prioritizes gaps for learning path creation"

    system_prompt = """You are an expert learning path strategist. Your task is to analyze
the gap between a learner's current skills (State A) and their target skills (State B),
then prioritize which gaps to address first.

Consider these factors when prioritizing:
1. Job criticality - How important is this skill for the target role?
2. Prerequisites - What skills must be learned first?
3. Learning intent - What did the user say they want to focus on?
4. Difficulty estimation - How big is the jump?
5. Quick wins - Are there skills that can be gained quickly?

Create a prioritized list that balances immediate value with logical learning progression."""

    async def execute(self, task: dict) -> dict:
        """Analyze gaps between State A and State B skills.

        Args:
            task: {
                "state_a_skills": dict - Current skill levels
                "state_b_skills": dict - Required skill levels
                "learning_intent": str - User's learning goals
                "industry": str - User's industry
                "jd_requirements": list - Detailed JD requirements (optional)
            }

        Returns:
            {
                "gaps": list - Prioritized list of skill gaps
                "summary": dict - Gap analysis summary
                "recommendations": list - Learning recommendations
            }
        """
        self._start_execution()

        state_a = task.get("state_a_skills", {})
        state_b = task.get("state_b_skills", {})
        learning_intent = task.get("learning_intent", "")
        industry = task.get("industry", "")
        jd_requirements = task.get("jd_requirements", [])

        # Calculate raw gaps
        raw_gaps = self._calculate_raw_gaps(state_a, state_b)

        # Get skill details for prioritization (parallel RAG calls for better performance)
        gaps_to_process = raw_gaps[:20]
        skill_results = await asyncio.gather(
            *[self.rag.retrieve_skills(gap["skill_id"], n_results=1) for gap in gaps_to_process]
        )

        # Fallback: when RAG is unavailable, use OntologyService for skill metadata
        ontology = None
        any_rag_hit = any(skills for skills in skill_results)
        if not any_rag_hit:
            ontology = get_ontology_service()

        skill_details = []
        for gap, skills in zip(gaps_to_process, skill_results):
            if skills:
                gap.update(skills[0])
            elif ontology:
                skill_obj = ontology.get_skill(gap["skill_id"])
                if skill_obj:
                    domain = ontology.get_domain(skill_obj["domain"])
                    gap["skill_name"] = skill_obj["name"]
                    gap["domain"] = skill_obj["domain"]
                    gap["domain_label"] = domain["label"] if domain else ""
                    gap["level"] = skill_obj.get("level", 1)
            skill_details.append(gap)

        # Use LLM to prioritize
        prompt = self._build_prioritization_prompt(
            skill_details, learning_intent, industry, jd_requirements
        )

        output_schema = {
            "type": "object",
            "properties": {
                "prioritized_gaps": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "skill_id": {"type": "string"},
                            "skill_name": {"type": "string"},
                            "domain": {"type": "string"},
                            "current_level": {"type": "integer"},
                            "target_level": {"type": "integer"},
                            "gap": {"type": "integer"},
                            "priority": {"type": "integer"},
                            "priority_reason": {"type": "string"},
                            "prerequisites": {"type": "array", "items": {"type": "string"}},
                            "estimated_effort": {"type": "string"}
                        }
                    }
                },
                "summary": {
                    "type": "object",
                    "properties": {
                        "total_gaps": {"type": "integer"},
                        "critical_gaps": {"type": "integer"},
                        "primary_domains": {"type": "array", "items": {"type": "string"}},
                        "estimated_learning_time": {"type": "string"}
                    }
                },
                "recommendations": {
                    "type": "array",
                    "items": {"type": "string"}
                }
            }
        }

        result = await self._call_llm_structured(prompt, output_schema)

        # Format final gaps list
        result["gaps"] = result.pop("prioritized_gaps", [])

        self._log_execution("analyze_gaps", task, result)
        result["duration_ms"] = self._end_execution()

        return result

    def _calculate_raw_gaps(self, state_a: dict, state_b: dict) -> list:
        """Calculate raw skill gaps between states."""
        gaps = []

        for skill_id, target_level in state_b.items():
            current_level = state_a.get(skill_id, 0)
            gap = target_level - current_level

            if gap > 0:
                gaps.append({
                    "skill_id": skill_id,
                    "current_level": current_level,
                    "target_level": target_level,
                    "gap": gap,
                })

        # Sort by gap size (largest first)
        gaps.sort(key=lambda x: x["gap"], reverse=True)
        return gaps

    def _build_prioritization_prompt(
        self,
        skill_gaps: list,
        learning_intent: str,
        industry: str,
        jd_requirements: list,
    ) -> str:
        """Build the prioritization prompt."""
        gaps_str = json.dumps(skill_gaps, indent=2)
        requirements_str = json.dumps(jd_requirements[:10], indent=2) if jd_requirements else "Not provided"

        return f"""Prioritize these skill gaps for a learning path.

SKILL GAPS TO PRIORITIZE:
{gaps_str}

USER'S LEARNING INTENT:
{learning_intent or 'Not specified'}

INDUSTRY CONTEXT:
{industry or 'General'}

JOB REQUIREMENTS (for importance weighting):
{requirements_str}

Consider:
1. Which skills are most critical for the target role?
2. What prerequisites are needed before learning advanced skills?
3. What aligns best with the user's stated learning intent?
4. What provides quick wins to build momentum?
5. What's the logical learning sequence?

Return the top 10 gaps in priority order (1 = highest priority)."""
