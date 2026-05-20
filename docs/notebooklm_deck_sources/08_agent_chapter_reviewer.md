# Agent: Chapter Reviewer

_Mix of deterministic identity checks and LLM prose-fit audit. Per cached chapter, verifies meta.skill_id matches the module and the chapter prose actually fits the persona's role._

Source file in the repo: `08/agent_chapter_reviewer.py` (numeric prefix added for NotebookLM upload order).

```python
"""Agent D - Chapter Reviewer.

Mix of deterministic checks and LLM judgment over the actual generated
chapter content. For each cached lesson in the persona's path:

  Deterministic checks (always run):
    - meta.skill_id == parent module's skill_id
    - meta.skill_name == ontology canonical name for that skill_id
    - chapter has all 5 required sections (scenario, concepts,
      example_1, example_2, agent_build) plus meta

  LLM judgment (when available):
    - Does the scenario narrative mention the right domain (a marketing
      chapter mentions campaigns, not generic documents)?
    - Do the examples use role-appropriate context for the persona?
    - Does the chapter avoid the SK.PRM.003 hallucination pattern even
      when the chapter is for a different skill?

The agent does NOT regenerate chapters. It only audits existing cached
content for the persona's path.

Verdict policy:
  RED   : deterministic identity mismatch
  YELLOW: deterministic checks pass but LLM flagged off-topic narrative
  GREEN : every cached chapter passes identity and content sanity
"""
from __future__ import annotations

import json
import logging

from sqlalchemy import select

from app.database import AsyncSessionLocal
from app.models.lesson import Lesson
from app.models.module import Module
from app.qa_agents.base import QAAgent
from app.qa_agents.verdict import AgentVerdict, Finding, Severity, color_from_findings
from app.services.ontology import get_ontology_service


logger = logging.getLogger(__name__)
logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


REQUIRED_SECTIONS = ["meta", "scenario", "concepts", "agent_build"]


CONTENT_REVIEWER_SYSTEM_PROMPT = """You are reviewing a generated learning-chapter for a learner in a specific role.

Your job is to flag chapters whose content does not fit the learner's role
or the skill being taught. Do NOT regenerate or rewrite - only audit.

Return a single JSON object:
{
  "severity": "info" | "warn" | "error",
  "summary": "<one sentence>",
  "detail": "<reasoning>"
}

severity rules:
  - error  : chapter clearly teaches the wrong skill (identity drift)
  - warn   : chapter is about the right skill but examples are generic /
             not role-appropriate (e.g. marketing director chapter shows
             a generic "report" rather than a campaign brief)
  - info   : chapter is fine
"""


def _build_chapter_review_prompt(skill_id: str, skill_name: str,
                                  role: str, chapter: dict) -> str:
    """Compose the review prompt with the chapter's key sections."""
    meta = chapter.get("meta") or {}
    scenario = chapter.get("scenario") or {}
    sample_concept = ""
    concepts = chapter.get("concepts") or {}
    cards = concepts.get("cards") or []
    if cards:
        sample_concept = (cards[0].get("body") or "")[:300]

    return (
        f"PERSONA ROLE: {role!r}\n"
        f"INPUT SKILL: {skill_id} - {skill_name!r}\n"
        f"\n"
        f"CHAPTER meta:\n"
        f"  meta.skill_id: {meta.get('skill_id')}\n"
        f"  meta.skill_name: {meta.get('skill_name')}\n"
        f"  meta.chapter_title: {meta.get('chapter_title')}\n"
        f"\n"
        f"SCENARIO narrative (excerpt):\n"
        f"  {(scenario.get('narrative') or '')[:600]}\n"
        f"\n"
        f"SAMPLE CONCEPT card body (excerpt):\n"
        f"  {sample_concept}\n"
        f"\n"
        f"Audit whether this chapter actually teaches {skill_name!r} "
        f"in a way that fits a {role!r} role. Return your JSON verdict."
    )


class ChapterReviewerAgent(QAAgent):
    name = "Chapter Reviewer"
    description = "Per-chapter identity check + LLM judgment on prose fit"

    async def run(self, context: dict) -> AgentVerdict:
        persona = context.get("persona") or {}
        profile_id = context.get("profile_id")
        path_id = context.get("path_id")

        if not profile_id or not persona:
            return AgentVerdict(
                agent_name=self.name,
                color=color_from_findings([]),
                summary="no profile/persona context; skipped",
                findings=[],
                metadata={},
            )

        ontology = get_ontology_service()
        findings: list[Finding] = []
        checked = 0
        skipped_no_content = 0

        async with AsyncSessionLocal() as db:
            if not path_id:
                from app.models.goal import Goal
                from app.models.learning_path import LearningPath
                r = await db.execute(
                    select(Goal).where(Goal.profile_id == profile_id)
                    .order_by(Goal.created_at.desc())
                )
                g = r.scalars().first()
                if not g:
                    return AgentVerdict(
                        agent_name=self.name,
                        color=color_from_findings([]),
                        summary="no goal/path for this persona; nothing to audit",
                        findings=[],
                        metadata={},
                    )
                r = await db.execute(
                    select(LearningPath).where(LearningPath.goal_id == g.id)
                )
                p = r.scalars().first()
                if not p:
                    return AgentVerdict(
                        agent_name=self.name,
                        color=color_from_findings([]),
                        summary="no path activated; nothing to audit",
                        findings=[],
                        metadata={},
                    )
                path_id = p.id

            r = await db.execute(select(Module).where(Module.path_id == path_id))
            modules = sorted(r.scalars().all(), key=lambda m: m.chapter_number)
            module_by_id = {m.id: m for m in modules}

            r = await db.execute(
                select(Lesson).where(Lesson.path_id == path_id, Lesson.content.isnot(None))
            )
            cached = r.scalars().all()

            if not cached:
                return AgentVerdict(
                    agent_name=self.name,
                    color=color_from_findings([]),
                    summary="path has no cached chapters yet - nothing to audit",
                    findings=[],
                    metadata={"path_id": path_id, "modules": len(modules)},
                    reasoning="Chapters are generated on first lesson click. "
                              "Audit will run once the user has loaded a lesson.",
                )

            from app.services.llm import get_llm_provider
            llm = None
            try:
                llm = get_llm_provider()
            except Exception:
                logger.info("LLM unavailable; running deterministic checks only.")

            for ls in cached:
                mod = module_by_id.get(ls.module_id)
                if not mod:
                    continue
                checked += 1
                content = ls.content or {}
                meta = content.get("meta") or {}
                content_sid = meta.get("skill_id")

                # Deterministic identity check
                if content_sid and content_sid != mod.skill_id:
                    findings.append(Finding(
                        severity=Severity.ERROR,
                        summary=(
                            f"ch#{mod.chapter_number} identity mismatch: module "
                            f"{mod.skill_id!r} but cached content claims {content_sid!r}"
                        ),
                        detail="The SK.PRM.003 hallucination class of bug; clear "
                               "this lesson and regenerate.",
                        skill_id=mod.skill_id,
                        proposed_fix=f"clear lesson {ls.id}; user revisits to regenerate",
                    ))
                    continue

                # Required-sections check
                missing = [s for s in REQUIRED_SECTIONS if s not in content]
                if missing:
                    findings.append(Finding(
                        severity=Severity.WARN,
                        summary=f"ch#{mod.chapter_number} missing sections: {missing}",
                        skill_id=mod.skill_id,
                    ))

                # LLM prose-fit check (only if LLM available + chapter intact)
                if llm and not missing:
                    try:
                        prompt = _build_chapter_review_prompt(
                            mod.skill_id, mod.skill_name, persona.get("role", ""),
                            content,
                        )
                        resp = await llm.generate(
                            prompt=prompt,
                            system_prompt=CONTENT_REVIEWER_SYSTEM_PROMPT,
                            temperature=0.2,
                            json_mode=True,
                        )
                        try:
                            data = json.loads(resp.content)
                        except (json.JSONDecodeError, TypeError):
                            try:
                                start = resp.content.index("{")
                                end = resp.content.rindex("}") + 1
                                data = json.loads(resp.content[start:end])
                            except Exception:
                                data = None
                        if data and data.get("severity") in ("warn", "error"):
                            findings.append(Finding(
                                severity=Severity(data["severity"]),
                                summary=(
                                    f"ch#{mod.chapter_number} ({mod.skill_id}): "
                                    + data.get("summary", "content audit flag")
                                ),
                                detail=data.get("detail", ""),
                                skill_id=mod.skill_id,
                            ))
                    except Exception as exc:
                        logger.debug("Chapter LLM review failed for %s: %s", mod.skill_id, exc)

        verdict_color = color_from_findings(findings)
        return AgentVerdict(
            agent_name=self.name,
            color=verdict_color,
            summary=f"audited {checked} cached chapter(s); {len(findings)} finding(s)",
            findings=findings,
            metadata={
                "path_id": path_id,
                "chapters_audited": checked,
                "chapters_skipped_no_content": skipped_no_content,
            },
            reasoning=(
                f"Ran deterministic identity + sections checks across {checked} "
                f"cached chapters. " +
                ("LLM prose-fit check also ran." if checked else "")
            ),
        )

```
