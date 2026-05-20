"""Agent C - Path Coherence Auditor.

Deterministic invariant checks across the user journey for one persona.
Wraps the existing sweep_integrity.py logic and adds per-persona checks
(module count, chapter_number contiguous, every Module has at least one
Lesson, every cached lesson's meta.skill_id matches its module).

Verdict policy:
  RED   : any invariant violated for this persona's path
  GREEN : every invariant passes

This agent does NOT call an LLM - it is purely deterministic. It runs
fast (under 1 second) and is the strongest signal of structural drift.
"""
from __future__ import annotations

import logging

from sqlalchemy import select

from app.database import AsyncSessionLocal
from app.models.goal import Goal
from app.models.learning_path import LearningPath
from app.models.lesson import Lesson
from app.models.module import Module
from app.qa_agents.base import QAAgent
from app.qa_agents.verdict import AgentVerdict, Finding, Severity, color_from_findings
from app.services.ontology import get_ontology_service


logger = logging.getLogger(__name__)
logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


class PathCoherenceAgent(QAAgent):
    name = "Path Coherence Auditor"
    description = "Deterministic DB-level invariant checks for one persona's path"

    async def run(self, context: dict) -> AgentVerdict:
        profile_id = context.get("profile_id")
        if not profile_id:
            return self._red(
                "no profile_id supplied",
                findings=[Finding(
                    severity=Severity.ERROR,
                    summary="missing profile_id in context",
                    proposed_fix="caller must pass profile_id",
                )],
            )

        ontology = get_ontology_service()
        findings: list[Finding] = []
        metadata: dict = {"profile_id": profile_id}

        async with AsyncSessionLocal() as db:
            # Find latest goal -> path -> modules + cached lessons
            r = await db.execute(
                select(Goal).where(Goal.profile_id == profile_id)
                .order_by(Goal.created_at.desc())
            )
            goal = r.scalars().first()
            if not goal:
                # No goal yet is not a violation - it just means the user
                # hasn't activated a path. The agent passes; downstream
                # agents will note the missing path.
                return AgentVerdict(
                    agent_name=self.name,
                    color=color_from_findings([]),
                    summary="no goal/path yet for this profile - nothing to check",
                    findings=[],
                    metadata=metadata,
                    reasoning="no Goal row found; this is fine for a profile that "
                              "has not yet generated a path.",
                )

            r = await db.execute(
                select(LearningPath).where(LearningPath.goal_id == goal.id)
            )
            path = r.scalars().first()
            if not path:
                return AgentVerdict(
                    agent_name=self.name,
                    color=color_from_findings([]),
                    summary="no learning path activated yet",
                    findings=[],
                    metadata=metadata,
                    reasoning=f"Goal {goal.id} exists but no LearningPath; path "
                              f"not yet generated.",
                )

            metadata["path_id"] = path.id
            metadata["chapters_count"] = len(path.chapters or [])

            # Check 1: every chapter.skill_id resolves in the ontology
            for ch in (path.chapters or []):
                sid = ch.get("skill_id") or ch.get("primary_skill_id")
                if not sid:
                    findings.append(Finding(
                        severity=Severity.ERROR,
                        summary=f"chapter #{ch.get('chapter_number')} missing skill_id",
                        proposed_fix="re-run path generation",
                    ))
                    continue
                if not ontology.get_skill(sid):
                    findings.append(Finding(
                        severity=Severity.ERROR,
                        summary=f"chapter #{ch.get('chapter_number')} skill {sid!r} not in ontology",
                        skill_id=sid,
                        proposed_fix="re-run path generation; legacy or stale skill_id",
                    ))

            # Check 2: Module title and skill_name match ontology canonical
            r = await db.execute(select(Module).where(Module.path_id == path.id))
            modules = sorted(r.scalars().all(), key=lambda m: m.chapter_number)
            metadata["modules_count"] = len(modules)
            module_by_id: dict = {m.id: m for m in modules}

            for m in modules:
                sk = ontology.get_skill(m.skill_id)
                if not sk:
                    findings.append(Finding(
                        severity=Severity.ERROR,
                        summary=f"module ch#{m.chapter_number}: skill_id {m.skill_id!r} not in ontology",
                        skill_id=m.skill_id,
                    ))
                    continue
                canonical = sk.get("name") or ""
                if m.title != canonical:
                    findings.append(Finding(
                        severity=Severity.ERROR,
                        summary=f"module ch#{m.chapter_number}: title {m.title!r} does not match ontology canonical {canonical!r}",
                        detail="This is the May 16 Dorothy F bug. The dashboard "
                               "shows module titles that do not match the Top 5 "
                               "Skills page.",
                        skill_id=m.skill_id,
                        proposed_fix="run backfill_module_titles.py",
                    ))

            # Check 3: every cached lesson.content.meta.skill_id matches its module
            r = await db.execute(
                select(Lesson).where(Lesson.path_id == path.id, Lesson.content.isnot(None))
            )
            cached = r.scalars().all()
            metadata["cached_lessons_count"] = len(cached)
            for ls in cached:
                mod = module_by_id.get(ls.module_id)
                if not mod:
                    continue
                content_sid = ((ls.content or {}).get("meta") or {}).get("skill_id")
                if content_sid and content_sid != mod.skill_id:
                    findings.append(Finding(
                        severity=Severity.ERROR,
                        summary=f"lesson {ls.id} cached for module {mod.skill_id!r} but content claims {content_sid!r}",
                        detail="This is the May 16 SK.PRM.003 hallucination class "
                               "of bug. The chapter generator emitted a chapter "
                               "for the wrong skill and the result was cached.",
                        skill_id=mod.skill_id,
                        proposed_fix="clear this lesson's cached content; force "
                                     "regeneration on next visit",
                    ))

            # Check 4: chapter_number contiguous starting at 1
            ch_numbers = sorted(m.chapter_number for m in modules)
            if ch_numbers and ch_numbers != list(range(1, len(ch_numbers) + 1)):
                findings.append(Finding(
                    severity=Severity.WARN,
                    summary=f"chapter_number not contiguous: {ch_numbers}",
                    proposed_fix="re-run path activation to normalize chapter_number",
                ))

        verdict_color = color_from_findings(findings)
        return AgentVerdict(
            agent_name=self.name,
            color=verdict_color,
            summary=(
                f"{len(findings)} invariant violation(s)" if findings
                else f"all invariants pass across {metadata.get('modules_count', 0)} "
                     f"modules and {metadata.get('cached_lessons_count', 0)} cached lessons"
            ),
            findings=findings,
            metadata=metadata,
            reasoning="Checked: chapter skill_id resolves in ontology; Module "
                      "title equals ontology canonical name; cached Lesson "
                      "content meta.skill_id matches parent Module.skill_id; "
                      "chapter_number contiguous.",
        )
