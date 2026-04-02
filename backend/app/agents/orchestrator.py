"""Orchestrator Agent - Coordinates the multi-agent workflow."""
import asyncio
import json
import logging
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
from app.services.path_generator import LearningPathGenerator, MAX_CHAPTERS
from app.services.ontology import get_ontology_service
from app.data.role_templates import ROLE_TEMPLATES


logger = logging.getLogger(__name__)


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

            # Pass top-10 skill breakdowns through to the frontend
            top_10_current = profile_result.get("top_10_current_skills", [])
            top_10_target = jd_result.get("top_10_target_skills", [])
            results["top_10_current_skills"] = top_10_current

            # Re-rank top 10 using learner profile + 5-factor rubric
            try:
                from app.api.routes.analysis import _rerank_skills_for_learner
                learner_profile = task.get("profile", {})
                reranked = await _rerank_skills_for_learner(
                    top_10_target, learner_profile, jd_result.get("role_analysis", {}),
                )
                if reranked and len(reranked) >= 3:
                    # Use re-ranked top 5 as the primary skills, rest follow
                    top5_ids = {s["skill_id"] for s in reranked}
                    remaining = [s for s in top_10_target if s["skill_id"] not in top5_ids]
                    top_10_target = reranked + remaining
                    logger.info("Re-ranked skills: top 5 = %s", [s["skill_id"] for s in reranked])
            except Exception as e:
                logger.warning("Re-ranking failed in orchestrator, using JD order: %s", e)

            results["top_10_target_skills"] = top_10_target

            # Extract state_a_skills early — needed for gap computation below
            state_a_skills = profile_result.get("state_a_skills", {})

            # Override with user's self-assessed proficiency levels
            self_assessed = task.get("self_assessed_skills") or {}
            if self_assessed:
                for sid, level in self_assessed.items():
                    state_a_skills[sid] = level
                logger.info(
                    "Applied %d self-assessed skill overrides to state_a",
                    len(self_assessed),
                )

            # Build top-10 skill gaps: start from target skills, compare vs current
            state_a_lookup = {s["skill_id"]: s["current_level"] for s in top_10_current}
            top_10_gaps = []
            for skill in top_10_target:
                current = state_a_lookup.get(
                    skill["skill_id"],
                    state_a_skills.get(skill["skill_id"], 0),
                )
                required = skill["required_level"]
                top_10_gaps.append({
                    "rank": skill["rank"],
                    "skill_id": skill["skill_id"],
                    "skill_name": skill["skill_name"],
                    "domain": skill["domain"],
                    "domain_label": skill.get("domain_label", ""),
                    "current_level": current,
                    "required_level": required,
                    "gap": max(0, required - current),
                    "importance": skill.get("importance", ""),
                    "rationale": skill.get("rationale", ""),
                })
            results["top_10_skill_gaps"] = top_10_gaps

            # Step 3: Optional Assessment
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
            # Build learner background summary for Momentum scoring
            _profile = task.get("profile", {})
            _cp = _profile.get("current_profile") or {}
            _bg_parts = []
            if _cp.get("summary"):
                _bg_parts.append(_cp["summary"])
            if _profile.get("technical_background"):
                _bg_parts.append(f"Technical background: {_profile['technical_background']}")
            if _profile.get("tools_used"):
                _tools = _profile["tools_used"]
                if isinstance(_tools, list):
                    _tools = ", ".join(_tools)
                _bg_parts.append(f"AI tools used: {_tools}")
            _learner_bg = " | ".join(_bg_parts) if _bg_parts else ""

            gap_result = await self._execute_step(
                "gap_analysis",
                self.gap_analyzer,
                {
                    "state_a_skills": state_a_skills,
                    "state_b_skills": jd_result.get("state_b_skills", {}),
                    "learning_intent": _profile.get("learning_intent", ""),
                    "industry": _profile.get("industry", ""),
                    "jd_requirements": jd_result.get("extracted_requirements", []),
                    "learner_background": _learner_bg,
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
            # the profile's expected_skill_gaps.
            profile_data = task.get("profile", {})
            if not valid_state_b and profile_data.get("expected_skill_gaps"):
                for gap_group in profile_data["expected_skill_gaps"]:
                    for sid in gap_group.get("skills", []):
                        skill = ontology.get_skill(sid)
                        if skill:
                            valid_state_b[sid] = skill["level"]

            # Role template overlay: when a client-approved role
            # template exists, overlay its confirmed target levels on
            # state_b — whether state_b came from the LLM JD parser
            # or the fallback above.  This corrects LLM-guessed
            # target levels to match what the client specified and
            # keeps state_b focused on approved skills.
            template = ROLE_TEMPLATES.get(
                profile_data.get("target_role", "")
            )
            if template:
                for sid, level in template.items():
                    if sid in valid_state_b:
                        valid_state_b[sid] = max(
                            valid_state_b[sid], level,
                        )
                    else:
                        valid_state_b[sid] = level
            elif profile_data.get("expected_skill_gaps"):
                # No template: add only the specific skills listed
                # in each gap group (not the entire domain).
                for gap_group in profile_data["expected_skill_gaps"]:
                    for sid in gap_group.get("skills", []):
                        if sid not in valid_state_b:
                            skill = ontology.get_skill(sid)
                            if skill:
                                valid_state_b[sid] = skill["level"]

            # When a role template is active, rebuild top_10_target
            # and top_10_gaps from the template skills so the Skills
            # Gap Overview and Journey Roadmap "remaining" section
            # match the scaffold chapters (which use valid_state_b).
            if template:
                rebuilt = []
                for sid, level in template.items():
                    skill_obj = ontology.get_skill(sid)
                    if not skill_obj:
                        continue
                    domain_obj = ontology.get_domain(
                        skill_obj["domain"]
                    )
                    current = valid_state_a.get(sid, 0)
                    gap = max(0, level - current)
                    if gap <= 0:
                        continue
                    importance = (
                        "CRITICAL" if gap >= 3
                        else "HIGH" if gap >= 2
                        else "MEDIUM"
                    )
                    rebuilt.append({
                        "rank": 0,
                        "skill_id": sid,
                        "skill_name": skill_obj["name"],
                        "domain": skill_obj["domain"],
                        "domain_label": (
                            domain_obj["label"]
                            if domain_obj else ""
                        ),
                        "required_level": level,
                        "current_level": current,
                        "gap": gap,
                        "importance": importance,
                        "rationale": (
                            f"Required for "
                            f"{profile_data.get('target_role', '')} "
                            f"role"
                        ),
                    })
                rebuilt.sort(
                    key=lambda x: (-x["gap"], -x["required_level"])
                )
                for i, entry in enumerate(rebuilt[:10]):
                    entry["rank"] = i + 1
                top_10_target = rebuilt[:10]  # noqa: F841
                top_10_gaps = rebuilt[:10]
                results["top_10_target_skills"] = top_10_target
                results["top_10_skill_gaps"] = top_10_gaps

            # Fallback for custom profiles (no expected_skill_gaps):
            # match LLM-returned skill names against ontology via text
            # search, then try role-based domain matching.
            if not valid_state_b:
                valid_state_b = self._derive_state_b_from_jd(
                    jd_result, profile_data, ontology,
                )

            # Build role_context for better gap prioritization
            target_domains = [
                g["domain"]
                for g in (profile_data.get("expected_skill_gaps") or [])
                if "domain" in g
            ]
            role_context = None
            if profile_data.get("target_role") or target_domains:
                # If no explicit target_domains, derive from the
                # skills we just resolved in valid_state_b.
                if not target_domains and valid_state_b:
                    seen = set()
                    for sid in valid_state_b:
                        parts = sid.split(".")
                        if len(parts) >= 3:
                            did = f"D.{parts[1]}"
                            if did not in seen:
                                seen.add(did)
                                target_domains.append(did)
                # When a role template exists, pass its skill IDs as
                # priority_skills so the path generator can protect
                # them from mandatory-category swaps.
                _tpl = ROLE_TEMPLATES.get(
                    profile_data.get("target_role", "")
                )
                # Extract primary domains from JD parser's role_analysis
                primary_domains = jd_result.get("role_analysis", {}).get("key_domains", [])

                role_context = {
                    "target_role": profile_data.get("target_role", ""),
                    "target_domains": target_domains,
                    "primary_domains": primary_domains,
                    "priority_skills": set(_tpl.keys()) if _tpl else set(),
                }

            # Build skill_importance dict from JD parser's importance ratings
            skill_importance: dict[str, str] = {}
            for skill in jd_result.get("top_10_target_skills", []):
                sid = skill.get("skill_id")
                imp = skill.get("importance", "medium")
                if sid:
                    skill_importance[sid] = imp

            deterministic = LearningPathGenerator(ontology_service=ontology)
            scaffold_result = deterministic.generate_path(
                valid_state_a, valid_state_b, role_context=role_context,
                skill_importance=skill_importance,
            )
            results["steps"].append({
                "step": "deterministic_scaffold", "status": "completed",
            })

            # Reconcile gap_analysis to match the deterministic scaffold.
            # The LLM gap analyzer and the deterministic gap engine use
            # different prioritization, so the displayed gaps should
            # reflect the actual chapters that will be generated.
            # NOTE: scaffold chapters use "primary_skill_id" / "primary_skill_name"
            # (from LearningPathGenerator._build_chapter), not "skill_id".
            scaffold_chapters = scaffold_result.get("chapters", [])
            if scaffold_chapters:
                # Build aligned gaps list from scaffold chapters
                aligned_gaps = []
                for ch in scaffold_chapters:
                    sid = ch.get("primary_skill_id", ch.get("skill_id", ""))
                    skill_obj = ontology.get_skill(sid)
                    domain = skill_obj["domain"] if skill_obj else ""
                    skill_name = ch.get("primary_skill_name", ch.get("skill_name", sid))
                    current = ch.get("current_level", 0)
                    target = ch.get("target_level", 1)
                    aligned_gaps.append({
                        "skill_id": sid,
                        "skill_name": skill_name,
                        "domain": domain,
                        "current_level": current,
                        "target_level": target,
                        "gap": target - current,
                        "priority": ch.get("chapter_number", 0),
                        "priority_reason": "Selected by deterministic gap engine",
                    })
                gap_result["gaps"] = aligned_gaps
                gap_result["summary"] = {
                    "total_gaps": len(aligned_gaps),
                    "critical_gaps": len([g for g in aligned_gaps if g["gap"] >= 2]),
                    "primary_domains": list({
                        g["domain"] for g in aligned_gaps if g.get("domain")
                    }),
                }
                results["gap_analysis"] = gap_result

                # Also reconcile top_10_skill_gaps to match scaffold
                # chapters so the Skills Gap Overview displays the
                # same skills as the learning path.
                reconciled_top = []
                for ch in scaffold_chapters:
                    sid = ch.get(
                        "primary_skill_id", ch.get("skill_id", "")
                    )
                    skill_obj = ontology.get_skill(sid)
                    if not skill_obj:
                        continue
                    domain_obj = ontology.get_domain(
                        skill_obj["domain"]
                    )
                    current = ch.get("current_level", 0)
                    target = ch.get("target_level", 1)
                    gap = target - current
                    reconciled_top.append({
                        "rank": ch.get("chapter_number", 0),
                        "skill_id": sid,
                        "skill_name": skill_obj["name"],
                        "domain": skill_obj["domain"],
                        "domain_label": (
                            domain_obj["label"]
                            if domain_obj else ""
                        ),
                        "required_level": target,
                        "current_level": current,
                        "gap": gap,
                        "importance": (
                            "CRITICAL" if gap >= 3
                            else "HIGH" if gap >= 2
                            else "MEDIUM"
                        ),
                        "rationale": (
                            f"Selected for your learning path"
                            f" \u2013 advances from L{current}"
                            f" to L{target}"
                        ),
                    })
                results["top_10_skill_gaps"] = reconciled_top
                results["top_10_target_skills"] = reconciled_top

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
            # If LLM enrichment failed (no chapters), fall back to
            # the deterministic scaffold so we never return 0 chapters.
            if not path_result.get("chapters") and scaffold_result.get("chapters"):
                logger.warning(
                    "Path generation returned no chapters (error: %s). "
                    "Falling back to deterministic scaffold.",
                    path_result.get("error", "unknown"),
                )
                path_result = self.path_generator._scaffold_fallback(
                    scaffold_result["chapters"]
                )
                results["steps"].append({"step": "path_generation", "status": "fallback"})
            else:
                results["steps"].append({"step": "path_generation", "status": "completed"})

            results["learning_path"] = path_result

            # Journey Roadmap — bridge gap analysis and learning path
            # Shows users where this +1-per-chapter path fits in
            # their full multi-path journey to the target role.
            path_chapters = path_result.get("chapters", [])
            path_skill_ids = {
                ch.get("primary_skill_id") or ch.get("skill_id", "")
                for ch in path_chapters
            }

            # Compute ALL gaps from state_a vs state_b so the numbers
            # add up correctly (not just top-10).
            all_gaps_full = []
            for sid, required_level in valid_state_b.items():
                current = valid_state_a.get(sid, 0)
                gap = max(0, required_level - current)
                if gap > 0:
                    skill_obj = ontology.get_skill(sid)
                    if skill_obj:
                        domain_obj = ontology.get_domain(
                            skill_obj["domain"]
                        )
                        all_gaps_full.append({
                            "skill_id": sid,
                            "skill_name": skill_obj["name"],
                            "domain": skill_obj["domain"],
                            "domain_label": (
                                domain_obj["label"]
                                if domain_obj else ""
                            ),
                            "current_level": current,
                            "target_level": required_level,
                            "gap": gap,
                        })
            all_gaps_full.sort(
                key=lambda x: (-x["gap"], x["skill_id"])
            )
            results["all_skill_gaps"] = all_gaps_full

            # Fit score: how close the person is to the target role.
            # Calculated as: sum(min(current, required)) / sum(required)
            # across all state_b skills.  0.0 = no match, 1.0 = perfect.
            total_required = sum(valid_state_b.values())
            total_current_matched = sum(
                min(valid_state_a.get(sid, 0), req)
                for sid, req in valid_state_b.items()
            )
            fit_score = (
                round(total_current_matched / total_required, 2)
                if total_required > 0 else 0.0
            )
            results["fit_score"] = fit_score

            total_gap_levels = sum(
                g["gap"] for g in all_gaps_full
            )
            all_gaps_map = {
                g["skill_id"]: g for g in all_gaps_full
            }
            # path_closes: only count chapters that address a state_b
            # skill (prerequisite/category fills not in state_b don't
            # close any of the total_gap_levels).
            path_closes = sum(
                1 for ch in path_chapters
                if (ch.get("primary_skill_id")
                    or ch.get("skill_id", "")) in all_gaps_map
            )

            # Build skills_addressed from CHAPTERS directly (not
            # top_10_gaps intersection) so prerequisites and mandatory
            # category fills appear in "This Path Covers".
            skills_addressed = []
            for ch in path_chapters:
                sid = ch.get("primary_skill_id") or ch.get("skill_id", "")
                if not sid:
                    continue
                skill_obj = ontology.get_skill(sid)
                domain_obj = (
                    ontology.get_domain(skill_obj["domain"])
                    if skill_obj else None
                )
                current = ch.get("current_level", 0)
                after = ch.get("target_level", current + 1)
                required = valid_state_b.get(sid, after)
                skills_addressed.append({
                    "skill_id": sid,
                    "skill_name": (
                        ch.get("primary_skill_name")
                        or ch.get("skill_name", sid)
                    ),
                    "domain_label": (
                        domain_obj["label"] if domain_obj else ""
                    ),
                    "current_level": current,
                    "after_path_level": after,
                    "required_level": required,
                    "gap_closed": after - current,
                    "gap_remaining": max(0, required - after),
                })

            # skills_remaining: ALL remaining gaps — includes partial
            # gaps on addressed skills AND full gaps on other skills.
            # Uses all_gaps_full perspective (state_a → state_b) so that
            # path_closes + sum(remaining.gap) = total_gap_levels.
            skills_remaining = []
            for gap_entry in all_gaps_full:
                sid = gap_entry["skill_id"]
                if sid in path_skill_ids:
                    # Skill IS in current path — path closes 1 of
                    # its gap levels; remaining = original_gap - 1.
                    remaining_gap = gap_entry["gap"] - 1
                    if remaining_gap > 0:
                        skills_remaining.append({
                            "skill_id": sid,
                            "skill_name": gap_entry["skill_name"],
                            "domain_label": gap_entry.get(
                                "domain_label", ""
                            ),
                            "current_level": gap_entry[
                                "current_level"
                            ],
                            "required_level": gap_entry[
                                "target_level"
                            ],
                            "gap": remaining_gap,
                            "partial": True,
                        })
                else:
                    skills_remaining.append({
                        "skill_id": sid,
                        "skill_name": gap_entry["skill_name"],
                        "domain_label": gap_entry.get(
                            "domain_label", ""
                        ),
                        "current_level": gap_entry["current_level"],
                        "required_level": gap_entry["target_level"],
                        "gap": gap_entry["gap"],
                        "partial": False,
                    })

            remaining_levels = total_gap_levels - path_closes
            hours_per_chapter = (
                path_result.get("total_estimated_hours", 0)
                / max(len(path_chapters), 1)
            )
            results["journey_roadmap"] = {
                "path_number": 1,
                "total_gap_levels": total_gap_levels,
                "path_closes_levels": path_closes,
                "remaining_gap_levels": remaining_levels,
                "estimated_total_paths": (
                    1 + -(-remaining_levels // MAX_CHAPTERS)
                    if remaining_levels > 0 else 1
                ),
                "skills_addressed": skills_addressed,
                "skills_remaining": skills_remaining,
            }
            results["full_journey_estimate"] = {
                "total_skills_with_gaps": len(all_gaps_full),
                "total_gap_levels": total_gap_levels,
                "total_estimated_chapters": total_gap_levels,
                "total_estimated_hours": round(
                    total_gap_levels * hours_per_chapter, 1
                ),
                "total_estimated_paths": (
                    1 + -(-remaining_levels // MAX_CHAPTERS)
                    if remaining_levels > 0 else 1
                ),
            }

            # Generate summary (needed for exec intro)
            results["summary"] = self._generate_summary(results)

            # Step 6 + 7: Content Curation + Executive Intro IN PARALLEL
            # These are independent — run concurrently for ~8s savings.
            exec_intro_task = self._generate_executive_intro(
                profile_data=task.get("profile", {}),
                profile_summary=profile_result.get("profile_summary", ""),
                fit_score=fit_score,
                total_gaps=len(all_gaps_full),
                total_chapters=len(path_chapters),
                target_role=results["summary"].get("target_role", ""),
                primary_domains=results["summary"].get("primary_domains", []),
            )

            if task.get("include_resources", True):
                curation_task = self._execute_step(
                    "content_curation",
                    self.content_curator,
                    {
                        "chapters": path_result.get("chapters", []),
                        "industry": task.get("profile", {}).get("industry", ""),
                    }
                )
                resources_result, exec_intro = await asyncio.gather(
                    curation_task, exec_intro_task,
                )
                # Merge resources into chapters
                for ch_resource in resources_result.get("chapter_resources", []):
                    ch_num = ch_resource.get("chapter_number")
                    for chapter in path_result.get("chapters", []):
                        if chapter.get("chapter_number") == ch_num:
                            chapter["resources"] = ch_resource.get("resources", [])
                results["steps"].append({"step": "content_curation", "status": "completed"})
            else:
                exec_intro = await exec_intro_task
                results["steps"].append({"step": "content_curation", "status": "skipped"})

            results["executive_introduction"] = exec_intro

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
            logger.error(
                "Step '%s' (%s) failed: %s",
                step_name, agent.name, e,
                exc_info=True,
            )
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
            "recommendations": self._build_recommendations(path),
        }

    @staticmethod
    def _derive_state_b_from_jd(
        jd_result: dict,
        profile_data: dict,
        ontology,
    ) -> dict[str, int]:
        """Derive valid state_b when JD parser returns non-ontology IDs.

        Strategy:
        0. Match top_10_target_skills skill names against ontology (most reliable)
        1. Match extracted_requirements skill names against ontology
        2. Match target role text against ontology roles for focus domains
        3. Final fallback: foundational AI domains
        """
        state_b: dict[str, int] = {}

        # Strategy 0: map top-10 target skill names to ontology.
        # This is the most reliable strategy because the JD parser's
        # structured output includes descriptive skill names even when
        # the IDs themselves are invalid.
        top10_target = jd_result.get("top_10_target_skills", [])
        for entry in top10_target:
            skill_name = entry.get("skill_name", "")
            if not skill_name:
                continue
            matches = ontology.search_skills(skill_name)
            if matches:
                best = matches[0]
                state_b[best["id"]] = max(
                    state_b.get(best["id"], 0),
                    entry.get("required_level", best["level"]),
                )

        if len(state_b) >= 5:
            logger.info(
                "state_b derived from top-10 skill name matching: %d skills",
                len(state_b),
            )
            return state_b

        # Strategy 1: match JD parser skill names to ontology
        extracted_reqs = jd_result.get("extracted_requirements", [])
        for req in extracted_reqs:
            skill_name = req.get("skill_name", "")
            if not skill_name:
                continue
            matches = ontology.search_skills(skill_name)
            if matches:
                best = matches[0]
                state_b[best["id"]] = best["level"]

        if len(state_b) >= 5:
            logger.info(
                "state_b derived from JD skill name matching: %d skills",
                len(state_b),
            )
            return state_b

        # Strategy 2: match target role against ontology roles
        target_role = (
            profile_data.get("target_role", "")
            or jd_result.get("role_analysis", {}).get("primary_function", "")
        )
        if target_role:
            target_lower = target_role.lower()
            for role in ontology.roles:
                role_label = role.get("label", "").lower()
                # Check if any significant word from the target role
                # appears in the ontology role label or vice versa.
                target_words = {
                    w for w in target_lower.split()
                    if len(w) > 3 and w not in {"with", "from", "this", "that", "will", "have"}
                }
                role_words = {
                    w for w in role_label.split()
                    if len(w) > 3
                }
                if target_words & role_words:
                    for domain_id in role.get("focus_domains", []):
                        for skill in ontology.get_skills_by_domain(domain_id):
                            if skill["id"] not in state_b:
                                state_b[skill["id"]] = skill["level"]
                    break

        if state_b:
            logger.info(
                "state_b derived from role matching: %d skills",
                len(state_b),
            )
            return state_b

        # Strategy 3: match JD key_domains against ontology domain labels
        key_domains = jd_result.get("role_analysis", {}).get("key_domains", [])
        if key_domains:
            for kd in key_domains:
                kd_lower = kd.lower()
                for domain in ontology.domains:
                    if kd_lower in domain["label"].lower() or domain["label"].lower() in kd_lower:
                        for skill in ontology.get_skills_by_domain(domain["id"]):
                            if skill["id"] not in state_b:
                                state_b[skill["id"]] = skill["level"]

        if state_b:
            logger.info(
                "state_b derived from domain label matching: %d skills",
                len(state_b),
            )
            return state_b

        # Strategy 4: foundational AI domains as last resort
        fallback_domains = ["D.FND", "D.PRM", "D.CTIC"]
        for domain_id in fallback_domains:
            for skill in ontology.get_skills_by_domain(domain_id):
                state_b[skill["id"]] = skill["level"]

        logger.warning(
            "state_b using foundational fallback: %d skills from %s",
            len(state_b), fallback_domains,
        )
        return state_b

    async def _generate_executive_intro(
        self,
        *,
        profile_data: dict,
        profile_summary: str,
        fit_score: float,
        total_gaps: int,
        total_chapters: int,
        target_role: str,
        primary_domains: list[str],
    ) -> str:
        """Generate a personalized executive introduction narrative.

        Uses the profile data, fit score, and gap analysis to produce
        a 200-400 word narrative about the learner's career trajectory
        and what their learning path addresses.

        Falls back to a deterministic summary if the LLM call fails.
        """
        pct = round(fit_score * 100)
        domains_str = ", ".join(primary_domains[:5]) if primary_domains else "AI/ML"
        current_role = profile_data.get("current_role", "professional")
        name = profile_data.get("name", "Learner")
        industry = profile_data.get("industry", "your industry")

        prompt = f"""Write a 200-400 word personalized executive introduction for a learning pathway report.

LEARNER: {name}
CURRENT ROLE: {current_role}
TARGET ROLE: {target_role}
INDUSTRY: {industry}
PROFILE SUMMARY: {profile_summary}
FIT SCORE: {pct}% match to target role
SKILLS GAP: {total_gaps} skills need development
LEARNING PATH: {total_chapters} chapters across {domains_str}

REQUIREMENTS:
- Address the learner directly in second person ("you")
- Reference their current role and how it connects to their target
- Mention the fit score as a positive starting point
- Describe the gap areas and how this learning path addresses them
- End with an encouraging statement about their career trajectory
- Professional but warm tone
- Do NOT use bullet points — write flowing paragraphs
- Return ONLY the introduction text, no headers or formatting"""

        try:
            result = await self._call_llm_structured(
                prompt,
                {"type": "object", "properties": {"text": {"type": "string"}}},
                max_tokens=2048,
            )
            text = result.get("text", "")
            if text and len(text) > 100:
                return text
        except Exception as exc:
            logger.warning(
                "Executive introduction LLM call failed: %s", exc,
            )

        # Deterministic fallback
        return (
            f"As a {current_role} in {industry}, you bring valuable "
            f"domain expertise to your journey toward becoming a "
            f"{target_role}. Your current skill profile shows a "
            f"{pct}% match with the target role requirements, "
            f"demonstrating a solid foundation to build upon. "
            f"This personalized learning path addresses {total_gaps} "
            f"skill gaps across {domains_str} through {total_chapters} "
            f"structured chapters designed to bridge the distance "
            f"between where you are and where you want to be."
        )

    def _build_recommendations(self, path: dict) -> list[str]:
        """Generate deterministic recommendations from actual chapter data.

        Produces 3 actionable recommendations that reference the real
        domains and skills in the learning path — not the broader gap
        landscape that the LLM gap analyzer sees.
        """
        chapters = path.get("chapters", [])
        if not chapters:
            return []

        LEVEL_LABELS = {
            0: "Unaware", 1: "Aware", 2: "User",
            3: "Practitioner", 4: "Builder", 5: "Architect",
        }

        ontology = get_ontology_service()

        # Extract domain info per chapter
        chapter_info: list[dict] = []
        seen_domains: dict[str, str] = {}  # domain_id -> label
        for ch in chapters:
            sid = ch.get("skill_id") or ch.get("primary_skill_id", "")
            parts = sid.split(".")
            domain_id = f"D.{parts[1]}" if len(parts) >= 3 else None
            domain_obj = ontology.get_domain(domain_id) if domain_id else None
            domain_label = domain_obj["label"] if domain_obj else (domain_id or "Unknown")
            skill_name = ch.get("skill_name") or ch.get("primary_skill_name", sid)
            current = ch.get("current_level", 0)
            target = ch.get("target_level", 1)

            if domain_id and domain_id not in seen_domains:
                seen_domains[domain_id] = domain_label

            chapter_info.append({
                "domain_label": domain_label,
                "skill_name": skill_name,
                "current_level": current,
                "target_level": target,
            })

        foundational = [c for c in chapter_info if c["current_level"] <= 1]
        advancing = [c for c in chapter_info if c["current_level"] >= 2]
        unique_domains = list(seen_domains.values())

        recs: list[str] = []

        # Rec 1 — learning priority
        if foundational:
            names = " and ".join(
                c["skill_name"] for c in foundational[:2]
            )
            recs.append(
                f"Start with foundational skills like {names} "
                f"to build core understanding before tackling advanced topics."
            )
        elif advancing:
            names = " and ".join(
                c["skill_name"] for c in advancing[:2]
            )
            recs.append(
                f"Build on your existing knowledge by deepening "
                f"expertise in {names}."
            )

        # Rec 2 — progression pattern
        from_levels = [c["current_level"] for c in chapter_info]
        dominant_from = max(set(from_levels), key=from_levels.count)
        dominant_to = dominant_from + 1
        recs.append(
            f"Your path focuses on progressing from "
            f"{LEVEL_LABELS.get(dominant_from, f'L{dominant_from}')} to "
            f"{LEVEL_LABELS.get(dominant_to, f'L{dominant_to}')} proficiency "
            f"across {len(chapters)} chapters. Complete them in order "
            f"for best results."
        )

        # Rec 3 — domain coverage
        if len(unique_domains) > 1:
            recs.append(
                f"Your path covers {len(unique_domains)} skill domains: "
                f"{', '.join(unique_domains)}. This breadth ensures "
                f"a well-rounded AI skill set for your target role."
            )
        elif unique_domains:
            recs.append(
                f"Your path focuses deeply on {unique_domains[0]}, "
                f"building progressive mastery within this critical domain."
            )

        return recs[:3]


# Singleton instance
_orchestrator_instance = None


def get_orchestrator() -> Orchestrator:
    """Get singleton orchestrator instance."""
    global _orchestrator_instance
    if _orchestrator_instance is None:
        _orchestrator_instance = Orchestrator()
    return _orchestrator_instance
