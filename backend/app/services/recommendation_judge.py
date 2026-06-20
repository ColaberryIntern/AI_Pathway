"""Recommendation judge gate (Trust Before Intelligence - Governance/Permitted layer).

Runs the calibrated v4 judge on a final recommendation set:
  - the LLM (PINNED to the calibrated judge model via get_judge_provider) produces
    ONLY per-item judgments (requirement rows, per-skill fit/gap, invalid IDs);
  - judge_scoring.deterministic_score computes the coverage/role-fit/ontology/gap
    scores, the composite, the gates, and the verdict in Python;
  - ontology precision is validated against the real ontology, not the model.

gate_decision() turns the verdict into a pass/action the pipeline can act on.
This is the Governance gate the framework requires before a recommendation reaches
the learner. Wire it into the recommendation path (analysis route / orchestrator).
"""
import json
from pathlib import Path

from app.services.llm.factory import get_judge_provider
from app.services.judge_scoring import deterministic_score, JudgeResult
from app.services.ontology import get_ontology_service

# Lexicon (GOALS) - the shared grading definitions, derived from the expert
# reference gradings. Appended to the judge system prompt so full/partial coverage
# and role_specific are scored consistently.
LEXICON = """

LEXICON CALIBRATION (apply strictly):
COVERAGE per AI-relevant requirement: full = the requirement's mapped ontology skill is in the recommended set, or a recommended skill directly addresses it (if the mapped skill is in the set, grade full); partial = adjacent but not the mapped skill; none = no recommended skill addresses it.
ROLE FIT per recommended skill: role_specific = maps to an Explicit or Implied Step-1 row; contextually_relevant = relevant to the role's function but maps to no Step-1 row; generic = a general AI skill with no tie to any AI-relevant requirement."""


def _load_spec() -> tuple[str, dict]:
    path = Path(__file__).resolve().parents[1] / "data" / "judge_spec_v4.md"
    text = path.read_text(encoding="utf-8")
    sys_part, schema_part = text.split("## OUTPUT SCHEMA")
    system_prompt = sys_part.split("## SYSTEM PROMPT", 1)[1].strip()
    start = schema_part.find("```json") + 7
    end = schema_part.find("```", start)
    return system_prompt, json.loads(schema_part[start:end].strip())


_SYSTEM_PROMPT, _SCHEMA = _load_spec()


def _render_skills(skills: list[dict]) -> str:
    lines = []
    for i, s in enumerate(skills, 1):
        sid = s.get("skill_id", "")
        name = s.get("skill_name") or s.get("name") or sid
        lvl = s.get("target_level") or s.get("target_proficiency_level") or ""
        lines.append(f"  #{i}  {sid}  L{lvl}  {name}")
    return "\n".join(lines)


def _build_prompt(jd_text: str, li_text: str, skills: list[dict], ontology_md: str) -> str:
    return f"""=== INPUT 1: JOB DESCRIPTION ===
{jd_text}

=== INPUT 2: LINKEDIN PROFILE ===
{li_text}

=== INPUT 3: RECOMMENDED SKILLS TO EVALUATE ===
{_render_skills(skills)}

=== INPUT 4: ONTOLOGIES.md (canonical reference) ===
{ontology_md}

=== TASK ===
Evaluate the recommended skill list using the four-parameter framework. Return the structured JSON response per the schema."""


async def evaluate_recommendation(jd_text: str, li_text: str, skills: list[dict],
                                  ontology_md: str | None = None) -> JudgeResult:
    """Judge a final recommendation set and return the deterministic verdict."""
    onto = get_ontology_service()
    if ontology_md is None:
        ontology_md = onto.format_skills_for_prompt()
    judge = get_judge_provider()  # pinned, calibrated model (gpt-4.1)
    raw = await judge.generate_structured(
        prompt=_build_prompt(jd_text, li_text, skills, ontology_md),
        output_schema=_SCHEMA,
        system_prompt=_SYSTEM_PROMPT + LEXICON,
        temperature=0.0,
    )
    rec_ids = [s.get("skill_id") for s in skills if s.get("skill_id")]
    return deterministic_score(
        raw.get("parameters", {}),
        total_skills=len(rec_ids),
        recommended_ids=rec_ids,
        valid_skill_ids=onto.get_all_skill_ids(),
    )


_ACTION = {"ACCEPT": "accept", "ACCEPT_WITH_REVIEW": "review", "REJECT": "regenerate"}


def gate_decision(result: JudgeResult) -> dict:
    """Deterministic gate decision from a JudgeResult."""
    verdict = result["overall_verdict"]
    return {
        "pass": verdict != "REJECT",
        "verdict": verdict,
        "action": _ACTION.get(verdict, "regenerate"),
        "composite": result["composite"],
        "gate_failures": result["gate_failures"],
    }
