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
import asyncio
import json
from pathlib import Path
from statistics import median

from app.config import get_settings
from app.services.llm.factory import get_judge_provider
from app.services.judge_scoring import (
    deterministic_score,
    verdict_from_scores,
    JudgeResult,
)
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


async def _judge_once(jd_text: str, li_text: str, skills: list[dict],
                      ontology_md: str, valid_ids) -> tuple[JudgeResult, dict]:
    """One judge sample -> (deterministic JudgeResult, raw LLM parameters).
    The raw params carry the per-skill fit detail the regeneration step needs."""
    judge = get_judge_provider()  # pinned, calibrated model (gpt-4.1)
    raw = await judge.generate_structured(
        prompt=_build_prompt(jd_text, li_text, skills, ontology_md),
        output_schema=_SCHEMA,
        system_prompt=_SYSTEM_PROMPT + LEXICON,
        temperature=0.0,
    )
    params = raw.get("parameters", {})
    rec_ids = [s.get("skill_id") for s in skills if s.get("skill_id")]
    result = deterministic_score(
        params,
        total_skills=len(rec_ids),
        recommended_ids=rec_ids,
        valid_skill_ids=valid_ids,
    )
    return result, params


async def evaluate_recommendation(jd_text: str, li_text: str, skills: list[dict],
                                  ontology_md: str | None = None) -> JudgeResult:
    """Judge a final recommendation set with a single sample (legacy/back-compat).
    Prefer evaluate_recommendation_stable for governance decisions."""
    onto = get_ontology_service()
    if ontology_md is None:
        ontology_md = onto.format_skills_for_prompt()
    result, _params = await _judge_once(
        jd_text, li_text, skills, ontology_md, onto.get_all_skill_ids())
    return result


def _aggregate_skill_fit(raws: list[dict]) -> tuple[dict, list[str]]:
    """Majority fit_level per recommended skill id across K runs (robust to the
    judge's per-call variance). Returns (skill_fit, weak_skill_ids) where weak =
    skills whose majority verdict is not role_specific (the regeneration targets)."""
    from collections import Counter
    by_id: dict[str, Counter] = {}
    for raw in raws or []:
        for s in ((raw.get("role_fit_strength") or {}).get("skills") or []):
            sid = s.get("id") or s.get("skill_id")
            if not sid:
                continue
            by_id.setdefault(sid, Counter())[s.get("fit_level", "generic")] += 1
    fit = {sid: c.most_common(1)[0][0] for sid, c in by_id.items()}
    weak = [sid for sid, lvl in fit.items() if lvl != "role_specific"]
    return fit, weak


def aggregate_results(results: list[JudgeResult], k: int,
                      raws: list[dict] | None = None) -> dict:
    """Aggregate K judge samples deterministically (Trust Before Intelligence).

    Each sub-score is collapsed to its median across the K runs (robust to the
    LLM's per-call variance), then the canonical gate logic produces the verdict.
    A disagreement guard refuses to hard-act (ACCEPT/REJECT) when the K-run panel
    is not unanimous: a non-unanimous panel is routed to ACCEPT_WITH_REVIEW so a
    coin-flip never auto-accepts or auto-regenerates a recommendation.

    When raws (the per-run LLM parameters) are supplied, the result also carries
    skill_fit (majority fit_level per skill) and weak_skill_ids (the regeneration
    targets).
    """
    if not results:
        raise ValueError("aggregate_results requires at least one JudgeResult")
    keys = ("jd_coverage", "role_fit_strength", "ontology_precision", "gap_validity")
    med = {key: round(median(r["scores"][key] for r in results), 4) for key in keys}
    composite, gate_failures, base_verdict = verdict_from_scores(med)

    run_verdicts = [r["overall_verdict"] for r in results]
    unanimous = len(set(run_verdicts)) == 1
    verdict = base_verdict
    routed = False
    if not unanimous and base_verdict in ("ACCEPT", "REJECT"):
        verdict = "ACCEPT_WITH_REVIEW"  # low judge confidence -> human review
        routed = True

    composites = [r["composite"] for r in results]
    verdict_counts: dict[str, int] = {}
    for v in run_verdicts:
        verdict_counts[v] = verdict_counts.get(v, 0) + 1
    out = {
        "composite": composite,
        "overall_verdict": verdict,
        "gate_failures": gate_failures,
        "scores": med,
        "regeneration_recommended": verdict == "REJECT",
        # stability / observability
        "n_runs": len(results),
        "k_requested": k,
        "unanimous": unanimous,
        "routed_to_review_on_disagreement": routed,
        "verdict_counts": verdict_counts,
        "composite_median": round(median(composites), 4),
        "composite_spread": round(max(composites) - min(composites), 4),
    }
    if raws is not None:
        skill_fit, weak = _aggregate_skill_fit(raws)
        out["skill_fit"] = skill_fit
        out["weak_skill_ids"] = weak
    return out


async def evaluate_recommendation_stable(jd_text: str, li_text: str, skills: list[dict],
                                         k: int | None = None,
                                         ontology_md: str | None = None) -> dict:
    """Ensembled judge: K concurrent samples aggregated to a stable verdict.

    This is the governance entry point. K defaults to settings.judge_ensemble_k.
    Returns the JudgeResult fields plus stability metadata (see aggregate_results).
    """
    if k is None:
        k = get_settings().judge_ensemble_k
    k = max(1, int(k))
    onto = get_ontology_service()
    if ontology_md is None:
        ontology_md = onto.format_skills_for_prompt()
    valid_ids = onto.get_all_skill_ids()
    pairs = await asyncio.gather(
        *[_judge_once(jd_text, li_text, skills, ontology_md, valid_ids) for _ in range(k)]
    )
    results = [p[0] for p in pairs]
    raws = [p[1] for p in pairs]
    return aggregate_results(results, k, raws)


_ACTION = {"ACCEPT": "accept", "ACCEPT_WITH_REVIEW": "review", "REJECT": "regenerate"}


def gate_decision(result: JudgeResult | dict) -> dict:
    """Deterministic gate decision from a JudgeResult or an ensemble result.
    Passes through stability metadata when the result came from the ensemble."""
    verdict = result["overall_verdict"]
    decision = {
        "pass": verdict != "REJECT",
        "verdict": verdict,
        "action": _ACTION.get(verdict, "regenerate"),
        "composite": result["composite"],
        "gate_failures": result["gate_failures"],
    }
    for key in ("unanimous", "composite_spread", "verdict_counts",
                "routed_to_review_on_disagreement", "n_runs"):
        if key in result:
            decision[key] = result[key]
    return decision
