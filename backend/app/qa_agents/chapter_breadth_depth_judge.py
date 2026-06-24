"""Agent E - Chapter Breadth + Depth Judge.

Scores generated chapter content on BREADTH (does it cover enough of the skill
at the target level?) and DEPTH (does it go deep enough?). This is the judge
Luda flagged at the Jun 23 weekly sync as the urgent missing piece, and the
rubric is documented in `app/data/chapter_breadth_depth_rubric.md`.

Trust-Before-Intelligence contract (CLAUDE.md):
  - The judge LLM returns ONLY per-criterion integer scores (1-5) + a short
    justification. It never computes the composite or the gate.
  - `compose_score()` (pure Python, no I/O) normalizes, weights, and gates.
  - The judge model is pinned via `get_judge_provider()`, independent of the
    content generator, so judging is not coupled to whatever wrote the chapter.

The deterministic core (`structural_findings`, `compose_score`,
`findings_for_chapter`) is importable and unit-tested without any LLM.
"""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field

from sqlalchemy import select

from app.database import AsyncSessionLocal
from app.models.lesson import Lesson
from app.models.module import Module
from app.qa_agents.base import QAAgent
from app.qa_agents.verdict import AgentVerdict, Finding, Severity, color_from_findings


logger = logging.getLogger(__name__)
logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


# --- Rubric constants (mirror app/data/chapter_breadth_depth_rubric.md) -------

BREADTH_CRITERIA = {
    "concept_coverage": 0.50,
    "scenario_grounding": 0.25,
    "example_variety": 0.25,
}
DEPTH_CRITERIA = {
    "conceptual_depth": 0.25,
    "worked_example_rigor": 0.25,
    "application_rigor": 0.25,
    "level_alignment": 0.25,
}
DIMENSION_WEIGHTS = {"breadth": 0.40, "depth": 0.60}
DIMENSION_GATE = 0.60
OVERALL_GREEN = 0.70
OVERALL_YELLOW = 0.55

ALL_CRITERIA = tuple(BREADTH_CRITERIA) + tuple(DEPTH_CRITERIA)
REQUIRED_SECTIONS = ("meta", "scenario", "concepts", "example_1", "agent_build")
# Missing either of these is fatal (RED); the rest are WARN-level.
CRITICAL_SECTIONS = ("scenario", "concepts")
MIN_NARRATIVE_WORDS = 50
MIN_CONCEPT_CARDS = 3


# --- Typed contract -----------------------------------------------------------

@dataclass
class ChapterScore:
    """Deterministic result for one chapter. The boundary contract of the
    judge's scoring core - importable and asserted in tests."""

    chapter_number: int
    skill_id: str
    breadth: float            # 0..1
    depth: float              # 0..1
    overall: float            # 0..1
    color: str                # "green" | "yellow" | "red"
    structural_violations: list[str] = field(default_factory=list)
    criterion_scores: dict = field(default_factory=dict)  # raw 1-5 per criterion


# --- Deterministic core (no I/O, no LLM) --------------------------------------

def _norm(score_1_to_5: float) -> float:
    """Normalize a 1-5 rubric score to 0..1. Out-of-range inputs are clamped."""
    n = max(1.0, min(5.0, float(score_1_to_5)))
    return (n - 1.0) / 4.0


def structural_findings(chapter: dict) -> list[str]:
    """Deterministic structural floor. Returns a list of violation strings.
    A violation naming a CRITICAL_SECTIONS member is fatal (caller -> RED).
    Pure function: no LLM, no DB."""
    violations: list[str] = []
    chapter = chapter or {}
    for sec in REQUIRED_SECTIONS:
        if sec not in chapter or chapter.get(sec) in (None, {}, []):
            violations.append(f"missing section: {sec}")
    scenario = chapter.get("scenario") or {}
    narrative = (scenario.get("narrative") or "")
    if narrative and len(narrative.split()) < MIN_NARRATIVE_WORDS:
        violations.append(
            f"scenario.narrative thin ({len(narrative.split())}w < {MIN_NARRATIVE_WORDS})"
        )
    concepts = chapter.get("concepts") or {}
    cards = concepts.get("cards") or []
    if cards and len(cards) < MIN_CONCEPT_CARDS:
        violations.append(f"concepts.cards narrow ({len(cards)} < {MIN_CONCEPT_CARDS})")
    return violations


def _has_critical_violation(violations: list[str]) -> bool:
    return any(
        any(f"missing section: {c}" == v for c in CRITICAL_SECTIONS)
        for v in violations
    )


def compose_score(chapter: dict, llm_scores: dict, *,
                  chapter_number: int = 0, skill_id: str = "") -> ChapterScore:
    """Deterministic composition + gate. The LLM never runs here.

    `llm_scores` maps each criterion name to a 1-5 integer. Missing criteria
    default to the failing anchor (1). A critical structural violation forces
    RED regardless of the LLM scores; a non-critical violation caps the color
    at YELLOW.
    """
    violations = structural_findings(chapter)

    breadth = sum(_norm(llm_scores.get(c, 1)) * w for c, w in BREADTH_CRITERIA.items())
    depth = sum(_norm(llm_scores.get(c, 1)) * w for c, w in DEPTH_CRITERIA.items())
    overall = DIMENSION_WEIGHTS["breadth"] * breadth + DIMENSION_WEIGHTS["depth"] * depth

    # Score-driven color
    if overall >= OVERALL_GREEN and breadth >= DIMENSION_GATE and depth >= DIMENSION_GATE:
        color = "green"
    elif overall >= OVERALL_YELLOW:
        color = "yellow"
    else:
        color = "red"

    # Structural floors override upward severity only (never relax it).
    if _has_critical_violation(violations):
        color = "red"
    elif violations and color == "green":
        color = "yellow"

    return ChapterScore(
        chapter_number=chapter_number,
        skill_id=skill_id,
        breadth=round(breadth, 4),
        depth=round(depth, 4),
        overall=round(overall, 4),
        color=color,
        structural_violations=violations,
        criterion_scores={c: int(llm_scores.get(c, 1)) for c in ALL_CRITERIA},
    )


def findings_for_chapter(score: ChapterScore) -> list[Finding]:
    """Translate a ChapterScore into QA Findings. Pure function."""
    findings: list[Finding] = []
    sid = score.skill_id
    cn = score.chapter_number

    for v in score.structural_violations:
        is_critical = any(f"missing section: {c}" == v for c in CRITICAL_SECTIONS)
        findings.append(Finding(
            severity=Severity.ERROR if is_critical else Severity.WARN,
            summary=f"ch#{cn} structural: {v}",
            skill_id=sid,
            proposed_fix="regenerate chapter; structural floor in rubric v1",
        ))

    if score.color == "red" and not score.structural_violations:
        findings.append(Finding(
            severity=Severity.ERROR,
            summary=(f"ch#{cn} ({sid}) below depth/breadth floor: "
                     f"overall={score.overall} breadth={score.breadth} depth={score.depth}"),
            detail="overall < 0.55 on the breadth+depth rubric",
            skill_id=sid,
            proposed_fix="regenerate with richer concepts + worked examples at target level",
        ))
    elif score.color == "yellow" and not score.structural_violations:
        weak = "breadth" if score.breadth < score.depth else "depth"
        findings.append(Finding(
            severity=Severity.WARN,
            summary=(f"ch#{cn} ({sid}) accept-with-review: weak {weak} "
                     f"(overall={score.overall}, breadth={score.breadth}, depth={score.depth})"),
            skill_id=sid,
            proposed_fix=f"deepen {weak} to clear the 0.70 GREEN bar",
        ))
    return findings


# --- LLM scoring schema -------------------------------------------------------

def _score_schema() -> dict:
    props = {c: {"type": "integer", "minimum": 1, "maximum": 5} for c in ALL_CRITERIA}
    props["justification"] = {"type": "string"}
    return {
        "type": "object",
        "properties": props,
        "required": list(ALL_CRITERIA),
        "additionalProperties": False,
    }


JUDGE_SYSTEM_PROMPT = """You are a calibrated chapter-quality judge scoring a
generated learning chapter for BREADTH and DEPTH against a fixed rubric.

You return ONLY integer scores 1-5 per criterion. You do NOT compute averages,
composites, or a verdict - a separate deterministic step does that. Score each
criterion independently against the target level.

Level anchors (every criterion): 5 exemplary at target level; 4 strong, minor
gaps; 3 adequate but thin; 2 weak, visibly shallow/narrow; 1 absent or wrong.

Criteria:
  BREADTH:
    concept_coverage    - range of distinct concepts vs. what the skill needs at target level
    scenario_grounding  - realistic, role-relevant context spanning real applications
    example_variety     - examples cover more than one angle (iteration AND comparison)
  DEPTH:
    conceptual_depth    - mechanism / why, not just definitions
    worked_example_rigor- genuine iteration, diagnosis, before/after with ratings
    application_rigor   - agent_build + implementation_task require real application
    level_alignment     - depth matches current->target level jump

Be strict. A chapter that looks fine but is generic should not score 5s."""


def _build_prompt(skill_id: str, skill_name: str, current_level, target_level,
                  chapter: dict) -> str:
    meta = chapter.get("meta") or {}
    scenario = chapter.get("scenario") or {}
    concepts = chapter.get("concepts") or {}
    cards = concepts.get("cards") or []
    card_titles = [c.get("headline") or c.get("word") or "" for c in cards][:8]
    has_ex1 = bool(chapter.get("example_1"))
    has_ex2 = bool(chapter.get("example_2"))
    has_task = bool(chapter.get("implementation_task"))
    agent_build = chapter.get("agent_build") or {}
    return (
        f"SKILL: {skill_id} - {skill_name!r}\n"
        f"LEVEL JUMP: {current_level} -> {target_level}\n"
        f"chapter_title: {meta.get('chapter_title')}\n\n"
        f"scenario.narrative:\n  {(scenario.get('narrative') or '')[:800]}\n"
        f"why_it_matters: {(scenario.get('why_it_matters') or '')[:300]}\n\n"
        f"concept cards ({len(cards)}): {card_titles}\n"
        f"first card body: {((cards[0].get('body') if cards else '') or '')[:400]}\n\n"
        f"has example_1 (iteration): {has_ex1}\n"
        f"has example_2 (comparison): {has_ex2}\n"
        f"has implementation_task: {has_task}\n"
        f"agent_build system_prompt_template len: "
        f"{len((agent_build.get('system_prompt_template') or ''))} chars\n\n"
        f"Score every criterion 1-5 against the target level. Return JSON only."
    )


class ChapterBreadthDepthJudge(QAAgent):
    name = "Chapter Breadth + Depth"
    description = "Scores cached chapters on breadth + depth (rubric v1, deterministic gate)"

    async def run(self, context: dict) -> AgentVerdict:
        profile_id = context.get("profile_id")
        path_id = context.get("path_id")

        findings: list[Finding] = []
        scored: list[ChapterScore] = []

        async with AsyncSessionLocal() as db:
            path_id = await self._resolve_path_id(db, profile_id, path_id)
            if not path_id:
                return self._green("no path activated; nothing to judge")

            r = await db.execute(select(Module).where(Module.path_id == path_id))
            modules = sorted(r.scalars().all(), key=lambda m: m.chapter_number)
            module_by_id = {m.id: m for m in modules}

            r = await db.execute(
                select(Lesson).where(Lesson.path_id == path_id, Lesson.content.isnot(None))
            )
            cached = [ls for ls in r.scalars().all() if ls.content]

            if not cached:
                return AgentVerdict(
                    agent_name=self.name, color=color_from_findings([]),
                    summary="path has no cached chapters yet - nothing to judge",
                    findings=[], metadata={"path_id": path_id, "modules": len(modules)},
                    reasoning="Chapters are generated on first lesson click.",
                )

            judge = None
            try:
                from app.services.llm import get_judge_provider
                judge = get_judge_provider()
            except Exception:
                logger.info("Judge LLM unavailable; structural floor only.")

            for ls in cached:
                mod = module_by_id.get(ls.module_id)
                if not mod:
                    continue
                content = ls.content or {}
                llm_scores: dict = {}
                if judge:
                    llm_scores = await self._score_chapter_llm(judge, mod, content)
                score = compose_score(
                    content, llm_scores,
                    chapter_number=mod.chapter_number, skill_id=mod.skill_id,
                )
                scored.append(score)
                findings.extend(findings_for_chapter(score))

        color = color_from_findings(findings)
        avg_overall = round(sum(s.overall for s in scored) / len(scored), 4) if scored else 0.0
        return AgentVerdict(
            agent_name=self.name,
            color=color,
            summary=(f"judged {len(scored)} chapter(s) on breadth+depth; "
                     f"avg overall={avg_overall}; {len(findings)} finding(s)"),
            findings=findings,
            metadata={
                "path_id": path_id,
                "chapters_judged": len(scored),
                "avg_overall": avg_overall,
                "rubric": "chapter_breadth_depth_rubric.md v1",
                "scores": [
                    {"ch": s.chapter_number, "skill_id": s.skill_id,
                     "breadth": s.breadth, "depth": s.depth, "overall": s.overall,
                     "color": s.color}
                    for s in scored
                ],
            },
            reasoning="LLM scored each criterion 1-5; Python composed the "
                      "composite + gate per rubric v1 (Trust-Before-Intelligence).",
        )

    async def _resolve_path_id(self, db, profile_id, path_id):
        if path_id:
            return path_id
        if not profile_id:
            return None
        from app.models.goal import Goal
        from app.models.learning_path import LearningPath
        r = await db.execute(
            select(Goal).where(Goal.profile_id == profile_id).order_by(Goal.created_at.desc())
        )
        g = r.scalars().first()
        if not g:
            return None
        r = await db.execute(select(LearningPath).where(LearningPath.goal_id == g.id))
        p = r.scalars().first()
        return p.id if p else None

    async def _score_chapter_llm(self, judge, mod, content: dict) -> dict:
        meta = content.get("meta") or {}
        try:
            raw = await judge.generate_structured(
                prompt=_build_prompt(
                    mod.skill_id, mod.skill_name,
                    meta.get("current_level"), meta.get("target_level"), content,
                ),
                output_schema=_score_schema(),
                system_prompt=JUDGE_SYSTEM_PROMPT,
                temperature=0.0,
            )
            if isinstance(raw, str):
                raw = json.loads(raw)
            return {c: raw.get(c, 1) for c in ALL_CRITERIA}
        except Exception as exc:
            logger.debug("Breadth/depth LLM scoring failed for %s: %s", mod.skill_id, exc)
            return {}
