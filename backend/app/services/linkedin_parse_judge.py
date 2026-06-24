"""LinkedIn Parser Judge - reusable, deterministic-gated quality judge.

Per the 2026-06-09 / 2026-06-23 weekly calls: every step gets a judge, and we
"fix what the judge doesn't pass" rather than run a self-improving loop. This
judges the LinkedIn parser's output (the AI skills it says a learner already
has) on four parameters.

Trust-Before-Intelligence (CLAUDE.md):
  - ONTOLOGY PRECISION is DETERMINISTIC: whether each skill_id is a real
    ontology id is computed in Python (`ontology_precision_score`), never asked
    of the LLM. The model does not grade ID validity it can look up.
  - The genuinely subjective parameters (evidence_quality, conservativeness,
    coverage) are scored by the PINNED judge model via `get_judge_provider()`,
    NOT the generation provider. Coupling judging to the generator is the bug
    this module fixes.
  - `compute_composite` / `determine_verdict` (pure Python) own the arithmetic
    and the gate. They are importable and unit-tested without any LLM.

The script `backend/scripts/run_linkedin_parser_judge.py` imports this module so
the batch runner and any pipeline share one calibrated implementation.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


# --- Rubric constants ---------------------------------------------------------

WEIGHTS = {
    "ontology_precision": 0.20,
    "evidence_quality": 0.35,
    "conservativeness": 0.30,
    "coverage": 0.15,
}
GATES = {
    "ontology_precision": 0.95,
    "evidence_quality": 0.70,
    "conservativeness": 0.70,
}
ACCEPT_THRESHOLD = 0.85
REVIEW_THRESHOLD = 0.70

LLM_PARAMETERS = ("evidence_quality", "conservativeness", "coverage")


# --- Typed contract -----------------------------------------------------------

@dataclass
class ParseJudgeResult:
    """Boundary contract of the judge. Importable and asserted in tests."""

    verdict: str                 # "ACCEPT" | "ACCEPT_WITH_REVIEW" | "REJECT"
    composite: float             # 0..1
    parameter_scores: dict       # param name -> 0..1
    gate_failures: list[str] = field(default_factory=list)
    invalid_skill_ids: list[str] = field(default_factory=list)
    llm_used: bool = True
    summary: str = ""


# --- Deterministic core (pure, no LLM, no I/O) --------------------------------

def ontology_precision_score(parser_result: dict,
                             valid_skill_ids) -> tuple[float, list[str]]:
    """Fraction of claimed skills whose skill_id is a real ontology id.
    Deterministic - computed in Python, never asked of the model. An empty
    claim list scores 1.0 (nothing wrong was claimed; coverage handles misses)."""
    skills = parser_result.get("existing_skills") or []
    if not skills:
        return 1.0, []
    valid = set(valid_skill_ids or [])
    invalid = [s.get("skill_id", "?") for s in skills if s.get("skill_id") not in valid]
    return (len(skills) - len(invalid)) / len(skills), invalid


def compute_composite(scores: dict) -> float:
    """Weighted composite. Missing parameters count as 0."""
    return round(sum(float(scores.get(k, 0.0)) * w for k, w in WEIGHTS.items()), 4)


def gate_failures(scores: dict) -> list[str]:
    """Parameters that fall below their gate. Order matches WEIGHTS."""
    return [k for k in WEIGHTS if k in GATES and float(scores.get(k, 0.0)) < GATES[k]]


def determine_verdict(composite: float, gates: list[str]) -> str:
    if gates:
        return "REJECT"
    if composite < REVIEW_THRESHOLD:
        return "REJECT"
    if composite < ACCEPT_THRESHOLD:
        return "ACCEPT_WITH_REVIEW"
    return "ACCEPT"


def assemble_result(parser_result: dict, valid_skill_ids, llm_param_scores: dict,
                    *, llm_used: bool = True, summary: str = "") -> ParseJudgeResult:
    """Combine the deterministic ontology-precision score with the LLM's
    subjective parameter scores, then compute the composite + gate + verdict.
    Pure function - the LLM has already run before this is called."""
    op, invalid = ontology_precision_score(parser_result, valid_skill_ids)
    scores = {"ontology_precision": op}
    for p in LLM_PARAMETERS:
        scores[p] = max(0.0, min(1.0, float(llm_param_scores.get(p, 0.0))))
    gates = gate_failures(scores)
    composite = compute_composite(scores)
    return ParseJudgeResult(
        verdict=determine_verdict(composite, gates),
        composite=composite,
        parameter_scores=scores,
        gate_failures=gates,
        invalid_skill_ids=invalid,
        llm_used=llm_used,
        summary=summary,
    )


# --- LLM scoring (pinned judge model) -----------------------------------------

SYSTEM_PROMPT = """You are an expert evaluator for AI-skill parsers operating on LinkedIn profiles. You receive a LinkedIn profile text, the parser's output (a list of existing AI skills with evidence + confidence + level claims), and the GenAI Skills Ontology. Evaluate the parser output against three SUBJECTIVE parameters (ontology precision is computed separately and is NOT your job).

The parser's job was to identify what AI skills the learner ALREADY HAS based on the LI text, with evidence. Your job is to judge whether it did that well.

PARAMETER - EVIDENCE QUALITY (gate >= 0.70). For each parser claim, verify the cited evidence is actually present in the LI text AND supports the level + confidence claim. Per skill: evidence_supports_claim (1.0), evidence_present_but_weak (0.5), evidence_not_in_text_or_unrelated (0). Score = average.

PARAMETER - CONSERVATIVENESS (gate >= 0.70). Over-claiming is the cardinal sin. Per skill: appropriately_conservative (1.0), slightly_overclaimed (0.5), heavily_overclaimed (0). Score = average.

PARAMETER - COVERAGE (no gate). Did the parser miss obvious AI skills explicitly named in the LI? List up to 5 missed skills with supporting LI text. Score = 1 - (missed / 5), floored at 0.

Return the three scores 0..1. DO NOT compute the composite; the wrapper does that."""

OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "evidence_quality": {"type": "number", "minimum": 0, "maximum": 1},
        "conservativeness": {"type": "number", "minimum": 0, "maximum": 1},
        "coverage": {"type": "number", "minimum": 0, "maximum": 1},
        "missed_skills": {"type": "array", "items": {"type": "string"}},
        "summary": {"type": "string"},
    },
    "required": ["evidence_quality", "conservativeness", "coverage"],
}


def render_parser_output(existing_skills: list) -> str:
    if not existing_skills:
        return "  (parser returned no existing skills)"
    lines = []
    for s in existing_skills:
        lines.append(
            f"  {s.get('skill_id', '?'):<16} L{s.get('estimated_current_level', '?')}  "
            f"conf={s.get('confidence', '?'):<7}  {s.get('skill_name', '?')}"
        )
        if s.get("evidence"):
            lines.append(f"     evidence: {s['evidence'][:250]}")
    return "\n".join(lines)


async def judge_linkedin_parse(parser_result: dict, linkedin_text: str,
                               ontology_md: str, valid_skill_ids,
                               judge=None) -> ParseJudgeResult:
    """Full judge: deterministic ontology precision + pinned-model subjective
    scores. Falls back to a structural-only verdict if the judge LLM is
    unavailable (cannot confirm grounding -> never a clean ACCEPT)."""
    if judge is None:
        try:
            from app.services.llm import get_judge_provider
            judge = get_judge_provider()
        except Exception:
            logger.info("Judge LLM unavailable; ontology-precision only.")
            op, invalid = ontology_precision_score(parser_result, valid_skill_ids)
            verdict = "ACCEPT_WITH_REVIEW" if op >= GATES["ontology_precision"] else "REJECT"
            return ParseJudgeResult(
                verdict=verdict, composite=op * WEIGHTS["ontology_precision"],
                parameter_scores={"ontology_precision": op}, invalid_skill_ids=invalid,
                llm_used=False, summary="grounding not verified (no judge LLM)",
            )

    prompt = (
        f"=== INPUT 1: LINKEDIN PROFILE TEXT ===\n{linkedin_text}\n\n"
        f"=== INPUT 2: LINKEDIN PARSER OUTPUT (claimed existing skills) ===\n"
        f"{render_parser_output(parser_result.get('existing_skills', []))}\n\n"
        f"AI fluency: {(parser_result.get('ai_fluency_assessment') or {}).get('level', '?')}\n\n"
        f"=== INPUT 3: ONTOLOGY ===\n{ontology_md}\n\n"
        f"Score evidence_quality, conservativeness, coverage (each 0..1). JSON only."
    )
    raw = await judge.generate_structured(
        prompt=prompt, output_schema=OUTPUT_SCHEMA,
        system_prompt=SYSTEM_PROMPT, temperature=0.0, max_tokens=2000,
    )
    if isinstance(raw, str):
        import json
        raw = json.loads(raw)
    return assemble_result(
        parser_result, valid_skill_ids, raw, llm_used=True,
        summary=raw.get("summary", ""),
    )
