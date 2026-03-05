"""Path Generator Agent - Creates personalized learning paths."""
import asyncio
import json
import logging
from app.agents.base import BaseAgent
from app.services.ontology import get_ontology_service
from app.services.path_quality_evaluator import PathQualityEvaluator

logger = logging.getLogger(__name__)

MAX_ENRICHMENT_ATTEMPTS = 2
QUALITY_THRESHOLD = 2.5
ENRICHMENT_PROMPT_VERSION = "v1"
BATCH_SIZE = 3          # chapters per parallel enrichment batch
BATCH_MAX_TOKENS = 22000  # tokens per batch (~7k per chapter)


class PathGeneratorAgent(BaseAgent):
    """Agent for generating personalized 5-chapter learning paths."""

    name = "PathGeneratorAgent"
    description = "Creates structured learning paths with chapters, exercises, and assessments"

    system_prompt = """You are an expert instructional designer specializing in AI/ML education.
Your task is to enrich deterministic learning-path scaffolds with high-quality
educational content for working professionals.

HARD RULES — violating any of these invalidates the output:
1. NEVER modify these immutable scaffold fields:
   chapter_number, skill_id, skill_name, current_level, target_level.
2. Produce EXACTLY the same number of chapters as the scaffold.
   Do NOT add, remove, reorder, or merge chapters.
3. Each chapter MUST contain 3-5 measurable learning objectives.
   Each objective must start with a Bloom's-taxonomy verb
   (e.g. Identify, Explain, Implement, Evaluate, Design)
   and describe an observable, assessable outcome.
4. Each chapter MUST contain exactly 1 applied_project — a
   realistic, industry-relevant deliverable the learner builds.
   Include: project_title, project_description, deliverable,
   and estimated_time_minutes.
5. Chapter complexity MUST increase across the path: earlier
   chapters use lower-order verbs (Identify, Describe, Explain);
   later chapters use higher-order verbs (Analyze, Design, Evaluate).

ENRICHMENT FIELDS you must populate for every chapter:
- title (short, descriptive)
- learning_objectives (3-5 measurable objectives)
- introduction (200-300 word personalized narrative connecting the learner's
  current role, daily work, and existing skills to this chapter's topic;
  explain what they will be able to do after completing the chapter)
- core_concepts (2-3, each with title, content, examples)
- prompting_examples (2-3 per chapter, each with: title, description,
  prompt (exact copy-paste text), expected_output, customization_tips)
- agent_examples (1-2 per chapter, each with: title, scenario,
  agent_role, instructions (multi-step list), expected_behavior, use_case)
- exercises (2 practical exercises — one hands-on, one reflection)
- applied_project (1 realistic project with deliverable)
- key_takeaways (5 concise bullet points summarizing the chapter's
  most important lessons and actionable insights)
- exact_prompt (1 copy-paste-ready prompt per chapter with: title,
  context, prompt_text (the full prompt), expected_output,
  how_to_customize)
- self_assessment_questions (3, each with question, options, answer)
- industry_context (1 paragraph)
- estimated_time_hours (typically 3-5 hours)

Also provide top-level: title, description, total_estimated_hours.
Ensure single-level progression per chapter.
Make content practical and immediately applicable.
Prompting examples and agent examples should be SPECIFIC to the chapter's
skill topic and the learner's industry — not generic boilerplate."""

    async def execute(self, task: dict) -> dict:
        """Enrich a deterministic chapter scaffold with LLM-generated content.

        When a ``chapter_scaffold`` is provided (from
        ``LearningPathGenerator``), the agent treats it as the locked
        structure — chapter count, skill assignments, and level targets
        are immutable.  The LLM only adds titles, objectives, concepts,
        exercises, assessment questions, and industry context.

        Falls back to the legacy ``prioritized_gaps`` flow when no
        scaffold is present.

        Args:
            task: {
                "chapter_scaffold": list - Deterministic chapter dicts
                    (preferred).
                "prioritized_gaps": list - Legacy gap list (fallback).
                "industry": str - User's industry
                "learning_intent": str - User's learning goals
                "profile_summary": str - Summary of user's background
                "num_chapters": int - Number of chapters (default 5)
            }

        Returns:
            {
                "title": str - Path title
                "description": str - Path description
                "chapters": list - List of enriched chapter content
                "total_estimated_hours": float
            }
        """
        self._start_execution()

        # Telemetry accumulators — updated as execution progresses.
        structural_failures = 0
        quality_failures = 0
        fallback_used = False

        scaffold = task.get("chapter_scaffold")
        industry = task.get("industry", "")
        learning_intent = task.get("learning_intent", "")
        profile_summary = task.get("profile_summary", "")

        if scaffold:
            chapters_input = scaffold
            num_chapters = len(scaffold)
            skill_ids = [ch.get("primary_skill_id", "") for ch in scaffold]
        else:
            gaps = task.get("prioritized_gaps", [])[:5]
            chapters_input = gaps
            num_chapters = task.get("num_chapters", 5)
            skill_ids = [g.get("skill_id", "") for g in gaps]

        # Get learning content from RAG for each skill (parallel calls for better performance)
        content_results = await asyncio.gather(
            *[self.rag.retrieve_learning_content(sid, industry) for sid in skill_ids]
        )
        for ch, content in zip(chapters_input, content_results):
            ch["reference_content"] = content[:3] if content else []

        # Generate path using LLM — parallel batch enrichment
        # Split chapters into batches of BATCH_SIZE and enrich in parallel.
        # Each batch gets its own LLM call with reduced token budget,
        # running concurrently for ~3x speedup on 10 chapters.
        output_schema = self._chapter_output_schema()

        # Build a full prompt for quality gate (needed regardless of path)
        prompt = self._build_generation_prompt(
            chapters_input, industry, learning_intent, profile_summary,
            num_chapters,
            is_scaffold=bool(scaffold),
            prompt_version=ENRICHMENT_PROMPT_VERSION,
        )

        if scaffold:
            batches = [
                chapters_input[i:i + BATCH_SIZE]
                for i in range(0, len(chapters_input), BATCH_SIZE)
            ]
            logger.info(
                "PathGeneratorAgent: enriching %d chapters in %d parallel "
                "batches of up to %d",
                num_chapters, len(batches), BATCH_SIZE,
            )

            batch_tasks = [
                self._enrich_batch(
                    batch, industry, learning_intent, profile_summary,
                    scaffold,
                )
                for batch in batches
            ]
            batch_results = await asyncio.gather(*batch_tasks)

            # Merge batch results into a single chapters list
            all_chapters = []
            for batch_result, batch_failures in batch_results:
                structural_failures += batch_failures
                all_chapters.extend(batch_result)

            if len(all_chapters) == num_chapters:
                result = {
                    "title": self._build_path_title(all_chapters),
                    "description": (
                        f"A personalized {num_chapters}-chapter learning path "
                        f"for {industry or 'technology'} professionals."
                    ),
                    "chapters": all_chapters,
                    "total_estimated_hours": sum(
                        ch.get("estimated_time_hours", 3.0)
                        for ch in all_chapters
                    ),
                }
            else:
                logger.error(
                    "Batch enrichment produced %d chapters (expected %d). "
                    "Falling back to scaffold.",
                    len(all_chapters), num_chapters,
                )
                result = self._scaffold_fallback(scaffold)
                fallback_used = True
        else:
            # Legacy non-scaffold path — single call (rare)
            prompt = self._build_generation_prompt(
                chapters_input, industry, learning_intent, profile_summary,
                num_chapters,
                is_scaffold=False,
                prompt_version=ENRICHMENT_PROMPT_VERSION,
            )
            result = await self._call_llm_structured(
                prompt, output_schema, max_tokens=65536,
            )
            errors = self._validate_enrichment(result, scaffold, num_chapters)
            if errors:
                logger.warning("Legacy enrichment failed: %s", errors)
                result = {"chapters": [], "title": "", "description": ""}
                fallback_used = True

        # ---------------------------------------------------------------
        # Stage 2: Soft quality gate (single retry, never blocks)
        # ---------------------------------------------------------------
        # Only runs when a scaffold is present (quality scoring requires
        # enriched chapter fields).  If quality is below threshold, one
        # additional LLM call is made with weakness feedback.  A second
        # failure is accepted and logged — path generation is never
        # blocked by low quality.
        quality_report = None
        if scaffold and result.get("chapters"):
            quality_report, quality_failures = await self._evaluate_quality(
                result, prompt, output_schema, scaffold, num_chapters,
            )

        self._log_execution("generate_path", task, result)
        duration_ms = self._end_execution()
        result["duration_ms"] = duration_ms
        if quality_report is not None:
            result["quality_report"] = quality_report

        # ---------------------------------------------------------------
        # Structured telemetry — single JSON object, never blocks
        # ---------------------------------------------------------------
        overall_score = (
            quality_report["overall_score"]
            if quality_report is not None
            else None
        )
        metrics = self._build_generation_metrics(
            persona_id=task.get("persona_id"),
            overall_score=overall_score,
            chapter_count=len(result.get("chapters", [])),
            retry_count=structural_failures + quality_failures,
            structural_failures=structural_failures,
            quality_failures=quality_failures,
            fallback_used=fallback_used,
            prompt_version=ENRICHMENT_PROMPT_VERSION,
            state_b_source=task.get("state_b_source"),
            inferred_skill_count=task.get("inferred_skill_count"),
            confidence_weighted=task.get("confidence_weighted"),
            decay_applied=task.get("decay_applied"),
            avg_decay_factor=task.get("avg_decay_factor"),
            duration_ms=duration_ms,
        )
        logger.info("path_generation_metrics %s", json.dumps(metrics))

        return result

    @staticmethod
    def _build_path_title(chapters: list[dict]) -> str:
        """Derive a descriptive path title from chapter domain labels.

        Produces titles like
        "AI Learning Path: Evaluation & Observability, Foundations, Governance"
        instead of the old "AI Learning Path: {first_skill} & Beyond".
        """
        ontology = get_ontology_service()
        domain_labels: list[str] = []
        seen: set[str] = set()
        for ch in chapters:
            sid = ch.get("primary_skill_id") or ch.get("skill_id", "")
            parts = sid.split(".")
            domain_id = f"D.{parts[1]}" if len(parts) >= 3 else None
            if domain_id and domain_id not in seen:
                seen.add(domain_id)
                domain_obj = ontology.get_domain(domain_id)
                if domain_obj:
                    domain_labels.append(domain_obj["label"])
        if not domain_labels:
            return "AI Learning Path"
        title = f"AI Learning Path: {', '.join(domain_labels[:3])}"
        if len(domain_labels) > 3:
            title += f" & {len(domain_labels) - 3} More"
        return title

    def _build_generation_prompt(
        self,
        chapters_input: list,
        industry: str,
        learning_intent: str,
        profile_summary: str,
        num_chapters: int,
        *,
        is_scaffold: bool = False,
        prompt_version: str = "v1",
    ) -> str:
        """Build the path generation prompt.

        When *is_scaffold* is True the prompt is routed through a
        versioned builder (``_build_scaffold_prompt_v1``, etc.).
        The ``prompt_version`` parameter selects which variant to use,
        enabling controlled A/B experiments on prompt phrasing.

        Non-scaffold (legacy) prompts are unversioned.
        """
        data_str = json.dumps(chapters_input, indent=2)

        if is_scaffold:
            # ----- Versioned prompt routing -----
            if prompt_version == "v1":
                return self._build_scaffold_prompt_v1(
                    data_str, industry, learning_intent,
                    profile_summary, num_chapters,
                )
            elif prompt_version == "v2":
                return self._build_scaffold_prompt_v2(
                    data_str, industry, learning_intent,
                    profile_summary, num_chapters,
                )
            elif prompt_version == "v3":
                return self._build_scaffold_prompt_v3(
                    data_str, industry, learning_intent,
                    profile_summary, num_chapters,
                )
            else:
                logger.warning(
                    "Unknown prompt version %r — falling back to v1.",
                    prompt_version,
                )
                return self._build_scaffold_prompt_v1(
                    data_str, industry, learning_intent,
                    profile_summary, num_chapters,
                )

        # Legacy fallback — raw gap list, no scaffold, unversioned.
        return self._build_legacy_prompt(
            data_str, industry, learning_intent,
            profile_summary, num_chapters,
        )

    # ------------------------------------------------------------------
    # Versioned scaffold prompts
    # ------------------------------------------------------------------

    @staticmethod
    def _build_scaffold_prompt_v1(
        data_str: str,
        industry: str,
        learning_intent: str,
        profile_summary: str,
        num_chapters: int,
    ) -> str:
        """V1 scaffold enrichment prompt — current production baseline."""
        return f"""Enrich the following deterministic learning-path scaffold.

LEARNER PROFILE:
{profile_summary}

INDUSTRY: {industry or 'General'}

LEARNING INTENT:
{learning_intent or 'Develop AI skills for career advancement'}

LOCKED CHAPTER SCAFFOLD (DO NOT CHANGE):
{data_str}

IMMUTABLE FIELDS — copy these EXACTLY for each chapter:
- chapter_number
- skill_id  (use the scaffold's "primary_skill_id" value)
- skill_name (use the scaffold's "primary_skill_name" value)
- current_level
- target_level

ENRICHMENT REQUIREMENTS — for EVERY chapter provide:
1. "title" — short, descriptive chapter title
2. "learning_objectives" — 3 to 5 measurable objectives.
   Each MUST start with a Bloom's-taxonomy action verb
   (Identify, Explain, Implement, Analyze, Evaluate, Design)
   and describe an observable outcome the learner can demonstrate.
3. "introduction" — 200-300 word personalized narrative that:
   - References the learner's current role, team context, and daily work
   - Bridges their existing skills to this chapter's topic
   - Explains what they will be able to do after completing the chapter
   - Uses second person ("you") and a supportive, professional tone
4. "core_concepts" — 2-3 items (each with title, content (100+ words), examples)
5. "prompting_examples" — 2-3 per chapter, each with:
   {{
     "title": "descriptive name",
     "description": "when and why to use this prompt",
     "prompt": "EXACT copy-paste prompt text the learner can use",
     "expected_output": "what the AI should return",
     "customization_tips": "how to adapt for their specific context"
   }}
6. "agent_examples" — 1-2 per chapter, each with:
   {{
     "title": "descriptive name",
     "scenario": "business context where this agent is useful",
     "agent_role": "the agent's defined role/persona",
     "instructions": ["step 1", "step 2", ...],
     "expected_behavior": "what the agent does end-to-end",
     "use_case": "how this maps to the target role's JD requirements"
   }}
7. "exercises" — 2 practical exercises (one hands-on, one reflection)
8. "applied_project" — 1 realistic, industry-relevant project:
   {{
     "project_title": "...",
     "project_description": "...",
     "deliverable": "...",
     "estimated_time_minutes": int
   }}
9. "key_takeaways" — exactly 5 concise bullet points summarizing the
   chapter's most important lessons, written as actionable statements
10. "exact_prompt" — 1 copy-paste-ready prompt per chapter:
   {{
     "title": "descriptive name for this prompt",
     "context": "when to use this prompt in daily work",
     "prompt_text": "THE FULL EXACT PROMPT (50-200 words)",
     "expected_output": "what the AI will produce",
     "how_to_customize": "placeholders the learner should replace"
   }}
11. "self_assessment_questions" — 3 items (question, options, answer)
12. "industry_context" — 1 paragraph for {industry or 'the general business context'}
13. "estimated_time_hours" — typically 3-5 hours

COMPLEXITY PROGRESSION:
- Chapters 1-2: use lower-order verbs (Identify, Describe, Explain)
- Middle chapters: use mid-order verbs (Apply, Implement, Compare)
- Final chapters: use higher-order verbs (Analyze, Design, Evaluate)
Projects must similarly increase in scope and autonomy.

Also provide top-level "title", "description", and "total_estimated_hours".

You MUST produce EXACTLY {num_chapters} chapters — no more, no fewer.
Do NOT add, remove, reorder, or merge chapters.
Do NOT change skill assignments or level targets."""

    @staticmethod
    def _build_scaffold_prompt_v2(
        data_str: str,
        industry: str,
        learning_intent: str,
        profile_summary: str,
        num_chapters: int,
    ) -> str:
        """V2 scaffold enrichment prompt — placeholder for experiment.

        Future changes might test:
        - Stronger few-shot examples
        - Explicit JSON template in the prompt
        - Different Bloom's verb emphasis
        """
        raise NotImplementedError(
            "Prompt v2 is a placeholder for future A/B experiments. "
            "Implement the variant before setting ENRICHMENT_PROMPT_VERSION='v2'."
        )

    @staticmethod
    def _build_scaffold_prompt_v3(
        data_str: str,
        industry: str,
        learning_intent: str,
        profile_summary: str,
        num_chapters: int,
    ) -> str:
        """V3 scaffold enrichment prompt — placeholder for experiment.

        Future changes might test:
        - Chain-of-thought enrichment
        - Role-specific system prompt overrides
        - Decomposed per-chapter prompts
        """
        raise NotImplementedError(
            "Prompt v3 is a placeholder for future A/B experiments. "
            "Implement the variant before setting ENRICHMENT_PROMPT_VERSION='v3'."
        )

    # ------------------------------------------------------------------
    # Legacy (non-scaffold) prompt
    # ------------------------------------------------------------------

    @staticmethod
    def _build_legacy_prompt(
        data_str: str,
        industry: str,
        learning_intent: str,
        profile_summary: str,
        num_chapters: int,
    ) -> str:
        """Legacy prompt for raw gap-list input (no scaffold)."""
        return f"""Create a personalized {num_chapters}-chapter learning path.

LEARNER PROFILE:
{profile_summary}

INDUSTRY: {industry or 'General'}

LEARNING INTENT:
{learning_intent or 'Develop AI skills for career advancement'}

PRIORITIZED SKILL GAPS TO ADDRESS:
{data_str}

REQUIREMENTS:
1. Create exactly {num_chapters} chapters
2. Each chapter should focus on ONE skill with single-level progression
3. Include 2-3 core concepts per chapter
4. Design 2 practical exercises per chapter (one hands-on, one reflection)
5. Include 3 self-assessment questions per chapter
6. Add industry-specific context and examples for {industry or 'the general business context'}
7. Estimate time for each chapter (typically 2-4 hours)

Make the content:
- Practical and immediately applicable
- Progressively building on previous chapters
- Relevant to the user's industry and goals
- Engaging with real-world examples"""

    # ------------------------------------------------------------------
    # Batch enrichment
    # ------------------------------------------------------------------

    @staticmethod
    def _chapter_output_schema() -> dict:
        """Return the JSON schema for enriched chapter output."""
        return {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "description": {"type": "string"},
                "chapters": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "chapter_number": {"type": "integer"},
                            "skill_id": {"type": "string"},
                            "skill_name": {"type": "string"},
                            "title": {"type": "string"},
                            "learning_objectives": {
                                "type": "array",
                                "items": {"type": "string"}
                            },
                            "current_level": {"type": "integer"},
                            "target_level": {"type": "integer"},
                            "introduction": {"type": "string"},
                            "core_concepts": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "title": {"type": "string"},
                                        "content": {"type": "string"},
                                        "examples": {
                                            "type": "array",
                                            "items": {"type": "string"}
                                        }
                                    }
                                }
                            },
                            "prompting_examples": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "title": {"type": "string"},
                                        "description": {"type": "string"},
                                        "prompt": {"type": "string"},
                                        "expected_output": {"type": "string"},
                                        "customization_tips": {"type": "string"}
                                    }
                                }
                            },
                            "agent_examples": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "title": {"type": "string"},
                                        "scenario": {"type": "string"},
                                        "agent_role": {"type": "string"},
                                        "instructions": {
                                            "type": "array",
                                            "items": {"type": "string"}
                                        },
                                        "expected_behavior": {"type": "string"},
                                        "use_case": {"type": "string"}
                                    }
                                }
                            },
                            "exercises": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "id": {"type": "string"},
                                        "title": {"type": "string"},
                                        "description": {"type": "string"},
                                        "type": {"type": "string"},
                                        "estimated_time_minutes": {"type": "integer"},
                                        "instructions": {
                                            "type": "array",
                                            "items": {"type": "string"}
                                        },
                                        "deliverable": {"type": "string"}
                                    }
                                }
                            },
                            "applied_project": {
                                "type": "object",
                                "properties": {
                                    "project_title": {"type": "string"},
                                    "project_description": {"type": "string"},
                                    "deliverable": {"type": "string"},
                                    "estimated_time_minutes": {"type": "integer"}
                                }
                            },
                            "key_takeaways": {
                                "type": "array",
                                "items": {"type": "string"}
                            },
                            "exact_prompt": {
                                "type": "object",
                                "properties": {
                                    "title": {"type": "string"},
                                    "context": {"type": "string"},
                                    "prompt_text": {"type": "string"},
                                    "expected_output": {"type": "string"},
                                    "how_to_customize": {"type": "string"}
                                }
                            },
                            "self_assessment_questions": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "question": {"type": "string"},
                                        "options": {
                                            "type": "array",
                                            "items": {"type": "string"}
                                        },
                                        "answer": {"type": "string"}
                                    }
                                }
                            },
                            "industry_context": {"type": "string"},
                            "estimated_time_hours": {"type": "number"}
                        }
                    }
                },
                "total_estimated_hours": {"type": "number"}
            }
        }

    async def _enrich_batch(
        self,
        batch: list[dict],
        industry: str,
        learning_intent: str,
        profile_summary: str,
        full_scaffold: list[dict],
    ) -> tuple[list[dict], int]:
        """Enrich a batch of chapters with retry logic.

        Returns (enriched_chapters, structural_failure_count).
        On failure, returns scaffold fallback chapters for this batch.
        """
        batch_size = len(batch)
        batch_nums = [ch["chapter_number"] for ch in batch]

        prompt = self._build_generation_prompt(
            batch, industry, learning_intent, profile_summary,
            batch_size,
            is_scaffold=True,
            prompt_version=ENRICHMENT_PROMPT_VERSION,
        )

        output_schema = self._chapter_output_schema()
        failures = 0
        last_error = ""

        for attempt in range(1, MAX_ENRICHMENT_ATTEMPTS + 1):
            retry_prompt = prompt
            if last_error:
                retry_prompt = (
                    f"{prompt}\n\n"
                    f"PREVIOUS ATTEMPT FAILED VALIDATION:\n{last_error}\n"
                    f"Fix these issues in your response."
                )

            result = await self._call_llm_structured(
                retry_prompt, output_schema, max_tokens=BATCH_MAX_TOKENS,
            )

            errors = self._validate_enrichment(result, batch, batch_size)
            if not errors:
                logger.info(
                    "Batch chapters %s enriched successfully (attempt %d)",
                    batch_nums, attempt,
                )
                return result.get("chapters", []), failures

            failures += 1
            last_error = "\n".join(f"- {e}" for e in errors)
            logger.warning(
                "Batch chapters %s failed validation (attempt %d/%d): %s",
                batch_nums, attempt, MAX_ENRICHMENT_ATTEMPTS, last_error,
            )

        # All attempts failed — return scaffold fallback for this batch
        logger.error(
            "Batch chapters %s enrichment failed after %d attempts. "
            "Using scaffold fallback.",
            batch_nums, MAX_ENRICHMENT_ATTEMPTS,
        )
        fallback = self._scaffold_fallback(batch)
        return fallback.get("chapters", []), failures

    # ------------------------------------------------------------------
    # Soft quality gate
    # ------------------------------------------------------------------

    async def _evaluate_quality(
        self,
        result: dict,
        prompt: str,
        output_schema: dict,
        scaffold: list[dict],
        num_chapters: int,
    ) -> tuple[dict, int]:
        """Run PathQualityEvaluator; retry once if below threshold.

        This method makes at most **one** additional LLM call.  It
        never raises, never blocks path generation, and never enters a
        loop.

        Returns:
            (quality_report, quality_failures) — the report dict and
            the number of quality-gate failures (0 or 1).
        """
        evaluator = PathQualityEvaluator()
        report = evaluator.evaluate(result)

        if report["overall_score"] >= QUALITY_THRESHOLD:
            logger.info(
                "PathGeneratorAgent quality passed: %.2f/5.0",
                report["overall_score"],
            )
            return report, 0

        # Quality below threshold — retry once with weakness feedback.
        weakness_text = "\n".join(
            f"- {f}" for f in report["weakness_flags"][:10]
        )
        quality_prompt = (
            f"{prompt}\n\n"
            f"QUALITY FEEDBACK (score {report['overall_score']:.1f}/5.0 "
            f"— minimum {QUALITY_THRESHOLD:.1f}):\n"
            f"{weakness_text}\n\n"
            f"Improve the weak areas listed above.  Remember:\n"
            f"- Every objective MUST start with a Bloom's-taxonomy verb\n"
            f"- Every applied_project needs a detailed description "
            f"(>= 20 words) and a specific deliverable\n"
            f"- Use lower-order verbs in early chapters, "
            f"higher-order verbs in later chapters"
        )

        retry_result = await self._call_llm_structured(
            quality_prompt, output_schema, max_tokens=65536,
        )

        # The retry must still pass structural validation.
        structural_errors = self._validate_enrichment(
            retry_result, scaffold, num_chapters,
        )
        if structural_errors:
            # Retry broke structure — keep the original result.
            logger.warning(
                "PathGeneratorAgent quality retry broke structural "
                "validation — keeping original result.  Errors: %s",
                structural_errors,
            )
            return report, 1

        # Retry passed structure — check quality again.
        retry_report = evaluator.evaluate(retry_result)

        if retry_report["overall_score"] >= QUALITY_THRESHOLD:
            # Quality improved — swap in the better result.
            logger.info(
                "PathGeneratorAgent quality improved on retry: "
                "%.2f -> %.2f/5.0",
                report["overall_score"],
                retry_report["overall_score"],
            )
            result.clear()
            result.update(retry_result)
            return retry_report, 1

        # Still below threshold — accept and log.
        if retry_report["overall_score"] > report["overall_score"]:
            # Retry is at least better — use it.
            result.clear()
            result.update(retry_result)
            report = retry_report

        logger.warning(
            "PathGeneratorAgent quality still below threshold after "
            "retry: %.2f/5.0.  Weakness flags: %s",
            report["overall_score"],
            report["weakness_flags"][:5],
        )
        return report, 1

    # ------------------------------------------------------------------
    # Structural validation
    # ------------------------------------------------------------------

    @staticmethod
    def _validate_enrichment(
        result: dict,
        scaffold: list[dict] | None,
        expected_chapters: int,
    ) -> list[str]:
        """Validate LLM output against scaffold invariants.

        Returns a list of human-readable error strings.
        An empty list means the output passed all checks.
        """
        errors: list[str] = []
        chapters = result.get("chapters")

        if not chapters or not isinstance(chapters, list):
            errors.append("Output contains no 'chapters' array.")
            return errors

        # ---- Chapter count ----
        if len(chapters) != expected_chapters:
            errors.append(
                f"Chapter count mismatch: expected {expected_chapters}, "
                f"got {len(chapters)}."
            )
            return errors  # fatal — remaining checks are meaningless

        for idx, chapter in enumerate(chapters):
            ch_label = f"Chapter {idx + 1}"

            # ---- Immutable field integrity (scaffold mode only) ----
            if scaffold:
                src = scaffold[idx]
                for scaffold_key, output_key in [
                    ("chapter_number", "chapter_number"),
                    ("primary_skill_id", "skill_id"),
                    ("primary_skill_name", "skill_name"),
                    ("current_level", "current_level"),
                    ("target_level", "target_level"),
                ]:
                    expected = src.get(scaffold_key)
                    actual = chapter.get(output_key)
                    if expected is not None and actual != expected:
                        errors.append(
                            f"{ch_label}: immutable field '{output_key}' "
                            f"changed — expected {expected!r}, got {actual!r}."
                        )

            # ---- Learning objectives: 3-5 required ----
            objectives = chapter.get("learning_objectives")
            if not objectives or not isinstance(objectives, list):
                errors.append(
                    f"{ch_label}: 'learning_objectives' is missing or empty."
                )
            elif len(objectives) < 3:
                errors.append(
                    f"{ch_label}: only {len(objectives)} objectives "
                    f"(minimum 3 required)."
                )
            elif len(objectives) > 5:
                errors.append(
                    f"{ch_label}: {len(objectives)} objectives "
                    f"(maximum 5 allowed)."
                )

            # ---- Applied project required ----
            project = chapter.get("applied_project")
            if not project or not isinstance(project, dict):
                errors.append(
                    f"{ch_label}: 'applied_project' is missing or empty."
                )
            else:
                for field in ("project_title", "project_description",
                              "deliverable"):
                    if not project.get(field):
                        errors.append(
                            f"{ch_label}: applied_project.{field} is missing."
                        )

            # ---- Introduction required (200+ chars) ----
            intro = chapter.get("introduction")
            if not intro or not isinstance(intro, str) or len(intro) < 100:
                errors.append(
                    f"{ch_label}: 'introduction' is missing or too short "
                    f"(need 200-300 words)."
                )

            # ---- Prompting examples: 2-3 required ----
            prompts = chapter.get("prompting_examples")
            if not prompts or not isinstance(prompts, list) or len(prompts) < 2:
                errors.append(
                    f"{ch_label}: need at least 2 'prompting_examples'."
                )

            # ---- Agent examples: 1-2 required ----
            agents = chapter.get("agent_examples")
            if not agents or not isinstance(agents, list) or len(agents) < 1:
                errors.append(
                    f"{ch_label}: need at least 1 'agent_examples'."
                )

            # ---- Key takeaways: exactly 5 ----
            takeaways = chapter.get("key_takeaways")
            if not takeaways or not isinstance(takeaways, list) or len(takeaways) < 5:
                errors.append(
                    f"{ch_label}: need exactly 5 'key_takeaways'."
                )

            # ---- Exact prompt required ----
            exact = chapter.get("exact_prompt")
            if not exact or not isinstance(exact, dict):
                errors.append(
                    f"{ch_label}: 'exact_prompt' is missing or empty."
                )
            elif not exact.get("prompt_text"):
                errors.append(
                    f"{ch_label}: exact_prompt.prompt_text is missing."
                )

        return errors

    # ------------------------------------------------------------------
    # Telemetry
    # ------------------------------------------------------------------

    @staticmethod
    def _build_generation_metrics(
        *,
        persona_id: str | None,
        overall_score: float | None,
        chapter_count: int,
        retry_count: int,
        structural_failures: int,
        quality_failures: int,
        fallback_used: bool,
        prompt_version: str,
        state_b_source: str | None = None,
        inferred_skill_count: int | None = None,
        confidence_weighted: bool | None = None,
        decay_applied: bool | None = None,
        avg_decay_factor: float | None = None,
        duration_ms: int | None = None,
    ) -> dict:
        """Build a structured telemetry dict for a single path generation.

        All fields are primitives — safe for JSON serialization and
        downstream log aggregation (ELK, CloudWatch, Datadog, etc.).
        """
        return {
            "event": "path_generation",
            "persona_id": persona_id,
            "prompt_version": prompt_version,
            "state_b_source": state_b_source,
            "inferred_skill_count": inferred_skill_count,
            "confidence_weighted": confidence_weighted,
            "decay_applied": decay_applied,
            "avg_decay_factor": avg_decay_factor,
            "overall_score": overall_score,
            "chapter_count": chapter_count,
            "retry_count": retry_count,
            "structural_failures": structural_failures,
            "quality_failures": quality_failures,
            "fallback_used": fallback_used,
            "duration_ms": duration_ms,
        }

    @staticmethod
    def _scaffold_fallback(scaffold: list[dict]) -> dict:
        """Build a minimal valid response from the raw scaffold.

        Used when all enrichment attempts fail, so the deterministic
        structure is never lost.  Chapters carry placeholder text that
        signals the content needs manual enrichment.
        """
        title = PathGeneratorAgent._build_path_title(scaffold)
        chapters = []
        for ch in scaffold:
            chapters.append({
                "chapter_number": ch["chapter_number"],
                "skill_id": ch["primary_skill_id"],
                "skill_name": ch["primary_skill_name"],
                "title": f"Chapter {ch['chapter_number']}: {ch['primary_skill_name']}",
                "learning_objectives": [
                    "Identify key concepts in this topic area",
                    "Explain the relevance of this skill to your role",
                    "Describe one practical application of this skill",
                ],
                "current_level": ch["current_level"],
                "target_level": ch["target_level"],
                "introduction": (
                    "This chapter introduction will be populated once "
                    "content enrichment is completed. It will contain a "
                    "personalized narrative connecting your background to "
                    "this topic. Please re-run enrichment to generate "
                    "the full content for this chapter."
                ),
                "core_concepts": [],
                "prompting_examples": [
                    {
                        "title": "Pending enrichment",
                        "description": "Prompting example pending.",
                        "prompt": "Prompt text pending enrichment.",
                        "expected_output": "Pending.",
                        "customization_tips": "Pending.",
                    },
                    {
                        "title": "Pending enrichment",
                        "description": "Prompting example pending.",
                        "prompt": "Prompt text pending enrichment.",
                        "expected_output": "Pending.",
                        "customization_tips": "Pending.",
                    },
                ],
                "agent_examples": [
                    {
                        "title": "Pending enrichment",
                        "scenario": "Agent example pending.",
                        "agent_role": "Pending.",
                        "instructions": ["Pending enrichment."],
                        "expected_behavior": "Pending.",
                        "use_case": "Pending.",
                    },
                ],
                "exercises": [],
                "applied_project": {
                    "project_title": "Pending enrichment",
                    "project_description": (
                        "This project will be populated once content "
                        "enrichment is completed."
                    ),
                    "deliverable": "To be determined",
                    "estimated_time_minutes": 60,
                },
                "key_takeaways": [
                    "Key takeaway pending enrichment.",
                    "Key takeaway pending enrichment.",
                    "Key takeaway pending enrichment.",
                    "Key takeaway pending enrichment.",
                    "Key takeaway pending enrichment.",
                ],
                "exact_prompt": {
                    "title": "Pending enrichment",
                    "context": "Pending.",
                    "prompt_text": "Exact prompt text pending enrichment.",
                    "expected_output": "Pending.",
                    "how_to_customize": "Pending.",
                },
                "self_assessment_questions": [],
                "industry_context": "",
                "estimated_time_hours": 3.0,
            })

        return {
            "title": title,
            "description": (
                "Content enrichment was unsuccessful. The deterministic "
                "chapter structure is preserved. Re-run enrichment to "
                "populate full content."
            ),
            "chapters": chapters,
            "total_estimated_hours": 3.0 * len(chapters),
        }
